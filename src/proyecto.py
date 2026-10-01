"""ETL reproducible del archivo recibido; PostgreSQL es el único destino."""
from pathlib import Path
import hashlib
import os
import unicodedata
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError

RAIZ = Path(__file__).resolve().parents[1]
ESQUEMA = 'p1_homicidios'
RENOMBRES = {'FECHA HECHO':'fecha', 'COD_DEPTO':'cod_departamento',
    'DEPARTAMENTO':'departamento', 'COD_MUNI':'cod_municipio',
    'MUNICIPIO':'municipio', 'ZONA':'zona', 'SEXO':'sexo',
    'ARMA MEDIO':'arma_medio', 'MODALIDAD PRESUNTA':'modalidad_presunta',
    'SPOA_CARACTERIZACION':'caracterizacion', 'CANTIDAD':'cantidad'}
DIMENSIONES = {
    'dim_tiempo': ('tiempo_id', ['fecha','anio','mes','dia','trimestre']),
    'dim_ubicacion': ('ubicacion_id', ['cod_departamento','departamento','cod_municipio','municipio','zona']),
    'dim_sexo': ('sexo_id', ['sexo']),
    'dim_contexto': ('contexto_id', ['arma_medio','modalidad_presunta','caracterizacion'])}

def conectar():
    load_dotenv(RAIZ / '.env')
    valor = os.getenv('DATABASE_URL', '')
    if not valor:
        raise RuntimeError('Falta DATABASE_URL. Copie .env.example a .env y configure PostgreSQL.')
    try:
        url = make_url(valor)
        if url.get_backend_name() != 'postgresql':
            raise ValueError('PostgreSQL es obligatorio')
        url = url.set(drivername='postgresql+psycopg')
        motor = create_engine(url, connect_args={'connect_timeout':10}, pool_pre_ping=True)
        with motor.connect() as conexion:
            conexion.execute(text('SELECT 1'))
        return motor
    except (SQLAlchemyError, ValueError, ImportError):
        raise RuntimeError('No se pudo conectar a PostgreSQL. Revise servicio, host, puerto, base, usuario y contraseña en .env. La URL se oculta para proteger credenciales.') from None

def extraer():
    ruta = RAIZ / 'datos/homicidios_fuente.csv'
    fuente = pd.read_csv(ruta, dtype='string', keep_default_na=False)
    fuente.columns = fuente.columns.str.strip()
    if set(fuente.columns) != set(RENOMBRES):
        raise ValueError('El CSV no tiene las 11 columnas esperadas. Revise el origen.')
    if fuente.empty:
        raise ValueError('La fuente no contiene registros.')
    return fuente, hashlib.sha256(ruta.read_bytes()).hexdigest()

def normalizar(valor):
    return ' '.join(unicodedata.normalize('NFC', str(valor)).upper().split())

def transformar(fuente, huella):
    datos = fuente.rename(columns=RENOMBRES).copy()
    datos['fila_fuente'] = range(2, len(datos)+2)  # Fila del CSV con encabezado.
    datos['fuente_sha256'] = huella
    datos['fecha'] = pd.to_datetime(datos['fecha'], format='%Y-%m-%d', errors='raise')
    cantidad = pd.to_numeric(datos['cantidad'], errors='raise')
    if cantidad.isna().any() or (cantidad <= 0).any() or (cantidad % 1 != 0).any():
        raise ValueError('CANTIDAD debe ser un entero positivo en todas las filas.')
    datos['cantidad'] = cantidad.astype('int64')
    for col, ancho in [('cod_departamento',2),('cod_municipio',5)]:
        if not datos[col].str.fullmatch(r'\d+').all():
            raise ValueError(f'Código no válido en {col}.')
        datos[col] = datos[col].str.zfill(ancho)
        if not datos[col].str.len().eq(ancho).all():
            raise ValueError(f'Longitud no válida en {col}.')
    if not datos.cod_municipio.str[:2].eq(datos.cod_departamento).all():
        raise ValueError('El prefijo municipal no coincide con el departamento.')
    textos = ['departamento','municipio','zona','sexo','arma_medio','modalidad_presunta','caracterizacion']
    vacios = {}
    for col in textos:
        datos[col] = datos[col].map(normalizar)
        vacios[col] = int(datos[col].eq('').sum())
    # Completar un nombre vacío solo si el código tiene una única etiqueta conocida.
    reparados = 0
    for codigo, nombre in [('cod_departamento','departamento'),('cod_municipio','municipio')]:
        conocidos = datos.loc[datos[nombre].ne(''), [codigo,nombre]].drop_duplicates()
        if conocidos.groupby(codigo)[nombre].nunique().gt(1).any():
            raise ValueError(f'Hay etiquetas contradictorias para {codigo}; revisar antes de cargar.')
        mapa = conocidos.set_index(codigo)[nombre]
        faltan = datos[nombre].eq('')
        relleno = datos.loc[faltan,codigo].map(mapa)
        reparados += int(relleno.notna().sum())
        datos.loc[faltan,nombre] = relleno.fillna('SIN INFORMACION')
    for col in textos:
        datos[col] = datos[col].replace('', 'SIN INFORMACION')
    datos['anio'] = datos.fecha.dt.year
    datos['mes'] = datos.fecha.dt.month
    datos['dia'] = datos.fecha.dt.day
    datos['trimestre'] = datos.fecha.dt.quarter
    tablas = {}
    hecho = datos.copy()
    for nombre, (clave, atributos) in DIMENSIONES.items():
        dimension = datos[atributos].drop_duplicates().sort_values(atributos).reset_index(drop=True)
        dimension.insert(0, clave, range(1,len(dimension)+1))
        hecho = hecho.merge(dimension, on=atributos, how='left', validate='many_to_one', sort=False)
        if hecho[clave].isna().any():
            raise ValueError(f'Claves huérfanas en {nombre}.')
        tablas[nombre] = dimension
    hecho = hecho.sort_values('fila_fuente').reset_index(drop=True)
    claves = [especificacion[0] for especificacion in DIMENSIONES.values()]
    hecho = hecho[['fuente_sha256','fila_fuente',*claves,'cantidad']].copy()
    hecho.insert(0, 'hecho_id', range(1,len(hecho)+1))
    if len(hecho) != len(fuente) or hecho.cantidad.sum() != datos.cantidad.sum():
        raise ValueError('No se conserva el número de filas o la suma de cantidades.')
    tablas['hecho_homicidios'] = hecho
    auditoria = {'filas_fuente':len(fuente), 'filas_hecho':len(hecho),
        'suma_cantidad':int(hecho.cantidad.sum()), 'duplicados_exactos_conservados':int(fuente.duplicated().sum()),
        'nombres_completados_por_codigo':reparados, 'textos_vacios_originales':vacios,
        'fecha_min':str(datos.fecha.min().date()),'fecha_max':str(datos.fecha.max().date()),
        'dias_distintos':sorted(int(x) for x in datos.dia.unique()),'fuente_sha256':huella}
    return tablas, datos, auditoria

DDL = '''
CREATE SCHEMA IF NOT EXISTS p1_homicidios;
CREATE TABLE IF NOT EXISTS p1_homicidios.dim_tiempo (
 tiempo_id INTEGER PRIMARY KEY, fecha DATE NOT NULL UNIQUE,
 anio INTEGER NOT NULL, mes INTEGER NOT NULL CHECK(mes BETWEEN 1 AND 12),
 dia INTEGER NOT NULL CHECK(dia BETWEEN 1 AND 31), trimestre INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS p1_homicidios.dim_ubicacion (
 ubicacion_id INTEGER PRIMARY KEY, cod_departamento VARCHAR(2) NOT NULL,
 departamento TEXT NOT NULL, cod_municipio VARCHAR(5) NOT NULL,
 municipio TEXT NOT NULL, zona TEXT NOT NULL,
 UNIQUE(cod_municipio,zona));
CREATE TABLE IF NOT EXISTS p1_homicidios.dim_sexo (
 sexo_id INTEGER PRIMARY KEY, sexo TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS p1_homicidios.dim_contexto (
 contexto_id INTEGER PRIMARY KEY, arma_medio TEXT NOT NULL,
 modalidad_presunta TEXT NOT NULL, caracterizacion TEXT NOT NULL,
 UNIQUE(arma_medio,modalidad_presunta,caracterizacion));
CREATE TABLE IF NOT EXISTS p1_homicidios.hecho_homicidios (
 hecho_id BIGINT PRIMARY KEY, fuente_sha256 VARCHAR(64) NOT NULL,
 fila_fuente INTEGER NOT NULL,
 tiempo_id INTEGER NOT NULL REFERENCES p1_homicidios.dim_tiempo,
 ubicacion_id INTEGER NOT NULL REFERENCES p1_homicidios.dim_ubicacion,
 sexo_id INTEGER NOT NULL REFERENCES p1_homicidios.dim_sexo,
 contexto_id INTEGER NOT NULL REFERENCES p1_homicidios.dim_contexto,
 cantidad INTEGER NOT NULL CHECK(cantidad>0), UNIQUE(fuente_sha256,fila_fuente));
CREATE INDEX IF NOT EXISTS idx_hecho_tiempo ON p1_homicidios.hecho_homicidios(tiempo_id);
CREATE INDEX IF NOT EXISTS idx_hecho_ubicacion ON p1_homicidios.hecho_homicidios(ubicacion_id);
CREATE INDEX IF NOT EXISTS idx_hecho_sexo ON p1_homicidios.hecho_homicidios(sexo_id);
CREATE INDEX IF NOT EXISTS idx_hecho_contexto ON p1_homicidios.hecho_homicidios(contexto_id);
'''

def cargar(motor, tablas):
    """Recarga atómica del esquema dedicado: las restricciones nunca se eliminan."""
    try:
        with motor.begin() as conexion:
            for sentencia in DDL.split(';'):
                if sentencia.strip():
                    conexion.execute(text(sentencia))
            # Serializar recargas concurrentes del mismo proyecto.
            conexion.execute(text('SELECT pg_advisory_xact_lock(1731001)'))
            conexion.execute(text('TRUNCATE TABLE p1_homicidios.hecho_homicidios, '
                'p1_homicidios.dim_tiempo, p1_homicidios.dim_ubicacion, '
                'p1_homicidios.dim_sexo, p1_homicidios.dim_contexto'))
            for nombre, tabla in tablas.items():
                tabla.to_sql(nombre,conexion,schema=ESQUEMA,if_exists='append',index=False,chunksize=2000)
            control = conexion.execute(text('SELECT COUNT(*), SUM(cantidad) FROM p1_homicidios.hecho_homicidios')).one()
            if tuple(control) != (len(tablas['hecho_homicidios']),int(tablas['hecho_homicidios'].cantidad.sum())):
                raise ValueError('La conciliación en PostgreSQL no coincide con la fuente.')
    except (SQLAlchemyError, pd.errors.DatabaseError):
        raise RuntimeError('Falló la carga PostgreSQL y se revirtió la transacción. Revise permisos CREATE/INSERT y compatibilidad del esquema p1_homicidios. No se muestran credenciales ni filas de datos.') from None
    return {'filas_postgresql':int(control[0]),'cantidad_postgresql':int(control[1])}

def consultar(motor, sql):
    try:
        with motor.connect() as conexion:
            return pd.read_sql_query(text(sql), conexion)
    except (SQLAlchemyError, pd.errors.DatabaseError):
        raise RuntimeError('No se pudo consultar la bodega. Ejecute primero fase_b_etl.ipynb y compruebe PostgreSQL.') from None

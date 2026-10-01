# Proyecto 1 · Bodega de datos de homicidios

**Grupo 1:** Andres Felipe Castrillon Martinez, Bryan Panesso Avila y Juan David Turrigao Orozco.

**Pregunta:** ¿Cómo se distribuye la cantidad registrada por tiempo, territorio, sexo y características del hecho en el archivo aportado?

## Ejecutar

Requisitos: Python 3.12, PostgreSQL 16 o posterior y una base dedicada. Como alternativa, Docker Desktop permite crear PostgreSQL con el archivo incluido.

1. Descomprimir el ZIP (o clonar el repositorio del grupo) y entrar a su raíz.
2. Crear un entorno y activarlo, por ejemplo en PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

3. Editar `.env`: completar `DATABASE_URL`. Si se usa Docker, cambiar `POSTGRES_PASSWORD` y usar esa misma clave en la URL. Codificar caracteres especiales de la contraseña en la URL. 
4. Con Docker: `docker compose -p grupo1p1 up -d --wait`. Con PostgreSQL existente: crear antes la base y dar al usuario permisos para crear el esquema `p1_homicidios`. Las cinco tablas de ese esquema se recargan completamente.
5. Abrir `jupyter lab`. Ejecutar **Restart Kernel & Run All Cells** en este orden:
   - `entrega/fase_b_etl.ipynb`
   - `entrega/fase_c_sql.ipynb`
   - `entrega/fase_d_visualizaciones.ipynb`

Los notebooks ya incluyen salidas de una ejecución verificada. C y D abren su propia conexión y no necesitan variables de otros kernels. Para detener PostgreSQL sin borrar datos: `docker compose -p grupo1p1 stop`.

## Archivos y alcance

Los seis entregables principales están en `entrega/`. `datos/` conserva el Excel aportado, su conversión CSV sin filtrar y las huellas SHA-256. `src/` contiene el ETL, las seis consultas y las ocho figuras. `documentacion/` contiene el análisis de avances, la validación y el guion oral. Los notebooks de exploración inicial y EDA son complementos pedidos por los avances.

**Acuerdo del avance 1 (firma pendiente):** Los integrantes del grupo se comprometen a mantener el dataset elegido durante los tres proyectos del semestre (P1, P2/3, P4). Cambios sólo por autorización del profesor. Iniciales de conformidad por completar: ___ / ___ / ___. Registro en Moodle y repositorio compartido con el docente: pendientes de confirmación.

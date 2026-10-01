"""Seis consultas compartidas por las fases C y D."""
PREGUNTAS = [
 '¿Cómo cambia la cantidad registrada por mes y frente al mes anterior?',
 '¿Qué departamentos concentran la mayor cantidad registrada?',
 '¿Cómo se distribuye la cantidad por año, zona y sexo?',
 '¿Qué armas o medios predominan y cómo se distribuyen por sexo?',
 '¿Qué relación existe entre las cantidades urbanas y rurales por municipio?',
 '¿Cómo se distribuyen las cantidades mensuales de cada departamento?']
SQL = [
'''WITH mensual AS (
 SELECT t.anio, t.mes, SUM(h.cantidad) AS cantidad,
        COUNT(DISTINCT t.fecha) AS dias_con_registro
 FROM p1_homicidios.hecho_homicidios h
 JOIN p1_homicidios.dim_tiempo t ON h.tiempo_id=t.tiempo_id
 GROUP BY t.anio,t.mes
), cambios AS (
 SELECT *, LAG(cantidad) OVER (ORDER BY anio,mes) AS cantidad_anterior
 FROM mensual
)
SELECT *, cantidad-cantidad_anterior AS cambio_absoluto,
 ROUND(100.0*(cantidad-cantidad_anterior)/NULLIF(cantidad_anterior,0),2) AS cambio_pct
FROM cambios ORDER BY anio,mes''',
'''WITH totales AS (
 SELECT u.cod_departamento,u.departamento,SUM(h.cantidad) AS cantidad
 FROM p1_homicidios.hecho_homicidios h
 JOIN p1_homicidios.dim_ubicacion u ON h.ubicacion_id=u.ubicacion_id
 GROUP BY u.cod_departamento,u.departamento
)
SELECT *, RANK() OVER (ORDER BY cantidad DESC) AS posicion,
 ROUND(100.0*cantidad/SUM(cantidad) OVER (),2) AS participacion_pct
FROM totales ORDER BY cantidad DESC,cod_departamento''',
'''SELECT t.anio,u.zona,s.sexo,SUM(h.cantidad) AS cantidad
FROM p1_homicidios.hecho_homicidios h
JOIN p1_homicidios.dim_tiempo t ON h.tiempo_id=t.tiempo_id
JOIN p1_homicidios.dim_ubicacion u ON h.ubicacion_id=u.ubicacion_id
JOIN p1_homicidios.dim_sexo s ON h.sexo_id=s.sexo_id
GROUP BY t.anio,u.zona,s.sexo ORDER BY t.anio,u.zona,s.sexo''',
'''SELECT c.arma_medio,s.sexo,SUM(h.cantidad) AS cantidad
FROM p1_homicidios.hecho_homicidios h
JOIN p1_homicidios.dim_contexto c ON h.contexto_id=c.contexto_id
JOIN p1_homicidios.dim_sexo s ON h.sexo_id=s.sexo_id
GROUP BY c.arma_medio,s.sexo ORDER BY cantidad DESC,c.arma_medio,s.sexo''',
'''SELECT u.cod_departamento,u.departamento,u.cod_municipio,u.municipio,
 SUM(CASE WHEN u.zona='URBANA' THEN h.cantidad ELSE 0 END) AS urbana,
 SUM(CASE WHEN u.zona='RURAL' THEN h.cantidad ELSE 0 END) AS rural,
 SUM(h.cantidad) AS cantidad
FROM p1_homicidios.hecho_homicidios h
JOIN p1_homicidios.dim_ubicacion u ON h.ubicacion_id=u.ubicacion_id
GROUP BY u.cod_departamento,u.departamento,u.cod_municipio,u.municipio
ORDER BY cantidad DESC,u.cod_municipio''',
'''WITH meses AS (
 SELECT DISTINCT anio,mes FROM p1_homicidios.dim_tiempo
), departamentos AS (
 SELECT DISTINCT cod_departamento,departamento FROM p1_homicidios.dim_ubicacion
), observado AS (
 SELECT u.cod_departamento,t.anio,t.mes,SUM(h.cantidad) AS cantidad
 FROM p1_homicidios.hecho_homicidios h
 JOIN p1_homicidios.dim_tiempo t ON h.tiempo_id=t.tiempo_id
 JOIN p1_homicidios.dim_ubicacion u ON h.ubicacion_id=u.ubicacion_id
 GROUP BY u.cod_departamento,t.anio,t.mes
)
SELECT d.cod_departamento,d.departamento,m.anio,m.mes,
 COALESCE(o.cantidad,0) AS cantidad
FROM departamentos d CROSS JOIN meses m
LEFT JOIN observado o ON o.cod_departamento=d.cod_departamento
 AND o.anio=m.anio AND o.mes=m.mes
ORDER BY d.cod_departamento,m.anio,m.mes''']

def interpretar(i, tabla):
    total = tabla.cantidad.sum()
    if i == 0:
        mayor=tabla.loc[tabla.cantidad.idxmax()]
        return f'El archivo contiene {len(tabla)} meses y suma {total:,.0f} unidades de CANTIDAD. El máximo mensual es {mayor.cantidad:,.0f} en {int(mayor.anio)}-{int(mayor.mes):02d}; el cambio calculado describe el archivo, cuya cobertura de días es anómala.'
    if i == 1:
        r=tabla.iloc[0]
        return f'{r.departamento} ocupa el primer lugar con {r.cantidad:,.0f} unidades ({r.participacion_pct:.2f}% del archivo). Son cantidades absolutas; sin población y cobertura verificadas no representan tasas de riesgo.'
    if i == 2:
        r=tabla.loc[tabla.cantidad.idxmax()]
        return f'La combinación más frecuente es {int(r.anio)}, {r.zona}, {r.sexo}: {r.cantidad:,.0f} unidades. La consulta cruza tres dimensiones y conserva {total:,.0f} unidades; las diferencias son descriptivas.'
    if i == 3:
        g=tabla.groupby('arma_medio').cantidad.sum().sort_values(ascending=False)
        return f'{g.index[0]} concentra {g.iloc[0]:,.0f} unidades ({100*g.iloc[0]/total:.2f}%). La separación por sexo describe registros, sin establecer causalidad ni riesgo individual.'
    if i == 4:
        r=tabla.iloc[0]
        return f'Se observan {len(tabla)} municipios; {r.municipio} reúne {r.cantidad:,.0f} unidades. La correlación de Pearson urbana-rural es {tabla.urbana.corr(tabla.rural):.3f}; está afectada por tamaño municipal, cobertura y valores extremos.'
    return f'La cuadrícula contiene {len(tabla)} combinaciones departamento-mes; su mediana es {tabla.cantidad.median():.1f} unidades. Los {int(tabla.cantidad.eq(0).sum())} ceros significan ausencia de filas en el archivo para esa combinación, no ausencia confirmada de homicidios.'

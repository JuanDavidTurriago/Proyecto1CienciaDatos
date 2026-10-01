# Lectura de los avances y decisiones de implementación

La autoridad para el entregable es `Proyecto 1.pdf`, por solicitud del grupo. Los cuatro Markdown recibidos son guías de actividades; no contienen trabajo previo resuelto, comentarios del profesor ni evidencias de entrega.

| Documento | Requisito | Implementación / estado |
|---|---|---|
| Avance 1 | Grupo, dataset, lectura inicial, pregunta y acuerdo | Grupo identificado; exploración incluida; pregunta y acuerdo en README. Registro, firmas, aprobación del dataset y repo compartido pendientes de confirmación. |
| Avance 2 | Hecho, 3 dimensiones, granularidad y diagrama revisado | Una tabla de hechos y cuatro dimensiones; diseño final en PDF; modelo editable DBML. No se inventan comentarios del docente. |
| Avance 3 | Tipos, surrogate keys, FKs, conservación de filas y carga | ETL con validaciones y carga PostgreSQL. Su permiso para SQLite queda superado por el requisito explícito del PDF. Reflexión incremental en B. |
| Avance 4 | Tipos de variables, descriptivos, IQR y tres gráficos | EDA adicional con histograma/KDE, boxplot y correlación de medidas derivadas. Se mantiene separado del diseño dimensional que el PDF llama Fase A. |

## Matriz de rúbrica

| Fase | Peso | Evidencia |
|---|---:|---|
| A: diseño | 25% | `fase_a_diseño.pdf`: granularidad, justificación, atributos, claves y diagrama. |
| B: ETL | 30% | `fase_b_etl.ipynb`: CSV con pandas, normalización, tipos, claves, validación, SQLAlchemy y DATABASE_URL. |
| C: SQL | 20% | `fase_c_sql.ipynb`: seis preguntas, seis consultas reales, tablas e interpretaciones; Q3 agrupa tres dimensiones; Q1 usa LAG y Q2 RANK. |
| D: figuras | 20% | `fase_d_visualizaciones.ipynb`: ocho figuras derivadas de Q1-Q6, cuatro familias mínimas e insights Markdown calculados. |
| E: informe/oral | 5% | `informe.pdf`, cinco páginas; guion oral de ocho minutos. La exposición depende del grupo. |

## Decisiones de datos

- **Unidad del hecho:** una fila del archivo recibido. No se asegura que sea un evento único ni una víctima individual. El indicador aditivo es CANTIDAD.
- **Duplicados:** 4.383 repeticiones exactas posteriores a la primera aparición. Se conservan porque una combinación de fecha, lugar y categorías puede representar varios hechos. Tampoco se afirma que todos sean eventos distintos.
- **Fechas:** solo aparecen días 1 a 12; 864 fechas distintas. Puede haber filtrado o un problema de transformación previo, pero el archivo no permite identificar la causa. No se intercambian día/mes ni se imputan fechas.
- **Municipio vacío:** se normalizan espacios y se usa la etiqueta no vacía del mismo código si es única. Toda corrección se cuenta en la auditoría; el original queda preservado.
- **Códigos:** departamento y municipio son nominales, no medidas continuas. Se guardan como texto de 2 y 5 posiciones y se comprueba su relación de prefijo.
- **Tasas:** no hay denominadores de población; se presentan cantidades y participaciones, sin inferir riesgo territorial ni causalidad.
- **Recarga:** transacción completa sobre esquema dedicado, con restricciones permanentes. No se usa `to_sql(if_exists='replace')` porque eliminaría el esquema de restricciones.
- **Procedencia:** el Excel fue localizado en la carpeta indicada por el usuario. Su nombre no prueba el origen oficial. El CSV incluido es una conversión, no se presenta como descarga oficial cruda.

## Orden de trabajo del grupo

1. Revisar el diseño y comprender las unidades antes de ejecutar.
2. Confirmar fuente/cobertura con el proveedor o docente. Conservar la versión analizada.
3. Ejecutar B, revisar controles y luego ejecutar C y D.
4. Revisar los tres hallazgos del informe, ensayar el guion y completar las firmas.
5. Comprobar los pendientes administrativos y cargar `grupo-1-p1.zip` cuando corresponda.

## Diferencias documentales pendientes

El PDF fija entrega para 23/24-sep-2026; los avances 3 y 4 dicen 30-sep. La fecha efectiva requiere confirmación docente. El esquema del ZIP se conserva y se añaden datos, código y documentos de apoyo necesarios para reproducir el trabajo. No se ha publicado un repositorio ni se ha enviado información a Moodle.

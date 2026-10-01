# Evidencia de ejecución

La versión incluida se ejecutó contra PostgreSQL 16 en una base local de Docker. Los resultados detallados están en `validacion.json` y las salidas guardadas en los cinco notebooks.

- Recarga completa repetida: mismas filas y valores, sin acumulación.
- Inserción inválida con CANTIDAD=0: rechazada por CHECK; la transacción conserva la carga anterior.
- Fecha inválida: rechazada durante la transformación, antes de cargar.
- Seis consultas: todas concilian la suma de CANTIDAD; serie mensual y distribución por departamento contrastadas con agrupaciones independientes en pandas.
- Cuatro claves foráneas físicas: comprobadas en el catálogo de PostgreSQL.
- Exploración, EDA, B, C y D: ejecución completa en kernels nuevos, sin errores.
- Fase D: ocho imágenes y ocho insights renderizados como Markdown; Fase C: seis interpretaciones Markdown.
- Diseño: tres páginas. Informe: cinco páginas. Se revisó visualmente la totalidad de los PDF y las ocho figuras.
- ZIP: estructura obligatoria presente, integridad del archivo verificada, `.env` y clave local excluidos.

Estas pruebas verifican el funcionamiento con el archivo recibido. No certifican procedencia oficial, cobertura completa, aprobación del docente, inscripción en Moodle ni realización de la exposición.

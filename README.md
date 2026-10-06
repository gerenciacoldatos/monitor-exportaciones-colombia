# Monitor de Exportaciones de Colombia

Tablero interactivo de **Colombia en Datos** con las exportaciones de bienes de Colombia, enero de 2023 a agosto de 2026: valor FOB y peso neto por departamento de origen, país de destino, grupo de productos, intensidad tecnológica, capítulo y subpartida arancelaria, modo de transporte, empresa y concentración (IHH).

## Archivos

- `index.html`: el tablero, autocontenido (datos incluidos). Se abre directo en el navegador o se publica con GitHub Pages.
- `datos/exportaciones-2023-2026.json`: los datos agregados que usa el tablero (millones de US$ FOB y miles de toneladas).
- `fuente/plantilla.html`: la plantilla del tablero; `__DATA__` se reemplaza por el JSON.
- `fuente/preparar_datos.py`: script que arma el JSON a partir de la consulta de exportaciones.

## Actualizar con un nuevo mes

1. Correr `fuente/preparar_datos.py` con la nueva consulta para regenerar el JSON.
2. Reemplazar `__DATA__` en la plantilla por el JSON (escapando `</` como `<\/`) y guardar como `index.html`.

## Fuente y notas

DIAN, registros de exportaciones procesados por Colombia en Datos, consistentes con el boletín EXPO del DANE (5 de octubre de 2026). Cifras provisionales. La base viene agregada por una dimensión a la vez, así que los filtros de cada sección no se cruzan entre sí.

Mapas: SVG Maps (@svg-maps/colombia, CC BY 4.0) y Natural Earth vía world-atlas. Gráficos con Apache ECharts.

Colombia en Datos · Datos que conectan, decisiones que transforman.

# Ruta-Cafetera

## Requisitos
Python 3.12, uv.

## Instalación
make install

En Windows (sin `make`), usar los mismos comandos con `uv`:

    uv sync --all-groups
    uv run pytest -q
    uv run ruff check .
    uv run streamlit run app/streamlit_app.py

## Reproducir resultados
(se completa por fase: make data, make r1, ...)

Las descargas de OSMnx usan el catálogo de servidores Overpass definido en
`src/rutas/data/descarga.py`. Si un servidor falla, se prueba el siguiente; el
servidor que respondió queda registrado en los metadatos de cada red.

## Ejecutar la aplicación
make app

## Máquina de medición
Medición oficial en Windows 11 Pro con Python 3.12.16 (ver `docs/decisiones.md`, D1).
Procesador / RAM: (por definir)

## Fecha de descarga de OSM
(por completar en Fase 1)
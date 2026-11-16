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
Medición oficial (ver `docs/decisiones.md`, D1):
- Procesador: AMD Ryzen 5 3400G (4 núcleos físicos, 8 lógicos)
- RAM: 17,1 GB
- SO: Windows 11 Pro (10.0.26200)
- Python: 3.12.16 (gestionado con uv)

## Datos de OSM (Fase 1)
Descarga: 2026-11-09 con OSMnx 2.1.1, desde `maps.mail.ru` (Overpass).

| Red | Nodos (V) | Aristas (E) |
|---|---|---|
| Radio 2 km | 1.648 | 3.658 |
| Radio 5 km | 4.301 | 9.714 |
| Radio 10 km | 5.960 | 13.442 |
| Radio 20 km | 8.773 | 20.045 |
| Departamento | 8.807 | 20.153 |

Procesamiento (R1): componente fuertemente conexa del departamento con 8.791 nodos y 20.132 aristas; CSR con 19.973 aristas (tras quitar 122 paralelas y 37 bucles).
## Ejecutar la aplicación (R5)
Comando:

```
uv run streamlit run app/streamlit_app.py
```

Requisito: `data/processed/graph_csr.npz` (junto con `places.csv`, `nodes.csv` y `hull.json`), generado por el pipeline de R1 y no versionado. No necesita OSMnx. Opcional: `RUTAS_DATA_DIR` apunta la app a otra carpeta de datos procesados (se usa en las pruebas).

Vistas (menú lateral):
- **Ruta:** elige origen y destino por nombre; muestra el tiempo en minutos y la ruta en un mapa.
- **Envolvente:** polígono de la envolvente convexa del departamento con los lugares como marcadores.
- **Itinerario:** elige partida y de 6 a 8 atractivos; compara el recorrido óptimo (Held-Karp) con el voraz y avisa si supera 11 h.
- **Resultados:** tablas de `results/` (con su unidad de tiempo) y las gráficas de `figures/`.

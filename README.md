# Ruta-Cafetera

Aplicación y experimentos para analizar redes viales del Quindío, calcular
caminos mínimos, construir la envolvente convexa y comparar algoritmos de
recorrido de atractivos turísticos.

## Requisitos

- Python 3.12 o posterior.
- [`uv`](https://docs.astral.sh/uv/).
- Acceso a Internet solo para descargar las redes de OpenStreetMap o instalar
    las dependencias por primera vez.

Todos los comandos se ejecutan desde la raíz del repositorio.

## Instalación

```bash
uv sync --all-groups
```

En Linux o macOS también se puede usar:

```bash
make install
```

El proyecto usa un entorno administrado por `uv`; por eso los comandos de
Python, pruebas y Streamlit se ejecutan con `uv run`.

## Puesta en marcha rápida

Si el repositorio ya contiene los artefactos de `data/processed/`, `results/`
y `figures/`, basta con instalar las dependencias y lanzar:

```bash
uv sync --all-groups
uv run streamlit run app/streamlit_app.py
```

La aplicación se abre en la dirección local que muestra Streamlit, normalmente
`http://localhost:8501`.

También puede usarse:

```bash
make app
```

La app necesita estos archivos en `data/processed/`:

- `graph_csr.npz`
- `nodes.csv`
- `places.csv`
- `hull.json`

La vista **Resultados** además lee los CSV de `results/` y las imágenes de
`figures/`. La app no descarga datos ni vuelve a ejecutar los experimentos al
abrirse.

## Reproducción completa

### 1. Descargar las redes de OSM

Este paso es opcional si los archivos `.graphml` ya están en `data/raw/` y
puede tardar varios minutos. Descarga las cuatro redes por radio y la red del
departamento:

```bash
uv run python -m rutas.data.descarga todo
```

Comandos alternativos:

```bash
uv run python -m rutas.data.descarga radios
uv run python -m rutas.data.descarga departamento
uv run python -m rutas.data.descarga radios --radio 2
```

Las descargas usan los servidores Overpass definidos en
`src/rutas/data/descarga.py`. Si uno falla, se prueba el siguiente. Cada red
queda guardada como `data/raw/<nombre>.graphml` y con sus metadatos en
`data/raw/<nombre>.meta.json`.

### 2. Validar entradas y preparar pares

El catálogo y la tabla de municipios vecinos son entradas del proyecto. El
catálogo debe estar en `data/raw/catalogo.csv` y los vecinos en
`data/raw/vecinos_municipios.csv`.

```bash
uv run python -m rutas.data.catalogo
uv run python -m rutas.data.pares
```

El primer comando valida el catálogo; el segundo genera los 20 pares de
medición en `data/raw/pares_dijkstra.csv`.

### 3. Procesar la red para la aplicación

El siguiente comando lee `data/raw/quindio.graphml` y genera la representación
CSR junto con los nodos y lugares asignados:

```bash
uv run python -m rutas.graph.procesar
```

Escribe `graph_csr.npz`, `nodes.csv` y `places.csv` en `data/processed/`.

### 4. Ejecutar los experimentos

Ejecuta las fases en este orden:

```bash
uv run python -m rutas.experiments.r1_componente
uv run python -m rutas.experiments.r2_dijkstra
uv run python -m rutas.experiments.r3_envolvente
uv run python -m rutas.experiments.r4_viajante
```

Los experimentos escriben sus tablas en `results/` y los metadatos en
`results/_meta/`. R3 también genera `data/processed/hull.json`, necesario para
la vista **Envolvente**.

### 5. Generar las figuras

```bash
uv run python -m rutas.report.figuras
```

Las imágenes se guardan en `figures/` y se muestran en la vista **Resultados**.

## Verificación

```bash
uv run pytest -q
uv run ruff check .
```

Con `make` están disponibles los mismos pasos:

```bash
make test
make lint
make format
```

`make format` aplica el formateo de Ruff; no es necesario para ejecutar la
aplicación.

## Configuración de datos de la app

Por defecto, Streamlit lee `data/processed/`. Para usar otra carpeta de datos
procesados:

```bash
RUTAS_DATA_DIR=/ruta/a/data/processed \
    uv run streamlit run app/streamlit_app.py
```

En Windows PowerShell:

```powershell
$env:RUTAS_DATA_DIR = "C:\ruta\a\data\processed"
uv run streamlit run app/streamlit_app.py
```

## Vistas de la aplicación

- **Ruta:** selecciona origen y destino y calcula el camino más rápido.
- **Envolvente:** muestra la envolvente convexa y los lugares del catálogo.
- **Itinerario:** compara Held-Karp con la heurística voraz para recorridos de
    6 a 8 atractivos.
- **Resultados:** presenta las tablas de `results/` y las figuras de
    `figures/`.

## Datos y resultados registrados

La descarga oficial se realizó el 2026-11-09 con OSMnx 2.1.1, desde
`maps.mail.ru` (Overpass).

| Red | Nodos (V) | Aristas (E) |
|---|---:|---:|
| Radio 2 km | 1.648 | 3.658 |
| Radio 5 km | 4.301 | 9.714 |
| Radio 10 km | 5.960 | 13.442 |
| Radio 20 km | 8.773 | 20.045 |
| Departamento | 8.807 | 20.153 |

El procesamiento R1 conserva una componente fuertemente conexa de 8.791
nodos y 20.132 aristas. La representación CSR final tiene 19.973 aristas,
después de quitar 122 paralelas y 37 bucles.

La medición oficial se documenta en `docs/decisiones.md` (D1): AMD Ryzen 5
3400G, 17,1 GB de RAM, Windows 11 Pro y Python 3.12.16 gestionado con `uv`.

## Documentación adicional

- `specs/`: especificaciones de cada fase y contratos de datos.
- `docs/decisiones.md`: decisiones técnicas y protocolo de medición.
- `docs/verificacion_mapa.md`: verificación de la visualización cartográfica.
- `docs/auditoria_repo.md`: estado de auditoría y artefactos del repositorio.

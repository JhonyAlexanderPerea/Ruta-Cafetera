# Spec: R5 · Aplicación demostrativa

**Autor:** Claude (borrador con el grupo) · **Revisor:** <pendiente: nombre distinto del autor> · **Estado:** borrador

## Objetivo
Una aplicación Streamlit que muestre los resultados de R1 a R4 y permita dos cálculos en vivo: la ruta origen-destino (Dijkstra con cola de prioridad) y el itinerario de un día (Held-Karp y heurística voraz). Se evalúa que muestre los resultados y que funcione siguiendo el README, no su diseño visual.

## Entradas y salidas
- **Entrada (solo lectura):**
  - `data/processed/graph_csr.npz` (grafo CSR de R1; no versionado, se genera con el pipeline de R1).
  - `data/processed/nodes.csv` (`idx, osmid, lat, lon, x_utm, y_utm`).
  - `data/processed/places.csv` (`id, nombre, municipio, categoria, lat, lon, duracion_visita_min, nodo_idx, osmid, dist_nodo_m, a_mas_de_500m`).
  - `data/processed/hull.json` (`crs_utm`, `vertices` con `x_utm, y_utm, lat, lon`).
  - `results/r2_matriz_tiempos.csv` (40×40, segundos, fila i a columna j; primera fila y columna = ids).
  - `results/r1_tamano_red.csv`, `results/r1_tiempos_componente.csv`, `results/r2_dijkstra.csv`, `results/r2_cociente.csv`, `results/r3_envolvente.csv`, `results/r4_exactas.csv`, `results/r4_heuristica.csv`, `results/r4_itinerario.csv`.
  - `figures/` (gráficas de R1 a R4 ya generadas).
- **Salida:** ninguna escritura en disco. La app no modifica datos ni resultados.
- **Código:**
  - `app/streamlit_app.py`: solo interfaz (Streamlit y `streamlit-folium`). Sin lógica de negocio.
  - `src/rutas/app_servicios.py`: funciones puras de cálculo y carga, probables con tests (ver más abajo).
  - `tests/test_app_servicios.py` y `tests/test_app_smoke.py`.

## Restricciones
- **Sin OSMnx ni NetworkX** en `app/` ni en `app_servicios.py` (regla de R5: lee `data/processed/`, `results/`, `figures/`).
- La app **no recalcula** R1 a R4 de forma completa. Solo recalcula en vivo: una ruta Dijkstra y un itinerario de 6 a 8 atractivos.
- Los algoritmos se importan de `rutas.algorithms` (implementación propia). No se duplican.

## Comportamiento esperado

### Vista 1: Ruta
1. Elegir origen y destino entre los 40 lugares de `places.csv` (menú por nombre).
2. Si origen y destino son el mismo, mostrar un mensaje y no calcular.
3. Calcular con `dijkstra` de cola de prioridad (`dijkstra_heap`) desde `nodo_idx` del origen hasta `nodo_idx` del destino.
4. Mostrar en un mapa de Folium la ruta (polilínea con `lat, lon` de `nodes.csv` por cada nodo del `path`) y el tiempo de viaje en minutos (`cost / 60`).
5. Si el destino no es alcanzable (`cost` es `None`), mostrar un mensaje claro (no debería pasar por R1, pero se maneja).

### Vista 2: Envolvente
1. Polígono de `hull.json["vertices"]` (lat, lon) sobre el mapa del departamento.
2. Centrar el mapa en el centroide de los vértices. Mostrar en la misma vista los lugares del catálogo como marcadores.
3. Mostrar el número de vértices y el conjunto de puntos a partir de `r3_envolvente.csv` como dato de contexto.

### Vista 3: Itinerario
1. Elegir partida (por defecto `cab_01`, Plaza de Bolívar en Armenia).
2. Elegir entre 6 y 8 atractivos (solo categoría `atractivo`, menú múltiple).
3. Validación: menos de 6 o más de 8 atractivos → mensaje claro y no calcular. Un atractivo repetido no es posible en el menú.
4. Calcular el recorrido óptimo con `tsp_heldkarp` y el recorrido voraz con `tsp_greedy`, ambos sobre la matriz de `r2_matriz_tiempos.csv` (segundos, convertidos a minutos para mostrar).
5. Mostrar, para cada recorrido: orden de visita, desplazamientos, visitas (`duracion_visita_min` de cada atractivo), y duración total (visitas + desplazamientos). Mostrar la diferencia entre ambos (minutos y %).
6. Si la duración total de cualquiera supera 11 h (660 min), mostrar una advertencia. **No se quitan atractivos automáticamente** en esta vista; la regla de corte está en R4 (`r4_itinerario.csv`).

### Vista 4: Resultados
1. Tablas: `r1_tamano_red.csv`, `r1_tiempos_componente.csv`, `r2_cociente.csv`, `r2_dijkstra.csv`, `r3_envolvente.csv`, `r4_exactas.csv`, `r4_heuristica.csv`, `r4_itinerario.csv`.
2. Gráficas: las imágenes de `figures/` (se muestran tal cual; si una falta, se indica con un mensaje y no se rompe la vista).
3. Cada tabla y gráfica muestra su unidad de tiempo en el encabezado (requisito de la sección 5 del enunciado).

### Carga y caché
- El grafo se carga una sola vez con `st.cache_resource`. Las tablas CSV y el JSON se cargan con `st.cache_data`.
- Si falta un archivo de `data/processed/` o de `results/`, la vista correspondiente muestra un mensaje que dice qué archivo falta y cómo generarlo. La app no se cae.

### Entradas inválidas (resumen)
| Caso | Comportamiento |
|---|---|
| origen = destino | mensaje, sin cálculo |
| menos de 6 o más de 8 atractivos | mensaje, sin cálculo |
| archivo faltante | mensaje con el archivo, la vista se omite |
| `cost is None` en Dijkstra | mensaje de no alcanzable |

## Funciones de `app_servicios.py` (contrato)
- `cargar_grafo(ruta) -> CSRGraph`: envuelve `CSRGraph.load`.
- `cargar_lugares(ruta) -> list[dict]`: lee `places.csv` con tipos (floats, ints, bool).
- `cargar_nodos(ruta) -> dict[int, tuple[float, float]]`: `idx -> (lat, lon)`.
- `cargar_matriz(ruta) -> tuple[list[str], list[list[float]]]`: ids y matriz en segundos.
- `ruta_optima(g, nodos_latlon, origen_nodo, destino_nodo) -> dict`: `{"tiempo_min", "polilinea"} | {"error"}`.
- `itinerario(matriz, ids, duraciones, partida, atractivos) -> dict`: `{"heldkarp": {...}, "voraz": {...}, "diferencia_min", "diferencia_pct"}`, donde cada recorrido trae `orden`, `desplazamiento_min`, `visita_min`, `total_min`.
- `validar_itinerario(atractivos) -> str | None`: mensaje de error o `None`.

## Casos de prueba
1. **Ruta, caso a mano:** grafo diminuto (3 nodos, aristas con tiempos conocidos). La ruta y el tiempo coinciden con el cálculo a mano.
2. **Ruta, mismo origen y destino:** `ruta_optima` devuelve error sin llamar a Dijkstra.
3. **Ruta, verificación:** en la red real, el tiempo de `ruta_optima` coincide con `dijkstra` de cola de prioridad y con `r2_dijkstra.csv` para los pares de esa tabla.
4. **Itinerario, caso a mano:** matriz 3×3 + partida; Held-Karp da el óptimo esperado; la voraz no es menor que el óptimo.
5. **Itinerario, validación:** 5 atractivos → error; 9 → error; 6 y 8 → sin error.
6. **Itinerario, coherencia:** el orden visita cada atractivo una vez y el costo recalculado desde la matriz coincide con el reportado.
7. **Diferencia:** `diferencia_min` = voraz − Held-Karp ≥ 0.
8. **Carga:** `cargar_matriz` lee 40×40 y las ids coinciden con `places.csv`.
9. **Smoke de la app (`streamlit.testing.v1.AppTest`):** la app arranca sin excepciones; las cuatro vistas están presentes; con un archivo faltante (ruta temporal) muestra el mensaje y no lanza excepción.

## Cómo se mide
La app no es un experimento: no se mide su tiempo como requisito. Sí se verifica con los tests de arriba. Las tablas de R4 que muestra la app son las ya generadas en `results/`.

## Decisiones abiertas (para el grupo)
- **Fuente de tiempos en vivo:** la app usa `r2_matriz_tiempos.csv` para el itinerario (rápido, consistente con R4). Alternativa: recalcular con Dijkstra; más lento y sin ganancia para la nota.
- **Advertencia de 11 h sin poda automática:** la app avisa pero no quita atractivos. Si el grupo quiere poda en la app, hay que decidir el criterio (el de R4 está en D14).
- **Partida por defecto:** Armenia (`cab_01`, Plaza de Bolívar), según el enunciado.

## Criterio de terminado
- [ ] `app_servicios.py` con tests en verde.
- [ ] Smoke de la app con `AppTest` en verde.
- [ ] `make app` (o `uv run streamlit run app/streamlit_app.py`) levanta la app.
- [ ] README con pasos para correrla en local, sin OSMnx.
- [ ] Las cuatro vistas muestran datos reales de `data/processed/` y `results/`.
- [ ] `make test` y `make lint` en verde.
- [ ] PARADA 7: una persona ajena al código levanta la app solo con el README.

# Spec: R1 · Modelo de la red vial

**Autor:** Claude (borrador para el grupo) · **Revisor:** <pendiente> · **Estado:** borrador (decisiones D4, D8 y tratamiento de lugares >500 m pendientes de PARADA 2)

## Objetivo
Convertir la red vial del Quindío (OSMnx) en un grafo dirigido con tiempo de viaje por arista, quedarse con su componente fuertemente conexa y guardar el grafo en formato CSR, junto con los nodos y la asociación de cada lugar del catálogo.

## Entradas y salidas
- **Entrada:**
  - `data/raw/quindio.graphml` (departamento, descargado 2026-11-09 con OSMnx 2.1.1).
  - `data/raw/catalogo.csv` (40 lugares; provisional hasta PARADA 1).
- **Salida:**
  - `data/processed/graph_csr.npz`: `indptr` (int64, V+1), `indices` (int32, E'), `dist_m` (float64), `time_s` (float64).
  - `data/processed/nodes.csv`: `idx, osmid, lat, lon, x_utm, y_utm` (UTM 18N, EPSG:32618).
  - `data/processed/places.csv`: id, datos del lugar, `nodo_idx`, `osmid`, `dist_nodo_m`, `a_mas_de_500m`.
  - Reporte de nodos y aristas antes y después de filtrar la componente (salida de `rutas.graph.procesar`).
- **Archivos que lee / escribe:** lee los dos de entrada. Escribe los tres de salida (no versionados el `.npz`, ver `.gitignore`).
- **Código:** `src/rutas/graph/pesos.py`, `csr.py`, `memoria.py`, `lugares.py`, `procesar.py`.

## Comportamiento esperado

**1. Velocidad y tiempo (D8).** `time_s = dist_m / (velocidad / 3,6)`. La velocidad de cada arista:
1. `maxspeed` explícito de OSM (si es numérico; si es lista, el primer valor).
2. Residencial: 30 km/h.
3. Troncal: 50 km/h (urbana o nacional, sin dato explícito).
4. Primaria: 50 km/h.
5. Secundaria, terciaria, no clasificada y otras: 30 km/h.
6. Respaldo: 30 km/h.

El tiempo es una **estimación del modelo**, no el tiempo real de recorrido.

**2. Componente fuertemente conexa.** `ox.truncate.largest_component(G, strongly=True)`. Todo el resto del proyecto trabaja solo con esa componente: garantiza que cualquier lugar es alcanzable desde cualquier otro, de modo que Dijkstra no devuelve infinitos, la matriz de tiempos no tiene huecos y el problema del viajante siempre tiene solución.

**3. Limpieza para CSR.** Aristas paralelas: se conserva la de menor `time_s` (con su `dist_m`). Bucles propios: se descartan. Ambos conteos se reportan.

**4. Asociación de lugares.** Cada lugar se asocia al nodo de la componente más cercano en línea recta, en UTM 18N. Si el nodo queda a más de 500 m, el lugar se marca con `a_mas_de_500m = True`.

**5. Entradas inválidas.** Si falta `quindio.graphml` o `catalogo.csv`, el pipeline termina con código 1 y un mensaje claro. Si una arista no tiene `length`, el pipeline se detiene: no hay tiempo de viaje sin distancia.

## Complejidad esperada (con fuente)
- **Pesos:** tiempo O(E), memoria O(E).
- **Componente fuertemente conexa:** `ox.truncate.largest_component(strongly=True)` (OSMnx 2.1.1) llama a `nx.strongly_connected_components` (NetworkX 3.7), implementado con una versión iterativa del algoritmo de Tarjan (documentación de NetworkX 3.7, referencia a Tarjan y Zwick). Tiempo O(V+E) y memoria O(V+E): Tarjan, R. E. (1972), "Depth-First Search and Linear Graph Algorithms", *SIAM Journal on Computing* 1(2), pp. 146–160. Verificado en el código instalado; la cota O(V+E) viene del artículo de 1972 y su acceso no se revisó en línea.
- **Conversión a CSR:** tiempo O(V+E log E) por el ordenamiento de las aristas; memoria O(V+E).
- **Asociación de lugares (fuerza bruta con NumPy):** tiempo O(L·V), con L lugares y V nodos; memoria O(V).
- **Estimación de memoria (con los valores reales, V = 8.791, E = 19.973):**
  - Matriz de adyacencia: 8.791² × 8 bytes ≈ **618,3 MB**.
  - Listas de adyacencia (CSR): 19.973 × 12 + 8.792 × 8 bytes ≈ **0,31 MB**.
  - Se elige **listas**, porque el grafo es disperso (≈ 2,3 aristas por nodo).

## Casos de prueba
1. **Caso pequeño resuelto a mano** (`test_csr.py`): grafo de 3 nodos con una arista paralela y un bucle. Arreglos esperados: `indptr=[0,1,2,2]`, `indices=[1,2]`, `dist_m=[30,70]`, `time_s=[3,7]`, y reporte `paralelas_reducidas=1, bucles_descartados=1`.
2. **Casos límite:**
   - Velocidad explícita gana sobre el tipo de vía; lista de velocidades; tipo con lista; enlace (`_link`) usa su tipo base; `maxspeed` no numérico cae al tipo (`test_pesos.py`).
   - Lugar a ~100 m de un nodo se asigna a ese nodo; lugar a más de 500 m se marca (`test_lugares.py`).
   - Round trip `save`/`load` del CSR (`test_csr.py`).
3. **Verificación contra otra fuente:**
   - La distancia de asignación coincide con un cálculo independiente con pyproj y `math.hypot` (`test_lugares.py`).
   - Los conteos de la componente se comparan con `ox.load_graphml` y con el `.meta.json` de la descarga.
   - Pendiente: validar el número de nodos y aristas de la componente con NetworkX sobre el mismo grafo.

## Cómo se mide
Esta fase no es un requerimiento de medición de rendimiento. La medición de `largest_component(strongly=True)` (tabla de V, E, V+E y tiempo en 2, 5, 10 y 20 km y el departamento) va en la Fase 3 con el protocolo de la sección 6 del enunciado: misma máquina (Windows, D1), mediana de 5 repeticiones, semilla 42 (no aplica aquí), y el cronómetro solo alrededor de la llamada.

## Resultados del procesamiento (departamento, 2026-11-10)

| Etapa | Nodos (V) | Aristas (E) |
|---|---|---|
| Red descargada | 8.807 | 20.153 |
| Componente fuertemente conexa | 8.791 | 20.132 |
| CSR (tras quitar 122 paralelas y 37 bucles) | 8.791 | 19.973 |

- **Lugares a más de 500 m de su nodo:** `at_03` (Valle de Cocora) y `at_11` (El Paraíso del Bambú y La Guadua). La distancia máxima es 1.063 m.

## Decisiones de PARADA 2 (aprobadas)
- **Lugares a más de 500 m:** se conservan y se documentan (D9): `at_03` y `at_11`.
- **Velocidad en troncales de ruta nacional sin dato:** 50 km/h, como supuesto documentado (D10).
- **Velocidades (D8):** aprobadas con el ajuste de troncales urbanas a 50 km/h.

## Criterio de terminado
- [ ] Pesos calculados con la regla D8 y tests en verde.
- [ ] Componente fuertemente conexa y CSR generados desde `data/raw/quindio.graphml`.
- [ ] `places.csv` con todos los lugares del catálogo validado (PARADA 1).
- [ ] Tabla de tamaños antes y después en el README.
- [ ] Tiempos de `largest_component` medidos en Fase 3 con el protocolo.
- [ ] Decisiones de lugares >500 m y de velocidades confirmadas por el grupo (PARADA 2).

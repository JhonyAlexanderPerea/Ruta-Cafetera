# Spec: R4 · Ruta óptima de recorrido (viajante asimétrico)

**Autor:** Claude (borrador con el grupo) · **Revisor:** JhonyAlexanderPerea (asignado, pendiente de revisión) · **Estado:** implementada (revisión pendiente); decisiones D13 y D14 aprobadas en PARADA 6

## Objetivo
Dado un lugar de partida y k lugares a visitar, encontrar el recorrido de menor tiempo total que sale de la partida, visita cada lugar una vez y regresa. Se usa la matriz de tiempos de R2 (asimétrica).

## Entradas y salidas
- **Entrada:** `results/r2_matriz_tiempos.csv` (40×40, en segundos, fila i a columna j) y `data/processed/places.csv`.
- **Salida:**
  - `results/r4_exactas.csv`: k, tiempo de fuerza bruta (ms), tiempo de Held-Karp (ms), con "no completada" si pasa el límite.
  - `results/r4_heuristica.csv`: k, instancias, brecha promedio (%), brecha máxima (%).
  - `results/r4_itinerario.csv`: orden, lugar, desplazamiento (min), visita (min), acumulado (h), y las filas de regreso y totales.
- **Código:** `src/rutas/algorithms/tsp_bruteforce.py`, `tsp_heldkarp.py`, `tsp_greedy.py`.

## Convención de las funciones
`tsp_*(c, start, nodes) -> (costo, orden)`:
- `c`: matriz de tiempos (lista de listas o arreglo), `c[i][j]` = tiempo de i a j.
- `start`: índice de la partida.
- `nodes`: índices de los lugares a visitar, sin la partida.
- `orden`: los `nodes` en el orden de visita, **sin** repetir la partida.
- `costo`: incluye el regreso desde el último lugar a la partida.

## Comportamiento esperado
1. **Fuerza bruta:** prueba todas las permutaciones de `nodes` (`itertools.permutations` como estructura de apoyo). Devuelve la de menor costo.
2. **Held-Karp:** programación dinámica sobre subconjuntos (ver recurrencia). Devuelve el orden de visita, no solo el costo.
3. **Voraz (heurística):** desde la partida, va al lugar no visitado de menor `c[actual][j]`, y al final regresa a la partida. Propuesta del grupo (ver D13).
4. **Dirigido:** `c[i][j]` puede ser distinto de `c[j][i]`. Ningún algoritmo supone simetría.
5. **Entradas inválidas:** lista vacía de lugares devuelve costo `c[start][start]` (0) y orden vacío. Un índice repetido o fuera de rango lanza `ValueError`.

## Recurrencia de Held-Karp (fijada antes de programar)
Sea `s` la partida, y para un subconjunto `S` de lugares y un lugar `j ∈ S`:

- **Caso base:** `dp[{j}][j] = c[s][j]`.
- **Recurrencia:** `dp[S][j] = min_{i ∈ S \ {j}} ( dp[S \ {j}][i] + c[i][j] )`.
- **Óptimo:** `min_{j ∈ T} ( dp[T][j] + c[j][s] )`, donde `T` son todos los lugares.
- **Reconstrucción:** se guarda, para cada `(S, j)`, el predecesor `i` que minimiza la recurrencia. Desde el mejor `j` final se retrocede hasta la partida.

**Justificación de la subestructura óptima:** si un recorrido óptimo que termina en `j` y visita `S` pasa por `i` justo antes de `j`, el tramo hasta `i` debe ser óptimo para `S \ {j}` terminando en `i`; si no, se reemplazaría por uno mejor. Con pesos no negativos y sin el requisito de simetría, el argumento vale igual.

## Complejidad esperada (con fuente)
- **Fuerza bruta:** tiempo O(k!·k), memoria O(k). Fuente: Cormen et al., *Introduction to Algorithms* (cap. de programación dinámica y problema del viajante como referencia de costos). [Edición y página por confirmar.]
- **Held-Karp:** tiempo O(2^k · k²), memoria O(2^k · k) para la tabla `dp` y el predecesor. Fuente: Held y Karp (1962), "A dynamic programming approach to sequencing problems", *Journal of the Society for Industrial and Applied Mathematics* 10(1), pp. 196–210. [Verificar el acceso al artículo.]
- **Voraz:** tiempo O(k²), memoria O(k).
- **Estimación de memoria de Held-Karp:** con k = 12, la tabla tiene 2^12 · 12 = 49.152 celdas de 8 bytes (≈ 0,4 MB) más los predecesores. Se contrasta con la medición.

## Casos de prueba
1. **Caso de 4 lugares resuelto a mano** (matriz pequeña asimétrica). Fuerza bruta y Held-Karp dan el mismo óptimo y el mismo orden.
2. **Casos límite:** `nodes` vacío; un solo lugar; índice repetido (error).
3. **Coherencia:** en cada solución el orden visita cada lugar exactamente una vez, y el costo recalculado desde la matriz coincide con el reportado.
4. **Fuerza bruta frente a Held-Karp:** mismo costo óptimo en instancias aleatorias con k ≤ 8.
5. **Voraz:** su costo nunca es menor que el óptimo.
6. **Matrices asimétricas aleatorias:** las propiedades anteriores se cumplen con c no simétrica.

## Cómo se mide
Protocolo de la sección 6: máquina oficial (D1), mediana de 5 repeticiones, límite de 5 minutos, solo la llamada cronometrada. Para k de 5 a 12, o hasta que una ejecución pase el límite. Las instancias se eligen al azar de todo el catálogo, sin Armenia, con semilla derivada de (SEED, k, número de instancia). La partida es Armenia.

## Decisiones de PARADA 6 (aprobadas)
- **Heurística (D13):** voraz del vecino más cercano dirigido, aprobada.
- **Atractivos del itinerario y regla de corte a 11 h (D14):** aprobados. Los atractivos son provisionales (semilla 42) y el grupo puede elegirlos a mano.

## Criterio de terminado
- [x] Tres solvers con tests en verde (15 pasan con `uv run pytest -k "tsp or heldkarp or bruteforce or greedy"`).
- [x] Verificación cruzada de fuerza bruta y Held-Karp (incluida en esos tests).
- [x] Experimentos generados: `results/r4_exactas.csv`, `r4_heuristica.csv`, `r4_itinerario.csv`, `r4_ejemplo_voraz.csv`. Pendiente confirmar que la calidad de la heurística cubre k=5, 8, 10 y 12 con ≥ 5 instancias.
- [ ] Citas de Held-Karp y de Cormen confirmadas.
- [ ] Revisión por una persona distinta del autor.

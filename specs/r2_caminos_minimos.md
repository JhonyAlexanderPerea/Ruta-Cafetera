# Spec: R2 · Caminos mínimos (Dijkstra)

**Autor:** Claude (borrador con el grupo) · **Revisor:** <pendiente: nombre distinto del autor> · **Estado:** implementada (revisión pendiente)

## Objetivo
Implementar Dijkstra en dos versiones (búsqueda lineal O(V²) y cola de prioridad O((V+E) log V)), medirlas en la red del departamento y calcular la matriz de tiempos entre los lugares del catálogo.

## Entradas y salidas
- **Entrada:** `data/processed/graph_csr.npz` (CSR, tiempos en segundos), `data/processed/places.csv` (nodo de cada lugar), `data/raw/pares_dijkstra.csv` (20 pares; 10 con `usa_lineal=True`).
- **Salida:** `results/r2_dijkstra.csv` (origen, destino, versión, tiempo de viaje, nodos explorados, tiempo en ms, estado), `results/r2_cociente.csv` (mediana, mínimo y máximo del cociente lineal / heap), `results/r2_matriz_tiempos.csv` (40×40 en segundos), `results/_meta/r2_dijkstra.json`.
- **Código:** `src/rutas/algorithms/dijkstra_heap.py`, `dijkstra_lineal.py`, `resultado.py`; `src/rutas/experiments/r2_dijkstra.py`.

## Comportamiento esperado
1. **Parada:** ambas versiones se detienen al sacar el destino.
2. **Explorados:** un nodo cuenta una sola vez, la primera vez que sale de la cola. Las entradas obsoletas no cuentan.
3. **Ruta:** se reconstruye con el predecesor de cada nodo.
4. **Pesos:** no negativos (los tiempos del CSR salen de velocidades positivas).
5. **Destino inalcanzable:** costo `inf`, sin ruta. Sin destino: costo y ruta `None`, y se devuelven las distancias a todos los nodos.
6. **Matriz:** versión con cola de prioridad sin destino, desde cada lugar.
7. **Tiempos:** protocolo de la sección 6 (mediana de 5, límite de 5 min, solo la llamada cronometrada, máquina oficial D1). Costo y explorados se calculan una vez, fuera del cronómetro.

## Complejidad esperada (con fuente)
- **Lineal:** tiempo O(V²), memoria O(V). Fuente: Cormen, Leiserson, Rivest, Stein, *Introduction to Algorithms* (capítulo de Dijkstra). [Edición y página por confirmar.]
- **Cola de prioridad (binario, heapq):** tiempo O((V+E) log V), memoria O(V+E). Misma fuente.
- **Matriz completa:** 40 ejecuciones de la versión con cola de prioridad sin destino.

## Casos de prueba
1. **Caso pequeño a mano:** grafo de 4 nodos; costo 5 por 0→1→2→3 (`test_dijkstra.py`).
2. **Casos límite:** destino inalcanzable; sin destino; parada al sacar el destino (`test_dijkstra.py`).
3. **Verificación contra NetworkX:** 20 grafos aleatorios (`test_dijkstra.py`).
4. **La ruta suma el costo** y **ambas versiones dan lo mismo** (`test_dijkstra.py`).
5. **Verificación de la matriz:** diagonal cero, sin infinitos, desigualdad triangular con tolerancia de 1e-6 s (`test_r2_helpers.py`).
6. **Medición real:** en los 10 pares, heap y lineal dan el mismo tiempo de viaje (0 diferencias).

## Resultados (departamento, 2026-11-10)
- **Cociente lineal / heap en 10 pares:** mediana 211,0; mínimo 35,0; máximo 226,7.
- **Matriz 40×40:** diagonal cero; sin infinitos; 777 pares asimétricos (la red es dirigida); desigualdad triangular cumplida con tolerancia de 1e-6 s. Las violaciones exactas de punto flotante llegan a 5e-12 s.

## Criterio de terminado
- [x] Ambas versiones y tests en verde.
- [x] Verificación con NetworkX y ruta válida.
- [x] Experimento de 20 y 10 pares, cociente y matriz.
- [ ] Citas de Cormen con edición y página confirmadas.
- [ ] Revisión por una persona distinta del autor.

# Spec: R3 · Envolvente convexa

**Autor:** Claude (borrador con el grupo) · **Revisor:** JhonyAlexanderPerea (asignado, pendiente de revisión) · **Estado:** implementada (revisión pendiente)

## Objetivo
Calcular la envolvente convexa de los nodos de la red vial del departamento y de nubes aleatorias, con un algoritmo de divide y vencerás propio, y compararlo contra `scipy.spatial.ConvexHull`.

## Entradas y salidas
- **Entrada:**
  - `data/processed/nodes.csv` (`x_utm`, `y_utm`): coordenadas UTM redondeadas al entero más cercano, sin repetidos.
  - Nubes aleatorias: 1.000, 10.000 y 50.000 puntos enteros en [0, 10⁶), semilla 42 (`rutas.config.SEED`).
- **Salida:**
  - `results/r3_envolvente.csv`: `conjunto, n, vertices, tiempo_propio_ms, tiempo_scipy_ms, cociente, coinciden`.
  - `data/processed/hull.json`: vértices de la envolvente de la red en UTM y en lat/lon (lo usa la vista Envolvente de R5).
  - `results/_meta/r3_envolvente.json`: máquina, versiones, commit, semilla, repeticiones y límite.
- **Código:** `src/rutas/algorithms/convex_hull_dc.py` (algoritmo), `src/rutas/experiments/r3_envolvente.py` (experimento).

## Comportamiento esperado
1. Se ordenan los puntos por (x, y) y se parten en dos mitades. Cada mitad da su envolvente en sentido antihorario.
2. La fusión busca las dos tangentes comunes (inferior y superior) entre las envolventes izquierda y derecha, y arma la envolvente del conjunto.
3. Salida: vértices en sentido antihorario, sin colineales ni duplicados.
4. Casos límite:
   - 0 puntos: lista vacía.
   - 1 punto: ese punto.
   - 2 o 3 puntos: cadena monótona de Andrew.
   - Todos colineales: los dos extremos.
   - Puntos colineales sobre un lado: no son vértices.
5. Coordenadas enteras y aritmética exacta (`int` de Python), sin errores de punto flotante.
6. Entradas inválidas: el algoritmo no valida tipos; se asume lista de pares de números.

## Complejidad esperada
- **Tiempo:** T(n) = 2 T(n/2) + O(n), así que O(n log n) en el peor caso. No depende de la distribución de los puntos.
- **Memoria:** O(n) para las listas de la recursión; profundidad de recursión log₂ n.
- **Recurrencia:** T(n) = 2 T(n/2) + O(n).
- **Referencia de la clasificación:** divide y vencerás en su forma clásica. Decisión D12 (`docs/decisiones.md`).

## Casos de prueba
1. **Caso a mano:** cuadrado con puntos interiores; la envolvente son los 4 vértices.
2. **Límite:** puntos colineales sobre los lados no son vértices; todos colineales devuelve los dos extremos; duplicados se eliminan; 1, 2 y 3 puntos.
3. **Verificación contra SciPy:** 40 nubes aleatorias con semillas 0 a 39 (`tests/test_convex_hull.py`) y nubes agrupadas. Todas coinciden con `scipy.spatial.ConvexHull`.
4. **Experimento:** `coinciden = True` en las cuatro filas de `results/r3_envolvente.csv` (red y tres cuadrados).

Estado verificado al escribir esta spec: `uv run pytest -q tests/test_convex_hull.py` → 49 pasan.

## Cómo se mide
Protocolo de la sección 6: máquina oficial (D1), mediana de 5 repeticiones, límite de 5 minutos, solo la llamada cronometrada. La carga de datos y la generación de las nubes quedan fuera del cronómetro. Semilla 42. Se miden el algoritmo propio y `ConvexHull` sobre los mismos puntos.

Resultados registrados (`results/r3_envolvente.csv`):

| Conjunto | n | Vértices | Propio (ms) | SciPy (ms) | Cociente |
|---|---|---|---|---|---|
| Red | 8.791 | 14 | 59,75 | 3,35 | 17,84 |
| Cuadrado | 1.000 | 22 | 6,81 | 2,30 | 2,96 |
| Cuadrado | 10.000 | 24 | 70,65 | 3,87 | 18,26 |
| Cuadrado | 50.000 | 30 | 414,41 | 10,41 | 39,81 |

Limitación: el algoritmo propio está en Python puro y SciPy/Qhull en C. El cociente mide la implementación, no el algoritmo.

## Decisiones (ver `docs/decisiones.md`)
- **D12:** fusión por tangentes, aprobada en PARADA 5. Se descartó QuickHull porque su peor caso es O(n²).
- **D5:** la opción de algoritmo quedó resuelta por D12.

## Criterio de terminado
- [x] Algoritmo con tests en verde (49 pasan).
- [x] Verificación contra SciPy en nubes aleatorias y en la red.
- [x] `results/r3_envolvente.csv`, `data/processed/hull.json` y `results/_meta/r3_envolvente.json` generados.
- [ ] Revisión por una persona distinta del autor.

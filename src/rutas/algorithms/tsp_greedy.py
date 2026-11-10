"""Heurística voraz: vecino más cercano dirigido. O(k²).

Desde la partida, va siempre al lugar no visitado de menor c[actual][j];
al final regresa a la partida.
No garantiza el óptimo (ver tests y specs/r4_recorrido.md, caso de comparación con Held-Karp).
"""

from __future__ import annotations

from rutas.algorithms.tsp_common import costo_recorrido, validar_entrada


def tsp_greedy(c, start: int, nodes: list[int]) -> tuple[float, list[int]]:
    validar_entrada(c, start, nodes)
    pendientes = list(nodes)
    orden: list[int] = []
    actual = start
    while pendientes:
        siguiente = min(pendientes, key=lambda j: (c[actual][j], j))
        orden.append(siguiente)
        pendientes.remove(siguiente)
        actual = siguiente
    return costo_recorrido(c, start, orden), orden

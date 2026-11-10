"""Viajante por fuerza bruta: todas las permutaciones de los lugares. O(k!·k)."""

from __future__ import annotations

import itertools

from rutas.algorithms.tsp_common import costo_recorrido, validar_entrada


def tsp_bruteforce(c, start: int, nodes: list[int]) -> tuple[float, list[int]]:
    validar_entrada(c, start, nodes)
    if not nodes:
        return 0.0, []
    mejor_costo = float("inf")
    mejor_orden: list[int] = []
    for perm in itertools.permutations(nodes):
        costo = costo_recorrido(c, start, list(perm))
        if costo < mejor_costo:
            mejor_costo = costo
            mejor_orden = list(perm)
    return mejor_costo, mejor_orden

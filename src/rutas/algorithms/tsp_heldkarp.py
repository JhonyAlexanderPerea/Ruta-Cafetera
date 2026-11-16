"""Viajante exacto por Held-Karp (programación dinámica sobre subconjuntos).

Recurrencia y justificación en specs/r4_recorrido.md. Tiempo O(2^k · k²), memoria O(2^k · k).
"""

from __future__ import annotations

import math

from rutas.algorithms.tsp_common import validar_entrada


def tsp_heldkarp(c, start: int, nodes: list[int]) -> tuple[float, list[int]]:
    validar_entrada(c, start, nodes)
    k = len(nodes)
    if k == 0:
        return 0.0, []

    completo = (1 << k) - 1
    # dp[S][j]: costo mínimo de salir de start, visitar exactamente S y terminar en j (j en S).
    dp = [[math.inf] * k for _ in range(1 << k)]
    padre = [[-1] * k for _ in range(1 << k)]
    for j in range(k):
        dp[1 << j][j] = c[start][nodes[j]]

    for S in range(1, 1 << k):
        for j in range(k):
            if not (S >> j) & 1 or dp[S][j] == math.inf:
                continue
            for nxt in range(k):
                if (S >> nxt) & 1:
                    continue
                T = S | (1 << nxt)
                cand = dp[S][j] + c[nodes[j]][nodes[nxt]]
                if cand < dp[T][nxt]:
                    dp[T][nxt] = cand
                    padre[T][nxt] = j

    mejor_costo = math.inf
    fin = -1
    for j in range(k):
        cand = dp[completo][j] + c[nodes[j]][start]
        if cand < mejor_costo:
            mejor_costo = cand
            fin = j

    # Reconstrucción del orden desde el final hacia atrás.
    orden_idx = []
    S, j = completo, fin
    while j != -1:
        orden_idx.append(j)
        anterior = padre[S][j]
        S ^= 1 << j
        j = anterior
    orden_idx.reverse()
    return mejor_costo, [nodes[i] for i in orden_idx]

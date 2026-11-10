"""Dijkstra con cola de prioridad (heapq, eliminación perezosa). O((V + E) log V).

Cada nodo cuenta como explorado una sola vez: la primera vez que sale de la cola.
Las entradas obsoletas de la cola se descartan sin contarlas.
"""

from __future__ import annotations

import heapq
import math

from rutas.algorithms.resultado import DijkstraResult
from rutas.graph.csr import CSRGraph


def _reconstruir(pred: list[int], origen: int, destino: int) -> list[int]:
    ruta = [destino]
    while ruta[-1] != origen:
        ruta.append(pred[ruta[-1]])
    ruta.reverse()
    return ruta


def dijkstra(g: CSRGraph, source: int, target: int | None = None) -> DijkstraResult:
    V = g.n_nodes
    dist = [math.inf] * V
    pred = [-1] * V
    hecho = [False] * V
    explored = 0
    dist[source] = 0.0
    cola = [(0.0, source)]

    while cola:
        d, u = heapq.heappop(cola)
        if hecho[u]:
            continue  # entrada obsoleta
        hecho[u] = True
        explored += 1
        if target is not None and u == target:
            break
        for k in range(g.indptr[u], g.indptr[u + 1]):
            v = int(g.indices[k])
            nd = d + float(g.time_s[k])
            if nd < dist[v]:
                dist[v] = nd
                pred[v] = u
                heapq.heappush(cola, (nd, v))

    if target is None:
        return DijkstraResult(dist=dist, pred=pred, explored=explored, cost=None, path=None)
    if math.isinf(dist[target]):
        return DijkstraResult(dist=dist, pred=pred, explored=explored, cost=math.inf, path=None)
    return DijkstraResult(
        dist=dist,
        pred=pred,
        explored=explored,
        cost=dist[target],
        path=_reconstruir(pred, source, target),
    )

"""Dijkstra con búsqueda lineal del mínimo. O(V^2).

El mínimo se busca con un recorrido lineal en Python puro sobre los nodos no visitados
(sin argmin de NumPy), para que la complejidad O(V^2) sea la que se estudia.
Misma parada y mismo conteo de explorados que la versión con cola de prioridad.
"""

from __future__ import annotations

import math

from rutas.algorithms.dijkstra_heap import _reconstruir
from rutas.algorithms.resultado import DijkstraResult
from rutas.graph.csr import CSRGraph


def dijkstra(g: CSRGraph, source: int, target: int | None = None) -> DijkstraResult:
    V = g.n_nodes
    dist = [math.inf] * V
    pred = [-1] * V
    hecho = [False] * V
    explored = 0
    dist[source] = 0.0

    while True:
        u = -1
        mejor = math.inf
        for i in range(V):
            if not hecho[i] and dist[i] < mejor:
                mejor = dist[i]
                u = i
        if u == -1:
            break  # no quedan nodos alcanzables
        hecho[u] = True
        explored += 1
        if target is not None and u == target:
            break
        for k in range(g.indptr[u], g.indptr[u + 1]):
            v = int(g.indices[k])
            nd = mejor + float(g.time_s[k])
            if nd < dist[v]:
                dist[v] = nd
                pred[v] = u

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

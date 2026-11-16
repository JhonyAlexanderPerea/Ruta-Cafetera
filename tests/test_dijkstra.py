import math
import random

import networkx as nx
import numpy as np
import pytest

from rutas.algorithms import dijkstra_heap, dijkstra_lineal
from rutas.graph.csr import CSRGraph

VERSIONES = [dijkstra_heap.dijkstra, dijkstra_lineal.dijkstra]


def _csr_desde_aristas(n, aristas):
    """aristas = [(u, v, tiempo)], nodos 0..n-1."""
    aristas = sorted(aristas)
    indptr = np.zeros(n + 1, dtype=np.int64)
    for u, _, _ in aristas:
        indptr[u + 1] += 1
    indptr = np.cumsum(indptr)
    indices = np.array([v for _, v, _ in aristas], dtype=np.int32)
    time_s = np.array([t for _, _, t in aristas], dtype=np.float64)
    dist_m = time_s.copy()
    return CSRGraph(indptr, indices, dist_m, time_s)


def _grafo_a_mano():
    # 0 -> 1 (2), 0 -> 2 (5), 1 -> 2 (1), 2 -> 3 (2), 1 -> 3 (7)
    return _csr_desde_aristas(4, [(0, 1, 2.0), (0, 2, 5.0), (1, 2, 1.0), (2, 3, 2.0), (1, 3, 7.0)])


@pytest.mark.parametrize("fn", VERSIONES)
def test_caso_pequeno_resuelto_a_mano(fn):
    r = fn(_grafo_a_mano(), 0, 3)

    assert r.cost == pytest.approx(5.0)  # 0 -> 1 -> 2 -> 3 = 2 + 1 + 2
    assert r.path == [0, 1, 2, 3]


@pytest.mark.parametrize("fn", VERSIONES)
def test_se_detiene_al_sacar_el_destino(fn):
    # Destino 1 es el más cercano: no debe explorar el resto.
    r = fn(_grafo_a_mano(), 0, 1)

    assert r.cost == pytest.approx(2.0)
    assert r.explored == 2  # origen y destino


@pytest.mark.parametrize("fn", VERSIONES)
def test_sin_destino_calcula_distancias_a_todos(fn):
    r = fn(_grafo_a_mano(), 0, None)

    assert r.cost is None
    assert r.path is None
    assert r.dist[3] == pytest.approx(5.0)
    assert r.explored == 4


@pytest.mark.parametrize("fn", VERSIONES)
def test_destino_inalcanzable_devuelve_infinito(fn):
    g = _csr_desde_aristas(3, [(0, 1, 1.0)])

    r = fn(g, 0, 2)

    assert math.isinf(r.cost)
    assert r.path is None


@pytest.mark.parametrize("fn", VERSIONES)
def test_comparacion_con_networkx_en_grafos_aleatorios(fn):
    rng = random.Random(42)
    for _ in range(20):
        n = rng.randint(4, 25)
        aristas = []
        for _ in range(rng.randint(n, 4 * n)):
            u, v = rng.randrange(n), rng.randrange(n)
            if u != v:
                aristas.append((u, v, rng.uniform(0.5, 10.0)))
        g = _csr_desde_aristas(n, aristas)
        G = nx.DiGraph()
        G.add_nodes_from(range(n))
        for u, v, t in aristas:
            if not G.has_edge(u, v) or G[u][v]["w"] > t:
                G.add_edge(u, v, w=t)

        destino = rng.randrange(n)
        r = fn(g, 0, destino)
        try:
            esperado = nx.dijkstra_path_length(G, 0, destino, weight="w")
        except nx.NetworkXNoPath:
            esperado = math.inf

        assert r.cost == pytest.approx(esperado, rel=1e-9) or (
            math.isinf(r.cost) and math.isinf(esperado)
        )


@pytest.mark.parametrize("fn", VERSIONES)
def test_la_ruta_suma_el_costo(fn):
    g = _grafo_a_mano()
    r = fn(g, 0, 3)

    total = 0.0
    for a, b in zip(r.path, r.path[1:], strict=False):
        k = next(k for k in range(g.indptr[a], g.indptr[a + 1]) if g.indices[k] == b)
        total += g.time_s[k]
    assert total == pytest.approx(r.cost)


def test_ambas_versiones_dan_el_mismo_costo():
    rng = random.Random(7)
    for _ in range(10):
        n = rng.randint(5, 30)
        aristas = [
            (u, v, rng.uniform(1.0, 9.0))
            for u in range(n)
            for v in range(n)
            if u != v and rng.random() < 0.2
        ]
        g = _csr_desde_aristas(n, aristas)
        for destino in range(n):
            a = dijkstra_heap.dijkstra(g, 0, destino)
            b = dijkstra_lineal.dijkstra(g, 0, destino)
            assert a.cost == pytest.approx(b.cost, abs=1e-9) or (
                math.isinf(a.cost) and math.isinf(b.cost)
            )

import networkx as nx
import numpy as np

from rutas.graph import csr
from rutas.graph.memoria import estimar_mb


def _grafo_diminuto():
    G = nx.MultiDiGraph()
    G.add_node(1, y=4.5, x=-75.6)
    G.add_node(2, y=4.51, x=-75.61)
    G.add_node(3, y=4.52, x=-75.62)
    G.add_edge(1, 2, length=50.0, travel_time=5.0)
    G.add_edge(1, 2, length=30.0, travel_time=3.0)  # paralela: gana la de menor tiempo
    G.add_edge(2, 2, length=10.0, travel_time=1.0)  # bucle propio: se descarta
    G.add_edge(2, 3, length=70.0, travel_time=7.0)
    return G


def test_convierte_grafo_diminuto_a_csr_esperado():
    g, reporte = csr.desde_networkx(_grafo_diminuto())

    assert g.indptr.tolist() == [0, 1, 2, 2]
    assert g.indices.tolist() == [1, 2]
    assert g.dist_m.tolist() == [30.0, 70.0]
    assert g.time_s.tolist() == [3.0, 7.0]
    assert reporte == {"paralelas_reducidas": 1, "bucles_descartados": 1}


def test_csr_round_trip_save_load(tmp_path):
    g, _ = csr.desde_networkx(_grafo_diminuto())
    ruta = tmp_path / "graph_csr.npz"

    g.save(ruta)
    cargado = csr.CSRGraph.load(ruta)

    assert np.array_equal(cargado.indptr, g.indptr)
    assert np.array_equal(cargado.indices, g.indices)
    assert np.array_equal(cargado.dist_m, g.dist_m)
    assert np.array_equal(cargado.time_s, g.time_s)
    assert cargado.n_nodes == 3
    assert cargado.n_edges == 2


def test_estimar_mb_matriz_y_listas_con_supuestos_explicitos():
    resultado = estimar_mb(V=8807, E=20153)

    # Matriz densa de float64: V*V*8 bytes.
    assert resultado["matriz_mb"] == round(8807 * 8807 * 8 / 1e6, 1)
    # Listas: E*(4 bytes índice + 8 bytes peso) + (V+1)*8 bytes de punteros.
    assert resultado["listas_mb"] == round((20153 * 12 + 8808 * 8) / 1e6, 2)
    assert resultado["listas_mb"] < resultado["matriz_mb"]
    assert "supuestos" in resultado

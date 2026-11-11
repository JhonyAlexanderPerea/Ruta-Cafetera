"""Pruebas de los servicios de la aplicación (specs/r5_aplicacion.md)."""

from __future__ import annotations

import csv
import itertools
import random
from pathlib import Path

import numpy as np
import pytest

from rutas import app_servicios as svc
from rutas.graph.csr import CSRGraph

RAIZ = Path(__file__).resolve().parents[1]


def _grafo_pequeno() -> CSRGraph:
    # 0->1 (60 s), 0->2 (300 s), 1->2 (120 s). El nodo 2 no sale a ningún lado.
    return CSRGraph(
        indptr=np.array([0, 2, 3, 3], dtype=np.int64),
        indices=np.array([1, 2, 2], dtype=np.int32),
        dist_m=np.array([10.0, 20.0, 50.0]),
        time_s=np.array([60.0, 300.0, 120.0]),
    )


NODOS = {0: (4.0, -75.0), 1: (4.1, -75.1), 2: (4.2, -75.2), 3: (4.3, -75.3)}


def test_ruta_optima_a_mano():
    r = svc.ruta_optima(_grafo_pequeno(), NODOS, 0, 2)
    assert r["tiempo_min"] == pytest.approx(3.0)
    assert r["polilinea"] == [NODOS[0], NODOS[1], NODOS[2]]


def test_ruta_optima_mismo_origen_destino_no_llama_dijkstra(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("dijkstra no debe llamarse")

    monkeypatch.setattr(svc, "dijkstra", _boom)
    r = svc.ruta_optima(_grafo_pequeno(), NODOS, 1, 1)
    assert "error" in r


def test_ruta_optima_inalcanzable():
    g = _grafo_pequeno()
    r = svc.ruta_optima(g, NODOS, 2, 0)
    assert "error" in r and "tiempo_min" not in r


def _matriz_aleatoria(n: int, semilla: int = 7) -> list[list[float]]:
    rng = random.Random(semilla)
    return [[0.0 if i == j else float(rng.randint(60, 3000)) for j in range(n)] for i in range(n)]


def _ids(n: int) -> list[str]:
    return [f"p{i}" for i in range(n)]


def test_itinerario_a_mano_en_linea():
    n = 7
    m = [[60.0 * abs(i - j) for j in range(n)] for i in range(n)]
    ids = _ids(n)
    dur = {i: 30.0 for i in ids}
    r = svc.itinerario(m, ids, dur, "p0", ids[1:])
    assert r["heldkarp"]["desplazamiento_min"] == pytest.approx(12.0)
    assert r["heldkarp"]["visita_min"] == pytest.approx(180.0)
    assert r["heldkarp"]["total_min"] == pytest.approx(192.0)
    assert r["voraz"]["desplazamiento_min"] >= r["heldkarp"]["desplazamiento_min"] - 1e-9
    assert r["diferencia_min"] >= 0


def test_itinerario_heldkarp_es_el_minimo_por_fuerza_bruta():
    n = 7
    m = _matriz_aleatoria(n)
    ids = _ids(n)
    dur = {i: 20.0 for i in ids}
    r = svc.itinerario(m, ids, dur, "p0", ids[1:])
    mejor = min(
        sum(m[a][b] for a, b in itertools.pairwise([0, *p, 0]))
        for p in itertools.permutations(range(1, n))
    )
    assert r["heldkarp"]["desplazamiento_min"] == pytest.approx(mejor / 60)
    assert r["voraz"]["desplazamiento_min"] >= r["heldkarp"]["desplazamiento_min"] - 1e-9
    assert r["diferencia_min"] == pytest.approx(
        r["voraz"]["total_min"] - r["heldkarp"]["total_min"]
    )
    assert r["diferencia_min"] >= 0


@pytest.mark.parametrize("cantidad,ok", [(5, False), (6, True), (8, True), (9, False)])
def test_validar_itinerario_cantidad(cantidad, ok):
    atr = [f"a{i}" for i in range(cantidad)]
    res = svc.validar_itinerario(atr)
    assert (res is None) == ok
    if not ok:
        assert isinstance(res, str) and res


def test_validar_itinerario_duplicado():
    assert svc.validar_itinerario(["a", "a", "b", "c", "d", "e"]) is not None


def test_itinerario_invalido_devuelve_error():
    ids = _ids(7)
    r = svc.itinerario(_matriz_aleatoria(7), ids, {i: 1.0 for i in ids}, "p0", ids[1:4])
    assert "error" in r and "heldkarp" not in r


def test_itinerario_coherencia():
    n = 9
    m = _matriz_aleatoria(n, semilla=11)
    ids = _ids(n)
    dur = {i: 15.0 + k for k, i in enumerate(ids)}
    atr = ids[2:9]
    r = svc.itinerario(m, ids, dur, "p0", atr)
    for clave in ("heldkarp", "voraz"):
        res = r[clave]
        assert sorted(res["orden"]) == sorted(atr)
        pos = {i: k for k, i in enumerate(ids)}
        ruta = [pos["p0"], *(pos[x] for x in res["orden"]), pos["p0"]]
        costo = sum(m[a][b] for a, b in itertools.pairwise(ruta)) / 60
        assert res["desplazamiento_min"] == pytest.approx(costo)
        assert res["visita_min"] == pytest.approx(sum(dur[a] for a in atr))
        assert res["total_min"] == pytest.approx(costo + res["visita_min"])


def test_cargar_matriz_temporal(tmp_path):
    f = tmp_path / "m.csv"
    f.write_text(",a,b\na,0.0,10.5\nb,20.0,0.0\n", encoding="utf-8")
    ids, m = svc.cargar_matriz(f)
    assert ids == ["a", "b"]
    assert m == [[0.0, 10.5], [20.0, 0.0]]


def test_cargar_lugares_tipos(tmp_path):
    f = tmp_path / "p.csv"
    f.write_text(
        "id,nombre,municipio,categoria,lat,lon,duracion_visita_min,nodo_idx,osmid,"
        "dist_nodo_m,a_mas_de_500m\n"
        "cab_01,Plaza,Armenia,cabecera,4.5,-75.6,,8215,100,51.6,False\n"
        "atr_01,Parque,Salento,atractivo,4.6,-75.5,90,12,200,600.0,True\n",
        encoding="utf-8",
    )
    lugares = svc.cargar_lugares(f)
    a, b = lugares
    assert a["duracion_visita_min"] is None
    assert isinstance(a["lat"], float) and isinstance(a["nodo_idx"], int)
    assert a["a_mas_de_500m"] is False
    assert b["duracion_visita_min"] == 90.0 and b["a_mas_de_500m"] is True


def test_cargar_nodos_temporal(tmp_path):
    f = tmp_path / "n.csv"
    f.write_text("idx,osmid,lat,lon,x_utm,y_utm\n0,9,4.5,-75.6,1.0,2.0\n", encoding="utf-8")
    assert svc.cargar_nodos(f) == {0: (4.5, -75.6)}


def test_datos_reales_matriz_y_lugares():
    places = RAIZ / "data/processed/places.csv"
    matriz = RAIZ / "results/r2_matriz_tiempos.csv"
    if not (places.exists() and matriz.exists()):
        pytest.skip("faltan places.csv o r2_matriz_tiempos.csv")
    ids, m = svc.cargar_matriz(matriz)
    assert len(ids) == 40 and len(m) == 40 and all(len(f) == 40 for f in m)
    assert ids == [p["id"] for p in svc.cargar_lugares(places)]


def _pares_dijkstra_reales():
    tabla = RAIZ / "results/r2_dijkstra.csv"
    if not tabla.exists():
        return []
    with open(tabla, newline="", encoding="utf-8") as f:
        return [
            (r["origen"], r["destino"], float(r["tiempo_viaje_s"]))
            for r in csv.DictReader(f)
            if r["version"] == "cola_prioridad" and r["estado"] == "completada"
        ]


@pytest.mark.skipif(
    not (RAIZ / "data/processed/graph_csr.npz").exists()
    or not (RAIZ / "results/r2_dijkstra.csv").exists(),
    reason="faltan graph_csr.npz o r2_dijkstra.csv (pipeline de R1 y R2)",
)
@pytest.mark.parametrize("origen,destino,esperado_s", _pares_dijkstra_reales())
def test_ruta_optima_coincide_con_r2_dijkstra(origen, destino, esperado_s):
    proc = RAIZ / "data/processed"
    g = svc.cargar_grafo(proc / "graph_csr.npz")
    nodos = svc.cargar_nodos(proc / "nodes.csv")
    lugares = {p["id"]: p for p in svc.cargar_lugares(proc / "places.csv")}
    r = svc.ruta_optima(g, nodos, lugares[origen]["nodo_idx"], lugares[destino]["nodo_idx"])
    assert "error" not in r
    # La tabla redondea a 2 decimales en segundos.
    assert r["tiempo_min"] * 60 == pytest.approx(esperado_s, abs=0.01)


# ---------- Datos extra para la interfaz (distancia, exploración, envolvente) ----------


def test_ruta_optima_distancia_y_velocidad():
    # Ruta 0->1->2: 10 m + 50 m = 60 m en 3 min.
    r = svc.ruta_optima(_grafo_pequeno(), NODOS, 0, 2)
    assert r["distancia_km"] == pytest.approx(0.06)
    assert r["velocidad_kmh"] == pytest.approx(0.06 / (3.0 / 60))
    assert r["nodos"] == [0, 1, 2]


def test_nodos_explorados_en_orden_de_cercania():
    g = _grafo_pequeno()
    pts = svc.nodos_explorados(g, NODOS, 0, 2)
    # Dijkstra fija 0 (0 s), 1 (60 s) y 2 (180 s): ese es el orden de exploración.
    assert pts == [NODOS[0], NODOS[1], NODOS[2]]


def test_nodos_explorados_respeta_el_maximo_y_conserva_extremos():
    n = 50
    g = CSRGraph(
        indptr=np.array([*range(n), n - 1, n - 1][: n + 1], dtype=np.int64),
        indices=np.arange(1, n, dtype=np.int32),
        dist_m=np.full(n - 1, 10.0),
        time_s=np.full(n - 1, 5.0),
    )
    nodos = {i: (4.0 + i / 100, -75.0) for i in range(n)}
    pts = svc.nodos_explorados(g, nodos, 0, n - 1, maximo=10)
    assert len(pts) <= 10
    assert pts[0] == nodos[0] and pts[-1] == nodos[n - 1]


def test_nodos_explorados_sin_ruta_devuelve_vacio():
    assert svc.nodos_explorados(_grafo_pequeno(), NODOS, 2, 0) == []


def test_metricas_envolvente_cuadrado():
    v = [
        {"x_utm": 0, "y_utm": 0},
        {"x_utm": 2000, "y_utm": 0},
        {"x_utm": 2000, "y_utm": 3000},
        {"x_utm": 0, "y_utm": 3000},
    ]
    m = svc.metricas_envolvente(v)
    assert m["area_km2"] == pytest.approx(6.0)
    assert m["perimetro_km"] == pytest.approx(10.0)
    assert m["vertices"] == 4


def test_itinerario_incluye_tramos_que_suman_el_desplazamiento():
    n = 7
    m = _matriz_aleatoria(n, semilla=3)
    ids = _ids(n)
    r = svc.itinerario(m, ids, {i: 10.0 for i in ids}, "p0", ids[1:])
    for clave in ("heldkarp", "voraz"):
        tramos = r[clave]["tramos_min"]
        assert len(tramos) == len(r[clave]["orden"]) + 1  # incluye el regreso a la partida
        assert sum(tramos) == pytest.approx(r[clave]["desplazamiento_min"])


@pytest.mark.parametrize(
    "minutos,texto",
    [(0, "0 min"), (45, "45 min"), (60, "1 h"), (65.4, "1 h 05 min"), (125, "2 h 05 min")],
)
def test_formato_duracion(minutos, texto):
    assert svc.formato_duracion(minutos) == texto


def test_ruta_optima_informa_nodos_explorados():
    r = svc.ruta_optima(_grafo_pequeno(), NODOS, 0, 2)
    assert r["explorados"] == 3


def test_distancia_recta_un_grado_de_latitud():
    assert svc.distancia_recta_km((4.0, -75.0), (5.0, -75.0)) == pytest.approx(111.19, abs=0.1)
    assert svc.distancia_recta_km((4.5, -75.6), (4.5, -75.6)) == 0.0


def test_tramos_polilinea_une_paradas_consecutivas():
    # 0->1->2 existe; 2 no sale a ningún lado, así que el tramo 2->0 queda vacío.
    legs = svc.tramos_polilinea(_grafo_pequeno(), NODOS, [0, 1, 2])
    assert legs[0] == [NODOS[0], NODOS[1]]
    assert legs[1] == [NODOS[1], NODOS[2]]


def test_tramos_polilinea_inalcanzable_devuelve_tramo_recto():
    legs = svc.tramos_polilinea(_grafo_pequeno(), NODOS, [2, 0])
    assert legs == [[NODOS[2], NODOS[0]]]

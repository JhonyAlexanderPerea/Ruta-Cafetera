"""Pipeline de R1: red cruda -> componente fuertemente conexa -> pesos -> CSR, nodos y lugares.

Lee `data/raw/<red>.graphml` y `data/raw/catalogo.csv`; escribe en `data/processed/`:
graph_csr.npz, nodes.csv y places.csv. Imprime el reporte de nodos y aristas antes y después.
"""

from __future__ import annotations

import csv
import json
import sys

import osmnx as ox

from rutas.config import DATA_PROCESSED, DATA_RAW
from rutas.graph import csr, lugares, pesos

RED = "quindio"


def _conteos(G) -> dict:
    return {"nodos": G.number_of_nodes(), "aristas": G.number_of_edges()}


def procesar(red: str = RED) -> dict:
    G = ox.load_graphml(DATA_RAW / f"{red}.graphml")
    antes = _conteos(G)

    for _, _, d in G.edges(data=True):
        d["travel_time"] = pesos.tiempo_s(d)

    G = ox.truncate.largest_component(G, strongly=True)
    despues = _conteos(G)

    g, limpieza = csr.desde_networkx(G)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    g.save(DATA_PROCESSED / "graph_csr.npz")

    nodos = sorted(G.nodes(data=True), key=lambda n: n[0])
    lista = [(osmid, d["y"], d["x"]) for osmid, d in nodos]
    xy, osmids = lugares.nodos_utm(lista)
    with open(DATA_PROCESSED / "nodes.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["idx", "osmid", "lat", "lon", "x_utm", "y_utm"])
        for i, ((osmid, lat, lon), (x, y)) in enumerate(zip(lista, xy, strict=True)):
            w.writerow([i, osmid, lat, lon, round(x, 3), round(y, 3)])

    with open(DATA_RAW / "catalogo.csv", encoding="utf-8", newline="") as f:
        catalogo = list(csv.DictReader(f))
    asignados = lugares.asignar(catalogo, xy, osmids)
    por_id = {a["id"]: a for a in asignados}
    with open(DATA_PROCESSED / "places.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "id",
                "nombre",
                "municipio",
                "categoria",
                "lat",
                "lon",
                "duracion_visita_min",
                "nodo_idx",
                "osmid",
                "dist_nodo_m",
                "a_mas_de_500m",
            ]
        )
        for lugar in catalogo:
            a = por_id[lugar["id"]]
            w.writerow(
                [
                    lugar["id"],
                    lugar["nombre"],
                    lugar["municipio"],
                    lugar["categoria"],
                    lugar["lat"],
                    lugar["lon"],
                    lugar["duracion_visita_min"],
                    a["nodo_idx"],
                    a["osmid"],
                    a["dist_nodo_m"],
                    a["a_mas_de_500m"],
                ]
            )

    return {
        "red": red,
        "antes": antes,
        "componente_fuerte": despues,
        "csr": {"V": g.n_nodes, "E": g.n_edges, **limpieza},
        "lugares_mas_de_500m": [a["id"] for a in asignados if a["a_mas_de_500m"]],
        "distancia_max_m": max(a["dist_nodo_m"] for a in asignados),
    }


if __name__ == "__main__":
    if not (DATA_RAW / "catalogo.csv").exists():
        print("Falta data/raw/catalogo.csv", file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps(procesar(), indent=2, ensure_ascii=False))

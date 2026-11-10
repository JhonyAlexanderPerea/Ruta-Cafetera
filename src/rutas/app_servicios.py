"""Servicios puros de la aplicación (R5): carga de datos y cálculos en vivo.

Sin OSMnx, NetworkX, Streamlit ni impresión. Ver specs/r5_aplicacion.md."""

from __future__ import annotations

import csv
from pathlib import Path

from rutas.algorithms.dijkstra_heap import dijkstra
from rutas.algorithms.tsp_greedy import tsp_greedy
from rutas.algorithms.tsp_heldkarp import tsp_heldkarp
from rutas.graph.csr import CSRGraph

MIN_ATRACTIVOS = 6
MAX_ATRACTIVOS = 8


def cargar_grafo(ruta: Path | str) -> CSRGraph:
    return CSRGraph.load(ruta)


def cargar_lugares(ruta: Path | str) -> list[dict]:
    lugares = []
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            dur = fila["duracion_visita_min"].strip()
            lugares.append(
                {
                    "id": fila["id"],
                    "nombre": fila["nombre"],
                    "municipio": fila["municipio"],
                    "categoria": fila["categoria"],
                    "lat": float(fila["lat"]),
                    "lon": float(fila["lon"]),
                    "duracion_visita_min": float(dur) if dur else None,
                    "nodo_idx": int(fila["nodo_idx"]),
                    "osmid": int(fila["osmid"]),
                    "dist_nodo_m": float(fila["dist_nodo_m"]),
                    "a_mas_de_500m": fila["a_mas_de_500m"].strip().lower() == "true",
                }
            )
    return lugares


def cargar_nodos(ruta: Path | str) -> dict[int, tuple[float, float]]:
    with open(ruta, newline="", encoding="utf-8") as f:
        return {int(r["idx"]): (float(r["lat"]), float(r["lon"])) for r in csv.DictReader(f)}


def cargar_matriz(ruta: Path | str) -> tuple[list[str], list[list[float]]]:
    """Ids y matriz de tiempos en segundos (primera fila y columna son ids)."""
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = list(csv.reader(f))
    ids = filas[0][1:]
    matriz = [[float(v) for v in fila[1:]] for fila in filas[1:]]
    return ids, matriz


def ruta_optima(
    g: CSRGraph,
    nodos_latlon: dict[int, tuple[float, float]],
    origen_nodo: int,
    destino_nodo: int,
) -> dict:
    if origen_nodo == destino_nodo:
        return {"error": "El origen y el destino son el mismo lugar."}
    res = dijkstra(g, origen_nodo, destino_nodo)
    if res.cost is None or res.path is None:
        return {"error": "El destino no es alcanzable desde el origen."}
    return {
        "tiempo_min": res.cost / 60,
        "polilinea": [nodos_latlon[n] for n in res.path],
    }


def validar_itinerario(atractivos: list[str]) -> str | None:
    if len(set(atractivos)) != len(atractivos):
        return "Hay atractivos repetidos."
    if not MIN_ATRACTIVOS <= len(atractivos) <= MAX_ATRACTIVOS:
        return (
            f"Elige entre {MIN_ATRACTIVOS} y {MAX_ATRACTIVOS} atractivos "
            f"(elegiste {len(atractivos)})."
        )
    return None


def itinerario(
    matriz: list[list[float]],
    ids: list[str],
    duraciones: dict[str, float],
    partida: str,
    atractivos: list[str],
) -> dict:
    error = validar_itinerario(atractivos)
    if error:
        return {"error": error}
    pos = {i: k for k, i in enumerate(ids)}
    inicio = pos[partida]
    nodos = [pos[a] for a in atractivos]
    visita_min = sum(duraciones[a] for a in atractivos)

    def armar(solver) -> dict:
        costo_s, orden = solver(matriz, inicio, nodos)
        desp = costo_s / 60
        return {
            "orden": [ids[k] for k in orden],
            "desplazamiento_min": desp,
            "visita_min": visita_min,
            "total_min": desp + visita_min,
        }

    hk, vz = armar(tsp_heldkarp), armar(tsp_greedy)
    dif = vz["total_min"] - hk["total_min"]
    return {
        "heldkarp": hk,
        "voraz": vz,
        "diferencia_min": dif,
        "diferencia_pct": 100 * dif / hk["total_min"] if hk["total_min"] else 0.0,
    }

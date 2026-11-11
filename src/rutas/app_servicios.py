"""Servicios puros de la aplicación (R5): carga de datos y cálculos en vivo.

Sin OSMnx, NetworkX, Streamlit ni impresión. Ver specs/r5_aplicacion.md."""

from __future__ import annotations

import csv
import itertools
import math
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
    dist_m = sum(_longitud_arista(g, u, v) for u, v in zip(res.path, res.path[1:], strict=False))
    tiempo_min = res.cost / 60
    return {
        "tiempo_min": tiempo_min,
        "distancia_km": dist_m / 1000,
        "velocidad_kmh": (dist_m / 1000) / (tiempo_min / 60) if tiempo_min else 0.0,
        "nodos": list(res.path),
        "polilinea": [nodos_latlon[n] for n in res.path],
    }


def _longitud_arista(g: CSRGraph, u: int, v: int) -> float:
    """Metros de la arista u->v (el CSR guarda una sola por par)."""
    for k in range(g.indptr[u], g.indptr[u + 1]):
        if int(g.indices[k]) == v:
            return float(g.dist_m[k])
    raise KeyError(f"no hay arista {u}->{v}")


def nodos_explorados(
    g: CSRGraph,
    nodos_latlon: dict[int, tuple[float, float]],
    origen_nodo: int,
    destino_nodo: int,
    maximo: int = 1500,
) -> list[tuple[float, float]]:
    """Posiciones de los nodos que Dijkstra fija antes de llegar al destino, en orden.

    Dijkstra fija los nodos por tiempo creciente, así que ordenar por `dist` reproduce
    el orden de exploración sin duplicar el algoritmo. Se reduce a `maximo` puntos."""
    res = dijkstra(g, origen_nodo, destino_nodo)
    if res.cost is None or res.path is None:
        return []
    fijados = sorted(
        (v for v, d in enumerate(res.dist) if d <= res.cost),
        key=lambda v: (res.dist[v], v == destino_nodo, v),
    )
    if len(fijados) > maximo > 1:
        paso = (len(fijados) - 1) / (maximo - 1)
        fijados = [fijados[round(i * paso)] for i in range(maximo)]
    return [nodos_latlon[v] for v in fijados]


def metricas_envolvente(vertices: list[dict]) -> dict:
    """Área (fórmula del zapatero), perímetro y vértices de un polígono en metros UTM."""
    xy = [(float(v["x_utm"]), float(v["y_utm"])) for v in vertices]
    pares = list(zip(xy, xy[1:] + xy[:1], strict=True))
    area = abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in pares)) / 2
    perimetro = sum(math.hypot(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in pares)
    return {"area_km2": area / 1e6, "perimetro_km": perimetro / 1000, "vertices": len(xy)}


def formato_duracion(minutos: float) -> str:
    """'45 min', '1 h', '2 h 05 min'."""
    total = round(minutos)
    h, m = divmod(total, 60)
    if h == 0:
        return f"{m} min"
    return f"{h} h" if m == 0 else f"{h} h {m:02d} min"


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
        recorrido = [inicio, *orden, inicio]
        return {
            "orden": [ids[k] for k in orden],
            "tramos_min": [matriz[a][b] / 60 for a, b in itertools.pairwise(recorrido)],
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

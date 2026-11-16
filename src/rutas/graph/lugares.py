"""Asociación de cada lugar del catálogo al nodo de la componente más cercano en línea recta (R1.4).

Distancia euclidiana en UTM zona 18N (EPSG:32618). Búsqueda por fuerza bruta con NumPy:
con ~9.000 nodos y ~40 lugares son ~360.000 distancias, que cuestan milisegundos.
No se usa cKDTree en tiempo de ejecución para no añadir una dependencia de SciPy.
"""

from __future__ import annotations

import numpy as np
from pyproj import Transformer

from rutas.config import UTM_EPSG

UMBRAL_M = 500.0
_A_UTM = Transformer.from_crs("EPSG:4326", f"EPSG:{UTM_EPSG}", always_xy=True)


def nodos_utm(nodos: list[tuple[int, float, float]]) -> tuple[np.ndarray, list[int]]:
    """nodos = [(osmid, lat, lon), ...] -> (arreglo (N, 2) en UTM, lista de osmid)."""
    osmids = [n[0] for n in nodos]
    xy = np.array([_A_UTM.transform(lon, lat) for _, lat, lon in nodos], dtype=np.float64)
    return xy, osmids


def asignar(lugares: list[dict], xy: np.ndarray, osmids: list[int]) -> list[dict]:
    """Asigna cada lugar al nodo más cercano. Devuelve una fila por lugar."""
    salida = []
    for lugar in lugares:
        px, py = _A_UTM.transform(float(lugar["lon"]), float(lugar["lat"]))
        d = np.hypot(xy[:, 0] - px, xy[:, 1] - py)
        i = int(np.argmin(d))
        salida.append(
            {
                "id": lugar["id"],
                "nodo_idx": i,
                "osmid": osmids[i],
                "dist_nodo_m": round(float(d[i]), 1),
                "a_mas_de_500m": bool(d[i] > UMBRAL_M),
            }
        )
    return salida

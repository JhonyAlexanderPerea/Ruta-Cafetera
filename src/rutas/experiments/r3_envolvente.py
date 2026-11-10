"""R3: envolvente convexa de los nodos de la red y de nubes aleatorias en un cuadrado.

Puntos: coordenadas UTM redondeadas al entero más cercano, sin repetidos (enunciado, R3).
Nubes aleatorias: 1.000, 10.000 y 50.000 puntos enteros en [0, 10^6), semilla 42.
Tiempos: protocolo de la sección 6 (mediana de 5, límite 5 min, solo la llamada cronometrada).
Referencia: scipy.spatial.ConvexHull (solo para verificar y comparar).

Salidas: results/r3_envolvente.csv, data/processed/hull.json (vértices en UTM y lat/lon),
results/_meta/r3_envolvente.json.
"""

from __future__ import annotations

import csv
import json
from functools import partial

import numpy as np
from pyproj import Transformer
from scipy.spatial import ConvexHull

from rutas.algorithms.convex_hull_dc import convex_hull
from rutas.bench import io as bio
from rutas.bench import machine_info
from rutas.bench.runner import measure
from rutas.config import DATA_PROCESSED, REPETITIONS, RESULTS, SEED, TIME_LIMIT_S, UTM_EPSG

TAMANOS = [1_000, 10_000, 50_000]
COLUMNAS = [
    "conjunto",
    "n",
    "vertices",
    "tiempo_propio_ms",
    "tiempo_scipy_ms",
    "cociente",
    "coinciden",
]


def _scipy_hull(pts: np.ndarray) -> np.ndarray:
    return ConvexHull(pts).vertices


def _nodos_enteros() -> list[tuple[int, int]]:
    with open(DATA_PROCESSED / "nodes.csv", encoding="utf-8", newline="") as f:
        return sorted(
            {(round(float(r["x_utm"])), round(float(r["y_utm"]))) for r in csv.DictReader(f)}
        )


def _nube(n: int, rng: np.random.Generator) -> list[tuple[int, int]]:
    puntos = set()
    while len(puntos) < n:
        faltan = n - len(puntos)
        lote = rng.integers(0, 1_000_000, size=(faltan, 2))
        puntos.update((int(x), int(y)) for x, y in lote)
    return sorted(puntos)


def _medir_conjunto(nombre: str, pts: list[tuple[int, int]]) -> dict:
    arr = np.array(pts, dtype=float)
    propio = convex_hull(pts)
    ref_idx = _scipy_hull(arr)
    esperado = {pts[i] for i in ref_idx}
    coinciden = set(propio) == esperado

    m_propio = measure(partial(convex_hull, pts), reps=REPETITIONS, timeout_s=TIME_LIMIT_S)
    m_scipy = measure(partial(_scipy_hull, arr), reps=REPETITIONS, timeout_s=TIME_LIMIT_S)
    if m_propio.completed and m_scipy.completed:
        t_p = round(m_propio.median_ms, 2)
        t_s = round(m_scipy.median_ms, 2)
        cociente = round(t_p / t_s, 2)
    else:
        t_p = t_s = cociente = "no completada"
    print(
        f"{nombre}: n={len(pts)} vértices={len(propio)} propio={t_p} ms scipy={t_s} ms", flush=True
    )
    return {
        "conjunto": nombre,
        "n": len(pts),
        "vertices": len(propio),
        "tiempo_propio_ms": t_p,
        "tiempo_scipy_ms": t_s,
        "cociente": cociente,
        "coinciden": coinciden,
    }


def _guardar_hull_json(vertices: list[tuple[int, int]]) -> None:
    inv = Transformer.from_crs(f"EPSG:{UTM_EPSG}", "EPSG:4326", always_xy=True)
    salida = []
    for x, y in vertices:
        lon, lat = inv.transform(x, y)
        salida.append({"x_utm": x, "y_utm": y, "lat": round(lat, 6), "lon": round(lon, 6)})
    (DATA_PROCESSED / "hull.json").write_text(
        json.dumps(
            {"crs_utm": f"EPSG:{UTM_EPSG}", "vertices": salida}, indent=1, ensure_ascii=False
        ),
        encoding="utf-8",
    )


def main() -> None:
    filas = []
    rng = np.random.default_rng(SEED)

    nodos = _nodos_enteros()
    filas.append(_medir_conjunto("nodos_de_la_red", nodos))
    _guardar_hull_json(convex_hull(nodos))

    for n in TAMANOS:
        filas.append(_medir_conjunto(f"cuadrado_{n}", _nube(n, rng)))

    bio.escribir_csv(RESULTS / "r3_envolvente.csv", COLUMNAS, filas)
    machine_info.guardar(
        "r3_envolvente",
        extra={
            "semilla": SEED,
            "repeticiones": REPETITIONS,
            "limite_s": TIME_LIMIT_S,
            "rango_cuadrado": [0, 1_000_000],
            "tamanos": TAMANOS,
        },
    )
    print("listo: results/r3_envolvente.csv y data/processed/hull.json")


if __name__ == "__main__":
    main()

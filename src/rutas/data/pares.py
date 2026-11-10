"""Genera los 20 pares origen-destino de medición de Dijkstra (R2) a partir del catálogo.

Regla (spec F1, decisión D4): un par "cercano" tiene sus dos lugares en el mismo
municipio o en municipios vecinos. Los 10 primeros pares (usa_lineal=True) incluyen
al menos 4 del mismo municipio y el resto de municipios vecinos distintos.
"""

from __future__ import annotations

import csv
import itertools
import math
import random
import sys
from pathlib import Path

from pyproj import Transformer

from rutas.config import DATA_RAW, SEED, UTM_EPSG

N_PARES = 20
N_LINEALES = 10
MIN_MISMO_MUNICIPIO = 4

VECINOS_CSV = DATA_RAW / "vecinos_municipios.csv"
CATALOGO_CSV = DATA_RAW / "catalogo.csv"
PARES_CSV = DATA_RAW / "pares_dijkstra.csv"
COLUMNAS_SALIDA = ["origen", "destino", "dist_recta_km", "mismo_municipio", "usa_lineal"]

_A_UTM = Transformer.from_crs("EPSG:4326", f"EPSG:{UTM_EPSG}", always_xy=True)


def cargar_vecinos(path: Path = VECINOS_CSV) -> set[frozenset[str]]:
    with open(path, encoding="utf-8", newline="") as f:
        return {frozenset((r["municipio_a"], r["municipio_b"])) for r in csv.DictReader(f)}


def _distancia_km(a: dict, b: dict) -> float:
    xa, ya = _A_UTM.transform(a["lon"], a["lat"])
    xb, yb = _A_UTM.transform(b["lon"], b["lat"])
    return math.hypot(xa - xb, ya - yb) / 1000


def _clave(a: dict, b: dict) -> frozenset[str]:
    return frozenset((a["id"], b["id"]))


def _orientar(rng: random.Random, a: dict, b: dict) -> tuple[dict, dict]:
    # La red es dirigida: el orden origen-destino se sortea.
    return (a, b) if rng.random() < 0.5 else (b, a)


def generar_pares(
    catalogo: list[dict], vecinos: set[frozenset[str]], seed: int = SEED
) -> list[dict]:
    rng = random.Random(seed)
    todos = list(itertools.combinations(catalogo, 2))

    mismo = [(a, b) for a, b in todos if a["municipio"] == b["municipio"]]
    vecinos_distintos = [
        (a, b)
        for a, b in todos
        if a["municipio"] != b["municipio"]
        and frozenset((a["municipio"], b["municipio"])) in vecinos
    ]
    necesarios_vecinos = N_LINEALES - MIN_MISMO_MUNICIPIO
    if len(mismo) < MIN_MISMO_MUNICIPIO or len(vecinos_distintos) < necesarios_vecinos:
        raise ValueError(
            "No hay suficientes pares cercanos para los 10 pares lineales "
            f"({len(mismo)} del mismo municipio, {len(vecinos_distintos)} entre vecinos)."
        )

    lineales = rng.sample(mismo, MIN_MISMO_MUNICIPIO) + rng.sample(
        vecinos_distintos, N_LINEALES - MIN_MISMO_MUNICIPIO
    )
    usados = {_clave(a, b) for a, b in lineales}
    resto = [(a, b) for a, b in todos if _clave(a, b) not in usados]
    if len(resto) < N_PARES - N_LINEALES:
        raise ValueError(
            f"El catálogo no tiene suficientes lugares para {N_PARES} pares distintos."
        )
    no_lineales = rng.sample(resto, N_PARES - N_LINEALES)

    salida = []
    for usa_lineal, pares in ((True, lineales), (False, no_lineales)):
        for a, b in pares:
            origen, destino = _orientar(rng, a, b)
            salida.append(
                {
                    "origen": origen["id"],
                    "destino": destino["id"],
                    "dist_recta_km": round(_distancia_km(a, b), 3),
                    "mismo_municipio": a["municipio"] == b["municipio"],
                    "usa_lineal": usa_lineal,
                    "municipio_origen": origen["municipio"],
                    "municipio_destino": destino["municipio"],
                }
            )
    return salida


def _leer_catalogo(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    for fila in filas:
        fila["lat"] = float(fila["lat"])
        fila["lon"] = float(fila["lon"])
    return sorted(filas, key=lambda fila: fila["id"])


def escribir_pares(pares: list[dict], path: Path = PARES_CSV) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS_SALIDA, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(pares)


def main() -> int:
    if not CATALOGO_CSV.exists():
        print(f"Falta {CATALOGO_CSV}. El catálogo lo arma el grupo (Fase 1).", file=sys.stderr)
        return 1
    pares = generar_pares(_leer_catalogo(CATALOGO_CSV), cargar_vecinos(), seed=SEED)
    escribir_pares(pares)
    print(f"{len(pares)} pares escritos en {PARES_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

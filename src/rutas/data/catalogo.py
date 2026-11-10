"""Validador del catálogo de lugares (Fase 1). Devuelve la lista de errores; 0 errores = válido."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from rutas.config import DATA_RAW

COLUMNAS = [
    "id",
    "nombre",
    "municipio",
    "categoria",
    "lat",
    "lon",
    "duracion_visita_min",
    "fuente_duracion",
    "fuente_coord",
    "verificado",
]
MINIMOS = {"cabecera": 12, "atractivo": 15, "finca": 8, "acopio": 5}
MINIMO_TOTAL = 40
# Caja aproximada del departamento del Quindío (grados).
LAT_MIN, LAT_MAX = 4.0, 5.0
LON_MIN, LON_MAX = -76.0, -75.3
CATALOGO_CSV = DATA_RAW / "catalogo.csv"


def validar(filas: list[dict], exigir_verificado: bool = True) -> list[str]:
    errores: list[str] = []
    if filas:
        faltantes = [c for c in COLUMNAS if c not in filas[0]]
        if faltantes:
            return [f"Faltan columnas obligatorias: {', '.join(faltantes)}"]

    if len(filas) < MINIMO_TOTAL:
        errores.append(f"El catálogo tiene {len(filas)} lugares; se piden al menos {MINIMO_TOTAL}.")

    ids = [f["id"] for f in filas]
    for repetido in sorted({i for i in ids if ids.count(i) > 1}):
        errores.append(f"id repetido: {repetido}")

    nombres = [f["nombre"] for f in filas]
    for repetido in sorted({n for n in nombres if nombres.count(n) > 1}):
        errores.append(f"nombre repetido: {repetido}")

    conteo: dict[str, int] = {}
    for fila in filas:
        cat = fila["categoria"]
        conteo[cat] = conteo.get(cat, 0) + 1
    for cat, minimo in MINIMOS.items():
        if conteo.get(cat, 0) < minimo:
            errores.append(
                f"Categoría '{cat}': {conteo.get(cat, 0)} lugares; se piden al menos {minimo}."
            )

    for fila in filas:
        ref = f"{fila['id']} ({fila['nombre']})"
        try:
            lat, lon = float(fila["lat"]), float(fila["lon"])
        except (TypeError, ValueError):
            errores.append(f"{ref}: coordenada ausente o no numérica.")
        else:
            if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
                errores.append(f"{ref}: coordenada fuera del Quindío ({lat}, {lon}).")

        if not fila["fuente_coord"].strip():
            errores.append(f"{ref}: falta fuente_coord.")

        if fila["categoria"] == "atractivo":
            try:
                duracion = float(fila["duracion_visita_min"])
            except (TypeError, ValueError):
                duracion = 0.0
            if duracion <= 0:
                errores.append(f"{ref}: atractivo sin duración de visita válida.")
            if not fila["fuente_duracion"].strip():
                errores.append(f"{ref}: atractivo sin fuente de duración.")

        if exigir_verificado and fila["verificado"].strip().lower() != "true":
            errores.append(f"{ref}: no está verificado (verificado=True requerido).")

    return errores


def leer(path: Path = CATALOGO_CSV) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    if not CATALOGO_CSV.exists():
        print(f"Falta {CATALOGO_CSV}. El catálogo lo arma el grupo (Fase 1).", file=sys.stderr)
        return 1
    errores = validar(leer())
    for e in errores:
        print(e)
    print("Catálogo válido." if not errores else f"{len(errores)} error(es).")
    return 1 if errores else 0


if __name__ == "__main__":
    raise SystemExit(main())

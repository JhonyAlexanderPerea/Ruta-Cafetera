"""Escritura y validación de los CSV de resultados (anexo del enunciado).

Las columnas se fijan al escribir y se validan al leer. Las columnas pueden ampliarse, no reducirse.
"""

from __future__ import annotations

import csv
from pathlib import Path


def escribir_csv(ruta: Path | str, columnas: list[str], filas: list[dict]) -> None:
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, extrasaction="raise")
        w.writeheader()
        w.writerows(filas)


def validar_columnas(ruta: Path | str, minimas: list[str]) -> None:
    """Lanza ValueError si el archivo no tiene al menos las columnas pedidas."""
    with open(ruta, encoding="utf-8", newline="") as f:
        encabezado = next(csv.reader(f))
    faltantes = [c for c in minimas if c not in encabezado]
    if faltantes:
        raise ValueError(f"{ruta}: faltan columnas {faltantes}")

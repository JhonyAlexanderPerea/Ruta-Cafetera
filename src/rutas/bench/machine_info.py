"""Registro de la máquina y del entorno de cada medición (protocolo, sección 6 del enunciado)."""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

import cpuinfo
import psutil

from rutas.config import ROOT

LIBRERIAS = ["osmnx", "networkx", "numpy", "pyproj", "scipy"]


def _commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "desconocido"


def _version(paquete: str) -> str:
    try:
        return metadata.version(paquete)
    except metadata.PackageNotFoundError:
        return "no instalado"


def recolectar() -> dict:
    cpu = cpuinfo.get_cpu_info()
    return {
        "procesador": cpu.get("brand_raw", platform.processor()),
        "nucleos_fisicos": psutil.cpu_count(logical=False),
        "nucleos_logicos": psutil.cpu_count(),
        "ram_gb": round(psutil.virtual_memory().total / 1e9, 1),
        "so": platform.platform(),
        "python": sys.version.split()[0],
        "librerias": {p: _version(p) for p in LIBRERIAS},
        "commit": _commit(),
        "fecha": datetime.now(UTC).isoformat(timespec="seconds"),
    }


def guardar(nombre: str, extra: dict | None = None, carpeta: Path | None = None) -> Path:
    carpeta = carpeta or (ROOT / "results" / "_meta")
    carpeta.mkdir(parents=True, exist_ok=True)
    datos = {**recolectar(), **(extra or {})}
    ruta = carpeta / f"{nombre}.json"
    ruta.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
    return ruta

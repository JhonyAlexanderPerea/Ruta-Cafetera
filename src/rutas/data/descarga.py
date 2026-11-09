"""Descarga las redes viales crudas (sin modificar) y guarda sus metadatos."""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import time
from collections.abc import Callable
from datetime import date
from typing import Any

import osmnx as ox
import requests
from osmnx._errors import InsufficientResponseError, ResponseStatusCodeError

from rutas.config import DATA_RAW

PLACE = "Quindío, Colombia"
NETWORK_TYPE = "drive"
# (lat, lon) de la plaza de Bolívar de Armenia. VERIFICAR en el mapa antes de descargar.
PLAZA_BOLIVAR = (4.5325757482519915, -75.67300446053777) 
RADIOS_KM = (2, 5, 10, 20)
SERVIDORES = [
    "https://overpass-api.de/api",
    "https://overpass.private.coffee/api",
    "https://overpass.kumi.systems/api",
    "https://maps.mail.ru/osm/tools/overpass/api",
]

ox.settings.use_cache = True
ox.settings.cache_folder = str(DATA_RAW / "cache")
ox.settings.log_console = True
ox.settings.requests_timeout = 180

LOGGER = logging.getLogger(__name__)
ERRORES_DESCARGA = (
    requests.exceptions.RequestException,
    InsufficientResponseError,
    ResponseStatusCodeError,
)

def _sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def _guardar(G, nombre: str, consulta: str, segundos: float, servidor: str) -> dict:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    ruta = DATA_RAW / f"{nombre}.graphml"
    ox.save_graphml(G, ruta)
    meta = {
        "nombre": nombre,
        "consulta": consulta,
        "servidor": servidor,
        "network_type": NETWORK_TYPE,
        "fecha_descarga": date.today().isoformat(),
        "osmnx": ox.__version__,
        "nodos": G.number_of_nodes(),
        "aristas": G.number_of_edges(),
        "tamano_mb": round(ruta.stat().st_size / 1e6, 2),
        "segundos_descarga": round(segundos, 1),
        "sha256": _sha256(ruta),
    }
    (DATA_RAW / f"{nombre}.meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return meta


def _descargar_con_servidores(descarga: Callable[[], Any]) -> tuple[Any, str]:
    errores: list[str] = []
    endpoint_original = ox.settings.overpass_url
    try:
        for servidor in SERVIDORES:
            ox.settings.overpass_url = servidor
            try:
                return descarga(), servidor
            except ERRORES_DESCARGA as exc:
                errores.append(f"{servidor}: {exc}")
                LOGGER.warning("Falló la descarga con %s: %s", servidor, exc)
    finally:
        ox.settings.overpass_url = endpoint_original

    detalle = "; ".join(errores)
    raise RuntimeError(f"No se pudo descargar desde ningún servidor Overpass. {detalle}") from None


def descargar_radio(km: int) -> dict:
    t0 = time.perf_counter()
    G, servidor = _descargar_con_servidores(
        lambda: ox.graph_from_point(PLAZA_BOLIVAR, dist=km * 1000, network_type=NETWORK_TYPE)
    )
    return _guardar(
        G,
        f"radio_{km}km",
        f"point{PLAZA_BOLIVAR} dist={km}km",
        time.perf_counter() - t0,
        servidor,
    )


def descargar_departamento() -> dict:
    t0 = time.perf_counter()
    G, servidor = _descargar_con_servidores(
        lambda: ox.graph_from_place(PLACE, network_type=NETWORK_TYPE)
    )
    return _guardar(G, "quindio", PLACE, time.perf_counter() - t0, servidor)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("que", choices=["radios", "departamento", "todo"])
    ap.add_argument("--radio", type=int, help="un solo radio en km (prueba de humo)")
    a = ap.parse_args()

    metas = []
    if a.radio:
        metas.append(descargar_radio(a.radio))
    else:
        if a.que in ("radios", "todo"):
            metas += [descargar_radio(k) for k in RADIOS_KM]
        if a.que in ("departamento", "todo"):
            metas.append(descargar_departamento())
    for m in metas:
        print(
            f"{m['nombre']:<12} V={m['nodos']:>7} E={m['aristas']:>7} "
            f"{m['tamano_mb']:>7} MB  {m['fecha_descarga']}"
        )


if __name__ == "__main__":
    main()
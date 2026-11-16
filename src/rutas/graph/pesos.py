"""Velocidad y tiempo de viaje de cada arista (R1.2), según la decisión D8 de docs/decisiones.md.

Orden de la regla:
1. `maxspeed` explícito de OSM (si es numérico).
2. Residencial: 30 km/h.
3. Troncal: 50 km/h (urbana o nacional, sin dato explícito).
4. Primaria: 50 km/h.
5. Secundaria, terciaria, no clasificada y otras: 30 km/h.
6. Respaldo: 30 km/h.
"""

from __future__ import annotations

import re

VELOCIDAD_POR_TIPO = {
    "residential": 30.0,
    "trunk": 50.0,
    "primary": 50.0,
    "secondary": 30.0,
    "tertiary": 30.0,
    "unclassified": 30.0,
}
RESPALDO_KMH = 30.0
_NUMERO = re.compile(r"^\s*(\d+(?:\.\d+)?)")


def _primero(valor):
    return valor[0] if isinstance(valor, list) and valor else valor


def velocidad_kmh(atributos: dict) -> float:
    explicita = _primero(atributos.get("maxspeed"))
    if explicita is not None:
        m = _NUMERO.match(str(explicita))
        if m:
            return float(m.group(1))

    tipo = _primero(atributos.get("highway"))
    tipo = str(tipo or "").removesuffix("_link")
    return VELOCIDAD_POR_TIPO.get(tipo, RESPALDO_KMH)


def tiempo_s(atributos: dict) -> float:
    """Tiempo de viaje en segundos: distancia (m) / velocidad (m/s)."""
    return float(atributos["length"]) / (velocidad_kmh(atributos) / 3.6)

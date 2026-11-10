"""Resultado común de Dijkstra (firma objetivo del roadmap, sección 2.4)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DijkstraResult:
    dist: list[float]  # inf si no se alcanzó
    pred: list[int]  # -1 si no hay predecesor
    explored: int  # nodos que salieron de la cola, contados una vez
    cost: float | None  # tiempo hasta el destino (None si no hubo destino)
    path: list[int] | None  # secuencia de nodos origen->destino

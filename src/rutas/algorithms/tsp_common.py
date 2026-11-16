"""Validación compartida de los solvers del viajante (convención de specs/r4_recorrido.md)."""

from __future__ import annotations


def validar_entrada(c, start: int, nodes: list[int]) -> None:
    """Lanza ValueError si hay índices repetidos o fuera de rango."""
    n = len(c)
    if not 0 <= start < n:
        raise ValueError(f"partida fuera de rango: {start}")
    if len(set(nodes)) != len(nodes):
        raise ValueError("lugares repetidos")
    if start in nodes:
        raise ValueError("la partida no puede estar entre los lugares a visitar")
    for v in nodes:
        if not 0 <= v < n:
            raise ValueError(f"lugar fuera de rango: {v}")


def costo_recorrido(c, start: int, orden: list[int]) -> float:
    """Costo del ciclo start -> orden... -> start."""
    ruta = [start, *orden, start]
    return sum(c[a][b] for a, b in zip(ruta, ruta[1:], strict=False))

"""Grafo en formato CSR (R1.5). Nodos indexados 0..V-1.

Aristas paralelas: se conserva la de menor tiempo. Bucles propios: se descartan.
Ambos conteos se reportan."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class CSRGraph:
    indptr: np.ndarray  # int64, V+1
    indices: np.ndarray  # int32, E'
    dist_m: np.ndarray  # float64, E'
    time_s: np.ndarray  # float64, E'

    @property
    def n_nodes(self) -> int:
        return len(self.indptr) - 1

    @property
    def n_edges(self) -> int:
        return len(self.indices)

    def save(self, path: Path | str) -> None:
        np.savez_compressed(
            path, indptr=self.indptr, indices=self.indices, dist_m=self.dist_m, time_s=self.time_s
        )

    @classmethod
    def load(cls, path: Path | str) -> CSRGraph:
        with np.load(path) as z:
            return cls(
                indptr=z["indptr"].astype(np.int64),
                indices=z["indices"].astype(np.int32),
                dist_m=z["dist_m"].astype(np.float64),
                time_s=z["time_s"].astype(np.float64),
            )


def desde_networkx(G) -> tuple[CSRGraph, dict]:
    """Convierte un MultiDiGraph de OSMnx a CSR. Devuelve (grafo, reporte de limpieza)."""
    nodos = sorted(G.nodes())
    idx = {osmid: i for i, osmid in enumerate(nodos)}
    mejor: dict[tuple[int, int], tuple[float, float]] = {}
    bucles = 0
    paralelas = 0
    for u, v, data in G.edges(data=True):
        a, b = idx[u], idx[v]
        if a == b:
            bucles += 1
            continue
        t, d = float(data["travel_time"]), float(data["length"])
        if (a, b) in mejor:
            paralelas += 1
            if t < mejor[(a, b)][0]:
                mejor[(a, b)] = (t, d)
        else:
            mejor[(a, b)] = (t, d)

    V = len(nodos)
    filas = sorted(mejor.items())
    indptr = np.zeros(V + 1, dtype=np.int64)
    for (a, _), _ in filas:
        indptr[a + 1] += 1
    indptr = np.cumsum(indptr)
    indices = np.array([b for (_, b), _ in filas], dtype=np.int32)
    time_s = np.array([t for _, (t, _) in filas], dtype=np.float64)
    dist_m = np.array([d for _, (_, d) in filas], dtype=np.float64)

    reporte = {"paralelas_reducidas": paralelas, "bucles_descartados": bucles}
    return CSRGraph(indptr, indices, dist_m, time_s), reporte

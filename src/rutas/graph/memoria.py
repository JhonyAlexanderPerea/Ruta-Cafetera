"""Estimación de memoria de la red como matriz de adyacencia frente a listas (R1.1).

Supuestos explícitos:
- Matriz densa de float64: V*V celdas de 8 bytes.
- Listas de adyacencia en CSR: E entradas de 4 bytes (índice int32) y E pesos de 8 bytes
  (float64), más V+1 punteros de 8 bytes (int64).
"""

from __future__ import annotations

BYTES_CELDA_MATRIZ = 8
BYTES_INDICE = 4
BYTES_PESO = 8
BYTES_PUNTERO = 8


def estimar_mb(V: int, E: int) -> dict:
    matriz = V * V * BYTES_CELDA_MATRIZ
    listas = E * (BYTES_INDICE + BYTES_PESO) + (V + 1) * BYTES_PUNTERO
    return {
        "matriz_mb": round(matriz / 1e6, 1),
        "listas_mb": round(listas / 1e6, 2),
        "supuestos": (
            f"matriz: {BYTES_CELDA_MATRIZ} bytes por celda (V*V); "
            f"listas: {BYTES_INDICE} bytes por índice + {BYTES_PESO} bytes por peso por arista, "
            f"{BYTES_PUNTERO} bytes por puntero (V+1)"
        ),
    }

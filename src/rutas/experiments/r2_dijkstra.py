"""R2: tiempos de Dijkstra en la red del departamento, y matriz de tiempos entre los lugares.

Pares (data/raw/pares_dijkstra.csv): 20 con cola de prioridad, y los 10 con
`usa_lineal=True` también con la versión lineal.
Tiempos con el protocolo (mediana de 5, límite 5 min, solo la llamada cronometrada).
Costo y nodos explorados: se calculan una vez fuera del cronómetro (es determinista).
Matriz: Dijkstra con cola de prioridad sin destino, desde cada lugar. Salida en segundos.
"""

from __future__ import annotations

import csv
from functools import partial

import numpy as np

from rutas.algorithms import dijkstra_heap, dijkstra_lineal
from rutas.bench import io as bio
from rutas.bench import machine_info
from rutas.bench.runner import measure
from rutas.config import DATA_PROCESSED, DATA_RAW, REPETITIONS, RESULTS, SEED, TIME_LIMIT_S
from rutas.graph.csr import CSRGraph

COLUMNAS_DIJKSTRA = [
    "origen",
    "destino",
    "version",
    "tiempo_viaje_s",
    "nodos_explorados",
    "tiempo_ms",
    "estado",
]


def cociente_stats(pares: list[tuple[float, float]]) -> dict:
    """pares = [(tiempo_lineal, tiempo_heap), ...].

    Devuelve la mediana, el mínimo y el máximo del cociente lineal / heap.
    """
    cocientes = sorted(lin / heap for lin, heap in pares)
    n = len(cocientes)
    mediana = cocientes[n // 2] if n % 2 else (cocientes[n // 2 - 1] + cocientes[n // 2]) / 2
    return {"mediana": mediana, "minimo": cocientes[0], "maximo": cocientes[-1]}


def verificar_matriz(M: np.ndarray) -> dict:
    """Chequeos del enunciado: diagonal cero, sin infinitos, asimetrías y desigualdad triangular."""
    diagonal_ok = bool(np.allclose(np.diag(M), 0.0))
    infinitos = int(np.isinf(M).sum())
    asimetricas = int(
        sum(1 for i in range(len(M)) for j in range(i + 1, len(M)) if M[i, j] != M[j, i])
    )
    # Violación: d(i,k) > d(i,j) + d(j,k), para todas las ternas (i, j, k)
    triangular = int((M[:, None, :] > M[:, :, None] + M[None, :, :]).sum())
    return {
        "diagonal_ok": diagonal_ok,
        "infinitos": infinitos,
        "asimetricas": asimetricas,
        "triangular_violaciones": triangular,
    }


def _cargar_lugares() -> dict[str, int]:
    with open(DATA_PROCESSED / "places.csv", encoding="utf-8", newline="") as f:
        return {r["id"]: int(r["nodo_idx"]) for r in csv.DictReader(f)}


def _cargar_pares(nodos: dict[str, int]) -> list[dict]:
    with open(DATA_RAW / "pares_dijkstra.csv", encoding="utf-8", newline="") as f:
        return [
            {
                "origen": r["origen"],
                "destino": r["destino"],
                "usa_lineal": r["usa_lineal"] == "True",
                "s": nodos[r["origen"]],
                "t": nodos[r["destino"]],
            }
            for r in csv.DictReader(f)
        ]


def main() -> None:
    g = CSRGraph.load(DATA_PROCESSED / "graph_csr.npz")
    nodos = _cargar_lugares()
    pares = _cargar_pares(nodos)

    filas = []
    cocientes = []
    for p in pares:
        versiones = [("cola_prioridad", dijkstra_heap.dijkstra)]
        if p["usa_lineal"]:
            versiones.append(("lineal", dijkstra_lineal.dijkstra))
        tiempos_por_version = {}
        for nombre, fn in versiones:
            valor = fn(g, p["s"], p["t"])  # cálculo fuera del cronómetro
            m = measure(partial(fn, g, p["s"], p["t"]), reps=REPETITIONS, timeout_s=TIME_LIMIT_S)
            if m.completed:
                ms, estado = round(m.median_ms, 1), "completada"
            else:
                ms, estado = "no completada", "no completada"
            tiempos_por_version[nombre] = ms
            filas.append(
                {
                    "origen": p["origen"],
                    "destino": p["destino"],
                    "version": nombre,
                    "tiempo_viaje_s": round(valor.cost, 2),
                    "nodos_explorados": valor.explored,
                    "tiempo_ms": ms,
                    "estado": estado,
                }
            )
            print(f"{p['origen']}->{p['destino']} {nombre}: {ms} ms", flush=True)
        if p["usa_lineal"] and all(
            isinstance(tiempos_por_version[v], float) for v in ("lineal", "cola_prioridad")
        ):
            cocientes.append((tiempos_por_version["lineal"], tiempos_por_version["cola_prioridad"]))

    bio.escribir_csv(RESULTS / "r2_dijkstra.csv", COLUMNAS_DIJKSTRA, filas)
    if cocientes:
        s = cociente_stats(cocientes)
        bio.escribir_csv(RESULTS / "r2_cociente.csv", ["mediana", "minimo", "maximo"], [s])

    # Matriz de tiempos (segundos) entre los lugares del catálogo
    ids = list(nodos.keys())
    M = np.zeros((len(ids), len(ids)))
    for i, a in enumerate(ids):
        dist = dijkstra_heap.dijkstra(g, nodos[a], None).dist
        for j, b in enumerate(ids):
            M[i, j] = dist[nodos[b]]
    with open(RESULTS / "r2_matriz_tiempos.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([""] + ids)
        for i, a in enumerate(ids):
            w.writerow([a] + [round(float(x), 2) for x in M[i]])

    machine_info.guardar(
        "r2_dijkstra",
        extra={
            "semilla": SEED,
            "repeticiones": REPETITIONS,
            "limite_s": TIME_LIMIT_S,
            "verificacion_matriz": verificar_matriz(M),
        },
    )
    print("verificación de la matriz:", verificar_matriz(M))


if __name__ == "__main__":
    main()

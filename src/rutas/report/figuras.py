"""Genera las figuras de la vista Resultados leyendo solo results/*.csv."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from rutas import config  # noqa: E402

NO_COMPLETADA = "no completada"


def leer(ruta: Path) -> list[dict]:
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def completadas(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r.get("estado") == "completada"]


def _guardar(fig, salida: Path) -> None:
    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(salida, dpi=120)
    plt.close(fig)


def figura_r1(rows: list[dict], salida: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    for r in rows:
        x, y = float(r["V_mas_E"]), float(r["tiempo_ms"])
        ax.scatter(x, y, color="tab:blue")
        ax.annotate(r["red"], (x, y), textcoords="offset points", xytext=(4, 4))
    ax.set(xscale="log", yscale="log", xlabel="V + E (elementos)",
           ylabel="Tiempo (ms)", title="R1: tiempo de componente conexa vs V+E")
    _guardar(fig, salida)


def figura_r2(rows: list[dict], salida: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    validas = completadas(rows)
    for version, marca in (("lineal", "o"), ("cola_prioridad", "s")):
        sel = [r for r in validas if r["version"] == version]
        ax.scatter([float(r["nodos_explorados"]) for r in sel],
                   [float(r["tiempo_ms"]) for r in sel], marker=marca, label=version)
    ax.set(xlabel="Nodos explorados (unidades)", ylabel="Tiempo (ms)",
           title="R2: Dijkstra, nodos explorados vs tiempo")
    ax.legend()
    _guardar(fig, salida)


def figura_r3(rows: list[dict], salida: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ns = [float(r["n"]) for r in rows]
    ax.scatter(ns, [float(r["tiempo_propio_ms"]) for r in rows], label="propio")
    ax.scatter(ns, [float(r["tiempo_scipy_ms"]) for r in rows], marker="s", label="scipy")
    ax.set(xscale="log", yscale="log", xlabel="n (puntos)", ylabel="Tiempo (ms)",
           title="R3: envolvente convexa, propio vs scipy")
    ax.legend()
    _guardar(fig, salida)


def figura_r4_exactas(rows: list[dict], salida: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    notas = []
    for col, etiqueta in (("tiempo_fuerza_bruta_ms", "fuerza bruta"),
                          ("tiempo_held_karp_ms", "Held-Karp")):
        pts = [(float(r["k"]), float(r[col])) for r in rows if r[col] != NO_COMPLETADA]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", label=etiqueta)
        if len(pts) < len(rows):
            notas.append(f"{etiqueta}: no completada desde k={int(pts[-1][0]) + 1}"
                         if pts else f"{etiqueta}: no completada")
    if notas:
        ax.text(0.02, 0.98, "\n".join(notas), transform=ax.transAxes, va="top", fontsize=8)
    ax.set(yscale="log", xlabel="k (lugares)", ylabel="Tiempo (ms)",
           title="R4: soluciones exactas, tiempo vs k")
    ax.legend(loc="lower right")
    _guardar(fig, salida)


def figura_r4_heuristica(rows: list[dict], salida: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ks = [float(r["k"]) for r in rows]
    ax.plot(ks, [float(r["brecha_promedio_pct"]) for r in rows], marker="o", label="promedio")
    ax.plot(ks, [float(r["brecha_maxima_pct"]) for r in rows], marker="s", label="máxima")
    ax.set(xlabel="k (lugares)", ylabel="Brecha (%)",
           title="R4: brecha de la heurística respecto al óptimo")
    ax.legend()
    _guardar(fig, salida)


def main() -> None:
    res, fig = config.RESULTS, config.FIGURES
    fig.mkdir(parents=True, exist_ok=True)
    figura_r1(completadas(leer(res / "r1_tiempos_componente.csv")), fig / "r1_tiempo_componente.png")
    figura_r2(leer(res / "r2_dijkstra.csv"), fig / "r2_nodos_vs_tiempo.png")
    figura_r3(leer(res / "r3_envolvente.csv"), fig / "r3_envolvente_tiempos.png")
    figura_r4_exactas(leer(res / "r4_exactas.csv"), fig / "r4_exactas_tiempo.png")
    figura_r4_heuristica(leer(res / "r4_heuristica.csv"), fig / "r4_heuristica_brecha.png")


if __name__ == "__main__":
    main()

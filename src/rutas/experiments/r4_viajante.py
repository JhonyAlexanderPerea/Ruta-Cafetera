"""R4: viajante asimétrico sobre la matriz de tiempos de R2 (40×40, en segundos). Partida: Armenia.

Instancias: k lugares al azar del catálogo, sin Armenia, con semilla derivada de (SEED, k, i).
Tiempos: protocolo de la sección 6 (mediana de 5, límite de 5 min, solo la llamada cronometrada).
Costos y órdenes: se calculan una vez fuera del cronómetro (son deterministas).

Salidas: results/r4_exactas.csv, results/r4_heuristica.csv, results/r4_itinerario.csv,
results/r4_ejemplo_voraz.csv, results/_meta/r4_viajante.json.
"""

from __future__ import annotations

import csv
import random
from functools import partial

from rutas.algorithms.tsp_bruteforce import tsp_bruteforce
from rutas.algorithms.tsp_greedy import tsp_greedy
from rutas.algorithms.tsp_heldkarp import tsp_heldkarp
from rutas.bench import io as bio
from rutas.bench import machine_info
from rutas.bench.runner import measure
from rutas.config import DATA_RAW, REPETITIONS, RESULTS, SEED, TIME_LIMIT_S

PARTIDA = "cab_01"  # Armenia (plaza de Bolívar)
KS_EXACTAS = list(range(5, 13))
KS_HEURISTICA = [5, 8, 10, 12]
INSTANCIAS = 5
JORNADA_MIN = 660  # 11 h


def _cargar_matriz():
    with open(RESULTS / "r2_matriz_tiempos.csv", encoding="utf-8", newline="") as f:
        filas = list(csv.reader(f))
    ids = filas[0][1:]
    c = [[float(x) for x in fila[1:]] for fila in filas[1:]]
    return ids, c


def _catalogo() -> dict[str, dict]:
    with open(DATA_RAW / "catalogo.csv", encoding="utf-8", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def instancia(ids: list[str], k: int, i: int) -> list[str]:
    """k lugares al azar del catálogo (sin la partida), reproducible con (SEED, k, i)."""
    rng = random.Random(SEED * 1_000_003 + k * 1009 + i)
    candidatos = [x for x in ids if x != PARTIDA]
    return rng.sample(candidatos, k)


def cociente_brecha(voraz: float, optimo: float) -> float:
    return (voraz - optimo) / optimo * 100


def medir_exactas(ids, c) -> list[dict]:
    idx = {x: n for n, x in enumerate(ids)}
    s = idx[PARTIDA]
    filas = []
    fuerza_bruta_activa = True
    for k in KS_EXACTAS:
        nodos = [idx[x] for x in instancia(ids, k, 0)]
        if fuerza_bruta_activa:
            mb = measure(
                partial(tsp_bruteforce, c, s, nodos), reps=REPETITIONS, timeout_s=TIME_LIMIT_S
            )
            t_b = round(mb.median_ms, 1) if mb.completed else "no completada"
            if not mb.completed:
                fuerza_bruta_activa = False
        else:
            t_b = "no completada"
        mh = measure(partial(tsp_heldkarp, c, s, nodos), reps=REPETITIONS, timeout_s=TIME_LIMIT_S)
        t_h = round(mh.median_ms, 1) if mh.completed else "no completada"
        filas.append({"k": k, "tiempo_fuerza_bruta_ms": t_b, "tiempo_held_karp_ms": t_h})
        print(f"k={k}: fuerza bruta={t_b} ms, Held-Karp={t_h} ms", flush=True)
        if not mh.completed:
            break
    return filas


def medir_heuristica(ids, c) -> list[dict]:
    idx = {x: n for n, x in enumerate(ids)}
    s = idx[PARTIDA]
    filas = []
    for k in KS_HEURISTICA:
        brechas = []
        for i in range(INSTANCIAS):
            nodos = [idx[x] for x in instancia(ids, k, i)]
            optimo, _ = tsp_heldkarp(c, s, nodos)
            voraz, _ = tsp_greedy(c, s, nodos)
            brechas.append(cociente_brecha(voraz, optimo))
        filas.append(
            {
                "k": k,
                "instancias": INSTANCIAS,
                "brecha_promedio_pct": round(sum(brechas) / len(brechas), 2),
                "brecha_maxima_pct": round(max(brechas), 2),
            }
        )
        print(f"k={k}: brecha promedio={filas[-1]['brecha_promedio_pct']}%", flush=True)
    return filas


def elegir_itinerario(ids, c, catalogo, candidatos: list[str], seleccion: int = 8) -> list[str]:
    """Quita atractivos hasta que visitas + desplazamientos quepan en la jornada.

    Regla (propuesta, pendiente de PARADA 6): en cada paso se quita el atractivo cuya eliminación
    reduce más la duración total; se repite hasta que quepa.
    """
    idx = {x: n for n, x in enumerate(ids)}
    s = idx[PARTIDA]

    def duracion(lista: list[str]) -> float:
        nodos = [idx[x] for x in lista]
        costo, _ = tsp_heldkarp(c, s, nodos)
        visitas = sum(float(catalogo[x]["duracion_visita_min"]) for x in lista)
        return costo / 60 + visitas

    actual = list(candidatos[:seleccion])
    while duracion(actual) > JORNADA_MIN and len(actual) > 6:
        mejor = min(actual, key=lambda x: duracion([y for y in actual if y != x]))
        actual.remove(mejor)
    return actual


def escribir_itinerario(ids, c, catalogo, lista: list[str]) -> None:
    idx = {x: n for n, x in enumerate(ids)}
    s = idx[PARTIDA]
    nodos = [idx[x] for x in lista]
    costo, orden_idx = tsp_heldkarp(c, s, nodos)
    orden = [ids[i] for i in orden_idx]
    filas = []
    acumulado = 0.0
    anterior = PARTIDA
    visitas_total = 0.0
    desplaz_total = 0.0
    for n, x in enumerate(orden, start=1):
        desplaz = c[idx[anterior]][idx[x]] / 60
        visita = float(catalogo[x]["duracion_visita_min"])
        acumulado += (desplaz + visita) / 60
        visitas_total += visita
        desplaz_total += desplaz
        filas.append(
            {
                "orden": n,
                "lugar": catalogo[x]["nombre"],
                "desplazamiento_min": round(desplaz, 1),
                "visita_min": visita,
                "acumulado_h": round(acumulado, 2),
            }
        )
        anterior = x
    regreso = c[idx[anterior]][idx[PARTIDA]] / 60
    desplaz_total += regreso
    acumulado += regreso / 60
    filas.append(
        {
            "orden": "Regreso",
            "lugar": f"Regreso → {catalogo[PARTIDA]['nombre']}",
            "desplazamiento_min": round(regreso, 1),
            "visita_min": 0,
            "acumulado_h": round(acumulado, 2),
        }
    )
    filas.append(
        {
            "orden": "Total visitas",
            "lugar": "",
            "desplazamiento_min": "",
            "visita_min": round(visitas_total, 1),
            "acumulado_h": "",
        }
    )
    filas.append(
        {
            "orden": "Total desplazamientos",
            "lugar": "",
            "desplazamiento_min": round(desplaz_total, 1),
            "visita_min": "",
            "acumulado_h": "",
        }
    )
    filas.append(
        {
            "orden": "Duración total",
            "lugar": "",
            "desplazamiento_min": "",
            "visita_min": "",
            "acumulado_h": round(acumulado, 2),
        }
    )
    bio.escribir_csv(
        RESULTS / "r4_itinerario.csv",
        ["orden", "lugar", "desplazamiento_min", "visita_min", "acumulado_h"],
        filas,
    )


def ejemplo_voraz(ids, c) -> None:
    """Busca una instancia pequeña donde la voraz no es óptima (semilla fija)."""
    idx = {x: n for n, x in enumerate(ids)}
    s = idx[PARTIDA]
    for i in range(500):
        nodos_ids = instancia(ids, 5, i)
        nodos = [idx[x] for x in nodos_ids]
        optimo, orden_o = tsp_heldkarp(c, s, nodos)
        voraz, orden_v = tsp_greedy(c, s, nodos)
        if voraz > optimo + 1e-9:
            filas = [
                {
                    "ruta": "voraz",
                    "orden": " -> ".join([PARTIDA] + [ids[j] for j in orden_v] + [PARTIDA]),
                    "costo_s": round(voraz, 1),
                },
                {
                    "ruta": "optimo_held_karp",
                    "orden": " -> ".join([PARTIDA] + [ids[j] for j in orden_o] + [PARTIDA]),
                    "costo_s": round(optimo, 1),
                },
            ]
            bio.escribir_csv(RESULTS / "r4_ejemplo_voraz.csv", ["ruta", "orden", "costo_s"], filas)
            print(
                f"ejemplo en la instancia {i}: voraz {voraz:.1f} s > óptimo {optimo:.1f} s",
                flush=True,
            )
            return
    print("no se encontró ejemplo en 500 instancias", flush=True)


def main() -> None:
    ids, c = _cargar_matriz()
    catalogo = _catalogo()
    exactas = medir_exactas(ids, c)
    bio.escribir_csv(
        RESULTS / "r4_exactas.csv", ["k", "tiempo_fuerza_bruta_ms", "tiempo_held_karp_ms"], exactas
    )
    heur = medir_heuristica(ids, c)
    bio.escribir_csv(
        RESULTS / "r4_heuristica.csv",
        ["k", "instancias", "brecha_promedio_pct", "brecha_maxima_pct"],
        heur,
    )
    atractivos = [x for x in ids if catalogo[x]["categoria"] == "atractivo" and x != PARTIDA]
    rng = random.Random(SEED)
    rng.shuffle(atractivos)
    itinerario = elegir_itinerario(ids, c, catalogo, atractivos)
    escribir_itinerario(ids, c, catalogo, itinerario)
    ejemplo_voraz(ids, c)
    machine_info.guardar(
        "r4_viajante",
        extra={
            "semilla": SEED,
            "repeticiones": REPETITIONS,
            "limite_s": TIME_LIMIT_S,
            "partida": PARTIDA,
        },
    )
    print("listo")


if __name__ == "__main__":
    main()

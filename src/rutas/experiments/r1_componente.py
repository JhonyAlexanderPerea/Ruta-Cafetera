"""R1.3: tiempo de `ox.truncate.largest_component(G, strongly=True)` en las 5 redes.

Protocolo (enunciado, sección 6): misma máquina, mediana de 5 repeticiones, límite de 5 minutos,
solo se mide la llamada. La carga del GraphML queda fuera del cronómetro.
Salidas: results/r1_tiempos_componente.csv, results/r1_tamano_red.csv
y results/_meta/r1_componente.json.
"""

from __future__ import annotations

from functools import partial

import osmnx as ox

from rutas.bench import io as bio
from rutas.bench import machine_info
from rutas.bench.runner import measure
from rutas.config import DATA_RAW, REPETITIONS, RESULTS, SEED, TIME_LIMIT_S

REDES = ["radio_2km", "radio_5km", "radio_10km", "radio_20km", "quindio"]
COLUMNAS_TIEMPOS = ["red", "V", "E", "V_mas_E", "tiempo_ms", "estado"]
COLUMNAS_TAMANO = ["red", "nodos", "aristas"]


def main() -> None:
    tiempos = []
    tamano = []
    for red in REDES:
        G = ox.load_graphml(DATA_RAW / f"{red}.graphml")
        V, E = G.number_of_nodes(), G.number_of_edges()
        tamano.append({"red": red, "nodos": V, "aristas": E})
        print(f"{red}: V={V} E={E} -> midiendo...", flush=True)

        m = measure(
            partial(ox.truncate.largest_component, G, strongly=True),
            reps=REPETITIONS,
            timeout_s=TIME_LIMIT_S,
        )
        if m.completed:
            tiempo = round(m.median_ms, 1)
            estado = "completada"
        else:
            tiempo = "no completada"
            estado = "no completada"
        tiempos.append(
            {"red": red, "V": V, "E": E, "V_mas_E": V + E, "tiempo_ms": tiempo, "estado": estado}
        )
        print(f"  -> {tiempo} ms ({estado}); repeticiones: {m.runs_ms}", flush=True)
        del G

    bio.escribir_csv(RESULTS / "r1_tiempos_componente.csv", COLUMNAS_TIEMPOS, tiempos)
    bio.escribir_csv(RESULTS / "r1_tamano_red.csv", COLUMNAS_TAMANO, tamano)
    machine_info.guardar(
        "r1_componente",
        extra={
            "semilla": SEED,
            "repeticiones": REPETITIONS,
            "limite_s": TIME_LIMIT_S,
            "medicion": "ox.truncate.largest_component(G, strongly=True)",
            "redes": REDES,
        },
    )
    bio.validar_columnas(
        RESULTS / "r1_tiempos_componente.csv", ["red", "V", "E", "V_mas_E", "tiempo_ms"]
    )
    print("listo: results/r1_tiempos_componente.csv")


if __name__ == "__main__":
    main()

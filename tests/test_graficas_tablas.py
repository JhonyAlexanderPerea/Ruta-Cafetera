"""Pruebas de las gráficas Altair y de las tablas HTML de la vista Resultados."""

import pandas as pd
import pytest

from rutas.config import RESULTS
from rutas.report import graficas
from rutas.report.tablas import tabla_html


def test_tabla_html_escapa_el_contenido():
    df = pd.DataFrame({"lugar": ["<script>alert(1)</script>"], "tiempo_ms": [1.5]})
    out = tabla_html(df)
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


def test_tabla_html_pone_barra_solo_en_columnas_de_tiempo():
    df = pd.DataFrame({"lugar": ["a", "b"], "tiempo_ms": [1.0, 4.0], "n": [3, 9]})
    out = tabla_html(df)
    assert out.count("class='barra'") == 2  # solo tiempo_ms
    assert "--w:100.0%" in out and "--w:25.0%" in out


def test_tabla_html_formatea_numeros_y_booleanos():
    df = pd.DataFrame({"n": [12345], "coinciden": [True], "x": [2.50]})
    out = tabla_html(df)
    assert "12,345" in out and ">sí<" in out and ">2.5<" in out


def _leer(nombre: str) -> pd.DataFrame:
    ruta = RESULTS / nombre
    if not ruta.exists():
        pytest.skip(f"falta results/{nombre}")
    return pd.read_csv(ruta)


@pytest.mark.parametrize(
    "funcion,archivo",
    [
        (graficas.grafica_r1, "r1_tiempos_componente.csv"),
        (graficas.grafica_r2, "r2_dijkstra.csv"),
        (graficas.grafica_r3, "r3_envolvente.csv"),
        (graficas.grafica_r4_exactas, "r4_exactas.csv"),
        (graficas.grafica_r4_heuristica, "r4_heuristica.csv"),
        (graficas.grafica_itinerario_dia, "r4_itinerario.csv"),
    ],
)
def test_graficas_se_serializan_con_los_resultados_reales(funcion, archivo):
    spec = funcion(_leer(archivo)).to_dict()
    assert spec  # Altair valida el esquema al serializar


def test_grafica_exactas_descarta_no_completadas():
    df = pd.DataFrame(
        {
            "k": [5, 6],
            "tiempo_fuerza_bruta_ms": ["0.2", "no completada"],
            "tiempo_held_karp_ms": ["0.1", "0.3"],
        }
    )
    spec = graficas.grafica_r4_exactas(df).to_dict()
    filas = next(iter(spec["datasets"].values()))
    assert len(filas) == 3


def test_grafica_comparacion_tiene_cuatro_barras():
    r = {"desplazamiento_min": 100.0, "visita_min": 200.0}
    spec = graficas.grafica_comparacion(r, r).to_dict()
    assert len(next(iter(spec["datasets"].values()))) == 4

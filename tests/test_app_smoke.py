"""Prueba de humo de la app Streamlit (R5)."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from rutas.config import DATA_PROCESSED

APP = str(Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py")
VISTAS = ["Ruta", "Envolvente", "Itinerario", "Resultados"]
hay_datos = pytest.mark.skipif(
    not (DATA_PROCESSED / "graph_csr.npz").exists(),
    reason="falta data/processed/graph_csr.npz (generar con el pipeline de R1)",
)


@hay_datos
@pytest.mark.parametrize("vista", VISTAS)
def test_cada_vista_arranca_sin_excepciones(vista):
    app = AppTest.from_file(APP, default_timeout=60).run()
    assert not app.exception
    assert list(app.radio[0].options) == VISTAS
    app.radio[0].set_value(vista).run()
    assert not app.exception


def test_datos_faltantes_muestra_error_sin_caerse(tmp_path, monkeypatch):
    monkeypatch.setenv("RUTAS_DATA_DIR", str(tmp_path))
    app = AppTest.from_file(APP, default_timeout=60).run()
    assert not app.exception
    assert any("graph_csr.npz" in e.value for e in app.error)
    assert any("pipeline de R1" in e.value for e in app.error)


@hay_datos
def test_itinerario_con_seis_atractivos_muestra_ambos_recorridos():
    app = AppTest.from_file(APP, default_timeout=60).run()
    app.radio[0].set_value("Itinerario").run()
    assert app.error == [] or all("Elige" in e.value for e in app.error)
    opciones = list(app.multiselect[0].options)
    app.multiselect[0].set_value(opciones[:6]).run()
    assert not app.exception
    assert len(app.error) == 0
    assert len(app.metric) == 6

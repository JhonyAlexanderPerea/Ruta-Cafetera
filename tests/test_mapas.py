"""Pruebas de los mapas Folium: se renderizan y llevan lo que la interfaz promete."""

import pytest

from rutas.report import mapas
from rutas.report.iconos import CATEGORIAS, estilo_categoria, svg

ORIGEN = {"nombre": "Plaza <b>", "municipio": "Armenia", "lat": 4.5, "lon": -75.6}
DESTINO = {"nombre": "Mirador", "municipio": "Filandia", "lat": 4.6, "lon": -75.65}
RUTA = [(4.5, -75.6), (4.55, -75.62), (4.6, -75.65)]


def _html(m) -> str:
    return m.get_root().render()


def test_mapa_ruta_tiene_brillo_animado_y_extremos():
    out = _html(mapas.mapa_ruta(RUTA, ORIGEN, DESTINO))
    assert "ruta-viva" in out and "Origen" in out and "Destino" in out


def test_tooltips_escapan_el_nombre():
    out = _html(mapas.mapa_ruta(RUTA, ORIGEN, DESTINO))
    assert "Plaza <b>" not in out and "Plaza &lt;b&gt;" in out


def test_mapa_exploracion_inyecta_el_script_con_los_puntos():
    m = mapas.mapa_exploracion(RUTA, RUTA, ORIGEN, DESTINO)
    out = _html(m)
    assert m.get_name() in out and "Nodos explorados por Dijkstra" in out
    assert "__MAPA__" not in out and "__PUNTOS__" not in out


@pytest.mark.parametrize("poligono,vertices", [(True, True), (False, False)])
def test_mapa_envolvente_respeta_las_capas(poligono, vertices):
    lug = [{"nombre": "A", "municipio": "M", "categoria": "finca", "lat": 4.5, "lon": -75.6}]
    out = _html(mapas.mapa_envolvente(RUTA, lug, poligono, vertices))
    assert ("hull-viva" in out.split("</style>", 1)[1]) is poligono
    assert ("Vértice 1" in out) is vertices


def test_iconos():
    assert "<svg" in svg("reloj") and "currentColor" in svg("reloj")
    assert set(CATEGORIAS) == {"cabecera", "atractivo", "finca", "acopio"}
    assert estilo_categoria("otra")[2] == "pin"

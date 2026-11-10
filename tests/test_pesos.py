import pytest

from rutas.graph import pesos


def test_maxspeed_explicito_gana_sobre_el_tipo_de_via():
    assert pesos.velocidad_kmh({"highway": "residential", "maxspeed": "40"}) == 40.0


def test_maxspeed_como_lista_toma_el_primer_valor():
    assert pesos.velocidad_kmh({"highway": "tertiary", "maxspeed": ["60", "40"]}) == 60.0


def test_residencial_sin_velocidad_es_30():
    assert pesos.velocidad_kmh({"highway": "residential"}) == 30.0


def test_troncal_sin_velocidad_es_50():
    assert pesos.velocidad_kmh({"highway": "trunk", "name": "Carrera 23"}) == 50.0
    assert pesos.velocidad_kmh({"highway": "trunk", "ref": "40"}) == 50.0


def test_tipo_con_lista_usa_el_primero():
    assert pesos.velocidad_kmh({"highway": ["unclassified", "residential"]}) == 30.0


def test_enlace_usa_el_tipo_base():
    assert pesos.velocidad_kmh({"highway": "primary_link"}) == 50.0


def test_tiempo_es_distancia_entre_velocidad():
    # 1.000 m a 36 km/h = 100 s
    assert pesos.tiempo_s({"length": 1000.0, "maxspeed": "36"}) == pytest.approx(100.0)


def test_maxspeed_invalido_cae_al_tipo_de_via():
    assert pesos.velocidad_kmh({"highway": "primary", "maxspeed": "none"}) == 50.0

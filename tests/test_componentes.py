"""Pruebas de los bloques HTML: escapan datos y respetan el contrato de entrada."""

from rutas.report import componentes as c


def test_tarjetas_datos_escapan_y_normalizan_el_tono():
    out = c.tarjetas_datos(
        [{"icono": "reloj", "etiqueta": "<b>x</b>", "valor": "5", "unidad": "min", "tono": "raro"}]
    )
    assert "<b>x</b>" not in out and "&lt;b&gt;x&lt;/b&gt;" in out
    assert "class='dato azul'" in out


def test_linea_tiempo_alterna_paradas_y_tramos():
    out = c.linea_tiempo(
        "Plaza <i>",
        [{"nombre": "A", "visita_min": 90}, {"nombre": "B", "visita_min": 60}],
        [10.0, 20.0, 30.0],
    )
    assert out.count("class='tl-t'") == 3 and out.count("class='tl-p") == 4
    assert "Plaza <i>" not in out and "Visita · 1 h 30 min" in out
    assert "30 min en carro" in out


def test_barra_limite_marca_el_exceso():
    assert "excede" in c.barra_limite(700, 660)
    assert "excede" not in c.barra_limite(300, 660)
    assert "--w:100.0%" in c.barra_limite(700, 660)


def test_leyenda_muestra_conteos():
    out = c.leyenda([("Fincas", "#30d158", "hoja", 8)])
    assert "Fincas" in out and "<b>8</b>" in out

import pytest

from rutas.data import descarga


def test_descargar_con_servidores_usa_el_siguiente_si_falla(monkeypatch):
    servidores = ["https://uno.test/api", "https://dos.test/api"]
    intentos = []

    monkeypatch.setattr(descarga, "SERVIDORES", servidores)
    monkeypatch.setattr(descarga.ox.settings, "overpass_url", "https://original.test/api")

    def descargar():
        intentos.append(descarga.ox.settings.overpass_url)
        if len(intentos) == 1:
            raise descarga.requests.exceptions.Timeout("servidor no disponible")
        return "grafo"

    grafo, servidor = descarga._descargar_con_servidores(descargar)

    assert grafo == "grafo"
    assert servidor == servidores[1]
    assert intentos == servidores
    assert descarga.ox.settings.overpass_url == "https://original.test/api"


def test_descargar_con_servidores_aplica_y_restaura_timeout(monkeypatch):
    monkeypatch.setattr(descarga, "SERVIDORES", ["https://uno.test/api"])
    monkeypatch.setattr(descarga.ox.settings, "requests_timeout", 180)
    visto = []

    def descargar():
        visto.append(descarga.ox.settings.requests_timeout)
        return "grafo"

    descarga._descargar_con_servidores(descargar, timeout_s=90)

    assert visto == [90]
    assert descarga.ox.settings.requests_timeout == 180


def test_timeout_por_red_crece_con_el_radio():
    assert descarga.timeout_para(2) == 90
    assert descarga.timeout_para(20) > descarga.timeout_para(10) > descarga.timeout_para(5)
    assert descarga.timeout_para(None) == 1800


def test_descargar_con_servidores_informa_fallo_total(monkeypatch):
    servidores = ["https://uno.test/api", "https://dos.test/api"]
    monkeypatch.setattr(descarga, "SERVIDORES", servidores)

    def descargar():
        raise descarga.requests.exceptions.ConnectionError("sin conexión")

    with pytest.raises(RuntimeError, match="ningún servidor Overpass"):
        descarga._descargar_con_servidores(descargar)

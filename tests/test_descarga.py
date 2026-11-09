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


def test_descargar_con_servidores_informa_fallo_total(monkeypatch):
    servidores = ["https://uno.test/api", "https://dos.test/api"]
    monkeypatch.setattr(descarga, "SERVIDORES", servidores)

    def descargar():
        raise descarga.requests.exceptions.ConnectionError("sin conexión")

    with pytest.raises(RuntimeError, match="ningún servidor Overpass"):
        descarga._descargar_con_servidores(descargar)

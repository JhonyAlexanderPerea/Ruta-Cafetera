import copy

from rutas.data import catalogo

MINIMOS = {"cabecera": 12, "atractivo": 15, "finca": 8, "acopio": 5}


def _catalogo_valido():
    filas = []
    for categoria, n in MINIMOS.items():
        for i in range(n):
            fila = {
                "id": f"{categoria[:3]}_{i:02d}",
                "nombre": f"{categoria} {i}",
                "municipio": "Armenia",
                "categoria": categoria,
                "lat": "4.53",
                "lon": "-75.67",
                "duracion_visita_min": "",
                "fuente_duracion": "",
                "fuente_coord": "Google Maps",
                "verificado": "True",
            }
            if categoria == "atractivo":
                fila["duracion_visita_min"] = "90"
                fila["fuente_duracion"] = "Guía oficial del sitio"
            filas.append(fila)
    return filas


def test_catalogo_valido_no_tiene_errores():
    assert catalogo.validar(_catalogo_valido()) == []


def test_categoria_incompleta_menciona_la_categoria():
    filas = [f for f in _catalogo_valido() if f["categoria"] != "acopio"]

    errores = catalogo.validar(filas)

    assert any("acopio" in e for e in errores)


def test_coordenada_fuera_del_quindio_se_reporta():
    filas = _catalogo_valido()
    filas[0]["lat"] = "10.0"

    errores = catalogo.validar(filas)

    assert any("fuera del Quindío" in e for e in errores)


def test_atractivo_sin_fuente_de_duracion_se_reporta():
    filas = _catalogo_valido()
    atractivo = next(f for f in filas if f["categoria"] == "atractivo")
    atractivo["fuente_duracion"] = ""

    errores = catalogo.validar(filas)

    assert any("duración" in e or "fuente" in e for e in errores)


def test_id_repetido_se_reporta():
    filas = _catalogo_valido()
    filas[1]["id"] = filas[0]["id"]

    errores = catalogo.validar(filas)

    assert any("repetido" in e for e in errores)


def test_menos_de_40_lugares_se_rechaza():
    filas = _catalogo_valido()[:-1]

    errores = catalogo.validar(filas)

    assert any("40" in e for e in errores)


def test_fila_sin_verificar_se_reporta_al_exigir_verificacion():
    filas = copy.deepcopy(_catalogo_valido())
    filas[0]["verificado"] = "False"

    assert any("verificado" in e for e in catalogo.validar(filas, exigir_verificado=True))
    assert catalogo.validar(filas, exigir_verificado=False) == []


def test_columnas_obligatorias_faltantes_se_reportan():
    filas = [{k: v for k, v in f.items() if k != "fuente_coord"} for f in _catalogo_valido()]

    errores = catalogo.validar(filas)

    assert any("fuente_coord" in e for e in errores)

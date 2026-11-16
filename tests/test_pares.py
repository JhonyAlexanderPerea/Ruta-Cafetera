import pytest

from rutas.data import pares


def _catalogo():
    # Tres municipios: A y B son vecinos; C no es vecino de ninguno.
    lugares = []
    for mun, n in (("A", 6), ("B", 6), ("C", 6)):
        for i in range(n):
            lugares.append(
                {
                    "id": f"{mun}{i}",
                    "municipio": mun,
                    "lat": 4.5 + 0.01 * i,
                    "lon": -75.6 + 0.01 * ord(mun),
                }
            )
    return lugares


VECINOS = {frozenset({"A", "B"})}


def test_genera_20_pares_con_10_lineales():
    resultado = pares.generar_pares(_catalogo(), VECINOS, seed=42)

    assert len(resultado) == 20
    assert sum(p["usa_lineal"] for p in resultado) == 10


def test_lineales_tienen_al_menos_4_del_mismo_municipio_y_el_resto_vecinos():
    resultado = pares.generar_pares(_catalogo(), VECINOS, seed=42)
    lineales = [p for p in resultado if p["usa_lineal"]]

    mismos = [p for p in lineales if p["mismo_municipio"]]
    otros = [p for p in lineales if not p["mismo_municipio"]]

    assert len(mismos) >= 4
    for p in otros:
        assert frozenset({p["municipio_origen"], p["municipio_destino"]}) in VECINOS


def test_es_reproducible_con_la_misma_semilla():
    a = pares.generar_pares(_catalogo(), VECINOS, seed=42)
    b = pares.generar_pares(_catalogo(), VECINOS, seed=42)

    assert a == b


def test_no_repite_pares_no_ordenados():
    resultado = pares.generar_pares(_catalogo(), VECINOS, seed=42)
    claves = [frozenset({p["origen"], p["destino"]}) for p in resultado]

    assert len(claves) == len(set(claves))


def test_catalogo_insuficiente_falla_con_mensaje_claro():
    solo_a = [lugar for lugar in _catalogo() if lugar["municipio"] == "A"]

    with pytest.raises(ValueError, match="pares"):
        pares.generar_pares(solo_a, VECINOS, seed=42)


def test_vecinos_csv_tiene_22_pares_del_quindio():
    vecinos = pares.cargar_vecinos()

    assert len(vecinos) == 22
    assert all(len(par) == 2 for par in vecinos)

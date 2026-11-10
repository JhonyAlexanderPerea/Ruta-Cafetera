import itertools
import random

import pytest

from rutas.algorithms import tsp_bruteforce, tsp_greedy, tsp_heldkarp

SOLVERS = [tsp_bruteforce.tsp_bruteforce, tsp_heldkarp.tsp_heldkarp]


def _matriz_a_mano():
    # Asimétrica. Partida 0; lugares 1, 2, 3.
    return [
        [0, 1, 15, 6],
        [2, 0, 7, 3],
        [9, 6, 0, 12],
        [10, 4, 8, 0],
    ]


def _costo_de(c, start, orden):
    ruta = [start, *orden, start]
    return sum(c[a][b] for a, b in zip(ruta, ruta[1:], strict=False))


def _matriz_aleatoria(rng, n):
    return [[0 if i == j else rng.randint(1, 50) for j in range(n)] for i in range(n)]


@pytest.mark.parametrize("fn", SOLVERS)
def test_caso_de_4_lugares_a_mano(fn):
    c = _matriz_a_mano()

    costo, orden = fn(c, 0, [1, 2, 3])

    # Mejor recorrido a mano: 0 -> 1 -> 3 -> 2 -> 0 = 1 + 3 + 8 + 9 = 21
    assert costo == 21
    assert sorted(orden) == [1, 2, 3]
    assert orden == [1, 3, 2]


@pytest.mark.parametrize("fn", SOLVERS)
def test_costo_coincide_con_el_recalculado(fn):
    c = _matriz_a_mano()

    costo, orden = fn(c, 0, [1, 2, 3])

    assert costo == _costo_de(c, 0, orden)


@pytest.mark.parametrize("fn", SOLVERS)
def test_lista_vacia(fn):
    costo, orden = fn(_matriz_a_mano(), 0, [])

    assert costo == 0
    assert orden == []


@pytest.mark.parametrize("fn", SOLVERS)
def test_un_solo_lugar(fn):
    c = _matriz_a_mano()

    costo, orden = fn(c, 0, [2])

    assert orden == [2]
    assert costo == c[0][2] + c[2][0]


@pytest.mark.parametrize("fn", SOLVERS)
def test_indice_repetido_lanza_error(fn):
    with pytest.raises(ValueError):
        fn(_matriz_a_mano(), 0, [1, 1, 2])


def test_fuerza_bruta_y_held_karp_coinciden_en_instancias_aleatorias():
    rng = random.Random(42)
    for _ in range(25):
        k = rng.randint(2, 7)
        n = k + 1
        c = _matriz_aleatoria(rng, n)
        lugares = list(range(1, n))

        cb, ob = tsp_bruteforce.tsp_bruteforce(c, 0, lugares)
        ch, oh = tsp_heldkarp.tsp_heldkarp(c, 0, lugares)

        assert ch == pytest.approx(cb)
        assert sorted(oh) == lugares
        assert _costo_de(c, 0, oh) == pytest.approx(ch)


def test_voraz_nunca_es_mejor_que_el_optimo():
    rng = random.Random(7)
    for _ in range(25):
        n = rng.randint(3, 8)
        c = _matriz_aleatoria(rng, n)
        lugares = list(range(1, n))

        optimo, _ = tsp_heldkarp.tsp_heldkarp(c, 0, lugares)
        cg, og = tsp_greedy.tsp_greedy(c, 0, lugares)

        assert cg >= optimo - 1e-9
        assert sorted(og) == lugares
        assert _costo_de(c, 0, og) == pytest.approx(cg)


def test_fuerza_bruta_recorre_todas_las_permutaciones():
    c = _matriz_a_mano()
    mejor = min(_costo_de(c, 0, p) for p in itertools.permutations([1, 2, 3]))

    costo, _ = tsp_bruteforce.tsp_bruteforce(c, 0, [1, 2, 3])

    assert costo == mejor


def test_voraz_caso_donde_no_es_optimo():
    # Voraz: 0 -> 2 (2), 2 -> 3 (4), 3 -> 1 (8), 1 -> 0 (2) = 16.
    # Óptimo: 0 -> 3 (5), 3 -> 2 (1), 2 -> 1 (7), 1 -> 0 (2) = 15.
    c = [
        [0, 3, 2, 5],
        [2, 0, 8, 8],
        [8, 7, 0, 4],
        [2, 8, 1, 0],
    ]
    cg, og = tsp_greedy.tsp_greedy(c, 0, [1, 2, 3])
    co, oo = tsp_heldkarp.tsp_heldkarp(c, 0, [1, 2, 3])

    assert og == [2, 3, 1]
    assert cg == 16
    assert oo == [3, 2, 1]
    assert co == 15
    assert cg > co

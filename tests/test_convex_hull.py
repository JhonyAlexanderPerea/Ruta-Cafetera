import math
import random

import numpy as np
import pytest
from scipy.spatial import ConvexHull

from rutas.algorithms.convex_hull_dc import convex_hull


def _conjunto(puntos):
    return set(map(tuple, puntos))


def _orientacion_ccw(h):
    # Área con signo positiva = antihorario.
    area2 = 0
    for i in range(len(h)):
        x1, y1 = h[i]
        x2, y2 = h[(i + 1) % len(h)]
        area2 += x1 * y2 - x2 * y1
    return area2 > 0


def test_cuadrado_con_puntos_interiores():
    pts = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (1, 3), (3, 1)]

    h = convex_hull(pts)

    assert _conjunto(h) == {(0, 0), (4, 0), (4, 4), (0, 4)}
    assert _orientacion_ccw(h)


def test_puntos_colineales_sobre_los_lados_no_son_vertices():
    pts = [(0, 0), (2, 0), (4, 0), (4, 4), (0, 4), (0, 2)]

    h = convex_hull(pts)

    assert _conjunto(h) == {(0, 0), (4, 0), (4, 4), (0, 4)}


def test_todos_colineales_devuelve_los_dos_extremos():
    pts = [(0, 0), (1, 1), (2, 2), (5, 5)]

    h = convex_hull(pts)

    assert _conjunto(h) == {(0, 0), (5, 5)}


def test_duplicados_se_eliminan():
    pts = [(0, 0), (0, 0), (3, 0), (3, 0), (0, 3), (0, 3)]

    h = convex_hull(pts)

    assert _conjunto(h) == {(0, 0), (3, 0), (0, 3)}
    assert len(h) == 3


@pytest.mark.parametrize(
    "pts,esperado",
    [
        ([(7, 7)], {(7, 7)}),
        ([(1, 2), (3, 4)], {(1, 2), (3, 4)}),
        ([(0, 0), (2, 0), (0, 2)], {(0, 0), (2, 0), (0, 2)}),
    ],
)
def test_casos_de_1_2_y_3_puntos(pts, esperado):
    assert _conjunto(convex_hull(pts)) == esperado


def test_circunferencia_entera_tiene_muchos_vertices():
    n = 360
    pts = [
        (round(1000 * math.cos(2 * math.pi * k / n)), round(1000 * math.sin(2 * math.pi * k / n)))
        for k in range(n)
    ]

    h = convex_hull(pts)

    # Con redondeo a enteros, algunos puntos quedan colineales y no son vértices (convexidad
    # estricta). La referencia es SciPy, no un número fijo.
    ref = ConvexHull(np.array(sorted(set(pts)), dtype=float))
    esperado = {tuple(map(int, sorted(set(pts))[i])) for i in ref.vertices}
    assert _conjunto(h) == esperado
    assert len(h) > 100
    assert _orientacion_ccw(h)


@pytest.mark.parametrize("semilla", range(40))
def test_compara_con_scipy_en_nubes_aleatorias(semilla):
    rng = random.Random(semilla)
    n = rng.randint(4, 300)
    pts = list({(rng.randint(-500, 500), rng.randint(-500, 500)) for _ in range(n)})
    if len(pts) < 4:
        pytest.skip("muy pocos puntos distintos")

    h = convex_hull(pts)
    ref = ConvexHull(np.array(pts, dtype=float))
    esperado = {tuple(map(int, pts[i])) for i in ref.vertices}

    assert _conjunto(h) == esperado
    assert _orientacion_ccw(h)


def test_nubes_agrupadas():
    rng = random.Random(3)
    pts = [(rng.randint(0, 20), rng.randint(0, 20)) for _ in range(500)]
    pts += [(rng.randint(1000, 1020), rng.randint(1000, 1020)) for _ in range(500)]

    h = convex_hull(pts)
    ref = ConvexHull(np.array(sorted(set(pts)), dtype=float))
    esperado = {tuple(map(int, sorted(set(pts))[i])) for i in ref.vertices}

    assert _conjunto(h) == esperado

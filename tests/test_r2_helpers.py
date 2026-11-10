import numpy as np

from rutas.experiments import r2_dijkstra as r2


def test_cociente_mediana_minimo_maximo():
    pares = [(10.0, 2.0), (9.0, 3.0), (8.0, 4.0)]  # cocientes 5, 3, 2

    s = r2.cociente_stats(pares)

    assert s == {"mediana": 3.0, "minimo": 2.0, "maximo": 5.0}


def test_matriz_valida_sin_problemas():
    M = np.array([[0.0, 3.0, 5.0], [3.0, 0.0, 2.0], [5.0, 2.0, 0.0]])

    v = r2.verificar_matriz(M)

    assert v["diagonal_ok"] is True
    assert v["infinitos"] == 0
    assert v["asimetricas"] == 0
    assert v["triangular_violaciones"] == 0


def test_matriz_detecta_asimetria_y_violacion_triangular():
    M = np.array([[0.0, 1.0, 10.0], [4.0, 0.0, 1.0], [10.0, 1.0, 0.0]])

    v = r2.verificar_matriz(M)

    assert v["asimetricas"] == 1  # solo el par (0,1): 1 frente a 4
    assert v["triangular_violaciones"] > 0  # d(0,2)=10 > d(0,1)+d(1,2)=2


def test_matriz_detecta_infinitos_y_diagonal():
    M = np.array([[0.0, np.inf], [1.0, 0.5]])

    v = r2.verificar_matriz(M)

    assert v["infinitos"] == 1
    assert v["diagonal_ok"] is False

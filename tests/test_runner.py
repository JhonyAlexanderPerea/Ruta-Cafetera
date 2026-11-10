import time

from rutas.bench import runner


def dormir_10_ms():
    time.sleep(0.01)


def dormir_5_s():
    time.sleep(5)


def devolver_constante():
    return 1


def test_mediana_de_una_funcion_que_duerme_10_ms():
    m = runner.measure(dormir_10_ms, reps=3, timeout_s=30)

    assert m.completed is True
    assert len(m.runs_ms) == 3
    assert 9.0 <= m.median_ms <= 80.0


def test_supera_el_limite_y_se_reporta_no_completada():
    m = runner.measure(dormir_5_s, reps=2, timeout_s=1)

    assert m.completed is False
    assert m.median_ms is None


def test_funcion_larga_se_mide_una_sola_vez():
    m = runner.measure(dormir_10_ms, reps=5, timeout_s=30, long_run_s=0.0)

    assert len(m.runs_ms) == 1


def test_resultado_y_metadatos_pequenos():
    m = runner.measure(devolver_constante, reps=2, timeout_s=30)

    assert m.completed is True
    assert isinstance(m.extra, dict)


def _preparar_datos_lentos(n):
    # Simula preparación pesada: la serialización de este argumento no debe contar.
    return [list(range(1000)) for _ in range(n)]


def contar(datos):
    return len(datos)


def test_preparacion_de_datos_queda_fuera_del_cronometro():
    import functools
    import time as _time

    datos = _preparar_datos_lentos(20000)
    fn = functools.partial(contar, datos)

    t0 = _time.perf_counter()
    m = runner.measure(fn, reps=2, timeout_s=60)
    total_s = _time.perf_counter() - t0

    assert m.completed is True
    # La llamada a `contar` tarda microsegundos; el resto (transferencia, arranque) no cuenta.
    assert m.median_ms < 200
    assert total_s >= m.median_ms / 1000

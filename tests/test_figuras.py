from rutas.report import figuras


def _ok(path):
    assert path.exists() and path.stat().st_size > 0


def test_r1(tmp_path):
    rows = [
        {"red": "a", "V_mas_E": "100", "tiempo_ms": "1.5"},
        {"red": "b", "V_mas_E": "1000", "tiempo_ms": "12.0"},
    ]
    out = tmp_path / "r1.png"
    figuras.figura_r1(rows, out)
    _ok(out)


def test_r2_filtra_no_completadas():
    rows = [
        {"estado": "completada", "version": "lineal"},
        {"estado": "agotada", "version": "lineal"},
    ]
    assert figuras.completadas(rows) == rows[:1]


def test_r2(tmp_path):
    rows = [
        {"version": v, "nodos_explorados": "5", "tiempo_ms": "0.5", "estado": "completada"}
        for v in ("lineal", "cola_prioridad")
    ] + [{"version": "lineal", "nodos_explorados": "9", "tiempo_ms": "1", "estado": "x"}]
    out = tmp_path / "r2.png"
    figuras.figura_r2(rows, out)
    _ok(out)


def test_r3(tmp_path):
    rows = [
        {"n": "100", "tiempo_propio_ms": "1.0", "tiempo_scipy_ms": "0.5"},
        {"n": "1000", "tiempo_propio_ms": "7.0", "tiempo_scipy_ms": "2.0"},
    ]
    out = tmp_path / "r3.png"
    figuras.figura_r3(rows, out)
    _ok(out)


def test_r4_exactas_con_no_completada(tmp_path):
    rows = [
        {"k": "5", "tiempo_fuerza_bruta_ms": "0.2", "tiempo_held_karp_ms": "0.1"},
        {"k": "6", "tiempo_fuerza_bruta_ms": "no completada", "tiempo_held_karp_ms": "0.4"},
    ]
    out = tmp_path / "r4.png"
    figuras.figura_r4_exactas(rows, out)
    _ok(out)


def test_r4_heuristica(tmp_path):
    rows = [
        {"k": "5", "brecha_promedio_pct": "8.7", "brecha_maxima_pct": "19.2"},
        {"k": "8", "brecha_promedio_pct": "9.9", "brecha_maxima_pct": "21.6"},
    ]
    out = tmp_path / "h.png"
    figuras.figura_r4_heuristica(rows, out)
    _ok(out)

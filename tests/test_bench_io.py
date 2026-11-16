import csv

import pytest

from rutas.bench import io as bio
from rutas.bench import machine_info


def test_escribe_csv_con_columnas_fijas(tmp_path):
    ruta = tmp_path / "r1.csv"
    bio.escribir_csv(
        ruta,
        ["red", "V", "E", "V_mas_E", "tiempo_ms"],
        [{"red": "radio_2km", "V": 1, "E": 2, "V_mas_E": 3, "tiempo_ms": 0.5}],
    )
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    assert list(filas[0].keys()) == ["red", "V", "E", "V_mas_E", "tiempo_ms"]
    assert filas[0]["tiempo_ms"] == "0.5"


def test_valida_columnas_minimas(tmp_path):
    ruta = tmp_path / "r1.csv"
    ruta.write_text("red,V,E\nx,1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="tiempo_ms"):
        bio.validar_columnas(ruta, ["red", "V", "E", "tiempo_ms"])


def test_machine_info_tiene_los_campos_del_protocolo():
    info = machine_info.recolectar()
    for clave in ["procesador", "ram_gb", "so", "python", "librerias", "commit", "fecha"]:
        assert clave in info
    assert info["ram_gb"] > 0

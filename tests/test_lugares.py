import math

import numpy as np
from pyproj import Transformer

from rutas.graph import lugares

A_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)


def _nodos():
    # Tres nodos cerca de Armenia: A, B (~1 km al este de A) y C (~3 km al norte de A).
    coords = [(4.5300, -75.6700), (4.5300, -75.6610), (4.5570, -75.6700)]
    osmids = [101, 102, 103]
    xy = np.array([A_UTM.transform(lon, lat) for lat, lon in coords])
    return xy, osmids


def test_asigna_al_nodo_mas_cercano_en_linea_recta():
    xy, osmids = _nodos()
    # Lugar a ~100 m al este del nodo B: debe asignarse a B.
    lugar = {"id": "x", "lat": 4.5300, "lon": -75.6609}

    res = lugares.asignar([lugar], xy, osmids)[0]

    assert res["osmid"] == 102
    assert res["nodo_idx"] == 1
    assert res["dist_nodo_m"] < 150
    assert res["a_mas_de_500m"] is False


def test_marca_lugares_a_mas_de_500_m():
    xy, osmids = _nodos()
    # Lugar en medio de la nada, ~1 km al sur de A.
    lugar = {"id": "y", "lat": 4.5210, "lon": -75.6700}

    res = lugares.asignar([lugar], xy, osmids)[0]

    assert res["a_mas_de_500m"] is True
    assert res["dist_nodo_m"] > 500


def test_distancia_coincide_con_calculo_independiente():
    xy, osmids = _nodos()
    lugar = {"id": "z", "lat": 4.5350, "lon": -75.6690}

    res = lugares.asignar([lugar], xy, osmids)[0]
    px, py = A_UTM.transform(lugar["lon"], lugar["lat"])
    esperado = min(math.hypot(px - x, py - y) for x, y in xy)

    # La salida se redondea a 0,1 m; la comparación tolera ese redondeo.
    assert math.isclose(res["dist_nodo_m"], esperado, abs_tol=0.1)

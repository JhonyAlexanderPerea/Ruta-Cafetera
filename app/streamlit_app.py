"""Aplicación Streamlit (R5): ruta, envolvente, itinerario y resultados.

Solo lee data/processed/, results/ y figures/. Ver specs/r5_aplicacion.md."""

import json
import os
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from rutas import app_servicios as svc
from rutas.config import DATA_PROCESSED, FIGURES, RESULTS

# RUTAS_DATA_DIR permite apuntar la app a otra carpeta de datos (pruebas).
DATA = Path(os.environ.get("RUTAS_DATA_DIR", DATA_PROCESSED))
UMBRAL_MIN = 660
PISTA = "generar con el pipeline de R1 (ver README)"
TABLAS = [
    ("r1_tamano_red.csv", "Tamaño de la red (conteos, sin unidad de tiempo)"),
    ("r1_tiempos_componente.csv", "Tiempos de la componente fuertemente conexa (ms)"),
    ("r2_cociente.csv", "Cociente de tiempos de Dijkstra (adimensional)"),
    ("r2_dijkstra.csv", "Dijkstra (viaje en s; tiempo de ejecución en ms)"),
    ("r3_envolvente.csv", "Envolvente convexa (tiempos en ms)"),
    ("r4_exactas.csv", "Soluciones exactas del TSP (tiempos en ms)"),
    ("r4_heuristica.csv", "Heurística voraz (brecha en %)"),
    ("r4_itinerario.csv", "Itinerario (desplazamiento y visita en min; acumulado en h)"),
]

st.set_page_config(page_title="Ruta Cafetera", layout="wide")


@st.cache_resource
def grafo(ruta: str):
    return svc.cargar_grafo(ruta)


@st.cache_data
def lugares(ruta: str):
    return svc.cargar_lugares(ruta)


@st.cache_data
def nodos(ruta: str):
    return svc.cargar_nodos(ruta)


@st.cache_data
def matriz(ruta: str):
    return svc.cargar_matriz(ruta)


@st.cache_data
def hull(ruta: str):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)["vertices"]


@st.cache_data
def tabla(ruta: str) -> pd.DataFrame:
    return pd.read_csv(ruta)


def faltan(*archivos: Path) -> bool:
    """Muestra un error por cada archivo ausente; True si falta alguno."""
    ausentes = [a for a in archivos if not a.exists()]
    for a in ausentes:
        st.error(f"Falta el archivo {a.name}: {PISTA}.")
    return bool(ausentes)


def vista_ruta():
    st.header("Ruta más rápida entre dos lugares")
    p, n, g = DATA / "places.csv", DATA / "nodes.csv", DATA / "graph_csr.npz"
    if faltan(p, n, g):
        return
    por_nombre = {x["nombre"]: x for x in lugares(str(p))}
    c1, c2 = st.columns(2)
    o = c1.selectbox("Origen", list(por_nombre), index=0)
    d = c2.selectbox("Destino", list(por_nombre), index=min(1, len(por_nombre) - 1))
    if o == d:
        st.warning("El origen y el destino son el mismo lugar.")
        return
    res = svc.ruta_optima(
        grafo(str(g)), nodos(str(n)), por_nombre[o]["nodo_idx"], por_nombre[d]["nodo_idx"]
    )
    if "error" in res:
        st.error(res["error"])
        return
    st.metric("Tiempo de viaje (min)", f"{res['tiempo_min']:.1f}")
    m = folium.Map(location=res["polilinea"][0], zoom_start=11)
    folium.PolyLine(res["polilinea"], color="red", weight=4).add_to(m)
    for nombre in (o, d):
        x = por_nombre[nombre]
        folium.Marker((x["lat"], x["lon"]), tooltip=nombre).add_to(m)
    st_folium(m, height=500, width=None, key="mapa_ruta", returned_objects=[])


def vista_envolvente():
    st.header("Envolvente convexa del departamento")
    h, p = DATA / "hull.json", DATA / "places.csv"
    if faltan(h, p):
        return
    vert = [(v["lat"], v["lon"]) for v in hull(str(h))]
    centro = (sum(v[0] for v in vert) / len(vert), sum(v[1] for v in vert) / len(vert))
    m = folium.Map(location=centro, zoom_start=9)
    folium.Polygon(vert, color="blue", fill=True, fill_opacity=0.1).add_to(m)
    for x in lugares(str(p)):
        folium.CircleMarker((x["lat"], x["lon"]), radius=4, tooltip=x["nombre"]).add_to(m)
    st_folium(m, height=500, width=None, key="mapa_hull", returned_objects=[])
    csv = RESULTS / "r3_envolvente.csv"
    if not csv.exists():
        st.info(f"No se encontró {csv.name} en results/.")
        return
    df = tabla(str(csv))
    fila = df.iloc[0]
    st.caption(
        f"Conjunto: {fila['conjunto']} ({int(fila['n'])} puntos); "
        f"{int(fila['vertices'])} vértices en la envolvente."
    )


def vista_itinerario():
    st.header("Itinerario de atractivos")
    p, mx = DATA / "places.csv", RESULTS / "r2_matriz_tiempos.csv"
    if faltan(p, mx):
        return
    lug = lugares(str(p))
    nombre = {x["id"]: x["nombre"] for x in lug}
    dur = {x["id"]: x["duracion_visita_min"] for x in lug}
    ids, mat = matriz(str(mx))
    partidas = [i for i in ids if i in nombre]
    ini = partidas.index("cab_01") if "cab_01" in partidas else 0
    partida = st.selectbox("Partida", partidas, index=ini, format_func=nombre.get)
    atr = [x["nombre"] for x in lug if x["categoria"] == "atractivo" and x["id"] in ids]
    por_id = {v: k for k, v in nombre.items()}
    sel = [por_id[n] for n in st.multiselect("Atractivos (de 6 a 8)", atr)]
    err = svc.validar_itinerario(sel)
    if err:
        st.error(err)
        return
    res = svc.itinerario(mat, ids, dur, partida, sel)
    if "error" in res:
        st.error(res["error"])
        return
    for clave, titulo in (("heldkarp", "Óptimo (Held-Karp)"), ("voraz", "Voraz")):
        r = res[clave]
        st.subheader(titulo)
        st.write(" → ".join(nombre[i] for i in r["orden"]))
        a, b, c = st.columns(3)
        a.metric("Desplazamiento (min)", f"{r['desplazamiento_min']:.1f}")
        b.metric("Visita (min)", f"{r['visita_min']:.1f}")
        c.metric("Total (min)", f"{r['total_min']:.1f}")
        if r["total_min"] > UMBRAL_MIN:
            st.warning(f"El total supera 11 h ({UMBRAL_MIN} min).")
    st.info(
        f"Diferencia voraz - óptimo: {res['diferencia_min']:.1f} min "
        f"({res['diferencia_pct']:.1f} %)."
    )


def vista_resultados():
    st.header("Resultados de R1 a R4")
    for archivo, titulo in TABLAS:
        st.subheader(titulo)
        ruta = RESULTS / archivo
        if ruta.exists():
            st.dataframe(tabla(str(ruta)))
        else:
            st.info(f"No se encontró {archivo} en results/.")
    st.subheader("Gráficas (ver unidad en cada eje)")
    imgs = sorted(FIGURES.glob("*.png"))
    if not imgs:
        st.info("No hay imágenes en figures/.")
    for img in imgs:
        st.image(str(img), caption=img.name)


VISTAS = {
    "Ruta": vista_ruta,
    "Envolvente": vista_envolvente,
    "Itinerario": vista_itinerario,
    "Resultados": vista_resultados,
}
st.title("Ruta Cafetera")
VISTAS[st.sidebar.radio("Vista", list(VISTAS))]()

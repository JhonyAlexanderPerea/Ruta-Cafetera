"""Aplicación Streamlit (R5): ruta, envolvente, itinerario y resultados.

Solo lee data/processed/, results/ y figures/. Ver specs/r5_aplicacion.md.
El estilo visual está en app/estilo.css; la lógica, en src/rutas/app_servicios.py."""

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
    ("r1_tamano_red.csv", "Tamaño de la red", "conteos, sin unidad de tiempo"),
    ("r1_tiempos_componente.csv", "Componente fuertemente conexa", "tiempos en ms"),
    ("r2_cociente.csv", "Cociente de Dijkstra", "adimensional"),
    ("r2_dijkstra.csv", "Dijkstra", "viaje en s; tiempo de ejecución en ms"),
    ("r3_envolvente.csv", "Envolvente convexa", "tiempos en ms"),
    ("r4_exactas.csv", "Soluciones exactas del TSP", "tiempos en ms"),
    ("r4_heuristica.csv", "Heurística voraz", "brecha en %"),
    ("r4_itinerario.csv", "Itinerario del día", "min; acumulado en h"),
]
VISTAS = ["Ruta", "Envolvente", "Itinerario", "Resultados"]
# Teselas de OpenStreetMap (sin API key). El filtro oscuro va dentro del mapa porque
# st_folium lo renderiza en un iframe que no hereda el CSS de la página.
ESTILO_MAPA = (
    "<style>.leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.85)"
    " saturate(.6)}.leaflet-container{background:#0b0d12}</style>"
)


def mapa(centro: tuple[float, float], zoom: int) -> folium.Map:
    m = folium.Map(location=centro, zoom_start=zoom, tiles="OpenStreetMap")
    m.get_root().header.add_child(folium.Element(ESTILO_MAPA))
    return m

st.set_page_config(page_title="Ruta Cafetera", page_icon="☕", layout="wide")
st.markdown(
    f"<style>{(Path(__file__).with_name('estilo.css')).read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)


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


def tarjeta(titulo: str, subtitulo: str = ""):
    """Abre una tarjeta de vidrio con título y subtítulo opcional."""
    contenedor = st.container(border=True)
    with contenedor:
        st.subheader(titulo)
        if subtitulo:
            st.caption(subtitulo)
    return contenedor


def vista_ruta():
    p, n, g = DATA / "places.csv", DATA / "nodes.csv", DATA / "graph_csr.npz"
    with tarjeta("Ruta más rápida", "Dijkstra con cola de prioridad, calculado al momento."):
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
        m = mapa(res["polilinea"][0], 11)
        folium.PolyLine(res["polilinea"], color="#0a84ff", weight=5, opacity=0.9).add_to(m)
        for nombre in (o, d):
            x = por_nombre[nombre]
            folium.Marker((x["lat"], x["lon"]), tooltip=nombre).add_to(m)
        st_folium(m, height=460, width=None, key="mapa_ruta", returned_objects=[])


def vista_envolvente():
    h, p = DATA / "hull.json", DATA / "places.csv"
    with tarjeta(
        "Envolvente convexa del departamento", "Polígono de R3 con los lugares del catálogo."
    ):
        if faltan(h, p):
            return
        vert = [(v["lat"], v["lon"]) for v in hull(str(h))]
        centro = (sum(v[0] for v in vert) / len(vert), sum(v[1] for v in vert) / len(vert))
        m = mapa(centro, 9)
        folium.Polygon(
            vert, color="#c8a27a", weight=2, fill=True, fill_color="#c8a27a", fill_opacity=0.12
        ).add_to(m)
        for x in lugares(str(p)):
            folium.CircleMarker(
                (x["lat"], x["lon"]), radius=4, color="#0a84ff", fill=True, tooltip=x["nombre"]
            ).add_to(m)
        st_folium(m, height=500, width=None, key="mapa_hull", returned_objects=[])
        csv = RESULTS / "r3_envolvente.csv"
        if not csv.exists():
            st.info(f"No se encontró {csv.name} en results/.")
            return
        fila = tabla(str(csv)).iloc[0]
        st.caption(
            f"Conjunto: {fila['conjunto']} ({int(fila['n'])} puntos) · "
            f"{int(fila['vertices'])} vértices en la envolvente."
        )


def vista_itinerario():
    p, mx = DATA / "places.csv", RESULTS / "r2_matriz_tiempos.csv"
    with tarjeta("Itinerario de atractivos", "Elige partida y de 6 a 8 atractivos."):
        if faltan(p, mx):
            return
        lug = lugares(str(p))
        nombre = {x["id"]: x["nombre"] for x in lug}
        dur = {x["id"]: x["duracion_visita_min"] for x in lug}
        ids, mat = matriz(str(mx))
        partidas = [i for i in ids if i in nombre]
        ini = partidas.index("cab_01") if "cab_01" in partidas else 0
        c1, c2 = st.columns([1, 2])
        partida = c1.selectbox("Partida", partidas, index=ini, format_func=nombre.get)
        atr = [x["nombre"] for x in lug if x["categoria"] == "atractivo" and x["id"] in ids]
        por_id = {v: k for k, v in nombre.items()}
        sel = [por_id[n] for n in c2.multiselect("Atractivos (de 6 a 8)", atr)]
        err = svc.validar_itinerario(sel)
        if err:
            st.error(err)
            return
        res = svc.itinerario(mat, ids, dur, partida, sel)
        if "error" in res:
            st.error(res["error"])
            return
        izq, der = st.columns(2)
        for col, clave, titulo in (
            (izq, "heldkarp", "Óptimo · Held-Karp"),
            (der, "voraz", "Heurística · voraz"),
        ):
            with col.container(border=True):
                r = res[clave]
                st.subheader(titulo)
                st.markdown(
                    f"<p class='ruta-orden'>{' → '.join(nombre[i] for i in r['orden'])}</p>",
                    unsafe_allow_html=True,
                )
                a, b, c = st.columns(3)
                a.metric("Desplazamiento (min)", f"{r['desplazamiento_min']:.1f}")
                b.metric("Visita (min)", f"{r['visita_min']:.1f}")
                c.metric("Total (min)", f"{r['total_min']:.1f}")
                if r["total_min"] > UMBRAL_MIN:
                    st.warning(f"El total supera 11 h ({UMBRAL_MIN} min).")
        st.markdown(
            f"<span class='pastilla'>Diferencia voraz − óptimo: "
            f"{res['diferencia_min']:.1f} min ({res['diferencia_pct']:.1f} %)</span>",
            unsafe_allow_html=True,
        )


def vista_resultados():
    st.subheader("Resultados de R1 a R4")
    st.caption("Cada tabla y gráfica indica su unidad de tiempo.")
    for archivo, titulo, unidad in TABLAS:
        with tarjeta(titulo, unidad):
            ruta = RESULTS / archivo
            if ruta.exists():
                st.dataframe(tabla(str(ruta)), use_container_width=True, hide_index=True)
            else:
                st.info(f"No se encontró {archivo} en results/.")
    imgs = sorted(FIGURES.glob("*.png"))
    st.subheader("Gráficas")
    if not imgs:
        st.info("No hay imágenes en figures/.")
    for i in range(0, len(imgs), 2):
        cols = st.columns(2)
        for col, img in zip(cols, imgs[i : i + 2], strict=False):
            with col.container(border=True):
                st.image(str(img), caption=img.name, use_container_width=True)


VISTAS_FN = {
    "Ruta": vista_ruta,
    "Envolvente": vista_envolvente,
    "Itinerario": vista_itinerario,
    "Resultados": vista_resultados,
}

st.markdown(
    """
    <header class="cabecera">
      <p class="marca">Quindío · Paisaje Cultural Cafetero</p>
      <h1>Ruta Cafetera</h1>
      <p>Rutas y recorridos entre los lugares del departamento, con los resultados de R1 a R4.</p>
    </header>
    """,
    unsafe_allow_html=True,
)
vista = st.radio("Vista", VISTAS, horizontal=True, label_visibility="collapsed")
VISTAS_FN[vista]()

"""Aplicación Streamlit (R5): ruta, envolvente, itinerario y resultados.

Solo lee data/processed/, results/ y figures/. Ver specs/r5_aplicacion.md.
El estilo visual está en app/estilo.css; la lógica, en src/rutas/app_servicios.py;
mapas, gráficas, tablas e iconos, en src/rutas/report/."""

import html
import json
import os
import random
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium

from rutas import app_servicios as svc
from rutas.config import DATA_PROCESSED, FIGURES, RESULTS
from rutas.report import componentes as ui
from rutas.report import graficas, mapas
from rutas.report.iconos import CATEGORIAS, estilo_categoria, svg
from rutas.report.tablas import tabla_html

# RUTAS_DATA_DIR permite apuntar la app a otra carpeta de datos (pruebas).
DATA = Path(os.environ.get("RUTAS_DATA_DIR", DATA_PROCESSED))
UMBRAL_MIN = 660
PISTA = "generar con el pipeline de R1 (ver README)"
VISTAS = ["Ruta", "Envolvente", "Itinerario", "Resultados"]

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


@st.cache_data(show_spinner=False)
def explorados(g_ruta: str, n_ruta: str, origen: int, destino: int):
    return svc.nodos_explorados(grafo(g_ruta), nodos(n_ruta), origen, destino)


def faltan(*archivos: Path) -> bool:
    """Muestra un error por cada archivo ausente; True si falta alguno."""
    ausentes = [a for a in archivos if not a.exists()]
    for a in ausentes:
        st.error(f"Falta el archivo {a.name}: {PISTA}.")
    return bool(ausentes)


def html_(contenido: str) -> None:
    st.markdown(contenido, unsafe_allow_html=True)


def tarjeta(titulo: str, subtitulo: str = "", icono: str = "brujula"):
    """Abre una tarjeta de vidrio con icono, título y subtítulo opcional."""
    contenedor = st.container(border=True)
    with contenedor:
        html_(ui.cabecera_tarjeta(icono, titulo, subtitulo))
    return contenedor


def grafica(chart) -> None:
    st.altair_chart(chart, use_container_width=True, theme=None)


# ---------------------------------------------------------------- Ruta


def _invertir() -> None:
    st.session_state.origen, st.session_state.destino = (
        st.session_state.destino,
        st.session_state.origen,
    )


def _alternar_exploracion() -> None:
    st.session_state.ver_exploracion = not st.session_state.get("ver_exploracion", False)


def vista_ruta():
    p, n, g = DATA / "places.csv", DATA / "nodes.csv", DATA / "graph_csr.npz"
    with tarjeta(
        "Ruta más rápida",
        "Dijkstra con cola de prioridad, calculado al momento.",
        "ruta",
    ):
        if faltan(p, n, g):
            return
        por_nombre = {x["nombre"]: x for x in lugares(str(p))}
        nombres = list(por_nombre)
        st.session_state.setdefault("origen", nombres[0])
        st.session_state.setdefault("destino", nombres[min(1, len(nombres) - 1)])

        def con_municipio(nombre: str) -> str:
            return f"{nombre} · {por_nombre[nombre]['municipio']}"

        c1, cm, c2 = st.columns([5, 2, 5], vertical_alignment="bottom")
        c1.selectbox("Origen", nombres, key="origen", format_func=con_municipio)
        cm.button(
            "Invertir",
            icon=":material/swap_horiz:",
            on_click=_invertir,
            use_container_width=True,
            help="Intercambia el origen y el destino",
            key="invertir",
        )
        c2.selectbox("Destino", nombres, key="destino", format_func=con_municipio)
        o, d = st.session_state.origen, st.session_state.destino
        if o == d:
            st.warning("El origen y el destino son el mismo lugar.")
            return
        a, b = por_nombre[o], por_nombre[d]
        res = svc.ruta_optima(grafo(str(g)), nodos(str(n)), a["nodo_idx"], b["nodo_idx"])
        if "error" in res:
            st.error(res["error"])
            return

        recta = svc.distancia_recta_km((a["lat"], a["lon"]), (b["lat"], b["lon"]))
        rodeo = res["distancia_km"] / recta if recta else 1.0
        html_(
            ui.tarjetas_datos(
                [
                    {
                        "icono": "reloj",
                        "etiqueta": "Tiempo de viaje",
                        "valor": f"{res['tiempo_min']:.1f}",
                        "unidad": " min",
                        "nota": svc.formato_duracion(res["tiempo_min"])
                        if res["tiempo_min"] >= 60
                        else "menos de una hora",
                        "tono": "azul",
                    },
                    {
                        "icono": "ruta",
                        "etiqueta": "Distancia por carretera",
                        "valor": f"{res['distancia_km']:.1f}",
                        "unidad": " km",
                        "nota": f"{recta:.1f} km en línea recta",
                        "tono": "verde",
                    },
                    {
                        "icono": "velocidad",
                        "etiqueta": "Velocidad media",
                        "valor": f"{res['velocidad_kmh']:.0f}",
                        "unidad": " km/h",
                        "nota": f"rodeo de {rodeo:.2f}× sobre la recta",
                        "tono": "naranja",
                    },
                    {
                        "icono": "nodos",
                        "etiqueta": "Cruces recorridos",
                        "valor": f"{len(res['nodos']):,}",
                        "nota": f"{res['explorados']:,} nodos explorados",
                        "tono": "cafe",
                    },
                ]
            )
        )

        viendo = st.session_state.get("ver_exploracion", False)
        st.button(
            "Ocultar la exploración" if viendo else "Ver cómo explora Dijkstra",
            icon=":material/stop_circle:" if viendo else ":material/play_circle:",
            on_click=_alternar_exploracion,
            type="primary",
            key="boton_exploracion",
        )
        if viendo:
            st.caption(
                "Cada punto es un nodo que Dijkstra fija, del más cercano al más lejano; "
                "al terminar se dibuja la ruta óptima."
            )
            puntos = explorados(str(g), str(n), a["nodo_idx"], b["nodo_idx"])
            m = mapas.mapa_exploracion(puntos, res["polilinea"], a, b, res["explorados"])
            # st_folium solo transmite capas y descarta el script de la animación:
            # el mapa va completo en un iframe (todo el HTML lo genera la app, sin datos externos).
            components.html(m.get_root().render(), height=500)
        else:
            m = mapas.mapa_ruta(res["polilinea"], a, b)
            st_folium(
                m, height=500, width=None, key=f"mapa_ruta_{a['id']}_{b['id']}", returned_objects=[]
            )


# ---------------------------------------------------------------- Envolvente


def vista_envolvente():
    h, p = DATA / "hull.json", DATA / "places.csv"
    with tarjeta(
        "Envolvente convexa del departamento",
        "Polígono de R3 con los lugares del catálogo.",
        "area",
    ):
        if faltan(h, p):
            return
        todos = lugares(str(p))
        vertices = hull(str(h))
        vert = [(v["lat"], v["lon"]) for v in vertices]

        categorias = sorted({x["categoria"] for x in todos}, key=list(CATEGORIAS).index)
        etiquetas = {c: estilo_categoria(c)[0] for c in categorias}
        elegidas = st.pills(
            "Qué lugares mostrar",
            categorias,
            selection_mode="multi",
            default=categorias,
            format_func=etiquetas.get,
            key="pills_categorias",
        )
        t1, t2, _ = st.columns([1, 1, 2])
        poligono = t1.toggle("Polígono", value=True, key="ver_poligono")
        marcas = t2.toggle("Vértices", value=False, key="ver_vertices")

        visibles = [x for x in todos if x["categoria"] in (elegidas or [])]
        geo = svc.metricas_envolvente(vertices)
        html_(
            ui.tarjetas_datos(
                [
                    {
                        "icono": "brujula",
                        "etiqueta": "Vértices",
                        "valor": str(geo["vertices"]),
                        "tono": "azul",
                    },
                    {
                        "icono": "area",
                        "etiqueta": "Área",
                        "valor": f"{geo['area_km2']:,.0f}",
                        "unidad": " km²",
                        "tono": "cafe",
                    },
                    {
                        "icono": "regla",
                        "etiqueta": "Perímetro",
                        "valor": f"{geo['perimetro_km']:,.0f}",
                        "unidad": " km",
                        "tono": "verde",
                    },
                    {
                        "icono": "pin",
                        "etiqueta": "Lugares visibles",
                        "valor": f"{len(visibles)}",
                        "unidad": f" de {len(todos)}",
                        "tono": "naranja",
                    },
                ]
            )
        )
        conteo = {c: sum(1 for x in visibles if x["categoria"] == c) for c in categorias}
        html_(
            ui.leyenda(
                [
                    (etiquetas[c], estilo_categoria(c)[1], estilo_categoria(c)[2], conteo[c])
                    for c in categorias
                ]
            )
        )
        m = mapas.mapa_envolvente(vert, visibles, poligono, marcas)
        st_folium(m, height=520, width=None, key="mapa_hull", returned_objects=[])
        csv = RESULTS / "r3_envolvente.csv"
        if not csv.exists():
            st.info(f"No se encontró {csv.name} en results/.")
            return
        fila = tabla(str(csv)).iloc[0]
        st.caption(
            f"Conjunto: {fila['conjunto']} ({int(fila['n'])} puntos) · "
            f"{int(fila['vertices'])} vértices en la envolvente."
        )


# ---------------------------------------------------------------- Itinerario


def _limpiar_atractivos() -> None:
    st.session_state.atractivos = []


def _sugerir_atractivos(opciones: list[str]) -> None:
    st.session_state.atractivos = random.sample(opciones, k=svc.MIN_ATRACTIVOS)


def _recorrido(titulo: str, r: dict, nombre: dict, dur: dict, partida: str, mejor: bool) -> None:
    with st.container(border=True):
        insignia = "<span class='insignia'>Óptimo</span>" if mejor else ""
        html_(f"<h3 class='tarjeta-titulo'>{html.escape(titulo)}{insignia}</h3>")
        paradas = [{"nombre": nombre[i], "visita_min": dur[i]} for i in r["orden"]]
        html_(ui.linea_tiempo(nombre[partida], paradas, r["tramos_min"]))
        a, b, c = st.columns(3)
        a.metric("Desplazamiento (min)", f"{r['desplazamiento_min']:.1f}")
        b.metric("Visita (min)", f"{r['visita_min']:.1f}")
        c.metric("Total (min)", f"{r['total_min']:.1f}")
        html_(ui.barra_limite(r["total_min"], UMBRAL_MIN))
        if r["total_min"] > UMBRAL_MIN:
            st.warning(f"El total supera 11 h ({UMBRAL_MIN} min).")


def vista_itinerario():
    p, mx = DATA / "places.csv", RESULTS / "r2_matriz_tiempos.csv"
    with tarjeta("Itinerario de atractivos", "Elige partida y de 6 a 8 atractivos.", "brujula"):
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
        st.session_state.setdefault("atractivos", [])
        sel_n = c2.multiselect("Atractivos (de 6 a 8)", atr, key="atractivos")
        b1, b2, b3 = st.columns([1, 1, 3], vertical_alignment="center")
        b1.button(
            "Sugerir 6",
            icon=":material/casino:",
            on_click=_sugerir_atractivos,
            args=(atr,),
            use_container_width=True,
            key="sugerir",
        )
        b2.button(
            "Limpiar",
            icon=":material/close:",
            on_click=_limpiar_atractivos,
            use_container_width=True,
            key="limpiar",
        )
        cuenta = len(sel_n)
        b3.markdown(
            f"<div class='contador {'ok' if 6 <= cuenta <= 8 else ''}'>"
            f"<i style='--w:{min(cuenta / svc.MAX_ATRACTIVOS, 1) * 100:.0f}%'></i>"
            f"<span>{cuenta} de {svc.MIN_ATRACTIVOS} a {svc.MAX_ATRACTIVOS} elegidos</span></div>",
            unsafe_allow_html=True,
        )
        sel = [por_id[n] for n in sel_n]
        err = svc.validar_itinerario(sel)
        if err:
            st.error(err)
            return
        res = svc.itinerario(mat, ids, dur, partida, sel)
        if "error" in res:
            st.error(res["error"])
            return
        izq, der = st.columns(2)
        with izq:
            _recorrido("Óptimo · Held-Karp", res["heldkarp"], nombre, dur, partida, True)
        with der:
            _recorrido("Heurística · voraz", res["voraz"], nombre, dur, partida, False)
        grafica(graficas.grafica_comparacion(res["heldkarp"], res["voraz"]))
        html_(
            f"<span class='pastilla'>Diferencia voraz − óptimo: "
            f"{res['diferencia_min']:.1f} min ({res['diferencia_pct']:.1f} %)</span>"
        )


# ---------------------------------------------------------------- Resultados


def _tabla(archivo: str, titulo: str, unidad: str, icono: str = "nodos", grafico=None) -> None:
    with tarjeta(titulo, unidad, icono):
        ruta = RESULTS / archivo
        if not ruta.exists():
            st.info(f"No se encontró {archivo} en results/.")
            return
        df = tabla(str(ruta))
        if grafico is not None:
            grafica(grafico(df))
        html_(tabla_html(df))


def _kpis() -> None:
    def leer(nombre: str) -> pd.DataFrame | None:
        ruta = RESULTS / nombre
        return tabla(str(ruta)) if ruta.exists() else None

    items = []
    if (c := leer("r2_cociente.csv")) is not None:
        items.append(
            {
                "icono": "rayo",
                "etiqueta": "Cola de prioridad vs lineal",
                "valor": f"{c['mediana'].iloc[0]:.0f}×",
                "nota": "más rápida (mediana)",
                "tono": "azul",
            }
        )
    if (e := leer("r3_envolvente.csv")) is not None:
        items.append(
            {
                "icono": "area",
                "etiqueta": "Envolvente de la red",
                "valor": f"{int(e['vertices'].iloc[0])}",
                "unidad": " vértices",
                "nota": f"con {int(e['n'].iloc[0]):,} nodos",
                "tono": "cafe",
            }
        )
    if (h := leer("r4_heuristica.csv")) is not None:
        items.append(
            {
                "icono": "balanza",
                "etiqueta": "Brecha de la voraz",
                "valor": f"{h['brecha_promedio_pct'].mean():.1f}",
                "unidad": " %",
                "nota": "promedio sobre el óptimo",
                "tono": "naranja",
            }
        )
    if (i := leer("r4_itinerario.csv")) is not None:
        items.append(
            {
                "icono": "reloj",
                "etiqueta": "Itinerario del día",
                "valor": f"{i['acumulado_h'].iloc[-1]:.1f}",
                "unidad": " h",
                "nota": f"{len(i)} paradas",
                "tono": "verde",
            }
        )
    if items:
        html_(ui.tarjetas_datos(items))


def vista_resultados():
    html_(
        ui.cabecera_tarjeta(
            "balanza", "Resultados de R1 a R4", "Cada tabla y gráfica indica su unidad de tiempo."
        )
    )
    _kpis()
    r1, r2, r3, r4 = st.tabs(["R1 · Red", "R2 · Dijkstra", "R3 · Envolvente", "R4 · Recorrido"])
    with r1:
        _tabla("r1_tamano_red.csv", "Tamaño de la red", "conteos, sin unidad de tiempo", "nodos")
        _tabla(
            "r1_tiempos_componente.csv",
            "Componente fuertemente conexa",
            "tiempos en ms",
            "reloj",
            graficas.grafica_r1,
        )
    with r2:
        _tabla(
            "r2_dijkstra.csv",
            "Dijkstra",
            "viaje en s; tiempo de ejecución en ms",
            "ruta",
            graficas.grafica_r2,
        )
        _tabla("r2_cociente.csv", "Cociente de Dijkstra", "adimensional", "rayo")
    with r3:
        _tabla(
            "r3_envolvente.csv", "Envolvente convexa", "tiempos en ms", "area", graficas.grafica_r3
        )
    with r4:
        _tabla(
            "r4_exactas.csv",
            "Soluciones exactas del TSP",
            "tiempos en ms",
            "reloj",
            graficas.grafica_r4_exactas,
        )
        _tabla(
            "r4_heuristica.csv",
            "Heurística voraz",
            "brecha en %",
            "balanza",
            graficas.grafica_r4_heuristica,
        )
        _tabla(
            "r4_itinerario.csv",
            "Itinerario del día",
            "min; acumulado en h",
            "brujula",
            graficas.grafica_itinerario_dia,
        )
    imgs = sorted(FIGURES.glob("*.png"))
    with st.expander("Figuras originales del informe (PNG)"):
        if not imgs:
            st.info("No hay imágenes en figures/.")
        for i in range(0, len(imgs), 2):
            cols = st.columns(2)
            for col, img in zip(cols, imgs[i : i + 2], strict=False):
                col.image(str(img), caption=img.name, use_container_width=True)


VISTAS_FN = {
    "Ruta": vista_ruta,
    "Envolvente": vista_envolvente,
    "Itinerario": vista_itinerario,
    "Resultados": vista_resultados,
}

html_(
    f"""
    <header class="cabecera">
      <p class="marca">{svg("taza", 16)} Quindío · Paisaje Cultural Cafetero</p>
      <h1>Ruta Cafetera</h1>
      <p>Rutas y recorridos entre los lugares del departamento, con los resultados de R1 a R4.</p>
    </header>
    """
)
vista = st.radio("Vista", VISTAS, horizontal=True, label_visibility="collapsed")
VISTAS_FN[vista]()

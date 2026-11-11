"""Gráficas interactivas (Altair) de la vista Resultados. Solo presentación.

Leen DataFrames ya cargados de results/*.csv; no calculan nada nuevo. Cada gráfica
indica su unidad de tiempo en el eje (requisito de la sección 5 del enunciado)."""

from __future__ import annotations

import altair as alt
import pandas as pd

AZUL = "#0a84ff"
CAFE = "#c8a27a"
VERDE = "#30d158"
NARANJA = "#ff9f0a"
TEXTO = "#a1a1a6"
REJILLA = "rgba(255,255,255,0.08)"
FUENTE = "-apple-system, 'SF Pro Text', 'Segoe UI', Roboto, sans-serif"
ALTO = 320


def _estilo(chart: alt.TopLevelMixin) -> alt.TopLevelMixin:
    """Tema oscuro común: fondo transparente, rejilla tenue, leyenda arriba."""
    return (
        chart.configure(background="transparent", font=FUENTE)
        .configure_view(stroke=None)
        .configure_axis(
            labelColor=TEXTO,
            titleColor=TEXTO,
            titleFontWeight=500,
            gridColor=REJILLA,
            domainColor=REJILLA,
            tickColor=REJILLA,
            labelFontSize=12,
            titleFontSize=12,
        )
        .configure_legend(
            labelColor=TEXTO,
            titleColor=TEXTO,
            orient="top",
            direction="horizontal",
            symbolType="circle",
            symbolSize=140,
            labelFontSize=12,
            padding=0,
            title=None,
        )
    )


def _numerico(df: pd.DataFrame, *cols: str) -> pd.DataFrame:
    """Copia con las columnas dadas como número; lo que no lo es (p. ej. 'no completada') → NaN."""
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out.dropna(subset=list(cols))


def _hover() -> alt.Parameter:
    return alt.selection_point(on="pointerover", nearest=True, empty=False, clear="pointerout")


def grafica_r1(df: pd.DataFrame) -> alt.TopLevelMixin:
    d = _numerico(df[df["estado"] == "completada"], "V_mas_E", "tiempo_ms")
    base = alt.Chart(d).encode(
        x=alt.X("V_mas_E:Q", scale=alt.Scale(type="log"), title="V + E (elementos)"),
        y=alt.Y("tiempo_ms:Q", scale=alt.Scale(type="log"), title="Tiempo (ms)"),
    )
    linea = base.mark_line(color=AZUL, opacity=0.35, strokeDash=[5, 4])
    puntos = base.mark_circle(color=AZUL, size=140, opacity=0.95).encode(
        tooltip=[
            alt.Tooltip("red:N", title="Red"),
            alt.Tooltip("V:Q", title="Nodos"),
            alt.Tooltip("E:Q", title="Aristas"),
            alt.Tooltip("tiempo_ms:Q", title="Tiempo (ms)"),
        ]
    )
    texto = base.mark_text(dy=-16, color="#f5f5f7", fontSize=12, fontWeight=600).encode(
        text="red:N"
    )
    return _estilo((linea + puntos + texto).properties(height=ALTO))


def grafica_r2(df: pd.DataFrame) -> alt.TopLevelMixin:
    d = _numerico(df[df["estado"] == "completada"], "nodos_explorados", "tiempo_ms")
    d = d.assign(
        version=d["version"].map({"lineal": "Lineal", "cola_prioridad": "Cola de prioridad"})
    )
    color = alt.Color(
        "version:N",
        scale=alt.Scale(domain=["Lineal", "Cola de prioridad"], range=[CAFE, AZUL]),
    )
    return _estilo(
        alt.Chart(d)
        .mark_circle(size=120, opacity=0.8)
        .encode(
            x=alt.X("nodos_explorados:Q", title="Nodos explorados (unidades)"),
            y=alt.Y("tiempo_ms:Q", scale=alt.Scale(type="log"), title="Tiempo (ms)"),
            color=color,
            tooltip=[
                alt.Tooltip("origen:N", title="Origen"),
                alt.Tooltip("destino:N", title="Destino"),
                alt.Tooltip("version:N", title="Versión"),
                alt.Tooltip("nodos_explorados:Q", title="Nodos explorados"),
                alt.Tooltip("tiempo_ms:Q", title="Tiempo (ms)"),
            ],
        )
        .properties(height=ALTO)
        .interactive()
    )


def grafica_r3(df: pd.DataFrame) -> alt.TopLevelMixin:
    d = _numerico(df, "n", "tiempo_propio_ms", "tiempo_scipy_ms")
    largo = d.melt(
        id_vars=["conjunto", "n"],
        value_vars=["tiempo_propio_ms", "tiempo_scipy_ms"],
        var_name="implementación",
        value_name="tiempo_ms",
    ).assign(
        implementación=lambda x: x["implementación"].map(
            {"tiempo_propio_ms": "Propia (divide y vencerás)", "tiempo_scipy_ms": "SciPy"}
        )
    )
    return _estilo(
        alt.Chart(largo)
        .mark_line(point=alt.OverlayMarkDef(size=110, filled=True), strokeWidth=2.5)
        .encode(
            x=alt.X("n:Q", scale=alt.Scale(type="log"), title="n (puntos)"),
            y=alt.Y("tiempo_ms:Q", scale=alt.Scale(type="log"), title="Tiempo (ms)"),
            color=alt.Color(
                "implementación:N",
                scale=alt.Scale(
                    domain=["Propia (divide y vencerás)", "SciPy"], range=[AZUL, NARANJA]
                ),
            ),
            tooltip=[
                alt.Tooltip("conjunto:N", title="Conjunto"),
                alt.Tooltip("n:Q", title="Puntos"),
                alt.Tooltip("tiempo_ms:Q", title="Tiempo (ms)"),
            ],
        )
        .properties(height=ALTO)
    )


def grafica_r4_exactas(df: pd.DataFrame) -> alt.TopLevelMixin:
    largo = df.melt(
        id_vars="k",
        value_vars=["tiempo_fuerza_bruta_ms", "tiempo_held_karp_ms"],
        var_name="método",
        value_name="tiempo_ms",
    ).assign(
        método=lambda x: x["método"].map(
            {"tiempo_fuerza_bruta_ms": "Fuerza bruta", "tiempo_held_karp_ms": "Held-Karp"}
        )
    )
    largo = _numerico(largo, "k", "tiempo_ms")
    return _estilo(
        alt.Chart(largo)
        .mark_line(point=alt.OverlayMarkDef(size=110, filled=True), strokeWidth=2.5)
        .encode(
            x=alt.X("k:Q", title="k (lugares)", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("tiempo_ms:Q", scale=alt.Scale(type="log"), title="Tiempo (ms)"),
            color=alt.Color(
                "método:N",
                scale=alt.Scale(domain=["Fuerza bruta", "Held-Karp"], range=[CAFE, VERDE]),
            ),
            tooltip=[
                alt.Tooltip("método:N", title="Método"),
                alt.Tooltip("k:Q", title="k"),
                alt.Tooltip("tiempo_ms:Q", title="Tiempo (ms)"),
            ],
        )
        .properties(height=ALTO)
    )


def grafica_r4_heuristica(df: pd.DataFrame) -> alt.TopLevelMixin:
    d = _numerico(df, "k", "brecha_promedio_pct", "brecha_maxima_pct")
    banda = (
        alt.Chart(d)
        .mark_area(opacity=0.18, color=NARANJA, interpolate="monotone")
        .encode(x="k:Q", y="brecha_promedio_pct:Q", y2="brecha_maxima_pct:Q")
    )
    largo = d.melt(
        id_vars="k",
        value_vars=["brecha_promedio_pct", "brecha_maxima_pct"],
        var_name="serie",
        value_name="brecha",
    ).assign(
        serie=lambda x: x["serie"].map(
            {"brecha_promedio_pct": "Promedio", "brecha_maxima_pct": "Máxima"}
        )
    )
    lineas = (
        alt.Chart(largo)
        .mark_line(
            point=alt.OverlayMarkDef(size=110, filled=True), strokeWidth=2.5, interpolate="monotone"
        )
        .encode(
            x=alt.X("k:Q", title="k (lugares)", axis=alt.Axis(tickMinStep=1)),
            y=alt.Y("brecha:Q", title="Brecha respecto al óptimo (%)"),
            color=alt.Color(
                "serie:N", scale=alt.Scale(domain=["Promedio", "Máxima"], range=[AZUL, NARANJA])
            ),
            tooltip=[
                alt.Tooltip("serie:N", title="Serie"),
                alt.Tooltip("k:Q", title="k"),
                alt.Tooltip("brecha:Q", title="Brecha (%)", format=".2f"),
            ],
        )
    )
    return _estilo((banda + lineas).properties(height=ALTO))


def grafica_itinerario_dia(df: pd.DataFrame) -> alt.TopLevelMixin:
    """Barras apiladas por parada: desplazamiento y visita, ambos en minutos."""
    largo = df.melt(
        id_vars=["orden", "lugar"],
        value_vars=["desplazamiento_min", "visita_min"],
        var_name="tipo",
        value_name="min",
    ).assign(
        tipo=lambda x: x["tipo"].map(
            {"desplazamiento_min": "Desplazamiento", "visita_min": "Visita"}
        )
    )
    return _estilo(
        alt.Chart(largo)
        .mark_bar(cornerRadiusEnd=6, height=18)
        .encode(
            y=alt.Y(
                "lugar:N",
                sort=alt.EncodingSortField("orden"),
                title=None,
                axis=alt.Axis(labelLimit=220),
            ),
            x=alt.X("min:Q", title="Minutos", stack="zero"),
            color=alt.Color(
                "tipo:N", scale=alt.Scale(domain=["Desplazamiento", "Visita"], range=[AZUL, CAFE])
            ),
            tooltip=[
                alt.Tooltip("lugar:N", title="Lugar"),
                alt.Tooltip("tipo:N", title="Tipo"),
                alt.Tooltip("min:Q", title="Minutos", format=".1f"),
            ],
        )
        .properties(height=max(180, 34 * df.shape[0]))
    )


def grafica_comparacion(optimo: dict, voraz: dict) -> alt.TopLevelMixin:
    """Held-Karp frente a la voraz: minutos de desplazamiento y de visita apilados."""
    filas = [
        {"recorrido": nombre, "tipo": tipo, "min": r[clave]}
        for nombre, r in (("Óptimo · Held-Karp", optimo), ("Voraz", voraz))
        for tipo, clave in (("Desplazamiento", "desplazamiento_min"), ("Visita", "visita_min"))
    ]
    return _estilo(
        alt.Chart(pd.DataFrame(filas))
        .mark_bar(cornerRadiusEnd=8, height=34)
        .encode(
            y=alt.Y("recorrido:N", title=None, sort=["Óptimo · Held-Karp", "Voraz"]),
            x=alt.X("min:Q", title="Minutos", stack="zero"),
            color=alt.Color(
                "tipo:N", scale=alt.Scale(domain=["Desplazamiento", "Visita"], range=[AZUL, CAFE])
            ),
            tooltip=[
                alt.Tooltip("recorrido:N", title="Recorrido"),
                alt.Tooltip("tipo:N", title="Tipo"),
                alt.Tooltip("min:Q", title="Minutos", format=".1f"),
            ],
        )
        .properties(height=130)
    )

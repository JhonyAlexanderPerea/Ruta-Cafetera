"""Tablas HTML con barras de datos para la vista Resultados. Solo presentación.

Todo valor de la tabla se escapa con html.escape: los CSV son datos, nunca marcado."""

from __future__ import annotations

import html

import pandas as pd

# Columnas cuyo valor se ve mejor con una barra proporcional al máximo de la columna.
CLAVES_BARRA = ("ms", "tiempo", "brecha", "min", "_s", "cociente")


def _formato(valor: object) -> str:
    if isinstance(valor, bool):
        return "sí" if valor else "no"
    if isinstance(valor, float):
        return f"{valor:,.2f}".rstrip("0").rstrip(".") if abs(valor) < 1e6 else f"{valor:,.0f}"
    if isinstance(valor, int):
        return f"{valor:,}"
    return str(valor)


def _con_barra(col: str, serie: pd.Series) -> bool:
    return pd.api.types.is_float_dtype(serie) and any(c in col.lower() for c in CLAVES_BARRA)


def tabla_html(df: pd.DataFrame, max_filas: int = 200) -> str:
    """Devuelve una tabla `<table class="tabla-datos">` lista para st.markdown."""
    df = df.head(max_filas)
    maximos = {c: float(df[c].max()) for c in df.columns if _con_barra(c, df[c])}
    cabecera = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    filas = []
    for i, fila in enumerate(df.itertuples(index=False)):
        celdas = []
        for col, valor in zip(df.columns, fila, strict=True):
            texto = html.escape(_formato(valor))
            if col in maximos and maximos[col] > 0 and pd.notna(valor):
                ancho = max(2.0, 100 * float(valor) / maximos[col])
                celdas.append(
                    f"<td class='num'><span class='barra' style='--w:{ancho:.1f}%'></span>"
                    f"<span class='v'>{texto}</span></td>"
                )
            else:
                numero = isinstance(valor, int | float) and not isinstance(valor, bool)
                celdas.append(f"<td class='{'num' if numero else 'txt'}'>{texto}</td>")
        filas.append(f"<tr style='--i:{min(i, 12)}'>{''.join(celdas)}</tr>")
    return (
        "<div class='tabla-envoltura'><table class='tabla-datos'>"
        f"<thead><tr>{cabecera}</tr></thead><tbody>{''.join(filas)}</tbody></table></div>"
    )

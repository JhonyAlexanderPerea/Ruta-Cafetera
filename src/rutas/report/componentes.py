"""Bloques HTML de la interfaz (tarjetas de datos, línea de tiempo, leyenda). Solo presentación.

Todo texto que viene de datos se escapa con html.escape; el resto es marcado propio."""

from __future__ import annotations

import html

from rutas.app_servicios import formato_duracion
from rutas.report.iconos import svg

TONOS = ("azul", "cafe", "verde", "naranja")


def _e(texto: object) -> str:
    return html.escape(str(texto))


def cabecera_tarjeta(icono: str, titulo: str, subtitulo: str = "") -> str:
    sub = f"<p class='tarjeta-sub'>{_e(subtitulo)}</p>" if subtitulo else ""
    return (
        f"<div class='tarjeta-cab'><span class='tarjeta-ico'>{svg(icono, 22)}</span>"
        f"<div><h3 class='tarjeta-titulo'>{_e(titulo)}</h3>{sub}</div></div>"
    )


def tarjetas_datos(items: list[dict]) -> str:
    """Rejilla de datos: cada item trae icono, etiqueta, valor, unidad (opcional) y tono."""
    celdas = []
    for i, it in enumerate(items):
        tono = it.get("tono", "azul")
        tono = tono if tono in TONOS else "azul"
        unidad = f"<span class='dato-u'>{_e(it['unidad'])}</span>" if it.get("unidad") else ""
        nota = f"<small>{_e(it['nota'])}</small>" if it.get("nota") else ""
        celdas.append(
            f"<div class='dato {tono}' style='--i:{i}'>"
            f"<span class='dato-ico'>{svg(it['icono'], 20)}</span>"
            f"<span class='dato-e'>{_e(it['etiqueta'])}</span>"
            f"<span class='dato-v'>{_e(it['valor'])}{unidad}</span>{nota}</div>"
        )
    return f"<div class='datos'>{''.join(celdas)}</div>"


def linea_tiempo(
    partida: str, paradas: list[dict], tramos_min: list[float], visita_partida: bool = False
) -> str:
    """Itinerario vertical: partida, tramos de viaje, paradas con su visita y regreso."""
    pasos = [f"<li class='tl-p inicio' style='--i:0'>{_punto('casa', partida, 'Partida')}</li>"]
    for k, parada in enumerate(paradas):
        pasos.append(_tramo(tramos_min[k], k * 2 + 1))
        visita = formato_duracion(parada["visita_min"])
        pasos.append(
            f"<li class='tl-p' style='--i:{k * 2 + 2}'>"
            f"{_punto('estrella', parada['nombre'], f'Visita · {visita}', k + 1)}</li>"
        )
    pasos.append(_tramo(tramos_min[len(paradas)], len(paradas) * 2 + 1))
    pasos.append(
        f"<li class='tl-p fin' style='--i:{len(paradas) * 2 + 2}'>"
        f"{_punto('bandera', partida, 'Regreso')}</li>"
    )
    return f"<ol class='tl'>{''.join(pasos)}</ol>"


def _punto(icono: str, nombre: str, detalle: str, numero: int | None = None) -> str:
    insignia = f"<i class='tl-n'>{numero}</i>" if numero else ""
    return (
        f"<span class='tl-ico'>{svg(icono, 18)}{insignia}</span>"
        f"<div class='tl-txt'><b>{_e(nombre)}</b><small>{_e(detalle)}</small></div>"
    )


def _tramo(minutos: float, i: int) -> str:
    return (
        f"<li class='tl-t' style='--i:{i}'><span class='tl-viaje'>{svg('ruta', 14)}"
        f"{_e(formato_duracion(minutos))} en carro</span></li>"
    )


def barra_limite(total_min: float, limite_min: float) -> str:
    """Barra de la jornada: cuánto del límite (11 h) consume el recorrido."""
    pct = 100 * total_min / limite_min
    clase = "excede" if pct > 100 else ("alto" if pct > 85 else "")
    return (
        f"<div class='limite {clase}'><div class='limite-cab'><span>Jornada</span>"
        f"<b>{_e(formato_duracion(total_min))} de {_e(formato_duracion(limite_min))}</b></div>"
        f"<div class='limite-pista'><i style='--w:{min(pct, 100):.1f}%'></i></div></div>"
    )


def leyenda(items: list[tuple[str, str, str, int]]) -> str:
    """Chips (etiqueta, color, icono, conteo) para explicar los pines del mapa."""
    chips = "".join(
        f"<span class='chip' style='--c:{_e(color)}'>{svg(icono, 14)}{_e(etiqueta)}"
        f"<b>{conteo}</b></span>"
        for etiqueta, color, icono, conteo in items
    )
    return f"<div class='leyenda'>{chips}</div>"

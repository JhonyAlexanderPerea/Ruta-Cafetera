"""Mapas Folium de la app: ruta animada, exploración de Dijkstra y envolvente. Solo presentación.

El filtro oscuro y las animaciones van dentro del mapa porque st_folium lo renderiza en un
iframe que no hereda el CSS de la página."""

from __future__ import annotations

import html
import json
import math

import folium

from rutas.report.iconos import estilo_categoria, svg

AZUL = "#0a84ff"
CAFE = "#c8a27a"
NARANJA = "#ff9f0a"

ESTILO_MAPA = """
<style>
.leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.85) saturate(.6)}
.leaflet-container{background:#0b0d12;font-family:-apple-system,'Segoe UI',Roboto,sans-serif}
.pin{width:34px;height:34px;border-radius:50%;display:grid;place-items:center;color:#fff;
  background:var(--c);border:2px solid rgba(255,255,255,.9);box-shadow:0 4px 14px rgba(0,0,0,.5);
  transition:transform .25s cubic-bezier(.22,1,.36,1);animation:aparece .5s cubic-bezier(.22,1,.36,1) both}
.pin:hover{transform:scale(1.25) translateY(-3px)}
.pin svg{width:18px;height:18px}
.pin.grande{width:42px;height:42px}.pin.grande svg{width:22px;height:22px}
.pin.punto{width:14px;height:14px;border-width:2px}
@keyframes aparece{from{opacity:0;transform:scale(.3) translateY(-12px)}to{opacity:1}}
.ruta-viva{stroke-dasharray:10 12;animation:marcha 1.1s linear infinite}
@keyframes marcha{to{stroke-dashoffset:-22}}
.hull-viva{animation:pulso 3.6s ease-in-out infinite}
@keyframes pulso{50%{fill-opacity:.3;stroke-opacity:.6}}
.leaflet-tooltip{background:rgba(28,28,30,.92);color:#f5f5f7;border:1px solid rgba(255,255,255,.14);
  border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.45);padding:6px 10px;font-weight:600}
.leaflet-tooltip small{display:block;color:#a1a1a6;font-weight:500}
.leaflet-tooltip-top:before{border-top-color:rgba(28,28,30,.92)}
.expl-panel{background:rgba(28,28,30,.88);color:#f5f5f7;border:1px solid rgba(255,255,255,.14);
  border-radius:16px;padding:12px 14px;min-width:210px;backdrop-filter:blur(14px);
  box-shadow:0 12px 32px rgba(0,0,0,.5)}
.expl-panel b{font-size:1.35rem;letter-spacing:-.02em}
.expl-panel small{color:#a1a1a6;display:block;margin-bottom:6px}
.expl-barra{height:6px;border-radius:99px;background:rgba(255,255,255,.12);overflow:hidden;margin:8px 0 10px}
.expl-barra i{display:block;height:100%;width:0;border-radius:99px;
  background:linear-gradient(90deg,#0a84ff,#30d158,#ff9f0a)}
.expl-panel button{all:unset;cursor:pointer;padding:5px 11px;border-radius:99px;font-size:.8rem;
  font-weight:600;background:rgba(255,255,255,.1);margin-right:5px;transition:background .2s}
.expl-panel button:hover{background:rgba(255,255,255,.22)}
.expl-panel button.on{background:#f5f5f7;color:#000}
</style>
"""


def mapa_base(centro: tuple[float, float], zoom: int) -> folium.Map:
    m = folium.Map(location=centro, zoom_start=zoom, tiles="OpenStreetMap", zoom_control=True)
    m.get_root().header.add_child(folium.Element(ESTILO_MAPA))
    return m


def _pin(color: str, icono: str, grande: bool = False) -> folium.DivIcon:
    clase = "pin grande" if grande else "pin"
    tam = 42 if grande else 34
    return folium.DivIcon(
        html=f'<div class="{clase}" style="--c:{color}">{svg(icono, 22 if grande else 18)}</div>',
        icon_size=(tam, tam),
        icon_anchor=(tam // 2, tam // 2),
    )


def _tooltip(nombre: str, detalle: str = "") -> folium.Tooltip:
    extra = f"<small>{html.escape(detalle)}</small>" if detalle else ""
    return folium.Tooltip(f"{html.escape(nombre)}{extra}", sticky=False)


def _ruta_con_brillo(m: folium.Map, polilinea: list[tuple[float, float]]) -> None:
    folium.PolyLine(polilinea, color=AZUL, weight=14, opacity=0.18).add_to(m)
    folium.PolyLine(
        polilinea, color="#5ac8fa", weight=5, opacity=0.95, class_name="ruta-viva"
    ).add_to(m)


def _extremos(m: folium.Map, origen: dict, destino: dict) -> None:
    folium.Marker(
        (origen["lat"], origen["lon"]),
        icon=_pin("#30d158", "pin", grande=True),
        tooltip=_tooltip(origen["nombre"], f"Origen · {origen['municipio']}"),
    ).add_to(m)
    folium.Marker(
        (destino["lat"], destino["lon"]),
        icon=_pin(NARANJA, "bandera", grande=True),
        tooltip=_tooltip(destino["nombre"], f"Destino · {destino['municipio']}"),
    ).add_to(m)


def mapa_ruta(polilinea: list[tuple[float, float]], origen: dict, destino: dict) -> folium.Map:
    m = mapa_base(*encuadre(polilinea))
    _ruta_con_brillo(m, polilinea)
    _extremos(m, origen, destino)
    return m


_JS_EXPLORACION = """
window.addEventListener('load', function () {
  var map = __MAPA__, pts = __PUNTOS__, ruta = __RUTA__, total = __TOTAL__;
  var lienzo = L.canvas({padding: 0.5}), capa = L.layerGroup().addTo(map);
  var viva = null, i = 0, paso = 1, activo = false, n = pts.length;
  var ctl = L.control({position: 'topright'});
  ctl.onAdd = function () {
    var d = L.DomUtil.create('div', 'expl-panel');
    d.innerHTML = '<small>Nodos explorados por Dijkstra</small><b id="ex-n">0</b>' +
      ' <span style="color:#a1a1a6">/ ' + total.toLocaleString('es') + '</span>' +
      '<div class="expl-barra"><i id="ex-b"></i></div>' +
      '<button id="ex-play">Pausar</button><button id="ex-re">Repetir</button>' +
      '<div style="margin-top:8px"><button data-v="1" class="on">1×</button>' +
      '<button data-v="2">2×</button><button data-v="4">4×</button></div>';
    L.DomEvent.disableClickPropagation(d);
    return d;
  };
  ctl.addTo(map);
  var el = function (id) { return document.getElementById(id); };
  map.fitBounds(L.latLngBounds(pts), {padding: [30, 30]});

  function color(t) { return 'hsl(' + (210 - 175 * t) + ',90%,' + (62 - 6 * t) + '%)'; }
  function fotograma() {
    if (!activo) return;
    var lote = Math.max(1, Math.ceil(n / 160) * paso);
    for (var k = 0; k < lote && i < n; k++, i++) {
      L.circleMarker(pts[i], {renderer: lienzo, radius: 3.2, stroke: false,
        fillColor: color(i / n), fillOpacity: 0.85}).addTo(capa);
    }
    el('ex-n').textContent = Math.round(total * i / n).toLocaleString('es');
    el('ex-b').style.width = (100 * i / n) + '%';
    if (i < n) { requestAnimationFrame(fotograma); return; }
    activo = false; el('ex-play').textContent = 'Reproducir';
    viva = L.polyline(ruta, {color: '#5ac8fa', weight: 5, className: 'ruta-viva'}).addTo(map);
  }
  function reiniciar() {
    capa.clearLayers(); if (viva) { map.removeLayer(viva); viva = null; }
    i = 0; activo = true; el('ex-play').textContent = 'Pausar'; requestAnimationFrame(fotograma);
  }
  el('ex-play').onclick = function () {
    if (i >= n) { reiniciar(); return; }
    activo = !activo; this.textContent = activo ? 'Pausar' : 'Reproducir';
    if (activo) requestAnimationFrame(fotograma);
  };
  el('ex-re').onclick = reiniciar;
  document.querySelectorAll('.expl-panel [data-v]').forEach(function (b) {
    b.onclick = function () {
      paso = +b.dataset.v;
      document.querySelectorAll('.expl-panel [data-v]').forEach(function (x) {
        x.classList.toggle('on', x === b);
      });
    };
  });
  reiniciar();
});
"""


def mapa_exploracion(
    puntos: list[tuple[float, float]],
    polilinea: list[tuple[float, float]],
    origen: dict,
    destino: dict,
    total: int | None = None,
) -> folium.Map:
    """Mapa que reproduce la expansión de Dijkstra y al final dibuja la ruta óptima."""
    m = mapa_base(polilinea[0], 11)
    _extremos(m, origen, destino)
    js = (
        _JS_EXPLORACION.replace("__MAPA__", m.get_name())
        .replace("__PUNTOS__", json.dumps(puntos))
        .replace("__RUTA__", json.dumps(polilinea))
        .replace("__TOTAL__", str(int(total or len(puntos))))
    )
    m.get_root().script.add_child(folium.Element(js))
    return m


def mapa_envolvente(
    vertices: list[tuple[float, float]],
    lugares: list[dict],
    mostrar_poligono: bool = True,
    mostrar_vertices: bool = False,
) -> folium.Map:
    """Envolvente convexa con un pin por lugar, coloreado por categoría."""
    m = mapa_base(*encuadre(vertices))
    if mostrar_poligono:
        folium.Polygon(
            vertices,
            color=CAFE,
            weight=2.5,
            fill=True,
            fill_color=CAFE,
            fill_opacity=0.14,
            class_name="hull-viva",
        ).add_to(m)
    if mostrar_vertices:
        for k, (lat, lon) in enumerate(vertices, start=1):
            folium.Marker(
                (lat, lon),
                icon=_punto(),
                tooltip=_tooltip(f"Vértice {k}", f"{lat:.4f}, {lon:.4f}"),
            ).add_to(m)
    for x in lugares:
        _, color, icono = estilo_categoria(x["categoria"])
        folium.Marker(
            (x["lat"], x["lon"]),
            icon=_pin(color, icono),
            tooltip=_tooltip(x["nombre"], f"{x['municipio']} · {x['categoria']}"),
        ).add_to(m)
    return m


def _punto() -> folium.DivIcon:
    return folium.DivIcon(
        html=f'<div class="pin punto" style="--c:{CAFE}"></div>',
        icon_size=(14, 14),
        icon_anchor=(7, 7),
    )


def _pin_numero(numero: int | None, color: str, icono: str = "casa") -> folium.DivIcon:
    """Pin con el número de parada, o con un icono para la partida."""
    contenido = str(numero) if numero is not None else svg(icono, 20)
    return folium.DivIcon(
        html=f'<div class="pin grande" style="--c:{color};font-weight:700">{contenido}</div>',
        icon_size=(42, 42),
        icon_anchor=(21, 21),
    )


def mapa_itinerario(
    tramos: list[list[tuple[float, float]]], paradas: list[dict], minutos: list[float]
) -> folium.Map:
    """Recorrido en orden: tramos por carretera coloreados y paradas numeradas.

    `paradas` va en orden de visita (la primera es la partida); `tramos` y `minutos`
    traen un elemento por cada par consecutivo, incluido el regreso."""
    todos = [pt for tramo in tramos for pt in tramo]
    m = mapa_base(*encuadre(todos))
    n = len(tramos)
    for k, (tramo, mins) in enumerate(zip(tramos, minutos, strict=True), start=1):
        color = f"hsl({140 - 100 * (k - 1) / max(n - 1, 1):.0f},85%,58%)"
        folium.PolyLine(tramo, color=color, weight=13, opacity=0.16).add_to(m)
        folium.PolyLine(
            tramo,
            color=color,
            weight=5,
            opacity=0.95,
            class_name="ruta-viva",
            tooltip=_tooltip(f"Tramo {k}", f"{mins:.0f} min en carro"),
        ).add_to(m)
    for k, x in enumerate(paradas):
        inicio = k == 0
        folium.Marker(
            (x["lat"], x["lon"]),
            icon=_pin_numero(None if inicio else k, "#30d158" if inicio else NARANJA),
            tooltip=_tooltip(x["nombre"], "Partida y regreso" if inicio else f"Parada {k}"),
            z_index_offset=1000 - k,
        ).add_to(m)
    return m


def encuadre(
    puntos: list[tuple[float, float]], ancho_px: int = 900, alto_px: int = 520
) -> tuple[tuple[float, float], int]:
    """Centro y zoom de Leaflet que encierran los puntos (con margen).

    Se calcula aquí porque st_folium impone su propia vista e ignora fit_bounds."""
    lats = [p[0] for p in puntos]
    lons = [p[1] for p in puntos]
    centro = ((min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2)
    span_lat = max(max(lats) - min(lats), 1e-6) * 1.3
    span_lon = max(max(lons) - min(lons), 1e-6) * 1.3
    if len(puntos) < 2 or (max(lats) == min(lats) and max(lons) == min(lons)):
        return centro, 14
    escala_lat = 1 / max(math.cos(math.radians(centro[0])), 0.1)
    z_lon = math.log2(ancho_px / 256 * 360 / span_lon)
    z_lat = math.log2(alto_px / 256 * 180 / (span_lat * escala_lat))
    return centro, max(3, min(15, int(min(z_lon, z_lat))))

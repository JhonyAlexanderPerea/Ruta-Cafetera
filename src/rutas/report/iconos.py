"""Iconos SVG en línea (trazo, 24×24) y estilo por categoría de lugar. Solo presentación."""

from __future__ import annotations

_RUTAS = {
    "reloj": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "ruta": (
        '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 '
        '0-7H15"/><circle cx="18" cy="5" r="3"/>'
    ),
    "velocidad": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
    "bandera": (
        '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>'
        '<line x1="4" x2="4" y1="22" y2="15"/>'
    ),
    "intercambio": (
        '<path d="m16 3 4 4-4 4"/><path d="M20 7H4"/><path d="m8 21-4-4 4-4"/><path d="M4 17h16"/>'
    ),
    "nodos": (
        '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" '
        'rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 '
        '1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/>'
    ),
    "brujula": (
        '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 '
        '9.88 9.88 16.24 7.76"/>'
    ),
    "area": (
        '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 '
        '1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>'
    ),
    "regla": (
        '<path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.41 2.41 '
        '0 0 1 0-3.4l2.6-2.6a2.41 2.41 0 0 1 3.4 0Z"/><path d="m14.5 12.5 2-2"/>'
        '<path d="m11.5 9.5 2-2"/><path d="m8.5 6.5 2-2"/><path d="m17.5 15.5 2-2"/>'
    ),
    "play": '<polygon points="6 3 20 12 6 21 6 3"/>',
    "rayo": (
        '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 '
        '10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>'
    ),
    "pin": '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "casa": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    "estrella": (
        '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 '
        '14.14 2 9.27 8.91 8.26 12 2"/>'
    ),
    "hoja": (
        '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 '
        '10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>'
    ),
    "bodega": (
        '<path d="M22 8.35V20a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8.35A2 2 0 0 1 3.26 6.5l8-3.2a2 2 0 '
        '0 1 1.48 0l8 3.2A2 2 0 0 1 22 8.35Z"/><path d="M6 18h12"/><path d="M6 14h12"/>'
    ),
    "taza": (
        '<path d="M10 2v2"/><path d="M14 2v2"/><path d="M16 8a1 1 0 0 1 1 1v8a4 4 0 0 1-4 4H7a4 '
        '4 0 0 1-4-4V9a1 1 0 0 1 1-1h14a4 4 0 1 1 0 8h-1"/><path d="M6 2v2"/>'
    ),
    "balanza": (
        '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87'
        '.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/>'
        '<path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>'
    ),
}

# categoría -> (etiqueta plural, color, icono)
CATEGORIAS = {
    "cabecera": ("Cabeceras", "#0a84ff", "casa"),
    "atractivo": ("Atractivos", "#ff9f0a", "estrella"),
    "finca": ("Fincas", "#30d158", "hoja"),
    "acopio": ("Acopio", "#c8a27a", "bodega"),
}


def svg(nombre: str, tam: int = 20) -> str:
    """Icono como `<svg>` heredando el color del texto (currentColor)."""
    cuerpo = _RUTAS[nombre]
    return (
        f'<svg class="ico" width="{tam}" height="{tam}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{cuerpo}</svg>'
    )


def estilo_categoria(categoria: str) -> tuple[str, str, str]:
    """(etiqueta, color, icono) con un valor por defecto para categorías desconocidas."""
    return CATEGORIAS.get(categoria, (categoria.capitalize(), "#a1a1a6", "pin"))

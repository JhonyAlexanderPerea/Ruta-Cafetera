"""Envolvente convexa por divide y vencerás con fusión por tangentes (R3).

Algoritmo: se ordenan los puntos por (x, y) y se parten en dos mitades. Cada mitad produce su
envolvente (lista en sentido antihorario). La fusión busca las dos tangentes comunes (superior e
inferior) entre ambas envolventes y arma la envolvente del conjunto completo.

Recurrencia: T(n) = 2 T(n/2) + O(n), así que T(n) = O(n log n) en el peor caso.
Profundidad de la recursión: log2 n. Coordenadas enteras: aritmética exacta con int de Python.

Salida: vértices en sentido antihorario, sin colineales ni duplicados. Si todos los puntos son
colineales, devuelve los dos extremos.
"""

from __future__ import annotations

Punto = tuple[int, int]


def _cruz(o: Punto, a: Punto, b: Punto) -> int:
    """> 0 si b queda a la izquierda de o->a; < 0 si queda a la derecha; 0 si colineales."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _envolvente_monotona(pts: list[Punto]) -> list[Punto]:
    """Cadena monótona de Andrew: caso base y respaldo para casos degenerados."""
    pts = sorted(set(pts))
    if len(pts) <= 2:
        return pts

    def construir(seq):
        chain: list[Punto] = []
        for p in seq:
            while len(chain) >= 2 and _cruz(chain[-2], chain[-1], p) <= 0:
                chain.pop()
            chain.append(p)
        return chain

    inferior = construir(pts)
    superior = construir(reversed(pts))
    casco = inferior[:-1] + superior[:-1]
    return casco if len(casco) >= 2 else [pts[0], pts[-1]]


def _tangentes(A: list[Punto], B: list[Punto]) -> tuple[int, int, int, int]:
    """Índices (ia_inf, jb_inf, ia_sup, jb_sup) de las tangentes inferior y superior.

    A y B son envolventes CCW, con A a la izquierda de B.
    """
    na, nb = len(A), len(B)
    ia = max(range(na), key=lambda k: A[k])  # extremo derecho de A
    jb = min(range(nb), key=lambda k: B[k])  # extremo izquierdo de B

    # Tangente inferior: todos los puntos quedan a la izquierda de A[ia] -> B[jb].
    cambio = True
    limite = 4 * (na + nb) + 10
    while cambio and limite > 0:
        cambio = False
        limite -= 1
        while _cruz(A[ia], B[jb], A[(ia - 1) % na]) < 0:
            ia = (ia - 1) % na
            cambio = True
        while _cruz(A[ia], B[jb], B[(jb + 1) % nb]) < 0:
            jb = (jb + 1) % nb
            cambio = True
    ia_inf, jb_inf = ia, jb

    # Tangente superior: todos los puntos quedan a la derecha de A[ia] -> B[jb].
    ia = max(range(na), key=lambda k: A[k])
    jb = min(range(nb), key=lambda k: B[k])
    cambio = True
    limite = 4 * (na + nb) + 10
    while cambio and limite > 0:
        cambio = False
        limite -= 1
        while _cruz(A[ia], B[jb], A[(ia + 1) % na]) > 0:
            ia = (ia + 1) % na
            cambio = True
        while _cruz(A[ia], B[jb], B[(jb - 1) % nb]) > 0:
            jb = (jb - 1) % nb
            cambio = True
    ia_sup, jb_sup = ia, jb

    return ia_inf, jb_inf, ia_sup, jb_sup


def _fusionar(A: list[Punto], B: list[Punto]) -> list[Punto]:
    if len(A) <= 2 or len(B) <= 2:
        return _envolvente_monotona(A + B)
    ia_inf, jb_inf, ia_sup, jb_sup = _tangentes(A, B)
    na, nb = len(A), len(B)

    # A desde la tangente superior hasta la inferior (lado izquierdo), y B desde la inferior
    # hasta la superior (lado derecho), ambos en sentido antihorario.
    izquierda = []
    k = ia_sup
    while True:
        izquierda.append(A[k])
        if k == ia_inf:
            break
        k = (k + 1) % na
    derecha = []
    k = jb_inf
    while True:
        derecha.append(B[k])
        if k == jb_sup:
            break
        k = (k + 1) % nb
    casco = izquierda + derecha
    return _envolvente_monotona(casco) if len(casco) < 3 else _limpiar(casco)


def _limpiar(casco: list[Punto]) -> list[Punto]:
    """Quita colineales y duplicados de un ciclo CCW que ya es convexo salvo por ellos."""
    salida: list[Punto] = []
    for p in casco:
        if salida and salida[-1] == p:
            continue
        while len(salida) >= 2 and _cruz(salida[-2], salida[-1], p) <= 0:
            salida.pop()
        salida.append(p)
    # cierre: el último y el primero pueden requerir revisión
    while len(salida) >= 3 and _cruz(salida[-2], salida[-1], salida[0]) <= 0:
        salida.pop()
    while len(salida) >= 3 and _cruz(salida[-1], salida[0], salida[1]) <= 0:
        salida.pop(0)
    return salida


def _dc(pts: list[Punto]) -> list[Punto]:
    if len(pts) <= 3:
        return _envolvente_monotona(pts)
    medio = len(pts) // 2
    return _fusionar(_dc(pts[:medio]), _dc(pts[medio:]))


def convex_hull(points: list[Punto]) -> list[Punto]:
    """Envolvente convexa de puntos con coordenadas enteras, CCW, sin colineales."""
    pts = sorted(set((int(x), int(y)) for x, y in points))
    if not pts:
        return []
    if len(pts) == 1:
        return pts
    return _dc(pts)

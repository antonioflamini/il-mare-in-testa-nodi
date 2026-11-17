"""Geometria dei nodi: percorsi disegnati a mano (capo dormiente -> capo corrente).

Convenzioni: unita' = diametro della cima. x a destra, y in alto, z verso
chi guarda (O = il tratto passa sopra, U = passa sotto). Il primo punto e' il
dormiente, l'ultimo il capo corrente (quello che "lavora").
"""
import numpy as np
from geom import flat, rope3d, arc, helix

KNOTS = {}


def knot(fn):
    KNOTS[fn.__name__.replace('_', '-')] = fn
    return fn


# ------------------------------------------------------------ ARRESTO
@knot
def nodo_semplice():
    t = np.linspace(np.pi + 0.45, 3 * np.pi - 0.45, 16)
    s = 1.7
    core = [(s * (np.sin(a) + 2 * np.sin(2 * a)), s * (np.cos(a) - 2 * np.cos(2 * a))) for a in t]
    pts = [(9, -9.5), (5, -7.5)] + core + [(-5, -7.5), (-9, -9.5)]
    pts = [(-y, x) for x, y in pts]   # ruota: capi orizzontali
    R = flat([pts], 'OUOUOU')
    return dict(ropes=R, pulls=[dict(rope=0, at=0, dir=[1, 0, 0]), dict(rope=0, at=1, dir=[-1, 0, 0])])


@knot
def savoia():
    pts = [(0, 15), (0, 9), (0, 5), (0, 1.5), (1.6, -0.9), (3.4, 0.6), (3.4, 3.4),
           (1.6, 5.4), (-1.5, 6.8), (-3.0, 8.2), (-1.6, 9.8), (1.2, 10.0), (3.2, 8.6),
           (2.7, 6.0), (2.0, 3.4), (1.7, 0.6), (1.5, -2.5), (1.2, -7)]
    R = flat([pts], 'OUOUOUOU')
    return dict(ropes=R, pulls=[dict(rope=0, at=0, dir=[0, 1, 0]), dict(rope=0, at=1, dir=[0, -1, 0])])


# ------------------------------------------------------------- GASSE
@knot
def gassa_damante():
    """Tana in alto (incrocio X1 con il ramo verso la gassa sopra), coniglio
    che sale dalla tana, gira dietro l'albero e rientra. Gassa attorno a una bitta."""
    th = lambda a: (2.4 * np.cos(np.radians(a)), 6 + 2.4 * np.sin(np.radians(a)))
    pts = [(0.8, 19), (0.8, 13), (0.8, 11), (0.35, 9.2)]
    pts += [th(a) for a in (120, 150, 180, 210, 240, 270, 300, 330, 0, 30, 60)]
    pts += [(-1.6, 9.3), (-3.4, 8.6), (-4.6, 5.5), (-4.6, 1), (-3.2, -3), (0, -4.6), (3.2, -3), (4.4, 0.5),
            (3.4, 2.4), (1.6, 2.6), (0.9, 3.3), (0.85, 5.5), (0.9, 7.5), (1.0, 9.9),
            (2.2, 11.0), (1.6, 12.3), (0, 12.6), (-1.4, 11.8), (-1.6, 10.4), (-1.0, 9.4),
            (-0.9, 7.0), (-0.9, 5.0), (-0.9, 3.0), (-0.75, 1.2)]
    R = flat([pts], 'OUUOOUOUUOUOOU')
    post = dict(type='cyl', c=[0, -1.4, 2.6], axis=[0, 0, 1], r=2.0, h=7.4, mat='wood', cap=True)
    return dict(ropes=R, props=[post],
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0]), dict(rope=0, at=1, dir=[0, -1, 0], w=0.3)],
                view=dict(elev=55, zoom=1.15), jam=0.25, snug=0.9)


# --------------------------------------------------------- GIUNZIONE
@knot
def piano():
    white = [(-1.0, -13), (-1.2, -6), (-1.6, -3), (-2.5, 1.0), (-2.6, 2.6), (-2.0, 4.3), (0, 5.1),
             (2.0, 4.3), (2.6, 2.6), (2.5, 1.0), (1.6, -3), (1.2, -6), (1.0, -10)]
    red = [(-0.8, 13), (-0.8, 8), (-0.8, 4.4), (-1.3, 1.2), (-2.5, -1.4), (-2.6, -2.8), (-2.0, -4.4),
           (0, -5.2), (2.0, -4.4), (2.6, -2.8), (2.5, -1.4), (1.3, 1.2), (0.8, 4.4), (0.8, 10)]
    R = flat([white, red], 'OUOOUO' + 'UOUUOU')
    return dict(ropes=R, colors=['main', 'second'],
                reveal=[[0, 0.35, 0.0], [0.35, 1.0, 0.0]],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[0, -1, 0], w=0.6),
                       dict(rope=1, at=0, dir=[0, 1, 0]), dict(rope=1, at=1, dir=[0, 1, 0], w=0.6)],
                view=dict(elev=60, zoom=1.2))


@knot
def scotta():
    """Cima grossa (bianca) piegata a doppino; la sottile (arancio) sale nel
    doppino, gira dietro i due rami e passa sotto se stessa ma sopra il doppino."""
    white = [(-1.45, 14), (-1.45, 8), (-1.45, 3), (-1.3, 0.2), (-0.8, -1.3), (0, -1.75), (0.8, -1.3),
             (1.3, 0.2), (1.45, 3), (1.45, 8), (1.45, 11)]
    red = [(0.3, -13), (0.3, -6), (0.25, -2.6), (0.3, -0.6), (0.6, 1.0), (1.1, 2.6), (1.9, 3.7),
           (2.7, 4.6), (2.0, 5.3), (0, 5.4), (-2.0, 5.3), (-2.9, 4.4), (-2.7, 3.1), (-1.6, 2.2),
           (-0.2, 1.75), (1.0, 1.7), (2.4, 1.55), (4.6, 1.4)]
    R = flat([white, red], 'OUOUUO' + 'UOOUUOUO')
    return dict(ropes=R, colors=['main', 'second'], radii=[0.62, 0.42],
                reveal=[[0, 0.3, 0.0], [0.3, 1.0, 0.0]],
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0]), dict(rope=0, at=1, dir=[0, 1, 0], w=0.4),
                       dict(rope=1, at=0, dir=[0, -1, 0]), dict(rope=1, at=1, dir=[1, 0, 0], w=0.3)],
                view=dict(elev=60, zoom=1.3), snug=0.6)


# -------------------------------------------------------- ANCORAGGIO
def _clove_pts(rail_r=1.0, x0=-0.6, x1=1.35, x2=-1.35, x3=0.6, top=9, bottom=-12):
    """Parlato su un tientibene orizzontale (asse x): dormiente in basso,
    capo corrente che esce in alto sotto il "cavaliere" diagonale."""
    Rw = rail_r + 0.5
    pts = [(x0, bottom, Rw), (x0, bottom / 2, Rw), (x0, -1.2, Rw)]
    # primo giro: davanti -> sopra -> dietro -> sotto (x da x0 a x1)
    for th in np.linspace(0, 300, 11):
        x = x0 + (x1 - x0) * th / 300
        pts.append((x, Rw * np.sin(np.radians(th)), Rw * np.cos(np.radians(th))))
    # cavaliere diagonale davanti, piu' esterno (passa sopra dormiente e corrente)
    for th in np.linspace(300, 420, 9)[1:]:
        x = x1 + (x2 - x1) * (th - 300) / 120
        r = Rw + 1.05 * np.sin(np.pi * (th - 300) / 120)
        pts.append((x, r * np.sin(np.radians(th)), r * np.cos(np.radians(th))))
    # secondo giro: sopra -> dietro -> sotto -> davanti (x da x2 a x3)
    for th in np.linspace(420, 720, 11)[1:]:
        x = x2 + (x3 - x2) * (th - 420) / 300
        pts.append((x, Rw * np.sin(np.radians(th)), Rw * np.cos(np.radians(th))))
    pts += [(x3, 1.4, Rw), (x3, 4, Rw), (x3, top, Rw)]
    return pts


@knot
def parlato():
    pts = _clove_pts()
    R = [rope3d(pts)]
    rail = dict(type='cyl', c=[0, 0, 0], axis=[1, 0, 0], r=1.0, h=14, mat='steel')
    return dict(ropes=R, props=[rail],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[0, 1, 0], w=0.5)],
                view=dict(mode='stand', elev=12, az=-18, zoom=1.5), jam=0.25, snug=0.8)

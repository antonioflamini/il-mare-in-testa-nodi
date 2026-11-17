"""Nodario completo, parte 6."""
import numpy as np
from geom import flatm, rope3d, rturn, vturn, line
from knots_src import knot, _clove_pts

RAIL = dict(type='cyl', c=[0, 0, 0], axis=[1, 0, 0], r=1.0, h=14, mat='steel')


def _sv(**kw):
    v = dict(mode='stand', elev=12, az=-18, zoom=1.5)
    v.update(kw)
    return v


@knot
def per_sacchi():
    """Nodo per sacchi (ground-line): come il parlato, ma il capo esce sotto
    il cavaliere e anche sotto il dormiente."""
    pts = _clove_pts(x3=0.55)[:-3]
    Rw = 1.5
    pts += [(0.45, 0.9, Rw - 0.05), (-0.1, 1.6, Rw - 0.1), (-0.9, 2.1, Rw - 0.15), (-1.9, 2.4, Rw + 0.2),
            (-3.0, 2.6, Rw + 0.5), (-4.5, 2.0, Rw + 0.6)]
    return dict(ropes=[rope3d(pts)], props=[RAIL],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[-1, 0, 0], w=0.3, max=0.5)],
                view=_sv(), jam=0.25, snug=0.7)


@knot
def sagole_da_lancio():
    """Nodo per sagole da lancio: un doppino in fondo alla cima, fasciato da
    molti giri, e il capo infilato nell'asola in cima."""
    pts = [(-0.5, -15), (-0.5, -6), (-0.5, 1.0), (-0.5, 5.6), (0, 6.5), (0.5, 5.6), (0.5, 2.0), (0.5, -0.6),
           (0.8, -1.3), (1.5, -1.05)]
    marks = []
    y = -1.05
    n = 9
    for k in range(n):
        yl, yr = y + 0.27, y + 0.54                     # davanti: da destra a sinistra
        pts += [(-1.5, yl)]
        for xl in (0.5, -0.5):
            t = (1.5 - xl) / 3.0
            marks.append((xl, y + t * (yl - y), 'O'))
        pts += [(1.5, yr)]                              # dietro: da sinistra a destra
        for xl in (-0.5, 0.5):
            t = (xl + 1.5) / 3.0
            marks.append((xl, yl + t * (yr - yl), 'U'))
        y = yr
    pts += [(1.4, y + 0.4), (0.0, y + 0.9), (-0.9, y + 1.1), (-2.0, y + 1.8), (-3.4, y + 3.2)]
    marks = [(0.5, y + 0.6, 'O'), (-0.5, y + 1.02, 'U')]
    # i giri: il tratto che va verso sinistra passa davanti ai due rami, quello di ritorno dietro
    R = flatm([pts], marks, tol=0.35, rule=lambda x, yy, t: 'O' if t[0] < 0 else 'U')
    return dict(ropes=R, pulls=[dict(rope=0, at=0, dir=[0, -1, 0], max=1.5), dict(rope=0, at=1, dir=[-0.7, 1, 0], w=0.3, max=0.4)],
                view=dict(elev=65, zoom=0.9), jam=0.25, snug=0.6)


@knot
def stopper_ashley():
    """Arresto di Ashley: un'asola, un doppino del capo infilato dentro (come un
    nodo scorsoio) e il capo passato nel doppino."""
    cx, cy, rx, ry = 0.3, 1.45, 1.75, 1.45
    pts = [(-12, 0), (-6, 0), (-2.6, 0), (0.9, 0)]
    for a in np.linspace(-60, 200, 11):
        t = np.radians(a)
        pts.append((cx + rx * np.cos(t), cy + ry * np.sin(t)))
    pts += [(-1.75, 0.3), (-1.5, -0.8), (-1.0, -1.6),
            (-0.5, -1.5), (-0.35, 0), (-0.2, 1.6), (-0.1, 3.4), (0.25, 4.6), (0.6, 3.4), (0.7, 1.6), (0.75, 0),
            (0.85, -1.4), (2.0, -1.8), (3.2, -0.6), (3.4, 1.6), (2.9, 3.6), (1.8, 4.0), (0.4, 4.05),
            (-1.2, 4.2), (-3.0, 5.5)]
    ytop = lambda x: cy + ry * np.sqrt(max(0, 1 - ((x - cx) / rx) ** 2))
    marks = [(-1.7, 0, 'O'), (-0.35, 0, 'U'), (-0.12, ytop(-0.12), 'O'), (0.66, ytop(0.66), 'O'),
             (0.75, 0, 'U'), (0.6, 4.02, 'U'), (-0.05, 4.07, 'O')]
    R = flatm([pts], marks, tol=0.5)
    return dict(ropes=R, pulls=[dict(rope=0, at=0, dir=[-1, 0, 0]), dict(rope=0, at=1, dir=[-0.6, 1, 0], w=0.4)],
                view=dict(elev=65, zoom=1.5), snug=0.45)


@knot
def caviglia():
    """Volta di caviglia (marlinspike): un'asola della cima abbraccia la caviglia
    di legno, che passa sopra i lati dell'asola e sotto il tratto centrale."""
    rope = [(0, 12), (0, 6), (0.1, 2.6), (0.8, 1.9), (1.7, 0.7), (1.6, -1.0), (0.6, -1.9), (-0.8, -1.8),
            (-1.65, -0.8), (-1.6, 0.8), (-0.9, 1.7), (-0.05, 1.95), (0.15, 0.5), (0.1, -1.2), (0, -4), (0, -12)]
    spike = line(-5.5, 0.0, 5.5, 0.0, 8)
    marks = [(0.05, 1.98, 'U'), (0.1, -1.88, 'O'),            # il tratto centrale passa nell'asola
             (1.68, 0.0, 'U'), (-1.63, 0.0, 'U'), (0.13, 0.0, 'O')]   # caviglia sopra i lati, sotto il centro
    R = flatm([rope, spike], marks, solid={1}, tol=0.6)
    return dict(ropes=R, solid={1: 'wood'}, radii=[0.5, 0.55],
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0], max=1.0), dict(rope=0, at=1, dir=[0, -1, 0], max=1.0)],
                view=dict(elev=65, zoom=1.6), jam=0.25, snug=0.8)


@knot
def chiatta():
    """Nodo chiatta (lighterman's): volta tonda sulla bitta, poi un doppino del
    capo passa sotto il dormiente e si cala sulla testa della bitta."""
    post = dict(type='cyl', c=[0, 3.0, 0], axis=[0, 1, 0], r=1.2, h=6.0, mat='wood', cap=True)
    Rw = 1.7
    pts = [(-0.6, 1.3, 15), (-0.6, 1.3, 7), (-0.6, 1.3, 3.0)]
    pts += vturn(-20, -400, 1.3, 2.3, Rw)                      # volta tonda
    pts += [(-1.4, 2.2, 2.4), (-1.0, 0.5, 3.6), (-0.3, 0.45, 4.4), (0.3, 1.4, 4.0)]   # passa sotto il dormiente
    pts += [(0.6, 3.0, 2.6)]
    pts += vturn(20, -340, 3.5, 3.7, Rw, bumps=[(0, 30, 0.9), (-360, 30, 0.9)])       # doppino calato sulla bitta
    pts += [(1.0, 3.0, 2.4), (1.2, 1.9, 4.0), (1.3, 1.6, 9.0)]
    return dict(ropes=[rope3d(pts)], props=[post, dict(type='plane', y=0, hidden=True)],
                pulls=[dict(rope=0, at=0, dir=[0, 0, 1]), dict(rope=0, at=1, dir=[0, 0, 1], w=0.4, max=0.6)],
                view=_sv(elev=35, az=30, zoom=1.4, ground=0), jam=0.25, snug=0.6)


@knot
def bocca_di_lupo_migliorata():
    """Bocca di lupo migliorata: dopo la bocca di lupo il capo passa sotto il dormiente."""
    rail = dict(type='cyl', c=[0, 0, 0], axis=[1, 0, 0], r=0.6, h=14, mat='steel')
    Rw = 1.1
    pts = [(-0.55, -13, Rw), (-0.55, -6, Rw), (-0.55, -1.4, Rw)]
    for th in np.linspace(0, 360, 13)[1:]:
        x = -0.55 - 0.85 * th / 360
        r = Rw + 1.0 * np.exp(-((th - 360) / 30) ** 2)
        pts.append((x, r * np.sin(np.radians(th)), r * np.cos(np.radians(th))))
    pts += [(-0.5, 0.05, Rw + 1.0), (0.5, 0.05, Rw + 1.0)]
    for th in np.linspace(360, 720, 13):
        x = 1.4 - 0.85 * (th - 360) / 360
        r = Rw + 1.0 * np.exp(-((th - 360) / 30) ** 2)
        pts.append((x, r * np.sin(np.radians(-th)), r * np.cos(np.radians(-th))))
    pts += [(0.55, -1.4, Rw), (0.5, -2.4, Rw + 0.3), (-0.2, -3.0, Rw + 0.1), (-0.55, -3.2, Rw - 0.9),
            (-1.2, -3.4, Rw - 0.3), (-1.5, -4.4, Rw + 0.2), (-1.4, -7.0, Rw + 0.3)]
    return dict(ropes=[rope3d(pts)], props=[rail],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[0, -1, 0], w=0.4)],
                view=_sv(elev=12, az=-20, zoom=1.5), jam=0.25, snug=0.7)

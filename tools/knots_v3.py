"""Nodario completo, parte 3: famiglie di nodi costruite con generatori.

- multipli del nodo semplice: un'asola attraversata dal capo k volte (elica);
- varianti della gassa d'amante (stessa tana, collare diverso);
- famiglia del nodo di scotta (giri multipli, a otto, a tre vie, becket).
Gli incroci si annotano nel punto in cui avvengono (geom.flatm)."""
import numpy as np
from geom import flatm
from knots_src import knot


# ------------------------------------------------- nodi semplici multipli
def _multi_overhand(k, pitch=1.12, R=1.45):
    """Dormiente da sinistra, asola antioraria; il capo passa k volte
    nell'asola da dietro in avanti (sotto il dormiente, sopra l'arco alto)."""
    cx, cy = 0.0, R
    pts = [(-12, 0), (-6, 0), (-2.6, 0), (0.6 + pitch * (k - 1), 0)]
    # asola: sale a destra, passa in alto da destra a sinistra, scende a sinistra
    x_right = 0.9 + pitch * (k - 1)
    for a in np.linspace(-60, 200, 11):
        t = np.radians(a)
        rx = R + pitch * (k - 1) / 2
        pts.append((cx + pitch * (k - 1) / 2 + rx * np.cos(t), cy + R * np.sin(t)))
    marks = []
    # chiusura dell'asola: il tratto che scende passa sopra il dormiente
    pts += [(-1.75, 0.3), (-1.5, -0.8), (-1.0, -1.6)]
    marks.append((-1.7, 0.0, 'O'))
    for i in range(k):
        x0 = -0.35 + i * pitch
        pts += [(x0 - 0.15, -1.5), (x0, 0.0), (x0 + 0.15, 2.2)]
        marks.append((x0, 0.0, 'U'))                       # sotto il dormiente
        top_y = cy + R * np.sin(np.arccos(np.clip((x0 + 0.3 - cx - pitch * (k - 1) / 2) / (R + pitch * (k - 1) / 2), -1, 1)))
        marks.append((x0 + 0.3, top_y, 'O'))               # sopra l'arco alto
        if i < k - 1:                                        # gira fuori dall'asola e torna sotto
            xo = x_right + R + 1.2
            pts += [(x0 + 0.45, top_y + 1.3), (xo - 0.6, top_y + 0.4), (xo, cy), (xo - 0.4, -1.4),
                    (x0 + pitch + 0.1, -2.3)]
        else:
            pts += [(x0 + 0.5, top_y + 1.6), (x0 + 1.8, top_y + 3.6), (x0 + 3.5, top_y + 5.6)]
    return pts, marks


def _mo_knot(k, view=None):
    pts, marks = _multi_overhand(k)
    R = flatm([pts], marks, default='O')   # il capo finale passa sopra i giri esterni
    return dict(ropes=R, pulls=[dict(rope=0, at=0, dir=[-1, 0, 0]), dict(rope=0, at=1, dir=[0.4, 1, 0])],
                view=view or dict(zoom=1.6), snug=0.3)


@knot
def semplice_doppio():
    return _mo_knot(2)


@knot
def semplice_multiplo():
    return _mo_knot(4, dict(zoom=1.1))


@knot
def uli():
    return _mo_knot(5, dict(zoom=1.0))


# ---------------------------------------------------- famiglia della gassa
TH = lambda a: (2.4 * np.cos(np.radians(a)), 6 + 2.4 * np.sin(np.radians(a)))
BOW_HEAD = [(0.8, 19), (0.8, 13), (0.8, 11), (0.35, 9.2)] + [TH(a) for a in (120, 150, 180, 210, 240, 270, 300, 330, 0, 30, 60)]
BOW_EYE = [(-1.6, 9.3), (-3.4, 8.6), (-4.6, 5.5), (-4.6, 1), (-3.2, -3), (0, -4.6), (3.2, -3), (4.4, 0.5)]
BOW_WORK = [(3.4, 2.4), (1.6, 2.6), (0.9, 3.3), (0.85, 5.5), (0.9, 7.5), (1.0, 9.9),
            (2.2, 11.0), (1.6, 12.3), (0, 12.6), (-1.4, 11.8), (-1.6, 10.4), (-1.0, 9.4),
            (-0.9, 7.0), (-0.9, 5.0), (-0.9, 3.0), (-0.75, 1.2)]
BOW_MARKS = [(-0.15, 8.85, 'O'),                    # tana: il ramo verso la gassa passa sopra
             (0.88, 3.8, 'U'), (0.85, 8.3, 'O'),    # il coniglio sale da sotto ed esce sopra
             (0.75, 12.55, 'U'),                    # gira dietro l'albero
             (-1.0, 9.1, 'O'), (-0.92, 8.25, 'O'), (-0.9, 3.75, 'U')]   # rientra nella tana
POST = dict(type='cyl', c=[0, -1.4, 2.6], axis=[0, 0, 1], r=2.0, h=7.4, mat='wood', cap=True)


def _bow(pts, marks, extra_props=(), pulls=None, **kw):
    R = flatm([pts], marks)
    d = dict(ropes=R, props=[POST, *extra_props],
             pulls=pulls or [dict(rope=0, at=0, dir=[0, 1, 0]), dict(rope=0, at=1, dir=[0, -1, 0], w=0.3)],
             view=dict(elev=70, zoom=1.15), jam=0.25, snug=0.85)
    d.update(kw)
    return d


@knot
def gassa_rapido():
    return _bow(BOW_HEAD + BOW_EYE + BOW_WORK, BOW_MARKS)


@knot
def gassa_olanda():
    """Gassa del cowboy: il capo gira attorno al dormiente nel verso opposto
    e finisce fuori dall'occhio."""
    work = [(3.0, 1.4), (0.5, 1.9), (-0.8, 2.8), (-0.9, 4.4), (-0.9, 6.6), (-1.0, 8.7), (-1.1, 9.8),
            (-1.6, 10.9), (-0.7, 12.4), (0.6, 12.7), (2.0, 12.1), (2.3, 10.8), (1.5, 9.8),
            (0.95, 8.6), (0.9, 6.2), (0.9, 4.4), (0.85, 2.6), (0.8, 1.2)]
    marks = [(-0.15, 8.85, 'O'), (-0.9, 3.75, 'U'), (-0.95, 8.25, 'O'), (-1.05, 9.1, 'O'),
             (0.8, 12.6, 'U'), (0.9, 8.2, 'O'), (0.9, 3.84, 'U'), (0.71, 1.83, 'U')]
    return _bow(BOW_HEAD + BOW_EYE + work, marks)


@knot
def gassa_ganciata():
    """Gassa ganciata: l'ultimo passaggio si fa con un doppino, che si scioglie tirando il capo."""
    work = BOW_WORK[:-1] + [(-0.85, 2.4), (-1.3, 1.6), (-1.85, 2.4), (-1.92, 4.0), (-2.0, 6.0),
                            (-2.0, 7.8), (-2.05, 9.6), (-2.1, 10.8)]
    marks = BOW_MARKS + [(-1.9, 4.5, 'U'), (-1.95, 7.5, 'O'), (-2.0, 9.15, 'O')]
    return _bow(BOW_HEAD + BOW_EYE + work, marks,
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0], max=2.5), dict(rope=0, at=1, dir=[0, 1, 0], w=0.3, max=0.8)])


@knot
def gassa_scorsoia():
    """Gassa scorsoia: una piccola gassa d'amante fatta attorno al proprio dormiente."""
    main = [(-15, -1.2), (-9, -1.2), (-5.5, -1.2), (0, -1.2), (6, -1.2), (9.5, 0), (10.5, 6),
            (10, 16), (8, 21.5), (4, 22.5), (1.2, 21.2)]
    marks = BOW_MARKS + [(-4.55, -1.2, 'U'), (3.8, -1.2, 'O')]
    R = flatm([main + BOW_HEAD + BOW_EYE + BOW_WORK], marks)
    return dict(ropes=R, pulls=[dict(rope=0, at=0, dir=[-1, 0, 0], max=3.0), dict(rope=0, at=1, dir=[0, -1, 0], w=0.3, max=0.9)],
                view=dict(elev=70, zoom=1.0), jam=0.25, snug=0.8)


# --------------------------------------------------- famiglia della scotta
W_BIGHT = [(-1.45, 14), (-1.45, 8), (-1.45, 3), (-1.3, 0.2), (-0.8, -1.3), (0, -1.75), (0.8, -1.3),
           (1.3, 0.2), (1.45, 3), (1.45, 8), (1.45, 11)]


def _sheet(red, marks, white=W_BIGHT, extra=(), colors=('main', 'second', 'teal'), radii=(0.62, 0.42, 0.42), default=None, **kw):
    ropes = [white, red, *extra]
    R = flatm(ropes, marks, default=default)
    n = len(ropes)
    pulls = [dict(rope=0, at=0, dir=[0, 1, 0]), dict(rope=0, at=1, dir=[0, 1, 0], w=0.4)]
    for i in range(1, n):
        pulls += [dict(rope=i, at=0, dir=[0, -1, 0]), dict(rope=i, at=1, dir=[1, 0, 0], w=0.3)]
    step = 0.7 / (n - 1)
    d = dict(ropes=R, colors=list(colors[:n]), radii=list(radii[:n]),
             reveal=[[0, 0.3, 0]] + [[0.3 + step * (i - 1), 0.3 + step * i, 0] for i in range(1, n)],
             pulls=pulls, view=dict(elev=60, zoom=1.3), snug=0.5)
    d.update(kw)
    return d


def _wraps(n):
    """Cima sottile: sale nel doppino e fa n giri attorno ai due rami prima di
    passare sotto se stessa (n=1 scotta, 2 doppia, 3 tripla)."""
    red = [(0.3, -13), (0.3, -6), (0.25, -2.6), (0.3, -0.6), (0.6, 1.0), (1.1, 2.6)]
    marks = [(0.25, -1.65, 'U', 1)]
    y_front = 2.6 + 0.9 * (n - 1)     # quota del primo passaggio sopra il ramo destro
    for i in range(n):
        yb = 4.9 + 1.15 * (n - 1) - 1.15 * i        # passaggio dietro (dall'alto in basso)
        yf = 2.4 + 0.9 * (n - 1) - 0.95 * i          # passaggio davanti sul ramo sinistro
        if i == 0:
            red += [(1.9, y_front + 0.9), (2.8, yb - 0.3)]
            marks.append((1.45, y_front + 0.55, 'O', 1))
        red += [(2.0, yb + 0.4), (0, yb + 0.5), (-2.0, yb + 0.4), (-2.9 - 0.15 * i, yb - 0.6),
                (-2.7 - 0.15 * i, yf + 0.7), (-1.6, yf - 0.1)]
        marks += [(1.45, yb + 0.42, 'U', 1), (-1.45, yb + 0.42, 'U', 1), (-1.45, yf + 0.05, 'O', 1)]
        if i < n - 1:     # passa sopra il proprio dormiente e il ramo destro, risale dietro
            red += [(0, yf - 0.45), (1.9, yf - 0.6), (3.0 + 0.2 * i, yf + 0.4), (3.2 + 0.2 * i, yb - 1.2), (2.6, yb - 0.9)]
            marks += [(0.75, yf - 0.5, 'O', 1), (1.45, yf - 0.55, 'O', 1)]
        else:             # passa sotto se stesso, sopra il doppino, ed esce
            red += [(-0.2, yf - 0.5), (1.0, yf - 0.6), (2.4, yf - 0.7), (4.6, yf - 0.8)]
            marks += [(0.65, yf - 0.55, 'U', 1), (1.45, yf - 0.65, 'O', 1)]
    return red, marks


@knot
def scotta_doppio():
    red, marks = _wraps(2)
    return _sheet(red, marks, default='O')


@knot
def scotta_triplo():
    red, marks = _wraps(3)
    return _sheet(red, marks, view=dict(elev=60, zoom=1.2), default='O')


@knot
def becket():
    """Nodo becket: il nodo di scotta fatto su una gassa impiombata (qui la gassa bianca)."""
    white = W_BIGHT[:-2] + [(1.45, 6.5)]
    red, marks = _wraps(1)
    return _sheet(red, marks, white=white)


@knot
def scotta_tre_vie():
    """Due cime sottili sulla stessa gassa: due nodi di scotta uno sopra l'altro."""
    red, marks = _wraps(1)
    teal = [(-0.45, -13), (-0.45, -6), (-0.45, -2.6), (-0.45, -0.6), (-0.4, 3.5), (0.2, 5.8), (1.0, 6.6),
            (1.9, 7.4), (2.8, 8.2), (2.0, 8.9), (0, 9.0), (-2.0, 8.9), (-2.9, 8.0), (-2.7, 6.7),
            (-1.6, 5.9), (-0.2, 5.45), (1.0, 5.35), (2.4, 5.25), (4.6, 5.1)]
    marks = marks + [(-0.45, -1.7, 'U', 2), (-0.45, 2.05, 'O', 2), (1.45, 6.95, 'O', 2), (1.45, 8.95, 'U', 2),
                     (-1.45, 8.95, 'U', 2), (-1.45, 5.95, 'O', 2), (0.1, 5.5, 'U', 2), (1.45, 5.3, 'O', 2)]
    return _sheet(red, marks, extra=[teal], view=dict(elev=60, zoom=1.1))

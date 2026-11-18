"""Nodario completo, parte 5: Carrick, gasse collegate, famiglia Clara,
nodo di sollevamento, matasse."""
import numpy as np
from geom import flatm, rope3d, rturn, vturn, line
from knots_src import knot, _clove_pts
from knots_v3 import BOW_HEAD, BOW_EYE, BOW_WORK, BOW_MARKS


@knot
def carrick():
    """Nodo Carrick: due asole intrecciate sopra-sotto, otto incroci alternati."""
    A = [(-11, 1.2), (-4, 1.2), (-1, 1.2), (1.6, 1.0), (3.2, -0.2), (2.6, -2.0), (0.8, -2.4), (-0.6, -1.2),
         (-0.9, 0.6), (-1.3, 2.6), (-3.0, 4.5), (-4.5, 6.0)]
    B = [(-x, -y) for x, y in A]
    marks = [(-2.9, 1.2, 'O'), (-0.9, 1.2, 'O'), (0.6, 1.2, 'O'), (3.0, -1.2, 'U'), (1.2, -2.3, 'O'),
             (-0.62, -1.1, 'U'), (-1.2, 2.3, 'U'), (0.9, -1.2, 'O', 1)]
    R = flatm([A, B], marks)
    return dict(ropes=R, colors=['main', 'second'], reveal=[[0, 0.5, 0], [0.5, 1, 0]],
                pulls=[dict(rope=0, at=0, dir=[-1, 0, 0]), dict(rope=0, at=1, dir=[-0.5, 1, 0], w=0.3),
                       dict(rope=1, at=0, dir=[1, 0, 0]), dict(rope=1, at=1, dir=[0.5, -1, 0], w=0.3)],
                view=dict(elev=65, zoom=1.5), snug=0.4)


@knot
def gasse_collegate():
    """Due gasse d'amante con gli occhi incatenati."""
    c = -3.35
    rot = lambda p: (-p[0], 2 * c - p[1])
    A = BOW_HEAD + BOW_EYE + BOW_WORK
    B = [rot(p) for p in A]
    marks = list(BOW_MARKS) + [(*rot(m[:2]), m[2], 1) for m in BOW_MARKS]
    marks += [(2.25, -3.6, 'O', 0), (-2.25, -3.6, 'U', 0)]
    R = flatm([A, B], marks, tol=1.0)
    return dict(ropes=R, colors=['main', 'second'], reveal=[[0, 0.5, 0], [0.5, 1, 0]],
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0], max=2.5), dict(rope=0, at=1, dir=[0, -1, 0], w=0.3, max=0.8),
                       dict(rope=1, at=0, dir=[0, -1, 0], max=2.5), dict(rope=1, at=1, dir=[0, 1, 0], w=0.3, max=0.8)],
                view=dict(elev=70, zoom=1.5), jam=0.25, snug=0.8)


# ----------------------------------------------------- famiglia Clara
THICK_R, THIN_R = 0.9, 0.42


def _clara(turns=2, under=1, queen=False):
    """Cima sottile (bianca) su cima grossa (arancio, ferma), trazione lungo la grossa verso destra.
    turns giri verso sinistra, poi il capo torna sopra i giri e passa sotto 'under' parti."""
    Rw = THICK_R + THIN_R + 0.02
    p = 1.0                                          # passo dei giri
    x0 = 1.0
    pts = [(14, 0.4, 1.5), (6, 0.2, 1.4), (2.6, 0.05, Rw), (x0 + 0.6, 0.0, Rw)]
    pts += rturn(0, 360 * turns, x0, x0 - p * turns, Rw)
    xe = x0 - p * turns
    if queen:   # torna oltre il proprio dormiente e fa un giro in senso opposto
        pts += [(xe - 0.2, 0.9, Rw + 0.3), (x0 + 1.0, 1.9, Rw + 0.9), (x0 + 2.0, 1.4, Rw + 0.4)]
        pts += rturn(60, -300, x0 + 2.0, x0 + 2.8, Rw)
        pts += [(x0 + 2.6, 0.2, Rw + 1.3), (x0 + 1.3, 0.3, Rw + 1.0), (x0 + 0.2, 0.1, Rw + 0.25),
                (x0 - 0.6, -0.1, Rw - 0.15)]
    else:       # il capo risale in diagonale sopra i giri e si infila sotto
        pts += [(xe - 0.2, 0.8, Rw + 0.4), (xe + 0.6, 1.3, Rw + 1.0), (x0 - 0.2, 0.9, Rw + 1.1)]
        if under == 1:
            pts += [(x0 + 0.5, 0.15, Rw + 0.15), (x0 + 1.1, -0.6, Rw + 0.2)]
        else:
            pts += [(x0 - 0.1, 0.3, Rw + 0.15), (x0 + 0.6, -0.2, Rw - 0.05), (x0 + 1.4, -0.7, Rw + 0.2)]
    pts += [(pts[-1][0] + 1.6, pts[-1][1] - 1.4, pts[-1][2] + 0.4), (pts[-1][0] + 3.6, pts[-1][1] - 3.0, pts[-1][2] + 0.8)]
    thick = [(-16, 0, 0), (-8, 0, 0), (0, 0, 0), (8, 0, 0), (16, 0, 0)]
    return dict(ropes=[rope3d(pts), rope3d(thick)], solid={1: 'rope:second'}, radii=[THIN_R, THICK_R],
                colors=['main', 'second'],
                pulls=[dict(rope=0, at=0, dir=[1, 0, 0], max=3.0), dict(rope=0, at=1, dir=[1, -0.5, 0.3], w=0.4, max=1.2)],
                view=dict(elev=14, az=0, zoom=1.7), jam=0.3, snug=0.95)


@knot
def clara():
    return _clara(2, 1)


@knot
def clara_aggrappante():
    return _clara(2, 2)


@knot
def regina_clara():
    return _clara(2, 2, queen=True)


@knot
def grande_regina_clara():
    return _clara(6, 2, queen=True)


# ----------------------------------------------------- sollevamento
@knot
def sollevamento():
    """Nodo di sollevamento: 7 giri stretti verso il basso attorno al tubo,
    il capo risale sopra i giri e si chiude con due mezzi colli sul dormiente."""
    pole = dict(type='cyl', c=[0, 3.0, 0], axis=[0, 1, 0], r=1.0, h=22, mat='steel')
    Rw = 1.5
    pts = [(0, 22, Rw), (0, 15, Rw), (0, 9.2, Rw)]
    pts += vturn(0, -360 * 7, 9.0, 1.6, Rw)                       # giri verso il basso
    pts += [(0.5, 1.0, Rw + 0.2), (0.9, 2.6, Rw + 1.0), (0.9, 6.0, Rw + 1.0), (0.8, 9.6, Rw + 0.6), (0.7, 10.6, Rw + 0.1)]
    cl = _clove_pts(rail_r=0.5, x0=-0.6, x1=1.35, x2=-1.35, x3=0.6, top=3.0, bottom=-12)
    cl = [(-y, 11.9 + x, Rw + z) for x, y, z in cl]                # due mezzi colli sul dormiente
    pts += cl[3:]
    return dict(ropes=[rope3d(pts)], props=[pole],
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0]), dict(rope=0, at=1, dir=[-1, 0, 0], w=0.3, max=0.5)],
                view=dict(mode='stand', elev=12, az=-15, zoom=0.85, ground=-8), jam=0.25, snug=0.6)


# ----------------------------------------------------- matasse
def _coil(n=5, R=3.6, cy=6.0, z0=-2.2):
    pts = [(-0.4, -12, z0 - 0.6), (-0.3, -4, z0 - 0.4), (0.0, cy - R, z0)]
    for t in np.linspace(0, 2 * np.pi * n, 26 * n)[1:]:
        pts.append((R * np.sin(-t), cy - R * np.cos(t), z0 + 1.05 * t / (2 * np.pi)))
    return pts, z0 + 1.05 * n


@knot
def matassa_marinaio():
    """Matassa del marinaio: spire appese, il capo fa qualche giro attorno alla
    sommità e si infila dentro la matassa."""
    cy, R = 6.0, 3.6
    pts, zt = _coil(5, R, cy)
    top = cy + R
    pts += [(0.8, top - 0.2, zt + 0.4), (1.4, top + 0.4, zt - 0.4)]
    for k in range(3):     # giri attorno al fascio in cima (asse z)
        z = zt - 1.0 - k * 1.05
        pts += [(1.3, top, z), (0, top + 1.3, z - 0.25), (-1.3, top, z - 0.5), (0, top - 1.35, z - 0.75)]
    pts += [(0.9, top - 0.9, -3.0), (0.4, top - 2.0, -3.6), (0.2, top - 5.0, -3.8)]   # dentro la matassa
    hook = dict(type='cyl', c=[0, top + 0.2, 0], axis=[0, 0, 1], r=0.6, h=9, mat='steel', deco=True)
    return dict(ropes=[rope3d(pts)], props=[hook], pulls=[],
                view=dict(mode='stand', elev=10, az=-30, zoom=1.0, ground=-12.5), snug=1.0)


@knot
def matassa_briol():
    """Matassa di briol (gasket coil): il capo avvolge la matassa a meta' e un
    doppino passa nell'occhio in alto e si accavalla sulla cima della matassa."""
    cy, R = 6.0, 3.6
    pts, zt = _coil(5, R, cy)
    pts += [(1.0, cy + R - 0.4, zt + 0.3), (3.0, cy + 1.0, zt + 0.9), (4.6, cy, zt + 0.5)]
    for k in range(3):     # giri attorno a tutte le spire, a meta' altezza (lato destro)
        y = cy + 1.2 - k * 1.05
        pts += [(R + 1.2, y, zt + 0.8), (R + 1.2, y - 0.25, -3.6), (R - 1.2, y - 0.5, -3.6), (R - 1.2, y - 0.75, zt + 0.8)]
    pts += [(R + 1.0, cy - 2.2, zt + 0.9), (R + 0.2, cy - 3.2, zt), (R - 0.5, cy - 3.6, -1.0), (R - 0.4, cy - 5.6, -1.2)]
    hook = dict(type='cyl', c=[0, cy + R + 0.2, 0], axis=[0, 0, 1], r=0.6, h=9, mat='steel', deco=True)
    return dict(ropes=[rope3d(pts)], props=[hook], pulls=[],
                view=dict(mode='stand', elev=10, az=-30, zoom=1.0, ground=-12.5), snug=1.0)

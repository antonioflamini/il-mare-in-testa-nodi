"""Nodario completo, parte 4: nodi d'ancoraggio costruiti in 3D (eliche attorno
a tubi, pali, anelli e al proprio dormiente)."""
import numpy as np
from geom import rope3d, rturn, vturn, flatm
from knots_src import knot, _clove_pts
from knots_v2 import ring_solid

RAIL = dict(type='cyl', c=[0, 0, 0], axis=[1, 0, 0], r=1.0, h=14, mat='steel')


def _sv(**kw):
    v = dict(mode='stand', elev=12, az=-18, zoom=1.5)
    v.update(kw)
    return v


@knot
def barcaiolo_ganciato():
    """Parlato ganciato: il secondo giro esce con un doppino sotto il cavaliere."""
    pts = _clove_pts(x3=0.15)[:-3]
    Rw = 1.5
    pts += [(0.15, 1.2, Rw), (0.2, 2.6, Rw), (0.55, 3.4, Rw + 0.05), (0.95, 2.6, Rw), (0.95, 0.4, Rw),
            (0.95, -1.6, Rw), (0.95, -4.5, Rw)]
    return dict(ropes=[rope3d(pts)], props=[RAIL],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[0, -1, 0], w=0.3, max=0.5)],
                view=_sv(), jam=0.25, snug=0.7)


@knot
def barcaiolo_doppino():
    """Parlato a doppino: due asole calate dall'alto sulla bitta, senza usare i capi."""
    cl = _clove_pts(rail_r=1.0, x0=-0.7, x1=1.35, x2=-1.35, x3=0.7, top=11, bottom=-11)
    pts = [(y, 3.4 - x, z) for x, y, z in cl]          # asse del palo verticale
    post = dict(type='cyl', c=[0, 2.6, 0], axis=[0, 1, 0], r=1.0, h=5.2, mat='wood', cap=True)
    return dict(ropes=[rope3d(pts)], props=[post, dict(type='plane', y=0, hidden=True)],
                pulls=[dict(rope=0, at=0, dir=[-1, 0, 0]), dict(rope=0, at=1, dir=[1, 0, 0], w=0.5)],
                view=_sv(elev=22, az=-25, zoom=1.6, ground=0), jam=0.25, snug=0.7)


ANC_HEAD = [(-0.8, -12), (-0.8, -4), (-0.8, 1.2), (-0.8, 3.0), (-0.55, 3.95),
            (-0.3, 3.0), (-0.02, 1.15), (0.25, 3.0), (0.5, 3.95), (0.75, 3.0), (1.05, 1.15),
            (0.3, 0.75), (-0.8, 0.7), (-1.7, 0.9), (-1.9, 1.7), (-1.4, 2.0),
            (-0.75, 2.0), (-0.18, 2.0), (0.12, 2.0), (0.9, 2.0), (1.9, 2.0)]
ANC_MARKS = [(-0.8, 3.0, 'O'), (-0.3, 3.0, 'U'), (0.25, 3.0, 'O'), (0.75, 3.0, 'U'),
             (-0.8, 0.7, 'U'), (-0.8, 2.0, 'U'), (-0.17, 2.0, 'O'), (0.12, 2.0, 'U'), (0.88, 2.0, 'O')]


@knot
def drizza():
    """Nodo di drizza: volta tonda sul grillo/anello, capo attorno al dormiente e dentro i due giri."""
    rope = ANC_HEAD + [(2.6, 2.6), (3.3, 4.0), (3.6, 5.4)]
    R = flatm([rope, ring_solid()], ANC_MARKS, solid={1})
    return dict(ropes=R, solid={1: 'steel'}, radii=[0.5, 0.42],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[0.3, 1, 0], w=0.3, max=0.6)],
                view=_sv(elev=10, az=-15, zoom=1.4), jam=0.25, snug=0.8)


def _buntline(slipped=False):
    """Passa nell'anello, poi un parlato attorno al dormiente che risale verso l'anello."""
    ring = dict(type='torus', c=[0, 0, 0], axis=[0, 0, 1], R=3.0, r=0.42, mat='steel')
    bolt = dict(type='cyl', c=[0, 4.6, 0], axis=[0, 1, 0], r=0.55, h=3.2, mat='steel', deco=True)
    beam = dict(type='box', c=[0, 6.6, 0], size=[16, 1.6, 3.2], mat='wood', deco=True)
    Rw = 0.92
    pts = [(-1.0, -17, Rw), (-1.0, -9, Rw), (-1.0, -4.6, Rw), (-1.0, -3.6, Rw)]
    for th in np.linspace(0, 330, 12)[1:]:                         # un solo passaggio nell'anello
        pts.append((-1.0 + 1.0 * th / 330, -3 + Rw * np.sin(np.radians(th)), Rw * np.cos(np.radians(th))))
    pts += [(0.5, -4.0, 0.6), (1.4, -4.7, 1.0), (1.3, -5.5, 1.6)]
    cl = _clove_pts(rail_r=0.5, x0=-0.6, x1=1.35, x2=-1.35, x3=0.6, top=3.0, bottom=-12)
    cl = [(-1.0 - y, -5.7 + x, Rw + z) for x, y, z in cl]          # parlato che sale verso l'anello
    pts += cl[2:-2]
    if slipped:
        a = cl[-3]
        pts += [(a[0] - 0.4, a[1] + 0.9, a[2]), (a[0] - 1.6, a[1] + 1.4, a[2] - 0.2), (a[0] - 2.2, a[1] + 0.3, a[2]),
                (a[0] - 1.3, a[1] - 0.3, a[2] + 0.4), (a[0] + 0.2, a[1] - 0.2, a[2] + 0.3), (a[0] + 1.6, a[1] - 0.1, a[2])]
    else:
        pts += cl[-2:]
    return dict(ropes=[rope3d(pts)], props=[ring, bolt, beam],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[-1, 0, 0], w=0.3, max=0.6)],
                view=_sv(elev=8, az=-25, zoom=1.9, ground=-17.5), jam=0.25, snug=0.8)


@knot
def drizza_di_mura():
    return _buntline()


@knot
def drizza_ganciato():
    return _buntline(slipped=True)


@knot
def brancarella():
    """Nodo di brancarella (taut-line): attorno al picchetto, due giri sul
    dormiente verso il picchetto e un mezzo collo fuori."""
    peg = dict(type='cyl', c=[0, -10, 0], axis=[0, 0, 1], r=1.0, h=5, mat='wood')
    ax = -1.5
    pts = [(ax, 14, 0), (ax, 6, 0), (ax, -4, 0), (ax, -8.6, 0)]
    pts += [(-1.4, -10.0, 0), (-1.06, -11.06, 0), (0, -11.5, 0), (1.06, -11.06, 0), (1.5, -10.0, 0)]   # attorno al picchetto
    pts += [(1.5, -7, 0), (1.2, -3.6, 0), (0.0, -1.2, 0.0)]
    pts += vturn(90, 90 + 720, -0.9, -3.4, 1.02, ax=ax, az=0, bumps=[(450, 40, 0.0)])                 # due giri verso il picchetto
    pts += [(ax + 1.5, -3.2, 0.6), (ax + 0.6, -2.0, 2.0), (ax - 0.6, -0.4, 1.9), (ax - 1.15, 0.6, 0.5)]  # scavalca i giri davanti
    pts += vturn(-90, -450, 0.7, 1.9, 1.02, ax=ax, az=0)                                                # mezzo collo sopra
    pts += [(ax - 1.4, 1.2, -0.5), (ax - 1.7, 0.0, -0.4), (ax - 1.9, -1.6, -0.2)]                      # sotto se stesso
    return dict(ropes=[rope3d(pts)], props=[peg],
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0]), dict(rope=0, at=1, dir=[0, -1, 0], w=0.3, max=0.6)],
                view=_sv(elev=10, az=-10, zoom=1.3, ground=-12), jam=0.25, snug=0.8)


@knot
def volta_di_bitta():
    """Volta di bitta (pile hitch): un doppino gira dietro la bitta e la sua
    asola si cala dall'alto, passando davanti sopra i due rami."""
    post = dict(type='cyl', c=[0, 3.0, 0], axis=[0, 1, 0], r=1.2, h=6.0, mat='wood', cap=True)
    Rw = 1.7
    pts = [(-0.55, 1.8, 15), (-0.55, 1.8, 7), (-0.55, 1.8, 3.0)]
    pts += vturn(-18, -270, 1.8, 1.8, Rw)                    # ramo 1: sinistra, dietro, destra
    pts += vturn(-270, -330, 1.8, 2.4, Rw)                   # inizia il doppino davanti a destra
    pts += vturn(-330, -690, 2.4, 3.3, Rw, bumps=[(-360, 32, 1.1)])   # asola attorno alla bitta, davanti sopra i rami
    pts += vturn(-690, -630, 3.3, 3.1, Rw)                   # punta del doppino: torna indietro
    pts += vturn(-630, -378, 3.1, 2.9, Rw)                   # ramo 2: destra, dietro, sinistra
    pts += [(-0.55, 2.9, 3.0), (-0.55, 2.9, 7), (-0.55, 2.9, 12)]
    return dict(ropes=[rope3d(pts)], props=[post, dict(type='plane', y=0, hidden=True)],
                pulls=[dict(rope=0, at=0, dir=[0, 0, 1]), dict(rope=0, at=1, dir=[0, 0, 1], w=0.6)],
                view=_sv(elev=35, az=30, zoom=1.4, ground=0), jam=0.25, snug=0.6)

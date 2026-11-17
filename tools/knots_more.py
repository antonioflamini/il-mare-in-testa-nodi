"""Altri nodi del nodario (importati da knots_src)."""
import numpy as np
from geom import flat, rope3d
from knots_src import knot, _clove_pts


@knot
def stivatore():
    """Come il Savoia, ma con un giro in piu' attorno al dormiente."""
    pts = [(0, 19), (0, 14), (0, 9), (0, 5), (0, 1.5), (1.6, -0.9), (3.4, 0.6), (3.4, 3.4), (1.6, 5.4),
           (-1.5, 6.8), (-3.0, 8.0), (-1.6, 9.0), (1.6, 9.5), (2.7, 10.1), (1.6, 10.8), (-1.6, 11.2),
           (-2.7, 11.9), (-1.6, 12.6), (1.6, 13.0), (3.0, 12.6), (3.9, 11.0), (3.9, 8.5), (3.2, 6.4),
           (2.3, 4.4), (2.0, 3.0), (1.7, 0.6), (1.5, -2.5), (1.2, -7)]
    R = flat([pts], 'OUOUOUOUOUOU')
    return dict(ropes=R, pulls=[dict(rope=0, at=0, dir=[0, 1, 0]), dict(rope=0, at=1, dir=[0, -1, 0])],
                view=dict(zoom=1.1))


def _map(pts, f):
    return [f(*p) for p in pts]


@knot
def volta_tonda():
    """Volta tonda (due giri sull'anello) e due mezzi colli sul dormiente."""
    ring = dict(type='torus', c=[0, 0, 0], axis=[0, 0, 1], R=3.0, r=0.42, mat='steel')
    bolt = dict(type='cyl', c=[0, 4.6, 0], axis=[0, 1, 0], r=0.55, h=3.2, mat='steel', deco=True)
    beam = dict(type='box', c=[0, 6.6, 0], size=[16, 1.6, 3.2], mat='wood', deco=True)
    Rw = 0.92
    pts = [(-1.0, -17, Rw), (-1.0, -9, Rw), (-1.0, -4.6, Rw), (-1.0, -3.6, Rw)]
    for th in np.linspace(0, 700, 22)[1:]:
        x = -1.0 + 2.05 * th / 700
        pts.append((x, -3 + Rw * np.sin(np.radians(th)), Rw * np.cos(np.radians(th))))
    pts += [(1.35, -4.6, 1.15), (1.5, -5.6, 1.6)]
    # due mezzi colli = un parlato attorno al dormiente (asse verticale x=-1, z=Rw)
    cl = _clove_pts(rail_r=0.5, x0=-0.6, x1=1.35, x2=-1.35, x3=0.6, top=3.2, bottom=-12)
    cl = _map(cl, lambda x, y, z: (-1.0 - y, -7.6 - x, Rw + z))
    pts += cl[2:]
    R = [rope3d(pts)]
    return dict(ropes=R, props=[ring, bolt, beam],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[-1, 0, 0], w=0.35)],
                view=dict(mode='stand', elev=8, az=-25, zoom=1.25, ground=-17.5), jam=0.25, snug=0.8)


def _turn(a0, a1, x0, x1, Rw, bumps=(), n=None):
    """Giro attorno all'asse x (0 = davanti, 90 = sopra), con rialzi locali."""
    out = []
    for th in np.linspace(a0, a1, n or max(int(abs(a1 - a0) / 30), 3))[1:]:
        x = x0 + (x1 - x0) * (th - a0) / (a1 - a0)
        r = Rw
        for c, w, h in bumps:
            r += h * np.exp(-((th - c) / w) ** 2)
        out.append((x, r * np.sin(np.radians(th)), r * np.cos(np.radians(th))))
    return out


@knot
def bozza():
    """Nodo di bozza su una scotta in tensione (arancio): due giri che
    avanzano verso il carico e un mezzo collo dall'altra parte."""
    Rw = 1.12
    line = [(-16, 0, 0), (-8, 0, 0), (0, 0, 0), (8, 0, 0), (16, 0, 0)]
    pts = [(-15, -1.2, 2.6), (-8, -0.6, 1.8), (-3, -0.2, 1.15), (0.5, -0.1, 1.02), (1.6, -0.35, 1.0)]
    pts += _turn(-20, 360, 2.0, 0.8, Rw, bumps=[(360, 35, 1.0)])
    pts += _turn(360, 720, 0.8, -0.4, Rw, bumps=[(360, 35, 1.0), (720, 35, 1.0)])
    pts += _turn(720, 900, -0.4, 2.4, Rw, bumps=[(800, 50, 2.0)])
    pts += _turn(900, 1080, 2.4, 3.2, Rw)
    pts += _turn(1080, 1150, 3.2, 2.0, Rw, bumps=[(1150, 40, 1.0)])
    pts += [(1.2, 2.2, 0.1), (0.6, 2.0, -1.3)]
    R = [rope3d(pts), rope3d(line)]
    return dict(ropes=R, colors=['main', 'second'], reveal=[[0, 1, 0], [0, 0.001, 1.0]],
                pulls=[dict(rope=0, at=0, dir=[-1, -0.1, 0.15], max=2.0), dict(rope=0, at=1, dir=[0, 0.2, -1], w=0.3, max=0.6)],
                pins=[dict(rope=1, at=0), dict(rope=1, at=1)], fixed_rope=1,
                view=dict(elev=40, az=-10, zoom=1.4), jam=0.25, snug=0.8)


@knot
def bocca_di_lupo():
    """Bocca di lupo su un tientibene: il doppino abbraccia il tubo e i due
    rami passano dentro il doppino."""
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
    pts += [(0.55, -1.4, Rw), (0.55, -6, Rw), (0.55, -11, Rw)]
    R = [rope3d(pts)]
    return dict(ropes=R, props=[rail],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[0, -1, 0])],
                view=dict(mode='stand', elev=12, az=-20, zoom=1.5), jam=0.25, snug=0.8)


@knot
def galloccia():
    """Nodo di galloccia (proporzioni reali: galloccia ~15 diametri):
    giro alla base, un otto sulle corna, chiusura a mezzo collo."""
    H, rh = 3.6, 0.9
    props = [dict(type='cyl', c=[0, H, 0], axis=[1, 0, 0], r=rh, h=14.0, mat='steel'),
             dict(type='cyl', c=[-2.4, H / 2, 0], axis=[0, 1, 0], r=0.8, h=H, mat='steel'),
             dict(type='cyl', c=[2.4, H / 2, 0], axis=[0, 1, 0], r=0.8, h=H, mat='steel'),
             dict(type='box', c=[0, 0.15, 0], size=[7.0, 0.3, 2.2], mat='steel'),
             dict(type='plane', y=0, hidden=True)]

    def P(x, phi, r):        # coordinate polari attorno al corno (0 davanti, 90 sopra)
        a = np.radians(phi)
        return (x, H + r * np.sin(a), r * np.cos(a))
    R1, R2, R3 = 1.45, 2.45, 3.45
    pts = [(-20, 0.5, 8), (-11, 0.55, 4.5), (-6, 0.75, 2.0),
           (-3, 1.0, 1.5), (0, 1.0, 1.5), (3, 1.0, 1.5),                    # giro alla base
           (3.9, 1.0, 1.1), (4.25, 1.0, 0), (3.9, 1.0, -1.1), (3, 1.0, -1.5),
           (0, 1.0, -1.5), (-3, 1.05, -1.5),
           (-3.9, 1.15, -1.1), (-4.25, 1.4, 0), (-4.0, 1.9, 1.0), P(-3.2, -35, R1)]
    pts += [P(-2.2, 15, R1), P(-0.8, 70, R1), P(0.8, 110, R1), P(2.2, 165, R1), P(3.2, 215, R1)]   # 1o braccio
    pts += [P(4.3, 260, R1), P(4.4, 300, R1), P(4.3, 340, R1), P(3.4, 15, R1)]                      # sotto il corno +x
    pts += [P(2.2, 30, R1 + 0.3), P(0.9, 75, R2), P(-0.9, 105, R2), P(-2.2, 160, R1 + 0.3), P(-3.2, 210, R1)]  # 2o braccio
    pts += [P(-4.35, 255, R1), P(-4.45, 300, R1), P(-4.35, 340, R1), P(-3.4, 10, R1)]               # sotto il corno -x
    pts += [P(-1.8, 30, R1 + 0.2), P(-0.4, 65, R2), P(0.7, 95, R3), P(1.8, 130, R3 - 0.3),
            P(2.9, 165, R2), P(3.9, 205, R1 + 0.3)]                                                  # mezzo collo
    pts += [P(5.2, 260, R1), P(5.4, 310, R1), P(5.3, 355, R1), P(4.6, 40, R1), P(3.5, 95, R1),
            P(2.4, 135, R1 + 0.2), P(1.3, 175, R2), P(0.4, 215, R2), (-0.4, 1.4, -2.6), (-1.5, 0.6, -4.2)]
    R = [rope3d(pts)]
    return dict(ropes=R, props=props,
                pulls=[dict(rope=0, at=0, dir=[-1, 0, 0.45], max=1.5), dict(rope=0, at=1, dir=[-0.4, -0.3, -1], w=0.25, max=0.4)],
                view=dict(mode='stand', elev=40, az=-28, zoom=1.6, ground=0), jam=0.3, snug=1.0)


@knot
def fiocco_fiammingo():
    """Cima avvolta a spirale piatta in coperta (si parte dal capo, al centro)."""
    pts = []
    for t in np.linspace(0.6, 2 * np.pi * 4.6, 160):
        r = 0.9 + 1.04 * t / (2 * np.pi)
        pts.append((r * np.cos(t), r * np.sin(t)))
    last = pts[-1]
    pts += [(last[0] + 2.5, last[1] - 4), (last[0] + 4, last[1] - 12)]
    R = [rope3d([(x, y, 0) for x, y in pts])]
    return dict(ropes=R, pulls=[], view=dict(elev=70, zoom=1.3), snug=1.0)

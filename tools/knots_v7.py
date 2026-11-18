"""Nodario completo, parte 7: i nodi rari della categoria nautica, disegnati
confrontandoli con le immagini di riferimento."""
import numpy as np
from geom import flatm, flat_alt, rope3d, rturn, vturn, line, circle
from knots_src import knot, _clove_pts
from knots_v2 import ring_solid
from knots_v3 import BOW_HEAD, BOW_EYE, BOW_WORK, BOW_MARKS, W_BIGHT, _sheet, _wraps

RAIL = dict(type='cyl', c=[0, 0, 0], axis=[1, 0, 0], r=1.0, h=14, mat='steel')


def _sv(**kw):
    v = dict(mode='stand', elev=12, az=-18, zoom=1.5)
    v.update(kw)
    return v


def _two(A, B, marks=(), rule=None, colors=('main', 'second'), radii=(0.5, 0.5), view=None, **kw):
    R = flatm([A, B], list(marks), rule=rule)
    d = dict(ropes=R, colors=list(colors), radii=list(radii), reveal=[[0, 0.5, 0], [0.5, 1, 0]],
             pulls=[dict(rope=0, at=0, dir=[0, 1, 0], max=2.0), dict(rope=0, at=1, dir=[-1, 0, 0], w=0.3, max=0.6),
                    dict(rope=1, at=0, dir=[0, -1, 0], max=2.0), dict(rope=1, at=1, dir=[1, 0, 0], w=0.3, max=0.6)],
             view=view or dict(elev=65, zoom=1.4), jam=0.25, snug=0.6)
    d.update(kw)
    return d


# ------------------------------------------------------------- Simple Simon
def _simon(double=False, under=False):
    """La cima grossa (bianca) fa un doppino; la sottile (arancio) sale nel
    doppino, abbraccia i due rami in alto (una o due volte), incrocia se stessa
    e ridiscende nel doppino accanto al proprio dormiente."""
    A = [(-0.95, 13), (-0.95, 6), (-0.95, 0), (-0.8, -1.4), (0, -2.1), (0.8, -1.4), (0.95, 0), (0.95, 6), (0.95, 9)]
    B = [(-0.3, -13), (-0.3, -5), (-0.3, -1.0), (-0.1, 0.4), (0.9, 1.6), (2.0, 2.4)]
    marks = [(-0.3, -2.0, 'U', 1), (0.95, 1.45, 'U', 1)]
    tops = [3.6, 4.7] if double else [3.6]
    for k, yt in enumerate(tops):
        B += [(2.2, yt - 0.4), (1.2, yt + 0.25), (0, yt + 0.35), (-1.2, yt + 0.25), (-2.2, yt - 0.4)]
        marks += [(0.95, yt + 0.3, 'O', 1), (-0.95, yt + 0.3, 'O', 1)]
        if k < len(tops) - 1:
            B += [(-2.4, yt + 0.6), (0, yt + 1.0), (2.4, yt + 0.7)]
            marks += [(0.95, yt + 0.95, 'U', 1), (-0.95, yt + 0.95, 'U', 1)]
    B += [(-2.0, 2.4), (-0.9, 1.6), (0.1, 0.4), (0.3, -1.0), (0.3, -5), (0.3, -11)]
    marks += [(-0.95, 1.45, 'U', 1), (0.0, 1.0, 'U' if under else 'O', 1), (0.3, -2.0, 'U', 1)]
    return _two(A, B, marks, colors=('main', 'second'), radii=(0.6, 0.45),
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0], max=2.0), dict(rope=0, at=1, dir=[0, 1, 0], w=0.4, max=0.8),
                       dict(rope=1, at=0, dir=[0, -1, 0], max=2.0), dict(rope=1, at=1, dir=[0, -1, 0], w=0.4, max=0.8)],
                view=dict(elev=65, zoom=1.5), rule=lambda x, y, t: 'O')


@knot
def simon_sopra():
    return _simon(False, False)


@knot
def simon_sotto():
    return _simon(False, True)


@knot
def simon_doppio_sopra():
    return _simon(True, False)


@knot
def simon_doppio_sotto():
    return _simon(True, True)


# ------------------------------------------------------ intugliature per gomene
def _hawser(under=False):
    """Due asole incatenate; i capi escono ai lati opposti. 'Sopra': ogni
    capo chiude passando sopra il proprio dormiente; 'sotto': a mezzo collo."""
    A = [(0, 13), (0, 7), (0.05, 4.4), (0.25, 2.9), (1.45, 1.7), (1.35, 0.0), (0, -0.7), (-1.35, 0.0),
         (-1.45, 1.6), (-0.5, 2.7), (-1.8, 3.4), (-4.5, 3.2)]
    B = [(-x, -y) for x, y in A]
    L = 'U' if under else 'O'
    marks = [(0.15, 2.85, L, 0), (-0.15, -2.85, L, 1), (-1.3, 0.05, 'O', 0), (1.3, -0.05, 'U', 0)]
    return _two(A, B, marks, colors=('second', 'main'),
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0], max=2.0), dict(rope=0, at=1, dir=[-1, 0, 0], w=0.3, max=0.6),
                       dict(rope=1, at=0, dir=[0, -1, 0], max=2.0), dict(rope=1, at=1, dir=[1, 0, 0], w=0.3, max=0.6)],
                view=dict(elev=65, zoom=1.6), rule=lambda x, y, t: 'O')


@knot
def gomene_sopra():
    return _hawser(False)


@knot
def gomene_sotto():
    return _hawser(True)


@knot
def portoghese():
    """Intugliatura alla portoghese: la sottile tesse otto attorno ai due rami del doppino."""
    red = [(0.0, -13), (0.0, -6), (0.0, -2.6), (0.0, -0.8), (-1.8, 0.0)]
    marks = [(0.0, -1.9, 'U', 1)]
    y = 0.0
    for k in range(4):
        red += [(-2.1, y + 0.3), (0.0, y + 0.55), (2.1, y + 0.8), (2.1, y + 1.1), (0.0, y + 1.35), (-2.1, y + 1.6)]
        marks += [(-0.95, y + 0.45, 'O', 1), (0.95, y + 0.65, 'U', 1), (0.95, y + 1.25, 'O', 1), (-0.95, y + 1.45, 'U', 1)]
        y += 1.6
    red += [(-2.4, y + 0.6), (-3.6, y + 1.6)]
    A = [(-0.95, 13), (-0.95, 6), (-0.95, 0), (-0.8, -1.4), (0, -2.1), (0.8, -1.4), (0.95, 0), (0.95, 6), (0.95, 8.5)]
    return _two(A, red, marks, colors=('main', 'second'), radii=(0.62, 0.38),
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0], max=1.5), dict(rope=0, at=1, dir=[0, 1, 0], w=0.4, max=0.6),
                       dict(rope=1, at=0, dir=[0, -1, 0], max=1.5), dict(rope=1, at=1, dir=[-1, 1, 0], w=0.3, max=0.5)],
                view=dict(elev=65, zoom=1.3), rule=lambda x, y, t: 'O' if t[0] > 0 else 'U')


@knot
def intugliatura_due_gasse():
    """Ogni cima fa una gassa d'amante attorno al dormiente dell'altra: le due cime restano parallele."""
    s = 0.5
    P = BOW_HEAD[1:] + BOW_EYE + BOW_WORK
    tr = lambda p: (p[0] * s, p[1] * s - 12)
    A = [(0.4, 14), (0.4, 4)] + [tr(p) for p in P]
    cx = 1.15
    rot = lambda p: (2 * cx - p[0], -p[1])
    B = [rot(p) for p in A]
    marks = [(*tr(m[:2]), m[2], 0) for m in BOW_MARKS] + [(*rot(tr(m[:2])), m[2], 1) for m in BOW_MARKS]
    R = flatm([A, B], marks, tol=0.6, rule=lambda x, y, t: 'O' if y > -12 else 'U')
    return dict(ropes=R, colors=['third', 'teal'], reveal=[[0, 0.5, 0], [0.5, 1, 0]],
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0], max=2.0), dict(rope=0, at=1, dir=[0, -1, 0], w=0.3, max=0.6),
                       dict(rope=1, at=0, dir=[0, -1, 0], max=2.0), dict(rope=1, at=1, dir=[0, 1, 0], w=0.3, max=0.6)],
                view=dict(elev=70, zoom=1.25), jam=0.25, snug=0.6)


# ---------------------------------------------------- broach e stretta di mano
SAV = [(0, 15), (0, 9), (0, 5), (0, 1.5), (1.6, -0.9), (3.4, 0.6), (3.4, 3.4), (1.6, 5.4), (-1.5, 6.8),
       (-3.0, 8.2), (-1.6, 9.8), (1.2, 10.0), (3.2, 8.6), (2.7, 6.0), (2.0, 3.4), (1.7, 0.6), (1.4, -1.6), (-1.0, -2.6), (-4.5, -2.8)]
SAV_M = [(0, 6.1, 'O'), (0, 9.9, 'U'), (2.3, 4.6, 'O'), (1.6, -0.85, 'U')]


@knot
def broach():
    """Nodo broach: due nodi Savoia intrecciati; i capi escono ai lati opposti."""
    sc = 0.6
    A = [(x * sc, y * sc + 1.5) for x, y in SAV]
    B = [(-x, 2.6 - y) for x, y in A]
    marks = [(m[0] * sc, m[1] * sc + 1.5, m[2], 0) for m in SAV_M] + [(-m[0] * sc, 2.6 - (m[1] * sc + 1.5), m[2], 1) for m in SAV_M]
    return _two(A, B, marks, rule=lambda x, y, t: 'U' if y > 1.3 else 'O', view=dict(elev=65, zoom=1.1))


OV = None


@knot
def stretta_di_mano():
    """Stretta di mano: due nodi semplici, uno dentro l'altro; ogni capo esce
    lungo il dormiente dell'altra cima."""
    t = np.linspace(np.pi + 0.45, 3 * np.pi - 0.45, 14)
    s = 1.1
    core = [(s * (np.sin(a) + 2 * np.sin(2 * a)), s * (np.cos(a) - 2 * np.cos(2 * a))) for a in t]
    A = [(0.6, 13), (0.6, 6)] + [(x + 0.3, y + 3.0) for x, y in core] + [(-0.9, -2.0), (-0.6, -8)]
    B = [(-x, -y) for x, y in A]
    from geom import flat_alt
    R = flat_alt([A, B])
    return dict(ropes=R, colors=['main', 'teal'], reveal=[[0, 0.5, 0], [0.5, 1, 0]],
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0], max=2.0), dict(rope=0, at=1, dir=[0, -1, 0], w=0.3, max=0.6),
                       dict(rope=1, at=0, dir=[0, -1, 0], max=2.0), dict(rope=1, at=1, dir=[0, 1, 0], w=0.3, max=0.6)],
                view=dict(elev=65, zoom=1.0), jam=0.25, snug=0.6)


# ------------------------------------------------------------ occhi
@knot
def drago_doppio():
    """Cappio del drago doppio: un occhio fisso in testa; il capo gira due volte
    attorno al dormiente e si chiude come una gassa (capo che esce di lato)."""
    th = lambda a: (1.6 * np.cos(np.radians(a)), 1.6 * np.sin(np.radians(a)))
    pts = [(0, -14), (0, -6), (0, -2.0)]
    pts += [th(a) for a in (-80, -40, 0, 40, 80, 120, 160, 200, 240)]                   # tana
    pts += [(-1.4, -1.9), (-2.8, 0.5), (-3.0, 5), (-1.6, 9), (0, 10.2), (1.6, 9), (3.0, 5), (2.2, 2.4),   # occhio
            (0.6, 1.9), (0.5, 0.2), (0.5, -1.2), (0.6, -2.8),                                           # scende nella tana
            (1.6, -3.4), (1.2, -4.4), (-0.2, -4.6), (-1.4, -4.0), (-1.3, -3.0), (0.2, -2.9),             # due giri sul dormiente
            (1.7, -3.9), (1.4, -5.2), (-0.1, -5.5), (-1.5, -4.9), (-1.6, -3.6), (-0.5, -2.5),
            (-0.5, -0.8), (-0.6, 0.6), (-1.6, 1.6), (-4.5, 1.8)]
    R = flat_alt([pts])
    return dict(ropes=R, pulls=[dict(rope=0, at=0, dir=[0, -1, 0], max=2.0), dict(rope=0, at=1, dir=[-1, 0, 0], w=0.3, max=0.6)],
                props=[dict(type='cyl', c=[0, 6.0, 0], axis=[0, 0, 1], r=1.4, h=6, mat='steel', hidden=True)],
                view=dict(elev=70, zoom=1.2), jam=0.25, snug=0.6)


@knot
def gassa_cima_doppia():
    """Gassa d'amante con cima doppia: la gassa fatta con il doppino della cima,
    che lascia due occhi (seggiolino del nostromo)."""
    P = BOW_HEAD + BOW_EYE + BOW_WORK
    P = [(x, y) for x, y in P]
    def offset(path, d):
        out = []
        for i, (x, y) in enumerate(path):
            a = path[max(i - 1, 0)]; b = path[min(i + 1, len(path) - 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]; n = np.hypot(tx, ty) or 1
            out.append((x - ty / n * d, y + tx / n * d))
        return out
    A = offset(P, -0.52)
    B = offset(P, 0.52)[::-1]
    path = A + [(B[0][0] + 0.2, B[0][1] - 1.0)] + B
    path = [(x, y) for x, y in path]
    R = flat_alt([path])
    return dict(ropes=R, pulls=[dict(rope=0, at=0, dir=[0, 1, 0], max=1.5), dict(rope=0, at=1, dir=[0, 1, 0], max=1.5)],
                props=[dict(type='cyl', c=[0, -1.4, 2.6], axis=[0, 0, 1], r=2.4, h=7.4, mat='wood', hidden=True)],
                view=dict(elev=70, zoom=1.05), jam=0.25, snug=0.5)


@knot
def gassa_con_rotonda():
    """Gassa d'amante con rotonda: la tana e' fatta con due asole (un parlato)
    e il coniglio passa in entrambe."""
    th = lambda a, dy=0, dx=0: (2.4 * np.cos(np.radians(a)) + dx, 6 + dy + 2.4 * np.sin(np.radians(a)))
    head = [(0.8, 21), (0.8, 15), (0.8, 13.4), (0.35, 11.6)]
    head += [th(a, 2.2, 0.0) for a in (120, 150, 180, 210, 240, 270, 300, 330, 0, 30, 60)]     # prima asola (in alto)
    head += [(-1.4, 11.1), (-0.6, 9.6)]
    head += [th(a) for a in (150, 180, 210, 240, 270, 300, 330, 0, 30, 60)]                      # seconda asola
    work = [(3.4, 2.4), (1.6, 2.6), (0.9, 3.3), (0.85, 5.5), (0.9, 7.5), (0.95, 10.0), (1.0, 12.3),
            (2.2, 13.2), (1.6, 14.4), (0, 14.7), (-1.4, 13.9), (-1.6, 12.6), (-1.0, 11.6),
            (-0.9, 9.0), (-0.9, 6.0), (-0.9, 3.0), (-0.75, 1.2)]
    pts = head + BOW_EYE + work
    marks = [(0.88, 3.8, 'U'), (-0.9, 3.75, 'U'), (0.75, 14.6, 'U')]
    R = flatm([pts], marks, tol=0.5, rule=lambda x, y, t: 'O')
    return dict(ropes=R, props=[dict(type='cyl', c=[0, -1.4, 2.6], axis=[0, 0, 1], r=2.0, h=7.4, mat='wood', cap=True)],
                pulls=[dict(rope=0, at=0, dir=[0, 1, 0], max=2.5), dict(rope=0, at=1, dir=[0, -1, 0], w=0.3, max=0.8)],
                view=dict(elev=70, zoom=1.4), jam=0.25, snug=0.6)


@knot
def incappellaggio_doppio():
    """Incappellaggio doppio: tre asole intrecciate attorno a un foro centrale
    (sulla testa di un albero di fortuna)."""
    pts = []
    for t in np.linspace(0.25, 4 * np.pi - 0.25, 150):
        r = 3.0 + 1.9 * np.cos(1.5 * t)
        pts.append((r * np.sin(t), r * np.cos(t)))
    a, b = pts[0], pts[-1]
    pts = [(a[0] + 4, a[1] - 7), (a[0] + 1.5, a[1] - 2)] + pts + [(b[0] - 1.5, b[1] - 2), (b[0] - 4, b[1] - 7)]
    R = flat_alt([pts])
    return dict(ropes=R, pulls=[dict(rope=0, at=0, dir=[1, -1, 0], max=1.0), dict(rope=0, at=1, dir=[-1, -1, 0], max=1.0)],
                view=dict(elev=75, zoom=1.2), snug=0.3)


# ---------------------------------------------------------------- arresti
@knot
def estar():
    """Arresto EStar: un'asola a nodo scorsoio con il capo che ci passa due volte, serrata in un blocco."""
    from knots_v3 import _multi_overhand
    pts, marks = _multi_overhand(2, pitch=1.12, R=1.45)
    pts = pts[:-3] + [(pts[-4][0] + 0.6, pts[-4][1] + 1.0), (-0.6, pts[-4][1] + 1.6), (-2.6, pts[-4][1] + 1.2), (-4.5, pts[-4][1] + 0.4)]
    R = flatm([pts], marks, default='O')
    return dict(ropes=R, pulls=[dict(rope=0, at=0, dir=[-1, 0, 0]), dict(rope=0, at=1, dir=[-1, 0.3, 0], w=0.4)],
                view=dict(zoom=1.4), snug=0.4)


@knot
def capestro():
    """Nodo per capestro: tre giri attorno al proprio dormiente formano un cappio scorrevole (qui su un moschettone)."""
    ring = dict(type='torus', c=[0, 0, 0], axis=[0, 0, 1], R=2.2, r=0.38, mat='steel')
    Rw = 0.88
    pts = [(-0.6, -18, Rw), (-0.6, -10, Rw), (-0.6, -3.6, Rw), (-0.6, -2.6, Rw)]
    for th in np.linspace(0, 330, 12)[1:]:
        pts.append((-0.6 + 1.2 * th / 330, -2.2 + Rw * np.sin(np.radians(th)), Rw * np.cos(np.radians(th))))
    pts += [(0.6, -3.4, 0.6), (0.4, -4.6, 0.9)]
    pts += vturn(60, 60 - 360 * 3, -4.8, -7.8, 1.05, ax=-0.6, az=Rw)               # tre giri sul dormiente
    pts += [(0.4, -8.0, Rw + 0.2), (0.0, -7.0, Rw - 0.05), (-0.2, -5.0, Rw - 0.1), (-0.25, -3.4, Rw), (0.1, -2.9, Rw + 1.0),
            (0.9, -4.2, Rw + 1.6), (1.4, -6.0, Rw + 1.5)]
    return dict(ropes=[rope3d(pts)], props=[ring],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0], max=1.0), dict(rope=0, at=1, dir=[0.3, -1, 0], w=0.3, max=0.4)],
                view=_sv(elev=10, az=-20, zoom=1.15, ground=-18.5), jam=0.25, snug=0.7)


# ------------------------------------------------------------- ancoraggi
def _bull(Rw=0.92):
    """Nodo di toro: come la bocca di lupo sull'anello, ma ogni lato fa una volta tonda."""
    ring = dict(type='torus', c=[0, 0, 0], axis=[0, 0, 1], R=2.4, r=0.42, mat='steel')
    yb = -2.4
    pts = [(-0.55, -16, Rw), (-0.55, -8, Rw), (-0.55, yb - 1.4, Rw)]
    pts += rturn(0, 720, -0.55, -2.4, Rw, y0=yb, bumps=[(720, 30, 1.0)])
    pts += [(-1.6, yb + 0.05, Rw + 1.0), (1.6, yb + 0.05, Rw + 1.0)]
    pts += rturn(720, 0, 2.4, 0.55, Rw, y0=yb, bumps=[(720, 30, 1.0)])
    pts += [(0.55, yb - 1.4, Rw), (0.55, -8, Rw), (0.55, -14, Rw)]
    return dict(ropes=[rope3d(pts)], props=[ring],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[0, -1, 0])],
                view=_sv(elev=10, az=-15, zoom=1.6, ground=-16.5), jam=0.25, snug=0.7)


@knot
def toro_estremita():
    return _bull()


@knot
def toro_doppino():
    return _bull()


@knot
def snuggle():
    """Nodo snuggle: un parlato con un giro in piu' e il capo infilato sotto i giri: tiene sotto carichi variabili."""
    pts = _clove_pts(x3=0.55)[:-3]
    Rw = 1.5
    pts += rturn(720, 1000, 0.55, 1.5, Rw)
    pts += [(1.4, 0.4, Rw + 0.05), (0.7, 1.4, Rw - 0.1), (0.1, 2.4, Rw), (-0.2, 4.0, Rw + 0.2), (-0.3, 8.0, Rw + 0.3)]
    return dict(ropes=[rope3d(pts)], props=[RAIL],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[0, 1, 0], w=0.3, max=0.5)],
                view=_sv(), jam=0.25, snug=0.7)


@knot
def icicle():
    """Nodo icicle: giri attorno al palo lontano dal carico, il capo torna sopra
    i giri, gira attorno al dormiente e si infila sotto se stesso."""
    pole = dict(type='cyl', c=[0, 0, 0], axis=[1, 0, 0], r=0.9, h=16, mat='wood')
    Rw = 1.4
    pts = [(-1.6, -14, Rw), (-1.6, -6, Rw), (-1.6, -1.5, Rw)]
    pts += rturn(0, 360 * 4, -1.6, 2.6, Rw)                                        # quattro giri verso destra
    pts += [(2.9, 0.5, Rw + 0.3), (2.2, 1.6, Rw + 0.9), (0.5, 1.8, Rw + 1.1), (-1.0, 1.2, Rw + 1.0)]   # torna sopra i giri
    pts += rturn(60, -260, -2.5, -2.2, Rw)                                          # attorno al palo e al dormiente
    pts += [(-2.0, -1.8, Rw + 0.9), (-1.6, -2.6, Rw + 1.0), (-1.2, -3.0, Rw - 0.2), (-0.8, -4.0, Rw + 0.2), (-0.7, -9.0, Rw + 0.3)]
    return dict(ropes=[rope3d(pts)], props=[pole],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[0, -1, 0], w=0.3, max=0.5)],
                view=_sv(), jam=0.25, snug=0.7)


@knot
def boma():
    """Nodo del boma: giri incrociati a X attorno al tubo e capo infilato sotto le X."""
    pts = _clove_pts(x0=-1.3, x1=1.6, x2=-1.6, x3=1.3)[:-3]
    Rw = 1.5
    pts += rturn(720, 840, 1.3, -0.2, Rw, bumps=[(780, 35, 1.9)])                   # seconda X sopra
    pts += rturn(840, 1080, -0.2, 0.3, Rw)
    pts += [(0.3, 1.0, Rw - 0.05), (0.0, 2.6, Rw + 0.1), (-0.3, 4.4, Rw + 0.3), (-0.5, 8.0, Rw + 0.3)]
    return dict(ropes=[rope3d(pts)], props=[RAIL],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[0, 1, 0], w=0.3, max=0.5)],
                view=_sv(), jam=0.25, snug=0.7)


@knot
def muli():
    """Nodo dei muli (mooring hitch): la cima passa sul tubo, forma un'asola
    attorno al dormiente e un doppino a sgancio rapido."""
    rail = line(-8, 6.0, 8, 6.0, 8)
    pts = [(0.0, -14), (0.0, -6), (0.0, 2.0), (0.0, 6.0), (0.4, 7.4), (0.9, 6.0), (0.9, 3.8),      # sale, passa sul tubo, scende
           (2.4, 2.4), (1.6, 0.6), (0.0, 0.3), (-1.4, 1.0), (-1.2, 2.3),                            # asola attorno al dormiente
           (0.1, 2.5), (1.4, 1.9), (0.9, 1.3), (-1.4, 1.6), (-4.0, 1.9), (-5.2, 1.4), (-4.0, 1.0),  # doppino verso sinistra
           (-1.4, 1.25), (1.6, 1.1), (3.4, 1.0), (5.0, 0.8)]
    R = flatm([pts, rail], [(0.0, 6.0, 'O'), (0.9, 6.0, 'U')], solid={1}, rule=lambda x, y, t: 'O' if t[0] < 0 else 'U')
    return dict(ropes=R, solid={1: 'iron'}, radii=[0.5, 0.8], colors=['second'],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0], max=1.5), dict(rope=0, at=1, dir=[1, 0, 0], w=0.3, max=0.5)],
                view=_sv(elev=12, az=-10, zoom=1.5, ground=-14), jam=0.25, snug=0.6)


@knot
def bandito():
    """Nodo del bandito: tre doppini infilati uno nell'altro dietro il tubo; tirando il capo si libera."""
    Rw = 1.5
    pts = [(-0.9, -12, Rw), (-0.9, -5, Rw), (-0.9, -1.6, Rw)]
    pts += rturn(0, 300, -0.9, -0.3, Rw)                                            # primo doppino dietro il tubo
    pts += [(-0.2, -1.4, Rw + 0.1), (0.4, 0.0, Rw + 0.9), (0.6, 2.4, Rw + 0.8)]      # secondo doppino davanti, nel primo
    pts += rturn(70, 290, 0.8, 1.1, Rw + 0.1)
    pts += [(1.1, -1.4, Rw + 0.3), (0.6, -0.4, Rw + 1.6), (0.2, 2.0, Rw + 1.6), (0.6, 3.2, Rw + 1.2),  # terzo doppino
            (1.0, 2.0, Rw + 1.9), (1.3, -0.8, Rw + 1.0), (1.6, -5.0, Rw + 0.4), (1.7, -11, Rw + 0.3)]
    return dict(ropes=[rope3d(pts)], props=[RAIL],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0], max=1.0), dict(rope=0, at=1, dir=[0, -1, 0], w=0.3, max=0.4)],
                view=_sv(), jam=0.25, snug=0.6)


# ------------------------------------------------------------ scotta a otto
@knot
def scotta_otto():
    """Nodo di scotta a otto: dopo il nodo di scotta il capo sottile torna
    indietro e si infila nel nodo, disegnando un otto."""
    red, marks = _wraps(1)
    red = red[:-2] + [(1.0, 1.75), (1.9, 1.2), (1.6, 0.2), (0.9, -0.1), (0.4, 0.9), (0.9, 3.0), (1.2, 6.0), (1.25, 8.5)]
    return _sheet(red, marks, default='U', view=dict(elev=60, zoom=1.3))


# ------------------------------------------------ versioni "vestite" (confronto con i riferimenti)
from knots_src import KNOTS as _K


def _barrel(n):
    """Nodo semplice multiplo vestito: il capo passa nel nucleo e le spire lo
    avvolgono n volte (botticella); i capi escono da parti opposte."""
    R = 1.08
    H = 1.05 * n
    pts = [(-0.38, -14, 0), (-0.38, -6, 0), (-0.38, -1.4, 0), (-0.38, 0.2, 0), (-0.38, H - 0.2, 0.1),
           (-0.2, H + 0.7, 0.6), (0.6, H + 0.6, 0.9)]
    pts += vturn(60, 60 + 360 * n, H, 0.0, R)
    pts += [(0.9, -0.7, 0.6), (0.38, -1.0, 0.0), (0.38, 0.2, 0.0), (0.38, H, 0.0), (0.38, H + 1.6, -0.1),
            (0.38, H + 6, -0.1), (0.38, H + 13, 0)]
    return dict(ropes=[rope3d(pts)], pulls=[dict(rope=0, at=0, dir=[0, -1, 0], max=1.0), dict(rope=0, at=1, dir=[0, 1, 0], max=1.0)],
                view=dict(mode='stand', elev=12, az=-20, zoom=1.25), jam=0.3, snug=0.6)


def _heaving(n, tail_down=False):
    """Fasciatura su un doppino (nodo per sagole da lancio, nodo Uli): spire
    regolari attorno ai due rami e capo infilato nell'asola in cima."""
    R = 1.25
    pts = [(-0.52, -16, 0), (-0.52, -6, 0), (-0.52, -0.5, 0), (-0.52, 1.05 * n + 1.0, 0),
           (0, 1.05 * n + 1.8, 0), (0.52, 1.05 * n + 1.0, 0), (0.52, -0.2, 0), (0.6, -1.0, 0.4), (1.2, -0.6, 0.7)]
    pts += vturn(60, 60 + 360 * n, -0.3, 1.05 * n - 0.3, R)
    top = 1.05 * n
    pts += [(1.1, top + 0.3, 0.8), (0.2, top + 0.9, 0.9), (0.0, top + 1.1, 0.0), (-0.1, top + 1.0, -0.9), (-1.0, top + 0.4, -1.2),
            (-1.8, top - 0.6, -1.0), (-2.4, top - 2.0, -0.6)]
    return dict(ropes=[rope3d(pts)], pulls=[dict(rope=0, at=0, dir=[0, -1, 0], max=0.6), dict(rope=0, at=1, dir=[-0.5, -1, 0], w=0.4, max=0.3)],
                view=dict(mode='stand', elev=12, az=-20, zoom=0.9), jam=0.3, snug=0.6)


_K['semplice-doppio'] = lambda: _barrel(2)
_K['semplice-multiplo'] = lambda: _barrel(4)
_K['uli'] = lambda: _heaving(10)
_K['sagole-da-lancio'] = lambda: _heaving(7)


def _briol():
    """Matassa di briol: spire a goccia appese, il capo fascia tutte le spire
    sotto il gancio e un doppino passa nell'occhio in alto."""
    top, H, W, n = 10.0, 9.0, 2.8, 5
    z0, dz = -2.2, 1.0
    pts = [(-0.4, -12, z0 - 0.6), (-0.3, -4, z0 - 0.4), (0.0, top - H, z0)]
    for t in np.linspace(np.pi, np.pi + 2 * np.pi * n, 30 * n)[1:]:
        s = ((1 - np.cos(t)) / 2) ** 0.55
        pts.append((W * np.sin(t) * s, top - H / 2 - (H / 2) * np.cos(t), z0 + dz * (t - np.pi) / (2 * np.pi)))
    zc = z0 + dz * n / 2
    zt = z0 + dz * n
    Rb = dz * n / 2 + 0.9
    pts += [(0.9, top - 0.8, zt + 0.4), (1.6, top - 1.6, zt + 0.6)]
    pts += vturn(60, 60 - 360 * 4, top - 1.8, top - 5.4, Rb, ax=0, az=zc)          # fasciatura sotto il gancio
    pts += [(0.6, top - 5.6, zc + Rb), (0.2, top - 3.0, zc + Rb + 0.7), (0.0, top - 1.2, zc + 0.8),     # doppino nell'occhio
            (0.0, top + 0.6, zc), (0.0, top - 0.9, zc - 0.9), (-0.3, top - 3.0, zc - Rb - 0.7), (-0.5, top - 6.5, zc - Rb - 0.5)]
    hook = dict(type='cyl', c=[0, top + 0.6, zc], axis=[0, 0, 1], r=0.6, h=9, mat='steel', deco=True)
    return dict(ropes=[rope3d(pts)], props=[hook], pulls=[],
                view=dict(mode='stand', elev=10, az=-30, zoom=0.8, ground=-12.5), snug=1.0)


_K['matassa-briol'] = _briol

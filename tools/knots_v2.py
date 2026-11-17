"""Nodario completo, parte 2: nodi disegnati come diagrammi 2D sopra/sotto,
con tubi, aste e anelli come elementi solidi (non si muovono, la cima li abbraccia)."""
import numpy as np
from geom import flat, line, circle
from knots_src import knot

RING = dict(R=3.0, r=0.42)


def ring_solid(cx=0.0, cy=6.0, R=3.0):
    return circle(cx, cy, R, n=48, a0=-90)


def stand_view(**kw):
    v = dict(mode='stand', elev=10, az=-15, zoom=1.4)
    v.update(kw)
    return v


@knot
def ancorotto():
    """Nodo d'ancorotto: volta tonda sull'anello, capo sotto i due giri,
    mezzo collo sul dormiente."""
    rope = [(-0.8, -12), (-0.8, -4), (-0.8, 1.2), (-0.8, 3.0), (-0.55, 3.95),           # dormiente sale davanti
            (-0.3, 3.0), (-0.02, 1.15),                                                   # dietro l'anello, sotto
            (0.25, 3.0), (0.5, 3.95), (0.75, 3.0), (1.05, 1.15),                          # secondo giro
            (0.3, 0.75), (-0.8, 0.7), (-1.7, 0.9), (-1.9, 1.7), (-1.4, 2.0),              # dietro il dormiente
            (-0.75, 2.0), (-0.18, 2.0), (0.12, 2.0), (0.9, 2.0), (1.9, 2.0),              # sotto i due giri
            (2.3, 1.2), (1.8, 0.3), (-0.8, 0.25), (-1.9, 0.05),                           # mezzo collo
            (-2.0, -0.5), (-0.8, -0.65), (0.5, -0.5), (0.75, 0.3), (1.25, 0.55)]
    R = flat([rope, ring_solid()], 'OUOOO' + 'UU' + 'OO' + 'UU' + 'U' + 'UOUO' + 'OO' + 'U' + 'U', solid={1})
    return dict(ropes=R, solid={1: 'steel'}, radii=[0.5, 0.42], colors=['main'],
                pulls=[dict(rope=0, at=0, dir=[0, -1, 0]), dict(rope=0, at=1, dir=[0.3, 1, 0], w=0.3, max=0.6)],
                view=stand_view(), jam=0.25, snug=0.8)

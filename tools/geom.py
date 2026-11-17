"""Aiuti per disegnare i percorsi dei nodi."""
import numpy as np
from ropesim import catmull, resample, lift, SP


def rope2d(pts, step=SP):
    return resample(catmull(pts), step)


def rope3d(pts, step=SP):
    return resample(catmull(pts), step)


def flat(ropes2d, seq, h=0.62, width=1.5):
    """ropes2d: lista di liste di punti (x,y). seq: sopra/sotto in ordine."""
    R = [rope2d(p) for p in ropes2d]
    return lift(R, seq, h=h, width=width)


def arc(c, r, a0, a1, n=8, z=0.0):
    """Arco nel piano xy (angoli in gradi)."""
    a = np.radians(np.linspace(a0, a1, n))
    return [(c[0] + r * np.cos(t), c[1] + r * np.sin(t), z) for t in a]


def helix(c, axis, r, a0, a1, pitch_per_turn, n=None, up=None):
    """Elica attorno a un asse ('x','y','z'); angoli in gradi; il passo e'
    lo spostamento lungo l'asse per giro completo."""
    if n is None:
        n = max(int(abs(a1 - a0) / 30), 3)
    a = np.radians(np.linspace(a0, a1, n))
    t = (np.linspace(a0, a1, n) - a0) / 360.0 * pitch_per_turn
    c = np.asarray(c, float)
    out = []
    for ang, s in zip(a, t):
        if axis == 'y':      # asse verticale: angolo 0 = davanti (+z)
            p = c + [r * np.sin(ang), s, r * np.cos(ang)]
        elif axis == 'x':    # asse orizzontale: angolo 0 = davanti (+z), 90 = sopra
            p = c + [s, r * np.sin(ang), r * np.cos(ang)]
        else:                # asse z: angolo 0 = destra, 90 = sopra
            p = c + [r * np.cos(ang), r * np.sin(ang), s]
        out.append(tuple(p))
    return out

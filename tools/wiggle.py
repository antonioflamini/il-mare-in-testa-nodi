"""Misura quanto e' "pulito" il percorso della cima nel fotogramma sciolto
(quello che la cima segue mentre il nodo si lega).

- giri: rotazione totale della tangente in giri (360 gradi = 1)
- ond: ondulazioni, cioe' inversioni di curvatura con ampiezza apprezzabile
  (le S inutili); un percorso pulito ne ha poche.
uso: python wiggle.py [id ...]"""
import json, os, sys
import numpy as np

P = os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'geom.json')


def metrics(P3, step=0.32):
    P3 = np.asarray(P3, float).reshape(-1, 3)
    d = np.linalg.norm(np.diff(P3, axis=0), axis=1)
    s = np.r_[0, np.cumsum(d)]
    t = np.linspace(0, s[-1], max(int(s[-1] / step), 8))
    Q = np.c_[[np.interp(t, s, P3[:, k]) for k in range(3)]].T
    T = np.diff(Q, axis=0); T /= np.linalg.norm(T, axis=1)[:, None] + 1e-9
    ang = np.arccos(np.clip((T[:-1] * T[1:]).sum(1), -1, 1))
    turns = ang.sum() / (2 * np.pi)
    # curvatura con segno nel piano di vista principale (xy): conta le inversioni
    cz = T[:-1, 0] * T[1:, 1] - T[:-1, 1] * T[1:, 0]
    k = np.convolve(cz, np.ones(5) / 5, mode='same')
    thr = 0.035
    sgn = np.where(k > thr, 1, np.where(k < -thr, -1, 0))
    sgn = sgn[sgn != 0]
    flips = int((np.diff(sgn) != 0).sum()) if len(sgn) > 1 else 0
    return turns, flips


def report(ids=None, path=P):
    db = json.load(open(path))
    rows = []
    for kid, g in db.items():
        if ids and kid not in ids:
            continue
        solid = g.get('solid') or {}
        T = F = 0
        for i, frames in enumerate(g['ropes']):
            if str(i) in solid:
                continue
            t, f = metrics(frames[0])
            T += t; F += f
        rows.append((kid, T, F))
    return rows


if __name__ == '__main__':
    rows = report(sys.argv[1:] or None)
    for kid, t, f in sorted(rows, key=lambda r: -r[2]):
        print(f'{kid:28s} giri {t:5.1f}   ondulazioni {f:3d}')
    print('TOTALE ondulazioni', sum(r[2] for r in rows))

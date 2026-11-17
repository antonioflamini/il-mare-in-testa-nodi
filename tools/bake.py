"""Cuoce la geometria dei nodi in app/data/geom.json.

uso:  python bake.py            (tutti i nodi)
      python bake.py gassa-damante savoia
"""
import json, sys, time, os
import numpy as np
from ropesim import Rope, resample
from knots_src import KNOTS
import knots_more  # noqa: F401  (registra gli altri nodi)

OUT = os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'geom.json')
EXPORT_STEP = 0.32


def extend(P, L0, ws, we):
    """Restituisce ai capi la cima "recuperata" durante il serraggio."""
    L = np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1))
    dfc = L0 - L
    if dfc <= 1e-3 or ws + we == 0:
        return P
    a = dfc * ws / (ws + we); b = dfc * we / (ws + we)
    d0 = P[0] - P[3]; d0 /= np.linalg.norm(d0)
    d1 = P[-1] - P[-4]; d1 /= np.linalg.norm(d1)
    pre = [P[0] + d0 * t for t in np.linspace(a, 0, max(int(a / 0.2), 1), endpoint=False)] if a > 0 else []
    post = [P[-1] + d1 * t for t in np.linspace(0, b, max(int(b / 0.2), 1) + 1)[1:]] if b > 0 else []
    return np.vstack([np.array(pre).reshape(-1, 3), P, np.array(post).reshape(-1, 3)])


def export_frames(frames, n_pts, L0, weights):
    """frames: lista (fotogrammi) di liste (cime). Ricampiona ogni cima a n
    punti fissi (stesso n in tutti i fotogrammi, per poter interpolare)."""
    out = []
    for ri in range(len(frames[0])):
        fr = []
        for f in frames:
            P = f[ri]
            s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
            t = np.linspace(0, s[-1], n_pts[ri])
            Q = np.c_[[np.interp(t, s, P[:, k]) for k in range(3)]].T
            fr.append([round(float(v), 3) for v in Q.ravel()])
        out.append(fr)
    return out


def bake(kid, verbose=False):
    spec = KNOTS[kid]()
    t0 = time.time()
    sim = Rope(spec['ropes'], spec.get('props', []), radii=spec.get('radii'))
    pen = sim.relax(iters=spec.get('relax_iters', 700), alpha=spec.get('relax_alpha', 0.04), verbose=verbose, fixed_rope=spec.get('fixed_rope'))
    g0 = sim.min_gap()
    res = sim.tighten(spec['pulls'], iters=spec.get('iters', 3000), step=spec.get('step', 0.025),
                      frames=spec.get('frames', 7), alpha=spec.get('alpha', 0.04),
                      pins=spec.get('pins', ()), jam=spec.get('jam', 0.08), snug=spec.get('snug', 0.55), verbose=verbose)
    frames = [f for f, k in res]
    sim.X = np.vstack(frames[-1]); g1 = sim.min_gap()
    lens = [float(np.sum(np.linalg.norm(np.diff(r, axis=0), axis=1))) for r in frames[0]]
    weights = []
    for ri in range(len(lens)):
        ws = sum(p.get('w', 1) for p in spec['pulls'] if p['rope'] == ri and p['at'] == 0)
        we = sum(p.get('w', 1) for p in spec['pulls'] if p['rope'] == ri and p['at'] == 1)
        weights.append((ws, we))
    n_pts = [max(int(L / EXPORT_STEP), 8) for L in lens]
    data = dict(
        ropes=export_frames(frames, n_pts, lens, weights),
        lengths=[round(L, 2) for L in lens],
        props=spec.get('props', []),
        view=spec.get('view', {}),
        colors=spec.get('colors', None),
        radii=spec.get('radii', None),
        reveal=spec.get('reveal', None),
    )
    print(f"{kid:28s} gap sciolto {g0:.2f}  gap stretto {g1:.2f}  pen {pen:.3f}  "
          f"punti {sum(n_pts)}  tirato {sim.moved}  {time.time() - t0:.1f}s", flush=True)
    if g0 < 0.9 or g1 < 0.88:
        print(f"   ATTENZIONE {kid}: compenetrazione possibile", flush=True)
    return data


def main():
    ids = sys.argv[1:] or list(KNOTS)
    verbose = '-v' in ids
    ids = [i for i in ids if i != '-v']
    db = {}
    if os.path.exists(OUT):
        with open(OUT, encoding='utf-8') as f:
            db = json.load(f)
    for kid in ids:
        db[kid] = bake(kid, verbose)
    db = {k: db[k] for k in KNOTS if k in db}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(db, f, separators=(',', ':'))
    print('scritto', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()

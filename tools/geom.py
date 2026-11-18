"""Aiuti per disegnare i percorsi dei nodi."""
import numpy as np
from ropesim import catmull, resample, lift, SP


def rope2d(pts, step=SP):
    return resample(catmull(pts), step)


def rope3d(pts, step=SP):
    return resample(catmull(pts), step)


def flat(ropes2d, seq, h=0.62, width=1.5, solid=()):
    """ropes2d: lista di liste di punti (x,y[,dz]). seq: sopra/sotto in ordine
    (solo per le cime: i solidi prendono il contrario in automatico)."""
    R = []
    for p in ropes2d:
        q = [(pt[0], pt[1], pt[2] if len(pt) > 2 else 0.0) for pt in p]
        R.append(rope3d(q))
    return lift(R, seq, h=h, width=width, solid=solid)


def line(x0, y0, x1, y1, n=6):
    return [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t) for t in np.linspace(0, 1, n)]


def circle(cx, cy, r, n=36, a0=90):
    a = np.radians(np.linspace(a0, a0 + 360, n + 1))
    return [(cx + r * np.cos(t), cy + r * np.sin(t)) for t in a]


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


def flatm(ropes2d, marks, solid=(), h=0.62, width=1.5, tol=0.9, default=None, rule=None):
    """Come flat(), ma gli incroci si annotano nel punto in cui avvengono:
    marks = [(x, y, 'O'|'U'[, rope])] -> «qui la cima <rope> passa sopra/sotto».
    Basta annotare uno dei due tratti di ogni incrocio; i solidi prendono il contrario.
    Se la cima incrocia se stessa, la marca vale per il tratto che arriva DOPO
    (quello che si sta legando in quel momento)."""
    from ropesim import find_crossings, arclen
    R = []
    for p in ropes2d:
        q = [(pt[0], pt[1], pt[2] if len(pt) > 2 else 0.0) for pt in p]
        R.append(rope3d(q))
    enc, xs = find_crossings(R)
    solid = set(solid)
    pos = []
    for (ra, sa), (rb, sb) in xs:
        P = R[ra]; i = min(np.searchsorted(arclen(P), sa), len(P) - 1)
        pos.append(P[i, :2])
    M = [(m[0], m[1], m[2], m[3] if len(m) > 3 else 0) for m in marks]
    used = set()
    letters = {}   # (rope, crossing) -> letter
    missing = []
    for c, ((ra, sa), (rb, sb)) in enumerate(xs):
        p = pos[c]
        best = None
        for k, (mx, my, L, mr) in enumerate(M):
            if mr not in (ra, rb):
                continue
            d = np.hypot(mx - p[0], my - p[1])
            if d < tol and (best is None or d < best[0]):
                best = (d, k)
        if best is None and rule is not None:
            P2 = R[rb]; s2 = arclen(P2); j = min(np.searchsorted(s2, sb), len(P2) - 2)
            tang = P2[j + 1, :2] - P2[j, :2]
            L = rule(p[0], p[1], tang)
            if L:
                M.append((p[0], p[1], L, rb)); best = (0, len(M) - 1)
        if best is None and default:
            M.append((p[0], p[1], default, rb)); best = (0, len(M) - 1)
        if best is None:
            missing.append((c, ra, rb, p.round(2)))
            continue
        k = best[1]; used.add(k)
        mx, my, L, mr = M[k]
        other = rb if mr == ra else ra
        if ra == rb:   # incrocio con se stessa: la marca vale per il tratto PIU' TARDO (quello che si sta legando)
            letters[(ra, c, 1)] = L; letters[(ra, c, 0)] = 'U' if L == 'O' else 'O'
        else:
            letters[(mr, c, 0 if mr == ra else 1)] = L
            letters[(other, c, 1 if mr == ra else 0)] = 'U' if L == 'O' else 'O'
    if missing:
        raise ValueError('incroci senza annotazione: ' + '; '.join(f'#{c} cime {a}/{b} in {p}' for c, a, b, p in missing))
    unused = [M[k][:2] for k in range(len(M)) if k not in used]
    if unused:
        print('  (annotazioni non usate:', unused, ')')
    out = []
    for ri, P in enumerate(R):
        P = P.copy()
        if ri not in solid:
            s_ = arclen(P)
            for c, ((ra, sa), (rb, sb)) in enumerate(xs):
                for side, (r, sc) in enumerate(((ra, sa), (rb, sb))):
                    if r != ri:
                        continue
                    L = letters[(ri, c, side)]
                    P[:, 2] += (1 if L == 'O' else -1) * h * np.exp(-((s_ - sc) / width) ** 2)
        out.append(P)
    return out


# ------------------------------------------------ eliche per i nodi d'ancoraggio
def rturn(a0, a1, x0, x1, R, bumps=(), n=None, y0=0.0, z0=0.0):
    """Giro attorno a un tubo orizzontale (asse x passante per y0, z0).
    Angolo 0 = davanti (+z), 90 = sopra (+y). bumps: (angolo, ampiezza, rialzo)
    per far passare questo tratto SOPRA altri giri."""
    out = []
    n = n or max(int(abs(a1 - a0) / 24), 3)
    for th in np.linspace(a0, a1, n + 1)[1:]:
        x = x0 + (x1 - x0) * (th - a0) / (a1 - a0)
        r = R + sum(h * np.exp(-((th - c) / w) ** 2) for c, w, h in bumps)
        t = np.radians(th)
        out.append((x, y0 + r * np.sin(t), z0 + r * np.cos(t)))
    return out


def vturn(a0, a1, y0, y1, R, ax=0.0, az=0.0, bumps=(), n=None):
    """Giro attorno a un asse verticale (palo o dormiente) in (ax, az).
    Angolo 0 = davanti (+z), 90 = destra (+x)."""
    out = []
    n = n or max(int(abs(a1 - a0) / 24), 3)
    for th in np.linspace(a0, a1, n + 1)[1:]:
        y = y0 + (y1 - y0) * (th - a0) / (a1 - a0)
        r = R + sum(h * np.exp(-((th - c) / w) ** 2) for c, w, h in bumps)
        t = np.radians(th)
        out.append((ax + r * np.sin(t), y, az + r * np.cos(t)))
    return out


def flat_alt(ropes2d, solid=(), h=0.62, width=1.5, start='O'):
    """Diagramma ALTERNATO: lungo la cima gli incroci si alternano sopra/sotto
    (come nelle trame dei tappeti e degli incappellaggi)."""
    from ropesim import find_crossings, lift
    R = [rope3d([(p[0], p[1], 0.0) for p in r]) for r in ropes2d]
    enc, xs = find_crossings(R)
    seq, cur = [], start
    for e in enc:
        if e[0] in solid:
            continue
        seq.append(cur); cur = 'U' if cur == 'O' else 'O'
    return lift(R, ''.join(seq), h=h, width=width, solid=solid)

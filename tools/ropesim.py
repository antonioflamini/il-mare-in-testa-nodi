"""Simulatore di cima per Il Mare in Testa - Nodi.

La cima e' una catena di particelle (diametro D = 1). Il simulatore:
  1. ricampiona il percorso disegnato a mano (spline Catmull-Rom),
  2. alza/abbassa i tratti agli incroci secondo la sequenza sopra/sotto,
  3. rilassa la cima finche' nessun tratto compenetra un altro o un oggetto,
  4. "stringe" il nodo tirando i capi (position based dynamics) e salva
     alcuni fotogrammi intermedi, cosi' l'app mostra la cima che si serra.
Nessun tratto puo' attraversarne un altro: ogni passo e' piu' piccolo del raggio.
"""
import math
import numpy as np

D = 1.0          # diametro della cima
SP = 0.22        # passo tra le particelle


# ---------------------------------------------------------------- spline
def catmull(pts, samples=24):
    P = np.asarray(pts, float)
    if P.shape[1] == 2:
        P = np.c_[P, np.zeros(len(P))]
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        # centripeta
        def tj(ti, a, b):
            return ti + max(np.linalg.norm(b - a), 1e-6) ** 0.5
        t0 = 0; t1 = tj(t0, p0, p1); t2 = tj(t1, p1, p2); t3 = tj(t2, p2, p3)
        for t in np.linspace(t1, t2, samples, endpoint=False):
            a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
            a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
            b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
            b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3
            out.append((t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2)
    out.append(P[-2])
    return np.array(out)


def resample(P, step):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.r_[0, np.cumsum(seg)]
    n = max(int(round(s[-1] / step)), 2)
    t = np.linspace(0, s[-1], n + 1)
    return np.c_[[np.interp(t, s, P[:, k]) for k in range(3)]].T


def arclen(P):
    return np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]


# ------------------------------------------------- incroci sopra / sotto
def _seg_inter(a, b, c, d):
    r = b - a; s = d - c
    den = r[0] * s[1] - r[1] * s[0]
    if abs(den) < 1e-12:
        return None
    q = c - a
    t = (q[0] * s[1] - q[1] * s[0]) / den
    u = (q[0] * r[1] - q[1] * r[0]) / den
    if 0 <= t < 1 and 0 <= u < 1:
        return t, u
    return None


def find_crossings(ropes):
    """Incroci nella proiezione xy. Restituisce lista di incontri in ordine di
    percorrenza: (rope, s_arc, crossing_id)."""
    segs = []
    for ri, P in enumerate(ropes):
        s = arclen(P)
        for i in range(len(P) - 1):
            segs.append((ri, i, P[i, :2], P[i + 1, :2], s[i], s[i + 1]))
    xs = []
    for a in range(len(segs)):
        ra, ia, p0, p1, sa0, sa1 = segs[a]
        lo = np.minimum(p0, p1); hi = np.maximum(p0, p1)
        for b in range(a + 2, len(segs)):
            rb, ib, q0, q1, sb0, sb1 = segs[b]
            if ra == rb and ib - ia < 2:
                continue
            if (np.minimum(q0, q1) > hi).any() or (np.maximum(q0, q1) < lo).any():
                continue
            r = _seg_inter(p0, p1, q0, q1)
            if r:
                t, u = r
                xs.append(((ra, sa0 + t * (sa1 - sa0)), (rb, sb0 + u * (sb1 - sb0))))
    enc = []
    for cid, (e1, e2) in enumerate(xs):
        enc.append((e1[0], e1[1], cid))
        enc.append((e2[0], e2[1], cid))
    enc.sort(key=lambda e: (e[0], e[1]))
    return enc, xs


def lift(ropes, seq, h=0.62, width=1.5, solid=()):
    """Applica la sequenza 'OUOU...' agli incontri in ordine di percorrenza.
    Gli incontri sulle cime 'solid' (tubi, aste, anelli) non vanno nella
    sequenza: prendono automaticamente il contrario della cima che li incrocia,
    e i solidi restano dritti (z = 0)."""
    solid = set(solid)
    enc, xs = find_crossings(ropes)
    seq = seq.replace(' ', '')
    live = [k for k, e in enumerate(enc) if e[0] not in solid]
    if len(live) != len(seq):
        msg = [f"incontri (cime) trovati {len(live)} ma sequenza lunga {len(seq)}"]
        for n, k in enumerate(live):
            r, s_, c = enc[k]
            P = ropes[r]; i = np.searchsorted(arclen(P), s_)
            msg.append(f"  #{n} rope{r} s={s_:.1f} xy={P[min(i, len(P)-1), :2].round(1)} incrocio {c}")
        raise ValueError(chr(10).join(msg))
    letter = {}
    for n, k in enumerate(live):
        letter[k] = seq[n]
    seen = {}
    for k in live:
        c = enc[k][2]
        if c in seen and seen[c] == letter[k]:
            raise ValueError(f"incrocio {c} ha due '{letter[k]}'")
        seen[c] = letter[k]
    out = []
    for ri, P in enumerate(ropes):
        P = P.copy()
        if ri not in solid:
            s_ = arclen(P)
            for k in live:
                r, sc, c = enc[k]
                if r != ri:
                    continue
                sign = 1 if letter[k] == 'O' else -1
                P[:, 2] += sign * h * np.exp(-((s_ - sc) / width) ** 2)
        out.append(P)
    return out


# ------------------------------------------------------------- oggetti
class Prop:
    """Oggetti solidi attorno a cui si lega: cilindri e tori."""
    def __init__(self, spec):
        self.s = spec
        self.kind = spec['type']

    def push(self, X, rad):
        s = self.s
        if self.kind == 'cyl':
            c = np.array(s['c'], float); a = np.array(s['axis'], float); a /= np.linalg.norm(a)
            v = X - c; t = v @ a
            radial = v - np.outer(t, a); rn = np.linalg.norm(radial, axis=1) + 1e-9
            rad = np.broadcast_to(np.asarray(rad, float).reshape(-1), (len(X),)) if np.ndim(rad) else np.full(len(X), rad)
            inside_len = np.abs(t) <= s['h'] / 2 + rad * 0.3
            need = s['r'] + rad
            m = inside_len & (rn < need)
            X[m] += radial[m] / rn[m, None] * (need[m] - rn[m])[:, None]
        elif self.kind == 'torus':
            c = np.array(s['c'], float); a = np.array(s['axis'], float); a /= np.linalg.norm(a)
            v = X - c; t = v @ a
            radial = v - np.outer(t, a); rn = np.linalg.norm(radial, axis=1) + 1e-9
            ring = radial / rn[:, None] * s['R']
            w = v - ring; wn = np.linalg.norm(w, axis=1) + 1e-9
            rad = np.broadcast_to(np.asarray(rad, float).reshape(-1), (len(X),)) if np.ndim(rad) else np.full(len(X), rad)
            need = s['r'] + rad
            m = wn < need
            X[m] += w[m] / wn[m, None] * (need[m] - wn[m])[:, None]
        elif self.kind == 'box':
            rad = np.full(len(X), rad) if not np.ndim(rad) else np.asarray(rad, float).reshape(-1)
            c = np.array(s['c'], float)
            hs = np.array(s['size'], float)[None, :] / 2 + rad[:, None]
            v = X - c
            m = (np.abs(v) < hs).all(axis=1)
            if m.any():
                pen = hs[m] - np.abs(v[m])
                k = np.argmin(pen, axis=1)
                idx = np.where(m)[0]
                ar = np.arange(len(k))
                X[idx, k] += np.sign(v[m][ar, k] + 1e-9) * pen[ar, k]
        elif self.kind == 'plane':  # pavimento/coperta
            y0 = s['y']
            rad = np.full(len(X), rad) if not np.ndim(rad) else np.asarray(rad, float).reshape(-1)
            m = X[:, 1] < y0 + rad
            X[m, 1] = (y0 + rad)[m]
        return X


# ---------------------------------------------------------- simulatore
class Rope:
    def __init__(self, ropes, props=(), gap=1.02, radii=None):
        self.ropes = [np.asarray(r, float) for r in ropes]
        self.radii = list(radii) if radii else [D / 2] * len(self.ropes)
        self.props = [Prop(p) for p in props if not p.get('deco')]
        self.gap = gap
        self._build()

    def _build(self):
        self.X = np.vstack(self.ropes)
        self.rid = np.concatenate([np.full(len(r), i) for i, r in enumerate(self.ropes)])
        self.idx = np.concatenate([np.arange(len(r)) for r in self.ropes])
        self.start = np.cumsum([0] + [len(r) for r in self.ropes])[:-1]
        self.rest = []
        for r in self.ropes:
            self.rest.append(np.linalg.norm(np.diff(r, axis=0), axis=1))
        self.restc = np.concatenate(self.rest)
        self.segA = np.concatenate([np.arange(len(r) - 1) + st for r, st in zip(self.ropes, self.start)])
        self.segB = self.segA + 1
        self.rad = np.concatenate([np.full(len(r), rr) for r, rr in zip(self.ropes, self.radii)])
        self.skip_r = np.ceil(1.6 * 2 * np.array(self.radii) / SP).astype(int)
        self.skip = int(self.skip_r.max())
        self.pairs = None

    def _refresh_pairs(self, radius=2.6):
        X = self.X; n = len(X)
        d2 = ((X[:, None, :] - X[None, :, :]) ** 2).sum(-1)
        iu = np.triu_indices(n, 1)
        m = d2[iu] < radius ** 2
        a, b = iu[0][m], iu[1][m]
        same = self.rid[a] == self.rid[b]
        far = np.abs(self.idx[a] - self.idx[b]) > self.skip_r[self.rid[a]]
        keep = ~same | far
        sol = getattr(self, 'solid', [])
        if sol:
            iss = np.isin(self.rid[a], sol)
            keep &= ~(same & iss)           # un solido non urta se stesso
            keep &= ~(iss & np.isin(self.rid[b], sol))
        self.pairs = (a[keep], b[keep])

    def collide(self, X, mobile):
        a, b = self.pairs
        if len(a) == 0:
            return 0.0
        v = X[a] - X[b]; d = np.linalg.norm(v, axis=1) + 1e-9
        pen = self.gap * (self.rad[a] + self.rad[b]) - d
        m = pen > 0
        if not m.any():
            return 0.0
        a, b, v, d, pen = a[m], b[m], v[m], d[m], pen[m]
        corr = v / d[:, None] * (pen / 2)[:, None]
        acc = np.zeros_like(X); cnt = np.zeros(len(X))
        np.add.at(acc, a, corr); np.add.at(acc, b, -corr)
        np.add.at(cnt, a, 1); np.add.at(cnt, b, 1)
        cnt = np.maximum(cnt, 1)
        X += acc / cnt[:, None] * 0.9 * mobile[:, None]
        return pen.max()

    def lengths(self, X, mobile, k=1.0):
        a, b = self.segA, self.segB
        v = X[b] - X[a]; d = np.linalg.norm(v, axis=1) + 1e-9
        diff = (d - self.restc) / d
        wa = mobile[a]; wb = mobile[b]; w = wa + wb + 1e-9
        corr = v * (diff * k)[:, None]
        acc = np.zeros_like(X)
        np.add.at(acc, a, corr * (wa / w)[:, None])
        np.add.at(acc, b, -corr * (wb / w)[:, None])
        X += acc

    def bend(self, X, mobile, rb=0.75, k=3):
        """Raggio minimo di curvatura: la corda tra i-k e i+k non puo' essere
        piu' corta di quella di un arco di raggio rb."""
        s = 2 * k * SP
        cmin = 2 * rb * np.sin(min(s / (2 * rb), np.pi / 2))
        for st, r, rr in zip(self.start, self.ropes, self.radii):
            n = len(r)
            if n <= 2 * k:
                continue
            cmin = 2 * rb * rr / 0.5 * np.sin(min(s / (2 * rb * rr / 0.5), np.pi / 2))
            A = X[st:st + n - 2 * k]; B = X[st + 2 * k:st + n]
            v = B - A; d = np.linalg.norm(v, axis=1) + 1e-9
            m = d < cmin
            if not m.any():
                continue
            corr = v / d[:, None] * ((cmin - d) / 2 * m)[:, None] * 0.5
            ma = mobile[st:st + n - 2 * k, None]; mb = mobile[st + 2 * k:st + n, None]
            X[st:st + n - 2 * k] -= corr * ma
            X[st + 2 * k:st + n] += corr * mb

    def smooth(self, X, mobile, alpha):
        if alpha <= 0:
            return
        for st, r in zip(self.start, self.ropes):
            n = len(r)
            sl = slice(st + 1, st + n - 1)
            lap = 0.5 * (X[st:st + n - 2] + X[st + 2:st + n]) - X[sl]
            X[sl] += alpha * lap * mobile[sl, None]

    def props_push(self, X):
        for p in self.props:
            X[:] = p.push(X, self.rad[:, None] * 1.02)

    def stretch(self):
        d = np.linalg.norm(self.X[self.segB] - self.X[self.segA], axis=1)
        return (d / self.restc).max()

    def stretch_total(self):
        d = np.linalg.norm(self.X[self.segB] - self.X[self.segA], axis=1)
        return d.sum() / self.restc.sum()

    def min_gap(self):
        self._refresh_pairs(1.5)
        a, b = self.pairs
        if len(a) == 0:
            return 9.0
        return (np.linalg.norm(self.X[a] - self.X[b], axis=1) / (self.rad[a] + self.rad[b])).min()

    def relax(self, iters=600, alpha=0.05, verbose=False, fixed_rope=None):
        mobile = np.ones(len(self.X))
        for fr in ([fixed_rope] if isinstance(fixed_rope, int) else (fixed_rope or [])):
            mobile[self.rid == fr] = 0.0
        for it in range(iters):
            if it % 8 == 0:
                self._refresh_pairs()
            prev = self.X.copy()
            for _ in range(3):
                pen = self.collide(self.X, mobile)
                self.props_push(self.X)
                self.lengths(self.X, mobile)
                self.bend(self.X, mobile)
            self.smooth(self.X, mobile, alpha)
            self._clamp(prev)
            if it % 50 == 0 and verbose:
                print('relax', it, 'pen', round(pen, 3))
            if it > 60 and pen < 0.01:
                break
        self._x0 = self.X.copy()
        return pen

    def _clamp(self, prev, maxstep=0.12):
        dv = self.X - prev; n = np.linalg.norm(dv, axis=1)
        m = n > maxstep
        self.X[m] = prev[m] + dv[m] / n[m, None] * maxstep

    def particle(self, rope, at):
        n = len(self.ropes[rope])
        return self.start[rope] + int(round(at * (n - 1)))

    # ------------------------------------------------ trazione (FABRIK)
    def _chain_pass(self, X, rope, targets):
        """Passate indietro/avanti su una cima con punti fissi (indici locali)."""
        st = self.start[rope]; n = len(self.ropes[rope])
        rest = self.rest[rope]
        L = X[st:st + n].tolist()
        sqrt = math.sqrt

        def place(i, j):          # porta i a distanza rest da j
            a = L[i]; b = L[j]
            dx = a[0] - b[0]; dy = a[1] - b[1]; dz = a[2] - b[2]
            d = sqrt(dx * dx + dy * dy + dz * dz) or 1e-9
            r = rest[i if i < j else j] / d
            L[i] = [b[0] + dx * r, b[1] + dy * r, b[2] + dz * r]
        fx = sorted(targets)
        for k in fx:
            L[k] = list(targets[k])
        for i in range(fx[0] - 1, -1, -1):
            place(i, i + 1)
        for i in range(fx[-1] + 1, n):
            place(i, i - 1)
        for a_, b_ in zip(fx[:-1], fx[1:]):
            for i in range(b_ - 1, a_, -1):
                place(i, i + 1)
            for i in range(a_ + 1, b_):
                place(i, i - 1)
        X[st:st + n] = np.array(L)
        res = 0.0
        for a_, b_ in zip(fx[:-1], fx[1:]):
            d = np.linalg.norm(X[st + b_] - X[st + b_ - 1])
            res = max(res, abs(d - rest[b_ - 1]))
        return res

    def penetration(self):
        a, b = self.pairs
        if len(a) == 0:
            return 0.0
        d = np.linalg.norm(self.X[a] - self.X[b], axis=1)
        pr = max(0.0, (self.gap * (self.rad[a] + self.rad[b]) - d).max())
        for p in self.props:
            Y = self.X.copy(); p.push(Y, self.rad[:, None])
            pr = max(pr, np.linalg.norm(Y - self.X, axis=1).max())
        return pr

    def tighten(self, pulls, iters=3000, step=0.025, frames=7, alpha=0.04,
                pins=(), verbose=False, jam=0.08, **_):
        """Serra il nodo tirando i capi indicati (e tenendo fermi i 'pins').
        Un capo smette di muoversi quando la cima non arriva piu' (nodo serrato)."""
        self.jam = jam
        self.snug = _.get('snug', 0.55)
        P = []
        for p in list(pulls) + [dict(q, dir=[0, 0, 0], w=0) for q in pins]:
            d = np.array(p['dir'], float); nd = np.linalg.norm(d)
            d = d / nd if nd else d
            i = int(round(p['at'] * (len(self.ropes[p['rope']]) - 1)))
            P.append(dict(rope=p['rope'], i=i, d=d, w=p.get('w', 1.0), active=nd > 0,
                          maxd=p.get('max', 1e9), moved=0.0, hold=0,
                          pos=self.X[self.start[p['rope']] + i].copy()))
        by_rope = {}
        for p in P:
            by_rope.setdefault(p['rope'], []).append(p)
        mobile = np.ones(len(self.X))
        for fr in getattr(self, 'solid', []):
            mobile[self.rid == fr] = 0.0
        for p in P:
            mobile[self.start[p['rope']] + p['i']] = 0

        def passes():
            w = {}
            for r, lst in by_rope.items():
                w[r] = self._chain_pass(self.X, r, {p['i']: p['pos'] for p in lst})
            return w
        hist = []
        for it in range(iters):
            if it % 5 == 0:
                self._refresh_pairs()
            prev = self.X.copy()
            for p in P:
                if p['active']:
                    p['pos'] = p['pos'] + p['d'] * step * p['w']
                    p['moved'] += step * p['w']
            for sub in range(3):
                passes()
                self.bend(self.X, mobile)
                self.collide(self.X, mobile)
                self.props_push(self.X)
            self.smooth(self.X, mobile, alpha)
            worst = passes()
            pen = self.penetration()
            self.collide(self.X, mobile); self.props_push(self.X)
            self._clamp(prev, 0.15)
            self.props_push(self.X)          # mai dentro un oggetto, nemmeno dopo il limite di passo
            stretch = self.stretch_total()
            jam = pen > self.jam or stretch > 1.02
            for p in P:
                if not p['active']:
                    continue
                if jam:
                    p['hold'] += 1
                    p['pos'] = p['pos'] - p['d'] * step * p['w']
                    p['moved'] -= step * p['w']
                    if p['hold'] > 25:
                        p['active'] = False
                else:
                    p['hold'] = max(0, p['hold'] - 1)
                if p['moved'] >= p['maxd']:
                    p['active'] = False
            hist.append(self.X.copy())
            if verbose and it % 200 == 0:
                print('tighten', it, 'pen', round(pen, 3), 'str', round(stretch, 3), 'mossi', [round(p['moved'], 1) for p in P if p['w']],
                      'res', {k: round(v, 3) for k, v in worst.items()})
            if not any(p['active'] for p in P):
                break
        for it in range(200):           # assestamento: elimina ogni compenetrazione
            if it % 5 == 0:
                self._refresh_pairs()
            prev = self.X.copy()
            for k in range(4):
                self.lengths(self.X, mobile)
                self.bend(self.X, mobile)
                self.collide(self.X, mobile); self.props_push(self.X)
            self.smooth(self.X, mobile, alpha * 0.3)
            self._clamp(prev, 0.1); self.props_push(self.X)
        hist.append(self.X.copy())
        self.moved = [round(p['moved'], 2) for p in P if p['w']]
        disp = np.array([0] + [np.abs(hist[k] - hist[k - 1]).sum() for k in range(1, len(hist))])
        cum = np.cumsum(disp); cum = cum / cum[-1] if cum[-1] > 0 else cum
        snug = self.snug
        picks = [int(min(np.searchsorted(cum, snug * f / (frames - 1)), len(hist) - 1)) for f in range(1, frames)]
        out = [(self.split(self._x0), 0)]
        for k in picks:
            out.append((self.split(hist[k]), k))
        return out

    def split(self, X=None):
        X = self.X if X is None else X
        return [X[st:st + len(r)].copy() for st, r in zip(self.start, self.ropes)]

"""Disegna la linea d'asse dei fotogrammi (vista dall'alto) per controllo rapido."""
import json, sys, numpy as np
from PIL import Image, ImageDraw
g = json.load(open('app/data/geom.json'))[sys.argv[1]]
frames = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [0, len(g['ropes'][0]) - 1]
W = 520
im = Image.new('RGB', (W * len(frames), W), 'white'); dr = ImageDraw.Draw(im)
allp = np.vstack([np.array(f).reshape(-1, 3) for r in g['ropes'] for f in r])
lo, hi = allp[:, :2].min(0), allp[:, :2].max(0)
sc = (W - 40) / (hi - lo).max()
cols = [(20, 40, 90), (200, 70, 30), (200, 160, 30)]
for k, fi in enumerate(frames):
    for ri, r in enumerate(g['ropes']):
        P = np.array(r[fi]).reshape(-1, 3)
        z = P[:, 2]
        for i in range(len(P) - 1):
            x0, y0 = (P[i, :2] - lo) * sc + 20; x1, y1 = (P[i + 1, :2] - lo) * sc + 20
            c = cols[ri]; t = np.clip((z[i] + 1.5) / 3, 0, 1)
            c = tuple(int(cc * (0.4 + 0.6 * t) + 255 * (1 - t) * 0.5) for cc in c)
            dr.line([(x0 + k * W, W - y0), (x1 + k * W, W - y1)], fill=c, width=max(2, int(sc * 0.9)))
    dr.text((k * W + 8, 8), f'frame {fi}', fill='black')
im.save(sys.argv[2])

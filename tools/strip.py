"""Striscia di fotogrammi di un nodo (per giudicare l'animazione).
uso: python strip.py out.png id [g1,g2,...] [--bg deck]"""
import sys, os, tempfile
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw
from shot import shot
a = sys.argv[1:]
bg = 'studio'
if '--bg' in a:
    i = a.index('--bg'); bg = a[i + 1]; del a[i:i + 2]
out, kid = a[0], a[1]
gs = [float(x) for x in (a[2].split(',') if len(a) > 2 else '0.15,0.3,0.45,0.6,0.75,0.9,1.0,1.35'.split(','))]
tmp = tempfile.mkdtemp(); W, H = 360, 300
def one(g):
    p = os.path.join(tmp, f'{g}.png'); shot(kid, g, p, W, H, bg); return p
with ThreadPoolExecutor(4) as ex:
    paths = list(ex.map(one, gs))
s = Image.new('RGB', (W * 4, H * ((len(gs) + 3) // 4)), 'white'); d = ImageDraw.Draw(s)
for i, (g, p) in enumerate(zip(gs, paths)):
    im = Image.open(p).convert('RGBA'); b = Image.new('RGBA', im.size, (240, 238, 232, 255)); b.alpha_composite(im)
    s.paste(b.convert('RGB'), ((i % 4) * W, (i // 4) * H)); d.text(((i % 4) * W + 6, (i // 4) * H + 6), f'g={g}', fill='black')
s.save(out); print('ok')

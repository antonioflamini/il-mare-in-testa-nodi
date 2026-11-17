"""Rende piu' nodi e li monta in un foglio di controllo.
uso: python sheet.py out.png g id1 id2 ... [--bg paper]"""
import sys, os, tempfile
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw
from shot import shot
args = sys.argv[1:]
bg = 'deck'
if '--bg' in args:
    i = args.index('--bg'); bg = args[i + 1]; del args[i:i + 2]
out, g, ids = args[0], args[1], args[2:]
tmp = tempfile.mkdtemp()
W, H = 640, 520
def one(k):
    p = os.path.join(tmp, k + '.png'); shot(k, g, p, W, H, bg); return p
with ThreadPoolExecutor(3) as ex:
    paths = list(ex.map(one, ids))
cols = 3; rows = (len(ids) + cols - 1) // cols
sheet = Image.new('RGB', (W * cols, H * rows), 'white')
d = ImageDraw.Draw(sheet)
for i, (k, p) in enumerate(zip(ids, paths)):
    im = Image.open(p).convert('RGBA')
    bgc = Image.new('RGBA', im.size, (245, 243, 238, 255)); bgc.alpha_composite(im)
    sheet.paste(bgc.convert('RGB'), ((i % cols) * W, (i // cols) * H))
    d.text(((i % cols) * W + 10, (i // cols) * H + 10), k, fill='black')
sheet.save(out)
print('ok', out)

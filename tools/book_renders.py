"""Illustrazioni del libro: per ogni nodo l'immagine finale e i passaggi (fondo bianco)."""
import os, re, json
from concurrent.futures import ThreadPoolExecutor
from shot import shot
ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'book', 'img')
src = open(os.path.join(ROOT, 'app', 'data', 'knots.js'), encoding='utf-8').read()
jobs = []
for block in re.split(r"\n  \{\n", src)[1:]:
    kid = re.search(r"id: '([^']+)'", block).group(1)
    ats = [float(x) for x in re.findall(r"\{ at: ([0-9.]+), t:", block)]
    jobs.append((kid, 1.35, f'{kid}_final.png', 1500, 1150))
    for i, a in enumerate(ats):
        nxt = ats[i + 1] if i + 1 < len(ats) else 1.35
        g = 1.35 if a >= 1 else min(1.0, nxt)      # il nodo come appare alla fine del passo
        jobs.append((kid, g, f'{kid}_p{i + 1}.png', 700, 560))
def run(j):
    kid, g, name, w, h = j
    p = os.path.join(OUT, name)
    if '_final' not in name or not os.path.exists(p):   # i passi si rifanno sempre
        shot(kid, g, p, w, h, 'paper')
    return name
with ThreadPoolExecutor(3) as ex:
    for n in ex.map(run, jobs):
        print(n, flush=True)

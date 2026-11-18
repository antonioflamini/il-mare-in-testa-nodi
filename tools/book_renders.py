"""Illustrazioni del libro: per ogni nodo l'immagine finale e i passaggi (fondo bianco).
Legge book/knots.json (esportato dall'app con tools/export.html)."""
import os, json
from concurrent.futures import ThreadPoolExecutor
from shot import shot
ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'book', 'img')
os.makedirs(OUT, exist_ok=True)
D = json.load(open(os.path.join(ROOT, 'book', 'knots.json'), encoding='utf-8'))
jobs = []
for n in D['NODI']:
    kid = n['id']; ats = [p['at'] for p in n['passi']]
    jobs.append((kid, 1.35, f'{kid}_final.png', 1500, 1150))
    for i, a in enumerate(ats):
        nxt = ats[i + 1] if i + 1 < len(ats) else 1.35
        g = 1.35 if a >= 1 else min(1.0, nxt)      # il nodo come appare alla fine del passo
        jobs.append((kid, g, f'{kid}_p{i + 1}.png', 700, 560))
LOG = os.path.join(ROOT, 'book', 'renders.log')
DONE = set(open(LOG, encoding='utf-8').read().split()) if os.environ.get('RESUME') and os.path.exists(LOG) else set()


def run(j):
    kid, g, name, w, h = j
    if name in DONE:
        return name
    shot(kid, g, os.path.join(OUT, name), w, h, 'paper')
    return name
with ThreadPoolExecutor(3) as ex:
    for n in ex.map(run, jobs):
        print(n, flush=True)

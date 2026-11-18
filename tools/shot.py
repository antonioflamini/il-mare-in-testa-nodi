"""Render headless di un nodo con Edge -> PNG.
uso: python shot.py <id> <g> <out.png> [w] [h] [bg] [querystring extra]"""
import sys, subprocess, base64, re, os, tempfile, shutil
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
def shot(kid, g, out, w=900, h=700, bg='deck', extra='', tries=3):
    for t in range(tries):
        try:
            return _shot(kid, g, out, w, h, bg, extra)
        except SystemExit:
            if t == tries - 1:
                raise


def _shot(kid, g, out, w=900, h=700, bg='deck', extra=''):
    ud = tempfile.mkdtemp(prefix='edge-shot-')
    url = f"http://127.0.0.1:8771/app/render.html?k={kid}&g={g}&bg={bg}{extra}"
    r = subprocess.run([EDGE, '--headless=new', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
                        '--hide-scrollbars', f'--window-size={w},{h}', '--virtual-time-budget=30000',
                        f'--user-data-dir={ud}', '--dump-dom', url], capture_output=True, text=True, timeout=180)
    shutil.rmtree(ud, ignore_errors=True)
    m = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', r.stdout)
    if not m:
        raise SystemExit(f'nessuna immagine per {kid}')
    with open(out, 'wb') as f:
        f.write(base64.b64decode(m.group(1)))
    return out
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('id'); ap.add_argument('g'); ap.add_argument('out')
    ap.add_argument('--w', type=int, default=900); ap.add_argument('--h', type=int, default=700)
    ap.add_argument('--bg', default='deck'); ap.add_argument('--q', default='')
    a = ap.parse_args()
    shot(a.id, a.g, a.out, a.w, a.h, a.bg, a.q)

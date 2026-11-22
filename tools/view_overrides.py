"""Regolazioni d'inquadratura per la vista frontale "studio" (applicate da bake.py e da apply_views)."""
VIEWS = {
    'bozza': dict(zoom=2.1), 'galloccia': dict(zoom=1.0), 'volta-tonda': dict(zoom=1.05), 'scotta-tre-vie': dict(zoom=1.4), 'incappellaggio-doppio': dict(zoom=0.8),
    'fiocco-fiammingo': dict(zoom=0.85),
    'stopper-ashley': dict(zoom=0.85), 'estar': dict(zoom=0.85), 'semplice-doppio': dict(zoom=2.0),
    'portoghese': dict(zoom=0.8), 'broach': dict(zoom=0.8), 'stretta-di-mano': dict(zoom=0.8), 'barcaiolo-doppino': dict(zoom=1.1),
    'brancarella': dict(zoom=0.85), 'per-sacchi': dict(zoom=1.1), 'intugliatura-due-gasse': dict(zoom=1.05),
    'clara': dict(zoom=0.8), 'clara-aggrappante': dict(zoom=0.8), 'regina-clara': dict(zoom=0.75), 'grande-regina-clara': dict(zoom=0.7),
    'sollevamento': dict(zoom=1.1), 'toro-estremita': dict(zoom=1.1), 'toro-doppino': dict(zoom=1.1), 'volta-di-bitta': dict(zoom=1.0),
    'gasse-collegate': dict(zoom=0.85), 'gassa-con-rotonda': dict(zoom=0.85), 'drago-doppio': dict(zoom=0.85),
}


def apply(db):
    for k, v in VIEWS.items():
        if k in db:
            db[k].setdefault('view', {}).update(v)
    return db


if __name__ == '__main__':
    import json, os
    p = os.path.join(os.path.dirname(__file__), '..', 'app', 'data', 'geom.json')
    db = apply(json.load(open(p)))
    json.dump(db, open(p, 'w'), separators=(',', ':'))
    print('regolazioni applicate:', len(VIEWS))

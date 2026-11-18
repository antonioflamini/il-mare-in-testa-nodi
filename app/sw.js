// Il Mare in Testa · Nodi — funziona anche senza rete (in barca!)
const V = 'mit-nodi-v4';
const CORE = ['./', 'index.html', 'css/app.css', 'js/app.js', 'js/viewer.js', 'js/rope.js', 'data/knots.js', 'data/knots2.js', 'data/knots3.js', 'data/geom.json',
  'manifest.webmanifest', 'img/icon-192.png', 'img/icon-512.png'];
const CDN = ['https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js',
  'https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/controls/OrbitControls.js',
  'https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/environments/RoomEnvironment.js'];
self.addEventListener('install', (e) => e.waitUntil(caches.open(V).then(c => c.addAll(CORE).then(() => Promise.all(CDN.map(u => c.add(u).catch(() => {})))))));
self.addEventListener('activate', (e) => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(fetch(e.request).then(r => {
    if (r.ok && (e.request.url.startsWith(self.location.origin) || e.request.url.includes('cdn.jsdelivr.net'))) {
      const copy = r.clone(); caches.open(V).then(c => c.put(e.request, copy));
    }
    return r;
  }).catch(() => caches.match(e.request, { ignoreSearch: true })));
});

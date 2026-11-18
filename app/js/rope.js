// Il Mare in Testa · Nodi — cima 3D realistica (texture intrecciata procedurale)
import * as THREE from 'three';

const TEX_W = 512, TEX_H = 256;

// Calza intrecciata a 16 fusi (8 per verso, trama a "twill" 2 sopra 2 sotto).
function braidCanvas(base, tracer, tracerEvery = 4) {
  const hgt = new Float32Array(TEX_W * TEX_H);
  const col = new Uint8ClampedArray(TEX_W * TEX_H * 4);
  const cb = new THREE.Color(base), ct = new THREE.Color(tracer);
  const N = 8;
  const rnd = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  for (let y = 0; y < TEX_H; y++) {
    const v = y / TEX_H;
    for (let x = 0; x < TEX_W; x++) {
      const u = x / TEX_W;
      const a = (u + v) * N, b = (u - v) * N + 64;
      const ia = Math.floor(a), ib = Math.floor(b);
      const fa = a - ia, fb = b - ib;
      const twill = (Math.floor((ia + ib) / 2) % 2 + 2) % 2;   // chi sta sopra
      let h, strand, along, across;
      if (twill === 0) { strand = 'A' + ((ib % N + N) % N); across = fb; along = fa; }
      else { strand = 'B' + ((ia % N + N) % N); across = fa; along = fb; }
      // profilo del fuso: tondo trasversale, si abbassa dove passa sotto
      const prof = Math.pow(Math.sin(Math.PI * across), 0.55);
      const dip = 0.72 + 0.28 * Math.sin(Math.PI * ((along * 0.5 + (twill ? 0.25 : 0.75)) % 1));
      // fibre: righe sottili lungo il fuso
      const fib = 0.9 + 0.1 * Math.sin(across * 60 + rnd(ia * 31 + ib) * 6);
      h = prof * dip * fib;
      hgt[y * TEX_W + x] = h;
      const idx = parseInt(strand.slice(1));
      const isTracer = strand[0] === 'A' && idx % tracerEvery === 0;
      const c = isTracer ? ct : cb;
      const shade = 0.62 + 0.38 * h;
      const jitter = 0.94 + 0.06 * rnd(ia * 13 + ib * 7 + (strand[0] === 'A' ? 1 : 2));
      const o = (y * TEX_W + x) * 4;
      col[o] = 255 * c.r * shade * jitter;
      col[o + 1] = 255 * c.g * shade * jitter;
      col[o + 2] = 255 * c.b * shade * jitter;
      col[o + 3] = 255;
    }
  }
  const c1 = document.createElement('canvas'); c1.width = TEX_W; c1.height = TEX_H;
  c1.getContext('2d').putImageData(new ImageData(col, TEX_W, TEX_H), 0, 0);
  // normal map dal rilievo
  const nm = new Uint8ClampedArray(TEX_W * TEX_H * 4);
  const H = (x, y) => hgt[((y + TEX_H) % TEX_H) * TEX_W + ((x + TEX_W) % TEX_W)];
  for (let y = 0; y < TEX_H; y++) for (let x = 0; x < TEX_W; x++) {
    const dx = (H(x + 1, y) - H(x - 1, y)) * 2.2, dy = (H(x, y + 1) - H(x, y - 1)) * 2.2;
    const l = Math.hypot(dx, dy, 1);
    const o = (y * TEX_W + x) * 4;
    nm[o] = (-dx / l * 0.5 + 0.5) * 255; nm[o + 1] = (-dy / l * 0.5 + 0.5) * 255; nm[o + 2] = (1 / l * 0.5 + 0.5) * 255; nm[o + 3] = 255;
  }
  const c2 = document.createElement('canvas'); c2.width = TEX_W; c2.height = TEX_H;
  c2.getContext('2d').putImageData(new ImageData(nm, TEX_W, TEX_H), 0, 0);
  return [c1, c2];
}

const cache = {};
export function ropeMaterial(kind = 'main', renderer) {
  if (cache[kind]) return cache[kind];
  const palette = {
    main: ['#2f8ae0', '#ffd21f', 4],      // blu mare con traccianti gialli (si legge su teak e su carta)
    second: ['#e8622a', '#f7f4ec', 4],    // arancio con traccianti bianchi
    third: ['#e6c34a', '#0b2a4a', 4],     // giallo
    teal: ['#2f9e55', '#f7f4ec', 4],     // verde
  }[kind] || ['#f2efe6', '#0b2a4a', 4];
  const [c1, c2] = braidCanvas(palette[0], palette[1], palette[2]);
  const map = new THREE.CanvasTexture(c1);
  map.colorSpace = THREE.SRGBColorSpace;
  map.wrapS = map.wrapT = THREE.RepeatWrapping;
  map.anisotropy = renderer ? renderer.capabilities.getMaxAnisotropy() : 8;
  const nmap = new THREE.CanvasTexture(c2);
  nmap.wrapS = nmap.wrapT = THREE.RepeatWrapping;
  nmap.anisotropy = map.anisotropy;
  const m = new THREE.MeshPhysicalMaterial({
    map, normalMap: nmap, normalScale: new THREE.Vector2(1.1, 1.1),
    roughness: 0.78, metalness: 0.0, sheen: 1.0, sheenRoughness: 0.6,
    sheenColor: new THREE.Color('#ffffff').multiplyScalar(0.25),
    vertexColors: true,
  });
  cache[kind] = m;
  return m;
}

// ----------------------------------------------------------------- tubo
// Tubo con trasporto parallelo dei riferimenti (nessuna torsione spuria),
// coordinate UV in proporzione reale: u = lunghezza / circonferenza.
export class RopeMesh {
  constructor(nPts, material, opts = {}) {
    this.radius = opts.radius ?? 0.5;
    this.radial = opts.radial ?? 18;
    this.sub = opts.sub ?? 4;                 // suddivisioni per segmento
    this.nPts = nPts;
    this.rings = (nPts - 1) * this.sub + 1;
    const R = this.radial + 1;
    const nv = this.rings * R + 2 * (R + 1);
    this.geo = new THREE.BufferGeometry();
    this.pos = new Float32Array(nv * 3);
    this.nor = new Float32Array(nv * 3);
    this.uv = new Float32Array(nv * 2);
    this.col = new Float32Array(nv * 3).fill(1);
    const idx = [];
    for (let i = 0; i < this.rings - 1; i++) for (let j = 0; j < this.radial; j++) {
      const a = i * R + j, b = (i + 1) * R + j;
      idx.push(a, b, a + 1, b, b + 1, a + 1);
    }
    this.tubeIndexCount = idx.length;
    // tappi (due ventagli) – indici in coda
    this.capStart = this.rings * R;
    for (let c = 0; c < 2; c++) {
      const base = this.capStart + c * (R + 1);
      for (let j = 0; j < this.radial; j++) {
        if (c === 0) idx.push(base, base + 1 + j + 1, base + 1 + j);
        else idx.push(base, base + 1 + j, base + 1 + j + 1);
      }
    }
    this.geo.setIndex(idx);
    this.geo.setAttribute('position', new THREE.BufferAttribute(this.pos, 3));
    this.geo.setAttribute('normal', new THREE.BufferAttribute(this.nor, 3));
    this.geo.setAttribute('uv', new THREE.BufferAttribute(this.uv, 2));
    this.geo.setAttribute('color', new THREE.BufferAttribute(this.col, 3));
    this.mesh = new THREE.Mesh(this.geo, material);
    this.mesh.castShadow = true; this.mesh.receiveShadow = true;
    this.mesh.frustumCulled = false;
    this.whip = new THREE.Color(opts.whip ?? '#b8231c');
    this.whipStand = new THREE.Color(opts.whipStand ?? '#1c2833');
    this._curve = new THREE.CatmullRomCurve3([], false, 'centripetal');
    this._tmp = [];
  }

  // pts: Float32Array/array piatto x,y,z ; reveal: 0..1 quota visibile
  update(pts, reveal = 1) {
    const n = this.nPts;
    if (this._tmp.length !== n) this._tmp = Array.from({ length: n }, () => new THREE.Vector3());
    for (let i = 0; i < n; i++) this._tmp[i].set(pts[3 * i], pts[3 * i + 1], pts[3 * i + 2]);
    this._curve.points = this._tmp;
    const M = this.rings, R = this.radial + 1;
    const P = new Array(M), T = new Array(M);
    for (let i = 0; i < M; i++) {
      const t = i / (M - 1);
      P[i] = this._curve.getPoint(t);
    }
    // tangenti e lunghezze
    const s = new Float32Array(M);
    for (let i = 0; i < M; i++) {
      const a = P[Math.max(i - 1, 0)], b = P[Math.min(i + 1, M - 1)];
      T[i] = new THREE.Vector3().subVectors(b, a).normalize();
      if (i) s[i] = s[i - 1] + P[i].distanceTo(P[i - 1]);
    }
    const L = s[M - 1];
    // trasporto parallelo
    let N0 = new THREE.Vector3(0, 0, 1);
    if (Math.abs(N0.dot(T[0])) > 0.9) N0.set(0, 1, 0);
    N0.sub(T[0].clone().multiplyScalar(N0.dot(T[0]))).normalize();
    const Nn = [N0];
    for (let i = 1; i < M; i++) {
      const v = new THREE.Vector3().crossVectors(T[i - 1], T[i]);
      let n = Nn[i - 1].clone();
      const sl = v.length();
      if (sl > 1e-6) { v.divideScalar(sl); n.applyAxisAngle(v, Math.asin(Math.min(sl, 1))); }
      n.sub(T[i].clone().multiplyScalar(n.dot(T[i]))).normalize();
      Nn.push(n);
    }
    const circ = 2 * Math.PI * this.radius;
    const sTip = reveal * L;
    const whipLen = 1.1;
    const B = new THREE.Vector3();
    for (let i = 0; i < M; i++) {
      B.crossVectors(T[i], Nn[i]);
      // capo legato (whipping) in testa e sul dormiente
      const sw = s[i];
      let w = 0, ws = 0;
      if (!this.plain && sw > sTip - whipLen && sw <= sTip + 1e-3) w = 1;
      if (!this.plain && sw < whipLen * 0.8) ws = 1;
      for (let j = 0; j <= this.radial; j++) {
        const a = (j / this.radial) * Math.PI * 2;
        const cx = Math.cos(a), sy = Math.sin(a);
        const nx = Nn[i].x * cx + B.x * sy, ny = Nn[i].y * cx + B.y * sy, nz = Nn[i].z * cx + B.z * sy;
        const o = (i * R + j);
        // fasciatura: leggermente piu' sottile e liscia
        const rr = this.radius * (w || ws ? 0.97 : 1);
        this.pos[3 * o] = P[i].x + nx * rr; this.pos[3 * o + 1] = P[i].y + ny * rr; this.pos[3 * o + 2] = P[i].z + nz * rr;
        this.nor[3 * o] = nx; this.nor[3 * o + 1] = ny; this.nor[3 * o + 2] = nz;
        this.uv[2 * o] = sw / circ; this.uv[2 * o + 1] = j / this.radial;
        const c = w ? this.whip : ws ? this.whipStand : null;
        if (c) { this.col[3 * o] = c.r * 1.6; this.col[3 * o + 1] = c.g * 1.6; this.col[3 * o + 2] = c.b * 1.6; }
        else { this.col[3 * o] = 1; this.col[3 * o + 1] = 1; this.col[3 * o + 2] = 1; }
      }
    }
    // indice dell'anello in punta
    let iTip = M - 1;
    for (let i = 0; i < M; i++) if (s[i] > sTip) { iTip = Math.max(i - 1, 1); break; }
    // tappi: inizio e punta corrente
    const caps = [[0, -1], [iTip, 1]];
    caps.forEach(([ri, dir], c) => {
      const base = this.capStart + c * (R + 1);
      const t = T[ri].clone().multiplyScalar(dir);
      const ctr = P[ri].clone().addScaledVector(t, this.radius * 0.18);
      const cc = this.plain ? new THREE.Color(0.625, 0.625, 0.625) : (c === 1 ? this.whip : this.whipStand);
      this._setV(base, ctr, t, 0, 0.5, cc);
      for (let j = 0; j <= this.radial; j++) {
        const o = ri * R + j;
        const v = new THREE.Vector3(this.pos[3 * o], this.pos[3 * o + 1], this.pos[3 * o + 2]);
        this._setV(base + 1 + j, v, t, 0, 0.5, cc);
      }
    });
    this.geo.setDrawRange(0, Math.min(this.tubeIndexCount, iTip * this.radial * 6));
    this._capRange = this.tubeIndexCount;
    this.geo.attributes.position.needsUpdate = true;
    this.geo.attributes.normal.needsUpdate = true;
    this.geo.attributes.uv.needsUpdate = true;
    this.geo.attributes.color.needsUpdate = true;
    this.geo.computeBoundingSphere();
    // i tappi stanno in coda all'indice: li disegna una seconda mesh
    if (!this.capMesh) {
      this.capMesh = new THREE.Mesh(this.geo, this.mesh.material);
      this.capMesh.castShadow = true; this.capMesh.frustumCulled = false;
      this.capMesh.onBeforeRender = () => {};
      this.mesh.add(this.capMesh);
    }
    this.capGroups();
    this.length = L;
    this.tipPoint = P[iTip];
    return this;
  }

  capGroups() {
    // seconda mesh che usa solo i triangoli dei tappi
    if (!this.capGeo) {
      this.capGeo = new THREE.BufferGeometry();
      this.capGeo.setAttribute('position', this.geo.attributes.position);
      this.capGeo.setAttribute('normal', this.geo.attributes.normal);
      this.capGeo.setAttribute('uv', this.geo.attributes.uv);
      this.capGeo.setAttribute('color', this.geo.attributes.color);
      const all = this.geo.index.array;
      this.capGeo.setIndex(Array.from(all.slice(this.tubeIndexCount)));
      this.capMesh.geometry = this.capGeo;
    }
  }

  _setV(o, p, n, u, v, c) {
    this.pos[3 * o] = p.x; this.pos[3 * o + 1] = p.y; this.pos[3 * o + 2] = p.z;
    this.nor[3 * o] = n.x; this.nor[3 * o + 1] = n.y; this.nor[3 * o + 2] = n.z;
    this.uv[2 * o] = u; this.uv[2 * o + 1] = v;
    this.col[3 * o] = c.r * 1.6; this.col[3 * o + 1] = c.g * 1.6; this.col[3 * o + 2] = c.b * 1.6;
  }
}

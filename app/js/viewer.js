// Il Mare in Testa · Nodi — visore 3D (scena, oggetti di bordo, animazione)
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RopeMesh, ropeMaterial } from './rope.js';

// ------------------------------------------------------- materiali scena
function woodTexture(light = '#9a6a3c', dark = '#5b3a1e', planks = true) {
  // teak: venatura periodica (nessuna giunta visibile quando la texture si ripete)
  const W = 1024, H = 1024, c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d');
  const rnd = (i) => { const x = Math.sin(i * 91.7 + 17.3) * 43758.5453; return x - Math.floor(x); };
  const img = g.createImageData(W, H), d = img.data;
  const L = new THREE.Color(light), Dk = new THREE.Color(dark);
  const nP = planks ? 8 : 1, ph = H / nP;
  const TAU = Math.PI * 2;
  for (let y = 0; y < H; y++) {
    const p = Math.floor(y / ph), fy = (y % ph) / ph;
    const tone = 0.82 + rnd(p + 3) * 0.3;
    for (let x = 0; x < W; x++) {
      const u = x / W;
      let gr = 0;
      for (let k = 1; k <= 4; k++) gr += Math.sin(TAU * (fy * (6 + 9 * k + rnd(p * 9 + k) * 6) + Math.sin(TAU * (u * k + rnd(p + k))) * 0.35 * k / 4)) / k;
      const fine = Math.sin(TAU * (fy * 140 + Math.sin(TAU * (u * 3 + p * 0.37)) * 0.8)) * 0.5;
      let t = 0.55 + 0.14 * gr + 0.05 * fine;
      t = Math.min(1, Math.max(0, t)) * tone;
      let r = Dk.r + (L.r - Dk.r) * t, gg = Dk.g + (L.g - Dk.g) * t, b = Dk.b + (L.b - Dk.b) * t;
      if (planks) {
        const seam = fy < 0.035 || fy > 0.985;                     // comento nero
        const joint = Math.abs(u - rnd(p * 7)) < 0.0035;            // giunta di testa
        if (seam || joint) { r = 0.07; gg = 0.06; b = 0.05; }
      }
      const o = (y * W + x) * 4;
      d[o] = r * 255; d[o + 1] = gg * 255; d[o + 2] = b * 255; d[o + 3] = 255;
    }
  }
  g.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8;
  return t;
}

const MATS = {};
function mat(name) {
  if (MATS[name]) return MATS[name];
  let m;
  switch (name) {
    case 'steel': m = new THREE.MeshPhysicalMaterial({ color: '#d8dde2', metalness: 1, roughness: 0.22, clearcoat: 0.3 }); break;
    case 'galv': m = new THREE.MeshStandardMaterial({ color: '#9aa1a6', metalness: 0.85, roughness: 0.45 }); break;
    case 'bronze': m = new THREE.MeshStandardMaterial({ color: '#b98a4b', metalness: 1, roughness: 0.3 }); break;
    case 'black': m = new THREE.MeshStandardMaterial({ color: '#1d2127', metalness: 0.4, roughness: 0.5 }); break;
    case 'iron': m = new THREE.MeshStandardMaterial({ color: '#2f3a44', metalness: 0.6, roughness: 0.55 }); break;
    case 'concrete': m = new THREE.MeshStandardMaterial({ color: '#a7a39a', roughness: 0.95 }); break;
    case 'wood': {
      const t = woodTexture('#9c6b3c', '#5a3a1e', false); t.repeat.set(1, 2);
      m = new THREE.MeshStandardMaterial({ map: t, roughness: 0.75 }); break;
    }
    default: m = new THREE.MeshStandardMaterial({ color: '#888' });
  }
  MATS[name] = m; return m;
}

function axisQuat(axis) {
  const a = new THREE.Vector3(...axis).normalize();
  return new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), a);
}

function buildProp(p) {
  const g = new THREE.Group();
  if (p.hidden) return g;
  const m = mat(p.mat || (p.type === 'torus' ? 'steel' : 'wood'));
  let mesh;
  if (p.type === 'cyl') {
    mesh = new THREE.Mesh(new THREE.CylinderGeometry(p.r, p.r, p.h, 48, 1), m);
    mesh.quaternion.copy(axisQuat(p.axis));
    mesh.position.set(...p.c);
    if (p.cap) {   // testa a fungo (bitta)
      const cap = new THREE.Mesh(new THREE.CylinderGeometry(p.r * 1.25, p.r * 1.1, p.r * 0.5, 48), m);
      cap.position.y = p.h / 2 + p.r * 0.2; mesh.add(cap);
    }
  } else if (p.type === 'torus') {
    mesh = new THREE.Mesh(new THREE.TorusGeometry(p.R, p.r, 32, 96), m);
    const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), new THREE.Vector3(...p.axis).normalize());
    mesh.quaternion.copy(q); mesh.position.set(...p.c);
  } else if (p.type === 'box') {
    mesh = new THREE.Mesh(new THREE.BoxGeometry(...p.size), m);
    mesh.position.set(...p.c);
  } else if (p.type === 'capsule') {   // corno di galloccia, visivo
    mesh = new THREE.Mesh(new THREE.CapsuleGeometry(p.r, p.h, 12, 32), m);
    mesh.quaternion.copy(axisQuat(p.axis)); mesh.position.set(...p.c);
  } else return g;
  mesh.castShadow = true; mesh.receiveShadow = true;
  g.add(mesh);
  return g;
}

// ------------------------------------------------------------- visore
export class Viewer {
  constructor(container, opts = {}) {
    this.el = container;
    this.opts = opts;
    const r = this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: !!opts.capture });
    r.setPixelRatio(Math.min(window.devicePixelRatio, opts.pixelRatio || 2));
    r.outputColorSpace = THREE.SRGBColorSpace;
    r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = 1.05;
    r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(r.domElement);
    const scene = this.scene = new THREE.Scene();
    const pm = new THREE.PMREMGenerator(r);
    scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environmentIntensity = 0.55;
    this.camera = new THREE.PerspectiveCamera(32, 1, 0.1, 500);
    this.controls = new OrbitControls(this.camera, r.domElement);
    this.controls.enableDamping = true; this.controls.dampingFactor = 0.08;
    this.controls.minDistance = 6; this.controls.maxDistance = 140;
    // luci: sole caldo + cielo
    const hemi = new THREE.HemisphereLight('#e4f0ff', '#6a5236', 0.45); scene.add(hemi);
    const sun = this.sun = new THREE.DirectionalLight('#fff4e2', 2.8);
    sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03;
    sun.shadow.radius = 4;
    scene.add(sun, sun.target);
    const rim = new THREE.DirectionalLight('#9cc7ff', 0.7); rim.position.set(-20, 10, -25); scene.add(rim);
    // coperta in teak
    const deckTex = woodTexture('#b58f66', '#76553a', true); deckTex.repeat.set(4, 4);
    this.deck = new THREE.Mesh(new THREE.CircleGeometry(60, 96),
      new THREE.MeshStandardMaterial({ map: deckTex, roughness: 0.85 }));
    this.deck.rotation.x = -Math.PI / 2; this.deck.receiveShadow = true;
    scene.add(this.deck);
    this.shadowOnly = new THREE.Mesh(new THREE.CircleGeometry(60, 64), new THREE.ShadowMaterial({ opacity: 0.22 }));
    this.shadowOnly.rotation.x = -Math.PI / 2; this.shadowOnly.receiveShadow = true;
    scene.add(this.shadowOnly);
    this.setBackdrop(opts.backdrop || 'deck');
    this.root = new THREE.Group(); scene.add(this.root);
    this.ropes = []; this.knot = null;
    this.state = { g: 0, playing: false, speed: 1, loop: true, mirror: false };
    this._last = performance.now();
    this.resize();
    new ResizeObserver(() => this.resize()).observe(container);
    if (!opts.capture) this._loop();
  }

  setBackdrop(kind) {
    this.backdrop = kind;
    this.deck.visible = kind === 'deck';
    this.shadowOnly.visible = kind !== 'deck';
    this.shadowOnly.material.opacity = kind === 'paper' ? 0.16 : 0.22;
  }

  resize() {
    const w = this.el.clientWidth || 800, h = this.el.clientHeight || 600;
    this.renderer.setSize(w, h, false);
    this.renderer.domElement.style.width = '100%'; this.renderer.domElement.style.height = '100%';
    this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
  }

  load(id, geom, meta = {}) {
    this.root.clear();
    this.ropes = [];
    this.id = id; this.geom = geom; this.meta = meta;
    const v = geom.view || {};
    // "deck": il nodo e' disegnato nel piano xy e si appoggia in coperta
    this.layFlat = v.mode !== 'stand';
    const holder = this.holder = new THREE.Group();
    if (this.layFlat) holder.rotation.x = -Math.PI / 2;
    this.root.add(holder);
    (geom.props || []).forEach(p => holder.add(buildProp(p)));
    const kinds = geom.colors || ['main', 'second', 'third'];
    const solid = geom.solid || {};
    this.isSolid = geom.ropes.map((_, i) => !!solid[String(i)]);
    geom.ropes.forEach((frames, i) => {
      const n = frames[0].length / 3;
      const sname = solid[String(i)];
      const material = !this.isSolid[i] ? ropeMaterial(kinds[i] || 'main', this.renderer)
        : sname.startsWith('rope:') ? ropeMaterial(sname.slice(5), this.renderer) : mat(sname);
      const rm = new RopeMesh(n, material, {
        radius: (geom.radii && geom.radii[i]) || 0.5, radial: this.isSolid[i] ? 32 : 18,
        whip: i === 0 ? '#b8231c' : '#0b2a4a', whipStand: i === 0 ? '#14202b' : '#4a1d0e' });
      rm.solid = this.isSolid[i]; rm.plain = rm.solid;
      rm.frames = frames.map(f => Float32Array.from(f));
      rm.buf = new Float32Array(frames[0].length);
      holder.add(rm.mesh);
      this.ropes.push(rm);
    });
    // ordine di comparsa delle cime: [inizio, fine, quota gia' visibile]
    const L = geom.lengths.map((l, i) => this.isSolid[i] ? 0 : l);
    this.reveal = geom.reveal || (() => {
      const tot = L.reduce((a, b) => a + b, 0); let acc = 0;
      return L.map(l => { if (!l) return [0, 0.001, 1]; const a = acc / tot; acc += l; return [a, acc / tot, 0]; });
    })();
    this.totalLen = L.reduce((a, b) => a + b, 0);
    this.tieSeconds = Math.max(5, Math.min(16, this.totalLen / 5.5)) * (meta.tempo || 1);
    this.tightSeconds = 2.6;
    this.state.g = 0;
    this.applyMirror();
    this.render(1.0);   // inquadra il nodo appena legato (prima del serraggio)
    this.fit();
    this.render(this.state.g);
  }

  applyMirror() {
    // three.js inverte da solo il verso dei triangoli con scala negativa
    this.root.scale.x = this.state.mirror ? -1 : 1;
  }

  // g in [0,1] = legatura, (1, 1+T] = serraggio
  render(g) {
    if (!this.ropes.length) return;
    const tight = Math.max(0, Math.min(1, (g - 1) / 0.35));
    this.ropes.forEach((rm, i) => {
      const [a, b, pre] = this.reveal[i];
      let rv = g >= 1 ? 1 : Math.max(0, Math.min(1, (g - a) / Math.max(b - a, 1e-6)));
      rv = pre + (1 - pre) * rv;
      const F = rm.frames, K = F.length - 1;
      const x = this._ease(tight) * K, k0 = Math.min(Math.floor(x), K - 1), f = x - k0;
      const A = F[k0], B = F[Math.min(k0 + 1, K)], out = rm.buf;
      for (let j = 0; j < out.length; j++) out[j] = A[j] + (B[j] - A[j]) * f;
      if (rm.solid) rv = 1;
      rm.mesh.visible = rv > 0.002;
      rm.update(out, Math.max(rv, 0.004));
    });
  }

  _ease(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }

  fit(margin = 1.18) {
    // inquadra il "cuore" del nodo: esclude i capi lunghi (dormiente e corrente)
    this.holder.updateMatrixWorld(true);
    const box = new THREE.Box3(), p = new THREE.Vector3();
    this.ropes.forEach((rm) => {
      const F = rm.frames[0], n = F.length / 3;
      const a = rm.solid ? Math.floor(n * 0.3) : Math.floor(n * 0.16), b = rm.solid ? Math.ceil(n * 0.7) : Math.ceil(n * 0.93);
      for (let i = a; i < b; i++) box.expandByPoint(p.set(F[3 * i], F[3 * i + 1], F[3 * i + 2]).applyMatrix4(this.holder.matrixWorld));
    });
    this.holder.children.forEach(ch => { if (!this.ropes.some(r => r.mesh === ch)) box.union(new THREE.Box3().setFromObject(ch)); });
    const c = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
    const v = this.geom.view || {};
    const radius = Math.max(size.length() / 2, 4.5);
    const fov = this.camera.fov * Math.PI / 180;
    const fit = Math.min(fov, 2 * Math.atan(Math.tan(fov / 2) * this.camera.aspect));
    const dist = radius / Math.sin(fit / 2) * margin * (v.zoom ? 1 / v.zoom : 1) * 0.82;
    const el = (v.elev ?? (this.layFlat ? 62 : 18)) * Math.PI / 180;
    const az = (v.az ?? 0) * Math.PI / 180;
    const full = new THREE.Box3().setFromObject(this.holder);
    const ground = this.layFlat ? full.min.y : (v.ground ?? full.min.y);
    this.deck.position.y = ground - 0.001; this.shadowOnly.position.y = ground;
    if (this.layFlat) { const dy = -full.min.y; this.holder.position.y += dy; c.y += dy; this.deck.position.y = -0.001; this.shadowOnly.position.y = 0; }
    this.controls.target.copy(c);
    this.camera.position.set(c.x + dist * Math.cos(el) * Math.sin(az), c.y + dist * Math.sin(el), c.z + dist * Math.cos(el) * Math.cos(az));
    this.camera.near = dist / 50; this.camera.far = dist * 8; this.camera.updateProjectionMatrix();
    this.controls.update();
    const s = this.sun; s.position.set(c.x + 18, c.y + 40, c.z + 22); s.target.position.copy(c);
    const R = radius * 1.6, sc = s.shadow.camera;
    sc.left = -R; sc.right = R; sc.top = R; sc.bottom = -R; sc.near = 1; sc.far = 120; sc.updateProjectionMatrix();
    this.home = { pos: this.camera.position.clone(), target: c.clone() };
  }

  resetView() {
    if (!this.home) return;
    this.camera.position.copy(this.home.pos); this.controls.target.copy(this.home.target); this.controls.update();
  }

  get total() { return 1.35; }

  step(dt) {
    const st = this.state;
    if (st.playing) {
      const rate = st.g < 1 ? 1 / this.tieSeconds : 0.35 / this.tightSeconds;
      st.g += dt * rate * st.speed;
      if (st.g >= this.total) {
        if (st.loop) { st.hold = (st.hold || 0) + dt; st.g = this.total; if (st.hold > 1.6) { st.g = 0; st.hold = 0; } }
        else { st.g = this.total; st.playing = false; this.onEnd && this.onEnd(); }
      }
      this.render(st.g);
      this.onTick && this.onTick(st.g);
    }
  }

  seek(g) { this.state.g = Math.max(0, Math.min(this.total, g)); this.render(this.state.g); this.onTick && this.onTick(this.state.g); }

  _loop() {
    const now = performance.now(); const dt = Math.min((now - this._last) / 1000, 0.05); this._last = now;
    this.step(dt);
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
    requestAnimationFrame(() => this._loop());
  }

  draw() { this.controls.update(); this.renderer.render(this.scene, this.camera); }
}

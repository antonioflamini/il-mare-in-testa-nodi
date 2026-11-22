// Il Mare in Testa · Nodi — interfaccia
import { Viewer } from './viewer.js';
import { NODI, FAMIGLIE } from '../data/knots.js';

const $ = (s, el = document) => el.querySelector(s);
const store = {
  get(k, d) { try { const v = localStorage.getItem('mit-nodi:' + k); return v ? JSON.parse(v) : d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem('mit-nodi:' + k, JSON.stringify(v)); } catch { /* privato */ } },
};
const learned = new Set(store.get('learned', []));
const saveLearned = () => store.set('learned', [...learned]);
const byId = Object.fromEntries(NODI.map(n => [n.id, n]));
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

let GEOM = null, viewer = null, current = null;

async function loadGeom() {
  if (GEOM) return GEOM;
  GEOM = await (await fetch('data/geom.json')).json();
  return GEOM;
}

// ------------------------------------------------------------ elenco
function renderList() {
  const q = $('#q').value.trim().toLowerCase();
  const onlyExam = $('#onlyExam').checked;
  const html = FAMIGLIE.map(f => {
    const items = NODI.filter(n => n.famiglia === f.id)
      .filter(n => !onlyExam || n.esame)
      .filter(n => !q || [n.nome, ...n.altri, n.sintesi].join(' ').toLowerCase().includes(q));
    if (!items.length) return '';
    return `<div class="fam"><h3>${esc(f.nome)}</h3><p>${esc(f.motto)}</p>${items.map(n =>
      `<button class="item${current && current.id === n.id ? ' on' : ''}" data-id="${n.id}">
        <span class="dot${learned.has(n.id) ? ' done' : ''}"></span>${esc(n.nome)}${n.esame ? '<small>patente</small>' : ''}</button>`).join('')}</div>`;
  }).join('');
  $('#families').innerHTML = html || '<p class="small">Nessun nodo trovato.</p>';
}

// ------------------------------------------------------------ scheda
const anchors = (n, max = 3) => '⚓'.repeat(n) + '<span style="opacity:.25">' + '⚓'.repeat(max - n) + '</span>';

function renderCard(n) {
  const fam = FAMIGLIE.find(f => f.id === n.famiglia);
  $('#card').innerHTML = `
    <h1>${esc(n.nome)}</h1>
    <div class="alias">${n.altri.length ? 'Detto anche: ' + n.altri.map(esc).join(' · ') : '&nbsp;'}</div>
    <div class="badges">
      ${n.esame ? '<span class="badge esame">Patente nautica</span>' : ''}
      <span class="badge">${esc(fam.nome)}</span>
      <span class="badge" title="Difficoltà">Difficoltà ${anchors(n.difficolta)}</span>
      ${n.tenuta ? `<span class="badge" title="Tenuta">Tenuta ${anchors(n.tenuta)}</span>` : ''}
    </div>
    <p class="sintesi">${esc(n.sintesi)}</p>
    <div class="box regola"><b>La regola in 10 secondi</b><p>${esc(n.regola)}</p></div>
    <h2>Passo passo</h2>
    <ol class="passi">${n.passi.map((p, i) => `<li data-at="${p.at}" data-i="${i}">${esc(p.t)}</li>`).join('')}</ol>
    <div class="box trucco"><b>Il trucco del nostromo</b><p>${esc(n.trucco)}</p></div>
    <div class="box trappola"><b>Trappola</b><p>${esc(n.trappola)}</p></div>
    <h2>A cosa serve</h2>
    <ul>${n.usi.map(u => `<li>${esc(u)}</li>`).join('')}</ul>
    <div class="box storia"><b>La storia</b><p>${esc(n.storia)}</p></div>
    <h2>Mettiti alla prova</h2>
    <div id="cardQuiz">${n.quiz.map((q, qi) => quizHtml(q, `${n.id}-${qi}`)).join('')}</div>
    <label class="learned"><input type="checkbox" id="learnedBox" ${learned.has(n.id) ? 'checked' : ''}> So farlo a occhi chiusi</label>
    ${n.volume ? `<p class="vol">Nei libri: <b>Il Mare in Testa</b>, ${esc(n.volume)} · e nel quaderno <b>I Nodi</b>.</p>` : '<p class="vol">Nel quaderno <b>Il Mare in Testa · I Nodi</b>.</p>'}
    <p class="vol"><a href="mailto:ilmareintestaantonioflamini@gmail.com?subject=${encodeURIComponent('Nodi · Errore: ' + n.nome)}&body=${encodeURIComponent('Nodo: ' + n.nome + ' (' + location.origin + location.pathname + '#/nodo/' + n.id + ')\n\nCosa non torna:\n')}">Segnala un errore su questo nodo</a></p>
  `;
  $('#card').scrollTop = 0;
  $('#card').querySelectorAll('ol.passi li').forEach(li => li.addEventListener('click', () => {
    viewer.state.playing = false; setPlayIcon(); viewer.seek(+li.dataset.at + (li.dataset.at === '1' ? 0.35 : 0.001));
  }));
  $('#learnedBox').addEventListener('change', (e) => { e.target.checked ? learned.add(n.id) : learned.delete(n.id); saveLearned(); renderList(); });
  bindQuiz($('#cardQuiz'));
}

function quizHtml(q, key) {
  return `<div class="q" data-ok="${q.ok}" data-key="${key}"><p>${esc(q.q)}</p>${q.a.map((a, i) =>
    `<button class="ans" data-i="${i}">${'abc'[i]}) ${esc(a)}</button>`).join('')}</div>`;
}
function bindQuiz(root, onAnswer) {
  root.querySelectorAll('.q').forEach(qd => qd.querySelectorAll('.ans').forEach(b => b.addEventListener('click', () => {
    if (qd.dataset.done) return; qd.dataset.done = 1;
    const ok = +qd.dataset.ok, i = +b.dataset.i;
    b.classList.add(i === ok ? 'ok' : 'ko');
    qd.querySelectorAll('.ans')[ok].classList.add('ok');
    onAnswer && onAnswer(i === ok, qd.dataset.key);
  })));
}

// ------------------------------------------------- visore e controlli
function setPlayIcon() { $('#bPlay').textContent = viewer.state.playing ? '❚❚' : '▶'; }

function stepIndex(n, g) {
  let k = 0;
  n.passi.forEach((p, i) => { if (g + 1e-4 >= p.at) k = i; });
  return k;
}

function onTick(g) {
  if (!current) return;
  $('#scrub').value = g;
  $('#viewer').dataset.g = g.toFixed(3);
  const k = stepIndex(current, g);
  const p = current.passi[k];
  $('#caption').innerHTML = `<b>${k + 1}/${current.passi.length}</b>${esc(p.t)}`;
  document.querySelectorAll('ol.passi li').forEach((li, i) => li.classList.toggle('on', i === k));
}

async function openKnot(id, autoplay = true) {
  const n = byId[id] || NODI[0];
  current = n;
  renderList(); renderCard(n);
  document.title = `${n.nome} · Il Mare in Testa · Nodi`;
  const geom = await loadGeom();
  if (!viewer) {
    viewer = new Viewer($('#viewer'), { backdrop: store.get('bg2', 'studio') });
    viewer.onTick = onTick;
    window.__mitViewer = viewer;   // per i test automatici
    $('#bBg').classList.toggle('on', viewer.backdrop === 'deck');
  }
  $('#loading').style.display = 'none';
  viewer.load(n.id, geom[n.id], { tempo: 1 });
  viewer.setPauses(n.passi.map(p => p.at));
  viewer.state.playing = autoplay;
  setPlayIcon(); onTick(0);
}

function bindControls() {
  $('#bPlay').onclick = () => { if (viewer.state.g >= viewer.total - 1e-3) viewer.seek(0); viewer.state.playing = !viewer.state.playing; setPlayIcon(); };
  const jump = (dir) => {
    viewer.state.playing = false; setPlayIcon();
    const ats = current.passi.map(p => p.at === 1 ? 1.35 : p.at + 0.001);
    const g = viewer.state.g;
    let t = dir > 0 ? ats.find(a => a > g + 0.01) : [...ats].reverse().find(a => a < g - 0.01);
    if (t === undefined) t = dir > 0 ? viewer.total : 0;
    viewer.seek(t);
  };
  $('#bPrev').onclick = () => jump(-1);
  $('#bNext').onclick = () => jump(1);
  $('#scrub').oninput = (e) => { viewer.state.playing = false; setPlayIcon(); viewer.seek(+e.target.value); };
  $('#speed').onchange = (e) => { viewer.state.speed = +e.target.value; };
  $('#bLoop').onclick = (e) => { viewer.state.loop = !viewer.state.loop; e.currentTarget.classList.toggle('on', viewer.state.loop); e.currentTarget.setAttribute('aria-pressed', viewer.state.loop); };
  $('#bMirror').onclick = (e) => { viewer.state.mirror = !viewer.state.mirror; viewer.applyMirror(); e.currentTarget.classList.toggle('on', viewer.state.mirror); e.currentTarget.setAttribute('aria-pressed', viewer.state.mirror); };
  $('#bBg').onclick = (e) => {
    const k = viewer.backdrop === 'deck' ? 'studio' : 'deck';
    viewer.setBackdrop(k); store.set('bg2', k); e.currentTarget.classList.toggle('on', k === 'deck');
    const g = viewer.state.g; viewer.load(current.id, GEOM[current.id]); viewer.setPauses(current.passi.map(p => p.at)); viewer.seek(g);
  };
  $('#bHome').onclick = () => viewer.resetView();
  $('#bFull').onclick = () => { const el = $('.stage'); document.fullscreenElement ? document.exitFullscreen() : el.requestFullscreen && el.requestFullscreen(); };
  viewer.onEnd = setPlayIcon;
  document.addEventListener('keydown', (e) => {
    if (!$('#view-nodario').classList.contains('on') || e.target.matches('input,select,textarea')) return;
    if (e.code === 'Space') { e.preventDefault(); $('#bPlay').click(); }
    if (e.key === 'ArrowRight') $('#bNext').click();
    if (e.key === 'ArrowLeft') $('#bPrev').click();
  });
}

// ------------------------------------------------------------ allenati
let trainerViewer = null;
const wrong = store.get('wrong', {});
function pickWeighted(list, keyOf) {
  const w = list.map(x => 1 + 2 * (wrong[keyOf(x)] || 0));
  let r = Math.random() * w.reduce((a, b) => a + b, 0);
  for (let i = 0; i < list.length; i++) { r -= w[i]; if (r <= 0) return list[i]; }
  return list[list.length - 1];
}
function mark(key, ok) { wrong[key] = Math.max(0, (wrong[key] || 0) + (ok ? -1 : 1)); store.set('wrong', wrong); }
const score = { ok: 0, tot: 0 };

async function trainer(mode) {
  document.querySelectorAll('.mode').forEach(b => b.classList.toggle('on', b.dataset.mode === mode));
  const box = $('#trainer');
  if (mode === 'quiz') {
    $('#tv').hidden = true;
    const all = NODI.flatMap(n => n.quiz.map((q, i) => ({ ...q, key: `${n.id}-${i}`, nodo: n })));
    const q = pickWeighted(all, x => x.key);
    box.innerHTML = `<p class="score">Risposte giuste: ${score.ok} su ${score.tot}</p>${quizHtml(q, q.key)}
      <p class="small">Dal nodo: <a href="#/nodo/${q.nodo.id}">${esc(q.nodo.nome)}</a></p><button class="mode" id="nextQ"><b>Avanti →</b></button>`;
    bindQuiz(box, (ok, key) => { score.tot++; if (ok) score.ok++; mark(key, ok); $('.score', box).textContent = `Risposte giuste: ${score.ok} su ${score.tot}`; });
    $('#nextQ').onclick = () => trainer('quiz');
  } else {
    const target = pickWeighted(NODI, n => 'r-' + n.id);
    const others = NODI.filter(n => n.id !== target.id).sort(() => Math.random() - 0.5).slice(0, 2);
    const opts = [target, ...others].sort(() => Math.random() - 0.5);
    $('#tv').hidden = false;
    box.innerHTML = `<p class="score">Riconosciuti: ${score.ok} su ${score.tot}</p>
      <div class="q" data-ok="${opts.indexOf(target)}" data-key="r-${target.id}"><p>Come si chiama questo nodo?</p>${opts.map((o, i) =>
        `<button class="ans" data-i="${i}">${'abc'[i]}) ${esc(o.nome)}</button>`).join('')}</div>
      <button class="mode" id="nextQ"><b>Un altro →</b></button>`;
    const geom = await loadGeom();
    if (!trainerViewer) trainerViewer = new Viewer($('#tv'), { backdrop: 'none' });
    trainerViewer.resize();
    trainerViewer.load(target.id, geom[target.id]);
    trainerViewer.seek(trainerViewer.total);
    trainerViewer.controls.autoRotate = true; trainerViewer.controls.autoRotateSpeed = 1.2;
    bindQuiz(box, (ok, key) => {
      score.tot++; if (ok) score.ok++; mark(key, ok);
      $('.score', box).innerHTML = `Riconosciuti: ${score.ok} su ${score.tot} · <a href="#/nodo/${target.id}">rivedi il ${esc(target.nome)}</a>`;
    });
    $('#nextQ').onclick = () => trainer('riconosci');
  }
}

// ------------------------------------------------------------ progressi
function renderProgress() {
  const n = learned.size, tot = NODI.length;
  $('#progress').innerHTML = `<p><b>${n}</b> nodi su <b>${tot}</b></p><div class="bar"><i style="width:${(100 * n / tot).toFixed(0)}%"></i></div>
    <div class="prog">${NODI.map(k => `<label><input type="checkbox" data-id="${k.id}" ${learned.has(k.id) ? 'checked' : ''}> <span>${esc(k.nome)}${k.esame ? ' <span class="badge esame">patente</span>' : ''}</span></label>`).join('')}</div>`;
  $('#progress').querySelectorAll('input').forEach(i => i.addEventListener('change', () => {
    i.checked ? learned.add(i.dataset.id) : learned.delete(i.dataset.id); saveLearned(); renderProgress();
  }));
}

// ------------------------------------------------------------ router
function route() {
  const h = location.hash.replace(/^#\/?/, '');
  const [sec, arg] = h.split('/');
  const tab = sec === 'allenati' ? 'allenati' : sec === 'progressi' ? 'progressi' : sec === 'info' ? 'info' : 'nodario';
  document.querySelectorAll('.view').forEach(v => v.classList.toggle('on', v.id === 'view-' + tab));
  document.querySelectorAll('.tabs a').forEach(a => a.classList.toggle('on', a.dataset.tab === tab));
  if (tab === 'nodario') {
    const id = sec === 'nodo' && arg ? arg : (current ? current.id : store.get('last', 'gassa-damante'));
    if (!current || current.id !== id) openKnot(id).then(() => store.set('last', id));
    if (viewer) viewer.resize();
  }
  if (tab === 'allenati' && !$('#trainer').innerHTML) trainer('riconosci');
  if (tab === 'progressi') renderProgress();
}

$('#q').addEventListener('input', renderList);
$('#onlyExam').addEventListener('change', renderList);
$('#families').addEventListener('click', (e) => { const b = e.target.closest('.item'); if (b) location.hash = '#/nodo/' + b.dataset.id; });
document.querySelectorAll('.mode').forEach(b => b.addEventListener('click', () => trainer(b.dataset.mode)));
addEventListener('hashchange', route);

(async () => {
  renderList();
  route();
  const wait = () => new Promise(r => { const t = setInterval(() => { if (viewer) { clearInterval(t); r(); } }, 50); });
  await wait();
  bindControls();
})();

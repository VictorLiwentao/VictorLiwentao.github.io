{
const D = JSON.parse(document.getElementById('data').textContent);
const E = D.E, M = D.meta, MAC = D.MAC, FINE = D.FINE, nC = D.nC, TRAD = D.TRAD;
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
document.documentElement.classList.add('js');
const P = D.P.map((p, i) => ({...p, i, mf: p.mac.indexOf(Math.max(...p.mac)), sur: p.sort.split(',')[0]}));
const C = P.slice(0, nC);
const byId = Object.fromEntries(P.map(p => [p.id, p]));
const LC = D.H.map((h, i) => ({...h, i, mf: h.mac.indexOf(Math.max(...h.mac))}));
const hById = Object.fromEntries(LC.map(h => [h.id, h]));
const FC = MAC.map((_, k) => `var(--f${k})`);
const TC = ['var(--wst)', 'var(--f0)', 'var(--f1)', 'var(--f2)', 'var(--f6)'];
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
const fmt = n => n.toLocaleString('en-US');
const fold = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const nice = d => new Date(d + 'T12:00:00').toLocaleDateString('en-GB', {day: 'numeric', month: 'long', year: 'numeric'});
const life = p => p.b ? (p.d ? `${p.b}–${p.d}` : `born ${p.b}`) : '';
const yr = y => y <= 0 ? `${1 - y} BCE` : `${y}`;
const hlife = h => { const b = h.b, d = h.d;
  if (b == null) return ''; if (d == null) return 'born ' + yr(b); if (d < b) return 'died ' + yr(d);
  if (d === b) return 'c. ' + (b <= 0 ? (b % 100 === 0 ? -b : 1 - b) + ' BCE' : b);
  if (b <= 0 && d <= 0) return `c. ${1 - b}–${1 - d} BCE`; if (b <= 0) return `c. ${1 - b} BCE – ${d} CE`; return `${b}–${d}`; };
const hb = h => (h.d != null && h.d < h.b) ? h.d : h.b;
const delta = (n, o) => o == null ? '<span class="new">new</span>' : n > o ? '+' + (n - o) : n === o ? '0' : '−' + (o - n);
const dTitle = (o, r) => o == null ? 'Not on the 2024 list' : '2024: ' + o + ' entries, rank ' + r;
const plink = p => `<a href="#p-${p.id}">${esc(p.a)}</a>`;
const fp = p => { const t = p.mac.reduce((a, b) => a + b, 0) || 1; return `<span class="fp">${p.mac.map((v, k) => v ? `<i style="width:${v / t * 100}%;background:${FC[k]}" title="${MAC[k]}: ${v}"></i>` : '').join('')}</span>`; };
const women = C.filter(p => p.g === 'f'), gknown = C.filter(p => p.g).length, bknown = C.filter(p => p.b).length;
const top100w = C.slice(0, 100).filter(p => p.g === 'f').length;
const living = C.filter(p => p.b && !p.d).length;
const med = a => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
const ICON = {play: '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M3 1.5v11l9.5-5.5z"/></svg>', pause: '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2.5 1.5h3.2v11H2.5zM8.3 1.5h3.2v11H8.3z"/></svg>',
  replay: '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M7 2a5 5 0 1 1-4.6 3H.6L3.4 1.6 6.2 5H4.1A3.4 3.4 0 1 0 7 3.6z"/></svg>'};
let SPEED = 1; try { SPEED = +localStorage.getItem('sepSpeed') || 1; } catch (e) {}
const SPEEDS = [[.25, '¼×', 'quarter'], [.5, '½×', 'half'], [1, '1×', 'normal'], [2, '2×', 'double']];
document.querySelectorAll('.speed-slot').forEach(el => { el.outerHTML = `<div class="speed" role="group" aria-label="Playback speed"><span>Speed</span>${SPEEDS.map(([v, l, n]) => `<button type="button" data-s="${v}" aria-pressed="${v === SPEED}" aria-label="${n} speed">${l}</button>`).join('')}</div>`; });
document.addEventListener('click', e => { const b = e.target.closest('.speed button'); if (!b) return; SPEED = +b.dataset.s;
  try { localStorage.setItem('sepSpeed', String(SPEED)); } catch (err) {}
  document.querySelectorAll('.speed button').forEach(x => x.setAttribute('aria-pressed', String(+x.dataset.s === SPEED))); });
const tryLab = (boxes, x, y, r, s, W, H, attrs = 'class="lab"', cw = 7, minX = 2) => { const w = s.length * cw;
  for (const [tx, ty, an, bx] of [[x + r + 4, y + 4, 'start', x + r + 4], [x - r - 4, y + 4, 'end', x - r - 4 - w], [x, y - r - 5, 'middle', x - w / 2], [x, y + r + 14, 'middle', x - w / 2]]) {
    const b = {x: bx, y: ty - 12, w, h: 15}; if (b.x < minX || b.x + w > W - 2 || b.y < 0 || b.y + b.h > H) continue;
    if (boxes.some(o => b.x < o.x + o.w && b.x + b.w > o.x && b.y < o.y + o.h && b.y + b.h > o.y)) continue;
    boxes.push(b); return `<text ${attrs} x="${tx.toFixed(1)}" y="${ty.toFixed(1)}" text-anchor="${an}">${esc(s)}</text>`; }
  return ''; };

/* ---------- race data (needed by the header) ---------- */
const RC = D.RACE, RY0 = RC.y0, NY = RC.y1 - RC.y0;
const RR = RC.R.map(r => ({p: P[r.i], c: r.c, pos: 0, op: 0}));
const LSEG = []; { let cur = -1;
  for (let k = 0; k <= NY; k++) { let best = cur, bv = cur >= 0 ? RR[cur].c[k] : 0;
    RR.forEach((r, j) => { if (r.c[k] > bv) { bv = r.c[k]; best = j; } });
    if (best < 0) continue;
    if (best !== cur) { LSEG.push({p: RR[best].p, y0: RY0 + k, y1: RY0 + k}); cur = best; } else LSEG[LSEG.length - 1].y1 = RY0 + k; } }
const lastSeg = LSEG[LSEG.length - 1], prevSeg = LSEG[LSEG.length - 2];

/* ---------- header ---------- */
const earliest = LC.reduce((a, h) => hb(h) < hb(a) ? h : a, LC[0]);
const monthYear = new Date(M.date + 'T12:00:00').toLocaleDateString('en-GB', {month: 'long', year: 'numeric'});
$('#hkick').textContent = `Stanford Encyclopedia of Philosophy · ${monthYear}`;
$('#lead').innerHTML = `Every one of its ${fmt(M.entries)} entries, read for the people it cites and names. ${fmt(LC.length + C.length)} philosophers recur across them, from ${esc(earliest.a)} to people still writing today.`;
const STATS = [[M.entries, 'SEP entries read, from first to last'], [LC.length, 'philosophers born before 1900, named in 5+ entries'],
  [C.length, 'philosophers born since 1900, cited in 30+ entries'], [D.W.length, 'works since 1900, cited in 16+ entries']];
$('#stats').innerHTML = STATS.map(([v, lab]) => `<div><dt><span class="cu" data-to="${v}" data-from="0">${fmt(v)}</span></dt><dd>${lab}</dd></div>`).join('');
const countUp = (el, dur = 1500) => { const to = +el.dataset.to, from = +el.dataset.from, isY = el.dataset.y === '1', f = v => isY ? String(v) : fmt(v);
  if (RM) return; const t0 = performance.now();
  const step = now => { const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3); el.textContent = f(Math.round(from + (to - from) * e)); if (k < 1) requestAnimationFrame(step); };
  el.textContent = f(from); requestAnimationFrame(step); };
document.querySelectorAll('#stats .cu').forEach(countUp);
$('#atitle').textContent = `The ${C.length} most-cited philosophers born since 1900`;
$('#wtitle').textContent = `The ${D.W.length} most-cited works since 1900`;
$('#msrc').innerHTML = `All ${fmt(M.entries)} entries in the SEP table of contents were downloaded on ${nice(M.date)} and the bibliography of each main entry parsed (${fmt(M.lines)} lines). Supplementary documents are not included. A work or author counts once per entry.`;
$('#mlife').textContent = `Birth and death years, gender, short descriptions and Wikipedia links come from Wikidata, matched by name and checked against publication dates; birth years are known for ${bknown} and gender for ${gknown} of the ${C.length}. Gender is Wikidata’s “sex or gender” property, corrected by hand where it is plainly wrong (it currently lists William Godwin as female). Dates for ancient and medieval figures are often approximate.`;
$('#mrace').textContent = `For every year from 1900 to 2026, each philosopher born since 1850 is credited with the number of today’s entries that cite at least one work they had first published by that year; works from before 1900 are left out. The replay shows how the present encyclopedia’s citations are spread over publication dates. It is not a history of earlier versions of the SEP, which began in 1995.`;
$('#mlong').textContent = `The long canon covers the ${LC.length} philosophers born before 1900 who have an SEP entry of their own (found through Wikidata’s SEP identifiers and the SEP table of contents) and are named in the text of at least five other entries. Historical figures are usually cited by title rather than by author, so they are counted by mention instead: a name is matched in each entry’s main text, bibliographies excluded, with checks for namesakes cited in the same entry, surnames used as ordinary words, and later authors cited by surname and year. Expect these counts to be approximate, though usually within a few entries. “Linked from” counts entries that link to their article. Figures with no entry of their own, such as Thales or Chrysippus, are not included. Traditions are assigned from the field of their own entry and their Wikidata description.`;
$('#mdata').innerHTML = `Data and code: <a href="https://victorliwentao.github.io/sep-most-cited/data/philosophers.csv">philosophers.csv</a>, <a href="https://victorliwentao.github.io/sep-most-cited/data/works.csv">works.csv</a>, <a href="https://victorliwentao.github.io/sep-most-cited/data/before1900.csv">before1900.csv</a>, and the <a href="https://github.com/VictorLiwentao/VictorLiwentao.github.io/tree/main/sep-most-cited">scripts that produced them</a>. Original analyses: <a href="https://schwitzsplinters.blogspot.com/2025/03/the-253-most-cited-works-in-stanford.html">most-cited works</a> and <a href="https://schwitzsplinters.blogspot.com/2024/08/the-378-most-cited-contemporary-authors.html">most-cited contemporary authors</a> by Eric Schwitzgebel. Not affiliated with the <a href="https://plato.stanford.edu/">Stanford Encyclopedia of Philosophy</a>.`;
$('#foot').innerHTML = `Counts compiled ${nice(M.date)} from <a href="https://plato.stanford.edu/">plato.stanford.edu</a>, following the method of Eric Schwitzgebel and Jordan Jackson. Biographical data from <a href="https://www.wikidata.org/">Wikidata</a>.`;

/* ---------- sections enter once ---------- */
const sections = [...document.querySelectorAll('section.band')];
const markSeen = el => { if (el.classList.contains('seen')) return; el.classList.add('seen'); el.dispatchEvent(new Event('seen')); };
if (RM || !('IntersectionObserver' in window)) sections.forEach(s => s.classList.add('seen'));
const sio = 'IntersectionObserver' in window ? new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { markSeen(e.target); sio.unobserve(e.target); } }), {rootMargin: '0px 0px -12% 0px'}) : null;
const introOn = (svg, ms) => { if (RM) return; svg.classList.add('intro'); setTimeout(() => svg.classList.remove('intro'), ms); };

/* ---------- shared tooltip ---------- */
const placeTip = (tip, fig, x, y, htmlStr) => { tip.innerHTML = htmlStr; tip.style.opacity = 1;
  const fw = fig.clientWidth, tw = tip.offsetWidth, th = tip.offsetHeight;
  tip.style.left = Math.max(0, Math.min(fw - tw, x + 14)) + 'px'; tip.style.top = (y - th - 12 < 0 ? y + 14 : y - th - 12) + 'px'; };
const ptip = p => `<b>${esc(p.a)}</b>${p.b ? ' <span style="color:var(--mute)">' + life(p) + '</span>' : ''}<br>Cited in <b>${p.n}</b> entries · rank ${p.p ? p.ra + ' (all eras)' : p.r}<br><span style="color:var(--mute)">${MAC[p.mf]}</span>`;

/* ---------- map ---------- */
const msv = $('#msv'), mtip = $('#mtip'), mfig = $('#mapfig'), mcap = $('#mcap');
const ms = {f: null, hl: null, con: null};
let mpos = {};
$('#mchips').innerHTML = MAC.map((m, k) => `<button type="button" class="chip" data-k="${k}" aria-pressed="false"><i style="background:${FC[k]}"></i>${m}</button>`).join('');
$('#names').innerHTML = [...P, ...LC.filter(h => h.pi == null)].map(p => `<option value="${esc(p.a)}">`).join('');
const maxN = C[0].n;
const mapDraw = () => {
  const W = msv.clientWidth, H = msv.clientHeight; if (!W) return;
  const narrow = W < 600, sc = Math.max(.62, Math.min(1, W / 1100));
  const m = {l: 18, r: 18, t: 18, b: 18};
  const X = v => m.l + v * (W - m.l - m.r), Y = v => H - m.b - v * (H - m.t - m.b);
  const R = p => (2.6 + 13 * Math.sqrt(p.n / maxN)) * sc;
  const boxes = [];
  let g = '';
  const fade = p => (ms.f != null && p.mf !== ms.f) ? .12 : .88;
  mpos = {};
  g += C.slice().sort((a, b) => b.n - a.n).map((p, k) => { const x = X(p.xy[0]), y = Y(p.xy[1]), r = R(p); mpos[p.id] = {x, y, r};
    return `<circle class="dot" style="--d:${Math.min(1500, k * 3.3).toFixed(0)}ms" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}" fill="${FC[p.mf]}" fill-opacity="${fade(p)}" stroke="var(--bg)" stroke-width="1.2"/>`; }).join('');
  D.REG.slice().sort((a, b) => b.n - a.n).forEach(r => { const w = r.t.length * 8.2, x = X(r.x), y = Y(r.y);
    const b = {x: x - w / 2, y: y - 14, w, h: 18};
    if (narrow && r.n < 12) return;
    if (b.x < 0 || b.x + w > W || boxes.some(o => b.x < o.x + o.w && b.x + b.w > o.x && b.y < o.y + o.h && b.y + b.h > o.y)) return;
    boxes.push(b); g += `<text class="reg" x="${x}" y="${y}" text-anchor="middle">${esc(r.t)}</text>`; });
  const K = narrow ? 10 : W < 900 ? 24 : 42;
  C.slice().sort((a, b) => b.n - a.n).filter(p => ms.f == null || p.mf === ms.f).slice(0, K).forEach(p => { const o = mpos[p.id]; g += tryLab(boxes, o.x, o.y, o.r, p.sur, W, H); });
  if (ms.hl && mpos[ms.hl]) { const o = mpos[ms.hl]; g += `<circle cx="${o.x}" cy="${o.y}" r="${o.r + 6}" fill="none" stroke="var(--ink)" stroke-width="2"/>`; }
  g += '<g id="mov"></g>';
  g += C.map(p => { const o = mpos[p.id]; return `<circle class="hit" data-id="${p.id}" cx="${o.x.toFixed(1)}" cy="${o.y.toFixed(1)}" r="${Math.max(9, o.r + 2).toFixed(1)}" fill="transparent"/>`; }).join('');
  msv.innerHTML = g;
  if (ms.con) showCon(ms.con, ms.soft);
};
const showCon = (id, soft) => {
  const mov = msv.querySelector('#mov'), p = byId[id], a = mpos[id]; if (!mov || !p || !a) return;
  const W = msv.clientWidth, H = msv.clientHeight;
  const nbs = p.nb.map(j => P[j]).filter(q => mpos[q.id]).slice(0, 6);
  let g = nbs.map((q, k) => { const b = mpos[q.id], len = Math.hypot(b.x - a.x, b.y - a.y);
    return `<line class="cl" x1="${a.x.toFixed(1)}" y1="${a.y.toFixed(1)}" x2="${b.x.toFixed(1)}" y2="${b.y.toFixed(1)}" stroke="${FC[p.mf]}" stroke-width="1.7" stroke-linecap="round" style="--len:${len.toFixed(0)};animation-delay:${k * 70}ms"/>`; }).join('');
  g += [...nbs, p].map(q => { const b = mpos[q.id]; return `<circle cx="${b.x.toFixed(1)}" cy="${b.y.toFixed(1)}" r="${b.r.toFixed(1)}" fill="${FC[q.mf]}" stroke="var(--bg)" stroke-width="1.5"/>`; }).join('');
  g += `<circle cx="${a.x.toFixed(1)}" cy="${a.y.toFixed(1)}" r="${(a.r + 5).toFixed(1)}" fill="none" stroke="var(--ink)" stroke-width="2"/>`;
  const boxes = [];
  g += tryLab(boxes, a.x, a.y, a.r + 5, p.a, W, H, 'class="lab" style="font-size:15px"', 7.8);
  nbs.forEach(q => { const b = mpos[q.id]; g += tryLab(boxes, b.x, b.y, b.r, q.sur, W, H); });
  mov.innerHTML = g; msv.classList.add('focus'); msv.classList.toggle('soft', !!soft);
};
const hideCon = () => { const mov = msv.querySelector('#mov'); if (mov) mov.innerHTML = ''; msv.classList.remove('focus'); ms.con = null; };
new ResizeObserver(mapDraw).observe(msv);
msv.addEventListener('pointerover', e => { const id = e.target.dataset && e.target.dataset.id; if (!id) return; ms.con = id; ms.soft = false; showCon(id); const o = mpos[id]; placeTip(mtip, mfig, o.x, o.y, ptip(byId[id])); });
msv.addEventListener('pointerout', e => { if (e.target.dataset && e.target.dataset.id) { mtip.style.opacity = 0; hideCon(); } });
msv.addEventListener('click', e => { const id = e.target.dataset && e.target.dataset.id; if (id) location.hash = 'p-' + id; });
$('#mchips').addEventListener('click', e => { const b = e.target.closest('.chip'); if (!b) return; const k = +b.dataset.k;
  ms.f = ms.f === k ? null : k; document.querySelectorAll('#mchips .chip').forEach(c => c.setAttribute('aria-pressed', String(+c.dataset.k === ms.f))); mapDraw(); });
$('#mq').addEventListener('change', e => { const q = fold(e.target.value.trim()); if (!q) return;
  const p = P.find(x => fold(x.a) === q) || P.find(x => fold(x.a).includes(q)); if (p) { location.hash = 'p-' + p.id; return; }
  const h = LC.find(x => fold(x.a) === q) || LC.find(x => fold(x.a).includes(q)); if (h) location.hash = 'h-' + h.id; });
// spotlight: a slow tour of the most-cited philosophers' constellations while nobody is pointing at the map
const tourList = (() => { const top = C.slice(0, 60), out = []; for (let k = 0; k < top.length; k++) out.push(top[(k * 17) % top.length]); return out; })();
const tour = {on: !RM, user: false, vis: false, k: 0};
const tourBtn = () => { const b = $('#mtour'); b.innerHTML = tour.on ? ICON.pause + '<span>Pause spotlight</span>' : ICON.play + '<span>Play spotlight</span>'; b.setAttribute('aria-pressed', String(tour.on)); };
const andList = a => a.length < 2 ? a.join('') : a.slice(0, -1).join(', ') + ' and ' + a[a.length - 1];
const tourStep = () => {
  if (!tour.on || tour.user || !tour.vis || !sheet.hidden || document.hidden || !msv.classList.contains('shown')) return;
  const p = tourList[tour.k++ % tourList.length]; ms.con = p.id; ms.soft = true; showCon(p.id, true);
  const nbs = p.nb.map(j => P[j]).filter(q => mpos[q.id]).slice(0, 4).map(q => esc(q.a));
  mcap.innerHTML = `<span class="k">Spotlight</span><b>${esc(p.a)}</b> is most often cited in the same entries as ${andList(nbs)}.`; mcap.classList.add('on');
};
const tourLoop = () => { tourStep(); setTimeout(tourLoop, 3800 / SPEED); };
setTimeout(tourLoop, 3800);
tourBtn();
$('#mtour').addEventListener('click', () => { tour.on = !tour.on; tourBtn(); if (!tour.on) { mcap.classList.remove('on'); hideCon(); } else tourStep(); });
mfig.addEventListener('pointerenter', () => { tour.user = true; mcap.classList.remove('on'); if (ms.soft) hideCon(); });
mfig.addEventListener('pointerleave', () => { tour.user = false; mtip.style.opacity = 0; hideCon(); });
if ('IntersectionObserver' in window) new IntersectionObserver(es => { tour.vis = es[0].isIntersecting; if (!tour.vis) { mcap.classList.remove('on'); } }, {threshold: .35}).observe(mfig);
const mapShow = () => { msv.classList.add('shown'); introOn(msv, 2700); setTimeout(tourStep, RM ? 0 : 2900); };
if (RM) msv.classList.add('shown');
$('#map').addEventListener('seen', mapShow);

/* ---------- philosophers table ---------- */
$('#af').innerHTML += MAC.map((m, k) => `<option value="${k}">${m}</option>`).join('');
const as = {all: false};
const renderA = () => {
  const q = fold($('#aq').value.trim()), f = $('#af').value, wo = $('#aw').checked, pre = $('#apre').checked, nw = $('#anew').checked;
  const base = pre ? [...P].sort((a, b) => b.n - a.n || a.a.localeCompare(b.a)) : C;
  const list = base.filter(p => (!q || fold(p.a + ' ' + p.w.map(w => w.t).join(' ')).includes(q)) && (f === '' || p.mf == f) && (!wo || p.g === 'f') && (!nw || (p.o == null && !p.p)));
  const filtered = q || f !== '' || wo || nw, shown = filtered || as.all ? list : list.slice(0, 50), mx = base[0].n;
  $('#abody').innerHTML = shown.map((p, k) => `<tr class="row" data-id="${p.id}" tabindex="0" style="--k:${k}"><td class="r">${pre ? p.ra : p.r}</td><td><div class="t"><a href="#p-${p.id}">${esc(p.a)}</a>${p.p ? '<span class="old">born before 1900</span>' : ''}</div><div class="by">${[life(p), p.w[0] ? esc(p.w[0].t) : ''].filter(Boolean).join(' · ')}</div></td><td class="nb"><div class="nbw"><span class="num">${p.n}</span><span class="barbox"><span style="display:block;height:100%;width:${p.n / mx * 100}%">${fp(p)}</span></span></div></td><td class="d" title="${p.p ? 'Not ranked in 2024' : dTitle(p.o, p.or)}">${p.p ? '–' : delta(p.n, p.o)}</td></tr>`).join('') || '<tr><td colspan="4">No philosophers match.</td></tr>';
  $('#acount').textContent = `Showing ${shown.length} of ${filtered ? list.length + ' matching' : base.length}`;
  $('#amore').hidden = filtered || as.all;
};
['#aq', '#af', '#aw', '#apre', '#anew'].forEach(s => $(s).addEventListener('input', renderA));
$('#amore').addEventListener('click', () => { as.all = true; renderA(); });
const rowGo = (e, attr, pre) => { if (e.target.closest('a')) return; const tr = e.target.closest('tr.row'); if (tr) location.hash = pre + tr.dataset[attr]; };
$('#abody').addEventListener('click', e => rowGo(e, 'id', 'p-'));
$('#abody').addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.matches('tr.row')) rowGo(e, 'id', 'p-'); });

/* ---------- race ---------- */
const rbars = $('#rbars'), ryear = $('#ryear'), rlead = $('#rlead'), rtick = $('#rtick'), rscrub = $('#rscrub'), rph = $('#rph');
rbars.innerHTML = RR.map(r => `<div class="rb"><a class="rn" href="#p-${r.p.id}" tabindex="-1"><span class="full">${esc(r.p.a)}</span><span class="short">${esc(r.p.sur)}</span></a><span class="rt"><span class="rf" style="background:${FC[r.p.mf]}"></span><span class="rv">0</span></span></div>`).join('');
const relem = [...rbars.children].map(el => ({el, f: el.querySelector('.rf'), v: el.querySelector('.rv')}));
const KL = Object.entries(RC.K).map(([y, v]) => ({y: +y, ...v})).filter(v => v.n >= 40).sort((a, b) => a.y - b.y);
const rs = {t: RM ? NY : 0, play: false, last: null, xmax: 20, started: false, tick: null, settleUntil: 0, settling: false};
const small = () => innerWidth <= 600;
const valAt = (c, t) => { const a = Math.floor(t), b = Math.min(NY, a + 1); return c[a] + (c[b] - c[a]) * (t - a); };
const rframe = dt => {
  const t = rs.t, N = small() ? 10 : 12, RH = small() ? 30 : 34, snap = dt == null;
  const vals = RR.map(r => valAt(r.c, t));
  const order = vals.map((v, k) => k).sort((a, b) => vals[b] - vals[a] || RR[a].p.ra - RR[b].p.ra);
  const top = Math.max(10, vals[order[0]]);
  rs.xmax = snap ? top : rs.xmax + (top - rs.xmax) * Math.min(1, dt * 5);
  rbars.style.height = (N * RH) + 'px';
  order.forEach((k, rank) => { const r = RR[k], e = relem[k], vis = rank < N && vals[k] > 0, tgt = vis ? rank : N;
    r.pos = snap ? tgt : r.pos + (tgt - r.pos) * Math.min(1, dt * 8);
    r.op = snap ? +vis : r.op + (+vis - r.op) * Math.min(1, dt * 7);
    e.el.style.transform = `translateY(${(r.pos * RH).toFixed(1)}px)`;
    e.el.style.opacity = r.op.toFixed(3); e.el.style.visibility = r.op < .02 ? 'hidden' : 'visible';
    e.f.style.width = (Math.min(1, vals[k] / rs.xmax) * 86).toFixed(2) + '%';
    e.v.textContent = Math.round(vals[k]); });
  const y = RY0 + Math.floor(t + 1e-6);
  ryear.textContent = y;
  let ld = LSEG[0]; for (const s of LSEG) if (s.y0 <= y) ld = s;
  rlead.innerHTML = `Leader in ${y}: <b>${esc(ld.p.a)}</b>${ld.y0 < y ? ` <span>(since ${ld.y0})</span>` : ''}${rs.play && ld !== LSEG[0] && y - ld.y0 <= 3 ? '<em>New leader</em>' : ''}`;
  let kk = null; for (const v of KL) if (v.y <= y) kk = v;
  if (kk !== rs.tick) { rs.tick = kk;
    rtick.innerHTML = kk ? `Most-cited work from ${kk.y}: <i>${esc(kk.t)}</i>, ${esc(kk.a)}, now cited in ${kk.n} entries` : '';
    if (kk && !RM && rs.play) rtick.animate([{opacity: 0, transform: 'translateY(4px)'}, {opacity: 1, transform: 'none'}], {duration: 350, easing: 'ease-out'}); }
  rph.style.left = (t / NY * 100) + '%';
  rscrub.setAttribute('aria-valuenow', y); rscrub.setAttribute('aria-valuetext', `${y}: ${ld.p.a} leads`);
};
const speed = t => (RY0 + t < 1950 ? 8 : 5.6);
const rbtn = () => { const b = $('#rplay'); b.innerHTML = rs.play ? ICON.pause + '<span>Pause</span>' : rs.t >= NY ? ICON.replay + '<span>Replay</span>' : ICON.play + '<span>Play</span>';
  b.setAttribute('aria-label', rs.play ? 'Pause the replay' : rs.t >= NY ? 'Replay from 1900' : 'Play the replay'); };
const settle = () => { rs.settleUntil = performance.now() + 900; if (rs.settling) return; rs.settling = true; let lt = performance.now();
  const f = now => { const dt = Math.min(.1, (now - lt) / 1000); lt = now; if (!rs.play) rframe(RM ? null : dt);
    if (now < rs.settleUntil && !rs.play) requestAnimationFrame(f); else rs.settling = false; };
  requestAnimationFrame(f); };
const rloop = now => { if (!rs.play) return; const dt = rs.last == null ? 1 / 60 : Math.min(.1, (now - rs.last) / 1000); rs.last = now;
  rs.t = Math.min(NY, rs.t + dt * speed(rs.t) * SPEED); rframe(dt);
  if (rs.t >= NY) { rs.play = false; rbtn(); settle(); $('#rsr').textContent = `${RY0 + NY}: ${lastSeg.p.a} leads.`; return; }
  requestAnimationFrame(rloop); };
const rplay = () => { if (rs.t >= NY) { rs.t = 0; rframe(null); } rs.play = true; rs.last = null; rbtn(); requestAnimationFrame(rloop); };
const rpause = () => { rs.play = false; rs.auto = false; rbtn(); settle(); };
$('#rplay').addEventListener('click', () => rs.play ? rpause() : rplay());
$('#rseg').innerHTML = LSEG.map(s => `<i style="flex:${s.y1 - s.y0 + 1};background:${FC[s.p.mf]}" title="${esc(s.p.a)}, ${s.y0}–${s.y1}"></i>`).join('');
$('#rlabs').innerHTML = LSEG.filter(s => s.y1 - s.y0 >= 14).map(s => `<span style="left:${(s.y0 - RY0) / NY * 100}%">${esc(s.p.sur)} ${s.y0}–${s.y1 >= RY0 + NY ? '' : String(s.y1).slice(2)}</span>`).join('');
$('#rtk').innerHTML = [1900, 1925, 1950, 1975, 2000, 2026].map(v => `<span style="left:${(v - RY0) / NY * 100}%">${v}</span>`).join('');
let drag = false;
const scrubTo = cx => { const r = rscrub.getBoundingClientRect(); rs.t = Math.max(0, Math.min(1, (cx - r.left) / r.width)) * NY; if (!rs.play) settle(); };
rscrub.addEventListener('pointerdown', e => { drag = true; rs.auto = false; if (rs.play) { rs.play = false; rbtn(); } rscrub.setPointerCapture(e.pointerId); scrubTo(e.clientX); });
rscrub.addEventListener('pointermove', e => { if (drag) scrubTo(e.clientX); });
rscrub.addEventListener('pointerup', () => { drag = false; rbtn(); });
rscrub.addEventListener('keydown', e => { const k = {ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1, ArrowUp: 1, PageDown: -10, PageUp: 10}[e.key];
  if (k == null && e.key !== 'Home' && e.key !== 'End') return; e.preventDefault(); if (rs.play) { rs.play = false; }
  rs.t = e.key === 'Home' ? 0 : e.key === 'End' ? NY : Math.max(0, Math.min(NY, Math.round(rs.t) + k)); rbtn(); settle();
  $('#rsr').textContent = `${RY0 + Math.round(rs.t)}: ${rscrub.getAttribute('aria-valuetext')}`; });
addEventListener('resize', () => { if (!rs.play) rframe(null); });
rframe(null); rbtn();
const russellYears = prevSeg.y1 - prevSeg.y0 + 1;
$('#rtitle').textContent = `${prevSeg.p.a} led for ${russellYears} years, until ${lastSeg.p.a} overtook him in ${lastSeg.y0}`;
$('#rsub').textContent = `Each bar counts the entries in today’s SEP that cite work a philosopher had published by the year shown. Press play to watch the present-day canon assemble, one publication year at a time.`;
$('#rnote').textContent = `Philosophers born since 1850; works first published from 1900 on. The strip under the bars shows who led in each year (${LSEG.map(s => `${s.p.sur} ${s.y0}${s.y1 > s.y0 ? '–' + (s.y1 >= RY0 + NY ? '' : s.y1) : ''}`).join(', ')}). Drag it, or use the arrow keys, to move through time.`;
if ('IntersectionObserver' in window && !RM) new IntersectionObserver(es => { const e = es[es.length - 1];
  if (e.intersectionRatio >= .45 && !rs.started) { rs.started = true; setTimeout(rplay, 350); }
  else if (!e.isIntersecting && rs.play) { rs.play = false; rs.auto = true; rbtn(); }
  else if (e.intersectionRatio >= .45 && rs.auto) { rs.auto = false; rplay(); } }, {threshold: [0, .45]}).observe($('#rbox'));

/* ---------- before 1900 ---------- */
const tsv = $('#tsv'), ttip = $('#ttip'), tfig = $('#tlfig');
const BK = [-650, 500, 1400, 1600, 1800, 1900], BW = [.17, .12, .12, .25, .34], ERA = ['Ancient', 'Medieval', 'Renaissance', 'Early modern', '19th century'];
const ts = {mode: 0, s: RM ? 1 : 0, play: false, last: null, x0: 0, x1: 1, els: [], sw: null, sy: null, W: 0};
const tcol = h => ts.mode ? (h.g === 'f' ? 'var(--acc)' : 'var(--men)') : TC[h.tr];
const LCD = LC.slice().sort((a, b) => b.m - a.m);
const LBL = {'Elisabeth of the Palatinate': 'Elisabeth', 'Émilie du Châtelet': 'du Châtelet', 'Alexander of Aphrodisias': 'Alexander', 'Anselm of Canterbury': 'Anselm', 'Nicholas of Cusa': 'Cusanus', 'Sophie de Grouchy': 'de Grouchy', 'Pseudo-Dionysius': 'Pseudo-Dionysius'};
const shortName = h => LBL[h.a] || (h.a.length <= 16 ? h.a : h.a.split(' ').pop());
const tX = y => { let acc = 0; for (let k = 0; k < 5; k++) { const a = BK[k], b = BK[k + 1]; if (y <= b || k === 4) return ts.x0 + (acc + Math.max(0, Math.min(1, (y - a) / (b - a))) * BW[k]) * (ts.x1 - ts.x0); acc += BW[k]; } };
const tInv = px => { const f = (px - ts.x0) / (ts.x1 - ts.x0); let acc = 0; for (let k = 0; k < 5; k++) { if (f <= acc + BW[k] || k === 4) return BK[k] + Math.max(0, Math.min(1, (f - acc) / BW[k])) * (BK[k + 1] - BK[k]); acc += BW[k]; } };
const tDraw = () => {
  const W = tsv.clientWidth, H = tsv.clientHeight; if (!W) return; const narrow = W < 600; ts.W = W;
  const m = {l: 38, r: 12, t: 36, b: 30}; ts.x0 = m.l; ts.x1 = W - m.r;
  const ly0 = Math.log(4.2), ly1 = Math.log(1000), Y = v => H - m.b - (Math.log(v) - ly0) / (ly1 - ly0) * (H - m.t - m.b);
  const R = h => (2 + 11.5 * Math.sqrt(h.m / LC[0].m)) * (narrow ? .8 : 1);
  const sx = ts.x0 + ts.s * (ts.x1 - ts.x0), on = x => x <= sx + .5 ? ' on' : '';
  let g = '';
  for (let k = 0; k < 5; k++) { const a = tX(BK[k]), b = tX(BK[k + 1]);
    if (k % 2) g += `<rect x="${a.toFixed(1)}" y="${m.t - 28}" width="${(b - a).toFixed(1)}" height="${H - m.b - m.t + 28}" fill="var(--soft)"/>`;
    const lbl = narrow ? ['Ancient', 'Medieval', 'Ren.', 'Early mod.', '19th c.'][k] : ERA[k]; if (lbl.length * (narrow ? 6.6 : 7.6) < b - a - 2) g += `<text class="era" x="${((a + b) / 2).toFixed(1)}" y="${m.t - 12}" text-anchor="middle">${lbl}</text>`; }
  [5, 10, 25, 50, 100, 250, 500].forEach(v => g += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(v).toFixed(1)}" y2="${Y(v).toFixed(1)}" stroke="var(--rule)"/><text x="${m.l - 6}" y="${(Y(v) + 4).toFixed(1)}" text-anchor="end">${v}</text>`);
  (narrow ? [[-599, '600 BCE'], [500, '500'], [1400, '1400'], [1600, '1600'], [1800, '1800'], [1900, '1900']] : [[-599, '600 BCE'], [1, '1 CE'], [250, '250'], [500, '500'], [1000, '1000'], [1400, '1400'], [1500, '1500'], [1600, '1600'], [1700, '1700'], [1800, '1800'], [1850, '1850'], [1900, '1900']])
    .forEach(([y, l], k, arr) => g += `<text x="${tX(y).toFixed(1)}" y="${H - 9}" text-anchor="${k === arr.length - 1 ? 'end' : k === 0 ? 'start' : 'middle'}">${l}</text>`);
  const pts = LCD.map(h => ({h, x: tX(hb(h)), y: Y(h.m), r: R(h)}));
  g += pts.map(o => `<circle class="hd${on(o.x)}" data-x="${o.x.toFixed(1)}" data-k="${o.h.i}" cx="${o.x.toFixed(1)}" cy="${o.y.toFixed(1)}" r="${o.r.toFixed(1)}" fill="${tcol(o.h)}" fill-opacity=".88" stroke="var(--bg)" stroke-width="1.1"/>`).join('');
  const boxes = [], K = narrow ? 8 : W < 900 ? 18 : 30;
  const want = [...new Set([...LCD.slice(0, K), ...LCD.filter(h => h.g === 'f').slice(0, narrow ? 2 : 6), ...LCD.filter(h => h.tr).slice(0, narrow ? 3 : 8)])];
  want.forEach(h => { const o = pts.find(q => q.h === h); g += tryLab(boxes, o.x, o.y, o.r, shortName(h), W, H - m.b, `class="lab tl${on(o.x)}" data-x="${o.x.toFixed(1)}"`, 7, m.l + 2); });
  g += `<line id="tsw" x1="${sx}" x2="${sx}" y1="${m.t - 28}" y2="${H - m.b}" stroke="var(--acc)" stroke-width="2" opacity="0"/><text id="tsy" class="lab" x="${sx}" y="${m.t + 6}" opacity="0" style="fill:var(--acc)"></text>`;
  g += pts.map(o => `<circle class="hh${on(o.x)}" data-x="${o.x.toFixed(1)}" data-h="${o.h.id}" cx="${o.x.toFixed(1)}" cy="${o.y.toFixed(1)}" r="${Math.max(8, o.r + 2).toFixed(1)}" fill="transparent"/>`).join('');
  tsv.innerHTML = g; ts.els = [...tsv.querySelectorAll('[data-x]')]; ts.sw = tsv.querySelector('#tsw'); ts.sy = tsv.querySelector('#tsy');
  tApply();
};
const tApply = () => {
  const sx = ts.x0 + ts.s * (ts.x1 - ts.x0), mid = ts.s > 0 && ts.s < 1;
  ts.els.forEach(el => el.classList.toggle('on', +el.dataset.x <= sx + .5));
  if (!ts.sw) return;
  ts.sw.setAttribute('x1', sx); ts.sw.setAttribute('x2', sx); ts.sw.setAttribute('opacity', mid ? 1 : 0);
  const right = sx > ts.W - 90; ts.sy.setAttribute('x', right ? sx - 6 : sx + 6); ts.sy.setAttribute('text-anchor', right ? 'end' : 'start');
  ts.sy.setAttribute('opacity', mid ? 1 : 0); ts.sy.textContent = yr(Math.round(tInv(sx)));
};
new ResizeObserver(tDraw).observe(tsv);
const TDUR = 9000;
const tbtn = () => { const b = $('#bplay'); b.innerHTML = ts.play ? ICON.pause + '<span>Pause</span>' : ts.s >= 1 ? ICON.replay + '<span>Replay the timeline</span>' : ICON.play + '<span>Play</span>'; };
const tloop = now => { if (!ts.play) return; const dt = ts.last == null ? 16 : Math.min(100, now - ts.last); ts.last = now;
  ts.s = Math.min(1, ts.s + dt / TDUR * SPEED); tApply(); if (ts.s >= 1) { ts.play = false; tbtn(); return; } requestAnimationFrame(tloop); };
const tplay = () => { if (ts.s >= 1) { ts.s = 0; tApply(); } ts.play = true; ts.last = null; tbtn(); requestAnimationFrame(tloop); };
$('#bplay').addEventListener('click', () => { if (ts.play) { ts.play = false; tbtn(); } else tplay(); });
tbtn();
if ('IntersectionObserver' in window && !RM) { const tio = new IntersectionObserver(es => { if (es[0].isIntersecting) { tio.disconnect(); setTimeout(tplay, 300); } }, {threshold: .4}); tio.observe(tfig); }
else { ts.s = 1; }
const tcount = k => LC.filter(h => h.tr === k).length;
const bLegend = () => { $('#blegend').innerHTML = ts.mode ? `<span><i class="sw" style="background:var(--acc)"></i>Women ${LC.filter(h => h.g === 'f').length}</span><span><i class="sw" style="background:var(--men)"></i>Men ${LC.filter(h => h.g !== 'f').length}</span>`
  : TRAD.map((t, k) => [t, k]).filter(([, k]) => tcount(k)).map(([t, k]) => `<span><i class="sw" style="background:${TC[k]}"></i>${t} ${tcount(k)}</span>`).join(''); };
bLegend();
$('#bmode').addEventListener('click', e => { const b = e.target.closest('.chip'); if (!b) return; ts.mode = +b.dataset.m;
  document.querySelectorAll('#bmode .chip').forEach(c => c.setAttribute('aria-pressed', String(c === b)));
  tsv.querySelectorAll('.hd').forEach(c => c.setAttribute('fill', tcol(LC[+c.dataset.k]))); bLegend(); });
const htip = h => `<b>${esc(h.a)}</b> <span style="color:var(--mute)">${hlife(h)}</span><br>Named in <b>${h.m}</b> entries · rank ${h.r}<br><span style="color:var(--mute)">${TRAD[h.tr]}</span>`;
tsv.addEventListener('pointerover', e => { const id = e.target.dataset && e.target.dataset.h; if (id) placeTip(ttip, tfig, +e.target.getAttribute('cx'), +e.target.getAttribute('cy'), htip(hById[id])); });
tsv.addEventListener('pointerout', e => { if (e.target.dataset && e.target.dataset.h) ttip.style.opacity = 0; });
tsv.addEventListener('click', e => { const id = e.target.dataset && e.target.dataset.h; if (id) location.hash = 'h-' + id; });
// headline, facts, table
const lw = LC.filter(h => h.g === 'f'), lnon = LC.filter(h => h.tr), pct = Math.round(LC[0].m / M.entries * 100);
$('#btitle').textContent = `Before 1900: ${LC[0].a} is named in ${pct}% of all SEP entries`;
$('#bsub').textContent = `${LC.length} philosophers born before 1900 have their own entry and are named in at least five others. ${LC[0].a}, ${LC[1].a} and ${LC[2].a} lead; ${lw.length} are women, and ${lnon.length} come from Arabic, Islamic and Jewish, Indian and Buddhist, Chinese or Japanese traditions. The SEP cites historical figures by title rather than by author, so here they are counted by mention.`;
const ancients = LC.filter(h => hb(h) < 500).length, c19 = LC.filter(h => hb(h) >= 1800).length;
$('#bfacts').innerHTML = [[LC[0].m, `entries name ${LC[0].a}`], [c19, 'born in the 19th century'], [ancients, 'born before 500 CE'], [lw.length, 'women, led by ' + lw[0].a], [lnon.length, 'from outside the Western tradition']].map(([a, b]) => `<div><b><span class="cu" data-to="${a}" data-from="0">${a}</span></b><span>${esc(b)}</span></div>`).join('');
$('#bth').textContent = `The long canon: all ${LC.length}`;
$('#bt').innerHTML += TRAD.map((t, k) => tcount(k) ? `<option value="${k}">${t}</option>` : '').join('');
const bs = {all: false};
const renderB = () => {
  const q = fold($('#bq').value.trim()), t = $('#bt').value, wo = $('#bw').checked;
  const list = LC.filter(h => (!q || fold(h.a + ' ' + h.wd).includes(q)) && (t === '' || h.tr == t) && (!wo || h.g === 'f'));
  const filtered = q || t !== '' || wo, shown = filtered || bs.all ? list : list.slice(0, 50), mx = LC[0].m;
  $('#bbody').innerHTML = shown.map((h, k) => `<tr class="row" data-h="${h.id}" tabindex="0" style="--k:${k}"><td class="r">${h.r}</td><td><div class="t"><a href="#h-${h.id}">${esc(h.a)}</a>${h.tr ? `<span class="tr-tag"><i class="sw" style="background:${TC[h.tr]}"></i>${TRAD[h.tr]}</span>` : ''}</div><div class="by">${[hlife(h), esc(h.wd)].filter(Boolean).join(' · ')}</div></td><td class="nb"><div class="nbw"><span class="num">${h.m}</span><span class="bar hide-s"><i style="width:${h.m / mx * 100}%"></i></span></div></td><td class="d">${h.l}</td></tr>`).join('') || '<tr><td colspan="4">No philosophers match.</td></tr>';
  $('#bcount').textContent = `Showing ${shown.length} of ${filtered ? list.length + ' matching' : LC.length}`;
  $('#bmore').hidden = filtered || bs.all;
};
['#bq', '#bt', '#bw'].forEach(s => $(s).addEventListener('input', renderB));
$('#bmore').addEventListener('click', () => { bs.all = true; renderB(); });
$('#bbody').addEventListener('click', e => rowGo(e, 'h', 'h-'));
$('#bbody').addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.matches('tr.row')) rowGo(e, 'h', 'h-'); });

/* ---------- profile sheet ---------- */
const sheet = $('#sheet'), scrim = $('#scrim'), sin = $('#sheetin');
let lastFocus = null;
const entryGroups = (es) => { const groups = {}; es.forEach(k => { const m = E[k][2]; (groups[m] = groups[m] || []).push(k); });
  return Object.keys(groups).sort((a, b) => groups[b].length - groups[a].length).map(m => `<details class="ent"><summary><i class="sw" style="background:${m >= 0 ? FC[m] : 'var(--rule)'}"></i>${m >= 0 ? MAC[m] : 'Other'}<b>${groups[m].length}</b></summary><p>${groups[m].map(k => `<a href="https://plato.stanford.edu/entries/${E[k][0]}/">${esc(E[k][1])}</a>`).join(', ')}</p></details>`).join(''); };
const fieldBlock = (p, verb) => `<div class="psec"><h3>Where they are ${verb}</h3><div class="bigfp">${p.mac.map((v, k) => v ? `<i style="flex:${v};background:${FC[k]}"></i>` : '').join('')}</div>
  <div class="fl">${p.mac.map((v, k) => [v, k]).filter(x => x[0]).sort((a, b) => b[0] - a[0]).map(([v, k]) => `<span><i class="sw" style="background:${FC[k]}"></i>${MAC[k]}<b>${v}</b></span>`).join('')}</div>
  <p class="note">Most-${verb === 'cited' ? 'citing' : 'naming'} areas: ${p.fine.map(([f, c]) => `${esc(FINE[f])} (${c})`).join(', ')}.</p></div>`;
const sbar = (prev, next, pre) => `<div class="sbar"><div class="nav">${prev ? `<button type="button" data-go="${pre}${prev.id}" aria-label="Previous: ${esc(prev.a)}">← Prev</button>` : ''}${next ? `<button type="button" data-go="${pre}${next.id}" aria-label="Next: ${esc(next.a)}">Next →</button>` : ''}</div><button type="button" id="pclose" aria-label="Close profile">Close ✕</button></div>`;
const showSheet = () => { const was = !sheet.hidden; if (!was) lastFocus = document.activeElement;
  sheet.hidden = false; scrim.hidden = false; document.body.style.overflow = 'hidden'; sheet.scrollTop = 0; $('#pclose').focus({preventScroll: true});
  sin.querySelectorAll('.pnums b').forEach(b => { const v = +b.textContent; if (Number.isFinite(v) && v > 0 && /^\d+$/.test(b.textContent)) { b.innerHTML = `<span class="cu" data-to="${v}" data-from="0">${v}</span>`; countUp(b.firstChild, 700); } });
  if (was && !RM) sin.animate([{opacity: 0, transform: 'translateY(8px)'}, {opacity: 1, transform: 'none'}], {duration: 260, easing: 'ease-out'}); };
const openProfile = id => {
  const p = byId[id]; if (!p) return;
  const rankLine = p.p ? `<b>${p.ra}</b><span>rank, all eras</span>` : `<b>${p.r}</b><span>rank of ${C.length}</span>`;
  const prevNext = p.p ? [] : [C[p.i - 1], C[p.i + 1]];
  const wmax = p.w.length ? p.w[0].n : 1;
  const h = p.h != null ? LC[p.h] : null;
  sin.innerHTML = `${sbar(prevNext[0], prevNext[1], 'p-')}
  <p class="pkick">${p.p ? 'Born before 1900 · cited as an author' : 'Most-cited philosophers born since 1900'}</p>
  <h2 class="pname" id="pname">${esc(p.a)}</h2>
  <p class="plife">${[life(p), esc(p.wd)].filter(Boolean).join(' · ')}</p>
  <div class="plinks">${p.wp ? `<a href="${esc(p.wp)}">Wikipedia</a>` : ''}${p.q ? `<a href="https://www.wikidata.org/wiki/${p.q}">Wikidata</a>` : ''}<a href="https://plato.stanford.edu/search/searcher.py?query=${encodeURIComponent(p.a)}">Search the SEP</a></div>
  <div class="pnums"><div>${rankLine}</div><div><b>${p.n}</b><span>of ${fmt(M.entries)} entries cite them</span></div><div><b>${p.p ? '–' : p.o == null ? 'new' : (p.n >= p.o ? '+' : '−') + Math.abs(p.n - p.o)}</b><span>${p.p ? 'not ranked in 2024' : p.o == null ? 'not on the 2024 list' : 'since 2024 (' + p.o + ', rank ' + p.or + ')'}</span></div></div>
  ${h ? `<a class="xlink" href="#h-${h.id}"><span>Named in the text of <b>${h.m}</b> entries · rank ${h.r} before 1900</span><span>Long-canon profile →</span></a>` : ''}
  ${fieldBlock(p, 'cited')}
  ${p.w.length ? `<div class="psec"><h3>Most-cited works</h3>${p.w.map(w => `<div class="pw"><span>${esc(w.t)} <em>${w.y || ''}</em></span><span class="bar"><i style="width:${w.n / wmax * 100}%"></i></span><b>${w.n}</b></div>`).join('')}<p class="note">Entries citing each work as first author.</p></div>` : ''}
  <div class="psec"><h3>Most often cited alongside</h3><div class="nbs">${p.nb.map(j => P[j]).map(q => `<a href="#p-${q.id}"><i class="sw" style="background:${FC[q.mf]}"></i>${esc(q.a)}</a>`).join('')}</div></div>
  <div class="psec"><h3>The ${p.n} entries that cite them</h3>${entryGroups(p.e)}</div>`;
  showSheet(); ms.hl = id; mapDraw();
};
const openHist = id => {
  const h = hById[id]; if (!h) return;
  const bib = h.pi != null ? P[h.pi] : null;
  const own = h.oe.map(k => `<a href="https://plato.stanford.edu/entries/${E[k][0]}/">${esc(E[k][1])}</a>`).join(', ');
  sin.innerHTML = `${sbar(LC[h.i - 1], LC[h.i + 1], 'h-')}
  <p class="pkick">The long canon · born before 1900</p>
  <h2 class="pname" id="pname">${esc(h.a)}</h2>
  <p class="plife">${[hlife(h), esc(h.wd)].filter(Boolean).join(' · ')}</p>
  <div class="plinks">${own ? '' : ''}${h.wp ? `<a href="${esc(h.wp)}">Wikipedia</a>` : ''}${h.q ? `<a href="https://www.wikidata.org/wiki/${h.q}">Wikidata</a>` : ''}<span style="color:var(--mute)"><i class="sw" style="background:${TC[h.tr]};margin-right:6px"></i>${TRAD[h.tr]}</span></div>
  <div class="pnums"><div><b>${h.r}</b><span>rank of ${LC.length} born before 1900</span></div><div><b>${h.m}</b><span>of ${fmt(M.entries)} entries name them</span></div><div><b>${h.l}</b><span>entries link to their article</span></div></div>
  ${own ? `<p class="pown"><b>SEP ${h.oe.length > 1 ? 'articles' : 'article'} on them:</b> ${own}</p>` : ''}
  ${bib ? `<a class="xlink" href="#p-${bib.id}"><span>Also cited as an author in <b>${bib.n}</b> bibliographies</span><span>Citation profile →</span></a>` : ''}
  ${fieldBlock(h, 'named')}
  <div class="psec"><h3>Most often named alongside</h3><div class="nbs">${h.nb.map(j => LC[j]).map(q => `<a href="#h-${q.id}"><i class="sw" style="background:${TC[q.tr]}"></i>${esc(q.a)}</a>`).join('')}</div></div>
  <div class="psec"><h3>The ${h.e.length} entries that name them</h3>${entryGroups(h.e)}<p class="note">Their own articles are not counted.</p></div>`;
  showSheet();
};
const closeProfile = () => { sheet.hidden = true; scrim.hidden = true; document.body.style.overflow = '';
  try { history.replaceState(null, '', location.pathname + location.search); } catch (e) { location.hash = 'philosophers'; }
  if (ms.hl) { ms.hl = null; mapDraw(); }
  if (lastFocus && lastFocus.focus) lastFocus.focus({preventScroll: true}); };
sheet.addEventListener('click', e => { if (e.target.closest('#pclose')) closeProfile(); const g = e.target.closest('[data-go]'); if (g) location.hash = g.dataset.go; });
scrim.addEventListener('click', closeProfile);
document.addEventListener('keydown', e => { if (e.key === 'Escape' && !sheet.hidden) closeProfile(); });
const route = () => { const h = decodeURIComponent(location.hash.slice(1));
  if (h.startsWith('p-')) openProfile(h.slice(2)); else if (h.startsWith('h-')) openHist(h.slice(2));
  else if (!sheet.hidden) { sheet.hidden = true; scrim.hidden = true; document.body.style.overflow = ''; } };
window.addEventListener('hashchange', route);

/* ---------- generations ---------- */
const gsv = $('#gsv'), gtip = $('#gtip'), gfig = $('#genfig');
const GP = C.filter(p => p.b && p.b >= 1895);
const gcol = p => p.g === 'f' ? 'var(--acc)' : p.g === 'm' ? 'var(--men)' : p.g === 'x' ? 'var(--nb)' : 'none';
const genDraw = () => {
  const W = gsv.clientWidth, H = gsv.clientHeight; if (!W) return; const narrow = W < 520;
  const m = {l: 40, r: 14, t: 14, b: 28};
  const x0 = 1898, x1 = Math.max(1982, ...GP.map(p => p.b + 2)), ly0 = Math.log(28), ly1 = Math.log(360);
  const X = v => m.l + (v - x0) / (x1 - x0) * (W - m.l - m.r), Y = v => H - m.b - (Math.log(v) - ly0) / (ly1 - ly0) * (H - m.t - m.b);
  let g = '';
  [30, 50, 100, 200, 300].forEach(v => g += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--rule)"/><text x="${m.l - 6}" y="${Y(v) + 4}" text-anchor="end">${v}</text>`);
  for (let v = 1900; v <= 1980; v += narrow ? 20 : 10) g += `<text x="${X(v)}" y="${H - 8}" text-anchor="middle">${v}</text>`;
  const order = GP.slice().sort((a, b) => (a.g === 'f') - (b.g === 'f'));
  g += `<text class="pyear" id="gyr" x="${m.l + 10}" y="${m.t + 40}"></text>`;
  g += order.map(p => `<circle class="gd${p.b > gs.y ? ' off' : ''}" data-b="${p.b}" cx="${X(p.b + .5).toFixed(1)}" cy="${Y(p.n).toFixed(1)}" r="${p.g ? 4.6 : 4}" fill="${gcol(p)}" ${p.g ? 'stroke="var(--bg)" stroke-width="1.2"' : 'stroke="var(--men)" stroke-width="1.5"'}/>`).join('');
  const boxes = [];
  const lab = [...new Set([...GP.slice().sort((a, b) => b.n - a.n).slice(0, narrow ? 4 : 9), ...GP.filter(p => p.g === 'f').sort((a, b) => b.n - a.n).slice(0, narrow ? 3 : 8)])];
  boxes.push({x: m.l + 6, y: m.t, w: 130, h: 46});
  lab.forEach(p => { g += tryLab(boxes, X(p.b + .5), Y(p.n), 3, p.sur, W, H - m.b, `class="lab${p.b > gs.y ? ' off' : ''}" data-b="${p.b}"${p.g === 'f' ? ' style="fill:var(--acc)"' : ''}`, 6.9); });
  g += GP.map(p => `<circle class="hit${p.b > gs.y ? ' off' : ''}" data-b="${p.b}" data-id="${p.id}" cx="${X(p.b + .5).toFixed(1)}" cy="${Y(p.n).toFixed(1)}" r="8" fill="transparent"/>`).join('');
  gsv.innerHTML = g; gApply();
};
const G0 = 1896, G1 = Math.max(1982, ...GP.map(p => p.b + 1));
const gs = {y: ('IntersectionObserver' in window && !RM) ? G0 : G1, play: false, last: null};
const gApply = () => { const y = gs.y, mid = gs.play || (y > G0 && y < G1);
  gsv.querySelectorAll('[data-b]').forEach(el => el.classList.toggle('off', +el.dataset.b > y));
  document.querySelectorAll('#decs .dec').forEach(el => el.classList.toggle('off', +el.dataset.d > y));
  const t = gsv.querySelector('#gyr'); if (t) t.textContent = mid ? Math.floor(y) : ''; };
const gbtn = () => { $('#gplay').innerHTML = gs.play ? ICON.pause + '<span>Pause</span>' : gs.y >= G1 ? ICON.replay + '<span>Replay by birth year</span>' : ICON.play + '<span>Play</span>'; };
const gloop = now => { if (!gs.play) return; const dt = gs.last == null ? 16 : Math.min(100, now - gs.last); gs.last = now;
  gs.y = Math.min(G1, gs.y + dt / 1000 * 10 * SPEED); gApply(); if (gs.y >= G1) { gs.play = false; $('#decs').classList.remove('live'); gbtn(); gApply(); return; } requestAnimationFrame(gloop); };
const gplay = () => { if (gs.y >= G1) { gs.y = G0; gApply(); } $('#decs').classList.add('live'); gs.play = true; gs.last = null; gbtn(); requestAnimationFrame(gloop); };
$('#gplay').addEventListener('click', () => { if (gs.play) { gs.play = false; gbtn(); } else gplay(); });
new ResizeObserver(genDraw).observe(gsv);
if ('IntersectionObserver' in window && !RM) { const gio = new IntersectionObserver(es => { if (es[0].isIntersecting) { gio.disconnect(); setTimeout(gplay, 250); } }, {threshold: .4}); gio.observe(gfig); }
gsv.addEventListener('pointerover', e => { const id = e.target.dataset && e.target.dataset.id; if (id) placeTip(gtip, gfig, +e.target.getAttribute('cx'), +e.target.getAttribute('cy'), ptip(byId[id])); });
gsv.addEventListener('pointerout', e => { if (e.target.dataset && e.target.dataset.id) gtip.style.opacity = 0; });
gsv.addEventListener('click', e => { const id = e.target.dataset && e.target.dataset.id; if (id) location.hash = 'p-' + id; });
const decs = {}; C.forEach(p => { if (!p.b) return; const d = Math.floor(p.b / 10) * 10; const o = decs[d] = decs[d] || {n: 0, w: 0}; o.n++; if (p.g === 'f') o.w++; });
const dkeys = Object.keys(decs).map(Number).filter(d => decs[d].n >= 3).sort(), dmax = Math.max(...dkeys.map(d => decs[d].n));
$('#decs').innerHTML = dkeys.map((d, k) => `<div class="dec" data-d="${d}" style="--k:${k}"><span>${d}s</span><span class="bar" style="width:${decs[d].n / dmax * 100}%"><i style="width:${decs[d].w / decs[d].n * 100}%"></i></span><span class="v">${decs[d].n} · ${decs[d].w} women (${Math.round(decs[d].w / decs[d].n * 100)}%)</span></div>`).join('');
const wShare = Math.round(women.length / gknown * 100);
const peak = dkeys.reduce((a, d) => decs[d].n > decs[a].n ? d : a, dkeys[0]);
$('#gtitle').textContent = `The largest cohort was born in the ${peak}s, and ${top100w} of the top 100 are women`;
$('#gsub').textContent = `Women are ${women.length} of the ${gknown} philosophers whose gender Wikidata records (${wShare}%), and only ${top100w} of the 100 most-cited. Their share is higher among those born after 1940 than before, but has not risen much since. Before 1900 it is ${lw.length} of ${LC.length}.`;
$('#gfacts').innerHTML = [[med(C.slice(0, 100).filter(p => p.b).map(p => p.b)), 'median birth year, top 100'], [med(C.filter(p => p.b).map(p => p.b)), `median birth year, all ${C.length}`],
  [living, 'still living, of ' + bknown + ' with known birth year'], [women.length, 'women on the list']].map(([a, b]) => `<div><b><span class="cu" data-to="${a}" data-from="${a > 1800 ? 1900 : 0}" data-y="${a > 1800 ? 1 : 0}">${a}</span></b><span>${b}</span></div>`).join('');

/* ---------- fields ---------- */
const fieldTotals = MAC.map((_, k) => E.filter(e => e[2] === k).length);
$('#fieldgrid').innerHTML = MAC.map((m, k) => { const top = C.slice().sort((a, b) => b.mac[k] - a.mac[k]).slice(0, 6), mx = top[0].mac[k];
  return `<div class="field" style="--fk:${k}"><h3><i class="sw" style="background:${FC[k]};width:12px;height:12px"></i>${m}</h3><p class="sub">${fieldTotals[k]} entries</p>${top.map((p, j) => `<div class="lrow" style="--k:${k * 2 + j}"><a href="#p-${p.id}">${esc(p.a)}</a><span class="bar"><i style="width:${p.mac[k] / mx * 100}%;background:${FC[k]}"></i></span><b>${p.mac[k]}</b></div>`).join('')}</div>`; }).join('');

/* ---------- works ---------- */
const W = D.W.map((w, i) => ({...w, i, yr: +String(w.y).slice(0, 4)}));
const wsv = $('#wsv'), wtip = $('#wtip'), wfig = $('#workfig');
const wmed = med(W.map(w => w.yr));
const short = (t, n) => { t = t.split(/:\s/)[0]; return t.length > n ? t.slice(0, n - 1).trim() + '…' : t; };
const surOf = w => { const a = w.a.split(' & ')[0].split(' '); return a[a.length - 1]; };
const workDraw = () => {
  const Wd = wsv.clientWidth, H = wsv.clientHeight; if (!Wd) return; const narrow = Wd < 520;
  const m = {l: 34, r: 12, t: 14, b: 28}, x0 = 1900, x1 = 2026, y0 = 10, y1 = 140;
  const X = v => m.l + (v - x0) / (x1 - x0) * (Wd - m.l - m.r), Y = v => H - m.b - (v - y0) / (y1 - y0) * (H - m.t - m.b);
  let g = '';
  for (let v = 25; v <= 125; v += 25) g += `<line x1="${m.l}" x2="${Wd - m.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--rule)"/><text x="${m.l - 6}" y="${Y(v) + 4}" text-anchor="end">${v}</text>`;
  for (let v = 1900; v <= 2020; v += narrow ? 40 : 20) g += `<text x="${X(v)}" y="${H - 8}" text-anchor="middle">${v}</text>`;
  const mt = `median ${wmed}`, mw = mt.length * 7, mR = X(wmed) + 8 + mw < Wd - m.r;
  const wo = ws2.y < W1 ? ' off' : '';
  g += `<line class="wmed${wo}" data-b="${W1}" x1="${X(wmed)}" x2="${X(wmed)}" y1="${m.t}" y2="${H - m.b}" stroke="var(--mute)" stroke-dasharray="3 4"/><text class="wmed${wo}" data-b="${W1}" x="${mR ? X(wmed) + 6 : X(wmed) - 6}" y="${m.t + 10}" text-anchor="${mR ? 'start' : 'end'}">${mt}</text>`;
  g += `<text class="pyear" id="wyr" x="${m.l + 10}" y="${m.t + 40}"></text><text class="pyear sub" id="wyn" x="${m.l + 12}" y="${m.t + 60}"></text>`;
  const seen = {}, pts = W.map(w => { const k = w.yr + '|' + w.n, j = seen[k] = (seen[k] || 0) + 1; return {w, x: X(w.yr) + (j - 1) * 3.2, y: Y(w.n)}; });
  g += pts.map(p => `<circle class="wd${p.w.yr > ws2.y ? ' off' : ''}" data-b="${p.w.yr}" cx="${p.x}" cy="${p.y}" r="4.5" fill="${p.w.o == null ? 'var(--f0)' : 'var(--acc)'}" stroke="var(--bg)" stroke-width="1.5"/>`).join('');
  const boxes = [{x: mR ? X(wmed) + 2 : X(wmed) - 8 - mw, y: m.t - 4, w: mw + 6, h: 18}, {x: m.l + 6, y: m.t, w: 130, h: 66}], K = narrow ? 4 : Wd < 760 ? 7 : 12, cw = 6.9;
  [...pts].sort((a, b) => b.w.n - a.w.n).slice(0, K).forEach(p => { const s = short(p.w.t, narrow ? 20 : 30) + ' · ' + surOf(p.w), w = s.length * cw;
    for (const [tx, ty, an, bx] of [[p.x + 8, p.y + 4, 'start', p.x + 8], [p.x - 8, p.y + 4, 'end', p.x - 8 - w], [p.x + 7, p.y - 6, 'start', p.x + 7], [p.x - 7, p.y - 6, 'end', p.x - 7 - w], [p.x + 7, p.y + 15, 'start', p.x + 7], [p.x - 7, p.y + 15, 'end', p.x - 7 - w], [p.x, p.y - 10, 'middle', p.x - w / 2], [p.x, p.y + 18, 'middle', p.x - w / 2]]) {
      const b = {x: bx, y: ty - 12, w, h: 15}; if (b.x < m.l || b.x + w > Wd - m.r || b.y < 0 || b.y + b.h > H - m.b) continue;
      if (boxes.some(o => b.x < o.x + o.w && b.x + b.w > o.x && b.y < o.y + o.h && b.y + b.h > o.y)) continue;
      boxes.push(b); g += `<text class="lab${p.w.yr > ws2.y ? ' off' : ''}" data-b="${p.w.yr}" x="${tx}" y="${ty}" text-anchor="${an}">${esc(s)}</text>`; break; } });
  g += pts.map(p => `<circle class="hit${p.w.yr > ws2.y ? ' off' : ''}" data-b="${p.w.yr}" data-i="${p.w.i}" cx="${p.x}" cy="${p.y}" r="10" fill="transparent"/>`).join('');
  wsv.innerHTML = g; wApply();
};
const W0 = 1899, W1 = 2027;
const ws2 = {y: ('IntersectionObserver' in window && !RM) ? W0 : W1, play: false, last: null};
const wApply = () => { const y = ws2.y, mid = ws2.play || (y > W0 && y < W1);
  wsv.querySelectorAll('[data-b]').forEach(el => el.classList.toggle('off', +el.dataset.b > y));
  const t = wsv.querySelector('#wyr'), n = wsv.querySelector('#wyn');
  if (t) t.textContent = mid ? Math.min(2026, Math.floor(y)) : ''; if (n) n.textContent = mid ? `${W.filter(w => w.yr <= y).length} works` : ''; };
const wbtn = () => { $('#wplay').innerHTML = ws2.play ? ICON.pause + '<span>Pause</span>' : ws2.y >= W1 ? ICON.replay + '<span>Replay by year</span>' : ICON.play + '<span>Play</span>'; };
const wloop = now => { if (!ws2.play) return; const dt = ws2.last == null ? 16 : Math.min(100, now - ws2.last); ws2.last = now;
  ws2.y = Math.min(W1, ws2.y + dt / 1000 * 13 * SPEED); wApply(); if (ws2.y >= W1) { ws2.play = false; wbtn(); wApply(); return; } requestAnimationFrame(wloop); };
const wplay = () => { if (ws2.y >= W1) { ws2.y = W0; wApply(); } ws2.play = true; ws2.last = null; wbtn(); requestAnimationFrame(wloop); };
$('#wplay').addEventListener('click', () => { if (ws2.play) { ws2.play = false; wbtn(); } else wplay(); });
new ResizeObserver(workDraw).observe(wsv);
if ('IntersectionObserver' in window && !RM) { const wio = new IntersectionObserver(es => { if (es[0].isIntersecting) { wio.disconnect(); setTimeout(wplay, 250); } }, {threshold: .4}); wio.observe(wfig); }
wsv.addEventListener('pointerover', e => { const i = e.target.dataset && e.target.dataset.i; if (i == null) return; const w = W[+i];
  placeTip(wtip, wfig, +e.target.getAttribute('cx'), +e.target.getAttribute('cy'), `<b>${esc(w.t)}</b><br>${esc(w.a)}, ${w.y}<br>Cited in <b>${w.n}</b> entries · rank ${w.r}<br>${w.o == null ? 'New to the list' : '2024: ' + w.o + ' entries'}`); });
wsv.addEventListener('pointerout', e => { if (e.target.dataset && e.target.dataset.i != null) wtip.style.opacity = 0; });
const ws = {all: false, open: new Set()};
wsv.addEventListener('click', e => { const i = e.target.dataset && e.target.dataset.i; if (i == null) return;
  $('#wq').value = ''; $('#wdec').value = ''; $('#wnew').checked = false; ws.all = true; ws.open.add(+i); renderW();
  const r = document.getElementById('w' + i); if (r) { r.scrollIntoView({block: 'center'}); r.focus({preventScroll: true}); } });
const decsW = [...new Set(W.map(w => Math.floor(w.yr / 10) * 10))].sort();
$('#wdec').innerHTML += decsW.map(d => `<option value="${d}">${d}s</option>`).join('');
const elinks = e => e.map(k => `<a href="https://plato.stanford.edu/entries/${E[k][0]}/">${esc(E[k][1])}</a>`).join(', ');
const wauthor = w => w.pi != null ? `<a href="#p-${P[w.pi].id}">${esc(w.a)}</a>` : esc(w.a);
const renderW = () => {
  const q = fold($('#wq').value.trim()), dec = $('#wdec').value, nw = $('#wnew').checked;
  const list = W.filter(w => (!q || fold(w.t + ' ' + w.a).includes(q)) && (!dec || Math.floor(w.yr / 10) * 10 == dec) && (!nw || w.o == null));
  const filtered = q || dec || nw, shown = filtered || ws.all ? list : list.slice(0, 50), mx = W[0].n;
  $('#wbody').innerHTML = shown.map((w, k) => { const op = ws.open.has(w.i);
    return `<tr class="row" id="w${w.i}" data-i="${w.i}" tabindex="0" aria-expanded="${op}" style="--k:${k}"><td class="r">${w.r}</td><td class="nb"><div class="nbw"><span class="num">${w.n}</span><span class="bar hide-s"><i style="width:${w.n / mx * 100}%"></i></span></div></td><td><div class="t">${esc(w.t)}</div><div class="by">${wauthor(w)}, ${w.y}</div></td><td class="d" title="${dTitle(w.o, w.or)}">${delta(w.n, w.o)}</td></tr>`
      + (op ? `<tr class="det"><td colspan="4">Cited in ${w.n} entries: ${elinks(w.e)}</td></tr>` : ''); }).join('') || '<tr><td colspan="4">No works match.</td></tr>';
  $('#wcount').textContent = `Showing ${shown.length} of ${filtered ? list.length + ' matching' : W.length}`;
  $('#wmore').hidden = filtered || ws.all;
};
['#wq', '#wdec', '#wnew'].forEach(s => $(s).addEventListener('input', renderW));
$('#wmore').addEventListener('click', () => { ws.all = true; renderW(); });
const wgo = e => { if (e.target.closest('a')) return; const tr = e.target.closest('tr.row'); if (!tr) return; const v = +tr.dataset.i;
  ws.open.has(v) ? ws.open.delete(v) : ws.open.add(v); renderW(); const again = document.getElementById('w' + v); if (again) again.focus({preventScroll: true}); };
$('#wbody').addEventListener('click', wgo);
$('#wbody').addEventListener('keydown', e => { if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('tr.row')) { e.preventDefault(); wgo(e); } });

/* ---------- CSV ---------- */
const csv = rows => rows.map(r => r.map(v => { v = v == null ? '' : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }).join(',')).join('\n');
const copy = (btn, text) => { const t = btn.textContent;
  (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(() => btn.textContent = 'Copied', () => btn.textContent = 'Copy failed').finally(() => setTimeout(() => btn.textContent = t, 1800)); };
$('#wcopy').addEventListener('click', e => copy(e.currentTarget, csv([['rank', 'citing_entries', 'author', 'year', 'title', 'entries_2024'], ...W.map(w => [w.r, w.n, w.a, w.y, w.t, w.o])])));
$('#acopy').addEventListener('click', e => copy(e.currentTarget, csv([['rank_born_1900_plus', 'rank_all_eras', 'citing_entries', 'name', 'born', 'died', 'main_field', 'most_cited_work', 'entries_2024'],
  ...[...P].sort((a, b) => a.ra - b.ra).map(p => [p.p ? '' : p.r, p.ra, p.n, p.a, p.b, p.d, MAC[p.mf], p.w[0] ? p.w[0].t : '', p.o])])));
$('#bcopy').addEventListener('click', e => copy(e.currentTarget, csv([['rank', 'entries_naming', 'entries_linking', 'name', 'born', 'died', 'tradition', 'sep_article'],
  ...LC.map(h => [h.r, h.m, h.l, h.a, h.b, h.d, TRAD[h.tr], h.oe.length ? 'https://plato.stanford.edu/entries/' + E[h.oe[0]][0] + '/' : ''])])));

/* ---------- changes ---------- */
const gainRows = (arr, label) => { const top = arr.filter(x => x.o != null && !x.p).sort((a, b) => (b.n - b.o) - (a.n - a.o) || b.n - a.n).slice(0, 12), mx = top[0].n - top[0].o;
  return top.map((x, k) => `<div class="gain" style="--k:${k}"><div>${label(x)}</div><span class="bar"><i style="width:${(x.n - x.o) / mx * 100}%"></i></span><span class="g">+${x.n - x.o}</span><span class="f">${x.o} → ${x.n}</span></div>`).join(''); };
$('#ga').innerHTML = gainRows(C, p => plink(p));
$('#gw').innerHTML = gainRows(W, w => esc(w.t) + ' (' + esc(surOf(w)) + ')');
const nas = C.filter(p => p.o == null);
$('#nah').textContent = `New to the philosophers list (${nas.length})`;
$('#na').innerHTML = nas.map(p => `<li><b>${p.n}</b> ${plink(p)} <span class="by">${life(p)}</span></li>`).join('');
const nws = W.filter(w => w.o == null);
$('#nwh').textContent = `New to the works list (${nws.length})`;
$('#nw').innerHTML = nws.map(w => `<li><b>${w.n}</b> ${esc(w.t.split(/:\s/)[0])} <span class="by">${esc(surOf(w))}, ${w.y}</span></li>`).join('');
$('#dwh').textContent = `Works that dropped below 16 entries (${D.X.length})`;
$('#dw').innerHTML = D.X.map(w => `<li><b>${w.o} → ${w.n}</b> ${esc(w.t.split(/:\s/)[0])} <span class="by">${esc(w.a.split(' ').pop())}, ${w.y}</span></li>`).join('');
const ratios = C.filter(p => p.o).map(p => p.n / p.o), mr = med(ratios);
$('#chnote').textContent = `The SEP grew from 1,778 main entries in summer 2024 to ${fmt(M.entries)} now (+${((M.entries / 1778 - 1) * 100).toFixed(1)}%), and the median philosopher on both lists gained ${((mr - 1) * 100).toFixed(0)}%. Some names new to the list reflect how this count separates people who share a surname, rather than real change.`;

/* ---------- header illustration: everyone, by year of birth ---------- */
const hsv = $('#hsv'), hfig = $('#herofig'), hTip = $('#htip');
const HDOT = [...LC.map(h => ({h: 'h-' + h.id, b: hb(h), n: h.m, f: h.g === 'f', s: LBL[h.a] || h.a.split(' ').pop(), o: h, old: true})),
  ...C.filter(p => p.b).map(p => ({h: 'p-' + p.id, b: p.b, n: p.n, f: p.g === 'f', s: p.sur, o: p, old: false}))];
const HBK = [-650, 500, 1400, 1600, 1800, 1900, Math.max(1985, ...HDOT.map(d => d.b + 4))];
const HERA = ['Ancient', 'Medieval', 'Renaissance', 'Early modern', '19th century', 'Since 1900'], HERAs = ['Anc.', 'Med.', 'Ren.', 'Early mod.', '19th c.', 'Since 1900'];
const hSeg = y => { for (let k = 0; k < 6; k++) if (y < HBK[k + 1] || k === 5) return k; };
const hwRaw = HERA.map((_, k) => Math.pow(Math.max(30, HDOT.filter(d => hSeg(d.b) === k).length), .85)), hwSum = hwRaw.reduce((a, b) => a + b, 0), HWt = hwRaw.map(v => v / hwSum);
const hX = (y, x0, x1) => { let acc = 0; for (let k = 0; k < 6; k++) { if (y < HBK[k + 1] || k === 5) return x0 + (acc + Math.max(0, Math.min(1, (y - HBK[k]) / (HBK[k + 1] - HBK[k]))) * HWt[k]) * (x1 - x0); acc += HWt[k]; } };
const hMax = Math.max(...HDOT.map(d => d.n));
const hLabels = (() => { const segs = HERA.map((_, k) => HDOT.filter(d => hSeg(d.b) === k).sort((a, b) => b.n - a.n)), out = [];
  const wOld = HDOT.filter(d => d.f && d.old).sort((a, b) => b.n - a.n)[0], wNew = HDOT.filter(d => d.f && !d.old).sort((a, b) => b.n - a.n)[0];
  for (let r = 0; r < 12; r++) segs.forEach(s => { if (s[r]) out.push(s[r]); if (r === 1) { [wOld, wNew].forEach(w => { if (w && !out.includes(w)) out.push(w); }); } });
  return [...new Set(out)]; })();
let hDrawn = false, hLastH = 0;
const hDraw = () => {
  const W = hsv.clientWidth; if (!W) return;
  const narrow = W < 600, x0 = 4, x1 = W - 4, padTop = 58, padBot = 40, maxPile = narrow ? 210 : 250;
  let sc = Math.sqrt(Math.min(1, W / 1240)), pts, pile;
  for (let it = 0; it < 4; it++) {
    const rmax = 13 * sc, pad = .9, JIT = [-2, 2, -4, 4, -6, 6, -8, 8, -10, 10];
    pts = HDOT.map(d => ({d, x: hX(d.b, x0, x1), r: (2 + 11 * Math.sqrt(d.n / hMax)) * sc, y: 0}));
    const bk = new Map(), BW = 16; pile = 0;
    pts.slice().sort((a, b) => a.r - b.r || a.x - b.x).forEach(p => {
      const cand = []; for (let i = Math.floor((p.x - p.r - rmax - pad - 11) / BW); i <= Math.floor((p.x + p.r + rmax + pad + 11) / BW); i++) { const a = bk.get(i); if (a) cand.push(...a); }
      const lift = px => { let y = -p.r;
        for (let g = 0; g < 2000; g++) { let hit = null;
          for (const o of cand) { const dx = o.x - px, rr = o.r + p.r + pad; if (dx * dx + (o.y - y) * (o.y - y) < rr * rr - .01) { hit = o; break; } }
          if (!hit) break; const dx = hit.x - px, rr = hit.r + p.r + pad; y = hit.y - Math.sqrt(Math.max(0, rr * rr - dx * dx)) - .02; }
        return y; };
      let bestX = p.x, y = lift(p.x);
      for (const off of JIT) { const px = p.x + off * sc, yy = lift(px); if (yy > y + .5) { y = yy; bestX = px; } }
      p.x = bestX; p.y = y; pile = Math.max(pile, -(y - p.r));
      const bi = Math.floor(p.x / BW); if (!bk.has(bi)) bk.set(bi, []); bk.get(bi).push(p); });
    if (pile <= maxPile) break; sc *= Math.sqrt(maxPile / pile) * .98;
  }
  const H = Math.ceil(pile + padTop + padBot), base = H - padBot;
  if (Math.abs(H - hLastH) > 1) { hLastH = H; hfig.style.height = H + 'px'; }
  const intro = !hDrawn && !RM; hDrawn = true;
  const dl = p => Math.round(p.x / W * 1900 + (-p.y / pile) * 380);
  let g = '';
  for (let k = 0; k < 6; k++) { const a = hX(HBK[k], x0, x1), b = hX(HBK[k + 1] - .001, x0, x1);
    if (k % 2) g += `<rect x="${a.toFixed(1)}" y="${(padTop - 20).toFixed(1)}" width="${(b - a).toFixed(1)}" height="${(base - padTop + 20).toFixed(1)}" fill="rgba(255,255,255,.045)"/>`;
    const lab = !narrow && HERA[k].length * 7.4 < b - a - 4 ? HERA[k] : HERAs[k]; if (lab.length * 6.6 < b - a - 2) g += `<text class="era" x="${((a + b) / 2).toFixed(1)}" y="${base + 22}" text-anchor="middle">${lab}</text>`; }
  g += `<line x1="${x0}" x2="${x1}" y1="${base + .5}" y2="${base + .5}" stroke="rgba(255,255,255,.4)"/>`;
  const x19 = hX(1900, x0, x1);
  g += `<line x1="${x19.toFixed(1)}" x2="${x19.toFixed(1)}" y1="${padTop - 20}" y2="${base}" stroke="rgba(255,255,255,.45)" stroke-dasharray="3 4"/>`;
  if (!narrow) g += `<text class="tk" x="${(x19 - 8).toFixed(1)}" y="${padTop - 2}" text-anchor="end">size: entries naming them</text><text class="tk" x="${(x19 + 8).toFixed(1)}" y="${padTop - 2}">size: entries citing them</text>`;
  g += pts.map(p => `<circle class="hd2" style="--d:${dl(p)}ms" cx="${p.x.toFixed(1)}" cy="${(base + p.y).toFixed(1)}" r="${p.r.toFixed(2)}" fill="${p.d.f ? '#ffcf6b' : '#fff'}" fill-opacity="${p.d.f ? 1 : .82}"/>`).join('');
  const boxes = narrow ? [] : [{x: x19 - 190, y: padTop - 15, w: 380, h: 16}], K = narrow ? 7 : W < 1000 ? 13 : 20, cw = 6.9;
  // name the peaks like a mountain panorama: each label floats just above the local skyline, with a thin leader to its dot
  let lead = '', labs = '';
  hLabels.slice(0, K).forEach(d => { const p = pts.find(q => q.d === d); if (!p) return; const w = d.s.length * cw, x = p.x, dy = base + p.y - p.r;
    let sky = dy; pts.forEach(q => { if (Math.abs(q.x - x) < w / 2 + q.r + 2) sky = Math.min(sky, base + q.y - q.r); });
    const lx = Math.max(w / 2 + 3, Math.min(W - w / 2 - 3, x));
    for (let lvl = 0; lvl < 3; lvl++) { const ty = sky - 7 - lvl * 16, bb = {x: lx - w / 2 - 3, y: ty - 12, w: w + 6, h: 15};
      if (bb.y < 2) break;
      if (boxes.some(o => bb.x < o.x + o.w && bb.x + bb.w > o.x && bb.y < o.y + o.h && bb.y + bb.h > o.y)) continue;
      boxes.push(bb);
      if (dy - (ty + 3) > 3) lead += `<line x1="${x.toFixed(1)}" x2="${x.toFixed(1)}" y1="${(ty + 4).toFixed(1)}" y2="${(dy - 1).toFixed(1)}" stroke="rgba(255,255,255,.55)" style="--d:${dl(p) + 260}ms"/>`;
      labs += `<text x="${lx.toFixed(1)}" y="${ty.toFixed(1)}" text-anchor="middle" style="--d:${dl(p) + 260}ms">${esc(d.s)}</text>`; break; } });
  g += lead + labs;
  g += pts.map(p => `<circle class="hit" data-h="${p.d.h}" cx="${p.x.toFixed(1)}" cy="${(base + p.y).toFixed(1)}" r="${Math.max(5, p.r + 1).toFixed(1)}" fill="transparent"/>`).join('');
  hsv.innerHTML = g;
  if (intro) { hsv.classList.add('intro'); setTimeout(() => hsv.classList.remove('intro'), 3200); }
};
new ResizeObserver(hDraw).observe(hsv);
const hByH = Object.fromEntries(HDOT.map(d => [d.h, d]));
hsv.addEventListener('pointerover', e => { const k = e.target.dataset && e.target.dataset.h; if (!k) return; const d = hByH[k], o = d.o;
  placeTip(hTip, hfig, +e.target.getAttribute('cx'), +e.target.getAttribute('cy'), d.old ? htip(o) : ptip(o)); });
hsv.addEventListener('pointerout', e => { if (e.target.dataset && e.target.dataset.h) hTip.style.opacity = 0; });
hsv.addEventListener('click', e => { const k = e.target.dataset && e.target.dataset.h; if (k) location.hash = k; });
const nShown = HDOT.filter(d => !d.old).length;
const hSpotList = (() => { const lab = new Set(hLabels.slice(0, 20)), pool = HDOT.filter(d => !lab.has(d)).sort((a, b) => b.n - a.n);
  const picks = [...pool.filter(d => d.f).slice(0, 10), ...pool.filter(d => d.old && d.o.tr).slice(0, 8), ...HERA.flatMap((_, k) => pool.filter(d => hSeg(d.b) === k).slice(0, 4))];
  const uniq = [...new Set(picks)].sort((a, b) => a.b - b.b), out = [];
  for (let k = 0; k < uniq.length; k++) out.push(uniq[(k * 11) % uniq.length]);
  return [...new Set(out)]; })();
const hs = {on: !RM, user: false, vis: true, k: 0};
const hspotBtn = () => { const b = $('#hspot'); b.innerHTML = hs.on ? ICON.pause + '<span>Pause spotlight</span>' : ICON.play + '<span>Spotlight</span>'; b.setAttribute('aria-pressed', String(hs.on)); };
const hClear = () => { hsv.querySelectorAll('.hring,.hhalo').forEach(n => n.remove()); hTip.style.opacity = 0; };
const hStep = () => {
  if (!hs.on || hs.user || !hs.vis || !sheet.hidden || document.hidden || hsv.classList.contains('intro')) return;
  const d = hSpotList[hs.k++ % hSpotList.length], c = hsv.querySelector(`.hit[data-h="${d.h}"]`); if (!c) return;
  hClear(); const x = +c.getAttribute('cx'), y = +c.getAttribute('cy'), r = Math.max(4, +c.getAttribute('r') - 1);
  const ns = 'http://www.w3.org/2000/svg';
  [['hhalo', r + 3], ['hring', r + 2]].forEach(([cls, rr]) => { const e = document.createElementNS(ns, 'circle'); e.setAttribute('class', cls); e.setAttribute('cx', x); e.setAttribute('cy', y); e.setAttribute('r', rr); hsv.insertBefore(e, hsv.querySelector('.hit')); });
  placeTip(hTip, hfig, x, y, `<span style="display:block;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--acc)">${d.old ? 'Before 1900' : 'Since 1900'}</span>${d.old ? htip(d.o) : ptip(d.o)}`); };
const hLoop = () => { hStep(); setTimeout(hLoop, 3600 / SPEED); };
setTimeout(hLoop, RM ? 0 : 3600);
hspotBtn();
$('#hspot').addEventListener('click', () => { hs.on = !hs.on; hspotBtn(); if (!hs.on) hClear(); else hStep(); });
$('#hreplay').innerHTML = ICON.replay + '<span>Replay</span>';
$('#hreplay').addEventListener('click', () => { hClear(); hDrawn = false; hsv.classList.remove('intro'); void hsv.getBoundingClientRect(); hDraw(); if (RM) return; });
hfig.addEventListener('pointerenter', () => { hs.user = true; hClear(); });
hfig.addEventListener('pointerleave', () => { hs.user = false; hTip.style.opacity = 0; });
if ('IntersectionObserver' in window) new IntersectionObserver(es => { hs.vis = es[0].isIntersecting; if (!hs.vis) hClear(); }, {threshold: .3}).observe(hfig);
$('#hcap').textContent = `Each dot is a philosopher, placed by year of birth (${C.length - nShown} with no recorded birth year are not shown). Size shows how many entries name them, before 1900, or cite them, after; gold dots are women. Time is stretched where philosophers are many. Point at a dot for a name; click for a profile.`;

if ('IntersectionObserver' in window && !RM) { const fio = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { fio.unobserve(e.target); e.target.querySelectorAll('.cu').forEach(el => countUp(el, 1300)); } }), {threshold: .6});
  document.querySelectorAll('.facts').forEach(f => fio.observe(f)); }
gbtn(); wbtn();
renderA(); renderB(); renderW(); route();
if (sio) sections.forEach(s => sio.observe(s));
}

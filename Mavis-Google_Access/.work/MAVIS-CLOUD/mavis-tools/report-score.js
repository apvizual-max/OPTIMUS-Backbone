#!/usr/bin/env node
/**
 * RAPORT ZILNIC — SCORING.
 *
 * Rulează ALEX-KIT/scoring.gs prin portul fidel (mavis-tools/score-port.js):
 * citește .gs-ul, aplică inserări pe anchor-uri EXACTE, refuză să ruleze dacă
 * un anchor lipsește. Nu rescriem logica de scoring.
 *
 * Ieșire: 4 secțiuni + "amânat" (locatie necunoscuta) + dropped, cu marcaj NEW
 * față de setul din ziua precedentă.
 */
const fs = require('fs');
const path = require('path');
const { loadEngine } = require('./score-port.js');

const DIR = __dirname;
const TODAY = process.argv[2] || '2026-10-23';
const PREV = process.argv[3] || path.join(DIR, 'jobs-2026-10-22.json');
const OUTJSON = process.argv[4] || path.join(DIR, `scoring-result-${TODAY}.json`);

// ---------- normalizare ----------
const deAccent = s => s.replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'")
  .replace(/&nbsp;/g, ' ').replace(/&euro;/g, 'EUR')
  .normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[șş]/g, 's').replace(/[țţ]/g, 't');

const CITY_RE = [
  [/\bbucharest\b|\bbucure[sș]ti\b|\bbucuresti\b/i, 'Bucuresti'],
  [/\bcluj\b/i, 'Cluj'],
  [/\bia[sș]i\b/i, 'Iasi'],
  [/\btimi[sș]oara\b/i, 'Timisoara'],
  [/\bbra[sș]ov\b/i, 'Brasov'],
  [/\bconstan[sș]a\b/i, 'Constanta'],
  [/\bsibiu\b/i, 'Sibiu'],
  [/\bcraiova\b/i, 'Craiova'],
  [/\bploie[sș]ti\b/i, 'Ploiesti'],
  [/\boradea\b/i, 'Oradea'],
  [/\bromania\b/i, 'Romania'],
];

function cityIn(text) {
  for (const [re, name] of CITY_RE) {
    const m = text.match(re);
    if (m) return { name, evidence: m[0], at: m.index };
  }
  return null;
}

/** Locație IQads: din textul anunțului + tipul de job. Fără oras => necunoscuta. */
function iqadsLoc(job) {
  const txt = deAccent(job.jd);
  const c = cityIn(txt);
  const types = job.jobType.map(t => deAccent(t));
  const hasRemote = types.some(t => /remote/i.test(t));
  const hasHybrid = types.some(t => /hybrid/i.test(t));
  const hasOffice = types.some(t => /at the office/i.test(t));
  const parts = [];
  if (c) parts.push(c.name);
  if (hasHybrid) parts.push('Hybrid (Office & Remote)');
  else if (hasRemote) parts.push('Remote');
  if (!parts.length) return { loc: '', why: 'nici oras, nici remote/hybrid in anunt' };
  if (!c && (hasRemote || hasHybrid)) {
    // doar remote, fara oras
    return { loc: parts.join(', '), why: 'remote/hybrid din tipul jobului, oras neprecizat' };
  }
  if (!c && hasOffice) return { loc: '', why: 'at the office, dar orasul nu apare in anunt' };
  return { loc: parts.join(', '), why: c ? `oras: "${c.evidence}"` : 'din tipul jobului' };
}

function iqadsEng(job) {
  // Tip job -> engagement, in ordinea scoring.gs: Full Time > Contract > Part Time
  const types = job.jobType.map(t => deAccent(t));
  const hasFT = types.some(t => /full\s*time/i.test(t));
  const hasCon = types.some(t => /contract|freelance|project/i.test(t));
  if (hasFT && !hasCon) return 'Full Time';
  if (hasCon && !hasFT) return 'Contract';
  if (hasFT && hasCon) return 'Full Time, Project Based';
  return job.jobType.join(', ') || '';
}

/**
 * ENGAGEMENT pentru designproject.io.
 *
 * MĂSURAT 2026-10-23: sursa are TREI câmpuri care se contrazic.
 *   1. JSON-LD employmentType  -> FULL_TIME pentru toate cele 26 (inutil)
 *   2. badge-ul din listing     -> "Full-time" pentru toate cele 26 (inutil)
 *   3. linia "Job Type:" din descriere -> corecta, si confirma in prosa
 *      (Trade Nation: "this is a contractor role"; Mindrift: "part-time freelance")
 * => sursa de adevar e (3). Daca "Job Type" lipseste, cadem pe (1) si marcam.
 */
function dpEng(jd, title) {
  const m = jd.match(/Job Type:\s*([^\n]+)/i);
  const v = (m ? m[1] : '').trim();
  const vl = v.toLowerCase();
  const tl = (title || '').toLowerCase();
  const hasFT = /full[\s_-]?time/.test(vl);
  const hasPart = /part[\s_-]?time/.test(vl);
  const hasContract = /contract|freelance|independent|temporary|consultanc/.test(vl)
    || /freelance|contractor/.test(tl);
  const hasIntern = /intern/.test(vl);
  const parts = [];
  if (hasFT) parts.push('Full Time');
  if (hasPart) parts.push('Part Time');
  if (hasContract) parts.push('Contract');
  if (hasIntern) parts.push('Intern');
  return { eng: parts.join(', ') || v || 'Full Time', from: m ? 'Job Type (descriere)' : 'capat de linie (fara Job Type)' };
}

/**
 * Diagnostic: 'remote' apare in text dar NU inseamna ca jobul e remote.
 * Exemple reale: "nu se lucreaza remote/hybrid" (negatie), "Remote Status: Hybrid" (eticheta).
 * Nu schimbam motorul (portul ramane fidel) — masuram impactul ca decizia sa fie a lui Alex.
 */
function remoteFalsePositive(jd) {
  const neg = jd.match(/(nu se lucreaza|nu lucram|fara|without|no)\s+[^.\n]{0,40}remote/gi);
  const label = jd.match(/Remote Status:\s*Hybrid/gi);
  if (neg) return { kind: 'negatie', hit: neg[0].trim() };
  if (label) return { kind: 'eticheta', hit: label[0].trim() };
  return null;
}

/**
 * Diagnostic: axa a fost ridicata de PROSA, nu de titlul rolului.
 * designproject.io serveste acum descrieri rescrise de AI (24k-33k caractere
 * fata de 71-1484 pe 2026-10-22). Proza contine cuvinte-cheie de tier
 * ("creatives", "senior") care ridica D/S artificial.
 * NU schimbam scorul — portul ramane fidel. Masuram si semnalam.
 */
const DISCIPLINE_D = [
  { score: 10, name: 'Creative Leadership', k: ['art director','creative director','creative lead','head of creative','brand director','advertising lead','campaign art director','ad conceptor','creative systems','art mid','senior creatives','creatives','art team'] },
  { score: 8, name: 'Core Design', k: ['graphic designer','visual designer','senior graphic','ui/ux','ux/ui','ux designer','ui designer','product designer','interaction designer','web designer','dtp designer','brand designer','identity designer','graphic design','visual design','social media','content designer','content specialist','creative designer'] },
  { score: 6, name: 'Media Production', k: ['video editor','motion designer','motion graphics','photographer','photo retoucher','studio lighting','content creator','ugc','video editing','photo','retouching'] },
  { score: 5, name: 'Emerging Sectors', k: ['ai designer','ai creative','ai performance','ai strategist','prompt engineer','design automation','generative','ai implementation','mcp','llm','comfy','midjourney','firefly','artificial intelligence'] },
  { score: 4, name: 'Adjacent Strategic', k: ['presentation designer','infographic','data visualization','dashboard','proposal','report design','deck'] },
];
const SENIOR_KW_D = ['senior','sr.','sr ','snr','art director','art mid','creatives','lead','director','head of','chief','principal','architect','expert','staff','manager','global','seasoned','experienced','established','10+ years','9+ years','8+ years','7+ years','6+ years'];
const _rxCache = new Map();
function hasWord(text, w) {
  let rx = _rxCache.get(w);
  if (!rx) {
    const esc = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    rx = new RegExp('(^|[^a-z0-9])' + esc + '($|[^a-z0-9])', 'i');
    _rxCache.set(w, rx);
  }
  return rx.test(text);
}
/** Returneaza cuvanta care a ridicat axa si de unde vine (titlu sau prosa). */
function axisFromProse(job) {
  const role = (job.role || '').toLowerCase();
  const txt = (job.jd || '').toLowerCase();
  const flags = [];
  for (const k of SENIOR_KW_D) {
    if (hasWord(role, k)) { flags.push({ axis: 'S', val: job.S, trigger: '"' + k + '"', from: 'titlu' }); break; }
  }
  if (!flags.length) {
    for (const k of SENIOR_KW_D) {
      if (hasWord(txt, k)) { flags.push({ axis: 'S', val: job.S, trigger: '"' + k + '"', from: 'prosa anuntului' }); break; }
    }
  }
  for (const t of DISCIPLINE_D) {
    // motorul parcurge TIER cu tier, iar in fiecare tier cauta titlu SAU text.
    // trebuie replicata exact ordinea, altfel diagnosticul minte.
    let hit = null, from = null;
    for (const k of t.k) { if (hasWord(role, k)) { hit = k; from = 'titlu'; break; } }
    if (!hit) for (const k of t.k) { if (hasWord(txt, k)) { hit = k; from = 'prosa anuntului'; break; } }
    if (hit) { flags.push({ axis: 'D', val: job.D, trigger: '"' + hit + '"', from, tier: t.name }); break; }
  }
  // doar axele care vin din prosa sunt semnalate ca risceptibile
  return flags.filter(f => f.from !== 'titlu');
}

function loadJobs() {
  const out = [];
  const iq = JSON.parse(fs.readFileSync(path.join(DIR, `jobs-iqads-${TODAY}.json`), 'utf8'));
  for (const j of iq.jobs) {
    const L = iqadsLoc(j);
    out.push({
      src: 'IQads', company: deAccent(j.company || ''), role: deAccent(j.title || j.slug),
      loc: L.loc, locWhy: L.why, eng: iqadsEng(j), jd: deAccent(j.jd),
      url: j.url, expiry: j.expiry, level: j.level, id: j.id, special: j.specialization.join(', '),
    });
  }
  const dp = JSON.parse(fs.readFileSync(path.join(DIR, `jobs-designproject-${TODAY}.json`), 'utf8'));
  for (const j of dp.jobs) {
    const e = dpEng(j.jd, j.ld && j.ld.title ? j.ld.title : j.title);
    out.push({
      src: 'designproject.io', company: deAccent(j.ld && j.ld.company ? j.ld.company : j.company || ''),
      role: deAccent(j.ld && j.ld.title ? j.ld.title : j.title), loc: deAccent(j.loc || ''),
      locWhy: 'din JSON-LD (adresa) + "Remote Status" din descriere', eng: e.eng, engWhy: e.from, jd: deAccent(j.jd),
      url: j.url, date: j.date, expiry: j.ld && j.ld.validThrough, salary: j.ld && j.ld.baseSalary,
    });
  }
  return out;
}

const key = j => (j.company + '|' + j.role).toLowerCase().replace(/\s+/g, ' ').trim();

/**
 * POSTARI GENUIN NOI (nu doar "absente din raportul de ieri").
 *
 * - IQads: ad ID-ul crește monoton cu postarea. Comparăm cu cel mai mare ID
 *   din setul de ieri -> peste acesta, anuntul e aparut dupa ultima rulare.
 * - designproject.io: comparam data de publicare cu data ultimei rulari.
 */
const MON = { Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5, Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11 };
function parseDpDate(s) {
  const m = (s || '').match(/([A-Z][a-z]{2}) (\d{1,2}), (\d{4})/);
  if (!m || MON[m[1]] === undefined) return null;
  return new Date(Date.UTC(+m[3], MON[m[1]], +m[2]));
}
function computeGenuinelyNew(jobs, prev) {
  const prevIds = (prev.jobs || []).map(j => { const m = (j.url || '').match(/adjob\/(\d+)/); return m ? +m[1] : 0; });
  const maxPrev = prevIds.length ? Math.max(...prevIds) : 0;
  const iq = jobs.filter(j => j.src === 'IQads' && j.id && +j.id > maxPrev)
    .map(j => ({ company: j.company, role: j.role, id: j.id, url: j.url, expiry: j.expiry }));
  // data ultimei rulari = data din numele fisierului PREV (jobs-AAAA-LL-ZZ.json)
  const prevRunDate = new Date((path.basename(PREV).match(/(\d{4}-\d{2}-\d{2})/) || [, '2026-10-22'])[1] + 'T00:00:00Z');
  const dp = jobs.filter(j => j.src === 'designproject.io')
    .map(j => ({ j, d: parseDpDate(j.date) }))
    .filter(x => x.d && x.d > prevRunDate)
    .map(x => ({ company: x.j.company, role: x.j.role, date: x.j.date, url: x.j.url }));
  const dpAll = jobs.filter(j => j.src === 'designproject.io').map(j => parseDpDate(j.date)).filter(Boolean);
  const newestDp = dpAll.length ? new Date(Math.max(...dpAll.map(d => d.getTime()))) : null;
  return {
    maxPrevIqadsId: maxPrev, newIqads: iq, newDesignproject: dp,
    newestDesignprojectDate: newestDp ? newestDp.toISOString().slice(0, 10) : null,
  };
}

function main() {  const eng = loadEngine();
  const engFixed = loadEngine({ fixAi: true });
  const jobs = loadJobs();

  // --save-set: salveaza setul NORMALIZAT (company/role/loc/eng/jd) pentru data
  // curenta, ca sa poata fi folosit drept PREV la rularea urmatoare.
  // Nu atinge scoring-result-ul. Aceeasi normalizare, nu o reimplementare.
  if (process.argv.includes('--save-set')) {
    const out = path.join(DIR, `jobs-${TODAY}.json`);
    fs.writeFileSync(out, JSON.stringify({ _meta: { date: TODAY, count: jobs.length, note: 'set normalizat pentru comparatie zilnica' }, jobs }, null, 2));
    console.log(`set normalizat salvat: ${out} (${jobs.length} joburi)`);
    return;
  }

  const prev = JSON.parse(fs.readFileSync(PREV, 'utf8'));
  const prevKeys = new Set(prev.jobs.map(key));
  const PREV_DATE = (path.basename(PREV).match(/(\d{4}-\d{2}-\d{2})/) || [, '2026-10-22'])[1];
  const prevResPath = path.join(DIR, `scoring-result-${PREV_DATE}.json`);
  const prevRes = fs.existsSync(prevResPath)
    ? JSON.parse(fs.readFileSync(prevResPath, 'utf8')) : null;
  const prevScored = new Set();
  if (prevRes) {
    for (const k of Object.keys(prevRes.sections)) prevRes.sections[k].forEach(x => prevScored.add((x.company + '|' + x.role).toLowerCase().trim()));
    (prevRes.amanzat || []).forEach(x => prevScored.add((x.company + '|' + x.role).toLowerCase().trim()));
    (prevRes.dropped || []).forEach(x => prevScored.add((x.company + '|' + x.role).toLowerCase().trim()));
  }

  const kept = [], dropped = [];
  for (const j of jobs) {
    const r = eng.scoreJob(j.company, j.role, j.loc, j.eng, j.jd, '');
    const rf = engFixed.scoreJob(j.company, j.role, j.loc, j.eng, j.jd, '');
    // data de expirare, normalizata la AAAA-LL-ZZ.
    // MĂSURAT 2026-10-24: la designproject.io validThrough = datePosted + 30 zile
    // pentru toate cele 26 de joburi (24 exacte, 2 cu o zi diferita de fus orar).
    // Deci E o data de expirare reala, nu o derivatie inutila — se marcheaza.
    const expDate = (j.expiry || '').slice(0, 10) || null;
    const meta = { src: j.src, url: j.url, expiry: expDate, date: j.date || null, level: j.level || null,
                   expKind: 'expiră',
                   expired: !!(expDate && expDate < TODAY),
                   loc: j.loc, locWhy: j.locWhy, eng: j.eng, engWhy: j.engWhy || null, special: j.special || null, salary: j.salary || null,
                   inPrevSet: prevKeys.has(key(j)), inPrevScored: prevScored.has(key(j)), jd: j.jd };
    const fp = remoteFalsePositive(j.jd);
    if (fp) meta.remoteFalsePositive = fp;
    if (r.dropped) { dropped.push({ ...r, ...meta, reasonFixed: rf.dropped ? rf.reason : null }); continue; }
    const row = { ...r, ...meta, scoreFixed: rf.dropped ? null : rf.score,
      sectionFixed: rf.dropped ? null : rf.section, isNew: !prevKeys.has(key(j)) };
    const pf = axisFromProse(row);
    if (pf.length) row.axisFromProse = pf;
    kept.push(row);
  }
  kept.sort((a, b) => b.score - a.score);
  const sections = { 1: [], 2: [], 3: [], 4: [] };
  const amanzat = [];
  for (const k of kept) { if (k.section === 0) amanzat.push(k); else sections[k.section].push(k); }

  const out = {
    date: TODAY, prevDate: PREV_DATE, stats: { total: jobs.length, kept: kept.length, dropped: dropped.length, amanzat: amanzat.length,
      newJobs: kept.filter(k => k.isNew).length, newDropped: dropped.filter(k => !k.inPrevSet).length },
    sections, amanzat, dropped,
    remoteFalsePositives: kept.filter(k => k.remoteFalsePositive),
    axisFromProse: kept.filter(k => k.axisFromProse).map(k => ({ role: k.role, company: k.company, score: k.score, section: k.section, flags: k.axisFromProse })),
    newList: kept.filter(k => k.isNew).map(k => ({ role: k.role, company: k.company, score: k.score, section: k.section, src: k.src })),
    genuinelyNew: computeGenuinelyNew(jobs, prev),
  };
  fs.writeFileSync(OUTJSON, JSON.stringify(out, null, 2));

  console.log('STATISTICI: ' + JSON.stringify(out.stats));
  for (const s of [1, 2, 3, 4]) {
    console.log(`\n=== SECTIUNEA ${s} (${sections[s].length}) ===`);
    sections[s].forEach(x => console.log(`  ${String(x.score).padStart(6)} | ${x.tag} | ${x.role.slice(0, 44).padEnd(44)} | ${x.company.slice(0, 28).padEnd(28)} | S${x.S} D${x.D} L${x.L} E${x.E} ${x.isNew ? '<< NEW' : ''}`));
  }
  console.log(`\n=== AMANAT — locatie necunoscuta (${amanzat.length}) ===`);
  amanzat.forEach(x => console.log(`  ${String(x.score).padStart(6)} | ${x.role.slice(0, 44).padEnd(44)} | ${x.company.slice(0, 28).padEnd(28)} | ${x.isNew ? '<< NEW' : ''}`));
  console.log(`\n=== DROPPED (${dropped.length}) ===`);
  dropped.forEach(x => console.log(`  ${x.role.slice(0, 42).padEnd(42)} | ${x.company.slice(0, 26).padEnd(26)} | ${String(x.reason).slice(0, 78)} ${!x.inPrevSet ? '<< NEW' : ''}`));
  console.log(`\n=== 'remote' FALS POZITIV (${out.remoteFalsePositives.length}) ===`);
  out.remoteFalsePositives.forEach(x => console.log(`  ${x.role.slice(0, 40).padEnd(40)} | ${x.company.slice(0, 24).padEnd(24)} | ${x.remoteFalsePositive.kind}: "${x.remoteFalsePositive.hit}" | L=${x.L}`));
  console.log(`\n=== AXA RIDICATA DE PROSA, NU DE TITLU (${out.axisFromProse.length}) ===`);
  out.axisFromProse.forEach(x => console.log(`  ${x.role.slice(0, 40).padEnd(40)} | ${x.company.slice(0, 24).padEnd(24)} | ${x.flags.map(f => f.axis + '=' + f.val + ' via ' + f.trigger + ' (' + f.from + ')').join(' ; ')}`));
  console.log('\n-> ' + OUTJSON);
}

main();

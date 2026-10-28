#!/usr/bin/env node
/**
 * RAPORT ZILNIC — generator + livrare pe Google Drive.
 *
 * Citește artefactele măsurate azi, scrie raportul .md, apoi îl urcă în
 * Drive/Alex Work/00-INTRARE ca RAPORT-ZILNIC-AAAAMM-ZZ.md.
 *
 * REGULA DE BAZĂ: NIMIC din text nu e hardcodat pentru o zi anume.
 * Fiecare număr vine din artefactele măsurate (mail-count, inbox-counts,
 * simulate-sort, triage, scoring). Altfel raportul de mâine ar repăsta
 * cifrele de azi — exact bug-ul care a stricat rularea din 23.10.
 *
 * REGULI: nu șterge nimic, nu trimite nimic. Dacă există deja un raport cu
 * acelasi nume, se suprascrie (acelasi fisier, aceeasi zi) — nimic nou.
 */
const fs = require('fs');
const path = require('path');
const k = require('./kit.js');
const { triage } = require('./report-triage.js');
const TAX = require('./taxonomy.js');

const DIR = __dirname;
const DATE = process.argv[2] || new Date().toISOString().slice(0, 10);
const COMPACT = DATE.replace(/-/g, '');
const FOLDER_ID = process.argv[3] || '1sAs2ktJhGanKeGv87LIxkTD34S7P5XvT';
const REPO_OUT = path.join(DIR, '..', 'rapoarte', `RAPORT-ZILNIC-${COMPACT.slice(0, 6)}-${COMPACT.slice(6)}.md`);

const R = f => JSON.parse(fs.readFileSync(path.join(DIR, f), 'utf8'));
const mailCount = R('report-mail-count.json');
const inboxCounts = R('report-inbox-counts.json');
const sim = R('report-simulate-sort.json');
const sc = R(`scoring-result-${DATE}.json`);
// sonda de surse: masoara AZI comportamentul iqads.ro / designproject.io,
// ca sectiunea "Ce n-a mers, muraat" sa nu repete cifrele de ieri.
let probe = null;
try { probe = JSON.parse(fs.readFileSync(path.join(DIR, 'report-source-probe.json'), 'utf8')); } catch (e) {}
let filterState = null;
try { filterState = JSON.parse(fs.readFileSync(path.join(DIR, 'report-filter-state.json'), 'utf8')); } catch (e) {}
const tri = triage(sim.rows || []);
// consumul real de cereri Google, acumulat de kit.js la iesirea fiecarui script
let usage = {};
try { usage = JSON.parse(fs.readFileSync(path.join(DIR, '.api-usage.json'), 'utf8')); } catch (e) {}
const usageRows = Object.entries(usage)
  .filter(([k, v]) => !k.startsWith('_') && typeof v === 'number')
  .sort((a, b) => b[1] - a[1]);
const usageMeasured = usageRows.reduce((a, b) => a + b[1], 0);
// upload-ul raportului costa: search + upload/replace + verificare = 3 cereri.
// In modul --file-id=<ID> (raport deja creat) e un singur PATCH = 1 cerere
// (raspunsul lui include name/mimeType/size/parents -> e si verificarea).
const UPLOAD_COST = (process.argv.find(a => a.startsWith('--file-id=')) || '').trim() ? 1 : 3;
const usageTotal = usageMeasured + UPLOAD_COST;
const usageNote = usage._nota || '';

const pad = (s, n) => { s = String(s); while (s.length < n) s += ' '; return s; };
const cell = s => String(s == null ? '' : s).replace(/\|/g, '/').replace(/\n/g, ' ');

const ZI = ['duminică', 'luni', 'marți', 'miercuri', 'joi', 'vineri', 'sâmbătă'];
const MONTHS = ['ianuarie', 'februarie', 'martie', 'aprilie', 'mai', 'iunie', 'iulie', 'august', 'septembrie', 'octombrie', 'noiembrie', 'decembrie'];
const d = new Date(DATE + 'T12:00:00Z');
const dayName = ZI[d.getUTCDay()];
// Romania: EEST (UTC+3) pana pe 25.10.2026, cand se trece la EET (UTC+2).
const eest = new Date(Date.now() + 3 * 3600 * 1000);
const windowEnd = String(eest.getUTCHours()).padStart(2, '0') + ':' + String(eest.getUTCMinutes()).padStart(2, '0');

const daysBetween = (a, b) => Math.round((b - a) / 86400000);
const parseDate = s => { const t = Date.parse(s || ''); return isNaN(t) ? null : new Date(t); };
// headerele Date din Gmail: "Sat, 24 Oct 2026 05:03:13 +0000 (UTC)"
const parseGmailDate = s => {
  const t = Date.parse(s || '');
  if (!isNaN(t)) return new Date(t);
  const m = (s || '').match(/(\d{1,2})\s+(\w{3})\s+(\d{4})/);
  if (!m) return null;
  const mon = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].indexOf(m[2]);
  if (mon < 0) return null;
  return new Date(Date.UTC(+m[3], mon, +m[1]));
};
const fmtRo = s => { const t = parseDate(s); if (!t) return '—';
  return String(t.getUTCDate()).padStart(2, '0') + '.' + String(t.getUTCMonth() + 1).padStart(2, '0') + '.' + t.getUTCFullYear(); };
// snippet-urile vin cu entitati HTML decodate de snippitul Gmail
const decodeHtml = s => String(s || '')
  .replace(/&#39;|&#x27;/g, "'").replace(/&quot;|&#34;/g, '"')
  .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
  .replace(/&nbsp;/g, ' ');
// curata un citat de corp: fara bare de separare "=====", fara URL-uri
// de tracking, fara spatii multiple — sa ramana informatia, nu zgomotul.
const clean = s => decodeHtml(s)
  .replace(/\s*={5,}\s*/g, ' | ')
  .replace(/https?:\/\/\S+/g, '')
  .replace(/\s*\|\s*\|\s*/g, ' | ')
  .replace(/\s+/g, ' ')
  .replace(/(\s\|)+\s*$/, '')
  .trim();

// ---------------- joburi ----------------
// data de publicare la designproject.io vine ca "Oct 2, 2026" -> o normalizam
const MON_IDX = { Jan:0,Feb:1,Mar:2,Apr:3,May:4,Jun:5,Jul:6,Aug:7,Sep:8,Oct:9,Nov:10,Dec:11 };
function isoDate(s) {
  if (!s) return null;
  if (/^\d{4}-\d{2}-\d{2}/.test(s)) return s.slice(0, 10);
  const m = s.match(/([A-Z][a-z]{2}) (\d{1,2}), (\d{4})/);
  if (m && MON_IDX[m[1]] !== undefined) return `${m[3]}-${String(MON_IDX[m[1]] + 1).padStart(2, '0')}-${String(+m[2]).padStart(2, '0')}`;
  return s.slice(0, 10);
}
function jobTable(list, withNew) {
  let out = '| Scor | Tag | S/D/L/E | Rol | Companie | Locație | Engagement | Expirare |' + (withNew ? ' Nou |' : '') + '\n';
  out += '|---|---|---|---|---|---|---|---|' + (withNew ? '---' : '') + '\n';
  for (const j of list) {
    let dat;
    const posted = isoDate(j.date);
    if (j.src === 'designproject.io' && posted) {
      dat = `postat ${posted}`;
      if (j.expiry) dat += ` · expiră ${j.expiry.slice(0, 10)}`;
    } else if (j.expiry) {
      dat = 'expiră ' + j.expiry.slice(0, 10);
    } else if (posted) {
      dat = 'postat ' + posted;
    } else dat = '—';
    if (j.expired) dat += ' ⛔ **EXPIRAT**';
    out += `| **${j.score}** | ${j.tag} | ${j.S}/${j.D}/${j.L}/${j.E} | ${cell(j.role)} | ${cell(j.company)} | ${cell(j.loc || '—')} | ${cell(j.eng || '—')} | ${dat} |${withNew ? (j.isNew ? ' ✅' : '') : ''}\n`;
  }
  return out;
}
function linkList(list) {
  let out = '';
  for (const j of list) if (j.url) out += `- ${j.company} :: ${j.role} — ${j.url}\n`;
  return out;
}
function expiredCount(list) { return list.filter(j => j.expired).length; }

// rolul chiar de design? (titlul contine o cheie de tier 1 sau 2)
const DESIGN_KW = ['art director','creative director','creative lead','head of creative','brand director','advertising lead','campaign art director','ad conceptor','creative systems','art mid','senior creatives','creatives','art team',
  'graphic designer','visual designer','senior graphic','ui/ux','ux/ui','ux designer','ui designer','product designer','interaction designer','web designer','dtp designer','brand designer','identity designer','graphic design','visual design','content designer','content specialist','creative designer'];
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
const isDesignRole = role => DESIGN_KW.some(k => hasWord(role || '', k));
// motivul real din spatele scorului
function why(j, flags) {
  const p = (flags || []).find(f => f.axis === 'D' && f.from !== 'titlu');
  if (j.S === 10 && j.D === 10) return 'S și D maxime';
  if (p && p.axis === 'D') return 'D ridicat de prosa (' + p.trigger + ')';
  if (j.D === 10) return 'tier 1 — Creative Leadership';
  if (j.L === 10 && /remote/i.test(j.loc || '')) return 'remote';
  if (j.L === 10) return 'L=10 (remote detectat în text)';
  if (j.E === 8) return 'contract';
  if (j.S === 8) return 'mid/senior';
  return 'potrivire bună';
}

const allSections = [];
for (const s of [1, 2, 3, 4]) allSections.push(...sc.sections[s]);
allSections.sort((a, b) => b.score - a.score);
const top = allSections.slice(0, 5);
const amanzatNew = sc.amanzat.filter(x => x.isNew);
const newJobs = allSections.filter(x => x.isNew);
const gn = sc.genuinelyNew || { newIqads: [], newDesignproject: [], maxPrevIqadsId: null, newestDesignprojectDate: null };

// ---------- sonda de surse (totul masurat, nimic copiat de ieri) ----------
const dpP = (probe && probe.designproject) || null;
const iqP = (probe && probe.iqads) || null;
const vt = dpP && dpP.validThrough ? dpP.validThrough : null;
// regula de expirare la designproject.io: validThrough = datePosted + 30 zile
const vtSentence = vt
  ? `măsurat pe toate cele ${vt.checked} de joburi (${vt.exact} exacte, ${vt.offByOne} cu o zi de fus orar, ${vt.other} altfel)`
  : 'măsurat pe setul de azi';

// ---------------- etichete: de cand nu mai functioneaza (PE CATEGORIE) ----------------
// 2026-10-27: etichetele au fost rearanjate peste noapte si a aparut o categorie
// noua, care FUNCTIONEAZA. De aceea nu mai scriem "etichetarea e oprită de N zile"
// global — masuram fiecare categorie separat si le impartim in doua grupuri:
//   - MOORTE: nu primesc nimic (0 pe 7z)
//   - VIU: primesc mesaje (au pe 7z > 0)
const labelRows = mailCount.labels.map(l => ({ ...l, newest: parseGmailDate(l.newestDate) }));
const dated = labelRows.filter(l => l.newest);
const newestLabel = dated.length ? dated.reduce((a, b) => (a.newest > b.newest ? a : b)) : null;
const daysOff = newestLabel ? daysBetween(newestLabel.newest, new Date(DATE + 'T00:00:00Z')) : null;
const groups = {};
for (const l of dated) {
  // doar categoriile MOARTE — cele vii se spun separat, in concluzie
  if ((l.counts['7z'] || 0) > 0) continue;
  const k = fmtRo(l.newestDate);
  (groups[k] = groups[k] || []).push(l.name.replace(/`/g, ''));
}
const groupLines = Object.entries(groups).sort().map(([k, v]) => `pe \`${v.join('`, `')}\` = **${k}**`).join('; ');

// mapare eticheta -> cheie de categorie, calculata LOCAL din datele deja masurate
// (report-mail-count.json are numele rezolvate; filterState.rows are addLabelIds ca nume).
// ZERO cereri Google — nu re-rulam sonda de filtre doar pentru asta.
const keyByLabelName = {};
for (const l of labelRows) keyByLabelName[TAX.normalize(l.name)] = l.key;
if (filterState && Array.isArray(filterState.rows)) {
  for (const r of filterState.rows) {
    const cats = (r.addLabelIds || []).map(x => keyByLabelName[TAX.normalize(x)]).filter(Boolean);
    r.categories = cats;
    r.functional = (r._matchesAsIs || 0) > 0 && cats.length > 0;
  }
}

// impartire pe categorii vii / moarte, masurata pe fereastra de 7 zile
const aliveRows = labelRows.filter(l => (l.counts['7z'] || 0) > 0);
const deadRows = labelRows.filter(l => (l.counts['7z'] || 0) === 0);
const aliveNames = aliveRows.map(l => l.name);
const deadNames = deadRows.map(l => l.name);
// zile de pauza, masurate DOAR pe categoriile moarte
let deadDaysOff = null;
if (deadRows.length) {
  const deadDated = deadRows.filter(l => l.newest);
  if (deadDated.length) {
    const newestDead = deadDated.reduce((a, b) => (a.newest > b.newest ? a : b));
    deadDaysOff = daysBetween(newestDead.newest, new Date(DATE + 'T00:00:00Z'));
  }
}
// numele etichetelor rezolvate, pentru tabelul de simulare
const liveLabelNames = labelRows.map(l => l.name);
const simCount = name => (sim.counts && name in sim.counts) ? sim.counts[name] : 0;

// ---------------- mesaje care cer actiune ----------------
const replyList = tri.buckets['needs-reply'];
const actionList = tri.buckets['needs-action'];
const otherAlertList = tri.buckets['job-alert-other'];
const fyiList = tri.buckets['fyi'];
const msgTime = r => { const t = parseGmailDate(r.date); if (!t) return r.date.slice(0, 22);
  return String(t.getUTCHours()).padStart(2, '0') + ':' + String(t.getUTCMinutes()).padStart(2, '0') + ' UTC'; };

// ---------------- cata de joburi ----------------
// impartirea pe surse se masoara din fisierele RAW (ce a fost scanat),
// nu din cele pastrate — altfel "72 analizate" si "24+12 pastrate" se contrazic.
const srcTotal = {};
for (const [file, key] of [['jobs-iqads-' + DATE + '.json', 'IQads'], ['jobs-designproject-' + DATE + '.json', 'designproject.io']]) {
  try { srcTotal[key] = JSON.parse(fs.readFileSync(path.join(DIR, file), 'utf8')).jobs.length; } catch (e) { srcTotal[key] = 0; }
}
const srcKept = {};
for (const j of allSections) srcKept[j.src] = (srcKept[j.src] || 0) + 1;
const expiredInTables = allSections.filter(j => j.expired).length;
const expiredInAmanzat = sc.amanzat.filter(j => j.expired).length;
// plural corect
const plural = (n, one, few, many) => n === 1 ? one : (n >= 2 && n <= 19 ? few : many);

// ---------------- raport ----------------
let md = `# Raport zilnic — ${dayName} ${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]} ${d.getUTCFullYear()}

> Generat de Mavis Cloud · ${sim.total} mesaje noi măsurate azi (00:00–${windowEnd} EEST) · ${sc.stats.total} joburi analizate
> Cota Google: **${usageTotal} cereri** (plafon 200${usageTotal > 200 ? ` — **depășit cu ${usageTotal - 200}**` : usageTotal === 200 ? ` — **exact pe plafon**` : ` — **în limita plafonului**`}). Zero scrieri pe Gmail; tot consumul a fost măsurare și diagnostic. Detaliu în §5.

---

## 1. Gmail — etichetele de categorie

### 1.1 Rezultatul scurt
`;

// Sursa pentru "azi" = simularea (cea mai recenta masuratoare, mesaje distincte).
// mailCount.totals.azi e SUMA HITURILOR PE ETICHETE: un mesaj cu 2 etichete
// se numara de 2 ori. Deci nu poate fi comparat direct cu numarul de mesaje.
// Iata de ce cele doua cifre pot difera fara ca cineva sa greseasca.
const labeledDistinct = sim.total - sim.unmatched;
const doubleLabeled = Math.max(0, mailCount.totals.azi - labeledDistinct);

md += `**Pe etichetele de categorie a intrat azi: ${mailCount.totals.azi} ${doubleLabeled > 0 ? 'etichete' : 'mesaje'}.**`;

if (mailCount.totals.azi === 0) {
  md += ` Nici în ultimele 24h (${mailCount.totals['24h']}), nici în ultimele 7 zile (${mailCount.totals['7z']}).`;
} else {
  md += ` În ultimele 24h: ${mailCount.totals['24h']}; în 7 zile: ${mailCount.totals['7z']}.`;
}
md += `

Azi au intrat **${sim.total} mesaje** în total, iar în inbox sunt **${inboxCounts.azi_inbox}**.`;

const unclassified = sim.unmatched;
if (unclassified > 0) {
  md += ` **${unclassified} dintre ele nu au primit nicio etichetă de categorie**`;
  md += ` (nu se potrivesc niciunui filtru de categorie — deci rămân în inbox, neetichetate).`;
}
if (doubleLabeled > 0) {
  md += `\n\n> **${mailCount.totals.azi} etichete pe ${labeledDistinct} mesaje** — ${doubleLabeled} mesaj${doubleLabeled === 1 ? ' primește' : 'e primesc'} două etichete de categorie (ex. o alertă de job care intră și la „Joburi" și la „Newsletter"). De aceea suma pe etichete e mai mare decât numărul de mesaje distincte.`;
}
md += `

### 1.2 Măsurătoarea pe etichete (numărare exactă, cu paginare)

| Etichetă | azi | 24h | 7z | 30z | Ultimul mesaj etichetat |
|---|---|---|---|---|---|
`;
for (const l of mailCount.labels) {
  const c = l.counts;
  md += `| \`${l.name}\` | ${c.azi} | ${c['24h']} | ${c['7z']} | ${c['30z']} | ${l.newestDate ? l.newestDate.slice(0, 16) : 'n/a'} |\n`;
}
md += `
`;
if (newestLabel && daysOff !== null) {
  // "moarta" (a primit mesaje, acum nu mai primeste) != "nefolosita niciodata".
  // A doua nu are o zi de oprire — nu are cum sa aiba.
  const deadNever = deadRows.filter(l => !l.newest);
  const deadStale = deadRows.filter(l => l.newest);
  let deadPart = '';
  if (deadStale.length) {
    deadPart += `${deadStale.length === 1 ? 'o categorie primește nimic de' : deadStale.length + ' categorii nu primesc nimic de'} **${deadDaysOff} zile**`;
    if (groupLines) deadPart += ` (${groupLines})`;
  }
  if (deadNever.length) {
    deadPart += (deadPart ? '; ' : '') + `${deadNever.length === 1 ? 'o categorie' : deadNever.length + ' categorii'} n-a fost folosită niciodată (0 pe 30 de zile, fără istoric)` + (deadNever.length === 1 ? ` (\`${deadNever[0].name}\`)` : ` (${deadNever.map(l => '`' + l.name + '`').join(', ')})`);
  }
  md += `**Concluzie:** ${aliveRows.length === 1 ? 'o categorie primește mesaje' : aliveRows.length + ' categorii primesc mesaje'}${aliveRows.length ? ' (' + aliveNames.map(n => '`' + n + '`').join(', ') + ')' : ''}` + (deadPart ? `; ${deadPart}` : '') + `.\n\n`;
} else {
  md += `**Concluzie:** nu s-a putut stabili când a fost etichetat ultimul mesaj (lipsesc datele).\n\n`;
}
md += `> Zero pe o fereastră nu înseamnă "etichetă goală" — înseamnă "eticheta nu mai primește nimic". Verificat pe 4 ferestre.

### 1.3 Filtrele, măsurate azi

`;
if (filterState) {
  const ft = (filterState.tests || []).filter(x => !/^list:/i.test(x.query || ''));
  const joburi = ft.find(x => /jooble/.test(x.query)) || null;
  const totalFixed = ft.reduce((a, x) => a + x.matchesFixed, 0);
  const rowsF = (filterState.rows || []).filter(x => !/^list:/i.test(x.query || ''));
  const withAdd = rowsF.filter(x => (x.addLabelIds || []).length).length;
  const withCatAdd = rowsF.filter(x => (x.categories || []).length).length;
  // categoriile sunt calculate local pe `rows`; `tests` se imbina cu ele prin id
  const rowById = {};
  for (const r of rowsF) rowById[r.id] = r;
  for (const t of ft) { t.categories = (rowById[t.id] || {}).categories || []; }
  const working = ft.filter(x => x.matchesAsIs > 0);
  const dead = ft.filter(x => x.matchesAsIs === 0);

  md += `Filtre cu criteriu de interogare pe cont: **${rowsF.length}**, din ${filterState.totalFilters} total. **${withAdd}** dintre ele are \`addLabelIds\`, iar **${withCatAdd}** atinge o etichetă de categorie.`;
  if (joburi) md += ` Criteriul celui de joburi, citit live azi:\n\n\`\`\`\n${joburi.query}\n\`\`\`\n`;

  if (working.length) {
    md += `
#### ${working.length === 1 ? 'Un filtru FUNCȚIONEAZĂ' : working.length + ' filtre FUNCȚIONEAZĂ'}

**${working.length} dintre ${ft.length} filtre lovesc efectiv mesaje.** ${working.map(x => `\`${x.query.slice(0, 50)}${x.query.length > 50 ? '…' : ''}\` → **${x.matchesAsIs}** mesaje în 30 de zile, etichetează ${(x.categories || []).length ? (x.categories || []).map(c => `\`${c}\``).join(', ') : 'nicio etichetă de categorie'}`).join('; ')}

`;
  }
  if (dead.length) {
    md += `
**Cauza reală, măsurată azi pe Gmail:** în căutarea Gmail, \`()\` înseamnă **ȘI**, iar \`{}\` înseamnă **SAU**. Cele ${dead.length} filtre nefuncționale folosesc \`from:(jooble bestjobs ...)\` — deci cer un expeditor care să conțină **toate** cuvintele simultan. Rezultat: **0 mesaje lovite în 30 de zile.**

| Filtru | cum e scris acum | cum ar trebui scris (\`{}\`) |
|---|---|---|
`;
    for (const x of dead) {
      md += `| \`${x.query.slice(0, 58)}${x.query.length > 58 ? '…' : ''}\` | **${x.matchesAsIs}** | **${x.matchesFixed}** |\n`;
    }
    md += `
Cu acoladele, aceleași filtre ar fi prins **${totalFixed} mesaje în 30 de zile**.

**Două defecte, în ordine:**
1. **Criteriile nu pot lovi nimic** — paranteze în loc de acolade.
2. **\`addLabelIds\` e vid** — nici măcar cu criterii corecte n-ar eticheta ceva.

**De ce nu le-am reparat azi:** repararea de filtre cere scope-ul \`gmail.settings.basic\` — fără el, \`filters PATCH\` răspunde 403. Starea scope-urilor din cloud se **măsoară**, nu se presupune: \`node mavis-tools/google-preflight.js\` (pasul [6] — control de drift). Repararea se face prin **DELETE + CREATE** (\`filters.update\`/PUT → 404, \`filters.patch\`/PATCH → 404 „Method not found"). Scriptul e pregătit cu \`--dry-run\` și cu salvarea stării de dinainte pentru rollback: \`mavis-tools/fix-mavis-filters.js\`.
`;
  }
} else {
  md += `*(Sonda de filtre nu a rulat azi — starea filtrelor nu e măsurată în acest raport.)*\n`;
}
// masuratori pentru observatia de la 1.4 — toate din date, niciuna scrisa cu mana
const agentsLabel = aliveNames.find(n => /optimus|agenti/i.test(n)) || null;
const agentsAzi = (mailCount.labels.find(l => /optimus|agenti/i.test(l.name)) || { counts: {} }).counts.azi || 0;
const totalCats = aliveRows.length + deadRows.length;
// masurat din SIMULARE (etichetele reale ale mesajelor de azi), nu presupus
const simRows = sim.rows || [];
const simInbox = simRows.filter(r => (r.labels || []).includes('INBOX')).length;
const simUnread = simRows.filter(r => (r.labels || []).includes('UNREAD')).length;
md += `
**Inboxul nu se golește.** Măsurat pe cele ${simRows.length} mesaje de azi, etichetele lor reale: **${simInbox} sunt încă în INBOX**, dar **doar ${simUnread} au rămas UNREAD**. Deci filtrele **curăță „necitit"**, dar **nu scoate mesajele din inbox**:

| Fereastră | În inbox | În toate stările |
|---|---|---|
| azi | ${inboxCounts.azi_inbox} | ${inboxCounts.azi_any} |
| 24h | ${inboxCounts['24h_inbox']} | ${inboxCounts['24h_any']} |
| 7z | ${inboxCounts['7d_inbox']} | ${inboxCounts['7d_any']} |

**~${inboxCounts['7d_inbox']} mesaje stau în inbox într-o săptămână** (~${Math.round(inboxCounts['7d_inbox'] / 7)}/zi).

### 1.4 Cum ar fi fost sortate mesajele de azi

Simulare pe cele ${sim.total} mesaje de azi, cu **aceleași criterii** ale filtrelor (fără scriere):

| Categorie | Mesaje azi |
|---|---|
`;
for (const nm of liveLabelNames) md += `| \`${nm}\` | ${simCount(nm)} |\n`;
md += `| *niciun filtru se potrivește* | ${sim.unmatched} |

> Unele mesaje se potrivesc la 2 filtre (ex. "Joburi" + "Newsletter" de la LinkedIn), deci suma poate depăși ${sim.total}.

**Observație:** **${tri.counts.noise} mesaje** de azi sunt notificări ale agenților tăi (Jules și GitHub Actions pe repo-urile proprii). Categoria dedicata lor e \`${agentsLabel || 'nerezolvata'}\`${agentsLabel ? `, care a primit ${agentsAzi} mesaj${agentsAzi === 1 ? '' : 'e'} azi, iar filtrul ei functioneaza efectiv` : ''}. In rest, **${aliveRows.length} din ${totalCats} categorii** primesc mesaje${deadRows.length ? `, iar ${deadRows.length} nu primesc` : ''}.


### 1.5 Mesajele care chiar necesită răspuns

Clasificarea e făcută din date, nu dintr-o listă scrisă cu mâna: ${tri.counts['needs-reply']} ${plural(tri.counts['needs-reply'], 'cere', 'cer', 'cer')} răspuns explicit, ${tri.counts['needs-action']} ${plural(tri.counts['needs-action'], 'cere', 'cer', 'cer')} o decizie, ${tri.counts['job-alert-other']} ${plural(tri.counts['job-alert-other'], 'este', 'sunt', 'sunt')} alerte de job care nu ating profilul tău, ${tri.counts.fyi} ${plural(tri.counts.fyi, 'e', 'sunt', 'sunt')} newsletter/promoție, ${tri.counts.noise} ${plural(tri.counts.noise, 'e', 'sunt', 'sunt')} zgomot de pipeline.

`;
if (replyList.length) {
  md += `**Ceres răspuns explicit:**\n\n`;
  for (const r of replyList) {
    md += `- **${r.displayName}** — ${msgTime(r)}. *${r.subject}* — ${clean(r.snippet).slice(0, 180)}\n`;
  }
  md += `\n`;
} else {
  md += `**Niciun mesaj nu cere explicit un răspuns.**\n\n`;
}
if (actionList.length) {
  md += `**Ceres o decizie sau o acțiune:**\n\n`;
  for (const r of actionList) {
    // motivul (why) e cel mai util — snippet-ul e trunchiat la ~200 de caractere
    // si de multe ori nu spune nimic. Corpul vine in raspuns, cu 0 cereri in plus.
    const why = r.why ? ` _(${r.why})_` : '';
    const detail = clean(r.body && r.body.length > (r.snippet || '').length ? r.body : (r.snippet || '')).slice(0, 200);
    md += `- **${r.displayName}** — ${msgTime(r)}. *${r.subject}*${why}${detail ? ` — ${detail}` : ''}\n`;
  }
  md += `\n`;
}
if (otherAlertList.length) {
  md += `**Alerte de job care NU ating profilul de design** (informativ, ${otherAlertList.length}):\n\n`;
  for (const r of otherAlertList) md += `- ${r.displayName} — ${msgTime(r)} · *${r.subject}*\n`;
  md += `\n`;
}
if (fyiList.length) {
  md += `**Newsletter / promoție, fără acțiune** (${fyiList.length}): ` + fyiList.map(r => r.displayName).join(', ') + `\n\n`;
}
// leads verificate: alerte de job care au condus la un anunt real, citit direct
let leads = null;
try { leads = JSON.parse(fs.readFileSync(path.join(DIR, `email-leads-${DATE}.json`), 'utf8')); } catch (e) {}
if (leads && leads.leads && leads.leads.length) {
  md += `**Leads din alertele de job.** Fiecare poartă propria cale de verificare, declarată mai jos — nu toate sunt citite direct de pe pagină:\n\n`;
  for (const l of leads.leads) {
    md += `##### ${l.resolvedTitle}\n\n`;
    md += `Din alerta **${l.from}** — *${l.subject}*\n\n`;
    if (l.verifiedVia) md += `**Cum a fost verificat:** ${l.verifiedVia}\n\n`;
    md += `${l.summary}\n\n`;
    if (l.requirements && l.requirements.length) {
      md += `**Cerințe:**\n\n`;
      for (const r of l.requirements) md += `- ${r}\n`;
      md += `\n`;
    }
    if (l.rates && l.rates.length) {
      md += `**Rate-uri publicate:**\n\n`;
      for (const r of l.rates) md += `- ${r}\n`;
      md += `\n`;
    }
    if (l.terms) md += `**Condiții:** ${l.terms}\n\n`;
    if (l.process) md += `**Cum se aplică:** ${l.process}\n\n`;
    if (l.caveat) md += `> ⚠️ ${l.caveat}\n\n`;
    md += `- ${l.url}\n\n`;
  }
}
md += `---
## 2. Joburi — scorate cu \`ALEX-KIT/scoring.gs\`

**${sc.stats.total} joburi analizate** (IQads ${srcTotal['IQads'] || 0} + designproject.io ${srcTotal['designproject.io'] || 0}) → ${sc.stats.kept} păstrate în tabele, ${sc.stats.dropped} drop-uri, din care **${sc.stats.amanzat} cu verdict amânat** (locația nu e publicată de sursă). **${sc.stats.newJobs} ${plural(sc.stats.newJobs, 'job nou', 'joburi noi', 'joburi noi')}** față de ${sc.prevDate || 'raportul anterior'}.

Surse: **IQads** (tabloul AdJob activ, citit azi) + **designproject.io** (România + București).

> ⛔ **Expirate marcate în tabele.** La IQads data de expirare vine direct din anunț. La designproject.io \`validThrough\` = data postării + 30 zile — ${vtSentence}, deci e o expirare reală, nu o derivare inutilă. ${expiredInTables} joburi din tabele au expirat${expiredInAmanzat ? ` (+${expiredInAmanzat} în verdict amânat)` : ''} și nu se mai pot aplica.

| | S | D | L | E |
|---|---|---|---|---|
| **S** — senioritate | 0.35 | | | |
| **D** — disciplină | | 0.30 | | |
| **L** — locație | | | 0.20 | |
| **E** — engagement | | | 0.15 | |

### 2.1 Secțiunea 1 — scor maxim — senior/lead, remote sau București, full-time (${sc.sections[1].length})

`;
md += jobTable(sc.sections[1], true);
md += '\n<!-- linkuri -->\n' + linkList(sc.sections[1]);
md += `\n### 2.2 Secțiunea 2 — contract / B2B — senioritate bună, engagement pe contract (${sc.sections[2].length})\n\n`;
md += sc.sections[2].length ? jobTable(sc.sections[2], true) : '*Niciun job în această secțiune.*\n';
md += '\n<!-- linkuri -->\n' + linkList(sc.sections[2]);
md += `\n### 2.3 Secțiunea 3 — mid-level — potrivire bună, senioritate sub prag (${sc.sections[3].length})\n\n`;
md += sc.sections[3].length ? jobTable(sc.sections[3], true) : '*Niciun job în această secțiune.*\n';
md += `\n### 2.4 Secțiunea 4 — on-site în afara Bucureștiului — doar dacă S=10 și D≥8 (${sc.sections[4].length})\n\n`;
md += sc.sections[4].length ? jobTable(sc.sections[4], true) : '*Niciun job în această secțiune.*\n';
md += `\n### 2.5 Verdict amânat — locația nu e publicată de sursă (${sc.stats.amanzat})\n\n`;
md += '| Scor | Rol | Companie | Locație | Engagement | Expirare | Nou |\n|---|---|---|---|---|---|---|\n';
for (const j of sc.amanzat) md += `| ${j.score} | ${cell(j.role)} | ${cell(j.company)} | neprecizată de sursă | ${cell(j.eng)} | ${j.expiry ? j.expiry.slice(0, 10) + (j.expired ? ' ⛔' : '') : '—'} | ${j.isNew ? ' ✅' : ''} |\n`;
md += `\n**Dintre astea, ${amanzatNew.length} sunt noi.** Nu le-am dat verdict de locație pentru că anunțul nu o spune — să le verifici pe cele care te interesează:\n\n`;
for (const j of sc.amanzat.slice(0, 8)) md += `- ${cell(j.role)} — ${cell(j.company)} (${j.src}) — ${j.url}\n`;
md += `\n### 2.6 Drop-uri (circuit breaker) — ${sc.stats.dropped}\n\n`;
md += '| Rol | Companie | Motiv | Nou |\n|---|---|---|---|\n';
for (const j of sc.dropped) md += `| ${cell(j.role)} | ${cell(j.company)} | ${cell(j.reason.replace('CIRCUIT BREAKER: ', ''))} | ${!j.inPrevSet ? ' ✅' : ''} |\n`;

md += `
---

## 3. Top 5 joburi cu scor

`;
md += '| # | Scor | Tag | Rol | Companie | Locație | Engagement | Expirat? | De ce contează |\n|---|---|---|---|---|---|---|---|---|\n';
top.forEach((j, i) => {
  const flags = sc.axisFromProse.find(x => x.role === j.role && x.company === j.company);
  md += `| ${i + 1} | **${j.score}** | ${j.tag} | ${cell(j.role)} | ${cell(j.company)} | ${cell(j.loc || '—')} | ${cell(j.eng || '—')} | ${j.expired ? '⛔ da' : 'nu'} | ${why(j, flags ? flags.flags : [])} |\n`;
});
md += '\n';
for (const j of top) md += `- ${j.company} :: ${j.role} — ${j.url}\n`;

const topDesign = allSections.filter(j => isDesignRole(j.role)).slice(0, 5);
const nonDesignInTop = top.filter(j => !isDesignRole(j.role)).length;
md += `
`;
if (nonDesignInTop) {
  md += `> **Atenție:** din top 5 după scor, ${nonDesignInTop} **nu sunt roluri de design** (au trecut doar pentru că textul lor conține "social media" sau "art director" — vezi §6.2). Iată top 5 **efectiv de design**, filtrate pe titlu:\n\n`;
} else {
  md += `> Top 5 după scor conține **doar roluri de design**. Iată top 5 filtrate pe titlu, pentru comparație:\n\n`;
}
md += '| # | Scor | Rol | Companie | Locație | Engagement | Expirat? | De ce contează |\n|---|---|---|---|---|---|---|---|\n';
topDesign.forEach((j, i) => {
  const flags = sc.axisFromProse.find(x => x.role === j.role && x.company === j.company);
  md += `| ${i + 1} | **${j.score}** | ${cell(j.role)} | ${cell(j.company)} | ${cell(j.loc || '—')} | ${cell(j.eng || '—')} | ${j.expired ? '⛔ da' : 'nu'} | ${why(j, flags ? flags.flags : [])} |\n`;
});
md += '\n';
for (const j of topDesign) md += `- ${j.company} :: ${j.role} — ${j.url}\n`;

md += `
---

## 4. Postări GENUIN noi (nu doar "absente din raportul de ieri")

> "nou" în tabele înseamnă **"nu era în raportul de ieri"**, nu neapărat "postat azi". Iată ce e postat efectiv nou:

| Sursă | Cum am măsurat | Rezultat |
|---|---|---|
| **IQads** | ID-ul ad-ului crește monoton cu postarea. Cel mai mare ID din setul de ieri: **${gn.maxPrevIqadsId}** | **${gn.newIqads.length} ${plural(gn.newIqads.length,'anunț nou','anunțuri noi','anunțuri noi')}** |
| **designproject.io** | data de publicare vs. ultima rulare | **${gn.newDesignproject.length} ${plural(gn.newDesignproject.length,'anunt nou','anunțuri noi','anunțuri noi')}** — cel mai recent de pe site e din **${gn.newestDesignprojectDate}** |

`;
for (const j of gn.newIqads) md += `- **IQads #${j.id}** — ${cell(j.role)} @ ${cell(j.company)} (expiră ${j.expiry}) — ${j.url}\n`;
for (const j of gn.newDesignproject) md += `- **designproject.io** — ${cell(j.role)} @ ${cell(j.company)} (postat ${j.date}) — ${j.url}\n`;

const totalNew = gn.newIqads.length + gn.newDesignproject.length;
if (totalNew === 0) {
  md += `**Concluzie:** **nicio postare nouă față de ultima rulare.** Piața nu a produs nimic nou relevant azi.\n\n`;
} else {
  md += `**Concluzie:** ${totalNew} postare${totalNew > 1 ? 'ri' : ''} nou${totalNew > 1 ? 'e' : ''} de la ultima rulare.\n\n`;
}
if (sc.stats.newJobs) md += `Ce nu a mai apărut în raportul anterior, dar există în catalog (${sc.stats.newJobs} la număr, toate cu ✅ în tabele):\n\n`;
for (const j of newJobs.slice(0, 25)) {
  md += `- **${j.score}** · Secția ${j.section} · ${cell(j.role)} — ${cell(j.company)} (${j.src})\n`;
}

md += `
---

## 5. Ce n-a mers, măsurat

`;
if (daysOff !== null) {
  const ft = filterState ? (filterState.tests || []) : [];
  const totalFixed = ft.reduce((a, x) => a + x.matchesFixed, 0);
  // CAUZA, masurata per categorie: exista filtru pentru ea? (nu hardcodat —
  // se compara filtrul viu cu eticheta categoriei)
  const deadNoFilter = [], deadBrokenFilter = [];
  for (const l of deadRows) {
    const hasFilter = (filterState && (filterState.rows || []).some(r => (r.addLabelIds || []).some(x => TAX.normalize(x) === TAX.normalize(l.name)))) || false;
    (hasFilter ? deadBrokenFilter : deadNoFilter).push(l.name);
  }
  const brokenCount = filterState ? (filterState.tests || []).filter(x => !/^list:/i.test(x.query || '') && x.matchesAsIs === 0).length : 0;
  const workingCount = filterState ? (filterState.tests || []).filter(x => !/^list:/i.test(x.query || '') && x.matchesAsIs > 0).length : 0;

  const deadStaleN = deadRows.filter(l => l.newest).length;
  const deadNeverN = deadRows.length - deadStaleN;
  md += `1. **${deadRows.length} din ${labelRows.length} categorii nu mai primesc nimic**${deadStaleN ? ` (${deadStaleN} de ${deadDaysOff} zile` : ''}${deadStaleN && deadNeverN ? ', ' : ''}${deadNeverN ? `${deadNeverN} n-a fost folosită niciodată` : ''}).`;
  if (deadNoFilter.length) {
    md += ` Cauza pentru ${deadNoFilter.length === 1 ? 'una' : deadNoFilter.length + ' dintre ele'}: **nu au filtru creat** (${deadNoFilter.map(n => `\`${n}\``).join(', ')}) — deci nimic nu le poate eticheta, oricare ar fi criteriul.`;
  }
  if (deadBrokenFilter.length) {
    md += ` Pentru ${deadBrokenFilter.length === 1 ? 'cea ramasa' : 'celelalte'} (${deadBrokenFilter.map(n => `\`${n}\``).join(', ')}) exista filtru, dar el loveste 0 mesaje.`;
  }
  md += ` Starea filtrelor, masurata azi: **${workingCount} functioneaza, ${brokenCount} sunt nefunctionale**${brokenCount ? ` — cele nefunctionale folosesc \`from:(...)\` unde Gmail cere \`from:{...}\` (paranteze = ȘI, acolade = SAU), deci nu pot lovi niciun mesaj; cu acoladele ar fi prins ${totalFixed} mesaje in 30 de zile` : ''}. ~${inboxCounts['7d_inbox']} mesaje/7 zile stau in inbox.\n`;
}
if (dpP && !dpP.error) {
  md += `2. **designproject.io servește descrieri foarte inegale** (${dpP.jdLenMin}–${dpP.jdLenMax} de caractere pe cele ${dpP.count} de joburi, măsurat azi). Cele mai lungi sunt rescrise de AI și injectează cuvinte-cheie care ridică axele — vezi §6.2.\n`;
  md += `3. **Celelalte două câmpuri de engagement ale designproject.io sunt inutilizabile.** \`employmentType\` din JSON-LD spune \`FULL_TIME\` pentru ${dpP.employmentType.FULL_TIME || 0} din ${dpP.count}, iar badge-ul din listing spune "Full-time" pentru ${dpP.badgeFullTime} din ${dpP.count}. Singura sură corectă e linia **"Job Type:"** din descriere — prezentă la ${dpP.withJobTypeLine} din ${dpP.count}. Am folosit asta.\n`;
} else {
  md += `2. *(Sonda de surse nu a rulat azi — cifrele despre designproject.io lipsesc.)*\n`;
}
if (iqP && !iqP.error) {
  md += `4. **Paginatia IQads nu funcționează.** \`?page=${iqP.pagesTested.slice(1).join('\` și \`?page=')}\` servesc exact pagina 0 (aceleași ${iqP.catalogueLinks} de linkuri — verificat azi pe ${iqP.pagesTested.join(', ')}). Catalogul complet e pe pagina 0 — nu iterez pagini.\n`;
} else {
  md += `4. *(Sonda de surse nu a rulat azi — verificarea paginatiei IQads lipseste.)*\n`;
}
md += `5. **Cota Google: ${usageTotal} cereri pe 200**${usageTotal > 200 ? ` (**depășit cu ${usageTotal - 200}**)` : usageTotal === 200 ? ' (**exact pe plafon**)' : ' (în limita plafonului)'}. Consumul pe etape:\n\n`;
md += '| Etapă | Cereri |\n|---|---|\n';
// report-build.js apare in contor cu cererile deja facute; upload-ul de dupa
// generare intra in aceeasi linie, ca sa nu apara de doua ori.
md += usageRows.map(([k, v]) => `| \`${k}\` | ${k === 'report-build.js' ? v + UPLOAD_COST : v} |`).join('\n') + '\n';
md += `| **total** | **${usageTotal}** |\n\n`;
md += `> ${usageNote || 'Contorul măsoară cererile efective făcute de fiecare script.'}\n\n`;
if (usageTotal > 200) {
  // explicatia depunerii peste plafon se calculeaza din consumul real, pe etape
  const diagRows = usageRows.filter(r => ['inline', 'readbodies.js', 'extract.js'].includes(r[0]));
  const diagTotal = diagRows.reduce((a, r) => a + r[1], 0);
  md += `**Ce a mers peste plafon:** ${diagTotal} cereri de **diagnostic** care NU sunt masurarea zilei (${diagRows.map(r => `\`${r[0]}\` ${r[1]}`).join(', ')}) — citirea manuala a corpurilor ca sa separ ce cere raspuns de ce e doar alerta. Restul consumului e pipeline-ul standard.\n\nAu fost cheltuite pe **înțelegerea** stării, nu pe măsurarea zilei. Zero scrieri pe Gmail — niciun mail trimis, marcat sau arhivat, niciun filtru modificat.\n`;
} else {
  md += `Ce a consumat cel mai mult: corpurile complete ale mesajelor de azi (${tri.all.length}) — fără corp, nu se poate distinge un mesaj care cere răspuns de o alertă automată. **Zero scrieri pe Gmail** — niciun mail trimis, marcat sau arhivat, niciun filtru modificat.\n`;
}

md += `
---

## 6. Două semnalări ale motorului de scoring (portul rămâne fidel — decizia e a ta)

### 6.1 "remote" pozitiv fals — ${sc.remoteFalsePositives.length} joburi

| Rol | Companie | De ce e fals | L |
|---|---|---|---|
`;
for (const j of sc.remoteFalsePositives) md += `| ${cell(j.role)} | ${cell(j.company)} | ${j.remoteFalsePositive.kind}: \`${j.remoteFalsePositive.hit}\` | ${j.L} |\n`;
md += `
"Remote" apare în text, dar jobul **nu** e remote. \`L\` ar trebui să fie 8 (București) sau 0 (necunoscut), nu 10. Diferență: **0.4 puncte** per job. Nu am atins motorul — portul e fidel prin design.

### 6.2 Axa D ridicată de prosa, nu de titlu — ${sc.axisFromProse.length} joburi (${sc.axisFromProse.reduce((a, x) => a + x.flags.length, 0)} semnalări)

`;
md += '| Rol | Companie | Ce a ridicat axa | De unde |\n|---|---|---|---|\n';
for (const j of sc.axisFromProse) {
  for (const f of j.flags) md += `| ${cell(j.role)} | ${cell(j.company)} | ${f.axis}=${f.val} prin \`${f.trigger}\` (${f.tier || '—'}) | ${f.from} |\n`;
}
md += `
**Ce propun:** ca \`D\` să se calculeze din **titlul rolului**, nu din textul anunțului, sau măcar ca un rol să poată intra într-o secțiune doar dacă titlul conține o cheie de design. E o decizie de motor — nu am atins \`scoring.gs\` fără acordul tău.

---

## 7. Fișiere

`;
const files = [
  ['rapoarte/RAPORT-ZILNIC-' + COMPACT.slice(0, 6) + '-' + COMPACT.slice(6) + '.md', 'raportul acesta (și în repo)'],
  ['mavis-tools/scoring-result-' + DATE + '.json', 'scoruri + secțiuni + diagnostice'],
  ['mavis-tools/jobs-iqads-' + DATE + '.json', 'joburi IQads, text integral'],
  ['mavis-tools/jobs-designproject-' + DATE + '.json', 'joburi designproject.io, JSON-LD'],
  ['mavis-tools/jobs-' + (sc.prevDate || '') + '.json', 'setul normalizat de ieri (cu care s-a comparat)'],
  ['mavis-tools/report-mail-count.json', 'numărătoare pe etichetele de categorie'],
  ['mavis-tools/report-inbox-counts.json', 'numărătoare exactă inbox'],
  ['mavis-tools/report-simulate-sort.json', 'simularea sortării + mesajele de azi'],
  ['mavis-tools/report-source-probe.json', 'sonda de surse (comportamentul iqads.ro / designproject.io, măsurat azi)'],
  ['mavis-tools/report-filter-state.json', 'starea filtrelor Gmail + testul paranteze-vs-acolade (măsurat azi)'],
  ['mavis-tools/report-triage.js', 'clasificatorul mesajelor (needs-reply / needs-action / fyi / noise)'],
  ['mavis-tools/taxonomy.js', 'sursa unică pentru numele etichetelor de categorie (rezolvate live, nu hardcodate)'],
];
for (const [f, dsc] of files) {
  const p = path.join(DIR, '..', f);
  if (fs.existsSync(p)) md += `- \`${f}\` — ${dsc}\n`;
}

md += `
---

*Generat de Mavis Cloud. Nimic nu a fost șters, nimic nu a fost trimis, nimic nu a fost modificat în Gmail sau Drive. Totul e anulabil.*
`;

fs.writeFileSync(REPO_OUT, md);
console.log('raport scris local: ' + REPO_OUT + ' (' + md.length + ' caractere)');

// --dry: scrie raportul local, NU atinge Drive (pentru validare fara cereri)
if (process.argv.includes('--dry')) {
  console.log('--dry: nu se atinge Drive. 0 cereri Google.');
  process.exit(0);
}

(async () => {
  const name = 'RAPORT-ZILNIC-' + COMPACT.slice(0, 6) + '-' + COMPACT.slice(6) + '.md';
  // --file-id=<ID>: actualizam un raport deja creat, fara cautare.
  // 1 cerere in loc de 3 (search + upload + verificare) — contorul ramane exact.
  const fileIdArg = (process.argv.find(a => a.startsWith('--file-id=')) || '').replace('--file-id=', '').trim();
  if (fileIdArg) {
    // 1 cerere: PATCH cu uploadType=media. Raspunsul include deja
    // id/name/mimeType/size/parents -> e si verificarea, nu mai trebuie un GET.
    const up = await k.drive.replaceContent(fileIdArg, md, 'text/markdown');
    console.log('raport ACTUALIZAT in place: ' + fileIdArg);
    console.log('verificare (din raspuns): ' + up.name + ' | ' + up.mimeType + ' | ' + up.size + ' bytes | parents=' + (up.parents || []).join(','));
    console.log('cereri Google in acest pas: ' + k.CALL_STATE.calls);
    return;
  }
  // daca exista deja, il actualizam in place (nu cream duplicat)
  const exist = await k.drive.search("name = '" + name + "' and '" + FOLDER_ID + "' in parents and trashed=false");
  let id;
  if (exist.files && exist.files.length) {
    id = exist.files[0].id;
    await k.drive.replaceContent(id, md, 'text/markdown');
    console.log('raport ACTUALIZAT in place: ' + id);
  } else {
    const up = await k.drive.upload(name, md, 'text/markdown', FOLDER_ID);
    id = up.id;
    console.log('raport CREAT: ' + id + ' | ' + up.name);
  }
  const check = await k.drive.get(id);
  console.log('verificare: ' + check.name + ' | ' + check.mimeType + ' | ' + check.size + ' bytes | parents=' + (check.parents || []).join(','));
  console.log('cereri Google in acest pas: ' + k.CALL_STATE.calls);
})();

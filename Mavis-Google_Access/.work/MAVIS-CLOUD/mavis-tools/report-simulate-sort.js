#!/usr/bin/env node
/**
 * SIMULARE: cum ar fi fost sortate mesajele de azi, daca filtrele ar functiona.
 * Aplica EXACT criteriile filtrelor de categorie (masurate live de
 * report-filter-state.js; restul vin din email-sort-full.js, care le oglindeste).
 *
 * 2026-10-27: etichetele au fost rearanjate. CATEGORIES tine cheia stabila
 * ("joburi", "ai", ...); numele etichetei se rezolva la runtime din taxonomy.js.
 *
 * Nu scrie NIMIC. Doar calculeaza.
 */
const k = require('./kit.js');
const fs = require('fs');
const TAX = require('./taxonomy.js');

// data pentru fereastra "azi" (format Gmail: AAAA/LL/ZZ). Implicit: azi.
const TODAY = process.argv[2] || new Date().toISOString().slice(0, 10).replace(/-/g, '/');
const TODAY_ISO = TODAY.replace(/\//g, '-');

/**
 * Extrage textul din corpul mesajului, dintre payload-ul primit.
 *
 * REGULA (invatata pe 26.10): snippet-ul e trunchiat la ~200 de caractere si
 * contine doar antetul. CORPUL contine lucrurile care conteaza (lista de
 * joburi cu salariu, "trebuie sa alegi o parola noua", "alerta de securitate").
 * Nu costa nimic in plus: corpul vine deja in raspunsul format=full.
 */
function extractBody(payload) {
  if (!payload) return '';
  // MULTE emailuri au mai multe parti (multipart/alternative + quoted).
  // Nu te opresti la prima — altfel pierzi exact continutul util. De ex.
  // alerta HiPo are textul "Trebuie sa alegi o parola noua" intr-o parte
  // ulterioara, nu in prima.
  const plains = [], htmls = [];
  const walk = p => {
    if (!p) return;
    const d = p.body && p.body.data;
    if (d) {
      const raw = Buffer.from(d, 'base64').toString('utf8');
      if (p.mimeType === 'text/plain') plains.push(raw);
      else if (p.mimeType === 'text/html') htmls.push(raw);
    }
    for (const c of (p.parts || [])) walk(c);
  };
  walk(payload);
  // MĂSURAT 2026-10-28: unele emailuri au o parte text/plain care NU contine
  // ce contine partea HTML. Alerta HiPo: text/plain = 13.128 caractere fara
  // "parola"; text/html = 32.169 caractere SI contine "Trebuie sa alegi o
  // parola noua". ⇒ alegem HTML-ul (forma randata, cea pe care o citeste omul),
  // iar text/plain doar ca rezerva cand nu exista HTML.
  if (htmls.length) {
    const text = htmls.join('\n')
      .replace(/<script[\s\S]*?<\/script>/gi, ' ')
      .replace(/<style[\s\S]*?<\/style>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
      .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&')
      .replace(/&#39;/g, "'").replace(/&[a-z]+;/gi, ' ');
    // HTML-ul lasa zeci de randuri goale (un tag pe linie). Daca le pastram,
    // 1500 de caractere se termina inainte de continutul util — de ex.
    // "Trebuie sa alegi o parola noua" din alerta HiPo nu ajungea niciodata.
    const flat = text.replace(/\s+/g, ' ').trim();
    if (flat) return flat;
  }
  const plain = plains.sort((a, b) => b.length - a.length)[0] || '';
  return plain.replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
}

// Cat de mult corp pastram per mesaj. 4000 = suficient ca alerta de job
// (lista de 13 joburi cu salariu) sau emailul de cont sa intre complet.
const BODY_CAP = 4000;

// [key, criteriu] — cheia e stabila, nu numele etichetei.
const CATEGORIES = [
  ['joburi',     { from: /jooble|bestjobs|hipo|indeed|jobleads|recruit|linkedin|iqads|designproject/i, subject: /job|angajare|vacanta|oportunitate/i }],
  ['ai',         { from: /substack|goatacademy|aiautomationsociety|sadhguru|beehiiv|twine|comfy|deepmind|openai|anthropic/i, subject: /\bAI\b|artificial intelligence/i }],
  ['social',     { from: /skool|facebook|instagram|tiktok|pinterest|polibrawl|youtube/i, subject: null }],
  ['newsletter', { from: /noreply|no-reply|newsletter|digest|promotions|offers|deals|notificari|notificări/i, subject: null }],
  ['finante',    { from: /kraken|tradingview|bitunix|coinbase|binance/i, subject: /factura|investitie/i }],
  ['agenti',     { from: /notifications@github\.com|jules/i, subject: /jules|github/i }],
];

(async () => {
  // ---------- MOD BACKFILL: reia doar corpurile trunchiate ----------
  // De ce exista: o rulare poate sase cu un plafon mai mic al corpului
  // (ex. 1500 de caractere), iar continutul util — "trebuie sa alegi o parola
  // noua", lista completa de joburi — se pierde fara sa se stie.
  // Modul asta NU re-listeaza mesajele: pastreaza setul deja masurat (deci
  // nu se degradeaza consistenta cu report-inbox-counts.js) si cumpara doar
  // o cerere per mesaj trunchiat.
  if (process.argv.includes('--backfill')) {
    const p = '/workspace/Mavis/mavis-tools/report-simulate-sort.json';
    if (!fs.existsSync(p)) { console.log('nu exista ' + p + ' — ruleaza mai intai fara --backfill'); process.exit(1); }
    const data = JSON.parse(fs.readFileSync(p, 'utf8'));
    const { triage } = require('./report-triage.js');
    const tri = triage(data.rows || []);
    const actionable = new Set();
    for (const cls of ['needs-reply', 'needs-action', 'job-alert-other']) {
      for (const r of tri.buckets[cls]) actionable.add(r.id);
    }
    // plafonul cu care au fost scrise corpurile — daca e mai mic decat cel
    // curent, mesajele trunchiate trebuie refetate. Absent => 1500 (vechea
    // valoare, scris inainte de BODY_CAP).
    const writtenCap = data.bodyCap || 1500;
    // SELECTIE: refacem mesajele a caror CLASIFICARE depinde de continut.
    // Un newsletter isi stie clasa din expeditor — corpul lui nu schimba
    // nimic, deci refacerea lui ar arde cereri pentru zero informatie.
    // Cu --all se refac toate (cand vrei cu adevarat completitudine).
    const all = process.argv.includes('--all');
    // --ids=id1,id2,id3 : reface strict mesajele alea (interventie chirurgicala,
    // cand bugetul de cereri nu permite tot setul).
    const idsArg = (process.argv.find(a => a.startsWith('--ids=')) || '').replace('--ids=', '').split(',').filter(Boolean);
    const ids = new Set(idsArg);
    const capped = (data.rows || []).filter(r =>
      ids.size ? ids.has(r.id)
        : (actionable.has(r.id) || (all && (r.body || '').length >= writtenCap)));
    console.log('mesaje in set: ' + (data.rows || []).length
      + ' | plafon la scriere: ' + writtenCap
      + ' | clasa depinde de continut: ' + actionable.size
      + ' | de refacut: ' + capped.length + (all ? ' (--all)' : ''));
    if (!capped.length) { console.log('nimic de completat.'); process.exit(0); }
    for (const r of capped) {
      try {
        const m = await k.req('GET', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/' + r.id + '?format=full');
        const before = (r.body || '').length;
        r.body = extractBody(m.payload).slice(0, BODY_CAP);
        console.log('  ' + r.id + '  corp ' + before + ' -> ' + r.body.length + ' caractere');
      } catch (e) { console.log('  ' + r.id + '  ERR ' + e.message); }
    }
    data.bodyCap = BODY_CAP;
    fs.writeFileSync(p, JSON.stringify(data, null, 2));
    console.log('\nbackfill scris: ' + p);
    console.log('cereri: ' + k.CALL_STATE.calls);
    return;
  }

  // etichetele vii -> nume reale per categorie
  const labs = await k.gmail.labels();
  const { byKey, missing } = TAX.resolve(labs.labels || []);
  if (missing.length) console.log('!! categorii ne-rezolvate: ' + missing.map(m => m.title).join(' | '));
  const CATS = CATEGORIES.map(([key, c]) => [TAX.labelName(byKey, key) || key, c]);

  // toate mesajele de azi (in orice stare, nu doar inbox)
  let page = null; const ms = [];
  do {
    const url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages?q='
      + encodeURIComponent(`in:anywhere after:${TODAY}`) + '&maxResults=500' + (page ? '&pageToken=' + encodeURIComponent(page) : '');
    const r = await k.req('GET', url);
    for (const m of r.messages || []) ms.push(m.id);
    page = r.nextPageToken || null;
    if (page) await new Promise(res => setTimeout(res, 200));
  } while (page);

  const rows = [];
  for (const id of ms) {
    // format=full (nu metadata) => vine si snippet, necesar ca sa judec
    // care mesaje chiar cer raspuns. Costul e tot 1 cerere/mesaj.
    const m = await k.req('GET', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/' + id + '?format=full');
    const h = n => (m.payload && m.payload.headers || []).find(x => x.name === n)?.value || '';
    // REGULA: snippet = descoperire, corp = adevar. Fragmentul de text e
    // trunchiat la ~200 de caractere si contine doar antetul. Corpul vine DEJA
    // in raspunsul format=full — deci il decodam aici, cu 0 cereri in plus.
    // Fara asta, un email de tip "alerta de cont" sau "trebuie sa alegi o
    // parola" arata exact ca un newsletter si ajunge in clasele gresite.
    rows.push({
      id, from: h('From'), subject: h('Subject'), date: h('Date'),
      labels: m.labelIds || [], snippet: (m.snippet || '').slice(0, 400),
      body: extractBody(m.payload).slice(0, BODY_CAP),
    });
  }
  rows.sort((a, b) => new Date(b.date) - new Date(a.date));

  const buckets = {}; CATS.forEach(c => buckets[c[0]] = []);
  const unmatched = [];
  for (const r of rows) {
    let hit = false;
    for (const [name, c] of CATS) {
      const okF = c.from ? c.from.test(r.from) : false;
      const okS = c.subject ? c.subject.test(r.subject) : false;
      if (c.from && c.subject) { if (okF || okS) { buckets[name].push(r); hit = true; } }
      else if (okF) { buckets[name].push(r); hit = true; }
    }
    if (!hit) unmatched.push(r);
  }

  console.log('mesaje azi (orice stare): ' + rows.length + '\n');
  for (const [name] of CATS) {
    console.log(`${name.padEnd(24)} ${String(buckets[name].length).padStart(3)}`);
    buckets[name].slice(0, 12).forEach(r => console.log('      ' + r.date.slice(5, 22) + ' | ' + r.from.replace(/<[^>]*>/g, '').slice(0, 32).padEnd(32) + ' | ' + r.subject.slice(0, 52)));
  }
  console.log(`\n${'fara niciun filtru'.padEnd(24)} ${String(unmatched.length).padStart(3)}`);
  unmatched.forEach(r => console.log('      ' + r.date.slice(5, 22) + ' | ' + r.from.replace(/<[^>]*>/g, '').slice(0, 32).padEnd(32) + ' | ' + r.subject.slice(0, 52)));

  fs.writeFileSync('/workspace/Mavis/mavis-tools/report-simulate-sort.json',
    JSON.stringify({ date: TODAY_ISO, total: rows.length, bodyCap: BODY_CAP, counts: Object.fromEntries(CATS.map(c => [c[0], buckets[c[0]].length])), unmatched: unmatched.length, rows, buckets }, null, 2));
  console.log('\ncereri: ' + k.CALL_STATE.calls);
})();

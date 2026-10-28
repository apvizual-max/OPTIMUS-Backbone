/**
 * 0.8f — Sortarea thread-urilor 1-3 ani pe cele 8 categorii MAVIS
 * METODA IEFTINA: cautari cu filtre de expeditor -> thread-uri direct, fara messages.get
 * Cost: ~5 unitati per pagina de 500. Zero apeluri scumpe.
 */
const k = require('./kit.js');
const q = require('./quota.js');

// NUMELE ETICHETELOR NU SE HARDCODEAZA. Se rezolva live din taxonomy.js
// (sursa unica de adevar) - la 27.10 etichetele au fost rearanjate si
// 'MAVIS/Social', 'MAVIS/AI si comunitati' etc. nu mai exista.
const TAX = require('./taxonomy.js');
let L = {};
function rezolvaEtichete(liveLabels) {
  const r = TAX.resolve(liveLabels || []);
  L = {};
  for (const row of r.resolved) L[row.key] = row.name;
  if (r.missing.length)
    console.log('  ( etichete nerezolvate: ' + r.missing.map(m => m.key).join(', ') + ' )');
  return L;
}

const WINDOW = '';  // nefolosit: sortam tot inbox-ul
// categoriile zilnice nu pot folosi fereastra de 1-3 ani
const NO_WINDOW = new Set(['ai', 'actiune', 'facturi']);

const CATS = [
  ['social',    `{from:skool from:facebook from:instagram from:tiktok from:pinterest from:polibrawl from:youtube}`],
  ['joburi',    `{from:jooble from:bestjobs from:hipo from:indeed from:jobleads from:recruit from:linkedin from:iqads from:designproject}`],
  // AI si newsletter-urile vin ZILNIC: fereastra 'mai vechi de 1 an' le arunca pe TOATE.
  ['ai',        `{from:substack from:goatacademy from:aiautomationsociety from:beehiiv from:twine from:comfy from:deepmind from:openai from:anthropic subject:AI subject:"artificial intelligence"}`],
  // etichete care NU aveau nicio regula - create goale
  ['facturi',   `{subject:factura subject:factură subject:invoice subject:facturi}`],
  ['actiune',   `{is:starred} {is:important is:unread}`],
  ['finante',   `{from:kraken from:tradingview from:bitunix from:coinbase from:binance subject:factura subject:investitie}`],
  ['newsletter',`{from:noreply from:no-reply from:newsletter from:digest from:promotions from:offers from:deals from:notificari from:notificări}`],
  ['personal',  `{from:happyadv from:alexfiloti from:family from:parinti}`],
];

async function threadIds(query) {
  const out = []; let page = null;
  do {
    const r = await k.req('GET',
      'https://gmail.googleapis.com/gmail/v1/users/me/threads?q=' + encodeURIComponent(query) +
      '&maxResults=500' + (page ? '&pageToken=' + page : ''));
    out.push(...(r.threads || []).map(t => t.id));
    page = r.nextPageToken || null;
  } while (page);
  return out;
}

(async () => {
  const ex = await k.gmail.labels();
  rezolvaEtichete(ex.labels);                       // numele vii, din taxonomy.js
  const byName = new Map(ex.labels.map(l => [l.name, l.id]));
  // NU se creeaza etichete inexistente: daca o categorie n-a fost rezolvata,
  // eticheta ei nu se inventeaza. Se sare peste ea, cu raport.
  for (const [k2, n] of Object.entries(L)) {
    if (!n) { console.log('  ( eticheta pentru "' + k2 + '" nu exista - categorie rezolvata? sarit )'); continue; }
    if (!byName.has(n)) await k.gmail.createLabel(n);
  }
  const labels = await k.gmail.labels();
  const M = new Map((labels.labels||[]).map(l => [l.name, l.id]));

  const total = new Map();
  for (const [cat, flt] of CATS) {
    const w = '';   // SORTARE COMPLETA - fara fereastra de varsta
    // GHILIMELE OBLIGATORII: etichetele cu spatiu sau linie sunt stricate de Gmail.
    // Liniuta din nume face eticheta DE NEINDEXABILA - nicio forma de cautare
    // nu o gaseste. De aceea s-a renumit 'MAVIS/De raspuns'.
    // 'actiune' prinde si ce a fost deja sortat in alta categorie si scos din
    // inbox. Cu 'in:inbox' ar da 0, pentru ca mailurile cu stea nu mai sunt acolo.
    const inbox = (cat === 'actiune') ? '' : ' in:inbox';
    const query = w + flt + inbox + ' -label:"' + L[cat] + '"';
    let ids = [];
    try { ids = await threadIds(query); } catch (e) { console.log('cautare blocata', cat, e.message.slice(0,40)); continue; }
    console.log('\n' + cat.toUpperCase() + ': ' + ids.length + ' thread-uri  (cota ' + q.state.used + ')');
    if (!ids.length) continue;
    // aplica eticheta + scoate din inbox + marcheaza citit
    const lab = M.get(L[cat]);
    for (let i = 0; i < ids.length; i += 100) {
      try {
        const chunk = ids.slice(i, i + 100);
        await Promise.all(chunk.map(t =>
          k.req('POST', `https://gmail.googleapis.com/gmail/v1/users/me/threads/${t}/modify`,
            { addLabelIds: [lab], removeLabelIds: ['INBOX', 'UNREAD'] })
        ));
      } catch (e) { console.log('  blocat la', i, e.message.slice(0, 50)); break; }
      if (i % 1000 === 0) console.log('   ...', i, '/', ids.length);
    }
    total.set(cat, ids.length);
  }

  console.log('\n=== REZULTAT 0.8f ===');
  for (const [c, n] of total) console.log('  ' + String(n).padStart(6) + '  ' + L[c]);
  console.log('\ncota totala consumata:', q.state.used, 'unitati');
  console.log('GATA');
})().catch(e => console.error('E:', e.message));
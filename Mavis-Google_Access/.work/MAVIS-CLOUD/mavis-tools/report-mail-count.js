#!/usr/bin/env node
/**
 * RAPORT ZILNIC — MĂSURĂTOARE ETAICHETELOR DE CATEGORIE
 *
 * Numără EXACT (paginare reală, nu resultSizeEstimate) mesajele pe fiecare
 * etichetă de categorie, pe mai multe ferestre de timp. Regula: zero-ul pe o
 * fereastră nu înseamnă "eticheta e goală" — înseamnă "eticheta nu mai primește
 * nimic în acea fereastră". De aceea măsurăm 4 ferestre + ultima dată.
 *
 * 2026-10-27: etichetele MAVIS/* au fost rearanjate (Mavis Local). Niciun nume
 * de etichetă nu mai e scris aici — se rezolvă din taxonomy.js, la runtime.
 *
 * READ-ONLY. Nu trimite, nu șterge, nu modifică nimic.
 */
const k = require('./kit.js');
const fs = require('fs');
const TAX = require('./taxonomy.js');

const TODAY = process.argv[2] || new Date().toISOString().slice(0, 10).replace(/-/g, '/');
const OUT = process.argv[3] || '/workspace/Mavis/mavis-tools/report-mail-count.json';

// ferestre: [eticheta, query]
const WINDOWS = [
  ['azi',      q => `${q} after:${TODAY}`],
  ['24h',     q => `${q} newer_than:1d`],
  ['7z',      q => `${q} newer_than:7d`],
  ['30z',     q => `${q} newer_than:30d`],
];

async function countExact(query) {
  let page = null, total = 0, pages = 0;
  const ids = [];
  do {
    const url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages?q='
      + encodeURIComponent(query) + '&maxResults=500' + (page ? '&pageToken=' + encodeURIComponent(page) : '');
    const r = await k.req('GET', url);
    const ms = r.messages || [];
    total += ms.length;
    pages++;
    for (const m of ms) ids.push(m.id);
    page = r.nextPageToken || null;
    if (page) await new Promise(res => setTimeout(res, 220));
  } while (page);
  return { total, pages, ids };
}

(async () => {
  const l = await k.gmail.labels();
  const { resolved, missing, byKey } = TAX.resolve(l.labels || []);
  console.log('Etichete de categorie rezolvate: ' + resolved.length + ' -> ' + resolved.map(x => x.name).join(' | '));
  if (missing.length) {
    console.log('!! CATEGORII NE-REZOLVATE (eticheta nu exista in Gmail): ' + missing.map(m => m.title).join(' | '));
  }
  // etichete care NU apartin taxonomiei, dar contin "MAVIS/" — semnal de rearanjare
  const stray = (l.labels || []).filter(x => x.name.startsWith('MAVIS/') && !resolved.some(r => r.name === x.name));
  if (stray.length) console.log('!! Etichete MAVIS/* necunoscute pentru taxonomie: ' + stray.map(x => x.name).join(' | '));

  const res = { today: TODAY, labels: [], missing, totals: { azi: 0, '24h': 0, '7z': 0, '30z': 0 } };

  for (const cat of resolved) {
    const q = `label:"${cat.name}"`;
    const row = { key: cat.key, title: cat.title, name: cat.name, counts: {}, newest: null, newestDate: null };
    for (const [w, mk] of WINDOWS) {
      const c = await countExact(mk(q));
      row.counts[w] = c.total;
      res.totals[w] = (res.totals[w] || 0) + c.total;
      if (w === '30z' && c.ids.length) {
        // ultima etichetare: ia cea mai recentă din 30z.
        // QUOTA: messages.list intoarce ID-urile in ordine descrescatoare dupa data
        // interna, deci c.ids[0] e DEJA cel mai nou. Fetcham doar 4 in loc de 25
        // (25*8 etichete = 200 cereri, singure peste bugetul de 200/rulare).
        const det = [];
        for (const id of c.ids.slice(0, 4)) {
          const m = await k.req('GET', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/' + id + '?format=metadata&metadataHeaders=Subject&metadataHeaders=Date&metadataHeaders=From');
          det.push({ id, subject: (m.payload && m.payload.headers || []).find(h => h.name === 'Subject')?.value, date: (m.payload && m.payload.headers || []).find(h => h.name === 'Date')?.value, from: (m.payload && m.payload.headers || []).find(h => h.name === 'From')?.value });
        }
        det.sort((a, b) => new Date(b.date) - new Date(a.date));
        row.newest = det[0] || null;
        row.newestDate = det[0] ? det[0].date : null;
        row.samples = det.slice(0, 4);
      }
    }
    res.labels.push(row);
    console.log(`  ${row.name.padEnd(28)} azi=${String(row.counts.azi).padStart(4)}  24h=${String(row.counts['24h']).padStart(4)}  7z=${String(row.counts['7z']).padStart(5)}  30z=${String(row.counts['30z']).padStart(5)}  ultima=${row.newestDate || 'n/a'}`);
  }

  fs.writeFileSync(OUT, JSON.stringify(res, null, 2));
  console.log('\nTOTALE: ' + JSON.stringify(res.totals));
  console.log('-> ' + OUT);
  console.log('cereri: ' + k.CALL_STATE.calls);
})();

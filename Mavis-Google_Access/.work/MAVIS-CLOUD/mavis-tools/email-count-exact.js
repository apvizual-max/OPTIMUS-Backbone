// Numarare REALA prin paginare - resultSizeEstimate din Gmail este plafonat si nefolositor.
// Nu folosim quota.js intentionat: numaram cu ritm propriu si oprim la MAX.
const k = require('./kit.js');

const MAX = 60000;      // plafon per interogare
const SLEEP = 260;     // ms intre pagini

async function count(query, label) {
  let page = null, total = 0, pages = 0, capped = false;
  do {
    const url = 'https://gmail.googleapis.com/gmail/v1/users/me/threads?q='
      + encodeURIComponent(query) + '&maxResults=500' + (page ? '&pageToken=' + encodeURIComponent(page) : '');
    const r = await k.req('GET', url);
    const ts = (r.threads || []);
    total += ts.length;
    pages++;
    page = r.nextPageToken || null;
    if (total >= MAX) { capped = true; break; }
    if (page) await new Promise(res => setTimeout(res, SLEEP));
  } while (page);
  if (capped) console.log('  ( plafon atins la ' + MAX + ' pentru ' + label + ' — numar real mai mare )');
  return { total, pages, capped };
}

async function main() {
  const out = [];
  const l = await k.gmail.labels();
  const TAX = require('./taxonomy.js');
  // NUMELE ETICHETELOR se rezolva LIVE din taxonomy.js (sursa unica de adevar).
  // Prefixul 'MAVIS/' a murit la rearanjarea din 27.10 — filtrul ar numara doar Joburi.
  const _r = TAX.resolve(l.labels || []);
  const mavis = _r.resolved.map(r => ({ name: r.name, id: r.id }));
  if (_r.missing.length) console.log('  ( etichete nerezolvate: ' + _r.missing.map(m => m.key).join(', ') + ' )');
  for (const lab of mavis) {
    const c = await count('label:' + lab.name.replace(' ', ''), lab.name);
    out.push([lab.name, c.total, c.capped]);
    console.log(pad(lab.name, 30) + String(c.total).padStart(7) + (c.capped ? '  (plafon)' : ''));
  }
  const t = await count('in:trash', 'GUNOI');
  out.push(['GUNOI (total)', t.total, t.capped]);
  console.log(pad('GUNOI (total)', 30) + String(t.total).padStart(7) + (t.capped ? '  (plafon)' : ''));
  require('fs').writeFileSync('/workspace/mavis-tools/email-counts-exact.json', JSON.stringify(out, null, 2));
  console.log('\n-> email-counts.json');
}

if (require.main === module) {
  main();
}

module.exports = { pad, count, main };

function pad(s, n) { while (s.length < n) s += ' '; return s; }

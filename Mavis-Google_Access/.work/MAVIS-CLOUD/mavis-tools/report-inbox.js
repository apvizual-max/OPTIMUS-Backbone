#!/usr/bin/env node
/**
 * RAPORT ZILNIC — INBOX: ce mesaje NOI au venit efectiv (indiferent de etichete).
 *
 * Scop: etichetele MAVIS/* pot fi stricate (filtre cu addLabelIds vid).
 * Ca să separăm "n-a venit niciun mail" de "mailul vine dar nu mai e etichetat",
 * numărăm și inbox-ul brut pe aceeași fereastră de timp ca etichetele.
 *
 * READ-ONLY. Nimic nu se modifică.
 */
const k = require('./kit.js');
const TAX = require('./taxonomy.js');
const fs = require('fs');

const TODAY = process.argv[2] || '2026/10/23';
const OUT = process.argv[3] || '/workspace/Mavis/mavis-tools/report-inbox.json';

async function list(q, max = 100) {
  const url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages?q='
    + encodeURIComponent(q) + '&maxResults=' + max;
  const r = await k.req('GET', url);
  return { ids: (r.messages || []).map(m => m.id), estimate: r.resultSizeEstimate, size: r.size };
}

function hdr(h, n) { return (h.payload && h.payload.headers || []).find(x => x.name === n)?.value || ''; }

(async () => {
  const win = {
    azi: `in:anywhere after:${TODAY}`,
    '24h': 'in:anywhere newer_than:1d',
    '7z': 'in:anywhere newer_than:7d',
    '30z': 'in:anywhere newer_than:30d',
  };
  const counts = {};
  for (const [w, q] of Object.entries(win)) {
    const r = await list(q, 1);
    counts[w] = { estimate: r.estimate, size: r.size };
  }
  console.log('INBOX/ANYWHERE (estimate, size):');
  for (const [w, c] of Object.entries(counts)) console.log(`  ${w.padEnd(5)} estimate=${String(c.estimate).padStart(6)} size=${c.size}`);

  // lista detaliată pe 7 zile, inbox real
  const recent = await list('in:inbox newer_than:7d', 100);
  console.log(`\nINBOX 7z: ${recent.ids.length} mesaje`);
  const det = [];
  for (const id of recent.ids) {
    const m = await k.req('GET', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/' + id + '?format=full');
    det.push({
      id,
      subject: hdr(m, 'Subject'),
      from: hdr(m, 'From'),
      date: hdr(m, 'Date'),
      to: hdr(m, 'To'),
      labels: m.labelIds || [],
      snippet: (m.snippet || '').slice(0, 300),
      body: extract(m),
    });
  }
  det.sort((a, b) => new Date(b.date) - new Date(a.date));
  fs.writeFileSync(OUT, JSON.stringify({ counts, messages: det }, null, 2));
  console.log('-> ' + OUT + '  (cereri: ' + k.CALL_STATE.calls + ')');
  console.log('\n--- primele 40 (subiect | de la | data | etichete) ---');
  det.slice(0, 40).forEach(d => {
    const short = d.from.replace(/<[^>]*>/g, '').slice(0, 34);
    console.log(`  ${d.date.slice(5, 22)} | ${d.subject.slice(0, 52).padEnd(52)} | ${short} | ${(TAX.resolve(d.labels || []).resolved.map(r => r.title).join(',') || '-')}`);
  });

  function extract(m) {
    let out = '';
    (function walk(p) {
      if (!p) return;
      if (p.mimeType === 'text/plain' && p.body && p.body.data) out += Buffer.from(p.body.data, 'base64').toString('utf8');
      (p.parts || []).forEach(walk);
    })(m.payload);
    if (!out) {
      const h = m.payload && m.payload.body && m.payload.body.data;
      if (h) out = Buffer.from(h, 'base64').toString('utf8');
    }
    return out.replace(/\r/g, '').slice(0, 4000);
  }
})();

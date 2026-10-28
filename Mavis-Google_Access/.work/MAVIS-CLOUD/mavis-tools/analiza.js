// Analiza inbox-ului: 201 mesaje -> grupate pe domeniu
const k = require('./kit.js');

async function all(q, cap = 250) {
  const out = [];
  const first = await k.gmail.list(q, cap);
  const ids = (first.messages || []).map(m => m.id);
  for (let i = 0; i < ids.length; i += 100) {
    const batch = ids.slice(i, i + 100);
    const boundary = 'batch_' + Date.now() + '_' + Math.random().toString(36).substring(2);
    let body = '';

    for (const id of batch) {
      body += `--${boundary}\r\n`;
      body += 'Content-Type: application/http\r\n\r\n';
      body += `GET /gmail/v1/users/me/messages/${id}?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date&metadataHeaders=List-Id HTTP/1.1\r\n\r\n`;
    }
    body += `--${boundary}--\r\n`;

    const resp = await k.req('POST', 'https://www.googleapis.com/batch/gmail/v1',
      { __raw: body, __contentType: `multipart/mixed; boundary="${boundary}"` })
      .catch(() => ({ text: async () => '' }));

    const text = typeof resp.text === 'function' ? await resp.text() : '';
    const respBoundaryMatch = resp.headers?.get?.('content-type')?.match(/boundary="?([^"]+)"?/) || text.match(/--([^\r\n]+)/);
    const respBoundary = respBoundaryMatch ? respBoundaryMatch[1] : boundary;

    const parts = text.split(`--${respBoundary}`);
    const res = [];

    for (let j = 1; j < parts.length - 1; j++) {
      const part = parts[j];
      const bodyMatch = part.match(/\r?\n\r?\n(\{[\s\S]*)/);
      if (bodyMatch) {
        try {
          res.push(JSON.parse(bodyMatch[1]));
        } catch (e) {
          res.push(null);
        }
      } else {
        res.push(null);
      }
    }

    for (let j = 0; j < batch.length; j++) {
      const d = res[j];
      if (!d || !d.payload) continue;
      const h = {};
      (d.payload.headers || []).forEach(x => h[x.name] = x.value);
      out.push({ id: d.id, subj: h.Subject || '(fără subiect)', from: h.From || '?', date: h.date || '', list: h['List-Id'] || '' });
    }
  }
  return out;
}

(async () => {
  const msgs = await all('in:inbox');
  console.log('MESAJE ANALIZATE:', msgs.length, '\n');

  const byDomain = {};
  for (const m of msgs) {
    const dm = (m.from.match(/@([\w.-]+)/) || [])[1] || 'necunoscut';
    byDomain[dm] = (byDomain[dm] || 0) + 1;
  }
  const sorted = Object.entries(byDomain).sort((a, b) => b[1] - a[1]);
  console.log('=== PE DOMENIU (top 30) ===');
  sorted.slice(0, 30).forEach(([d, n]) => console.log(`  ${String(n).padStart(3)}  ${d}`));
  console.log('\nDOMENII TOTAL:', sorted.length);

  const bulk = sorted.filter(([, n]) => n >= 3);
  console.log('DOMENII BULK (>=3 mesaje):', bulk.length, '-> acopera', bulk.reduce((a, [, n]) => a + n, 0), 'mesaje');

  const personal = msgs.filter(m => !/noreply|no-reply|newsletter|notifications?|news@|digest|@.*\.(com|net)\b/i.test(m.from) || m.from.includes('gmail.com'));
  console.log('\nPOSIBIL PERSONALE (excl. automate):', personal.length);
  personal.slice(0, 25).forEach(m => console.log(`  - ${m.subj.slice(0, 65)}  <${m.from.split('<')[1] || m.from}>`));

  require('fs').writeFileSync('/workspace/mavis-tools/inbox.json', JSON.stringify(msgs, null, 1));
  console.log('\n salvat: /workspace/mavis-tools/inbox.json');
})();

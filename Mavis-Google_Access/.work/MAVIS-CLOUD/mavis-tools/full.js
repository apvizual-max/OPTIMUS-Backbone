// Trecere completa pe tot inbox-ul, cu paginare
const k = require('./kit.js');
const fs = require('fs');

const LABELS = {
  joburi: 'MAVIS/Joburi', ai: 'MAVIS/AI si comunitati', social: 'MAVIS/Social',
  news: 'MAVIS/Newsletter', finante: 'MAVIS/Finante', personal: 'MAVIS/Personal',
  actiune: 'MAVIS/Actiune - de raspuns', facturi: 'MAVIS/Facturi si conturi',
};
const FIN   = /\b(kraken|tradingview|crypto|bitunix|coinbase|binance|factur|digi|raiffeisen|bnr|banca|invest|trading|broker|conturi|taxe)\b/i;
const JOB   = /\b(jooble|bestjobs|hipo|indeed|jobleads|recruit|job|jobs|career|careers|hiring|vacanta|angaj|aplicare|interviu|oportunitate)\b/i;
const AI    = /\b(ai|openai|anthropic|comfy|comfyui|automation|midjourney|prompt|llm|chatgpt|substack|goatacademy|twine|beehiiv|sadguru|isha|aiautomationsociety|comfy\.org)\b/i;
const SOCIAL= /\b(linkedin|skool|facebook|instagram|twitter|discord|pinterest|tiktok|politi)\b/i;

function classify(m) {
  const f = m.from || '', s = m.subj || '';
  if (/(happyadv|iqads)/i.test(f)) return /follow-up|aplicare/i.test(s) ? 'actiune' : 'personal';
  if (/\b(factur|facturi|facture|invoice)\b/i.test(s)) return 'facturi';
  if (FIN.test(f) || FIN.test(s)) return 'finante';
  if (JOB.test(f) || JOB.test(s)) return 'joburi';
  if (SOCIAL.test(f)) return 'social';
  if (AI.test(f) || AI.test(s)) return 'ai';
  return 'news';
}

async function fetchAll(q) {
  const all = [];
  let page = null;
  do {
    const url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages?q=' + encodeURIComponent(q) +
      '&maxResults=500' + (page ? '&pageToken=' + page : '');
    const r = await k.req('GET', url);
    all.push(...(r.messages || []));
    page = r.nextPageToken || null;
  } while (page);
  return all;
}

(async () => {
  const list = await fetchAll('in:inbox');
  console.log('MESAJE IN INBOX:', list.length, '\n');

  const existing = await k.gmail.labels();
  const byName = new Map(existing.labels.map(l => [l.name, l.id]));
  const ids = {}; for (const [kk, n] of Object.entries(LABELS)) ids[kk] = byName.get(n);
  const allMavisIds = Object.values(ids);

  const counts = {}; const kept = [];
  let done = 0;

  // Categorii pentru batchModify
  const buckets = {};
  for (const kk of Object.keys(LABELS)) {
    buckets[kk] = {
      add: [ids[kk]],
      remove: [...allMavisIds, 'UNREAD'],
      msgIds: []
    };
    if (kk === 'actiune' || kk === 'personal' || kk === 'facturi') {
      buckets[kk].add.push('INBOX');
    } else {
      buckets[kk].remove.push('INBOX');
    }
  }

  for (let i = 0; i < list.length; i += 100) {
    const batch = list.slice(i, i + 100);
    const boundary = 'batch_' + Date.now() + '_' + Math.random().toString(36).substring(2);
    let body = '';

    for (const m of batch) {
      body += `--${boundary}\r\n`;
      body += 'Content-Type: application/http\r\n\r\n';
      body += `GET /gmail/v1/users/me/messages/${m.id}?format=metadata&metadataHeaders=Subject&metadataHeaders=From HTTP/1.1\r\n\r\n`;
    }
    body += `--${boundary}--\r\n`;

    const resp = await k.req('POST', 'https://www.googleapis.com/batch/gmail/v1',
      { __raw: body, __contentType: `multipart/mixed; boundary="${boundary}"` })
      .catch(() => ({ text: async () => '' }));

    const text = typeof resp.text === 'function' ? await resp.text() : '';
    // Use the actual response boundary
    const respBoundaryMatch = resp.headers?.get?.('content-type')?.match(/boundary="?([^"]+)"?/) || text.match(/--([^\r\n]+)/);
    const respBoundary = respBoundaryMatch ? respBoundaryMatch[1] : boundary;

    const parts = text.split(`--${respBoundary}`);
    const ds = [];

    for (let j = 1; j < parts.length - 1; j++) {
      const part = parts[j];
      const bodyMatch = part.match(/\r?\n\r?\n(\{[\s\S]*)/);
      if (bodyMatch) {
        try {
          ds.push(JSON.parse(bodyMatch[1]));
        } catch (e) {
          ds.push(null);
        }
      } else {
        ds.push(null);
      }
    }

    for (let j = 0; j < batch.length; j++) {
      const d = ds[j]; if (!d || !d.payload) continue;
      const h = {}; (d.payload.headers || []).forEach(x => h[x.name] = x.value);
      const msg = { subj: h.Subject || '', from: h.From || '' };
      const p = classify(msg);
      counts[p] = (counts[p] || 0) + 1;

      buckets[p].msgIds.push(batch[j].id);

      if (p === 'actiune' || p === 'personal' || p === 'facturi') {
        kept.push({ eticheta: LABELS[p], subj: msg.subj.slice(0, 70), from: msg.from });
      }
      done++;
      if (done % 100 === 0) console.log('  ...', done, '/', list.length);
    }
  }

  // Aplicare batchModify pentru a reduce masiv numarul de cereri API
  for (const p in buckets) {
    const b = buckets[p];
    if (b.msgIds.length === 0) continue;
    for (let i = 0; i < b.msgIds.length; i += 1000) {
      await k.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify', {
        ids: b.msgIds.slice(i, i + 1000),
        addLabelIds: b.add,
        removeLabelIds: b.remove
      });
    }
  }

  console.log('\n=== REZULTAT COMPLET ===');
  for (const [c, n] of Object.entries(counts).sort((a,b)=>b[1]-a[1]))
    console.log(`  ${String(n).padStart(4)}  ${LABELS[c]}`);
  console.log('\nRAMASE IN INBOX:', kept.length);
  kept.forEach(x => console.log(`  [${x.eticheta}] ${x.subj}  <${x.from}>`));
  fs.writeFileSync('/workspace/mavis-tools/kept_full.json', JSON.stringify(kept, null, 1));
})().catch(e => console.error('E:', e.message));

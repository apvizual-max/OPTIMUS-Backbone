#!/usr/bin/env node
/**
 * Numarare EXACTA a mesajelor noi in inbox, pe ferestre scurte.
 * resultSizeEstimate e plafonat la 201 -> nu e numaratoare. Paginam real.
 * READ-ONLY.
 */
const k = require('./kit.js');

// data pentru ferestrele "azi" (format Gmail: AAAA/LL/ZZ). Implicit: azi.
const TODAY = process.argv[2] || new Date().toISOString().slice(0, 10).replace(/-/g, '/');

async function count(q) {
  let page = null, total = 0;
  do {
    const url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages?q='
      + encodeURIComponent(q) + '&maxResults=500' + (page ? '&pageToken=' + encodeURIComponent(page) : '');
    const r = await k.req('GET', url);
    total += (r.messages || []).length;
    page = r.nextPageToken || null;
    if (page) await new Promise(res => setTimeout(res, 200));
  } while (page);
  return total;
}

(async () => {
  const out = {};
  out.azi_inbox = await count(`in:inbox after:${TODAY}`);
  out.azi_any = await count(`in:anywhere after:${TODAY}`);
  out['24h_inbox'] = await count('in:inbox newer_than:1d');
  out['24h_any'] = await count('in:anywhere newer_than:1d');
  out['7d_inbox'] = await count('in:inbox newer_than:7d');
  out['7d_any'] = await count('in:anywhere newer_than:7d');
  console.log(JSON.stringify(out, null, 2));
  require('fs').writeFileSync('/workspace/Mavis/mavis-tools/report-inbox-counts.json', JSON.stringify(out, null, 2));
  console.log('cereri: ' + k.CALL_STATE.calls);
})();

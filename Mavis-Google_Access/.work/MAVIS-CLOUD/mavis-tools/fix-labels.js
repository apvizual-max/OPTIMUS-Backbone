// Repune clasificarile gresite: surse care au ajuns in categoria care nu le apartine.
const k = require('./kit.js');
const q = require('./quota.js');

const FIX = [
  // [eticheta gresita din care scot, eticheta corecta in care bag, filtre sursa]
  ['MAVIS/Personal', 'MAVIS/Joburi', '{from:iqads from:designproject}'],
  ['MAVIS/Social',   'MAVIS/Joburi', '{from:linkedin}'],
];

async function threadIds(query) {
  const out = []; let page = null;
  do {
    const url = 'https://gmail.googleapis.com/gmail/v1/users/me/threads?q='
      + encodeURIComponent(query) + '&maxResults=500'
      + (page ? '&pageToken=' + encodeURIComponent(page) : '');
    const r = await k.req('GET', url); await q.reserve(q.costOf('threads','list'));
    out.push(...(r.threads || []).map(t => t.id));
    page = r.nextPageToken || null;
    if (page) await new Promise(s => setTimeout(s, 280));
  } while (page);
  return out;
}

(async () => {
  const L = await k.gmail.labels();
  const M = new Map((L.labels || []).map(l => [l.name, l.id]));

  for (const [from, to, flt] of FIX) {
    const fromId = M.get(from), toId = M.get(to);
    if (!fromId || !toId) { console.log('eticheta lipsa: ' + from + ' / ' + to); continue; }
    const query = 'in:inbox ' + flt + ' -label:' + to;
    let ids = [];
    try { ids = await threadIds(query); } catch (e) { console.log('cautare blocata ' + from, e.message.slice(0, 40)); continue; }
    console.log('\n' + from + ' -> ' + to + ' : ' + ids.length + ' thread-uri de mutat');

    let done = 0;
    for (let i = 0; i < ids.length; i += 20) {
      const batch = ids.slice(i, i + 20);
      await Promise.all(batch.map(t =>
        k.req('POST',
          'https://gmail.googleapis.com/gmail/v1/users/me/threads/' + t + '/modify',
          { addLabelIds: [toId], removeLabelIds: [fromId] })
      ));
      await new Promise(r => setTimeout(r, 1000)); // safe delay between batches
      done += batch.length;
      if (i % 200 === 0) console.log('  ... ' + done + ' / ' + ids.length);
    }
    console.log('  MUTAT: ' + done);
  }
  console.log('\nGATA');
})();
// Regula lui Alex:
//  - 1-3 ani  -> sortate
//  - 3-5 ani  -> nu ne intereseaza acum
//  - 5+ ani   -> se pastreaza DOAR mesajele la care a raspuns el; restul in recycle bin (trash, reversibil)
const k = require('./kit.js');

async function searchIds(q) {
  const out = []; let p = null;
  do {
    const r = await k.req('GET', 'https://gmail.googleapis.com/gmail/v1/users/me/messages?q=' +
      encodeURIComponent(q) + '&maxResults=500' + (p ? '&pageToken=' + p : ''));
    out.push(...(r.messages || []).map(m => m.id)); p = r.nextPageToken || null;
  } while (p);
  return out;
}

(async () => {
  // volumele
  const un1 = await searchIds('older_than:1y');
  const un3 = await searchIds('older_than:3y');
  const un5 = await searchIds('older_than:5y');
  console.log('mai vechi de 1 an :', un1.length);
  console.log('mai vechi de 3 ani :', un3.length);
  console.log('mai vechi de 5 ani :', un5.length);

  const sortate = un1.length - un3.length;
  console.log('\n-> SORTATE (1-3 ani):', sortate);
  console.log('-> NU NE INTERESEAZA (3-5 ani):', un3.length - un5.length);
  console.log('-> DE EVALUAT (5+ ani):', un5.length);

  // pt 5+ ani: pastram doar thread-urile in care el a raspuns (exista mesaj cu label SENT)
  const id5 = new Set(un5);
  const ids = await searchIds('in:sent older_than:5y');
  const replied = new Set();
  for (let i = 0; i < ids.length; i += 100) {
    const rs = await Promise.all(ids.slice(i, i + 100).map(id =>
      k.req('GET', `https://gmail.googleapis.com/gmail/v1/users/me/messages/${id}?format=minimal`).catch(() => null)));
    for (const r of rs) if (r && r.threadId) replied.add(r.threadId);
  }
  console.log('\nthread-uri 5+ ani in care a raspuns:', replied.size);

  // grupam mesajele 5+ ani pe thread
  const byThread = new Map();
  for (let i = 0; i < un5.length; i += 500) {
    const rs = await Promise.all(un5.slice(i, i + 500).map(id =>
      k.req('GET', `https://gmail.googleapis.com/gmail/v1/users/me/messages/${id}?format=minimal`).catch(() => null)));
    for (const r of rs) if (r && r.threadId) {
      if (!byThread.has(r.threadId)) byThread.set(r.threadId, []);
      byThread.get(r.threadId).push(r.id);
    }
  }
  const keep = [], drop = [];
  byThread.forEach((mids, tid) => { (replied.has(tid) ? keep : drop).push(...mids); });

  console.log('  se pastreaza (a raspuns):', keep.length);
  console.log('  se trimit in recycle bin:', drop.length);

  // TRASH in loturi de 1000 (reversibil)
  for (let i = 0; i < drop.length; i += 1000) {
    try {
      await k.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/batchTrash', { ids: drop.slice(i, i + 1000) });
    } catch (e) { console.log('  batch blocat la', i, e.message.slice(0, 50)); }
  }
  console.log('\nRECYCLE BIN: ' + drop.length + ' mesaje mutate (recuperabile, NU sterse definitiv)');
})().catch(e => console.error('E:', e.message));

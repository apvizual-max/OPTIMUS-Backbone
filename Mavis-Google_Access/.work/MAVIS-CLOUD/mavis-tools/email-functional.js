/**
 * 0.8e — CAISUTA DE EMAIL FUNCTIONALA
 * Regula lui Alex:
 *   1-3 ani  -> se sorteaza
 *   3-5 ani  -> nu ne intereseaza acum
 *   5+ ani   -> se pastreaza DOAR thread-urile in care a raspuns el; restul in recycle bin
 * METODA IEFTINA: threads.list (5 unitati) in loc de messages.get (20 unitati)
 */
const k = require('./kit.js');
const q = require('./quota.js');

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
  // volumele pe varsta (messages.list = 5 unitati, ieftin)
  const v1 = await threadIds('older_than:1y');
  const v3 = await threadIds('older_than:3y');
  const v5 = await threadIds('older_than:5y');
  console.log('THREAD-uri >1 an :', v1.length, '  (cota:', q.state.used, ')');
  console.log('THREAD-uri >3 ani :', v3.length);
  console.log('THREAD-uri >5 ani :', v5.length);
  console.log('  1-3 ani  (SORTATE)      :', v1.length - v3.length);
  console.log('  3-5 ani  (nu ne intereseaza):', v3.length - v5.length);
  console.log('  5+ ani  (DE EVALUAT)    :', v5.length);

  // thread-urile 5+ ani in care a raspuns: cauta in SENT
  const replied = new Set();
  {
    let page = null;
    do {
      const r = await k.req('GET',
        'https://gmail.googleapis.com/gmail/v1/users/me/threads?q=' + encodeURIComponent('in:sent older_than:5y') +
        '&maxResults=500' + (page ? '&pageToken=' + page : ''));
      (r.threads || []).forEach(t => replied.add(t.id));
      page = r.nextPageToken || null;
    } while (page);
  }
  console.log('\nthread-uri 5+ ani in care a raspuns:', replied.size);

  const drop = v5.filter(t => !replied.has(t));
  console.log('  se pastreaza:', v5.length - drop.length);
  console.log('  in recycle bin:', drop.length);

  let done = 0;
  for (const tid of drop) {
    try { await k.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/threads/' + tid + '/trash'); done++; }
    catch (e) { console.log('  blocat la', done, e.message.slice(0, 60)); break; }
    if (done % 25 === 0) console.log('  ...', done, '/', drop.length, '| cota:', q.state.used, 'unitati');
  }
  console.log('\nRECYCLE BIN:', done, 'thread-uri (recuperabile, NU sterse definitiv)');
  console.log('cota totala consumata:', q.state.used, 'unitati');
})().catch(e => console.error('E:', e.message));

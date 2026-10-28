// Backlog rămas: rulează continuu, batch de 1000, cu reluare
const k = require('./kit.js');
const fs = require('fs');

const L = { joburi:'MAVIS/Joburi', ai:'MAVIS/AI si comunitati', social:'MAVIS/Social',
  news:'MAVIS/Newsletter', finante:'MAVIS/Finante' };

const BATCHES = [
  ['MAVIS/Newsletter',      '{from:noreply from:no-reply from:newsletter from:digest from:mail from:info from:updates from:notifications}'],
  ['MAVIS/Joburi',          '{from:jooble from:bestjobs from:hipo from:indeed from:jobleads from:recruit} {subject:job subject:angajare subject:vacanta}'],
  ['MAVIS/AI si comunitati','{from:substack from:goatacademy from:aiautomationsociety from:sadhguru from:beehiiv from:twine from:comfy from:newsletter}'],
  ['MAVIS/Social',          '{from:linkedin from:skool from:facebook from:instagram from:pinterest from:tiktok}'],
  ['MAVIS/Finante',         '{from:kraken from:tradingview from:bitunix from:coinbase from:binance}'],
];

async function ids(q) {
  const out = []; let p = null;
  do {
    const r = await k.req('GET', 'https://gmail.googleapis.com/gmail/v1/users/me/messages?q=' +
      encodeURIComponent('in:inbox ' + q) + '&maxResults=1000' + (p ? '&pageToken=' + p : ''));
    out.push(...(r.messages || []).map(m => m.id)); p = r.nextPageToken || null;
  } while (p);
  return out;
}

(async () => {
  const ex = await k.gmail.labels();
  const byName = new Map(ex.labels.map(l => [l.name, l.id]));
  for (const [labelName, query] of BATCHES) {
    const lab = byName.get(labelName);
    const found = await ids(query);
    let done = 0;
    for (let i = 0; i < found.length; i += 1000) {
      try {
        await k.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify',
          { ids: found.slice(i, i + 1000), addLabelIds: [lab], removeLabelIds: ['INBOX', 'UNREAD'] });
        done += Math.min(1000, found.length - i);
      } catch (e) { console.log('blocat la', done, e.message.slice(0, 50)); break; }
    }
    console.log(`  ${done} -> ${labelName}`);
  }
  let n = 0, p = null;
  do { const r = await k.req('GET','https://gmail.googleapis.com/gmail/v1/users/me/messages?q='+encodeURIComponent('in:inbox')+'&maxResults=1000'+(p?'&pageToken='+p:'')); n += (r.messages||[]).length; p = r.nextPageToken||null; } while (p);
  console.log('\nINBOX RAMASE:', n);
  console.log('GATA');
})().catch(e => console.error('E:', e.message));

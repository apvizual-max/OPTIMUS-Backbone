// 1) FILTRE pe server (ruleaza pentru totdeauna)  2) BACKLOG in batch de 1000
const k = require('./kit.js');
const fs = require('fs');

const L = {
  joburi:   'MAVIS/Joburi',
  ai:       'MAVIS/AI si comunitati',
  social:   'MAVIS/Social',
  news:     'MAVIS/Newsletter',
  finante:  'MAVIS/Finante',
  personal: 'MAVIS/Personal',
  actiune:  'MAVIS/Actiune - de raspuns',
  facturi:  'MAVIS/Facturi si conturi',
};

const FILTERS = [
  ['MAVIS/Joburi',            'from:(jooble bestjobs hipo indeed jobleads linkedin) OR subject:(job angajare vacanta oportunitate)'],
  ['MAVIS/AI si comunitati',  'from:(substack goatacademy aiautomationsociety sadhguru beehiiv twine) OR subject:(AI artificial intelligence)'],
  ['MAVIS/Social',            'from:(skool facebook instagram pinterest tiktok polibrawl)'],
  ['MAVIS/Newsletter',        'from:(noreply no-reply newsletter digest mail@ info@ news@ updates@)'],
  ['MAVIS/Finante',           'from:(kraken tradingview bitunix coinbase binance) OR subject:(factura investitie trading)'],
];

async function searchIds(q) {
  const out = []; let page = null;
  do {
    const url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages?q=' + encodeURIComponent(q) +
      '&maxResults=1000' + (page ? '&pageToken=' + page : '');
    const r = await k.req('GET', url);
    out.push(...(r.messages || []).map(m => m.id));
    page = r.nextPageToken || null;
  } while (page);
  return out;
}

(async () => {
  const existing = await k.gmail.labels();
  const byName = new Map(existing.labels.map(l => [l.name, l.id]));
  const ids = {}; for (const [kk, n] of Object.entries(L)) ids[kk] = byName.get(n);

  // ---- A. FILTRE pentru mailul NOU, pe server ----
  const cur = await k.req('GET', 'https://gmail.googleapis.com/gmail/v1/users/me/settings/filters');
  console.log('Filtre existente:', (cur.filter || []).length);
  for (const [labelName, query] of FILTERS) {
    const already = (cur.filter || []).some(f => f.criteria && f.criteria.query === query);
    if (already) { console.log('  filtru exista deja:', labelName); continue; }
    try {
      await k.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/settings/filters', {
        criteria: { query },
        action: { addLabelIds: [ids[labelName]], removeLabelIds: ['INBOX', 'UNREAD'] }
      });
      console.log('  filtru creat:', labelName, '-> arhiveaza automat');
    } catch (e) { console.log('  FILTRU BLOCAT', labelName, e.message.slice(0, 70)); }
  }

  // ---- B. BACKLOG: batchModify, 1000 per apel ----
  const BACK = [
    ['MAVIS/Social',           '{from:linkedin from:skool from:facebook from:instagram from:pinterest from:tiktok from:polibrawl}'],
    ['MAVIS/Joburi',           '{from:jooble from:bestjobs from:hipo from:indeed from:jobleads} {subject:job subject:angajare subject:vacanta}'],
    ['MAVIS/AI si comunitati', '{from:substack from:goatacademy from:aiautomationsociety from:sadhguru from:beehiiv from:twine from:comfy}'],
    ['MAVIS/Finante',          '{from:kraken from:tradingview from:bitunix from:coinbase from:binance}'],
    ['MAVIS/Newsletter',       '{from:noreply from:no-reply from:newsletter from:digest from:mail from:info from:updates}'],
  ];
  console.log('\n--- BACKLOG (batch de 1000) ---');
  for (const [labelName, query] of BACK) {
    const q = 'in:inbox ' + query;
    const msgIds = await searchIds(q);
    let done = 0;
    for (let i = 0; i < msgIds.length; i += 1000) {
      try {
        await k.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify', {
          ids: msgIds.slice(i, i + 1000),
          addLabelIds: [ids[labelName]], removeLabelIds: ['INBOX', 'UNREAD']
        });
        done += Math.min(1000, msgIds.length - i);
      } catch (e) { console.log('  batch blocat la', done, e.message.slice(0, 60)); }
    }
    console.log(`  ${done} -> ${labelName}`);
  }
  console.log('\nGATA');
})().catch(e => console.error('E:', e.message));

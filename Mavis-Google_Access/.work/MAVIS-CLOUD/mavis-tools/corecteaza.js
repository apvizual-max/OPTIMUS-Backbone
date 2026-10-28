// Corectie: reclasifica tot inbox-ul cu regex corect, o singura eticheta primara
const k = require('./kit.js');
const fs = require('fs');
const msgs = JSON.parse(fs.readFileSync('/workspace/mavis-tools/inbox.json'));

const LABELS = {
  joburi: 'MAVIS/Joburi', ai: 'MAVIS/AI si comunitati', social: 'MAVIS/Social',
  news: 'MAVIS/Newsletter', finante: 'MAVIS/Finante', personal: 'MAVIS/Personal',
  actiune: 'MAVIS/Actiune - de raspuns', facturi: 'MAVIS/Facturi si conturi',
};
const ALL_IDS = Object.values(LABELS).map(n => n);

const FIN   = /\b(kraken|tradingview|crypto|bitunix|coinbase|binance|factur|digi|raiffeisen|bnr|banca|banc|invest|trading|stock|broker)\b/i;
const JOB   = /\b(jooble|bestjobs|hipo|indeed|jobleads|recruit|job|jobs|career|careers|hiring|vacanta|angaj|aplicare|interviu)\b/i;
const AI    = /\b(ai|openai|anthropic|comfy|comfyui|automation|midjourney|prompt|llm|chatgpt|substack|goatacademy|twine|beehiiv|sadguru|isha)\b/i;
const SOCIAL= /\b(linkedin|skool|facebook|instagram|twitter|discord|pinterest|tiktok)\b/i;

function classify(m) {
  const f = m.from || '', s = m.subj || '';
  if (/(happyadv|iqads)/i.test(f)) return s.includes('Follow-up') || s.includes('aplicare') ? 'actiune' : 'personal';
  if (/\b(factur|facturi|facture|invoice)\b/i.test(s)) return 'facturi';
  if (FIN.test(f) || FIN.test(s)) return 'finante';
  if (JOB.test(f) || JOB.test(s)) return 'joburi';
  if (SOCIAL.test(f)) return 'social';
  if (AI.test(f) || AI.test(s)) return 'ai';
  return 'news';
}

(async () => {
  const existing = await k.gmail.labels();
  const byName = new Map(existing.labels.map(l => [l.name, l.id]));
  const ids = {}; for (const [kk, n] of Object.entries(LABELS)) ids[kk] = byName.get(n);
  const idToName = new Map(ALL_IDS.map(n => [byName.get(n), n]));

  const counts = {}; const kept = [];
  await Promise.all(msgs.map(async m => {
    const primary = classify(m);
    counts[primary] = (counts[primary] || 0) + 1;
    // scoate TOATE etichetele MAVIS vechi
    await k.gmail.removeLabel(m.id, [...idToName.keys()]);
    // pune cea corecta
    await k.gmail.addLabel(m.id, [ids[primary]]);
    if (primary === 'actiune' || primary === 'personal' || primary === 'facturi') {
      await k.gmail.addLabel(m.id, ['INBOX']);
      kept.push({ subj: m.subj.slice(0, 70), from: m.from, eticheta: LABELS[primary] });
    } else {
      await k.gmail.removeLabel(m.id, ['INBOX']);
    }
  }));

  console.log('=== REZULTAT CORECTAT ===');
  for (const [c, n] of Object.entries(counts).sort((a,b)=>b[1]-a[1]))
    console.log(`  ${String(n).padStart(3)}  ${LABELS[c]}`);
  console.log('\nINBOX, cele care raman:', kept.length);
  kept.forEach(x => console.log(`  - [${x.eticheta}] ${x.subj}\n    ${x.from}`));

  // verificare finala
  const inbox = await k.gmail.list('in:inbox', 50);
  console.log('\nVERIFICARE -> mesaje ramase in Inbox:', (inbox.resultSizeEstimate || (inbox.messages||[]).length));
  const unread = await k.gmail.list('is:unread', 1);
  console.log('VERIFICARE -> necitite ramase:', (unread.resultSizeEstimate || (unread.messages||[]).length));
})().catch(e => console.error('E:', e.message));

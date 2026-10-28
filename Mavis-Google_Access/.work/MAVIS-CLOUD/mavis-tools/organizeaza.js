// Organizare Gmail — 100% reversibil. Nicio stergere.
const k = require('./kit.js');
const fs = require('fs');
const msgs = JSON.parse(fs.readFileSync('/workspace/mavis-tools/inbox.json'));

const LABELS = {
  joburi:    'MAVIS/Joburi',
  ai:        'MAVIS/AI si comunitati',
  social:    'MAVIS/Social',
  news:      'MAVIS/Newsletter',
  finante:   'MAVIS/Finante',
  personal:  'MAVIS/Personal',
  actiune:   'MAVIS/Actiune - de raspuns',
  facturi:   'MAVIS/Facturi si conturi',
};

const JOB = /(jooble|bestjobs|hipo\.ro|indeed|jobleads|recruit|jobs|career|hiring|job)/i;
const AI  = /(ai|openai|anthropic|comfy|automation|substack|goatacademy|twinehq|beehiiv|comfy\.org|sadguru|isha)/i;
const SOCIAL = /(linkedin|skool|facebook|instagram|twitter|medium|devto)/i;
const FIN = /(kraken|tradingview|crypto|bitunix|coinbase|binance|taxi|factura|digi|orange|bnr|banc|ing|bt|raiffeisen)/i;
const NEWS = /(mail|info|news|newsletter|noreply|no-reply|updates|notify|digest|hello@|contact@)/i;

function classify(m) {
  const f = m.from, s = m.subj;
  if (/(happyadv|iqads|alex@)/i.test(f)) return ['personal', 'actiune'];
  if (/(factura|facture|invoice|facturi)/i.test(s)) return ['facturi'];
  if (JOB.test(s) || JOB.test(f)) return ['joburi'];
  if (FIN.test(f) || FIN.test(s)) return ['finante'];
  if (SOCIAL.test(f)) return ['social'];
  if (AI.test(f) || AI.test(s)) return ['ai'];
  if (NEWS.test(f)) return ['news'];
  return ['news'];
}

(async () => {
  // 1. creeaza etichetele
  const existing = await k.gmail.labels();
  const byName = new Map(existing.labels.map(l => [l.name, l.id]));
  const ids = {};
  for (const [k2, name] of Object.entries(LABELS)) {
    if (byName.has(name)) { ids[k2] = byName.get(name); console.log('exista deja:', name); }
    else { const l = await k.gmail.createLabel(name); ids[k2] = l.id; console.log('creata:', name); }
  }

  // 2. eticheteaza + citeste + arhiveaza
  const counts = {}; const kept = [];
  await Promise.all(msgs.map(async m => {
    const cats = classify(m);
    cats.forEach(c => counts[c] = (counts[c] || 0) + 1);
    const add = cats.map(c => ids[c]);
    const keep = cats.includes('personal') || cats.includes('actiune') || cats.includes('facturi');
    if (keep) kept.push({ subj: m.subj.slice(0, 70), from: m.from });

    const p1 = k.gmail.addLabel(m.id, add);
    const p2 = k.gmail.removeLabel(m.id, ['UNREAD']);
    const p3 = !keep ? k.gmail.removeLabel(m.id, ['INBOX']) : Promise.resolve();

    await Promise.all([p1, p2, p3]);
  }));

  console.log('\n=== REZULTAT ===');
  for (const [c, n] of Object.entries(counts).sort((a,b)=>b[1]-a[1]))
    console.log(`  ${String(n).padStart(3)}  ${LABELS[c]}`);
  console.log('\nRAMASE IN INBOX (nu sunt automate):', kept.length);
  kept.forEach(x => console.log(`  - ${x.subj}\n    ${x.from}`));
  fs.writeFileSync('/workspace/mavis-tools/kept.json', JSON.stringify(kept, null, 1));
})().catch(e => console.error('E:', e.message));

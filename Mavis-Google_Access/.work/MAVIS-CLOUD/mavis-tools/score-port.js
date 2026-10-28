/**
 * PORT FIDEL al ALEX-KIT/scoring.gs — rulare în Node, pentru raportul zilnic.
 *
 * METODĂ (vezi memory topic `scoring-gs-buguri-masurate`):
 *  - NU rescriem scoring.gs. Îl CITIM, aplicăm inserări cu String.replace pe
 *    anchor EXACT, apoi evaluăm cu new Function.
 *  - Fiecare anchor e verificat: dacă nu se găsește sau e ambiguu, portul
 *    REFUZĂ să ruleze (throw) — în loc să dea cifre greșite.
 *  - Singura inserție funcțională e ramura `locUnknown` (L=0, secțiune 0,
 *    verdict amânat), aplicată ÎNAINTE de excepția pentru Secțiunea 4.
 *    Locație necunoscută NU e "on-site în afara Bucureștiului".
 *
 * BUG-URI CUNOSCUTE, NEAPLICATE (portul rămâne fidel — decizia e a lui Alex):
 *  - 'ai' ca substring în youngSectors (declanșează false pe 'mai', 'email', 'maintain'...)
 *  - 'remote' în negatie ("nu se lucreaza remote/hybrid") -> L=10 in loc de L=8
 *  - SENIOR_KW matchează prin substring ('art direction' conține 'art director')
 *
 * Comparația cu bug-ul 'ai' reparat se rulează cu { fixAi: true }.
 */
const fs = require('fs');
const path = require('path');

const GS = path.join(__dirname, '..', 'ALEX-KIT', 'scoring.gs');

function patch(src, anchor, replacement, label) {
  const n = src.split(anchor).length - 1;
  if (n === 0) throw new Error(`PORT REFUZAT: anchor inexistent [${label}]`);
  if (n > 1) throw new Error(`PORT REFUZAT: anchor ambiguu (${n}x) [${label}]`);
  return src.replace(anchor, replacement);
}

const A_L = '  if (isRemote) L = 10.0; else if (inBU) L = 8.0; else L = -5.0;';
const A_S = '  var section;\n  if (!isRemote && !inBU) {';
const A_AI = '    if (has(ALEX.youngSectors.keywords[y], txt)) { isYoung = true; break; }';

function loadEngine(opts = {}) {
  const { fixAi = false } = opts;
  let src = fs.readFileSync(GS, 'utf8');

  // 1) ramura locUnknown -> L=0
  src = patch(src, A_L,
`  var locUnknown = (!loc || loc === '-' || loc === 'nepublicata' || /nepublicat/i.test(loc));
  if (locUnknown) L = 0.0; else if (isRemote) L = 10.0; else if (inBU) L = 8.0; else L = -5.0;`,
    'A_L locUnknown');

  // 2) locUnknown -> sectiune 0, INAINTE de exceptia pentru Sectiunea 4
  src = patch(src, A_S,
`  var section;
  if (locUnknown) {
    section = 0;
  } else if (!isRemote && !inBU) {`,
    'A_S locUnknown->sectiune 0');

  // 3) optional: repararea bug-ului 'ai' (doar pentru comparatie)
  if (fixAi) {
    src = patch(src, A_AI,
`    if (hasWord(txt, ALEX.youngSectors.keywords[y])) { isYoung = true; break; }`,
      'A_AI hasWord');
  }

  const factory = new Function(src + '\n; return { scoreJob: scoreJob, scoreBatch: scoreBatch, ALEX: ALEX };');
  return factory();
}

module.exports = { loadEngine, GS };

if (require.main === module) {
  const eng = loadEngine();
  console.log('port OK — scoreJob:', typeof eng.scoreJob, '| scoreBatch:', typeof eng.scoreBatch);
  // sanity: un job cu locatie cunoscuta, scorat de engine-ul portat
  const t = eng.scoreJob('Test', 'Senior Graphic Designer', 'Bucuresti', 'Full Time',
    'Experienta 7-8 ani in agentie. Portofoliu Adobe.', '');
  console.log('sanity:', JSON.stringify(t));
}

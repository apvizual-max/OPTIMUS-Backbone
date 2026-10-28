/**
 * Rulează setul de joburi prin portul fidel al scoring.gs și scoate:
 *  - cele 4 sectiuni
 *  - grupul "verdict amanat" (locratie nepublicata -> sectiune 0)
 *  - drop-urile
 *  - comparatia cu bug-ul 'ai' reparat (impact masurat)
 */
const fs = require('fs');
const path = require('path');
const { loadEngine } = require('./score-port.js');

const SET = process.argv[2] || path.join(__dirname, 'jobs-2026-10-22.json');
const data = JSON.parse(fs.readFileSync(SET, 'utf8'));
const jobs = data.jobs.map((j) => ({
  company: j.company, role: j.role, location: j.loc, engage: j.eng, jd: j.jd, notes: j.notes,
  src: j.src, url: j.url, exp: j.exp,
}));

const eng = loadEngine();
const engFix = loadEngine({ fixAi: true });

function run(engine) {
  const kept = [], dropped = [];
  for (const j of jobs) {
    const r = engine.scoreJob(j.company, j.role, j.location, j.engage, j.jd, j.notes);
    const meta = { src: j.src, url: j.url, exp: j.exp };
    if (r.dropped) dropped.push({ ...r, ...meta });
    else kept.push({ ...r, ...meta });
  }
  kept.sort((a, b) => b.score - a.score);
  return { kept, dropped };
}

const A = run(eng);
const B = run(engFix);

const S = (n) => A.kept.filter((j) => j.section === n);
const sec0 = A.kept.filter((j) => j.section === 0);

const SEC_TITLES = {
  1: 'Sectiunea 1 — Scor maxim (senior/lead, remote sau Bucuresti, full-time)',
  2: 'Sectiunea 2 — Contract / B2B (senioritate ok, engagement pe contract)',
  3: 'Sectiunea 3 — Mid-level (potrivire buna, senioritate sub prag)',
  4: 'Sectiunea 4 — On-site in afara Bucurestiului, dar S=10 si D>=8 (merita verificat)',
};

console.log('='.repeat(100));
console.log(`SCORING — ${data._meta.date} | port fidel ALEX-KIT/scoring.gs | ${jobs.length} joburi analizate`);
console.log('='.repeat(100));

for (const n of [1, 2, 3, 4]) {
  const list = S(n);
  console.log(`\n${SEC_TITLES[n]}  (${list.length})`);
  console.log('-'.repeat(100));
  if (!list.length) { console.log('  (niciun rol)'); continue; }
  console.log('  ' + 'SCOR'.padEnd(6) + 'TAG'.padEnd(7) + 'S/D/L/E'.padEnd(12) + 'ROL'.padEnd(46) + 'COMPANIE / LOCATIE / ENGAGEMENT');
  for (const j of list) {
    const sdl = `${j.S}/${j.D}/${j.L}/${j.E}`.padEnd(12);
    console.log('  ' + String(j.score).padEnd(6) + j.tag.padEnd(7) + sdl + j.role.slice(0, 44).padEnd(46) + `${j.company} | ${j.location || 'loc. nepublicata'} | ${j.engage}`);
  }
}

console.log(`\n${'='.repeat(100)}\nVERDICT AMANAT — locatie nepublicata de sursa (sectiune 0)  (${sec0.length})\n${'='.repeat(100)}`);
console.log('  ' + 'SCOR*'.padEnd(7) + 'TAG'.padEnd(7) + 'S/D/L/E'.padEnd(12) + 'ROL'.padEnd(46) + 'COMPANIE / ENGAGEMENT / EXPIRARE');
for (const j of sec0) {
  const sdl = `${j.S}/${j.D}/${j.L}/${j.E}`.padEnd(12);
  console.log('  ' + String(j.score).padEnd(7) + j.tag.padEnd(7) + sdl + j.role.slice(0, 44).padEnd(46) + `${j.company} | ${j.engage} | ${j.exp || 'n/d'}`);
}
console.log('  * scor partial: L=0 (locatia necunoscuta, nu "on-site in afara Bucurestiului")');

console.log(`\n${'='.repeat(100)}\nDROP-URI (circuit breaker)  (${A.dropped.length})\n${'='.repeat(100)}`);
for (const j of A.dropped) console.log(`  DROP  ${j.role.slice(0, 42).padEnd(44)} ${j.company.padEnd(26)} ${j.reason.replace('CIRCUIT BREAKER: ', '')}`);

console.log(`\n${'='.repeat(100)}\nCOMPARATIE: port fidel vs. bug-ul 'ai' reparat (hasWord)\n${'='.repeat(100)}`);
const bmap = new Map(B.kept.map((j) => [`${j.company}|${j.role}`, j]));
let moved = 0;
for (const j of A.kept) {
  const b = bmap.get(`${j.company}|${j.role}`);
  if (b && (b.section !== j.section || Math.abs(b.score - j.score) > 0.001)) {
    moved++;
    console.log(`  ${j.company} :: ${j.role}`);
    console.log(`      fidel : sect ${j.section}  scor ${j.score}   (S=${j.S})`);
    console.log(`      reparat: sect ${b.section}  scor ${b.score}   (S=${b.S})`);
  }
}
console.log(`  -> ${moved} joburi isi schimba sectiunea sau scorul daca se repara bug-ul 'ai'.`);
console.log(`  -> kept: fidel ${A.kept.length} / reparat ${B.kept.length} | dropped: fidel ${A.dropped.length} / reparat ${B.dropped.length}`);

const out = {
  date: data._meta.date,
  stats: { total: jobs.length, kept: A.kept.length, dropped: A.dropped.length, amanzat: sec0.length },
  sections: { 1: S(1), 2: S(2), 3: S(3), 4: S(4) },
  amanzat: sec0,
  dropped: A.dropped,
  aiBugImpact: { moved, keptFidel: A.kept.length, keptFixed: B.kept.length },
};
fs.writeFileSync(path.join(__dirname, 'scoring-result-2026-10-22.json'), JSON.stringify(out, null, 2));
console.log('\n-> mavis-tools/scoring-result-2026-10-22.json');

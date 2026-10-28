#!/usr/bin/env node
/**
 * POARTA RITUALULUI DE INCHIDERE — C6
 * C:\Users\apviz\QWEN_BACKUP\_t62-ritual-gate.js
 *
 * construita INAINTE de a avea incredere in procedura. O procedura de inchidere
 * care nu poate spune "NU GATA" nu e o procedura — e un automat de incantare.
 *
 * Fiecare mutant trebuie SA CADA, si mutantul de control trebuie SA TREACA.
 * Daca toate mutantii cad, poarta e verde. Daca mutantul de control cade si el,
 * poarta spune ca instrumentul e stricat — nu ca mutantii sunt prinsi.
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const RITUAL = path.join(__dirname, '_close-ritual.js');
const results = [];

/** construieste un director de test complet, cu un singur lucru stricat */
function gitAll(dir, args) {
  return spawnSync('git', args, { cwd: dir, encoding: 'utf8',
    env: { ...process.env, GIT_AUTHOR_NAME: 'gate', GIT_AUTHOR_EMAIL: 'g@g',
           GIT_COMMITTER_NAME: 'gate', GIT_COMMITTER_EMAIL: 'g@g',
           // hook-ul global LiveReview BLOCHEA commitul si in fixture — masurat:
           // fisierele ramaneau 'A' (staged), nu comise. Fara asta, controlul
           // pozitiv nu poate trece niciodata. Scope strict pe acest proces.
           GIT_CONFIG_COUNT: '1',
           GIT_CONFIG_KEY_0: 'core.hooksPath',
           GIT_CONFIG_VALUE_0: path.join(os.tmpdir(), 'ritual-no-hooks') } });
}

function fixture(mutator) {
  // FRATI, nu imbricate. Masurat: cu qs/ in interiorul lui root/, git trateaza qs
  // drept gitlink, si orice commit nou din qs apare drept "necomitat" in root.
  // Un fixture care reproduce accidental recursivitatea pe care masuratoarea o
  // combatte produce un fals pozitiv — si l-ar fi raportat drept defect al ritualului.
  const base  = fs.mkdtempSync(path.join(os.tmpdir(), 'ritual-'));
  const root  = path.join(base, 'harness');
  const qs    = path.join(base, 'qs');
  fs.mkdirSync(path.join(qs, 'logs'), { recursive: true });
  fs.mkdirSync(root, { recursive: true });

  // starea nominala: certificare curata, jurnale valide, fara santinele
  fs.writeFileSync(path.join(root, 'tcv_cert_ok.log'),
    'CERTIFIED 11/11\npass=11 fail=0 unknown=0\n', 'utf8');
  fs.writeFileSync(path.join(qs, 'logs', 'guardrail.jsonl'),
    JSON.stringify({ t: '2026-10-09T19:00:00Z', level: 'info' }) + '\n' +
    JSON.stringify({ t: '2026-10-09T21:00:00Z', level: 'info' }) + '\n', 'utf8');
  fs.writeFileSync(path.join(qs, 'logs', 'supervisor.jsonl'),
    JSON.stringify({ t: '2026-10-09T19:00:00Z', level: 'info' }) + '\n', 'utf8');

  // repo-uri git REALE, comise DUPA ce starea exista — altfel "necomitat" ar fi
  // chiar corect, si controlul pozitiv nu ar putea trece niciodata.
  for (const d of [root, qs]) {
    gitAll(d, ['init', '-q']);
    fs.writeFileSync(path.join(d, '.seed'), 'seed\n', 'utf8');
    gitAll(d, ['add', '-A']);
    gitAll(d, ['commit', '-q', '-m', 'seed']);
  }

  mutator(root, qs);
  return { root, qs };
}

function run(root, qs) {
  const r = spawnSync(process.execPath, [RITUAL], {
    encoding: 'utf8',
    env: { ...process.env, RITUAL_ROOT: root, RITUAL_QS: qs },
  });
  return { code: r.status, out: (r.stdout || '') + (r.stderr || '') };
}

function t(name, mutator, expectCode, mustMention) {
  const f = fixture(mutator);
  const r = run(f.root, f.qs);
  const ok = r.code === expectCode &&
             (!mustMention || r.out.includes(mustMention));
  results.push({ name, ok, code: r.code, expected: expectCode, out: r.out,
                 snippet: r.out.split(/\r?\n/).filter(l => l.includes('VERDICT'))[0] || '(fara verdict)' });
  console.log(`${ok ? 'OK  ' : 'FAIL'}  ${name}  → exit=${r.code} (asteptat ${expectCode})`);
  // la o abatere, arata CAZUL complet — o poarta care iti spune doar "2 blocate"
  // iti cere sa ghicesti, si ghicitul e exact ce a produs acest defect.
  if (!ok) {
    for (const l of r.out.split(/\r?\n/)) {
      if (/^\s+-|^\[|VERDICT/.test(l)) console.log('        | ' + l.trim());
    }
  }
}

/* ── CONTROLUL POZITIV ──────────────────────────────────────────────────────
   Daca asta cade, procedura spune "NU GATA" la orice — instrumentul e stricat.
   O poarta care prinde doar mutantii, fara sa stie ca starea buna trece, este
   o poarta care ar trece si pe un instrument permanent ros. */
t('CONTROL — stare nominala → GATA', () => {}, 0, 'VERDICT: GATA');

/* ── M1: certificare cu UNKNOWN ───────────────────────────────────────────
   un UNKNOWN nu e zero si nu e trecere. blocheaza. Suprascrie fisierul existent
   si comiteaza, ca singurul motiv de NU GATA sa fie UNKNOWN — nu un fisier necomitat. */
t('M1 uncert=1 → NU GATA', (root) => {
  fs.writeFileSync(path.join(root, 'tcv_cert_ok.log'),
    'CERTIFIED 11/11\npass=10 fail=0 unknown=1\n', 'utf8');
  gitAll(root, ['add', '-A']); gitAll(root, ['commit', '-q', '-m', 'm1']);
}, 2, 'NU GATA');

/* ── M2: certificare NU certificata ────────────────────────────────────────*/
t('M2 not-certified → NU GATA', (root) => {
  fs.writeFileSync(path.join(root, 'tcv_cert_ok.log'),
    'NOT CERTIFIED\npass=9 fail=1 unknown=1\n', 'utf8');
  gitAll(root, ['add', '-A']); gitAll(root, ['commit', '-q', '-m', 'm2']);
}, 2, 'NU GATA');

/* ── M3: santinela lrc = poarta scoasa ─────────────────────────────────────*/
t('M3 poarta dezactivata → NU GATA', (root, qs) => {
  fs.mkdirSync(path.join(qs, '.git', 'lrc'), { recursive: true });
  fs.writeFileSync(path.join(qs, '.git', 'lrc', 'disabled'), '', 'utf8');
}, 2, 'DEGRADAT');

/* ── M4: jurnal cu linie JSON rupta ───────────────────────────────────────
   trunchierea exacta (1000 de linii) e DESIGN. o linie rupta e pierdere. */
t('M4 jurnal cu linie rupta → NU GATA', (root, qs) => {
  fs.appendFileSync(path.join(qs, 'logs', 'guardrail.jsonl'),
    '{"t":"2026-10-09T21:30:00Z","lev\n', 'utf8');
}, 2, 'RUPTE');

/* ── M5: jurnal lipsa ──────────────────────────────────────────────────────*/
t('M5 jurnal absent → NU GATA', (root, qs) => {
  fs.unlinkSync(path.join(qs, 'logs', 'supervisor.jsonl'));
}, 2, 'LIPSA');

/* ── M6: niciun log de certificare ────────────────────────────────────────*/
t('M6 fara log de certificare → UNKNOWN, nu GATA', (root) => {
  fs.unlinkSync(path.join(root, 'tcv_cert_ok.log'));
}, 2, 'UNKNOWN');

/* ── REZULTAT ───────────────────────────────────────────────────────────────*/
const passed = results.filter(r => r.ok).length;
console.log('');
console.log('='.repeat(72));
for (const r of results) {
  console.log(`${r.ok ? 'PASS' : 'FAIL'}  ${r.name}`);
  if (!r.ok) console.log(`        exit=${r.code} asteptat=${r.expected} | ${r.snippet}`);
}
console.log('='.repeat(72));
console.log(`RITUAL GATE: ${passed}/${results.length}`);
process.exit(passed === results.length ? 0 : 1);
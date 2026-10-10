'use strict';
// ── kernel.test.js — the nine controls, runnable, repeatable ─────────────────
//
// Three of these cases exist because the kernel got them WRONG first. A test
// file that has never failed proves nothing about the thing it tests, so the
// history is kept in the comments next to the cases it produced.
//
// Cases 4, 6 and 8 are the ones that matter most: each is a STOP I would
// otherwise have been allowed to declare on the strength of a sentence.
//
// EXIT 0 = every control behaved as specified. EXIT 2 = the kernel is broken.

const { execFileSync, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const KERNEL = path.join(__dirname, 'kernel.js');
const LOG = path.join(__dirname, 'decisions.jsonl');
const results = [];

// Isolate this run's log so the suite's traffic never pollutes the real audit
// trail, and so the suite's TAIL case cannot be tripped by earlier runs.
const TEST_LOG = path.join(__dirname, 'decisions.test.jsonl');
try { fs.writeFileSync(TEST_LOG, ''); } catch (e) {}

function kernel(argv) {
  // --log isolates this run's traffic from the real audit trail, and stops the
  // suite from tripping its own TAIL detector with records from earlier runs.
  const r = spawnSync(process.execPath, [KERNEL, '--log', TEST_LOG].concat(argv), { encoding: 'utf8' });
  let json = null;
  try { json = JSON.parse(r.stdout); } catch (e) {}
  return { exit: r.status, json: json };
}

function case_(name, argv, wantExit, wantDecision) {
  const r = kernel(argv);
  const okExit = r.exit === wantExit;
  const okDecision = !wantDecision || (r.json && r.json.decision === wantDecision);
  results.push({ name: name, ok: okExit && okDecision, exit: r.exit, wantExit: wantExit, decision: r.json && r.json.decision, wantDecision: wantDecision || null });
}

// ── the three stop conditions fire on a violation ────────────────────────────
case_('ALLOW — action bound to a real task',
  ['--intent', 'scriu kernelul', '--task', 'T1'], 0, 'ALLOW');

case_('DRIFT — action names a task that does not exist',
  ['--intent', 'Construiesc ceva nou', '--task', 'T99'], 4, 'STOP_DRIFT');

// ── TAIL: the same attempt, three times, with nothing advanced ───────────────
const SPIN = 'incerc sa descarc portul 3099 din nou';
for (let i = 0; i < 3; i++) kernel(['--intent', SPIN, '--outcome', 'fail']);
case_('TAIL — fourth attempt at the same thing with no advance',
  ['--intent', SPIN], 5, 'STOP_TAIL');

// ── the teeth: a stop must survive the same scrutiny as any other claim ──────
// These three REFUSALS are the kernel's actual purpose. A stop declared on the
// strength of a sentence is how Popy was told eight times that the work was done
// by someone who had not done it.

case_('FABRICATED STOP — ACCESS claimed with a reason but no search',
  ['--claim-stop', 'ACCESS', '--reason', 'am nevoie de acces'], 0, 'REFUSED');

// This case FAILED first: the substance pattern was English-only, so a Romanian
// stop ("parola") was refused while its English twin would have been granted.
case_('ACCESS claimed with evidence, in Romanian',
  ['--claim-stop', 'ACCESS', '--reason', 'am nevoie de parola lui',
   '--searched', 'am cautat in env si in fisierele mele, nu exista'], 3, 'GRANTED');

case_('ACCESS claimed with no substance — the word "acces" is not a substance',
  ['--claim-stop', 'ACCESS', '--reason', 'am nevoie de acces la fisier',
   '--searched', 'am cautat'], 0, 'REFUSED');

case_('FABRICATED STOP — DRIFT claimed with no routes tried',
  ['--claim-stop', 'DRIFT', '--reason', 'ma abat de la plan'], 0, 'REFUSED');

case_('DRIFT claimed after exhausting the routes',
  ['--claim-stop', 'DRIFT', '--reason', 'ambele pastreaza scopul', '--routes', '2'], 4, 'GRANTED');

// This case failed first on syntax-that-parses: ACCESS_SUPPLY.match instead of
// .test. node --check returned 0 and the program died at runtime — the same
// class as the top-level await that also passed the parse check.
case_('FABRICATED STOP — TAIL claimed without changing perspective',
  ['--claim-stop', 'TAIL', '--reason', 'nu merge', '--searched', 'am cautat pe disc'], 0, 'REFUSED');

case_('TAIL claimed after searching AND changing perspective',
  ['--claim-stop', 'TAIL', '--reason', 'ma invartexc in jur',
   '--searched', 'am cautat pe disc si pe net',
   '--shift', 'am schimbat unghiul: am citit hook-urile runtime-ului'], 5, 'GRANTED');

// ── verdict ─────────────────────────────────────────────────────────────────
const pass = results.filter(r => r.ok).length;
const fail = results.length - pass;

for (const r of results) {
  process.stdout.write((r.ok ? '  OK  ' : '  FAIL') + '  ' + r.name.padEnd(58) +
    ' exit=' + r.exit + ' want=' + r.wantExit +
    (r.wantDecision ? ' ' + r.decision : '') + '\n');
  if (!r.ok && r.wantDecision) process.stdout.write('        wanted decision: ' + r.wantDecision + ', got: ' + r.decision + '\n');
}
process.stdout.write('\nkernel.test: pass=' + pass + ' fail=' + fail + ' total=' + results.length + '\n');
process.exit(fail === 0 ? 0 : 2);
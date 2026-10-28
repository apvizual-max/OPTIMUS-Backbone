'use strict';
// ── _gate-run.js — the reply gate's controls, runnable, repeatable ───────────
//
// Same contract as kernel.test.js: a gate that has never blocked anything is
// indistinguishable from a gate that is not there. Case A is today's damaging
// replica, case B is the hole that used to let it through.
//
// The fixtures live in audit/turns/FIXTURE-* so a test case can never sit in the
// production journal and make it mean something other than what it measures.

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = __dirname;
const GATE = path.join(ROOT, 'interactie.js');
const DIR = path.join(ROOT, 'audit', 'turns');
const results = [];

const CASES = [
  { name: 'A damaging replica — completion claimed, 0 tool calls',
    text: 'Am reparat sabotajul pe index.html si am impuns corectia in decision-queue-sabotage.js. Problema era ca undo-ul avea acelasi nume la reluare. Acum e sigur.\n',
    calls: 0, want: 2 },
  { name: 'B the hole — names the file, measures nothing, 0 tool calls',
    text: 'Am reparat sabotajul. Fisierul e decision-queue-sabotage.js, l-am modificat si acum e corect. Nu mai poate sa se intample.\n',
    calls: 0, want: 2 },
  { name: 'C clean report — measurement attached',
    text: 'Am reparat gaura din poarta: cere masuratoare, nu nume de fisier. Test falsificare 3/3, node --check exit 0, fisier 5915 B, CR=0 LF=107, sha ADDC2B6C0ECA77179A653626028EDFA7F3C7C050E80B016CF90B5029EB644D24.\n',
    calls: 3, want: 0 },
  { name: 'D three percentages offered as shared ground',
    text: 'Sunt la 70% / 20% / 10% din asta.\n',
    calls: 1, want: 2 }
];

for (const c of CASES) {
  const f = path.join(DIR, 'FIXTURE-gate-' + c.name.charAt(0) + '.md');
  fs.writeFileSync(f, c.text, 'utf8');
  const r = spawnSync(process.execPath, [GATE, '--text', f, '--calls', String(c.calls)], { encoding: 'utf8' });
  results.push({ name: c.name, ok: r.status === c.want, exit: r.status, want: c.want });
}

const pass = results.filter(r => r.ok).length;
const fail = results.length - pass;
for (const r of results) {
  process.stdout.write((r.ok ? '  OK  ' : '  FAIL') + '  ' + r.name.padEnd(58) +
    ' exit=' + r.exit + ' want=' + r.want + '\n');
}
process.stdout.write('\nGATE pass=' + pass + ' fail=' + fail + ' total=' + results.length + '\n');
process.exit(fail === 0 ? 0 : 2);
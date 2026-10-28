'use strict';
// ── acceptance.js — one command, every claim this build makes, re-measured ────
//
// Popy's acceptance condition, 2026-10-07: "poți să spui 100% cu dovezi
// empirice că task-ul s-a terminat și s-a implementat." This file exists so that
// sentence does not depend on my memory or on my willingness to say it. Run it
// and it either prints PASS with the numbers, or prints what failed.
//
// Nothing here trusts an earlier run. Every check executes now. A report that
// cites yesterday's numbers is a promise; this is a measurement.
//
// EXIT 0 = every acceptance criterion currently holds. EXIT 2 = at least one
// does not, and the output names which.

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const checks = [];
const check = (criterion, ok, measured) => checks.push({ criterion, ok: Boolean(ok), measured: String(measured) });

function run(script, args) {
  const r = spawnSync(process.execPath, [path.join(ROOT, script)].concat(args || []), { encoding: 'utf8', cwd: ROOT });
  return { exit: r.status, out: (r.stdout || '') + (r.stderr || '') };
}
function lastJsonLine(out) {
  // The heartbeat self-test prints pretty-printed JSON across several lines, and
  // the gate/suites print one object per line. Trying the whole output first is
  // what makes both shapes parse — the first version read line by line and
  // reported "gap NaN" from a self-test that had in fact passed.
  const trimmed = (out || '').trim();
  const first = trimmed.indexOf('{');
  const last = trimmed.lastIndexOf('}');
  if (first >= 0 && last > first) {
    try { return JSON.parse(trimmed.slice(first, last + 1)); } catch (e) { /* fall through */ }
  }
  const lines = trimmed.split('\n').filter(Boolean);
  for (let i = lines.length - 1; i >= 0; i--) {
    const t = lines[i].trim();
    if (t.startsWith('{')) { try { return JSON.parse(t); } catch (e) {} }
  }
  return null;
}

// ── A1. the three stop conditions, ten controls ──────────────────────────────
{
  const r = run('core/kernel.test.js');
  const m = (r.out.match(/pass=(\d+) fail=(\d+) total=(\d+)/) || []);
  check('A1 the three stop conditions fire, and a fabricated stop is refused (10 controls)',
    r.exit === 0 && m[1] === '10' && m[2] === '0',
    'pass=' + m[1] + ' fail=' + m[2] + ' exit=' + r.exit);
}

// ── A2. survives a restart with no human input ───────────────────────────────
{
  const r = run('core/restart.test.js');
  const m = (r.out.match(/pass=(\d+) fail=(\d+) total=(\d+)/) || []);
  check('A2 state and refusal history survive a restart (9 controls)',
    r.exit === 0 && m[2] === '0',
    'pass=' + m[1] + ' fail=' + m[2] + ' exit=' + r.exit);
}

// ── A3. runs with no conversation open ───────────────────────────────────────
{
  const beatsPath = path.join(ROOT, 'core', 'heartbeat.jsonl');
  const beats = fs.existsSync(beatsPath) ? fs.readFileSync(beatsPath, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l)) : [];
  const sched = beats.filter(b => b.source === 'scheduler');
  const distinctPids = new Set(sched.map(b => b.pid)).size;
  check('A3 the kernel runs on a Windows schedule, not only when I type at it',
    sched.length >= 2 && distinctPids >= 2,
    sched.length + ' scheduler beats from ' + distinctPids + ' distinct pids');

  // and it can report itself dead
  const st = run('core/heartbeat.js', ['--self-test']);
  const marked = (st.out.split('\n').filter(l => l.startsWith('SELFTEST ')).map(l => JSON.parse(l.slice(9)))[0]) || null;
  check('A4 a missing heartbeat is reported MISSING, not silently healthy',
    marked && marked.wouldReport === 'MISSING',
    marked ? ('gap ' + Math.round(marked.synthesisedGapMs / 60000) + ' min, ' + marked.beatsMissed + ' missed vs tolerance ' + marked.tolerance + ' -> ' + marked.wouldReport) : 'no SELFTEST marker in output');
}

// ── A5. the scheduled task is registered and enabled ─────────────────────────
{
  const r = spawnSync('schtasks', ['/query', '/tn', 'AgenticOS Heartbeat', '/fo', 'LIST', '/v'], { encoding: 'utf8' });
  const enabled = /Scheduled Task State:\s+Enabled/i.test(r.stdout);
  const cadence = /Repeat: Every:.*5 Minute/i.test(r.stdout);
  check('A5 Windows has the heartbeat registered, enabled, every 5 minutes', r.status === 0 && enabled && cadence,
    'status=' + r.status + ' enabled=' + enabled + ' every5min=' + cadence);
}

// ── A6. the cross-process lock and the content trap ─────────────────────────
{
  const r = run('wire-boundary.js');
  const j = lastJsonLine(r.out);
  const outFull = r.out;
  const j2 = (() => { try { return JSON.parse(outFull); } catch (e) { return null; } })();
  check('A6 cross-process lock and content trap both hold (10 checks)',
    r.exit === 0 && j2 && j2.pass === 10,
    j2 ? ('pass=' + j2.pass + ' fail=' + j2.fail) : 'no verdict');
}

// ── A7. the reply gate, both polarities ──────────────────────────────────────
// The gate runner has two names in the wild: `_gate-run.js` in the working copy
// and `gate-run.js` in the archive. Looking for exactly one of them made the
// archive fail A7 for a reason that had nothing to do with the gate — a renamed
// file is not a broken gate, and a suite that reports a rename as a defect is a
// suite that will one day hide a real one behind it.
{
  const gateRun = ['_gate-run.js', 'gate-run.js'].find(n => fs.existsSync(path.join(ROOT, n)));
  if (!gateRun) {
    check('A7 the reply gate blocks what the session proved wrong (4 controls)', false,
      'neither _gate-run.js nor gate-run.js exists beside acceptance.js');
  } else {
    const r = run(gateRun);
    const m = r.out.match(/GATE pass=(\d+) fail=(\d+)/) || [];
    check('A7 the reply gate blocks what the session proved wrong (4 controls)',
      r.exit === 0 && m[1] === '4' && m[2] === '0',
      'runner=' + gateRun + ' pass=' + m[1] + ' fail=' + m[2] + ' exit=' + r.exit);
  }
}

// ── A8. the interaction journal, and its declared limit ──────────────────────
{
  const r = run('audit/self-audit.js');
  const out = r.out;
  const m = out.match(/"verdict":\s*"(\w+)"/);
  const turns = out.match(/"turns":\s*(\d+)/);
  const limit = /declaredLimit/.test(out);
  check('A8 the interaction journal is readable and states its own blind spot',
    r.exit === 0 && m && m[1] === 'PASS' && limit,
    'verdict=' + (m ? m[1] : '?') + ' turns=' + (turns ? turns[1] : '?') + ' limitDeclared=' + limit);
}

// ── A9. §00 leads the global AGENTS.md and its commands resolve ──────────────
{
  const p = 'C:\\Users\\apviz\\.minimax\\AGENTS.md';
  const t = fs.readFileSync(p, 'utf8');
  const gate = t.indexOf('## §00. THE GATE');
  const first = t.indexOf('## §0 Language');
  const st = run('core/kernel.js', ['--state']);
  check('A9 §00 loads first in every session and the commands in it resolve',
    gate >= 0 && gate < first && st.exit === 0,
    'gate@' + gate + ' firstSection@' + first + ' kernelResolves=' + (st.exit === 0));
}

// ── A10. the live system's identity is exactly what was declared ─────────────
// Measured, not promised. The scope changed on 2026-10-07: qwen-system went from
// forbidden outright to ADDITIVE_ONLY, so this criterion's old claim — "qwen-system
// is read-only for this goal" — stopped being true the moment T8 wrote into it, and
// a criterion that kept asserting it would have been documenting a fiction while
// still printing OK. So it now asserts the split that is actually real:
//
//   READ_ONLY — one file that stays read-only whatever else changes. index.html
//               lost 14 bytes to a sabotage suite and was recovered by byte
//               arithmetic because no copy of the good state existed. That is not
//               a risk worth re-testing on the live file.
//   WRITTEN   — the files this session actually wrote, pinned to the exact content
//               their verification ran against. server.js MOVED HERE on
//               2026-10-07: it was read-only when this criterion was written, and
//               the supervision fix had to go there because that is where the
//               verdict is produced. Leaving it in READ_ONLY would have turned the
//               assertion red on the next run for the honest reason that I changed
//               the file, and the tempting wrong fix was to move the goalposts and
//               leave it there. A pin that cannot report your own change is not a
//               pin. Note what this DOES mean: the running dashboard still holds
//               the old code in memory, so these bytes are on disk and not yet in
//               the process — the same state lib/j-total.js is in.
// RE-PINNED 2026-10-09, after a falsification run proved the detector still bites.
//
// These five pins were recorded 2026-10-07. On 2026-10-09 the qwen-system work
// legitimately changed all five: server.js by the T59-B fix, index.html and the three
// lib/ files by the earlier supervision repairs. A10 correctly went red — but for a
// stale-declaration reason, not a degradation reason. Measured before re-pinning:
//
//   - all five files are CLEAN in `git status` (no modified, no untracked);
//   - all five are byte-identical to commit 3fe5185, which `git branch -r --contains`
//     shows is on origin/main — an anchor independent of this machine;
//   - index.html's new hash 7D54312AB994026C appears in the certification log
//     tcv_cert_t61b_20261009-202449.log, so the certified and the pinned state agree.
//
// Re-pinning to the current, remote-anchored bytes is therefore recording reality, not
// moving a goalpost: the bytes were already committed and pushed before this edit.
// The pins below were falsified first (one poisoned -> A10 FAIL, exit 2) and
// re-falsified after, so this criterion is known to still be able to fail.
//
// The old comment claiming the running dashboard "still holds the old code in memory"
// was true on 2026-10-07 and is now false: D9 restarted the dashboard, so the served
// bytes and these pinned bytes are the same. Left uncorrected it would document a
// fiction while printing OK, which is the exact failure this criterion exists to catch.
{
  const READ_ONLY = {
    'C:\\Users\\apviz\\AI_Tools\\qwen-system\\dashboard\\index.html':
      '7D54312AB994026C778D0402889BC55B46BBBCDEEF7CA85ECF85E1E41D15AA66'
  };
  const WRITTEN = {
    'C:\\Users\\apviz\\AI_Tools\\qwen-system\\lib\\measured-census.js':
      'F0C90D39302F2245162ECC42B34D7EC01476D242D7C5137E29B8B18AE4EC3AEC',
    'C:\\Users\\apviz\\AI_Tools\\qwen-system\\lib\\j-total.js':
      '435070C47DDE67CDF96F69FA6533C4840FE404218737EC1A314F69046FEBC520',
    'C:\\Users\\apviz\\AI_Tools\\qwen-system\\lib\\lineage-supervision.js':
      '1B1C811377EF76EC267E423837AE37F3B71F687D79A2857187C0AE5443A793FD',
    'C:\\Users\\apviz\\AI_Tools\\qwen-system\\dashboard\\server.js':
      'BAD7306B42D386AB14D64B4088C68415E0627CAE240BA0C956C927E3BA7B51A6'
  };
  let ok = true, detail = [];
  const crypto = require('crypto');
  const assertPin = (label, f, expected) => {
    if (!fs.existsSync(f)) { ok = false; detail.push(label + ' MISSING'); return; }
    const h = crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex').toUpperCase();
    const good = h.startsWith(expected);
    if (!good) ok = false;
    detail.push(path.basename(f) + '=' + h.slice(0, 16) + (good ? ' OK' : ' CHANGED!'));
  };
  for (const [f, expected] of Object.entries(READ_ONLY)) assertPin('read-only', f, expected);
  for (const [f, expected] of Object.entries(WRITTEN)) assertPin('written', f, expected);
  check('A10 the live files are byte-for-byte what this acceptance was measured against — 1 read-only, 4 written',
    ok, detail.join(' '));
}

// ── verdict ─────────────────────────────────────────────────────────────────
const pass = checks.filter(c => c.ok).length;
const fail = checks.length - pass;
process.stdout.write('\nAGENTIC OS — ACCEPTANCE, measured now, not remembered\n\n');
for (const c of checks) {
  process.stdout.write((c.ok ? '  PASS  ' : '  FAIL  ') + c.criterion + '\n');
  process.stdout.write('        ' + c.measured + '\n');
}
process.stdout.write('\npass=' + pass + ' fail=' + fail + ' total=' + checks.length + '\n');
process.exit(fail === 0 ? 0 : 2);
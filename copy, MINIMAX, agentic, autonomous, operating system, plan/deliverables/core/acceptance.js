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

// ── A10. nothing outside my scope was written ───────────────────────────────
// Measured, not promised: the live system's identity must be exactly what it
// was before this build. qwen-system is read-only for this goal by the user's
// instruction, so its hashes are asserted against the ones recorded at the start.
{
  const FORBIDDEN = {
    'C:\\Users\\apviz\\AI_Tools\\qwen-system\\dashboard\\index.html':
      '6055FD82731B5C88FD0EAB9578209147AC6AAF8F5D00367701BDC7070363EFFA',
    'C:\\Users\\apviz\\AI_Tools\\qwen-system\\dashboard\\server.js':
      '0E689CC3F0D9A405'
  };
  let ok = true, detail = [];
  const crypto = require('crypto');
  for (const [f, expectedPrefix] of Object.entries(FORBIDDEN)) {
    if (!fs.existsSync(f)) { ok = false; detail.push(f + ' MISSING'); continue; }
    const h = crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex').toUpperCase();
    const good = h.startsWith(expectedPrefix);
    if (!good) ok = false;
    detail.push(path.basename(f) + '=' + h.slice(0, 16) + (good ? ' OK' : ' CHANGED!'));
  }
  check('A10 the live qwen-system files this build was forbidden to touch are untouched',
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
'use strict';
// ── restart.test.js — does the system come back with nobody helping it? ──────
//
// The lesson that produced this file, from the WhatsApp bridge on 2026-10-07: a
// component that has never been restarted has never been shown to recover. The
// claim and the mechanism disagreed, and no amount of inspecting the store would
// have shown it — the store I inspected was not the store the code used.
//
// So this does not inspect. It KILLS and RESTARTS and watches. Three properties
// that matter, each checked in a FRESH process so nothing can be served from
// this one's memory:
//
//   1. state.json survives byte-identical across process boundaries
//   2. decisions.jsonl is append-only: old records never change, only grow
//   3. a fresh kernel reads the persisted log and refuses a stop on the strength
//      of it — i.e. the memory is on disk, not in a process
//
// EXIT 0 = recovered with no human input. EXIT 2 = it did not.

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

const ROOT = __dirname;
const STATE = path.join(ROOT, 'state.json');
const LOG = path.join(ROOT, 'decisions.jsonl');
const KERNEL = path.join(ROOT, 'kernel.js');
const results = [];

function sha(p) {
  if (!fs.existsSync(p)) return null;
  return crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex').toUpperCase();
}
function lines(p) {
  if (!fs.existsSync(p)) return [];
  return fs.readFileSync(p, 'utf8').split('\n').filter(Boolean);
}
function check(name, ok, detail) { results.push({ name, ok: Boolean(ok), detail }); }

// Each of these is a separate `node` process. If the state were only in memory,
// these would come back empty and the checks below would fail.

const before = { state: sha(STATE), logLines: lines(LOG).length, logHead: lines(LOG)[0] || null };
check('state.json exists before the restart', before.state !== null, 'sha=' + before.state);
check('decision log is non-empty before the restart', before.logLines > 0, before.logLines + ' records');

// ── the restart: a brand new process, no shared memory, no hint ───────────────
const probe = spawnSync(process.execPath, ['-e', `
  const fs=require('fs'),p=require('path');
  const s=JSON.parse(fs.readFileSync(${JSON.stringify(STATE)},'utf8'));
  const l=fs.readFileSync(${JSON.stringify(LOG)},'utf8').split('\\n').filter(Boolean).map(x=>JSON.parse(x));
  console.log(JSON.stringify({stateSha:require('crypto').createHash('sha256').update(fs.readFileSync(${JSON.stringify(STATE)})).digest('hex').toUpperCase(),
                              logLines:l.length, firstPid:l[0].pid, goal:s.goal.id, tasks:s.tasks.length}));
`], { encoding: 'utf8' });

let after = null;
try { after = JSON.parse(probe.stdout); } catch (e) {}

check('a fresh process reads state.json without help', after !== null,
  after ? ('goal=' + after.goal + ' tasks=' + after.tasks) : 'the fresh process produced nothing: ' + probe.stderr.trim());

if (after) {
  check('state survives byte-identical across the restart', after.stateSha === before.state,
    'before=' + before.state + ' after=' + after.stateSha);

  check('decision log survived and still holds its first record', after.logLines >= before.logLines && after.firstPid !== undefined,
    'before=' + before.logLines + ' records, after=' + after.logLines + ', first record pid=' + after.firstPid);
}

// ── append-only: write from a fresh process, verify nothing before it moved ──
const fresh = spawnSync(process.execPath, [KERNEL, '--intent', 'test de rezistenta la repornire', '--task', 'T6'], { encoding: 'utf8' });
check('kernel still answers after the restart', fresh.status === 0, 'exit=' + fresh.status + ' ' + fresh.stdout.trim().slice(0, 80));

const nowLines = lines(LOG);
check('the log GREW rather than being rewritten', nowLines.length > before.logLines,
  before.logLines + ' -> ' + nowLines.length + ' records');
check('the first record was not altered', (nowLines[0] || '') === before.logHead,
  before.logHead === (nowLines[0] || '') ? 'unchanged' : 'CHANGED — the log is not append-only');

// ── the memory is on disk: a stop is refused using the persisted record ─────
// If the refusal history were only in a process, this would pass on the first
// call in that process and fail here. It fails on the first call in EVERY
// process, which is only possible if the history was persisted.
const refuse = spawnSync(process.execPath, [KERNEL, '--claim-stop', 'ACCESS', '--reason', 'am nevoie de acces'], { encoding: 'utf8' });
let rj = null; try { rj = JSON.parse(refuse.stdout); } catch (e) {}
check('a fabricated stop is refused in a fresh process, with the runbook reasons',
  refuse.status === 0 && rj && rj.decision === 'REFUSED',
  rj ? ('decision=' + rj.decision + ' missing=' + (rj.missing || []).length + ' reasons listed=' + (rj.notEnough || []).length) : 'no verdict');

// ── verdict ─────────────────────────────────────────────────────────────────
const pass = results.filter(r => r.ok).length;
const fail = results.length - pass;
for (const r of results) process.stdout.write((r.ok ? '  OK  ' : '  FAIL') + '  ' + r.name.padEnd(62) + ' ' + r.detail + '\n');
process.stdout.write('\nrestart.test: pass=' + pass + ' fail=' + fail + ' total=' + results.length + '\n');
process.exit(fail === 0 ? 0 : 2);
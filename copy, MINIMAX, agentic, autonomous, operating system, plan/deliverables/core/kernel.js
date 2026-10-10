'use strict';
// ── kernel.js — the decision function. Three stop conditions, mechanically. ───
//
// Popy's specification, 2026-10-07, and this file is that specification turned
// into something that can return a non-zero exit code. It has two jobs:
//
//   1. PREFLIGHT  — before I act: is this action allowed, or does it trip one of
//                   the three stop conditions?
//   2. CLAIM-STOP — when I want to stop: can I? A stop is a claim like any other
//                   and it gets held to the same standard. Declaring ACCESS
//                   without evidence of having searched is not a stop, it is a
//                   surrender with a technical adjective attached.
//
// Every decision, allow or refuse, is appended to decisions.jsonl. That file is
// the audit trail: an operating system you cannot audit is a promise.
//
// THE POINT OF CLAIM-STOP. The failure this kernel exists to prevent is not that
// I stop too often — it is that I stop with a WORD. "I need access", "I can't
// continue", "this is impossible" — each one a sentence with no evidence behind
// it, each one costing Popy a turn. So the burden of proof runs the other way:
// to stop, I show what I searched. If I cannot show it, the kernel refuses the
// stop and tells me to keep going. The default is CONTINUE, and stopping is the
// thing that has to be earned.
//
// USAGE:
//   node kernel.js --intent "<what I am about to do>" [--task <id>] [--outcome <ok|fail>]
//   node kernel.js --claim-stop ACCESS|DRIFT|TAIL --reason "<text>"
//                   --searched "<what I searched and found>" [--routes <n>] [--shift "<what>"]
//   node kernel.js --state
//
// EXIT: 0 ALLOW / CONTINUE · 3 STOP_ACCESS · 4 STOP_DRIFT · 5 STOP_TAIL · 1 usage

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = __dirname;
const STATE = path.join(ROOT, 'state.json');
// The log is overridable so a test run cannot pollute the real audit trail, and
// so a test cannot trip its own TAIL detector with traffic from earlier runs. A
// test that writes into production data is a test that can lie.
function logPath() {
  const i = process.argv.indexOf('--log');
  return (i >= 0 && process.argv[i + 1]) ? path.resolve(process.argv[i + 1]) : path.join(ROOT, 'decisions.jsonl');
}
const LOG = logPath();

// A tail is N attempts at the same thing with no advance. Both numbers are
// policy stated here, not measured: they say what counts as spinning, they do
// not pretend to have observed it.
const TAIL_SIGNATURE_LIMIT = 3;
const DRIFT_MIN_ROUTES = 2;

// DEFECT FOUND BY ITS OWN TEST, 2026-10-07. This pattern was English-only, so a
// legitimate Romanian stop — "am nevoie de parola lui" — was REFUSED while the
// same stop in English would have been granted. A guard keyed to one language
// is not a guard, it is a preference: it silently protects the model from the
// user rather than from the failure. Popy writes Romanian; the kernel must judge
// what Popy actually says.
const ACCESS_SUPPLY = /\b(parol[ăa]|parole|password|credential|credentiale|token|cheie|api[\s_-]?key|mfa|otp|cod(\s+de\s+)?(acces|verificare|autentificare|securitate|2fa|doar\s+o\s+dat[ăa])?|plat[ăa]|card|factur|acord|aprobare|confirmare|conectare|autentificare|logare|fizic|prezent[ăa]\s+(fizic|carte)|grant|permission\s+granted)\b/i;

const args = process.argv.slice(2);
const arg = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const has = (k) => args.indexOf(k) >= 0;

function loadState() { return JSON.parse(fs.readFileSync(STATE, 'utf8')); }
function sha256(s) { return crypto.createHash('sha256').update(s, 'utf8').digest('hex').toUpperCase(); }

// Normalised signature of an attempt: the intent with numbers, paths and
// volatile words stripped, so "retried the fetch 3 times" and "retried the fetch
// 7 times" are recognised as the SAME failure rather than three fresh tries.
function signature(intent) {
  return String(intent || '')
    .toLowerCase()
    .replace(/[0-9a-f]{8,}/g, '<hex>')
    .replace(/\d+/g, '<n>')
    .replace(/[a-z]:\\[^\s"']*/g, '<path>')
    .replace(/\s+/g, ' ')
    .trim();
}

function readLog() {
  if (!fs.existsSync(LOG)) return [];
  return fs.readFileSync(LOG, 'utf8').split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch (e) { return null; } })
    .filter(Boolean);
}

function record(entry) {
  entry.at = new Date().toISOString();
  entry.pid = process.pid;
  fs.appendFileSync(LOG, JSON.stringify(entry) + '\n', 'utf8');
  return entry;
}

function out(obj, code) {
  process.stdout.write(JSON.stringify(obj, null, 2) + '\n');
  process.exit(code);
}

// ── PREFLIGHT ────────────────────────────────────────────────────────────────

function preflight() {
  const intent = arg('--intent');
  if (!intent) out({ error: 'usage: --intent "<text>"' }, 1);
  const task = arg('--task');
  const sig = signature(intent);
  const log = readLog();

  // ── TAIL: the same attempt, repeatedly, with nothing advanced ─────────────
  // DEFECT FOUND BY restart.test.js, 2026-10-07. The original rule also fired on
  // a cross-signature window: three failures of ANY intent plus zero recorded
  // advances made an UNRELATED new intent report STOP_TAIL. A tail detector that
  // punishes you for what you are NOT repeating is worse than none — it stops
  // correct work and it is unfalsifiable in the direction that matters. The window
  // is now the same intent only.
  const sameSig = log.filter(e => e.kind === 'preflight' && e.signature === sig);
  const failedSame = sameSig.filter(e => e.outcome === 'fail');
  const tailHit = failedSame.length >= TAIL_SIGNATURE_LIMIT;

  // ── DRIFT: an action that no active task accounts for ─────────────────────
  const st = loadState();
  const known = st.tasks.map(t => t.id);
  const driftHit = Boolean(task) && !known.includes(task);

  if (driftHit) {
    record({ kind: 'preflight', decision: 'STOP_DRIFT', signature: sig, intent, task, reason: 'task ' + task + ' is not in state.json' });
    return out({
      decision: 'STOP_DRIFT', exit: 4,
      condition: st.stopConditions.DRIFT,
      why: 'the action names task ' + task + ', which does not exist in state.json',
      required: 'Either bind the action to a real task, or stop because progression is genuinely blocked and every remaining path deviates from goal and plan. Then claim the stop with --claim-stop and show the routes you tried.',
      doNot: 'Do not invent a task id to make this pass.'
    }, 4);
  }

  if (tailHit) {
    const n = failedSame.length;
    record({ kind: 'preflight', decision: 'STOP_TAIL', signature: sig, intent, task, reason: n + ' attempts at the same thing with no advance' });
    return out({
      decision: 'STOP_TAIL', exit: 5,
      condition: st.stopConditions.TAIL,
      why: 'this intent has been attempted ' + n + ' times with no advance since the last thing that moved',
      signature: sig,
      required: 'Change perspective. Look at what you have NOT looked at and have NOT analysed. Search the disk. Search the internet. Search for the thing you assume is missing — you may simply never have implemented it. Somewhere the solution exists.',
      doNot: 'Do not try the same move a fourth time and do not report the repeat as progress.'
    }, 5);
  }

  record({ kind: 'preflight', decision: 'ALLOW', signature: sig, intent, task: task || null, outcome: arg('--outcome') || null });
  return out({
    decision: 'ALLOW', exit: 0,
    why: task ? ('action is bound to task ' + task) : 'no task named, no drift found, not tailing',
    priorAttemptsOfThisIntent: failedSame.length
  }, 0);
}

// ── CLAIM-STOP ───────────────────────────────────────────────────────────────
// The teeth. A stop must survive the same scrutiny as any other claim.

function claimStop() {
  const id = arg('--claim-stop');
  const reason = arg('--reason') || '';
  const searched = arg('--searched') || '';
  const routes = Number(arg('--routes') || 0);
  const shift = arg('--shift') || '';
  const st = loadState();

  if (!id || !st.stopConditions[id]) {
    return out({ error: 'unknown stop condition: ' + id, valid: Object.keys(st.stopConditions) }, 1);
  }

  // The evidence bar. Each condition needs a DIFFERENT kind of proof, because
  // they fail in different ways: ACCESS is a claim about the world, DRIFT is a
  // claim about the plan, TAIL is a claim about my own behaviour.
  const bar = {
    ACCESS: {
      need: ['reason', 'searched'],
      missing: [],
      test: () => {
        const m = [];
        if (!reason) m.push('no reason');
        if (!searched) m.push('no evidence that you searched for another route first');
        if (!ACCESS_SUPPLY.test(reason + ' ' + searched)) {
          m.push('the reason does not name something only the user can supply');
        }
        return m;
      }
    },
    DRIFT: {
      need: ['reason', 'routes'],
      missing: [],
      test: () => {
        const m = [];
        if (!reason) m.push('no reason');
        if (routes < DRIFT_MIN_ROUTES) {
          m.push('only ' + routes + ' route(s) tried; at least ' + DRIFT_MIN_ROUTES + ' must be exhausted before drift is real');
        }
        return m;
      }
    },
    TAIL: {
      need: ['reason', 'searched', 'shift'],
      missing: [],
      test: () => {
        const m = [];
        if (!reason) m.push('no reason');
        if (!searched) m.push('you have not shown that you searched the disk or the internet');
        if (!shift) m.push('you have not changed perspective — you repeated the same reasoning instead');
        return m;
      }
    }
  }[id];

  const missing = bar.test();

  if (missing.length) {
    record({ kind: 'claim-stop', decision: 'REFUSED', condition: id, reason, searched, routes, shift });
    return out({
      decision: 'REFUSED', exit: 0,
      condition: id,
      why: 'the stop was claimed but the evidence is not there',
      missing: missing,
      notEnough: bar.need,
      theRule: st.stopConditions.illegalStops,
      instruction: 'Keep going. The default is CONTINUE; a stop has to be earned. Fill the missing evidence and claim again, or do the work.'
    }, 0);
  }

  record({ kind: 'claim-stop', decision: 'GRANTED', condition: id, reason, searched, routes, shift });
  return out({ decision: 'GRANTED', exit: st.stopConditions[id].exit, condition: id, reason, searched, routes, shift }, st.stopConditions[id].exit);
}

// ── STATE ────────────────────────────────────────────────────────────────────

function showState() {
  const st = loadState();
  const log = readLog();
  const counts = log.reduce((a, e) => { a[e.decision] = (a[e.decision] || 0) + 1; return a; }, {});
  const refused = log.filter(e => e.decision === 'REFUSED').length;
  out({
    state: st,
    decisionsRecorded: log.length,
    byDecision: counts,
    stopsRefusedForLackOfEvidence: refused,
    note: refused > 0
      ? 'The kernel has already refused ' + refused + ' stop(s) for lack of evidence. That is the mechanism working, not a fault.'
      : 'No stop has yet been refused. Until one is, this is untested machinery.'
  }, 0);
}

if (has('--state')) showState();
else if (has('--claim-stop')) claimStop();
else if (has('--intent')) preflight();
else out({
  usage: [
    'node kernel.js --intent "<what I am about to do>" [--task <id>] [--outcome ok|fail]',
    'node kernel.js --claim-stop ACCESS|DRIFT|TAIL --reason "<t>" --searched "<e>" [--routes <n>] [--shift "<e>"]',
    'node kernel.js --state'
  ],
  exitCodes: { '0': 'ALLOW or CONTINUE', '3': 'STOP_ACCESS', '4': 'STOP_DRIFT', '5': 'STOP_TAIL' }
}, 1);

module.exports = { signature, preflight, claimStop, loadState };
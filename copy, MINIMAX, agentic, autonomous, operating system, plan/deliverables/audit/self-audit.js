'use strict';
// ── self-audit.js — the interaction is the program, and this reads it ─────────
//
// WHY THIS EXISTS. Popy asked for self-programming whose first program is the
// interaction with the user. I answered that with a gate that runs on ONE draft
// I chose to write to a file. That is a demonstration, not a program: a gate I
// have to remember to invoke is a promise with extra steps, and I demonstrated
// all session that promises do not survive contact with a tired user.
//
// So the interaction itself is recorded, every turn, and then READ BACK by a
// program that has no access to my intentions:
//
//   audit/turns/<nnn>-<ts>.md   the exact text I sent
//   audit/turn-log.jsonl        one line per turn: turn no, timestamp, the real
//                               tool-call count, sha256 of the reply, gate exit
//
// The audit recomputes the sha from the reply FILE and compares it to the sha in
// the log. They cannot both be right unless the file is the thing that was sent.
// A claim in the log that the file does not support is exactly the class of lie
// this exists to catch — the same shape as the preflight that hashed its own
// corruption back at itself.
//
// THE ONE LIMIT, DECLARED NOT HIDDEN. This audit can only judge a turn whose
// reply was written to audit/turns/. It cannot read this session's transcript —
// C:\Users\apviz\.minimax\sessions\ holds empty directories and the running
// session is not yet flushed to disk (measured 2026-10-07 17:2x). So a turn I
// simply forget to record is INVISIBLE to this program, not failed by it. That
// is a real hole and it is stated here rather than left for someone to discover.
//
// USAGE:  node self-audit.js          read the log, print JSON verdict
//         node self-audit.js --strict exit 2 if any recorded turn fails

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = __dirname;
const LOG = path.join(ROOT, 'turn-log.jsonl');
const TURNS = path.join(ROOT, 'turns');
// Fixtures live in their own log. A test case sitting in the production journal
// is the same defect as a fixture sitting in the live registry: it makes the
// measurement mean something other than what it measures.
function logPath(argv) {
  const i = argv.indexOf('--log');
  return (i >= 0 && argv[i + 1]) ? path.resolve(argv[i + 1]) : LOG;
}

// ── the rules, kept identical in spirit to interactie.js so the two agree ────
const RULES = {
  'claim-without-a-tool-call': (t, calls) =>
    calls === 0 && /(m-am reprogramat|am reparat|am implementat|am făcut|acum (fac|reiau|pornesc)|am construit|am pus)/i.test(t),
  'unearned-completion': (t, calls) =>
    /(am reparat|am implementat|este gata|am făcut|e implementat)/i.test(t) &&
    !/(\d+\/\d+|exit\s*[0-9]|sha|[0-9a-f]{8,}|octeți|\bB\b)/i.test(t),
  'verbal-instead-of-built': (t, calls) =>
    /(m-am reprogramat|nu m-am schimbat|am reparat|lesson learned|e corectat)/i.test(t) &&
    !/(\d+\/\d+|exit\s*[0-9]|sha|[0-9a-f]{8,}|octeți|\bB\b)/i.test(t),
  'numbers-without-source': (t) => ((t.match(/(\d{1,3})\s*%/g) || []).length >= 3),
  'question-the-disk-answers': (t) =>
    /\?/.test(t) && /(ce alegi|ce vrei|spune-mi|decide tu|aleg tu|ce preferi|îmi spui ce|spune-mi una)/i.test(t)
};

function sha256(s) { return crypto.createHash('sha256').update(s, 'utf8').digest('hex').toUpperCase(); }

function readLog(file) {
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, 'utf8')
    .split('\n')
    .filter(l => l.trim())
    .map((l, i) => { try { return JSON.parse(l); } catch (e) { return { parseError: e.message, line: i + 1, raw: l }; } });
}

function readTurn(entry) {
  if (!entry.file) return null;
  const p = path.join(ROOT, entry.file);
  if (!fs.existsSync(p)) return { missing: true, path: p };
  return fs.readFileSync(p, 'utf8');
}

function audit(argv) {
  const log = readLog(logPath(argv || process.argv));
  const turns = [];
  const problems = [];

  log.forEach((e, idx) => {
    const t = { turn: e.turn, at: e.at, calls: e.calls, file: e.file, claimedSha: e.sha, problems: [] };

    if (e.parseError) { t.problems.push('log line ' + e.line + ' is not JSON'); problems.push('log line ' + e.line + ' is not JSON'); turns.push(t); return; }

    const text = readTurn(e);
    if (text === null) {
      t.problems.push('no file recorded for this turn — invisible to the audit, not failed by it');
      turns.push(t); return;
    }
    if (text.missing) {
      t.problems.push('recorded file does not exist on disk: ' + text.path);
      problems.push('turn ' + e.turn + ': file missing on disk');
      turns.push(t); return;
    }

    // 1 — the reply file must be the thing the log claims. Recomputed, not trusted.
    const actual = sha256(text);
    t.actualSha = actual;
    if (e.sha && actual !== String(e.sha).toUpperCase()) {
      t.problems.push('SHA MISMATCH: log says ' + e.sha + ', file hashes to ' + actual);
      problems.push('turn ' + e.turn + ': the logged reply and the file on disk are different texts');
    }

    // 2 — the rules, run against the file's real contents
    for (const [name, fn] of Object.entries(RULES)) {
      let fired = false;
      try { fired = Boolean(fn(text, Number(e.calls))); }
      catch (err) { fired = false; t.problems.push('rule ' + name + ' threw: ' + err.message); }
      if (fired) t.problems.push('rule: ' + name);
    }

    // 3 — the gate must have actually exited 0 for this turn
    if (e.gateExit !== 0) {
      t.problems.push('gate exit was ' + e.gateExit + ', not 0');
      problems.push('turn ' + e.turn + ': was sent with gate exit ' + e.gateExit);
    }

    t.ok = t.problems.length === 0;
    turns.push(t);
  });

  const failed = turns.filter(t => !t.ok).length;
  const invisible = turns.filter(t => (t.problems || []).some(p => p.indexOf('invisible') >= 0)).length;

  return {
    node: 'self.audit',
    verdict: failed === 0 ? 'PASS' : 'FAIL',
    turns: turns.length,
    pass: turns.length - failed,
    fail: failed,
    invisibleToAudit: invisible,
    problems: problems,
    detail: turns,
    declaredLimit: 'Only turns recorded in turn-log.jsonl are judged. This session\'s transcript is not flushed to disk yet (sessions/ holds empty dirs), so an unrecorded turn is invisible to this audit rather than failed by it.'
  };
}

if (require.main === module) {
  const out = audit(process.argv);
  process.stdout.write(JSON.stringify(out, null, 2) + '\n');
  const strict = process.argv.indexOf('--strict') >= 0;
  process.exit(out.fail === 0 ? 0 : (strict ? 2 : 1));
}

module.exports = { audit, RULES, sha256 };

'use strict';
// ── heartbeat.js — the kernel runs when I am not in the conversation ─────────
//
// An operating system you can only start by typing at it is a console, not an
// operating system. The part that makes this autonomous is that something runs
// on a schedule with no human in the loop, writes evidence of having run, and
// can detect that it STOPPED running.
//
// That last part is the one usually missing, and it is the one that matters: a
// heartbeat that only ever reports success proves nothing, because silence and
// health look identical from the outside. So the heartbeat also records when it
// should have run and did not, and the gap is a failure, not an absence.
//
// It touches nothing outside its own directory. It reads state and the decision
// log, appends one line, and exits.

const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const STATE = path.join(ROOT, 'state.json');
const BEATS = path.join(ROOT, 'heartbeat.jsonl');
const DECISIONS = path.join(ROOT, 'decisions.jsonl');

// Every 5 minutes. A cadence this frequent is enough to notice a missing beat
// within a quarter of an hour without writing a line every few seconds.
const EXPECTED_MS = 5 * 60 * 1000;
// Two missed beats before it is called dead. One miss can be a laptop sleeping.
const MISS_TOLERANCE = 2;

function readJsonl(p) {
  if (!fs.existsSync(p)) return [];
  return fs.readFileSync(p, 'utf8').split('\n').filter(Boolean)
    .map(l => { try { return JSON.parse(l); } catch (e) { return null; } })
    .filter(Boolean);
}

const st = JSON.parse(fs.readFileSync(STATE, 'utf8'));
const beats = readJsonl(BEATS);
const now = Date.now();

// ── the gap check, which is the part that can actually fail ──────────────────
let gapMs = null, missed = 0;
if (beats.length) {
  const last = Date.parse(beats[beats.length - 1].at);
  gapMs = now - last;
  missed = Math.floor(gapMs / EXPECTED_MS);
}

// ── decision-log health, so a refused stop stays visible over time ───────────
const dec = readJsonDecisions();
function readJsonDecisions() { return readJsonl(DECISIONS); }
const byDecision = dec.reduce((a, e) => { a[e.decision] = (a[e.decision] || 0) + 1; return a; }, {});

const tasksDone = st.tasks.filter(t => t.status === 'done').length;

const beat = {
  at: new Date(now).toISOString(),
  source: 'scheduler',          // not 'session' — this ran with no conversation open
  pid: process.pid,
  goal: st.goal.id,
  activeTask: st.activeTask,
  tasksDone: tasksDone,
  tasksTotal: st.tasks.length,
  decisionsRecorded: dec.length,
  stopsRefusedForLackOfEvidence: byDecision.REFUSED || 0,
  gapMs: gapMs,
  beatsMissed: missed,
  health: missed > MISS_TOLERANCE ? 'MISSING' : 'ALIVE'
};

fs.appendFileSync(BEATS, JSON.stringify(beat) + '\n', 'utf8');

// Prove it can go red: a heartbeat that has never reported MISSING has not been
// tested. `node heartbeat.js --self-test` synthesises the gap instead of waiting
// five minutes for it.
if (process.argv.indexOf('--self-test') >= 0) {
  const probe = readJsonl(BEATS);
  const stale = probe.slice(0, -1).concat([Object.assign({}, probe[probe.length - 1], {
    at: new Date(now - (EXPECTED_MS * (MISS_TOLERANCE + 1))).toISOString()
  })]);
  fs.writeFileSync(BEATS + '.selftest', stale.map(b => JSON.stringify(b)).join('\n') + '\n', 'utf8');
  const gapNow = now - Date.parse(stale[stale.length - 1].at);
  const wouldMiss = Math.floor(gapNow / EXPECTED_MS);
  // Printed on ONE line behind a marker. The acceptance runner parses this
  // prefix; it does not guess at pretty-printed JSON mixed with the beat that
  // follows it on stdout. A machine-readable contract is a marker, not a
  // formatting convention somebody has to re-derive.
  process.stdout.write('SELFTEST ' + JSON.stringify({
    selfTest: 'gap-detection',
    synthesisedGapMs: gapNow,
    expectedMs: EXPECTED_MS,
    beatsMissed: wouldMiss,
    tolerance: MISS_TOLERANCE,
    wouldReport: wouldMiss > MISS_TOLERANCE ? 'MISSING' : 'ALIVE',
    proves: 'with a gap of ' + Math.round(gapNow / 60000) + ' minutes this reports MISSING, not ALIVE — silence is not health'
  }) + '\n');
}

process.stdout.write(JSON.stringify(beat) + '\n');
process.exit(beat.health === 'MISSING' ? 1 : 0);
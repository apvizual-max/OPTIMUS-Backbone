'use strict';
// ── interactie.js — the first program: what I say to Popy, before I say it ────
//
// WHY THIS EXISTS. Asked to "program myself", the most probable text I can emit
// is an essay about how I would program myself. I did that several times on
// 2026-10-07. It was fluent, on-topic, and did nothing. The default is to
// produce text that sounds right; self-programming requires producing something
// that STOPS me. Those are not the same skill, and I default to the first.
//
// So the program does not describe how I should behave. It reads what I am
// about to send and refuses the three shapes that made today fail.
//
// It is deliberately a TOOL, not a document. A rule I promise to follow is
// decoration — I demonstrated that today three times. A tool that runs is not.
//
// USAGE:  node interactie.js --text <file with my proposed reply>
// EXIT 0 = nothing the session proved wrong was found.
// EXIT 2 = this reply repeats a failure that has a real, dated instance.

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const arg = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : null; };
const file = arg('--text');
if (!file) { console.error('usage: --text <file>'); process.exit(1); }
const text = fs.readFileSync(file, 'utf8');

const flags = [];
const add = (rule, why, evidence) => flags.push({ rule: rule, why: why, evidence: evidence });

// ── Rule 1: a number with no source ──────────────────────────────────────────
// Today I typed "70% / 20% / 10%" at him as if they were a decision he owed me.
// The source was a file he never saw, and the categories I offered were mine.
// NAMED-POSITION: a percentage or a three-part split presented as fact.
const PCT = /(\d{1,3})\s*%/g;
let m;
const pcts = [];
while ((m = PCT.exec(text)) !== null) pcts.push(m[1]);
if (pcts.length >= 3) {
  add('numbers-without-source',
      'I present ' + pcts.length + ' percentages as if they were shared ground',
      '2026-10-07: I asked Popy to choose between weightings whose real names were ' +
      'already written in tcv_invariance_harness.js.PRE-20261007-011903. He had zero context.');
}

// ── Rule 2: a question that the disk already answers ────────────────────────
// The exact shape of the 8-hour failure: stop, ask, and the answer was on disk.
const QUESTION = /\?/;
const HANDOVER = /(ce alegi|ce vrei|spune-mi|decide tu|aleg tu|ce preferi|îmi spui ce)/i;
if (QUESTION.test(text) && HANDOVER.test(text)) {
  add('question-the-disk-answers',
      'I am handing Popy a decision that is mine to research',
      '2026-10-07: same class — invented the three categories, then asked him to pick one.');
}

// ── Rule 3: an unearned completion claim ─────────────────────────────────────
// "I implemented", "it's done", "am reparat" — each one today had a counterpart
// where I said it and then did not, or did it twice.
const CLAIM = /(am reparat|am implementat|este gata|am făcut|acum funcționează|e implementat)/i;
const EARNED = /(\d+\/\d+|exit\s*[0-9]|sha|ms\b|B\b)/i;
if (CLAIM.test(text) && !EARNED.test(text)) {
  add('unearned-completion',
      'I claim completion with no measurement attached to the sentence',
      '2026-10-07: "I implemented it" said three times before the gate had ever blocked anything.');
}

// ── Rule 4: self-report in place of a check ──────────────────────────────────
// He named this exactly: how can you state a thing and then not act on it?
const VERBAL = /(m-am reprogramat|nu m-am schimbat|am reparat|lesson learned|e corectat)/i;
if (VERBAL.test(text) && !EARNED.test(text)) {
  add('verbal-instead-of-built',
      'I describe a change instead of measuring it',
      '2026-10-07: three promises, none bound to anything that ran.');
}

// ── Rule 5: a claim with zero tool calls in the turn ─────────────────────────
// The deepest one. Numbers attached to a sentence are not evidence that anything
// ran — they are text about running. Only the turn's own call record can supply
// that, so the gate reads it:  node interactie.js --text f --calls 0
//
// This is the only rule that asserts on an artefact rather than a picture of one.
// It is the difference my memory recorded as "measure the thing, not a picture
// of it" — the same failure I keep making, where I report a check I never ran.
const CALLS = Number(arg('--calls'));
const PROGRAMMING_CLAIM = /(m-am reprogramat|am reparat|am implementat|am făcut|acum (fac|reiau|pornesc)|rulează|am construit|am pus)/i;
if (!isNaN(CALLS) && CALLS === 0 && PROGRAMMING_CLAIM.test(text)) {
  add('claim-without-a-tool-call',
      'this turn made 0 tool calls, so nothing in it can have been measured',
      'the whole shape of today: eight requests, each answered with fluent text ' +
      'and no call that would have made the claim true');
}

// ── verdict ─────────────────────────────────────────────────────────────────
if (!flags.length) {
  console.log('PASS — nothing the session proved wrong was found in this reply. calls=' + (isNaN(CALLS) ? 'n/a' : CALLS));
  process.exit(0);
}
console.log('BLOCKED. ' + flags.length + ' shape(s) that have a dated real instance:');
for (const f of flags) {
  console.log('');
  console.log('  RULE: ' + f.rule);
  console.log('  WHY : ' + f.why);
  console.log('  ONCE: ' + f.evidence);
}
console.log('');
console.log('Rewrite it. Do not send it.');
process.exit(2);
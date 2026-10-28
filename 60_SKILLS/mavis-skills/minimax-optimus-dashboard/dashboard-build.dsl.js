// ═══════════════════════════════════════════════════════════════════════════
// dashboard-build.dsl.js — the executable build workflow
// ═══════════════════════════════════════════════════════════════════════════
//
// WHAT THIS IS
//   A runnable version of the method in `minimax-optimus-dashboard`, for the
//   case where Popy says "build me a dashboard for this system" and the session
//   has zero memory of the last one.
//
// WHY IT IS A WORKFLOW AND NOT A DOCUMENT
//   Because the expensive part was never the knowledge. It was the ORDER, and
//   the fact that four different verification layers were built in the wrong
//   order — or not at all. A panel whose clause and mutation were written
//   AFTER the panel shipped is a panel nobody can trust, and that is exactly
//   what happened for six runs on the Qwen dashboard: 105 green clauses, and
//   the form had never been pressed once.
//
// THE SHAPE
//   Seven phases. Three of them are gates that can stop the run, and one of
//   those gates is Popy. Everything else is the agent doing what it should
//   have done without being asked.
//
//   0 PREFLIGHT   measure the current state before touching anything
//   1 DISCOVERY   one batched questionnaire, answered while the system is inventoried
//   2 PLAN        on paper, with the refresh budget computed, then R0 — STOP
//   3 BUILD       panel by panel, each one leaving its four proofs behind it
//   4 VERIFY      four layers, all mandatory, plus the second-load test
//   5 ITERATE     six passes, each from a different angle
//   6 HANDOVER    the dashboard, the restore point, the running list
//
// THE FOUR PROOFS. Every panel leaves all four, in phase 3, before phase 4
// exists. This is the single most important structural claim in the file.
//
//   1. CONTRACT CLAUSE   a fixture drives the rule, and the DOM is read back.
//                        A harness that recomputes the rule proves its own
//                        arithmetic, not the panel's.
//   2. CLICK-THROUGH     a real finger on a real control, in a real browser.
//                        SEEDING STATE IS NOT DRIVING STATE.
//   3. FAULT INJECTION   make the panel throw; require the others to survive
//                        AND the failure to be visible. A guard that catches
//                        and drops trades a blank panel for a quiet one.
//   4. MUTATION          break the rule on purpose; require the clause to go
//                        red. A suite nobody has seen go red is a decoration.
//
// INPUT
//   input.subject    the system to build a surface over
//   input.root       where the code lives (or "" to discover it)
//   input.live       how the thing is already running, if at all
//   input.reference  a surface to match, if he named one
//
// EXECUTOR NOTE
//   mcode mode uses the signed-in identity and smart permissions and does not
//   sandbox. Phase 0 is the only phase that must be allowed to touch a machine
//   it has not measured yet, and it touches nothing.
// ═══════════════════════════════════════════════════════════════════════════

// ───────────────────────────────────────────────────────────────────────────
// PHASE 0 · PREFLIGHT — measure, touch nothing
// ───────────────────────────────────────────────────────────────────────────
await ctx.phase({ id: 'preflight', label: 'Preflight — establish ground truth' });

const preflight = await ctx.agent({
  id: 'preflight.measure',
  label: 'Measure the current state',
  phase: 'preflight',
  dependsOn: [],
  prompt:
    'You are starting a dashboard build. Before writing anything, produce a STATE ' +
    'file. Do NOT edit a single file in this phase. Everything below is a measurement, ' +
    'not a plan.\n\n' +
    '1. LOCATE. Find the existing code if it exists: entry points, the server/daemon, ' +
    'the page, the test harness. If a project skill exists for this system, read it and ' +
    'record its stated hashes so you can detect drift.\n\n' +
    '2. HASH EVERYTHING THAT MATTERS. Full SHA, byte count, line-ending style (count CR), ' +
    'BOM presence, and for every script block the parse status. Write these into the ' +
    'STATE file. A format invariant that is not measured is not an invariant.\n\n' +
    '3. RECORD WHAT RUNS. Is the service up? Which port, which process, which command ' +
    'line? How was it started — is there a supervisor, a startup entry, or was it ' +
    'launched by hand? This decides whether you may restart it later.\n\n' +
    '4. NAME THE PROHIBITIONS. What is load-bearing on this machine that must not be ' +
    'pruned, killed, or rewritten? Ask if you cannot tell. One past incident is enough ' +
    'to justify a prohibition forever.\n\n' +
    '5. LIST WHAT YOU DID NOT MEASURE, explicitly. This list is the honest beginning of ' +
    'the running list, and it is the first thing a reader checks.\n\n' +
    'Output a markdown STATE file with a "MEASURED" section and an "UNMEASURED" section, ' +
    'and a one-line verdict on whether the target is safe to build on. If it is not, ' +
    'say why in one line and stop.',
  input: { subject: '', root: '', live: '', reference: '' }
});

if (preflight.status !== 'ok') {
  ctx.log('PREFLIGHT FAILED: ' + (preflight.error || 'unknown') +
    '. Nothing was written. Do not proceed to discovery on an unmeasured machine.', { phase: 'preflight' });
} else {
  ctx.checkpoint('state.file', preflight.output);
  ctx.log('Preflight complete. Ground truth recorded. Nothing modified.', { phase: 'preflight' });
}

// ───────────────────────────────────────────────────────────────────────────
// PHASE 1 · DISCOVERY — the part Popy said took the longest
// ───────────────────────────────────────────────────────────────────────────
//
// The complaint was "too many questions, and I had to answer them twice".
// Both halves have a fix, and neither is "ask better":
//
//   * ASK ONCE, BATCHED, ONCE. One questionnaire, six sections, answered in a
//     single sitting. Never one question per turn.
//   * INVENTORISE WHILE HE ANSWERS. The half of discovery nobody does is
//     walking the actual system. Doing it in parallel means the questions he
//     answers can be answered with a real number instead of a guess, and most
//     of them turn out not to need asking at all.
//
// A question that can be answered by running something must never be asked.

await ctx.phase({ id: 'discovery', label: 'Discovery — one questionnaire, and a real inventory' });

const inventory = await ctx.agent({
  id: 'discovery.inventory',
  label: 'Inventorise the real system',
  phase: 'discovery',
  dependsOn: ['preflight.measure'],
  prompt:
    'Walk the subject system the way you would walk a building you have to sign off. ' +
    'Read-only. No edits, no restarts, no writes of any kind.\n\n' +
    'For every candidate number you find, get BOTH its source AND its cost. Measure ' +
    'the cost — do not assume it. A health check that you assume is fast is the single ' +
    'most common cause of a dashboard that feels broken under load.\n\n' +
    'Cover: processes and their parents · listening sockets and who owns them · ' +
    'endpoints the system exposes, with real timings · files and stores that hold state, ' +
    'and who writes them · anything that restarts on reboot · anything that has failed ' +
    'before and left a trace in a log.\n\n' +
    'Every state must be one of: OK, WARNING, FAILING, or NOT_MEASURED. Never a healthy ' +
    'default for something you did not read. NOT_MEASURED is a first-class answer and is ' +
    'always better than a guess.\n\n' +
    'Finish with: the three things about this system that would surprise a newcomer, and ' +
    'the one thing that would be most expensive to get wrong on screen.',
  input: { subject: '' }
});

const questionnaire = await ctx.agent({
  id: 'discovery.ask',
  label: 'Produce the single batched questionnaire',
  phase: 'discovery',
  dependsOn: ['preflight.measure'],
  schema: {
    type: 'object',
    properties: {
      purpose: { type: 'string' },
      decision: { type: 'string' },
      states: { type: 'array', items: { type: 'string' } },
      mustNeverBeWrong: { type: 'array', items: { type: 'string' } },
      explicitlyNotWanted: { type: 'array', items: { type: 'string' } },
      reference: { type: 'string' },
      restorePoint: { type: 'string' },
      mayRunDestructive: { type: 'boolean' },
      questions: { type: 'array', items: { type: 'string' } }
    }
  },
  prompt:
    'Using the inventory just produced, write ONE questionnaire for Popy. All of it, at ' +
    'once. He has answered these across several sessions and every batched round was ' +
    'better than the last.\n\n' +
    'HARD RULE: exclude every question the inventory can answer. If a number is ' +
    'measurable, do not ask him for it. Keep only what he alone knows: purpose, the ' +
    'decision the surface supports, what must never be wrong, what he explicitly does ' +
    'not want, and the standards he holds it to.\n\n' +
    'Aim for under fifteen questions, grouped in six sections: purpose, domain, ' +
    'measurability, constraints, standards, risk. For each, say WHY you need it in one ' +
    'line, so he can answer or skip deliberately.\n\n' +
    'Also state, in one sentence, the purpose of the whole surface. If you cannot, the ' +
    'discovery is not finished — say so and do not ask the rest yet.'
});

if (inventory.status !== 'ok' || questionnaire.status !== 'ok') {
  ctx.log('DISCOVERY INCOMPLETE: ' +
    (inventory.error || questionnaire.error || 'one half failed') +
    '. Do not plan on a half-inventory. Report which half is missing and why.', { phase: 'discovery' });
} else {
  ctx.checkpoint('discovery.inventory', inventory.output);
  ctx.checkpoint('discovery.questions', questionnaire.output);
}

// ───────────────────────────────────────────────────────────────────────────
// PHASE 2 · PLAN ON PAPER, THEN R0 — AND STOP
// ───────────────────────────────────────────────────────────────────────────
//
// The habit this replaces: building "while he reviews". The result is that a
// five-hour outage ships with a green suite, because the change was inside the
// system the measurement came from.
//
// Confidence in a mechanism is not a mandate.

await ctx.phase({ id: 'plan', label: 'Plan on paper — five questions, then R0, then STOP' });

const plan = await ctx.agent({
  id: 'plan.paper',
  label: 'Answer the five paper questions with arithmetic',
  phase: 'plan',
  dependsOn: ['discovery.inventory', 'discovery.ask'],
  prompt:
    'Write the plan as a set of claims, each of which must survive an attempt to break it. ' +
    'Answer these five specifically, with numbers:\n\n' +
    '1. What is the slowest thing here, and what happens when it is slow? ' +
    'MULTIPLY measurement cost by refresh interval. If the product is 1 or more the ' +
    'design is saturated and the operator will feel it as intermittent freezing. Show the ' +
    'multiplication.\n\n' +
    '2. What happens if the data source disappears mid-render? Last good must survive, ' +
    'marked old. Stale beats blank, always.\n\n' +
    '3. What happens on restart? A process that read its source once is not the source if ' +
    'the source can change. Decide now whether the design detects that.\n\n' +
    '4. What is the failure mode of the failure handler? Trace error to handler to ' +
    'display. If any link fails silently, there is a hole, and that hole is where a ' +
    'blank tab is born.\n\n' +
    '5. What does this design cost the system it observes, including your own ' +
    'maintenance habits?\n\n' +
    'Then: state the build order argued from rework cost, the refresh budget computed, the ' +
    'design language decided NOW, and the definition of done in his words.\n\n' +
    'Every dependency must have been EXECUTED, not read about. Record version measured and ' +
    'what breaks without it.\n\n' +
    'Finally, answer: what did I plan and not write down?'
});

if (plan.status === 'ok') {
  ctx.checkpoint('plan.text', plan.output);
  ctx.log('PLAN READY. Present it and WAIT for R0. Do not begin building while he reviews.', { phase: 'plan' });
}

// ───────────────────────────────────────────────────────────────────────────
// PHASE 3 · BUILD — panel by panel, each leaving four proofs
// ───────────────────────────────────────────────────────────────────────────
//
// THE STRUCTURAL CLAIM OF THIS FILE. Each panel is finished only when it has
// all four proofs, and the proofs are written BEFORE the next panel starts.
//
// The Qwen dashboard shipped 105 green clauses against a form that had never
// been pressed. A suite that only seeds state proves the read path and nothing
// about the write path — and a read path can be perfect while the write path
// destroys data. So: contract, click, break, and re-break, per panel.

await ctx.phase({ id: 'build', label: 'Build — one panel at a time, four proofs each' });

const panelIndex = await ctx.agent({
  id: 'build.order',
  label: 'Order the panels and name each proof',
  phase: 'build',
  dependsOn: ['plan.paper'],
  prompt:
    'List the panels this surface needs, in build order, argued from rework cost: ' +
    'most-uncertain first, and the pure-data panel before anything that reads it.\n\n' +
    'For each panel, name its FOUR proofs before writing any of it:\n\n' +
    '  1. CONTRACT CLAUSE  — the fixture that drives this panel rule, and the exact DOM ' +
    '        that will be read back. What must MOVE for the clause to mean anything? A ' +
    '        clause that passes on broken code is not a clause.\n' +
    '  2. CLICK-THROUGH    — the control a person will actually press, and what must ' +
    '        appear. Every write path needs this. A panel with a button and no ' +
    '        click-through is an untested button.\n' +
    '  3. FAULT INJECTION  — how this panel fails, and what the other panels must still ' +
    '        do when it does. The failure must be VISIBLE in this panel, not swallowed.\n' +
    '  4. MUTATION         — the single change to this panel that must turn its clause ' +
    '        red. If you cannot name one, the clause is not load-bearing.\n\n' +
    'Also record, per panel, its data source and its refresh cost, and whether it can be ' +
    'derived from payloads already in hand. A new request on an already-serialised path ' +
    'is a new race, and that is a rework decision, not a detail.'
});

if (panelIndex.status === 'ok') {
  ctx.checkpoint('build.order', panelIndex.output);
  ctx.log('Build order fixed. Each panel is finished only when its four proofs exist.', { phase: 'build' });
}

const pureRule = await ctx.agent({
  id: 'build.pure-rule',
  label: 'The rule stays pure, and the render chain stays guarded',
  phase: 'build',
  dependsOn: ['build.order'],
  prompt:
    'Two structural rules that have each cost a run when broken.\n\n' +
    'ONE. The decision rule must be a PURE FUNCTION of the payloads already in hand — no ' +
    'DOM, no fetch, no clock. Not "mostly pure". Pure, because that is the only reason a ' +
    'fixture can drive it and a test can mean anything. If the rule needs a request, that ' +
    'is a build-order decision, made now, not discovered later.\n\n' +
    'TWO. Every renderer in the chain runs inside a guard, and the guard PAINTS the failure ' +
    'into that panel own container — in the same UNKNOWN red used for a reading it could ' +
    'not take. Two reasons this is not optional:\n' +
    '   - The order of statements in a render chain is a dependency nobody wrote down. ' +
    '     One throw silently cancelled every statement after it, and because the ' +
    '     function was async it surfaced as a single unhandled rejection. The whole tab ' +
    '     rendered blank after every page refresh, and nothing logged it.\n' +
    '   - A guard that catches and drops trades a blank panel for a QUIET one, which is ' +
    '     worse. A panel that says nothing must never look like a panel that measured zero.\n\n' +
    'And note the consequence, because it will bite again: adding a guard CHANGES what a ' +
    'fault looks like. Checks written before the guard may now pass on broken code. Re-point ' +
    'them at the visible signal, not at the disappearance.'
});

if (pureRule.status !== 'ok') {
  ctx.log('STRUCTURE FAILED: ' + (pureRule.error || 'unknown') +
    '. Do not proceed to VERIFY. A build whose rule is impure and whose chain is ' +
    'unguarded cannot be honestly tested.', { phase: 'build' });
} else {
  ctx.checkpoint('build.structure', pureRule.output);
}

// ───────────────────────────────────────────────────────────────────────────
// PHASE 4 · VERIFY — four layers, all mandatory, plus the second load
// ───────────────────────────────────────────────────────────────────────────

await ctx.phase({ id: 'verify', label: 'Verify — four layers, and the second load' });

const verify = await ctx.agent({
  id: 'verify.four-layers',
  label: 'Run the four layers, then the triage',
  phase: 'verify',
  dependsOn: ['build.pure-rule'],
  prompt:
    'Run all four layers. Not three. Report which layer caught what.\n\n' +
    '1. CONTRACT   — parse every script block separately, not the file. A file check ' +
    '  that passes while one block is broken proves nothing, because a page that does ' +
    '  not parse still answers 200 and still serves perfect data.\n' +
    '2. BEHAVIOURAL — load it in a real browser. Read RENDERED GEOMETRY, not element ' +
    '  existence: height, visibility, and the text a person would read. Press every ' +
    '  control. Use textContent per element for content equality — innerText is the ' +
    '  RENDERED text, raised by text-transform and reflowed by wrapping, and it will ' +
    '  make a verbatim quote fail against a correct panel.\n' +
    '3. FAULT      — make a panel throw, mid-chain. Require: the panels after it still ' +
    '  paint, AND the faulted panel says so. Then read the blast radius from the STACK ' +
    '  TRACE, never from a source window — a 3000-character window missed a real ' +
    '  cross-panel dependency that the trace named in one line.\n' +
    '4. MUTATION   — break each rule on purpose, in the live file, restore from an ' +
    '  in-memory copy verified by SHA taken BEFORE the run. Every mutation must CHANGE ' +
    '  BEHAVIOUR and turn its named clauses red. Print the NAMES of the red clauses, ' +
    '  never only the count.\n\n' +
    'THEN, THE TEST NOBODY RUNS: reload the page and repeat the behavioural layer. A ' +
    'state that only appears on the SECOND load — a one-entry history, a partially ' +
    'written file, a cached value — is a state a fresh-profile suite never visits. The ' +
    'worst defect in the Qwen build passed every first-load test and blanked the whole ' +
    'tab on every refresh.\n\n' +
    'TRIAGE, before repairing anything: for each red, ask WHOSE DEFECT IS THIS. In the ' +
    'Qwen runs more reds were the harness than the product, and every one was reported ' +
    'as a product defect with total confidence. Sixteen independent clauses agreed with ' +
    'each other, which reads as a strong signal rather than a weak one. Check, in order: ' +
    'was the fixture seeded at all; does the clause point at the surface it reads; was ' +
    'the flag and its explanation sampled at the same instant; was an async result awaited ' +
    'before being inspected.'
});

if (verify.status !== 'ok') {
  ctx.log('VERIFY DID NOT COMPLETE: ' + (verify.error || 'unknown') +
    '. A suite that did not run is not a passing suite.', { phase: 'verify' });
} else {
  ctx.checkpoint('verify.report', verify.output);
  ctx.log('Four layers run, second load tested. Triage before any repair.', { phase: 'verify' });
}

// ───────────────────────────────────────────────────────────────────────────
// PHASE 5 · ITERATE — six passes, each from a different angle
// ───────────────────────────────────────────────────────────────────────────

await ctx.phase({ id: 'iterate', label: 'Iterate — six passes, six angles' });

// These six are written out one by one, and that is the point.
//
// The first draft of this file built them in a `for` loop over an array. It
// validated, and it was WRONG. The loop produces a dynamic node, the planner
// cannot resolve `iterate.handover` statically, and so the handover's declared
// dependency silently resolved to NOTHING: `handover.pack` came out of the
// validator with `dependsOn: []` and no incoming edge at all. The run would have
// packaged the handover while the six passes were still working, from a run that
// had produced no findings for it to package.
//
// The validator said `unresolvedDependencies` — in `warnings`, not in `issues`.
// `valid: true`. A warning that quietly DELETES an edge is more dangerous than no
// signal at all, because it reads like a pass.
//
// The rule this file now follows, and the same one the Qwen render chain follows:
// the order of statements is a dependency nobody wrote down, so write it down
// where a reader — human or parser — cannot miss it.
const PASS_TAIL =
  '\n\n' +
  'Report findings as a list. For each: what you did, what you saw, and whose ' +
  'decision it is if it needs one. Do not fix what needs his decision — record it.\n\n' +
  'Re-running the same tests finds nothing. Change the ANGLE.\n\n' +
  'The shape pass is the one that pays: the last real defect was a flag meaning ' +
  '"there is an earlier reading" computed from the wrong half of a comparison. ' +
  'Grep for that SHAPE everywhere — every flag derived from the wrong operand, every ' +
  'default that can silently blank a panel, every value with two possible homes. ' +
  'A fix is not done until its siblings are found.';

const press = await ctx.agent({
  id: 'iterate.press',
  label: 'Press everything and read what appears',
  phase: 'iterate',
  dependsOn: ['verify.four-layers'],
  prompt:
    'Press everything and read what appears. Every control, every tab, every ' +
    'staged row — with a real finger, in a real browser, reading rendered ' +
    'geometry rather than element existence. An untested button is not a ' +
    'button, it is a hope.' + PASS_TAIL
});
if (press.status === 'ok') ctx.checkpoint('iterate.press', press.output);
else ctx.log('pass press failed: ' + (press.error || 'unknown'), { phase: 'iterate' });

const shape = await ctx.agent({
  id: 'iterate.shape',
  label: 'Take the last defect and grep for its SHAPE, not its symptom',
  phase: 'iterate',
  dependsOn: ['verify.four-layers'],
  prompt:
    'Take the LAST real defect this build produced — not the loudest — and grep ' +
    'the whole codebase for its shape. A fix is not done until its siblings are ' +
    'found; that is what this pass is for.' + PASS_TAIL
});
if (shape.status === 'ok') ctx.checkpoint('iterate.shape', shape.output);
else ctx.log('pass shape failed: ' + (shape.error || 'unknown'), { phase: 'iterate' });

const lie = await ctx.agent({
  id: 'iterate.lie',
  label: 'Make it lie, and require each layer to go red',
  phase: 'iterate',
  dependsOn: ['verify.four-layers'],
  prompt:
    'Make the surface lie. For each layer you can reach — contract, behavioural, ' +
    'fault, mutation — construct the input under which it would report something ' +
    'the system did not actually do, and require that layer to refuse it. A ' +
    'dashboard that flatters its own system is worse than one that is blank.' + PASS_TAIL
});
if (lie.status === 'ok') ctx.checkpoint('iterate.lie', lie.output);
else ctx.log('pass lie failed: ' + (lie.error || 'unknown'), { phase: 'iterate' });

const numbers = await ctx.agent({
  id: 'iterate.numbers',
  label: 'Trace every figure to source; hunt missing denominators',
  phase: 'iterate',
  dependsOn: ['verify.four-layers'],
  prompt:
    'Trace every figure on the surface back to its source, and then hunt the ' +
    'denominators that are missing. A count with no base is not a measurement, ' +
    'it is a feeling; "2 retries" means nothing beside "2 of 2" and beside "2 of ' +
    '4000". Also hunt every number that is shown but whose staleness is not.' + PASS_TAIL
});
if (numbers.status === 'ok') ctx.checkpoint('iterate.numbers', numbers.output);
else ctx.log('pass numbers failed: ' + (numbers.error || 'unknown'), { phase: 'iterate' });

const cost = await ctx.agent({
  id: 'iterate.cost',
  label: 'What does the surface consume, including your own habits',
  phase: 'iterate',
  dependsOn: ['verify.four-layers'],
  prompt:
    'Account for everything this surface consumes: processes, sockets, file ' +
    'handles, CPU, memory, log growth — and the operator habits it creates. A ' +
    'dashboard that makes a person check it every ten minutes has spent more ' +
    'than the thing it measures. Say the number, and say who pays it.' + PASS_TAIL
});
if (cost.status === 'ok') ctx.checkpoint('iterate.cost', cost.output);
else ctx.log('pass cost failed: ' + (cost.error || 'unknown'), { phase: 'iterate' });

const handoverPass = await ctx.agent({
  id: 'iterate.handover',
  label: 'Could a stranger use this with no context at all',
  phase: 'iterate',
  dependsOn: ['verify.four-layers'],
  prompt:
    'Assume the reader has never seen this machine, this system, or you. Would ' +
    'they know what this surface is FOR, what each tab answers, which number to ' +
    'trust when two disagree, and what they are forbidden to do? Name every ' +
    'place the answer would be guesswork, and say whose decision fixing it is.' + PASS_TAIL
});
if (handoverPass.status === 'ok') ctx.checkpoint('iterate.handover', handoverPass.output);
else ctx.log('pass handover failed: ' + (handoverPass.error || 'unknown'), { phase: 'iterate' });

// ───────────────────────────────────────────────────────────────────────────
// PHASE 6 · HANDOVER — the deliverable is the method, packaged
// ───────────────────────────────────────────────────────────────────────────

await ctx.phase({ id: 'handover', label: 'Handover — the running list' });

const handover = await ctx.agent({
  id: 'handover.pack',
  label: 'Package it so the next one takes an afternoon, not a month',
  phase: 'handover',
  // All six, named. Declaring only the last one would be a lie about the shape
  // of the dependency: the handover packages what the six passes FOUND, so it
  // has to wait for all six and not merely for the one that happens to be last
  // in the file.
  dependsOn: ['iterate.press', 'iterate.shape', 'iterate.lie', 'iterate.numbers', 'iterate.cost', 'iterate.handover'],
  prompt:
    'The deliverable is not the dashboard. It is the method, packaged.\n\n' +
    'Produce four things:\n\n' +
    '1. THE DASHBOARD — running, self-contained, verified. No CDN, no webfont, no ' +
    '   network. It must work on a disconnected machine, and a test should ASSERT zero ' +
    '   external requests rather than hope for it.\n' +
    '2. THE RESTORE POINT — hashed, sampled, self-describing, provably restorable. ' +
    '   Never nested, never a backup inside its own source. State how to prove it ' +
    '   restores BEFORE you need it.\n' +
    '3. THE PROJECT SKILL — one file a fresh session can open and continue from with ' +
    '   zero context. Real paths, real ports, real hashes, real clause names, the ' +
    '   invariants with their gates, and the state of the build as measured, with the ' +
    '   date it was measured.\n' +
    '4. THE RUNNING LIST — found, not done, each item naming whose decision it is. ' +
    '   Never delete an entry: strike it through and say when.\n\n' +
    'Add to the project skill whatever this build taught that the general method does ' +
    'not already say. A general skill that grew from a specific project is the only ' +
    'artefact that compounds.'
});

if (handover.status === 'ok') {
  ctx.checkpoint('handover.pack', handover.output);
  ctx.log('Handover packaged. Report the running list first — that is what he reads.', { phase: 'handover' });
} else {
  ctx.log('HANDOVER INCOMPLETE: ' + (handover.error || 'unknown'), { phase: 'handover' });
}

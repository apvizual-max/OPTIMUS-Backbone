#!/usr/bin/env node
/**
 * verify-access-handoff.mjs - prove the handoff is actually hand-off-able.
 *
 * A handoff is complete when the next agent can act without asking a question
 * it could have read. This verifier checks that claim mechanically:
 *
 *   V1  the handoff folder exists and holds every required file
 *   V2  every path mentioned inside the handoff documents exists on disk
 *   V3  the priming prompt names the entry command, the goal and the state
 *   V4  the skills index lists every member of the bot's registry
 *   V5  the bot's registry verifies (every member is healthy)
 *
 * V2 is the one that matters: a handoff full of dead paths is worse than no
 * handoff, because the reader trusts it.
 *
 * Exit: 0 = all checks passed, 1 = a check failed, 3 = the handoff is absent.
 */

import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';

const REPO = 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Google_Access';
const HANDOFF = join(REPO, '.handoff');
const BOT = 'C:\\Users\\apviz\\.minimax\\agents\\mavis\\skills\\mavis-google-access-bot';
const REQUIRED = ['README.md', 'HANDOFF-GOOGLE-ACCESS.md', 'PRIMING-PROMPT.md', 'SKILLS-INDEX.md', 'STATE-MEASURED.md', 'MANIFEST.json'];
const defects = [];

function check(id, ok, detail) {
  console.log(`${ok ? 'OK  ' : 'FAIL'} ${id} ${detail}`);
  if (!ok) defects.push(`${id}: ${detail}`);
  return ok;
}

if (!check('V0.handoff-exists', existsSync(HANDOFF), HANDOFF)) {
  console.log('VERDICT=FAIL (no handoff folder)');
  process.exit(3);
}

// V1 - the required files
const present = readdirSync(HANDOFF);
const missing = REQUIRED.filter((f) => !present.includes(f));
check('V1.required-files', missing.length === 0, missing.length ? 'missing: ' + missing.join(', ') : `${REQUIRED.length} files present`);

// V2 - every absolute path mentioned in the handoff must exist
const deadPaths = [];
let pathCount = 0;
for (const f of present) {
  if (!/\.(md|json)$/i.test(f)) continue;
  const text = readFileSync(join(HANDOFF, f), 'utf8');
  const matches = text.match(/[A-Za-z]:\\[^\s"'`|)<>]+/g) || [];
  for (const raw of matches) {
    const p = raw.replace(/[.,;:]+$/, '');
    if (/\.(md|json|mjs|ps1|py|js|cmd)$/i.test(p)) {
      pathCount++;
      if (!existsSync(p)) deadPaths.push(`${f} -> ${p}`);
    }
  }
}
check('V2.no-dead-paths', deadPaths.length === 0, `checked=${pathCount} dead=${deadPaths.length}${deadPaths.length ? ' -> ' + deadPaths.slice(0, 5).join(', ') : ''}`);

// V3 - the priming prompt must carry the three things a zero-context session needs
const primingPath = join(HANDOFF, 'PRIMING-PROMPT.md');
let v3 = false;
let detail3 = 'priming prompt missing';
if (existsSync(primingPath)) {
  const p = readFileSync(primingPath, 'utf8');
  const hasCommand = /ga-doctor\.mjs/.test(p);
  const hasState = /VERDICT=PASS|checks=11/.test(p);
  const hasRefusals = /keep/.test(p) && /sites/.test(p);
  v3 = hasCommand && hasState && hasRefusals;
  detail3 = `command=${hasCommand} state=${hasState} refusals=${hasRefusals}`;
}
check('V3.priming-prompt-complete', v3, detail3);

// V4 - the skills index must cover every member of the registry
const registryPath = join(BOT, 'registry.json');
const indexPath = join(HANDOFF, 'SKILLS-INDEX.md');
let v4 = false;
let detail4 = 'registry or index missing';
if (existsSync(registryPath) && existsSync(indexPath)) {
  const reg = JSON.parse(readFileSync(registryPath, 'utf8'));
  const idx = readFileSync(indexPath, 'utf8');
  const members = (reg.skills || []).filter((s) => s.role !== 'reference');
  const missingFromIndex = members.filter((m) => !idx.includes(m.name));
  v4 = missingFromIndex.length === 0;
  detail4 = `members=${members.length} missing_from_index=${missingFromIndex.length}${missingFromIndex.length ? ' -> ' + missingFromIndex.map((m) => m.name).join(', ') : ''}`;
}
check('V4.index-covers-members', v4, detail4);

// V5 - the bot's own registry must verify
let v5 = false;
let detail5 = 'the bot registry verifier did not run';
try {
  const out = execFileSync(process.execPath, [join(BOT, 'scripts', 'bot-registry.mjs'), 'verify'], {
    encoding: 'utf8',
    windowsHide: true,
  });
  v5 = /VERDICT=PASS/.test(out);
  detail5 = (out.match(/VERDICT=\w+[^\n]*/) || [''])[0].trim();
} catch (e) {
  const out = (e && e.stdout ? e.stdout : '') + (e && e.stderr ? e.stderr : '');
  detail5 = (out.match(/VERDICT=\w+[^\n]*/) || ['registry verify failed'])[0].trim();
}
check('V5.bot-registry-verifies', v5, detail5);

console.log('');
console.log(defects.length === 0 ? 'VERDICT=PASS (5 checks)' : `VERDICT=FAIL (${defects.length} defect(s))`);
for (const x of defects) console.log('  - ' + x);
process.exit(defects.length === 0 ? 0 : 1);

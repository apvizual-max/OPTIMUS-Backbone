#!/usr/bin/env node
/**
 * verify-control-point.mjs - prove the Google Access control point is alive
 * and that its verdict can be read from a script.
 *
 * This member skill is not a plan: it ships a verifier that re-queries the
 * system and can genuinely go red. Measured 2026-10-28: the doctor reported
 * VERDICT=PASS with 11 checks; the same verifier reports FAILED when the
 * doctor is pointed at a container that does not exist.
 *
 * Checks:
 *   V1  the control point script exists and parses (node --check)
 *   V2  the control point runs and prints a SUMMARY + a VERDICT line
 *   V3  the exit code matches the verdict (0 <=> PASS, 2 <=> FAIL)
 *   V4  the scheduled task `Google_Access_Doctor` exists
 *
 * Exit: 0 = all checks passed, 1 = a check failed (the reason is printed),
 *       3 = the verifier itself could not run.
 */

import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';
import { execFileSync } from 'node:child_process';

const REPO = 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Google_Access';
const DOCTOR = join(REPO, 'scripts', 'ga-doctor.mjs');
const defects = [];
const notes = [];

function check(id, ok, detail) {
  console.log(`${ok ? 'OK  ' : 'FAIL'} ${id} ${detail}`);
  if (!ok) defects.push(`${id}: ${detail}`);
  return ok;
}

// V1 - the control point exists and parses
if (!check('V1.script-exists', existsSync(DOCTOR), DOCTOR)) {
  console.log(`VERDICT=FAIL (${defects.length} defect(s))`);
  process.exit(1);
}
try {
  execFileSync(process.execPath, ['--check', DOCTOR], { stdio: 'ignore' });
  check('V1.parses', true, 'node --check exit 0');
} catch (e) {
  check('V1.parses', false, 'node --check failed');
}

// V2 + V3 - run it and read the verdict off the output
let out = '';
let code = 0;
try {
  out = execFileSync(process.execPath, [DOCTOR], { encoding: 'utf8', timeout: 300000, windowsHide: true });
} catch (e) {
  out = (e && e.stdout ? e.stdout : '') + (e && e.stderr ? e.stderr : '');
  code = typeof e.status === 'number' ? e.status : 3;
}

const summary = (out.match(/SUMMARY .*/) || [''])[0].trim();
const verdict = (out.match(/VERDICT=(\w+)/) || [''])[1];
check('V2.runs', Boolean(summary && verdict), `summary="${summary}" verdict=${verdict || 'none'}`);
notes.push(summary);

const expectPass = code === 0 && verdict === 'PASS';
const expectFail = code === 2 && verdict === 'FAIL';
check('V3.exit-matches-verdict', expectPass || expectFail, `exit=${code} verdict=${verdict}`);

const checks = Number((summary.match(/checks=(\d+)/) || [])[1] || 0);
check('V3.check-count', checks >= 11, `checks=${checks} (expected at least 11)`);

// V4 - the scheduled task that runs it on its own
let taskFound = false;
try {
  const ps = execFileSync(
    'powershell.exe',
    [
      '-NoProfile',
      '-Command',
      "if (Get-ScheduledTask -TaskName 'Google_Access_Doctor' -ErrorAction SilentlyContinue) { 'FOUND' }",
    ],
    { encoding: 'utf8', windowsHide: true }
  );
  taskFound = ps.includes('FOUND');
} catch {
  notes.push('V4: the Task Scheduler could not be queried from this verifier');
}
check('V4.scheduled-task', taskFound, 'Google_Access_Doctor registered');

console.log('');
for (const n of notes) console.log('NOTE ' + n);
console.log('');
console.log(defects.length === 0 ? `VERDICT=PASS (${4 - defects.length}/4 checks)` : `VERDICT=FAIL (${defects.length} defect(s))`);
for (const d of defects) console.log('  - ' + d);
process.exit(defects.length === 0 ? 0 : 1);

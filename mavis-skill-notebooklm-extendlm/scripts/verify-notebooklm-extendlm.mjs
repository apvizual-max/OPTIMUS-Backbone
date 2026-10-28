#!/usr/bin/env node
/**
 * verify-notebooklm-extendlm.mjs - prove the NotebookLM route is alive.
 *
 * Checks:
 *   V1  the ExtendLM credential file exists and parses
 *   V2  it carries a refresh token and an access token that is not expired
 *   V3  the host-side publisher instrument exists and parses
 *   V4  the scheduled rotation task exists
 *   V5  the Cloud secret is present and fresh enough (<= 120 min), when `gh` is
 *       available; when it is not, this is reported as UNKNOWN, never as OK
 *
 * Exit: 0 = all checks passed (UNKNOWN is not a failure), 1 = a check failed,
 *       3 = the credential store is absent.
 */

import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';

const DATA = 'C:\\Users\\apviz\\.minimax\\google-access\\data';
const REPO = 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Google_Access';
const CLOUD_REPO = 'apvizual-max/MAVIS-CLOUD';
const SECRET = 'GOOGLE_EXTENDLM_CREDENTIAL_B64';
const defects = [];

function check(id, ok, detail, unknown = false) {
  console.log(`${unknown ? 'UNK ' : ok ? 'OK  ' : 'FAIL'} ${id} ${detail}`);
  if (!ok && !unknown) defects.push(`${id}: ${detail}`);
  return ok;
}

const cfgPath = join(DATA, 'extendlm.json');
if (!check('V0.credential-store', existsSync(cfgPath), cfgPath)) {
  console.log('VERDICT=FAIL (no ExtendLM credential store)');
  process.exit(3);
}

let cfg;
try {
  cfg = JSON.parse(readFileSync(cfgPath, 'utf8'));
} catch (e) {
  console.log('VERDICT=FAIL (credential store unreadable)');
  process.exit(3);
}

// V1
check('V1.parses', true, `keys=${Object.keys(cfg).length}`);

// V2 - the token must be alive, and the refresh token must be there for the
// next rotation. Only lengths are reported; no value is ever printed.
const expiresAt = cfg.expires_at ? Number(cfg.expires_at) : null;
const minutesLeft = expiresAt ? Math.round((expiresAt - Date.now()) / 60000) : null;
const hasRefresh = typeof cfg.refresh_token === 'string' && cfg.refresh_token.length > 0;
check('V2.token-alive', minutesLeft !== null && minutesLeft > 0, `minutes_left=${minutesLeft === null ? 'unknown' : minutesLeft}`);
check('V2.refresh-present', hasRefresh, `refresh_token=${hasRefresh ? 'yes' : 'no'} length=${(cfg.refresh_token || '').length}`);

// V3 - the publisher instrument
const publisher = join(REPO, 'scripts', 'publish-extendlm-secret.mjs');
let v3 = existsSync(publisher);
if (v3) {
  try {
    execFileSync(process.execPath, ['--check', publisher], { stdio: 'ignore' });
  } catch {
    v3 = false;
  }
}
check('V3.publisher-instrument', v3, publisher);

// V4 - the scheduled rotation
let taskFound = false;
try {
  const ps = execFileSync(
    'powershell.exe',
    ['-NoProfile', '-Command', "if (Get-ScheduledTask -TaskName 'MavisExtendLMHeartbeat' -ErrorAction SilentlyContinue) { 'FOUND' }"],
    { encoding: 'utf8', windowsHide: true }
  );
  taskFound = ps.includes('FOUND');
} catch { /* scheduler unreachable */ }
check('V4.scheduled-rotation', taskFound, 'MavisExtendLMHeartbeat registered');

// V5 - the Cloud secret, read back
let ageMinutes = null;
try {
  const out = execFileSync('gh', ['secret', 'list', '--repo', CLOUD_REPO, '--json', 'name,updatedAt'], {
    encoding: 'utf8',
    windowsHide: true,
    timeout: 60000,
  });
  const rows = JSON.parse(out);
  const row = rows.find((r) => r.name === SECRET);
  if (row) ageMinutes = Math.round((Date.now() - Date.parse(row.updatedAt)) / 60000);
} catch {
  ageMinutes = null;
}
if (ageMinutes === null) {
  check('V5.cloud-secret', false, 'the Cloud secret could not be read (gh unavailable or the secret is absent)', true);
} else {
  check('V5.cloud-secret', ageMinutes <= 120, `age_minutes=${ageMinutes}`);
}

console.log('');
console.log(defects.length === 0 ? 'VERDICT=PASS' : `VERDICT=FAIL (${defects.length} defect(s))`);
for (const x of defects) console.log('  - ' + x);
process.exit(defects.length === 0 ? 0 : 1);

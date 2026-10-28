#!/usr/bin/env node
/**
 * verify-keep-sites.mjs - prove that Keep and Sites are refused BY DESIGN,
 * and that their scope names have not been re-introduced.
 *
 * The trap this guards: both scope names are INVALID, and an invalid scope
 * invalidates the ENTIRE consent request. While they were in FULL_SCOPES, the
 * other valid scopes could not be granted either. So this verifier checks two
 * things that must both hold:
 *
 *   V1  the container source does NOT request the keep or sites scopes
 *   V2  the two tools still exist, so they report the refusal instead of
 *       disappearing silently
 *   V3  the control point still EXPECTS exactly these two refusals
 *   V4  the live probe currently reports them as REFUSED (not ERROR, not OK)
 *
 * Exit: 0 = all checks passed, 1 = a check failed.
 */

import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';

const REPO = 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Google_Access';
const SERVER = join(REPO, 'container', 'server.mjs');
const DOCTOR = join(REPO, 'scripts', 'ga-doctor.mjs');
const PROBE = 'C:\\Users\\apviz\\.minimax\\google-access\\probe-services.mjs';
const defects = [];

function check(id, ok, detail) {
  console.log(`${ok ? 'OK  ' : 'FAIL'} ${id} ${detail}`);
  if (!ok) defects.push(`${id}: ${detail}`);
  return ok;
}

// V1 - the invalid scopes must not be back in the consent request
let server = '';
if (existsSync(SERVER)) server = readFileSync(SERVER, 'utf8');
const scopesBlock = (server.match(/FULL_SCOPES[\s\S]{0,4000}/) || [''])[0];
const keepScope = /auth\/keep\b/.test(scopesBlock);
const sitesScope = /auth\/sites\b/.test(scopesBlock);
check('V1.keep-scope-absent', !keepScope, keepScope ? 'auth/keep IS in FULL_SCOPES - it invalidates the whole consent request' : 'auth/keep not requested');
check('V1.sites-scope-absent', !sitesScope, sitesScope ? 'auth/sites IS in FULL_SCOPES - it invalidates the whole consent request' : 'auth/sites not requested');

// V2 - the tools still exist, so the refusal is reported
const hasKeepTool = /gkeep_list/.test(server);
const hasSitesTool = /gsites_list/.test(server);
check('V2.tools-present', hasKeepTool && hasSitesTool, `gkeep_list=${hasKeepTool} gsites_list=${hasSitesTool}`);

// V3 - the control point expects exactly these two refusals
let doctor = '';
if (existsSync(DOCTOR)) doctor = readFileSync(DOCTOR, 'utf8');
const expected = (doctor.match(/EXPECTED_REFUSED\s*=\s*\[([^\]]*)\]/) || ['', ''])[1];
const names = expected.split(',').map((s) => s.trim().replace(/["']/g, '')).filter(Boolean);
const hasKeep = names.includes('keep');
const hasSites = names.includes('sites');
check('V3.doctor-expects-both', hasKeep && hasSites, `EXPECTED_REFUSED=[${names.join(',')}]`);

// V4 - the live probe's current answer for the two
if (existsSync(PROBE)) {
  let out = '';
  try {
    out = execFileSync(process.execPath, [PROBE], { encoding: 'utf8', timeout: 300000, windowsHide: true });
  } catch (e) {
    out = (e && e.stdout ? e.stdout : '') + (e && e.stderr ? e.stderr : '');
  }
  for (const svc of ['keep', 'sites']) {
    const line = (out.split(/\r?\n/).find((l) => l.startsWith('SERVICE=' + svc)) || '');
    const status = (line.match(/STATUS=(\w+)/) || [])[1] || 'absent';
    check('V4.probe-' + svc, status === 'REFUSED', `status=${status}${line ? ' detail=' + ((line.match(/DETAIL=(.*)$/) || [])[1] || '') : ''}`);
  }
} else {
  check('V4.probe', false, 'the live probe script is missing: ' + PROBE);
}

console.log('');
console.log(defects.length === 0 ? 'VERDICT=PASS' : `VERDICT=FAIL (${defects.length} defect(s))`);
for (const x of defects) console.log('  - ' + x);
process.exit(defects.length === 0 ? 0 : 1);

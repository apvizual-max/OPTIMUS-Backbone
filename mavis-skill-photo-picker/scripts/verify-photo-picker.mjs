#!/usr/bin/env node
/**
 * verify-photo-picker.mjs - prove the Photo Picker route is in a sane state.
 *
 * Checks:
 *   V1  the watcher and the downloader exist and parse
 *   V2  the picker session file is valid and in a KNOWN state
 *        (no session id / consumed / active) - never a half-written file
 *   V3  the picked-media summary, when present, is valid JSON with a count
 *   V4  the captured media on disk are real JPEGs (magic bytes), not error
 *       pages wearing a .jpg name
 *   V5  the scheduled capture task exists
 *
 * Exit: 0 = all checks passed, 1 = a check failed.
 */

import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';

const DATA = 'C:\\Users\\apviz\\.minimax\\google-access\\data';
const REPO = 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Google_Access';
const PICKED = join(REPO, 'state', 'picked');
const defects = [];

function check(id, ok, detail) {
  console.log(`${ok ? 'OK  ' : 'FAIL'} ${id} ${detail}`);
  if (!ok) defects.push(`${id}: ${detail}`);
  return ok;
}

// V1
const watcher = join(REPO, 'scripts', 'picker-watch.mjs');
const downloader = join(REPO, 'scripts', 'picker-download.mjs');
let v1 = existsSync(watcher) && existsSync(downloader);
if (v1) {
  for (const f of [watcher, downloader]) {
    try {
      execFileSync(process.execPath, ['--check', f], { stdio: 'ignore' });
    } catch {
      v1 = false;
    }
  }
}
check('V1.instruments', v1, `${watcher} | ${downloader}`);

// V2 - the session state
const sessionFile = join(DATA, 'picker-session.json');
let state = 'absent';
if (existsSync(sessionFile)) {
  try {
    const s = JSON.parse(readFileSync(sessionFile, 'utf8'));
    if (!s.session_id) state = 'consumed' + (s.consumed_at ? ' at ' + s.consumed_at : '');
    else state = 'active id=' + s.session_id;
  } catch {
    state = 'unreadable';
  }
}
check('V2.session-state-known', state !== 'unreadable', `state=${state}`);

// V3 - the picked summary
const pickedFile = join(DATA, 'picked-media.json');
let v3 = true;
let detail3 = 'no capture recorded yet';
if (existsSync(pickedFile)) {
  try {
    const p = JSON.parse(readFileSync(pickedFile, 'utf8'));
    const n = Number(p.count !== undefined ? p.count : (p.items || []).length);
    v3 = Number.isFinite(n);
    detail3 = `count=${n} session=${p.session_id || '?'}`;
  } catch {
    v3 = false;
    detail3 = 'picked-media.json is not valid JSON';
  }
}
check('V3.picked-summary', v3, detail3);

// V4 - the captured files are real JPEGs
let files = [];
if (existsSync(PICKED)) {
  for (const day of readdirSync(PICKED)) {
    const dir = join(PICKED, day);
    try {
      if (!statSync(dir).isDirectory()) continue;
      for (const f of readdirSync(dir)) {
        if (/\.jpe?g$/i.test(f)) files.push(join(dir, f));
      }
    } catch { /* unreadable day folder */ }
  }
}
const bad = [];
for (const f of files) {
  const b = readFileSync(f).subarray(0, 3);
  if (!(b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff)) bad.push(f);
}
check('V4.captured-are-jpegs', bad.length === 0, `files=${files.length} not_jpeg=${bad.length}${bad.length ? ' -> ' + bad.join(', ') : ''}`);

// V5 - the scheduled capture
let taskFound = false;
try {
  const ps = execFileSync(
    'powershell.exe',
    ['-NoProfile', '-Command', "if (Get-ScheduledTask -TaskName 'MavisPickerHeartbeat' -ErrorAction SilentlyContinue) { 'FOUND' }"],
    { encoding: 'utf8', windowsHide: true }
  );
  taskFound = ps.includes('FOUND');
} catch { /* scheduler not reachable from here */ }
check('V5.scheduled-task', taskFound, 'MavisPickerHeartbeat registered');

console.log('');
console.log(defects.length === 0 ? 'VERDICT=PASS (5 checks)' : `VERDICT=FAIL (${defects.length} defect(s))`);
for (const x of defects) console.log('  - ' + x);
process.exit(defects.length === 0 ? 0 : 1);

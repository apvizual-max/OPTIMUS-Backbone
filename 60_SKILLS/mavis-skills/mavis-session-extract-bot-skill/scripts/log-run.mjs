#!/usr/bin/env node
/**
 * log-run.mjs — append a run record to a member skill's run log.
 *
 * The bot's promise: a skill that is used gets updated. Not "maybe later" —
 * after every extraction, the skill that did the work carries the evidence:
 * what was extracted, what was measured, and (when it failed) the error
 * verbatim. Successes are captured with their numbers, because a success
 * without its numbers is a story, not evidence.
 *
 * The log is APPEND-ONLY. A corrected entry is a new entry that references the
 * old one; nothing above is ever rewritten.
 *
 * Usage:
 *   node log-run.mjs --skill <skillName> --status success|error \
 *        --task "<what was attempted>" --outcome "<measured result>" \
 *        [--error "<verbatim error>"] [--source <sourceId>] [--session <id>] \
 *        [--out <path to a .md log>] [--dry-run]
 *
 * Exit: 0 = appended (or dry-run ok) · 1 = skill/log not found, nothing written
 */

import { existsSync, readFileSync, writeFileSync, appendFileSync, mkdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, resolve, dirname } from 'node:path';

const BOT = 'mavis-session-extract-bot-skill';
const SKILLS_ROOT = join(homedir(), '.minimax', 'agents', 'mavis', 'skills');

function parseArgs(argv) {
  const a = {};
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k.startsWith('--')) a[k.slice(2)] = argv[++i];
  }
  return a;
}

function stamp(d = new Date()) {
  const p = (n) => String(n).padStart(2, '0');
  return (
    `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ` +
    `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
  );
}

const args = parseArgs(process.argv);
if (!args.skill) {
  console.error('ERROR: --skill is required');
  process.exit(2);
}
if (!args.status) {
  console.error('ERROR: --status is required (success|error)');
  process.exit(2);
}
if (!['success', 'error'].includes(args.status)) {
  console.error(`ERROR: --status must be success or error (got "${args.status}")`);
  process.exit(2);
}

const dir = join(SKILLS_ROOT, args.skill);
if (!existsSync(dir)) {
  console.error(`ERROR: skill folder not found: ${dir}`);
  console.error(`       Nothing was written.`);
  process.exit(1);
}

const logPath = args.out ? resolve(args.out) : join(dir, 'runs.md');

const lines = [];
lines.push(`## ${stamp()} — ${args.status} — ${args.task}`);
if (args.source) lines.push(`- source: ${args.source}`);
if (args.session) lines.push(`- session: ${args.session}`);
if (args.outcome) lines.push(`- outcome: ${args.outcome}`);
if (args.error) lines.push(`- error: ${args.error}`);
lines.push(`- logged-by: ${BOT}`);
lines.push('');

const entry = lines.join('\n') + '\n';

if (args['dry-run']) {
  console.log('DRY RUN — would append to ' + logPath + ':');
  console.log(entry);
  process.exit(0);
}

// Create the log with a header the first time. The parent directory is created too:
// a custom --out path pointing into a not-yet-existing folder must not fail the write.
mkdirSync(dirname(logPath), { recursive: true });
if (!existsSync(logPath)) {
  writeFileSync(
    logPath,
    `# Run log — ${args.skill}\n\n` +
      `Append-only. Each entry is one use of this skill: what was attempted, what was\n` +
      `measured, and (when it failed) the error verbatim. A corrected entry is a NEW\n` +
      `entry that references the old one — nothing above is ever rewritten.\n\n` +
      `Written by \`${BOT}\` → \`log-run.mjs\`.\n\n`,
    'utf8'
  );
}

appendFileSync(logPath, entry, 'utf8');

// Read it back and prove the entry landed.
const after = readFileSync(logPath, 'utf8');
const landed = after.includes(entry.trimEnd().split('\n')[0]);

console.log(`APPENDED  ${logPath}`);
console.log(`          ${entry.trimEnd().split('\n')[0]}`);
console.log(`          bytes now: ${Buffer.byteLength(after, 'utf8')}  readback=${landed ? 'OK' : 'FAILED'}`);
if (!landed) {
  console.error('ERROR: entry not found in the file after append — the write did not land.');
  process.exit(1);
}

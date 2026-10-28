#!/usr/bin/env node
/**
 * log-run.mjs - append a run record to a skill's run log.
 *
 * The update loop is the bot's working method, not an aspiration: after EVERY
 * action - success or failure - the member skill that did the work is updated.
 *
 *   success -> the run log gains the measured numbers (counts, bytes, exit code)
 *   error   -> the run log gains the error, VERBATIM
 *   lesson  -> the member's SKILL.md is edited in place (this script does not
 *              touch SKILL.md: a lesson is a claim, and only the agent that
 *              learned it can phrase it honestly)
 *
 * The log is APPEND-ONLY. A correction is a NEW entry that references the old
 * one - never an edit of an old line. Every write is READ BACK before the
 * script reports success: an append that was not read back is not an append.
 *
 * RESOLUTION (hardened 2026-10-28). The name is looked up in the bot's own
 * registry FIRST (../registry.json, relative to this script):
 *   - registered + registry "path" set -> that path is the folder
 *   - registered + registry "path" empty -> <skills-root>/<name>
 *   - NOT registered but a folder of that name exists -> that folder, and the
 *     script says so on stderr
 *   - nothing resolves -> exit 2 and the error LISTS what is available: the
 *     registered member names and the folder names actually on disk
 *
 * WHY (measured, not reproduced): in one batch of 8 sequential calls, 7 logged
 * and exactly one - mavis-skill-google-access-control-point - died with
 * "no skill folder at <dir>" although the folder was there (Get-Item: plain
 * Directory, no LinkType; Get-ChildItem: 39 chars, no trailing space;
 * Test-Path: True; fs.existsSync: True; fs.statSync: dir=true) and the very
 * next identical call logged fine. A single negative probe is therefore never
 * believed on its own: the folder is probed again, and the registry and the
 * directory listing get a vote.
 *
 * The registry is a SOFT dependency: if it is missing or unreadable the logger
 * falls back to the plain folder path and says so. A logger that dies because
 * a sibling file is missing is worse than the bug it fixes.
 *
 * The run log of a skill is <folder>/runs.md. The hub bot keeps its own log at
 * <folder>/logs/bot-runs.md, which is used when <folder>/runs.md is absent.
 *
 * Zero dependencies. Node >= 22.
 *
 * Usage:
 *   node log-run.mjs --skill <skillName> --status success|error \
 *        --task "<what was done>" --outcome "<measured result>" \
 *        [--error "<verbatim error>"] [--source <sourceId>] \
 *        [--skills-root <dir>] [--registry <file>]
 *
 * Exit codes:
 *   0  the run was logged and read back
 *   1  the entry was written but could not be read back
 *   2  the skill could not be resolved (nothing was written)
 *
 * Note: --source is accepted for call-site compatibility; the runs.md table has
 * no source column, so the value is not written into the log.
 */

import {
  appendFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const DEFAULT_SKILLS_ROOT = join(homedir(), '.minimax', 'agents', 'mavis', 'skills');
const DEFAULT_REGISTRY = join(SCRIPT_DIR, '..', 'registry.json');

// A negative probe has been observed to be wrong about a folder that exists.
const PROBE_ATTEMPTS = 3;
const PROBE_DELAY_MS = 60;

const FS_IO = {
  appendFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
};

function sleepSync(ms) {
  const sab = new SharedArrayBuffer(4);
  Atomics.wait(new Int32Array(sab), 0, 0, ms);
}

function isDirectory(io, p) {
  try {
    return io.statSync(p).isDirectory();
  } catch {
    return false;
  }
}

/** Probe a folder. One negative is a claim, three are a measurement. */
function directoryExists(io, p) {
  for (let i = 0; i < PROBE_ATTEMPTS; i++) {
    if (isDirectory(io, p)) return true;
    if (i < PROBE_ATTEMPTS - 1) sleepSync(PROBE_DELAY_MS);
  }
  return false;
}

function listFolderNames(io, root) {
  try {
    return io
      .readdirSync(root, { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => e.name)
      .sort();
  } catch {
    return [];
  }
}

/** The registry is read, never required. */
function loadRegistry(io, path) {
  try {
    if (!io.existsSync(path)) {
      return { ok: false, reg: null, reason: `no registry file at ${path}` };
    }
    const reg = JSON.parse(io.readFileSync(path, 'utf8'));
    if (!reg || !Array.isArray(reg.skills)) {
      return { ok: false, reg: null, reason: `registry at ${path} has no skills array` };
    }
    return { ok: true, reg, reason: '' };
  } catch (e) {
    const why = e && e.code ? e.code : 'parse error';
    return { ok: false, reg: null, reason: `registry at ${path} is unreadable (${why})` };
  }
}

/**
 * Resolve a skill name to a folder.
 * Returns { ok, dir, via, notes, folderNames, entry, registryOk, registry, registryReason }.
 */
export function resolveSkill(skill, skillsRoot, registryPath, io = FS_IO) {
  const notes = [];
  const registry = loadRegistry(io, registryPath);
  if (!registry.ok) {
    notes.push(`${registry.reason} - falling back to the plain folder path`);
  }

  const folderNames = listFolderNames(io, skillsRoot);
  const entry = registry.ok
    ? registry.reg.skills.find((s) => s && s.name === skill) || null
    : null;
  const plainDir = join(skillsRoot, skill);

  const done = (dir, via, extra = {}) => ({
    ok: true,
    dir,
    via,
    notes,
    folderNames,
    entry,
    registryOk: registry.ok,
    registry: registry.reg,
    registryReason: registry.reason,
    ...extra,
  });

  if (entry) {
    const registeredDir = entry.path ? resolve(entry.path) : plainDir;

    if (directoryExists(io, registeredDir)) {
      return done(registeredDir, entry.path ? 'registry.path' : 'registry.name', { registered: true });
    }
    if (registeredDir !== plainDir && directoryExists(io, plainDir)) {
      notes.push(`registry path ${registeredDir} is not a folder - used ${plainDir} instead`);
      return done(plainDir, 'registry.name', { registered: true });
    }
    if (folderNames.includes(skill)) {
      notes.push(`the direct probe of ${registeredDir} failed but the folder listing sees ${skill}`);
      return done(registeredDir, 'registry.listing', { registered: true });
    }
    return {
      ok: false,
      dir: registeredDir,
      via: 'registry',
      notes,
      folderNames,
      entry,
      registryOk: registry.ok,
      registry: registry.reg,
      registryReason: registry.reason,
      registered: true,
    };
  }

  if (directoryExists(io, plainDir)) {
    notes.push(`"${skill}" is not in the registry - logged to the folder that exists`);
    return done(plainDir, 'folder', { registered: false });
  }
  if (folderNames.includes(skill)) {
    notes.push(`the direct probe of ${plainDir} failed but the folder listing sees ${skill}`);
    return done(plainDir, 'folder.listing', { registered: false });
  }
  return {
    ok: false,
    dir: plainDir,
    via: 'folder',
    notes,
    folderNames,
    entry: null,
    registryOk: registry.ok,
    registry: registry.reg,
    registryReason: registry.reason,
    registered: false,
  };
}

/** The run log of a skill: <folder>/runs.md, or the hub bot's logs/bot-runs.md. */
export function pickLogFile(io, dir) {
  const primary = join(dir, 'runs.md');
  if (io.existsSync(primary)) return primary;
  const botLog = join(dir, 'logs', 'bot-runs.md');
  if (io.existsSync(botLog)) return botLog;
  return primary;
}

function editDistance(a, b) {
  const m = a.length;
  const n = b.length;
  if (!m) return n;
  if (!n) return m;
  let prev = Array.from({ length: n + 1 }, (_, i) => i);
  for (let i = 1; i <= m; i++) {
    const cur = [i];
    for (let j = 1; j <= n; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      cur[j] = Math.min(cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost);
    }
    prev = cur;
  }
  return prev[n];
}

function closestNames(name, candidates) {
  const limit = Math.max(3, Math.floor(name.length / 3));
  return candidates
    .map((c) => ({ c, d: editDistance(name.toLowerCase(), String(c).toLowerCase()) }))
    .filter((x) => x.d <= limit)
    .sort((a, b) => a.d - b.d)
    .slice(0, 5)
    .map((x) => x.c);
}

/** The failure message must let an operator SEE the mismatch, not guess it. */
function failureMessage(skill, res, skillsRoot) {
  const lines = [];
  lines.push(`ERROR: cannot resolve skill "${skill}"`);
  lines.push(`  looked for: ${res.dir}`);
  if (res.registryOk) {
    const members = res.registry.skills
      .filter((s) => s && s.role !== 'reference')
      .map((s) => s.name);
    lines.push(`  registered members (${members.length}): ${members.join(', ')}`);
  } else {
    lines.push(`  registered members: unknown - ${res.registryReason}`);
  }
  lines.push(
    `  folders under ${skillsRoot} (${res.folderNames.length}): ${res.folderNames.join(', ')}`
  );
  const near = closestNames(
    skill,
    res.registryOk
      ? res.registry.skills.map((s) => s && s.name).filter(Boolean)
      : []
  );
  if (near.length) lines.push(`  closest names: ${near.join(', ')}`);
  lines.push('  nothing was written.');
  return lines;
}

const cell = (s) =>
  String(s == null ? '' : s).replace(/\s+/g, ' ').trim().replace(/\|/g, '\\|');

/**
 * Log one run. Returns { code, out, err } - out goes to stdout, err to stderr.
 * io is injectable so the read-back gate can be falsified on a fixture.
 */
export function runLog(opts = {}) {
  const io = opts.io || FS_IO;
  const out = [];
  const err = [];

  const skill = String(opts.skill == null ? '' : opts.skill).trim();
  const status = opts.status || 'success';
  const task = opts.task || '';
  const outcome = opts.outcome || '';
  const errorText = opts.error || '';
  const skillsRoot = opts.skillsRoot || DEFAULT_SKILLS_ROOT;
  const registryPath = opts.registryPath || DEFAULT_REGISTRY;

  if (!skill || !task || !outcome) {
    err.push('ERROR: --skill, --task and --outcome are required');
    return { code: 2, out, err };
  }

  const res = resolveSkill(skill, skillsRoot, registryPath, io);
  for (const n of res.notes) err.push(`NOTE: ${n}`);

  if (!res.ok) {
    for (const l of failureMessage(skill, res, skillsRoot)) err.push(l);
    return { code: 2, out, err };
  }

  const dir = res.dir;
  const runsPath = pickLogFile(io, dir);
  const stamp = new Date().toISOString();

  const header =
    `# Runs \u2014 ${skill}\n` +
    '\n' +
    'Append-only. Every entry is one run of this skill, with its measured numbers.\n' +
    'A correction is a NEW entry that references the old one; no entry is ever\n' +
    'rewritten or removed.\n' +
    '\n' +
    '| when | status | task | outcome |\n' +
    '|---|---|---|---|\n';

  if (!io.existsSync(runsPath)) {
    io.mkdirSync(dirname(runsPath), { recursive: true });
    io.writeFileSync(runsPath, header, 'utf8');
  }

  const line = `| ${stamp} | ${cell(status)} | ${cell(task)} | ${cell(outcome)} |\n`;
  io.appendFileSync(runsPath, line, 'utf8');

  let block = '';
  if (status === 'error' && errorText) {
    block = `\n**Error, verbatim** \u2014 ${stamp}\n\n\`\`\`\n${errorText}\n\`\`\`\n`;
    io.appendFileSync(runsPath, block, 'utf8');
  }

  // Read back: an append that was not read back is not an append.
  const after = io.readFileSync(runsPath, 'utf8');
  if (!after.includes(line.trim())) {
    err.push('ERROR: the run entry could not be read back');
    return { code: 1, out, err };
  }

  out.push(`LOGGED ${skill} [${status}] ${stamp}`);
  out.push(`runs.md: ${runsPath}`);
  out.push(
    `rows now: ${after.split('\n').filter((l) => l.startsWith('| ') && l.includes('|')).length}`
  );
  if (block) out.push('the error was recorded verbatim');
  return { code: 0, out, err };
}

function parseArgs(argv) {
  const a = {};
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (!k.startsWith('--')) continue;
    const next = argv[i + 1];
    a[k.slice(2)] = next !== undefined && !next.startsWith('--') ? argv[++i] : '';
  }
  return a;
}

function isDirectRun() {
  const entry = process.argv[1];
  if (!entry) return false;
  try {
    const self = resolve(fileURLToPath(import.meta.url)).toLowerCase();
    return resolve(entry).toLowerCase() === self;
  } catch {
    return false;
  }
}

if (isDirectRun()) {
  const a = parseArgs(process.argv.slice(2));
  const result = runLog({
    skill: a.skill,
    status: a.status,
    task: a.task,
    outcome: a.outcome,
    error: a.error,
    source: a.source,
    skillsRoot: a['skills-root'] ? resolve(a['skills-root']) : undefined,
    registryPath: a.registry ? resolve(a.registry) : undefined,
  });
  for (const l of result.out) console.log(l);
  for (const l of result.err) console.error(l);
  process.exit(result.code);
}

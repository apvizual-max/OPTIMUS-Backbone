#!/usr/bin/env node
/**
 * bot-registry.mjs — the link registry of the Mavis Session Extract Bot.
 *
 * The bot is a hub: it owns no extraction logic. It owns the LIST of the small,
 * independent, per-source skills that do the work, and the contract they share.
 *
 * This script is the registry made executable:
 *   list    print the dispatch table (human) / --json for machines
 *   verify  prove every linked skill is healthy on disk (exit 1 on any defect)
 *   link    register a new member skill (must exist on disk; refuses otherwise)
 *   show    one member's full record
 *
 * Zero dependencies. Node >= 22.
 *
 * Usage:
 *   node bot-registry.mjs list [--json]
 *   node bot-registry.mjs verify
 *   node bot-registry.mjs show --name <skillName>
 *   node bot-registry.mjs link --name <skillName> --role <functional|meta> \
 *        --source <sourceId> --purpose "<one line>" [--path <dir>] [--status <S>]
 */

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, resolve, basename } from 'node:path';

const BOT = 'mavis-session-extract-bot-skill';
const SKILLS_ROOT = join(homedir(), '.minimax', 'agents', 'mavis', 'skills');
const BOT_DIR = join(SKILLS_ROOT, BOT);
const DEFAULT_REGISTRY = join(BOT_DIR, 'registry.json');
let REGISTRY = DEFAULT_REGISTRY;

function parseArgs(argv) {
  const a = { _: [] };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k.startsWith('--')) a[k.slice(2)] = argv[++i];
    else a._.push(k);
  }
  // --registry lets the verifier be exercised against a fixture, so it can be
  // falsified without breaking the live registry.
  if (a.registry) REGISTRY = resolve(a.registry);
  return a;
}

function fail(msg, code = 2) {
  console.error(`ERROR: ${msg}`);
  process.exit(code);
}

/** Parse the YAML-ish frontmatter of a SKILL.md (name, description, role, kind). */
export function readFrontmatter(path) {
  if (!existsSync(path)) return null;
  const text = readFileSync(path, 'utf8');
  if (!text.startsWith('---')) return null;
  const end = text.indexOf('\n---', 3);
  if (end === -1) return null;
  const block = text.slice(3, end);
  const fm = {};
  for (const line of block.split(/\r?\n/)) {
    const m = /^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$/.exec(line);
    if (m) fm[m[1]] = m[2].replace(/^["']|["']$/g, '').trim();
  }
  return fm;
}

function loadRegistry() {
  if (!existsSync(REGISTRY)) fail(`registry not found at ${REGISTRY}`);
  return JSON.parse(readFileSync(REGISTRY, 'utf8'));
}

function saveRegistry(reg) {
  writeFileSync(REGISTRY, JSON.stringify(reg, null, 2) + '\n', 'utf8');
}

function skillDir(entry) {
  return entry.path ? resolve(entry.path) : join(SKILLS_ROOT, entry.name);
}

/** One member's health. Every check returns a named defect, not a boolean. */
export function inspectSkill(entry) {
  const dir = skillDir(entry);
  const defects = [];
  const skillMd = join(dir, 'SKILL.md');

  if (!existsSync(dir)) {
    defects.push({ kind: 'folder-missing', detail: dir });
    return { entry, dir, defects, fm: null, hasRuns: false, backLinked: false };
  }
  const fm = readFrontmatter(skillMd);
  if (!fm) defects.push({ kind: 'skill-md-unreadable-or-no-frontmatter', detail: skillMd });
  else {
    if (!fm.name) defects.push({ kind: 'frontmatter-name-missing', detail: skillMd });
    else if (fm.name !== entry.name) {
      defects.push({ kind: 'name-folder-mismatch', detail: `frontmatter "${fm.name}" vs folder "${entry.name}"` });
    }
    if (!fm.description) defects.push({ kind: 'frontmatter-description-missing', detail: skillMd });
    if (!fm.role) defects.push({ kind: 'frontmatter-role-missing', detail: skillMd });
    else if (!['functional', 'meta', 'hub'].includes(fm.role)) {
      defects.push({ kind: 'frontmatter-role-invalid', detail: `${fm.role} (expected functional|meta|hub)` });
    }
  }

  const hasRuns = existsSync(join(dir, 'runs.md'));
  if (!hasRuns) defects.push({ kind: 'run-log-missing', detail: join(dir, 'runs.md') });

  let backLinked = false;
  if (existsSync(skillMd)) {
    backLinked = readFileSync(skillMd, 'utf8').includes(BOT);
  }
  if (!backLinked) defects.push({ kind: 'bot-backlink-missing', detail: `${skillMd} does not mention "${BOT}"` });

  if (entry.role === 'functional') {
    const hasScript = existsSync(join(dir, 'extract-transcript.mjs')) || existsSync(join(dir, 'extract.mjs')) ||
      existsSync(join(dir, 'scripts'));
    if (!hasScript) defects.push({ kind: 'functional-skill-has-no-extractor', detail: dir });
  }

  return { entry, dir, defects, fm, hasRuns, backLinked };
}

function cmdList(args) {
  const reg = loadRegistry();
  if (args.json) {
    console.log(JSON.stringify(reg, null, 2));
    return 0;
  }
  console.log(`=== ${reg.bot} — ${reg.skills.length} linked skill(s) ===`);
  console.log(`naming: functional = ${reg.naming.functional}`);
  console.log(`        meta       = ${reg.naming.meta}`);
  console.log('');
  for (const e of reg.skills) {
    const info = inspectSkill(e);
    const health = info.defects.length === 0 ? 'OK' : `DEFECTS=${info.defects.length}`;
    console.log(`- ${e.name}`);
    console.log(`    role=${e.role}  status=${e.status}  health=${health}`);
    console.log(`    source=${e.source}`);
    console.log(`    purpose: ${e.purpose}`);
    console.log(`    path: ${info.dir}`);
    if (info.defects.length) for (const d of info.defects) console.log(`    ! ${d.kind}: ${d.detail}`);
  }
  return 0;
}

function cmdVerify() {
  const reg = loadRegistry();
  let bad = 0;
  console.log(`=== VERIFY ${reg.bot} ===`);
  for (const e of reg.skills) {
    const info = inspectSkill(e);
    if (info.defects.length === 0) {
      console.log(`OK        ${e.name}  (${info.dir})`);
    } else {
      bad++;
      console.log(`DEFECT    ${e.name}`);
      for (const d of info.defects) console.log(`            - ${d.kind}: ${d.detail}`);
    }
  }
  // The registry must not list the same skill twice.
  const names = reg.skills.map((s) => s.name);
  const dupes = names.filter((n, i) => names.indexOf(n) !== i);
  if (dupes.length) {
    bad++;
    console.log(`DEFECT    duplicate entries in registry: ${[...new Set(dupes)].join(', ')}`);
  }
  // Every functional skill must be reachable from the bot's SKILL.md table.
  const botMd = join(BOT_DIR, 'SKILL.md');
  if (!existsSync(botMd)) {
    bad++;
    console.log(`DEFECT    bot SKILL.md missing: ${botMd}`);
  } else {
    const text = readFileSync(botMd, 'utf8');
    for (const e of reg.skills) {
      if (!text.includes(e.name)) {
        bad++;
        console.log(`DEFECT    ${e.name} is registered but not listed in the bot's SKILL.md`);
      }
    }
  }
  console.log('');
  console.log(bad === 0 ? `VERDICT=PASS  (${reg.skills.length} skills checked)` : `VERDICT=FAIL  (${bad} defect(s))`);
  return bad === 0 ? 0 : 1;
}

function cmdShow(args) {
  if (!args.name) fail('--name is required');
  const reg = loadRegistry();
  const e = reg.skills.find((s) => s.name === args.name);
  if (!e) fail(`skill "${args.name}" is not registered`);
  const info = inspectSkill(e);
  console.log(JSON.stringify({ ...e, dir: info.dir, defects: info.defects }, null, 2));
  return info.defects.length ? 1 : 0;
}

function cmdLink(args) {
  for (const k of ['name', 'role', 'source', 'purpose']) {
    if (!args[k]) fail(`--${k} is required`);
  }
  const reg = loadRegistry();
  if (reg.skills.some((s) => s.name === args.name)) {
    fail(`"${args.name}" is already registered — refuse to duplicate`);
  }
  const dir = args.path ? resolve(args.path) : join(SKILLS_ROOT, args.name);
  if (!existsSync(join(dir, 'SKILL.md'))) {
    fail(`no SKILL.md at ${dir} — the skill must exist on disk BEFORE it is linked (a plan is a gap, not a skill)`);
  }
  const entry = {
    name: args.name,
    role: args.role,
    source: args.source,
    purpose: args.purpose,
    status: args.status || 'BLUEPRINT',
    path: basename(dir) === args.name ? '' : dir,
    added_at: new Date().toISOString(),
  };
  reg.skills.push(entry);
  saveRegistry(reg);
  console.log(`LINKED ${entry.name} (${entry.role}, source=${entry.source})`);
  console.log(`registry now holds ${reg.skills.length} skill(s).`);
  console.log(`NEXT (not done for you): add a row for "${entry.name}" to the bot's SKILL.md table,`);
  console.log(`      and add \`role: ${entry.role}\` + \`bot: ${BOT}\` to its frontmatter.`);
  return 0;
}

const args = parseArgs(process.argv);
const cmd = args._[0] || 'list';
let rc = 0;
switch (cmd) {
  case 'list': rc = cmdList(args); break;
  case 'verify': rc = cmdVerify(); break;
  case 'show': rc = cmdShow(args); break;
  case 'link': rc = cmdLink(args); break;
  default:
    console.error(`unknown command "${cmd}". Use: list | verify | show | link`);
    rc = 2;
}
if (rc !== 0) process.exit(rc);

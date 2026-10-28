#!/usr/bin/env node
/**
 * bot-registry.mjs - the link registry of the Mavis Google Access Bot.
 *
 * The bot is a hub: it owns no Google logic. It owns the LIST of the member
 * skills that do the work, the contract they share, and the update loop.
 *
 * This script is the registry made executable:
 *   list    print the dispatch table (human) / --json for machines
 *   verify  prove every linked skill is healthy on disk (exit 1 on any defect)
 *   link    register a new member skill (must exist on disk; refuses otherwise)
 *   show    one member's full record
 *
 * DIFFERENCE FROM THE SIBLING BOT (mavis-session-extract-bot-skill), and why:
 * that bot's members are all EXTRACTORS, so every member must ship an
 * extractor script and a run log. This bot's list also contains REFERENCES:
 * skills that exist on the station and matter to the ecosystem but are not
 * owned here. A reference is held to a weaker, honest contract: the folder and
 * its SKILL.md must exist, and the frontmatter name must not contradict the
 * folder. Demanding a run log from a skill this bot does not own would be a
 * false failure; pretending a reference is a member would be a false claim.
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

const BOT = 'mavis-google-access-bot';
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

/** Parse the YAML-ish frontmatter of a SKILL.md (name, description, role). */
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

/**
 * One member's health. Every check returns a named defect, not a boolean.
 *
 * MEMBERS (functional | meta) are held to the full contract:
 *   - the folder exists
 *   - SKILL.md exists and parses
 *   - frontmatter name == folder name (the verifier fails if they drift)
 *   - frontmatter carries description and a valid role
 *   - the skill back-links to this bot
 *   - runs.md exists (the run log is the evidence)
 *   - a functional member ships something runnable in scripts/
 *
 * REFERENCES are held to the weaker contract they can honestly meet.
 */
export function inspectSkill(entry) {
  const dir = skillDir(entry);
  const defects = [];
  const warnings = [];
  const skillMd = join(dir, 'SKILL.md');

  if (!existsSync(dir)) {
    defects.push({ kind: 'folder-missing', detail: dir });
    return { entry, dir, defects, warnings, fm: null, hasRuns: false, backLinked: false };
  }

  const fm = readFrontmatter(skillMd);
  const isReference = entry.role === 'reference';

  if (!fm) {
    if (isReference) {
      warnings.push({ kind: 'reference-no-frontmatter', detail: skillMd });
    } else {
      defects.push({ kind: 'skill-md-unreadable-or-no-frontmatter', detail: skillMd });
    }
  } else {
    if (!fm.name) {
      if (isReference) warnings.push({ kind: 'reference-no-frontmatter-name', detail: skillMd });
      else defects.push({ kind: 'frontmatter-name-missing', detail: skillMd });
    } else if (fm.name !== entry.name) {
      defects.push({ kind: 'name-folder-mismatch', detail: `frontmatter "${fm.name}" vs folder "${entry.name}"` });
    }
    if (!fm.description) {
      if (isReference) warnings.push({ kind: 'reference-no-description', detail: skillMd });
      else defects.push({ kind: 'frontmatter-description-missing', detail: skillMd });
    }
    if (!isReference) {
      if (!fm.role) defects.push({ kind: 'frontmatter-role-missing', detail: skillMd });
      else if (!['functional', 'meta', 'hub'].includes(fm.role)) {
        defects.push({ kind: 'frontmatter-role-invalid', detail: `${fm.role} (expected functional|meta|hub)` });
      }
    }
  }

  const hasRuns = existsSync(join(dir, 'runs.md'));
  if (!hasRuns && !isReference) {
    defects.push({ kind: 'run-log-missing', detail: join(dir, 'runs.md') });
  }

  let backLinked = false;
  if (existsSync(skillMd)) {
    backLinked = readFileSync(skillMd, 'utf8').includes(BOT);
  }
  if (!backLinked && !isReference) {
    defects.push({ kind: 'bot-backlink-missing', detail: `${skillMd} does not mention "${BOT}"` });
  }

  if (!isReference && entry.role === 'functional') {
    const hasScript = existsSync(join(dir, 'scripts')) ||
      existsSync(join(dir, 'verify.mjs')) ||
      existsSync(join(dir, 'verify-control-point.mjs'));
    if (!hasScript) defects.push({ kind: 'functional-skill-has-no-runner', detail: dir });
  }

  return { entry, dir, defects, warnings, fm, hasRuns, backLinked };
}

function cmdList(args) {
  const reg = loadRegistry();
  if (args.json) {
    console.log(JSON.stringify(reg, null, 2));
    return 0;
  }
  const members = reg.skills.filter((s) => s.role !== 'reference');
  const refs = reg.skills.filter((s) => s.role === 'reference');
  console.log(`=== ${reg.bot} - ${members.length} member(s), ${refs.length} reference(s) ===`);
  console.log(`naming: functional = ${reg.naming.functional}`);
  console.log(`        meta       = ${reg.naming.meta}`);
  console.log(`        reference  = ${reg.naming.reference}`);
  console.log('');
  console.log('--- MEMBERS ---');
  for (const e of members) {
    const info = inspectSkill(e);
    const health = info.defects.length === 0 ? 'OK' : `DEFECTS=${info.defects.length}`;
    console.log(`- ${e.name}`);
    console.log(`    role=${e.role}  status=${e.status}  health=${health}`);
    console.log(`    source=${e.source}`);
    console.log(`    purpose: ${e.purpose}`);
    console.log(`    path: ${info.dir}`);
    if (info.defects.length) for (const d of info.defects) console.log(`    ! ${d.kind}: ${d.detail}`);
  }
  console.log('');
  console.log('--- REFERENCES (read, not owned) ---');
  for (const e of refs) {
    const info = inspectSkill(e);
    const health = info.defects.length === 0 ? 'OK' : `DEFECTS=${info.defects.length}`;
    console.log(`- ${e.name}  [${health}]  ${e.purpose}`);
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
      for (const w of info.warnings) console.log(`            ~ ${w.kind}: ${w.detail}`);
    } else {
      bad++;
      console.log(`DEFECT    ${e.name}`);
      for (const d of info.defects) console.log(`            - ${d.kind}: ${d.detail}`);
    }
  }

  const names = reg.skills.map((s) => s.name);
  const dupes = names.filter((n, i) => names.indexOf(n) !== i);
  if (dupes.length) {
    bad++;
    console.log(`DEFECT    duplicate entries in registry: ${[...new Set(dupes)].join(', ')}`);
  }

  // Every registered skill must be reachable from the bot's SKILL.md table.
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
  console.log(bad === 0
    ? `VERDICT=PASS  (${reg.skills.length} skills checked)`
    : `VERDICT=FAIL  (${bad} defect(s))`);
  return bad === 0 ? 0 : 1;
}

function cmdShow(args) {
  if (!args.name) fail('--name is required');
  const reg = loadRegistry();
  const e = reg.skills.find((s) => s.name === args.name);
  if (!e) fail(`skill "${args.name}" is not registered`);
  const info = inspectSkill(e);
  console.log(JSON.stringify({ ...e, dir: info.dir, defects: info.defects, warnings: info.warnings }, null, 2));
  return info.defects.length ? 1 : 0;
}

function cmdLink(args) {
  for (const k of ['name', 'role', 'source', 'purpose']) {
    if (!args[k]) fail(`--${k} is required`);
  }
  const reg = loadRegistry();
  if (reg.skills.some((s) => s.name === args.name)) {
    fail(`"${args.name}" is already registered - refuse to duplicate`);
  }
  const dir = args.path ? resolve(args.path) : join(SKILLS_ROOT, args.name);
  if (!existsSync(join(dir, 'SKILL.md'))) {
    fail(`no SKILL.md at ${dir} - the skill must exist on disk BEFORE it is linked (a plan is a gap, not a skill)`);
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
  case 'verify': rc = cmdVerify(args); break;
  case 'show': rc = cmdShow(args); break;
  case 'link': rc = cmdLink(args); break;
  default:
    console.error(`unknown command "${cmd}". Use: list | verify | show | link`);
    rc = 2;
}
if (rc !== 0) process.exit(rc);

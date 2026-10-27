#!/usr/bin/env node
/**
 * verify-transcript.mjs — independent coverage check for an extracted transcript.
 *
 * Does NOT trust the extractor's own self-check. It re-queries the runtime store and
 * proves that every message row and every tool call of the session actually survived
 * into the produced transcript.
 *
 * Exit 0 = coverage proven. Exit 1 = a gap exists. Exit 2 = cannot run the check.
 *
 * Usage:
 *   node verify-transcript.mjs --session <sessionId> --out <dir> [--title <name>]
 *                              [--data-dir <path>]
 */

import { existsSync, readFileSync, statSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';
import { DatabaseSync } from 'node:sqlite';

function parseArgs(argv) {
  const a = { session: null, out: null, title: null, dataDir: join(homedir(), '.minimax') };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--session') a.session = argv[++i];
    else if (k === '--out') a.out = argv[++i];
    else if (k === '--title') a.title = argv[++i];
    else if (k === '--data-dir') a.dataDir = argv[++i];
  }
  return a;
}

const args = parseArgs(process.argv);
if (!args.session || !args.out) {
  console.error('ERROR: --session and --out are required.');
  process.exit(2);
}

const outDir = resolve(args.out);
const manifestPath = join(outDir, 'manifest.json');
if (!existsSync(manifestPath)) {
  console.error(`ERROR: no manifest.json in ${outDir}`);
  process.exit(2);
}
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const title = args.title || manifest.title;
const jsonlPath = join(outDir, `${title}.jsonl`);
const mdPath = join(outDir, `${title}.md`);

for (const p of [jsonlPath, mdPath]) {
  if (!existsSync(p)) {
    console.error(`ERROR: missing transcript file: ${p}`);
    process.exit(2);
  }
}

const dbPath = join(args.dataDir, 'v2', 'sqlite', 'runtime-state.sqlite');
if (!existsSync(dbPath)) {
  console.error(`ERROR: runtime db not found: ${dbPath}`);
  process.exit(2);
}
const db = new DatabaseSync(dbPath, { readOnly: true });
const maxId = manifest?.sources?.row_id_max ?? null;
if (maxId == null) {
  console.error('ERROR: manifest has no sources.row_id_max — cannot bound the comparison.');
  db.close();
  process.exit(2);
}

const dbRows = db
  .prepare(
    `SELECT id, role, data_json FROM local_runtime_message_rows
      WHERE session_id = ? AND id <= ? ORDER BY id`
  )
  .all(args.session, maxId);

let dbToolCalls = 0;
const dbToolNames = new Map();
for (const r of dbRows) {
  const m = JSON.parse(r.data_json);
  for (const tc of m.tool_calls ?? []) {
    dbToolCalls++;
    const k = tc.tool_name ?? '<none>';
    dbToolNames.set(k, (dbToolNames.get(k) ?? 0) + 1);
  }
}
db.close();

// ---- read the produced transcript ----
const raw = readFileSync(jsonlPath, 'utf8');
const lines = raw.split('\n').filter((l) => l.trim());
let parsed = [];
let bad = 0;
for (const l of lines) {
  try {
    parsed.push(JSON.parse(l));
  } catch {
    bad++;
  }
}

const ids = new Set(parsed.map((m) => m.id));
let missingRows = 0;
const missingSamples = [];
for (const r of dbRows) {
  if (!ids.has(r.id)) {
    missingRows++;
    if (missingSamples.length < 5) missingSamples.push(r.id);
  }
}
const extraRows = parsed.filter((m) => !dbRows.some((r) => r.id === m.id)).length;

// tool calls present in the transcript
let outToolCalls = 0;
const outToolNames = new Map();
for (const m of parsed) {
  for (const tc of m.tool_calls ?? []) {
    outToolCalls++;
    const k = tc.tool_name ?? '<none>';
    outToolNames.set(k, (outToolNames.get(k) ?? 0) + 1);
  }
}

// markdown sections
const md = readFileSync(mdPath, 'utf8');
const mdSections = (md.match(/^## \[\d{4}\] /gm) || []).length;

// content integrity: every user message's first 120 chars must appear in the markdown
const mdHas = (s) => md.includes(s);
let userTextMissing = 0;
const userSamples = [];
for (const m of parsed.filter((x) => x.role === 'user')) {
  const c = String(m.content ?? '').trim();
  if (!c) continue;
  const probe = c.slice(0, 120);
  if (!mdHas(probe)) {
    userTextMissing++;
    if (userSamples.length < 3) userSamples.push({ seq: m.seq, probe: probe.slice(0, 60) });
  }
}

// ---- verdict ----
const problems = [];
if (bad > 0) problems.push(`${bad} JSONL lines failed to parse`);
if (missingRows > 0) problems.push(`${missingRows} message rows missing from the transcript`);
if (extraRows > 0) problems.push(`${extraRows} transcript rows are not in the store`);
if (outToolCalls !== dbToolCalls) {
  problems.push(`tool call count mismatch: store ${dbToolCalls} vs transcript ${outToolCalls}`);
}
if (mdSections !== parsed.length) {
  problems.push(`markdown sections ${mdSections} != transcript messages ${parsed.length}`);
}
if (userTextMissing > 0) problems.push(`${userTextMissing} user messages not found in the markdown`);
if ((manifest.gaps ?? []).length > 0) {
  problems.push(`manifest declares ${manifest.gaps.length} gap(s): ${JSON.stringify(manifest.gaps)}`);
}
for (const [k, n] of dbToolNames) {
  const m = outToolNames.get(k) ?? 0;
  if (m !== n) problems.push(`tool "${k}" count mismatch: store ${n} vs transcript ${m}`);
}

console.log('=== TRANSCRIPT VERIFICATION ===');
console.log(`session       : ${args.session}`);
console.log(`title         : ${title}`);
console.log(`store rows    : ${dbRows.length} (id <= ${maxId})`);
console.log(`transcript rows: ${parsed.length} (jsonl ${lines.length} lines, ${bad} unparseable)`);
console.log(`tool calls    : store ${dbToolCalls} / transcript ${outToolCalls}`);
console.log(`md sections   : ${mdSections}`);
console.log(`md bytes      : ${statSync(mdPath).size}  jsonl bytes: ${statSync(jsonlPath).size}`);
console.log(`declared gaps : ${(manifest.gaps ?? []).length}`);
if (missingSamples.length) console.log(`missing ids   : ${missingSamples.join(', ')}`);
if (userSamples.length) console.log(`user text not in md: ${JSON.stringify(userSamples)}`);

if (problems.length) {
  console.log('');
  console.log('=== VERDICT: FAIL ===');
  for (const p of problems) console.log('  - ' + p);
  process.exit(1);
}
console.log('');
console.log('=== VERDICT: PASS — every store row and tool call is present in the transcript ===');

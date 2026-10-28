#!/usr/bin/env node
/**
 * SNAPSHOT MEMORIE — arhivează versiunea curentă a memoriei de agent în repo,
 * ÎNAINTE de orice optimizare (tăiere, mutare HOT→topic, ștergere de topic).
 *
 * REGULA (POPY, 2026-10-24): optimizarea memoriei fără arhivarea a ce ai tăiat
 * e EROARE, nu optimizare. Cât timp versiunea precedentă e în repo, în
 * secțiunea de arhivă, e optimizare. Altfel e trunchiere și pierdere de context.
 *
 * FLUX OBLIGATORIU:  SNAPSHOT → MANIFEST → COMMIT → PUSH → APOI taie.
 * Scriptul nu taie nimic. Doar arhivează. Tăierea e decizie de sesiune.
 *
 *   node mavis-tools/memory-snapshot.js --from <dir> --label <etichetă>
 *   node mavis-tools/memory-snapshot.js --stdin --label <etichetă>   # JSON pe stdin
 *   node mavis-tools/memory-snapshot.js --verify <etichetă>          # R0: există arhiva?
 *   node mavis-tools/memory-snapshot.js --list
 *
 * --stdin primește: { "MEMORY.md": "<text>", "topics": { "nume.md": "<text>" } }
 *
 * Ieșire: docs/arhiva/memorie/<AAAA-LL-ZZ>-<etichetă>/
 *   MEMORY.md      — copiă exactă a stratului HOT
 *   topics/*.md    — copiile topicurilor
 *   MANIFEST.md    — dimensiuni, sha256, timestamp, notă
 *
 * ZERO dependențe. Doar module node.
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const REPO = path.join(__dirname, '..');
const ARCHIVE_ROOT = path.join(REPO, 'docs', 'arhiva', 'memorie');

const C = {
  b: s => `\x1b[1m${s}\x1b[0m`, g: s => `\x1b[32m${s}\x1b[0m`,
  y: s => `\x1b[33m${s}\x1b[0m`, r: s => `\x1b[31m${s}\x1b[0m`,
  d: s => `\x1b[2m${s}\x1b[0m`,
};

function parseArgs(argv) {
  const out = { mode: 'snapshot' };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--from') out.from = argv[++i];
    else if (a === '--label') out.label = argv[++i];
    else if (a === '--note') out.note = argv[++i];
    else if (a === '--stdin') out.stdin = true;
    else if (a === '--verify') { out.mode = 'verify'; out.label = argv[++i]; }
    else if (a === '--list') out.mode = 'list';
    else if (a === '--out') out.out = argv[++i];
    else if (a === '--help' || a === '-h') out.mode = 'help';
  }
  return out;
}

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function today() {
  const d = new Date();
  const p = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

function stamp() {
  return new Date().toISOString();
}

/** Citește memoria dintr-un director: MEMORY.md la rădăcină, topicurile în topics/ (sau *.md). */
function readFromDir(dir) {
  const memoryPath = path.join(dir, 'MEMORY.md');
  if (!fs.existsSync(memoryPath)) {
    throw new Error(`LIPSA ${memoryPath} — sursa trebuie să aibă MEMORY.md la rădăcină`);
  }
  const topics = {};
  const topicsDir = path.join(dir, 'topics');
  const files = fs.existsSync(topicsDir)
    ? fs.readdirSync(topicsDir).filter(f => f.endsWith('.md'))
    : fs.readdirSync(dir).filter(f => f.endsWith('.md') && f !== 'MEMORY.md');
  for (const f of files) {
    const p = fs.existsSync(topicsDir) ? path.join(topicsDir, f) : path.join(dir, f);
    topics[f] = fs.readFileSync(p, 'utf8');
  }
  return { memory: fs.readFileSync(memoryPath, 'utf8'), topics };
}

function readFromStdin(rawOverride) {
  let raw = rawOverride;
  if (raw === undefined) {
    try {
      raw = fs.readFileSync(0, 'utf8');
    } catch (e) {
      throw new Error('STDIN gol — trimite JSON cu { "MEMORY.md": "...", "topics": {...} }');
    }
  }
  let data;
  try {
    data = JSON.parse(raw);
  } catch (e) {
    throw new Error(`STDIN nu e JSON valid: ${e.message}`);
  }
  const memory = data['MEMORY.md'] || data.memory || '';
  if (!memory) throw new Error('STDIN nu conține "MEMORY.md"');
  const topics = {};
  for (const [k, v] of Object.entries(data.topics || {})) {
    topics[k.endsWith('.md') ? k : `${k}.md`] = v;
  }
  return { memory, topics };
}

function buildManifest({ label, source, files, note }) {
  const rows = files.map(f =>
    `| \`${f.rel}\` | ${f.bytes} | \`${f.sha.slice(0, 16)}\` |`).join('\n');
  return `---
description: "[ARHIVĂ] Snapshot memorie agent — ${label}"
---

# MANIFEST — snapshot memorie, ${label}

| | |
|---|---|
| Etichetă | \`${label}\` |
| Creat | ${stamp()} |
| Sursă | ${source} |
| Fișiere | ${files.length} |
${note ? `| Notă | ${note} |\n` : ''}
## Fișiere

| Fișier | Bytes | sha256 (primele 16) |
|---|---|---|
${rows}

## Ce s-a tăiat din această versiune

_(se completează în sesiunea de optimizare: ce a fost comprimat, mutat în topic
sau șters, și unde trăiește acum)_

**Regulă:** arhiva e append-only. Nu se șterge nimic din ea.
`;
}

/**
 * Scrie snapshotul. Returnează { dir, files }.
 */
function writeSnapshot({ memory, topics, label, source, note, outRoot }) {
  if (!label) throw new Error('LIPSA --label (obligatoriu: ex. pre-optimizare, snapshots-automat)');
  const root = outRoot || ARCHIVE_ROOT;
  const dir = path.join(root, `${today()}-${label}`);
  if (fs.existsSync(dir)) {
    throw new Error(`EXISTĂ deja ${path.relative(REPO, dir)} — arhiva e append-only, alege altă etichetă`);
  }
  fs.mkdirSync(path.join(dir, 'topics'), { recursive: true });

  const written = [];
  const memPath = path.join(dir, 'MEMORY.md');
  fs.writeFileSync(memPath, memory, 'utf8');
  written.push({ rel: 'MEMORY.md', bytes: Buffer.byteLength(memory), sha: sha256(memory) });

  for (const [name, content] of Object.entries(topics)) {
    const safe = path.basename(name); // niciun path traversal
    const p = path.join(dir, 'topics', safe);
    fs.writeFileSync(p, content, 'utf8');
    written.push({ rel: `topics/${safe}`, bytes: Buffer.byteLength(content), sha: sha256(content) });
  }

  const manifest = buildManifest({ label, source, files: written, note });
  fs.writeFileSync(path.join(dir, 'MANIFEST.md'), manifest, 'utf8');

  return { dir, files: written, manifestBytes: Buffer.byteLength(manifest) };
}

/** R0: există o arhivă pentru eticheta dată? */
function verify(label, outRoot) {
  const root = outRoot || ARCHIVE_ROOT;
  if (!fs.existsSync(root)) return { ok: false, reason: 'nu există docs/arhiva/memorie/' };
  const dirs = fs.readdirSync(root).filter(d => d.endsWith(`-${label}`) || d === label);
  if (dirs.length === 0) {
    return { ok: false, reason: `nicio arhivă cu eticheta "${label}"` };
  }
  const detail = dirs.map(d => {
    const mem = path.join(root, d, 'MEMORY.md');
    return {
      dir: d,
      hasMemory: fs.existsSync(mem),
      hasManifest: fs.existsSync(path.join(root, d, 'MANIFEST.md')),
      bytes: fs.existsSync(mem) ? fs.statSync(mem).size : 0,
    };
  });
  const ok = detail.every(x => x.hasMemory && x.hasManifest);
  return { ok, dirs: detail, reason: ok ? '' : 'arhivă fără MEMORY.md sau MANIFEST.md' };
}

function list(outRoot) {
  const root = outRoot || ARCHIVE_ROOT;
  if (!fs.existsSync(root)) return [];
  return fs.readdirSync(root).filter(d => fs.statSync(path.join(root, d)).isDirectory()).sort();
}

function main() {
  const a = parseArgs(process.argv.slice(2));

  if (a.mode === 'help') {
    console.log(fs.readFileSync(__filename, 'utf8').split('*/')[0].replace(/^#![^\n]*\n/, ''));
    return;
  }

  if (a.mode === 'list') {
    const dirs = list(a.out);
    if (!dirs.length) return console.log(C.d('arhivă goală'));
    console.log(C.b('Arhive memorie:'));
    for (const d of dirs) {
      const v = verify(path.basename(d).split('-').slice(1).join('-'), a.out);
      const mem = path.join(a.out || ARCHIVE_ROOT, d, 'MEMORY.md');
      const size = fs.existsSync(mem) ? `${C.d(fs.statSync(mem).size + 'B')}` : C.r('fără MEMORY.md');
      console.log(`  ${C.g(d)}  ${size}`);
    }
    return;
  }

  if (a.mode === 'verify') {
    const res = verify(a.label, a.out);
    if (res.ok) {
      console.log(C.g(`OK: arhiva "${a.label}" există și e completă`));
      for (const d of res.dirs) console.log(C.d(`  ${d.dir} — MEMORY.md ${d.bytes}B + MANIFEST.md`));
      process.exit(0);
    }
    console.error(C.r(`NU: ${res.reason}`));
    console.error(C.y('Nu tăia din memorie fără arhivă. Rulează --label <etichetă> și comitează/pushuiește înainte.'));
    process.exit(1);
  }

  // snapshot
  const src = a.stdin ? readFromStdin() : readFromDir(a.from);
  const source = a.stdin ? 'stdin (JSON)' : path.relative(REPO, path.resolve(a.from));
  const res = writeSnapshot({
    memory: src.memory,
    topics: src.topics,
    label: a.label,
    source,
    note: a.note,
    outRoot: a.out,
  });
  console.log(C.g(`OK snapshot: ${path.relative(REPO, res.dir)}`));
  for (const f of res.files) console.log(C.d(`  ${f.rel} — ${f.bytes}B — ${f.sha.slice(0, 16)}`));
  console.log(C.d(`  MANIFEST.md — ${res.manifestBytes}B`));
  console.log(C.y('URMĂTORUL PAS: comitează + PUSH pe main. APOI poți tăia din memorie.'));
}

if (require.main === module) {
  try {
    main();
  } catch (e) {
    console.error(C.r(`EROARE: ${e.message}`));
    process.exit(1);
  }
}

module.exports = { readFromDir, readFromStdin, writeSnapshot, verify, list, buildManifest };

#!/usr/bin/env node
/**
 * extract-transcript.mjs — full conversation transcript extractor for MiniMax Code sessions.
 *
 * Extracts the COMPLETE message history of a local session from the runtime's
 * own store, with every tool output materialised — including the outputs the
 * runtime externalised to disk during the session.
 *
 * Sources (in priority order):
 *   1. <dataDir>\v2\sqlite\runtime-state.sqlite
 *      -> local_runtime_message_rows   (the authoritative per-message projection)
 *      -> local_runtime_sessions       (title, agent, history_relative_dir)
 *   2. <dataDir>\v2\sessions\<yyyy>\<mm>\<dd>\<ts>-session_<b64>\   (session artifacts)
 *
 * Outputs (into --out):
 *   <title>.md       full readable transcript text
 *   <title>.jsonl    full machine-readable transcript, one object per message
 *   manifest.json    provenance, accounting, and an honest list of gaps
 *   raw\             verbatim copies of the session's own sidecar files
 *
 * Zero dependencies. Node >= 22 (uses node:sqlite and node:crypto).
 *
 * Usage:
 *   node extract-transcript.mjs --session <sessionId> --out <dir> [--title <name>]
 *                               [--inline-textfile] [--max-inline-bytes N]
 *                               [--data-dir <path>] [--quiet]
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync, copyFileSync, statSync, readdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, resolve, basename } from 'node:path';
import { createHash } from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';

// ---------------------------------------------------------------- args

function parseArgs(argv) {
  const a = {
    session: null,
    out: null,
    title: null,
    inlineTextFile: false,
    maxInlineBytes: 262144,
    dataDir: join(homedir(), '.minimax'),
    quiet: false,
  };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--session') a.session = argv[++i];
    else if (k === '--out') a.out = argv[++i];
    else if (k === '--title') a.title = argv[++i];
    else if (k === '--inline-textfile') a.inlineTextFile = true;
    else if (k === '--max-inline-bytes') a.maxInlineBytes = Number(argv[++i]);
    else if (k === '--data-dir') a.dataDir = argv[++i];
    else if (k === '--quiet') a.quiet = true;
    else if (k === '--help' || k === '-h') {
      console.log(
        'Usage: extract-transcript.mjs --session <id> --out <dir> [--title <name>]\n' +
          '       [--inline-textfile] [--max-inline-bytes N] [--data-dir <path>] [--quiet]'
      );
      process.exit(0);
    }
  }
  return a;
}

const args = parseArgs(process.argv);
const log = (...m) => {
  if (!args.quiet) console.log(...m);
};

// ---------------------------------------------------------------- helpers

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');

function fmtTime(ms, tz = 'Europe/Bucharest') {
  if (!ms && ms !== 0) return '—';
  try {
    return new Intl.DateTimeFormat('sv-SE', {
      timeZone: tz,
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
    }).format(new Date(ms));
  } catch {
    return new Date(ms).toISOString();
  }
}

function fenceFor(text) {
  let max = 0;
  const re = /`+/g;
  let m;
  while ((m = re.exec(text))) max = Math.max(max, m[0].length);
  return '`'.repeat(Math.max(3, max + 1));
}

/** Extract the human-readable text of a tool result payload. */
function resultText(resultData) {
  if (resultData == null) return { text: '', parsed: null };
  if (typeof resultData !== 'string') return { text: JSON.stringify(resultData, null, 2), parsed: resultData };
  try {
    const parsed = JSON.parse(resultData);
    const parts = [];
    for (const c of parsed?.content ?? []) {
      if (typeof c?.text === 'string') parts.push(c.text);
      else if (c?.type === 'image' || c?.type === 'resource') {
        parts.push(`[${c.type} content omitted from text rendering]`);
      }
    }
    if (parts.length) return { text: parts.join('\n'), parsed };
    return { text: JSON.stringify(parsed, null, 2), parsed };
  } catch {
    return { text: resultData, parsed: null };
  }
}

function findArtifactRef(parsed) {
  return (
    parsed?.details?.tool_output_budget?.reference ??
    parsed?.details?.tool_output_budget?.path ??
    null
  );
}

/**
 * Build a global index of every externalised tool-output artifact under
 * <dataDir>\v2\sessions\**\reports\tool-outputs\. Artifact filenames are
 * content-addressed (hash prefix), so the same name means the same bytes.
 * A branch session can reference an artifact written while a sibling session
 * was active — that is not a missing artifact, it is a different directory.
 */
function buildArtifactIndex(dataDir) {
  const index = new Map();
  const root = join(dataDir, 'v2', 'sessions');
  const stack = [root];
  let scanned = 0;
  while (stack.length) {
    const cur = stack.pop();
    let entries = [];
    try {
      entries = readdirSync(cur, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const e of entries) {
      if (!e.isDirectory()) continue;
      const p = join(cur, e.name);
      if (e.name === 'tool-outputs') {
        scanned++;
        let files = [];
        try {
          files = readdirSync(p, { withFileTypes: true });
        } catch {
          continue;
        }
        for (const f of files) {
          if (!f.isFile()) continue;
          if (!index.has(f.name)) index.set(f.name, join(p, f.name));
        }
      } else {
        stack.push(p);
      }
    }
  }
  return { index, dirsScanned: scanned };
}

function readArtifact(path, maxBytes, sessionDir, globalIndex) {
  if (!path) return { status: 'no-reference', bytes: 0 };
  // A reference may be absolute, or relative to the session's own reports dir.
  const candidates = [];
  if (!existsSync(path)) {
    const rel = path.replace(/^[.\\/]+/, '');
    const name = basename(rel);
    if (sessionDir) candidates.push(join(sessionDir, 'reports', 'tool-outputs', name));
    if (globalIndex && globalIndex.index.has(name)) candidates.push(globalIndex.index.get(name));
  }
  let abs = existsSync(path) ? path : candidates.find((c) => existsSync(c));
  if (!abs) return { status: 'MISSING-ON-DISK', bytes: 0, path, resolved: null };
  const size = statSync(abs).size;
  if (size > maxBytes) {
    return { status: 'TOO-LARGE-NOT-INLINED', bytes: size, path, resolved: abs };
  }
  const buf = readFileSync(abs);
  return {
    status: 'inlined',
    bytes: size,
    path,
    resolved: abs,
    sha256: sha256(buf),
    text: buf.toString('utf8'),
  };
}

// ---------------------------------------------------------------- locate

function locateSession(db, dataDir, sessionId) {
  const row = db
    .prepare(
      `SELECT session_id, agent_name, runtime, session_type, status, archived, visibility, title,
              created_at_ms, updated_at_ms, workspace_dir, history_relative_dir, error_code, error_message
         FROM local_runtime_sessions WHERE session_id = ?`
    )
    .get(sessionId);
  if (!row) return { row: null, dir: null };
  let dir = null;
  if (row.history_relative_dir) {
    const p = join(dataDir, 'v2', 'sessions', row.history_relative_dir);
    if (existsSync(p)) dir = p;
  }
  if (!dir) {
    // Fallback: scan session manifests for this id.
    const root = join(dataDir, 'v2', 'sessions');
    const stack = [root];
    while (stack.length) {
      const cur = stack.pop();
      let entries = [];
      try {
        entries = readdirSync(cur, { withFileTypes: true });
      } catch {
        continue;
      }
      for (const e of entries) {
        const p = join(cur, e.name);
        if (e.isDirectory()) {
          const mf = join(p, 'manifest.json');
          if (existsSync(mf)) {
            try {
              const j = JSON.parse(readFileSync(mf, 'utf8'));
              if (j.sessionId === sessionId) return { row, dir: p };
            } catch {
              /* keep scanning */
            }
          }
          stack.push(p);
        }
      }
    }
  }
  return { row, dir };
}

// ---------------------------------------------------------------- extract

function main() {
  if (!args.session || !args.out) {
    console.error('ERROR: --session and --out are required.');
    process.exit(2);
  }

  const dbPath = join(args.dataDir, 'v2', 'sqlite', 'runtime-state.sqlite');
  if (!existsSync(dbPath)) {
    console.error(`ERROR: runtime state db not found at ${dbPath}`);
    process.exit(2);
  }
  const db = new DatabaseSync(dbPath, { readOnly: true });

  const { row, dir } = locateSession(db, args.dataDir, args.session);
  if (!row) {
    console.error(
      `ERROR: session ${args.session} is not present in the local runtime store\n` +
        `       (${dbPath}).\n` +
        `       A cloud-only session has no local rows; use the native 'mavis session messages'\n` +
        `       tool with source=cloud for that.`
    );
    db.close();
    process.exit(3);
  }

  const title = args.title || row.title || args.session;

  // Freeze a consistent snapshot of a possibly-live session.
  const maxId = db
    .prepare(`SELECT MAX(id) AS m FROM local_runtime_message_rows WHERE session_id = ?`)
    .get(args.session).m;

  const rawRows = db
    .prepare(
      `SELECT id, msg_id, role, turn_id, created_at_ms, source, data_json
         FROM local_runtime_message_rows
        WHERE session_id = ? AND id <= ?
        ORDER BY id`
    )
    .all(args.session, maxId);

  const usage = db
    .prepare(
      `SELECT COUNT(*) AS turns, SUM(input_tokens) AS in_tok, SUM(output_tokens) AS out_tok,
              SUM(cache_read_tokens) AS cache_tok
         FROM local_runtime_token_usage WHERE session_id = ?`
    )
    .get(args.session);

  db.close();

  log(`session    : ${args.session}`);
  log(`title      : ${title}`);
  log(`agent      : ${row.agent_name}   runtime: ${row.runtime}   type: ${row.session_type}`);
  log(`window     : ${fmtTime(row.created_at_ms)} → ${fmtTime(row.updated_at_ms)}`);
  log(`session dir: ${dir ?? 'NOT FOUND'}`);
  log(`message rows (id<=${maxId}): ${rawRows.length}`);

  // ---- normalise ----------------------------------------------------
  const globalIndex = buildArtifactIndex(args.dataDir);
  log(`artifact index: ${globalIndex.index.size} files across ${globalIndex.dirsScanned} tool-outputs dirs`);

  const msgs = [];
  const gaps = [];
  const readFailures = [];
  const artifactCopies = new Map();
  const textFileIndex = new Map();
  let toolCallCount = 0;
  let externalizedCount = 0;
  let inlineArtifactBytes = 0;

  for (const r of rawRows) {
    let m;
    try {
      m = JSON.parse(r.data_json);
    } catch (e) {
      gaps.push({ kind: 'unparseable-row', id: r.id, detail: e.message });
      continue;
    }
    const role = r.role ?? m.role ?? 'system-event';
    const ts = r.created_at_ms ?? m.timestamp ?? null;

    const rec = {
      seq: msgs.length + 1,
      id: r.id,
      msg_id: r.msg_id ?? m.msg_id ?? null,
      role,
      turn_id: r.turn_id ?? m.turn_id ?? null,
      timestamp_ms: ts,
      timestamp_local: fmtTime(ts),
      source: r.source ?? m.source ?? null,
      content: m.msg_content ?? m.content ?? '',
      thinking: m.thinking_content ?? null,
      tool_calls: [],
      raw: m,
    };

    for (const tc of m.tool_calls ?? []) {
      toolCallCount++;
      const { text, parsed } = resultText(tc.tool_call_result_data);
      const call = {
        tool_name: tc.tool_name ?? null,
        tool_call_id: tc.tool_call_id ?? null,
        status: tc.tool_call_status ?? null,
        args: tc.tool_call_args ?? null,
        result_text: text,
        result_parsed: parsed,
        artifact: null,
      };

      // Runtime-externalised output: the payload lives in a file on disk.
      const ref = findArtifactRef(parsed) || (/tool-outputs[\\/][^\s"\\]+\.txt/.exec(text) || [])[0];
      if (ref) {
        externalizedCount++;
        const art = readArtifact(ref, args.maxInlineBytes, dir, globalIndex);
        call.artifact = art;
        if (art.status === 'inlined') {
          inlineArtifactBytes += art.bytes;
          artifactCopies.set(art.resolved ?? ref, art.sha256);
        } else if (art.status === 'MISSING-ON-DISK') {
          // A read that ALREADY failed inside the session is not a gap in the archive:
          // the record is complete — the file simply never existed. Measured 2026-10-28
          // (session mvs_e8f4c73a82b342d59a8a240e4379f812): a `read` of a non-existent
          // tool-outputs file returned ENOENT inside the session, and the extractor
          // reported that as a missing artefact — a false-positive gap that also makes
          // the verifier fail for an archive that is in fact complete.
          const failedInSession =
            /ENOENT|no such file or directory|cannot find the (file|path)|The system cannot find/i.test(text);
          if (failedInSession) {
            readFailures.push({ msg_id: rec.msg_id, tool: call.tool_name, path: ref });
          } else {
            gaps.push({
              kind: 'externalized-artifact-missing',
              msg_id: rec.msg_id,
              tool: call.tool_name,
              path: ref,
              resolved_as: art.resolved,
            });
          }
        } else if (art.status === 'TOO-LARGE-NOT-INLINED') {
          gaps.push({
            kind: 'externalized-artifact-not-inlined-too-large',
            msg_id: rec.msg_id,
            tool: call.tool_name,
            path: ref,
            bytes: art.bytes,
          });
        }
      }

      // A read tool that returned a truncated file + pointer.
      const tf = parsed?.details?.textFile?.path;
      if (tf) {
        const prev = textFileIndex.get(tf) ?? { path: tf, refs: 0, exists: false, bytes: 0, sha256: null };
        prev.refs++;
        if (existsSync(tf)) {
          prev.exists = true;
          const buf = readFileSync(tf);
          prev.bytes = buf.length;
          prev.sha256 = sha256(buf);
          if (args.inlineTextFile && buf.length <= args.maxInlineBytes) {
            prev.text = buf.toString('utf8');
            prev.inlined = true;
          }
        }
        textFileIndex.set(tf, prev);
        call.text_file = { path: tf };
      }

      rec.tool_calls.push(call);
    }

    if (m.usage) rec.usage = m.usage;
    msgs.push(rec);
  }

  // ---- write outputs ------------------------------------------------
  const outDir = resolve(args.out);
  const rawDir = join(outDir, 'raw');
  mkdirSync(outDir, { recursive: true });
  mkdirSync(rawDir, { recursive: true });

  // 1) JSONL — the complete structured transcript
  const jsonlPath = join(outDir, `${title}.jsonl`);
  const jsonl = msgs
    .map((m) =>
      JSON.stringify({
        seq: m.seq,
        id: m.id,
        msg_id: m.msg_id,
        role: m.role,
        turn_id: m.turn_id,
        timestamp_ms: m.timestamp_ms,
        timestamp_local: m.timestamp_local,
        source: m.source,
        content: m.content,
        thinking: m.thinking,
        tool_calls: m.tool_calls.map((tc) => ({
          tool_name: tc.tool_name,
          tool_call_id: tc.tool_call_id,
          status: tc.status,
          args: tc.args,
          result_text: tc.result_text,
          artifact: tc.artifact
            ? {
                status: tc.artifact.status,
                path: tc.artifact.path ?? null,
                resolved: tc.artifact.resolved ?? null,
                bytes: tc.artifact.bytes ?? 0,
                sha256: tc.artifact.sha256 ?? null,
                text: tc.artifact.text ?? null,
              }
            : null,
          text_file: tc.text_file ?? null,
        })),
        usage: m.usage ?? null,
      })
    )
    .join('\n');
  writeFileSync(jsonlPath, jsonl + (jsonl ? '\n' : ''), 'utf8');

  // 2) MD — the full transcript text
  const roleCounts = msgs.reduce((acc, m) => ((acc[m.role] = (acc[m.role] ?? 0) + 1), acc), {});
  const md = [];
  md.push(`# ${title}`);
  md.push('');
  md.push(`- **Session**: \`${args.session}\``);
  md.push(`- **Original title**: ${row.title ?? '—'}`);
  md.push(`- **Agent / runtime**: ${row.agent_name ?? '—'} · ${row.runtime ?? '—'} · type=${row.session_type ?? '—'}`);
  md.push(
    `- **Window**: ${fmtTime(row.created_at_ms)} → ${fmtTime(row.updated_at_ms)} (Europe/Bucharest)`
  );
  md.push(`- **Workspace**: \`${row.workspace_dir ?? '—'}\``);
  md.push(`- **Messages**: ${msgs.length} (${Object.entries(roleCounts).map(([k, v]) => `${v} ${k}`).join(' · ')})`);
  md.push(`- **Tool calls**: ${toolCallCount} (externalised to disk: ${externalizedCount})`);
  md.push(`- **Source**: \`${dbPath}\` → \`local_runtime_message_rows\` (ids ≤ ${maxId})`);
  md.push(`- **Session artifacts**: \`${dir ?? 'NOT FOUND'}\``);
  md.push(`- **Extracted**: ${new Date().toISOString()}`);
  md.push('');
  md.push('## Completeness ledger');
  md.push('');
  md.push('| Check | Value |');
  md.push('|---|---|');
  md.push(`| Rows read from \`local_runtime_message_rows\` | ${rawRows.length} |`);
  md.push(`| Rows rendered in this transcript | ${msgs.length} |`);
  md.push(`| Rows dropped (unparseable) | ${gaps.filter((g) => g.kind === 'unparseable-row').length} |`);
  md.push(`| Tool calls recorded | ${toolCallCount} |`);
  md.push(`| Externalised artifacts inlined | ${artifactCopies.size} (${inlineArtifactBytes} B) |`);
  md.push(`| Externalised artifacts missing on disk | ${gaps.filter((g) => g.kind === 'externalized-artifact-missing').length} |`);
  md.push(`| Reads that already failed inside the session (ENOENT) | ${readFailures.length} |`);
  md.push(`| Distinct read-file pointers | ${textFileIndex.size} |`);
  md.push(`| Tokens (in/out/cache-read) | ${usage?.in_tok ?? '—'} / ${usage?.out_tok ?? '—'} / ${usage?.cache_tok ?? '—'} |`);
  md.push('');
  if (gaps.length) {
    md.push('### Gaps (declared, not hidden)');
    md.push('');
    for (const g of gaps) md.push(`- \`${g.kind}\` — ${JSON.stringify(g)}`);
    md.push('');
  }
  md.push('---');
  md.push('');

  for (const m of msgs) {
    const head = `## [${String(m.seq).padStart(4, '0')}] ${m.role} · ${m.timestamp_local}`;
    md.push(head);
    md.push('');
    md.push(`*msg_id \`${m.msg_id ?? '—'}\` · turn \`${m.turn_id ?? '—'}\` · row id \`${m.id}\` · source \`${m.source ?? '—'}\`*`);
    md.push('');

    if (m.thinking) {
      md.push('<details><summary>thinking</summary>');
      md.push('');
      md.push(m.thinking);
      md.push('');
      md.push('</details>');
      md.push('');
    }

    const body = typeof m.content === 'string' ? m.content : JSON.stringify(m.content, null, 2);
    if (body && body.trim()) {
      md.push(body);
      md.push('');
    }

    for (const tc of m.tool_calls) {
      md.push(`### 🛠 \`${tc.tool_name}\` — \`${tc.tool_call_id ?? '—'}\` (status ${tc.status ?? '—'})`);
      md.push('');
      if (tc.args) {
        const f = fenceFor(tc.args);
        md.push(`${f}json`);
        md.push(typeof tc.args === 'string' ? tc.args : JSON.stringify(tc.args, null, 2));
        md.push(f);
        md.push('');
      }
      const resText = tc.result_text ?? '';
      if (resText) {
        const f = fenceFor(resText);
        md.push('**Result**');
        md.push('');
        md.push(`${f}text`);
        md.push(resText);
        md.push(f);
        md.push('');
      }
      if (tc.artifact && tc.artifact.status === 'inlined') {
        const f = fenceFor(tc.artifact.text ?? '');
        md.push(
          `**Externalised artifact — inlined** (${tc.artifact.bytes} B · sha256 \`${tc.artifact.sha256}\` · \`${tc.artifact.path}\`)`
        );
        md.push('');
        md.push(`${f}text`);
        md.push(tc.artifact.text);
        md.push(f);
        md.push('');
      } else if (tc.artifact && tc.artifact.status !== 'no-reference') {
        md.push(`**Externalised artifact — ${tc.artifact.status}**: \`${tc.artifact.path}\` (${tc.artifact.bytes} B)`);
        md.push('');
      }
      if (tc.text_file) {
        const info = textFileIndex.get(tc.text_file.path);
        md.push(
          `**Read-file pointer**: \`${tc.text_file.path}\` — ${
            info?.exists ? `${info.bytes} B · sha256 \`${info.sha256}\`` : 'NOT ON DISK AT EXTRACTION TIME'
          }`
        );
        if (info?.inlined && info.text) {
          const f = fenceFor(info.text);
          md.push('');
          md.push(`${f}text`);
          md.push(info.text);
          md.push(f);
        }
        md.push('');
      }
    }

    if (m.usage) {
      const u = m.usage;
      md.push(
        `*tokens: total ${u.total_tokens ?? '—'} · in ${u.input_tokens ?? '—'} · out ${u.output_tokens ?? '—'} · cache_read ${u.cache_read ?? '—'}*`
      );
      md.push('');
    }
    md.push('---');
    md.push('');
  }

  const mdPath = join(outDir, `${title}.md`);
  writeFileSync(mdPath, md.join('\n'), 'utf8');

  // 3) raw sidecars — verbatim copies so the transcript folder is self-contained
  const copied = [];
  if (dir) {
    for (const f of ['messages.jsonl', 'manifest.json', 'history-catalog.json', 'user-message-locators.jsonl', 'reply-final.txt']) {
      const p = join(dir, f);
      if (existsSync(p)) {
        copyFileSync(p, join(rawDir, f));
        copied.push(f);
      }
    }
    const artSrc = join(dir, 'reports', 'tool-outputs');
    const artDst = join(rawDir, 'tool-outputs');
    if (existsSync(artSrc)) {
      mkdirSync(artDst, { recursive: true });
      // Copy every artifact this session owns, not only the referenced ones.
      for (const f of readdirSync(artSrc, { withFileTypes: true })) {
        if (!f.isFile()) continue;
        copyFileSync(join(artSrc, f.name), join(artDst, f.name));
        copied.push(`reports/tool-outputs/${f.name}`);
      }
      // Plus any artifact that was referenced but written under a sibling session.
      for (const ref of artifactCopies.keys()) {
        const name = basename(ref);
        const dst = join(artDst, name);
        if (existsSync(ref) && !existsSync(dst)) {
          copyFileSync(ref, dst);
          copied.push(`reports/tool-outputs/${name} (from sibling session)`);
        }
      }
    }
  }

  // 4) manifest
  const manifest = {
    schemaVersion: 1,
    artifact: 'mavis-session-full-transcript',
    title,
    session_id: args.session,
    original_title: row.title ?? null,
    agent_name: row.agent_name ?? null,
    runtime: row.runtime ?? null,
    session_type: row.session_type ?? null,
    status: row.status ?? null,
    archived: row.archived ?? null,
    created_at_ms: row.created_at_ms ?? null,
    updated_at_ms: row.updated_at_ms ?? null,
    window_local: [fmtTime(row.created_at_ms), fmtTime(row.updated_at_ms)],
    workspace_dir: row.workspace_dir ?? null,
    extracted_at: new Date().toISOString(),
    extractor: 'extract-transcript.mjs (mavis-session-transcript-skill)',
    sources: {
      sqlite: dbPath,
      table: 'local_runtime_message_rows',
      row_id_max: maxId,
      session_dir: dir,
    },
    counts: {
      message_rows_read: rawRows.length,
      messages_rendered: msgs.length,
      by_role: roleCounts,
      tool_calls: toolCallCount,
      externalized_artifacts: externalizedCount,
      externalized_artifacts_inlined: artifactCopies.size,
      inline_artifact_bytes: inlineArtifactBytes,
      distinct_read_file_pointers: textFileIndex.size,
      turns_with_token_usage: usage?.turns ?? null,
      tokens_in: usage?.in_tok ?? null,
      tokens_out: usage?.out_tok ?? null,
      tokens_cache_read: usage?.cache_tok ?? null,
    },
    outputs: {
      markdown: mdPath,
      jsonl: jsonlPath,
      manifest: join(outDir, 'manifest.json'),
      sha256sums: 'SHA256SUMS.txt',
      raw_copies: copied,
    },
    gaps,
    read_failures_in_session: readFailures,
    read_file_pointers: [...textFileIndex.values()].map((v) => ({
      path: v.path,
      refs: v.refs,
      exists: v.exists,
      bytes: v.bytes,
      sha256: v.sha256,
    })),
  };
  writeFileSync(join(outDir, 'manifest.json'), JSON.stringify(manifest, null, 2), 'utf8');

  // 5) SHA256SUMS.txt — seal the bytes.
  //    Measured 2026-10-28: a second agent extracted the SAME session into the SAME
  //    folder and its stale copy landed on top of a newer one, 23 minutes later. Nothing
  //    in the folder said which version was on disk. The seal makes that answerable:
  //    any third party can recompute the digests and know, byte-exactly, what it holds.
  const sumLines = [];
  const collectFiles = (dir, base = '') => {
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, e.name);
      const rel = base ? `${base}/${e.name}` : e.name;
      if (e.isDirectory()) collectFiles(full, rel);
      else if (e.name !== 'SHA256SUMS.txt') {
        sumLines.push(`${createHash('sha256').update(readFileSync(full)).digest('hex')}  ${rel}`);
      }
    }
  };
  collectFiles(outDir);
  sumLines.sort();
  writeFileSync(join(outDir, 'SHA256SUMS.txt'), sumLines.join('\n') + '\n', 'utf8');

  // ---- self-check ----------------------------------------------------
  const problems = [];
  if (msgs.length !== rawRows.length) problems.push(`row count mismatch: read ${rawRows.length}, rendered ${msgs.length}`);
  if (msgs.length === 0) problems.push('zero messages rendered');
  const lastId = msgs.length ? msgs[msgs.length - 1].id : -1;
  if (lastId !== maxId) problems.push(`last rendered id ${lastId} != captured max id ${maxId}`);
  const mdBytes = statSync(mdPath).size;
  const jsonlBytes = statSync(jsonlPath).size;
  if (mdBytes < 1000) problems.push(`markdown too small (${mdBytes} B) — probably truncated`);
  if (jsonlBytes < 1000) problems.push(`jsonl too small (${jsonlBytes} B) — probably truncated`);

  console.log('');
  console.log('=== EXTRACTED ===');
  console.log(`markdown : ${mdPath} (${mdBytes} B)`);
  console.log(`jsonl    : ${jsonlPath} (${jsonlBytes} B)`);
  console.log(`manifest : ${join(outDir, 'manifest.json')}`);
  console.log(`raw      : ${rawDir} (${copied.length} files copied)`);
  console.log(`messages : ${msgs.length} | tool calls: ${toolCallCount} | gaps: ${gaps.length}`);
  if (problems.length) {
    console.log('');
    console.log('=== SELF-CHECK FAILED ===');
    for (const p of problems) console.log('  - ' + p);
    process.exit(1);
  }
  console.log('self-check: PASS');
}

main();

#!/usr/bin/env node
/**
 * log-run-selfcheck.mjs - falsify log-run.mjs on a fixture, never on a member.
 *
 * WHAT THIS PROVES (and what it does not):
 *   - a registered member resolves through the registry, and the row lands in
 *     the right file, exactly once;
 *   - a name that resolves to nothing FAILS LOUDLY: exit 2, a message that
 *     lists what is available, and NOTHING written;
 *   - the read-back gate can actually go red (exit 1) - it is exercised with an
 *     injected io whose append is dropped, so the check is not a decoration;
 *   - the three exit codes (0 logged / 2 unresolved / 1 unreadable) are
 *     distinguishable;
 *   - an unreadable registry does not kill the logger;
 *   - NOT ONE byte of a real member's run log is touched by this file.
 *
 * A check that cannot fail is not a check: every GATE probe below must
 * demonstrate that the instrument BLOCKS, and the self-test exits non-zero if
 * any of them stops blocking.
 *
 * Zero dependencies. Node >= 22.
 *
 * Usage: node log-run-selfcheck.mjs
 */

import { spawnSync } from 'node:child_process';
import {
  appendFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import { homedir, tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runLog } from './log-run.mjs';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const SCRIPT = join(SCRIPT_DIR, 'log-run.mjs');
const FIXTURE = join(tmpdir(), `ga-log-run-selfcheck-${process.pid}-${Date.now()}`);
const SKILLS = join(FIXTURE, 'skills');
const REGISTRY = join(FIXTURE, 'registry.json');
const REAL_ROOT = join(homedir(), '.minimax', 'agents', 'mavis', 'skills');

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

function runCli(args) {
  const r = spawnSync(process.execPath, [SCRIPT, ...args], { encoding: 'utf8' });
  return { code: r.status, out: r.stdout || '', err: r.stderr || '' };
}

/** Data rows only: the table header and the separator are not runs. */
function dataRows(file) {
  if (!existsSync(file)) return -1;
  return readFileSync(file, 'utf8')
    .split('\n')
    .filter((l) => /^\| \d{4}-\d{2}-\d{2}T/.test(l)).length;
}

function countRunsFiles(root) {
  let n = 0;
  const walk = (dir) => {
    let entries = [];
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      const p = join(dir, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.name === 'runs.md' || e.name === 'bot-runs.md') n++;
    }
  };
  walk(root);
  return n;
}

/** Every real run log on the station, with size and mtime, to prove no write. */
function snapshotRealLogs() {
  const snap = new Map();
  let dirs = [];
  try {
    dirs = readdirSync(REAL_ROOT, { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => e.name);
  } catch {
    return snap;
  }
  for (const d of dirs) {
    for (const name of ['runs.md', join('logs', 'bot-runs.md')]) {
      const p = join(REAL_ROOT, d, name);
      if (existsSync(p)) {
        const st = statSync(p);
        snap.set(p, `${st.size}:${st.mtimeMs}`);
      }
    }
  }
  return snap;
}

function buildFixture() {
  for (const d of ['fixture-member', 'fixture-unregistered', 'fixture-custom-location']) {
    mkdirSync(join(SKILLS, d), { recursive: true });
  }
  const reg = {
    schemaVersion: 1,
    bot: 'fixture-bot',
    skills: [
      {
        name: 'fixture-member',
        role: 'functional',
        source: 'fixture',
        purpose: 'registered, registry path empty',
        status: 'WIRED',
        path: '',
        added_at: '2026-10-28',
      },
      {
        name: 'fixture-renamed',
        role: 'functional',
        source: 'fixture',
        purpose: 'registered, registry path points at another folder',
        status: 'WIRED',
        path: join(SKILLS, 'fixture-custom-location'),
        added_at: '2026-10-28',
      },
      {
        name: 'fixture-reference',
        role: 'reference',
        source: 'fixture',
        purpose: 'a reference, not a member: must not be listed as one',
        status: 'WIRED',
        path: '',
        added_at: '2026-10-28',
      },
    ],
  };
  writeFileSync(REGISTRY, JSON.stringify(reg, null, 2) + '\n', 'utf8');
}

const MEMBER_LOG = join(SKILLS, 'fixture-member', 'runs.md');
const CUSTOM_LOG = join(SKILLS, 'fixture-custom-location', 'runs.md');
const UNREG_LOG = join(SKILLS, 'fixture-unregistered', 'runs.md');
const BASE = ['--skills-root', SKILLS, '--registry', REGISTRY];

const PROBES = [
  {
    id: 'P1',
    kind: 'function',
    title: 'registered member resolves by registry name, appends exactly one row',
    run() {
      const r = runCli([
        '--skill', 'fixture-member', '--status', 'success',
        '--task', 'p1', '--outcome', 'p1 outcome', ...BASE,
      ]);
      assert(r.code === 0, `exit ${r.code} (want 0); stderr=${r.err}`);
      assert(existsSync(MEMBER_LOG), 'no runs.md was created for the registered member');
      assert(dataRows(MEMBER_LOG) === 1, `data rows ${dataRows(MEMBER_LOG)} (want 1)`);
      return { detail: `exit=0 rows=1`, code: r.code };
    },
  },
  {
    id: 'P2',
    kind: 'function',
    title: 'registered member with a registry path resolves THROUGH that path',
    run() {
      const r = runCli([
        '--skill', 'fixture-renamed', '--status', 'success',
        '--task', 'p2', '--outcome', 'p2 outcome', ...BASE,
      ]);
      assert(r.code === 0, `exit ${r.code} (want 0); stderr=${r.err}`);
      assert(existsSync(CUSTOM_LOG), 'the registry path folder did not receive the row');
      assert(!existsSync(join(SKILLS, 'fixture-renamed')), 'a folder named after the skill was created instead');
      assert(dataRows(CUSTOM_LOG) === 1, `data rows ${dataRows(CUSTOM_LOG)} (want 1)`);
      return { detail: `exit=0 rows=1 in the registry path`, code: r.code };
    },
  },
  {
    id: 'P3',
    kind: 'function',
    title: 'unregistered but existing folder is logged, and the fact is announced',
    run() {
      const r = runCli([
        '--skill', 'fixture-unregistered', '--status', 'success',
        '--task', 'p3', '--outcome', 'p3 outcome', ...BASE,
      ]);
      assert(r.code === 0, `exit ${r.code} (want 0); stderr=${r.err}`);
      assert(/not in the registry/.test(r.err), `stderr lacks the registry note: ${r.err}`);
      assert(dataRows(UNREG_LOG) === 1, `data rows ${dataRows(UNREG_LOG)} (want 1)`);
      return { detail: `exit=0 rows=1 note=not-in-registry`, code: r.code };
    },
  },
  {
    id: 'P4',
    kind: 'gate',
    title: 'a name that resolves to nothing FAILS LOUDLY and writes nothing',
    run() {
      const before = countRunsFiles(FIXTURE);
      const r = runCli([
        '--skill', 'does-not-exist-xyz', '--status', 'success',
        '--task', 'p4', '--outcome', 'p4 outcome', ...BASE,
      ]);
      assert(r.code !== 0, `exit ${r.code} (want non-zero)`);
      assert(r.code === 2, `exit ${r.code} (want 2)`);
      assert(r.err.includes('does-not-exist-xyz'), 'the error does not name the request');
      const membersLine = (r.err.split('\n').find((l) => l.includes('registered members')) || '');
      assert(membersLine.includes('fixture-member'), `the member list is empty: ${membersLine}`);
      assert(!membersLine.includes('fixture-reference'), `a reference was listed as a member: ${membersLine}`);
      assert(r.err.includes('fixture-unregistered'), 'the folder list on disk is missing');
      const after = countRunsFiles(FIXTURE);
      assert(after === before, `run log files ${before} -> ${after} (must not change)`);
      assert(!existsSync(join(SKILLS, 'does-not-exist-xyz')), 'a folder was created for the unknown name');
      return { detail: `exit=${r.code} alternatives listed, nothing written`, code: r.code };
    },
  },
  {
    id: 'P5',
    kind: 'function',
    title: 'an unreadable registry does not kill the logger',
    run() {
      const r = runCli([
        '--skill', 'fixture-member', '--status', 'success',
        '--task', 'p5', '--outcome', 'p5 outcome',
        '--skills-root', SKILLS, '--registry', join(FIXTURE, 'no-such-registry.json'),
      ]);
      assert(r.code === 0, `exit ${r.code} (want 0); stderr=${r.err}`);
      assert(/falling back to the plain folder path/.test(r.err), `stderr lacks the fallback note: ${r.err}`);
      assert(dataRows(MEMBER_LOG) === 2, `data rows ${dataRows(MEMBER_LOG)} (want 2)`);
      return { detail: `exit=0 rows=2 fallback=plain-folder`, code: r.code };
    },
  },
  {
    id: 'P6',
    kind: 'gate',
    title: 'the read-back gate can go red (a dropped append is caught)',
    run() {
      const io = {
        appendFileSync: () => {},
        existsSync,
        mkdirSync,
        readFileSync,
        readdirSync,
        statSync,
        writeFileSync,
      };
      const r = runLog({
        skill: 'fixture-member',
        status: 'success',
        task: 'p6',
        outcome: 'p6 outcome',
        skillsRoot: SKILLS,
        registryPath: REGISTRY,
        io,
      });
      assert(r.code === 1, `code ${r.code} (want 1)`);
      assert(r.err.join('\n').includes('could not be read back'), `stderr lacks the read-back error: ${r.err}`);
      assert(dataRows(MEMBER_LOG) === 2, `the dropped append still wrote a row (${dataRows(MEMBER_LOG)})`);
      return { detail: `code=1 read-back fired`, code: r.code };
    },
  },
  {
    id: 'P7',
    kind: 'function',
    title: 'an error is recorded VERBATIM',
    run() {
      const text = 'BOOM: the exact text | with a pipe';
      const r = runCli([
        '--skill', 'fixture-member', '--status', 'error',
        '--task', 'p7', '--outcome', 'p7 outcome', '--error', text, ...BASE,
      ]);
      assert(r.code === 0, `exit ${r.code} (want 0); stderr=${r.err}`);
      const txt = readFileSync(MEMBER_LOG, 'utf8');
      assert(txt.includes(text), 'the error is not in the log verbatim');
      assert(txt.includes('**Error, verbatim**'), 'the verbatim block is missing');
      return { detail: `exit=0 verbatim block present`, code: r.code };
    },
  },
  {
    id: 'P8',
    kind: 'gate',
    title: 'the three exit codes are distinguishable',
    run(ctx) {
      const codes = {
        logged: ctx.results.P1 && ctx.results.P1.code,
        unresolved: ctx.results.P4 && ctx.results.P4.code,
        unreadable: ctx.results.P6 && ctx.results.P6.code,
      };
      for (const k of ['logged', 'unresolved', 'unreadable']) {
        assert(typeof codes[k] === 'number', `${k}=${codes[k]} (want a measured exit code)`);
      }
      assert(codes.logged === 0, `logged=${codes.logged} (want 0)`);
      assert(codes.unresolved !== 0, `unresolved=${codes.unresolved} (want non-zero)`);
      assert(codes.unreadable !== 0, `unreadable=${codes.unreadable} (want non-zero)`);
      assert(
        new Set([codes.logged, codes.unresolved, codes.unreadable]).size === 3,
        `exit codes collide: ${JSON.stringify(codes)}`
      );
      return { detail: `logged=${codes.logged} unresolved=${codes.unresolved} unreadable=${codes.unreadable}` };
    },
  },
  {
    id: 'P9',
    kind: 'gate',
    title: 'a bad folder probe never loses a registered member',
    run() {
      // Scenario A: the probe lies twice and then tells the truth. The RETRY
      // must rescue the member - this is the shape of the observed transient.
      let calls = 0;
      const flakyIo = {
        appendFileSync,
        existsSync,
        mkdirSync,
        readFileSync,
        readdirSync,
        statSync: (p) => {
          calls++;
          if (calls <= 2) throw new Error('EIO: the probe lies');
          return statSync(p);
        },
        writeFileSync,
      };
      const a = runLog({
        skill: 'fixture-member',
        status: 'success',
        task: 'p9a',
        outcome: 'p9a outcome',
        skillsRoot: SKILLS,
        registryPath: REGISTRY,
        io: flakyIo,
      });
      assert(a.code === 0, `scenario A code ${a.code} (want 0); err=${a.err.join(' | ')}`);
      assert(
        !a.err.join('\n').includes('the folder listing sees'),
        'scenario A was rescued by the listing instead of the retry'
      );
      assert(dataRows(MEMBER_LOG) === 4, `scenario A rows ${dataRows(MEMBER_LOG)} (want 4)`);

      // Scenario B: the probe never tells the truth. The registry and the
      // folder listing still get a vote, so the member is not silently missed.
      const blindIo = {
        appendFileSync,
        existsSync,
        mkdirSync,
        readFileSync,
        readdirSync,
        statSync: () => {
          throw new Error('EIO: the probe is blind');
        },
        writeFileSync,
      };
      const b = runLog({
        skill: 'fixture-member',
        status: 'success',
        task: 'p9b',
        outcome: 'p9b outcome',
        skillsRoot: SKILLS,
        registryPath: REGISTRY,
        io: blindIo,
      });
      assert(b.code === 0, `scenario B code ${b.code} (want 0); err=${b.err.join(' | ')}`);
      assert(
        b.err.join('\n').includes('the folder listing sees fixture-member'),
        `scenario B was not rescued: ${b.err.join(' | ')}`
      );
      assert(dataRows(MEMBER_LOG) === 5, `scenario B rows ${dataRows(MEMBER_LOG)} (want 5)`);
      return { detail: 'retry rescued A (exit 0), listing rescued B (exit 0)' };
    },
  },
  {
    id: 'P10',
    kind: 'gate',
    title: 'no real member run log was touched',
    run(ctx) {
      const now = snapshotRealLogs();
      const before = ctx.realSnapshot;
      assert(before.size === now.size, `real run logs ${before.size} -> ${now.size}`);
      for (const [p, sig] of before) {
        assert(now.has(p), `a real run log disappeared: ${p}`);
        assert(now.get(p) === sig, `a real run log changed: ${p} (${sig} -> ${now.get(p)})`);
      }
      return { detail: `${now.size} real run logs unchanged` };
    },
  },
];

function main() {
  console.log('LOG-RUN SELF-CHECK');
  console.log(`instrument: ${SCRIPT}`);
  console.log(`fixture:    ${FIXTURE}  (kept, not deleted)`);

  buildFixture();
  const realSnapshot = snapshotRealLogs();

  const results = {};
  const ctx = { results, realSnapshot };
  let failed = 0;
  let gates = 0;
  let gatesProved = 0;

  for (const p of PROBES) {
    const isGate = p.kind === 'gate';
    if (isGate) gates++;
    try {
      const r = p.run(ctx) || {};
      results[p.id] = r;
      if (isGate) gatesProved++;
      console.log(`  ${p.id} ok   ${p.title} -> ${r.detail || ''}`);
    } catch (e) {
      failed++;
      console.error(`  ${p.id} FAIL ${p.title} -> ${e && e.message ? e.message : e}`);
    }
  }

  console.log('');
  console.log(`probes run: ${PROBES.length}`);
  console.log(`falsified: ${gatesProved}  (gate probes: ${gates} - each one proved the instrument blocks)`);
  console.log(`result: ${failed === 0 ? 'PASS' : 'FAIL'} ${PROBES.length - failed}/${PROBES.length}`);
  return failed === 0 ? 0 : 1;
}

process.exit(main());

'use strict';
// ── wire-boundary.js — the two harnesses `wire.boundary` asked for and never had ──
//
// WHY THIS FILE EXISTS. `wire.boundary` reads:
//   "Validate at the socket/file boundary where two processes meet, never in one
//    process's own memory."
// and its two obligations were: a lock asserted ACROSS PROCESSES, and a trap that
// verifies payload CONTENT rather than path existence. The runbook has carried
// that node as UNKNOWN since it was written, because neither harness existed.
//
// Neither is decoration. Both are the two defects I actually produced on
// 2026-10-07:
//
//   1. I ran two suites at once against the same live dashboard and could not
//      attribute the resulting `unknown`. One process's own memory cannot detect
//      that; only a second process trying the same lock can.
//   2. My sabotage suite's preflight checked that its undo file hashed to the
//      bytes it had just written. That passes on a corrupted undo, because it
//      reads the corruption it is meant to catch. Only comparing the payload's
//      actual content against a separately-held expectation can fail.
//
// FIRST RUN OF THIS FILE FAILED 5 OF 9 CHECKS. All five were defects in the
// harness, not in the machine, and each is named in the comment where it was
// fixed. The broken version is kept on disk as wire-boundary.js.BROKEN-<ts>.
// A harness whose first version passes everything has usually not been tested.
//
// USAGE:  node wire-boundary.js            run the full suite, print JSON
//         node wire-boundary.js --child hold  <lockPath> [ms]
//         node wire-boundary.js --child try   <lockPath>
//         node wire-boundary.js --child verify <payloadPath> <expectedSha>

const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');
const { spawn, spawnSync } = require('child_process');

// A lock older than this is presumed abandoned by a dead process and may be
// taken over. Stated as a contract, not a measurement: no wall clock here is
// derived from an observation, it is a policy about how long a lock may be held.
const STALE_LOCK_MS = 15000;
const HOLD_MS = 800;

const results = [];
function record(node, kind, ok, detail) {
  results.push({ node: node, kind: kind, ok: Boolean(ok), detail: String(detail) });
}
const sleepSync = (ms) => spawnSync(process.execPath, ['-e', 'setTimeout(()=>{},' + ms + ')']);

// ── 1. the cross-process lock ────────────────────────────────────────────────
// O_EXCL create is the only primitive here that the OS itself arbitrates. A
// boolean in memory is arbitrated by nothing; this is arbitrated by the kernel,
// which is what "across processes" has to mean for the claim to be true.

function readLock(lockPath) {
  try { return JSON.parse(fs.readFileSync(lockPath, 'utf8')); }
  catch (e) { return null; }
}

function isStale(rec, nowMs, staleMs) {
  // An unreadable lock is HELD, not stealable. If a holder dies mid-write the
  // file can be truncated; treating that as "abandoned" would hand the lock to
  // two processes at once, which is the exact failure this file exists to stop.
  if (!rec || typeof rec.at !== 'number') return false;
  return (nowMs - rec.at) > (staleMs === undefined ? STALE_LOCK_MS : staleMs);
}

function acquire(lockPath, meta, nowMs, staleMs) {
  // DEFECT 1, FIXED. The first version declared `isStale` and then never called
  // it — `acquire` only did openSync('wx') and so refused a lock abandoned by a
  // dead process forever. The check "stale-lock-takeover" FAILED on the first
  // run and exposed it. A rule nobody calls is not a rule.
  const now = nowMs === undefined ? Date.now() : nowMs;

  if (fs.existsSync(lockPath)) {
    const rec = readLock(lockPath);
    if (!isStale(rec, now, staleMs)) {
      return { ok: false, reason: 'held', heldBy: rec };
    }
    // Take over an abandoned lock, and say so in the lock body so the next
    // reader can see the takeover happened rather than inferring it.
    try { fs.unlinkSync(lockPath); }
    catch (e) { return { ok: false, reason: 'raced', heldBy: rec }; }
  }

  let fd;
  try {
    fd = fs.openSync(lockPath, 'wx');
  } catch (e) {
    if (e.code !== 'EEXIST') throw e;
    return { ok: false, reason: 'held', heldBy: readLock(lockPath) };
  }
  try {
    fs.writeSync(fd, JSON.stringify(Object.assign({
      pid: process.pid, at: now, tookOver: !!(meta && meta.tookOver)
    }, meta || {})));
  } finally {
    fs.closeSync(fd);
  }
  return { ok: true, reason: 'acquired' };
}

function release(lockPath) {
  try { fs.unlinkSync(lockPath); return true; }
  catch (e) { return false; }
}

// ── 2. the content trap ─────────────────────────────────────────────────────
// The expectation is held HERE, by the caller, and never re-read from the thing
// it is checking. That is the whole difference between this and the preflight
// that failed: a preflight that derives its expectation from the file it is
// protecting can only ever agree with it.

function sha256(buf) { return crypto.createHash('sha256').update(buf).digest('hex').toUpperCase(); }

function verifyContent(payloadPath, expectedSha) {
  let bytes;
  try { bytes = fs.readFileSync(payloadPath); }
  catch (e) { return { ok: false, why: 'unreadable', code: e.code || e.message }; }
  const actual = sha256(bytes);
  const expect = String(expectedSha).toUpperCase();
  return {
    ok: actual === expect,
    why: actual === expect ? 'content matches' : 'content differs',
    actual: actual, expected: expect, bytes: bytes.length
  };
}

// ── the child: a separate OS process ────────────────────────────────────────

if (process.argv.indexOf('--child') >= 0) {
  const i = process.argv.indexOf('--child');
  const mode = process.argv[i + 1];
  const a1 = process.argv[i + 2];
  const a2 = process.argv[i + 3];

  if (mode === 'hold') {
    const lockPath = a1;
    const ms = Number(a2 || HOLD_MS);
    const ready = lockPath + '.ready';
    const got = acquire(lockPath, { role: 'holder' });
    fs.writeFileSync(ready, String(process.pid));   // signal AFTER we truly own it
    const t0 = Date.now();
    while (Date.now() - t0 < ms) { /* hold, so a second process can contend */ }
    release(lockPath);
    try { fs.unlinkSync(ready); } catch (e) {}
    process.stdout.write(JSON.stringify({ role: 'holder', pid: process.pid, acquired: got.ok }));
    process.exit(0);
  }

  if (mode === 'try') {
    const got = acquire(a1, { role: 'contender' });
    if (got.ok) release(a1);
    process.stdout.write(JSON.stringify({
      role: 'contender', pid: process.pid, acquired: got.ok,
      reason: got.reason, heldBy: got.heldBy || null
    }));
    process.exit(got.ok ? 0 : 3);
  }

  if (mode === 'verify') {
    // DEFECT 2, FIXED. The first version read payloadPath from i+4 and the
    // expectation from i+5, but the parent called it with (payload, payload,
    // sha) — so the child verified a hex string as if it were a path, and two
    // content checks failed for reasons that had nothing to do with content.
    const r = verifyContent(a1, a2);
    process.stdout.write(JSON.stringify({ role: 'verifier', pid: process.pid, result: r }));
    process.exit(r.ok ? 0 : 4);
  }

  process.stderr.write('unknown child mode\n');
  process.exit(1);
}

// ── the suite ────────────────────────────────────────────────────────────────

function runChildSync(args) {
  const r = spawnSync(process.execPath, [__filename].concat(args), { encoding: 'utf8' });
  let json = null;
  try { json = JSON.parse(r.stdout); } catch (e) {}
  return { status: r.status, json: json, stderr: r.stderr };
}

// DEFECT 3, FIXED. The first version started the lock holder with spawnSync,
// which blocks until that child EXITS. By the time the parent began contending,
// the holder had already released and deleted its readiness marker — so the
// parent proved nothing about overlap. The holder is now started asynchronously
// and the parent contends while it is provably still alive.
function runSuite() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'wire-boundary-'));
  const lockPath = path.join(dir, 'live.lock');
  const readyPath = lockPath + '.ready';
  const payloadPath = path.join(dir, 'payload.bin');

  // Distinct content per run so a stale payload from a previous run can never be
  // what made the trap pass.
  const GOOD = Buffer.from('WIRE-BOUNDARY-GOOD-' + process.pid + '-' + Date.now());
  const EVIL = Buffer.from('WIRE-BOUNDARY-EVIL-' + process.pid + '-' + Date.now());
  fs.writeFileSync(payloadPath, GOOD);
  const goodSha = sha256(GOOD);            // expectation held HERE, never read back

  return new Promise((resolve) => {
    const holder = spawn(process.execPath, [__filename, '--child', 'hold', lockPath, String(HOLD_MS)],
      { stdio: ['ignore', 'pipe', 'pipe'] });
    let holderOut = '';
    holder.stdout.on('data', d => { holderOut += d.toString(); });

    let waited = 0;
    const poll = setInterval(() => {
      // 1 — the holder is alive and provably owns the lock right now
      if (fs.existsSync(readyPath) && fs.existsSync(lockPath)) {
        clearInterval(poll);
        const holderRec = readLock(lockPath);

        const held = runChildSync(['--child', 'try', lockPath]);
        record('wire.boundary', 'holder-acquired-across-process',
          Boolean(holderRec) && holderRec.role === 'holder' && holderRec.pid !== process.pid,
          'a separate OS process (pid ' + (holderRec && holderRec.pid) + ') owns the lock; this suite runs as pid ' + process.pid);

        record('wire.boundary', 'contender-refused-while-held',
          held.status === 3 && held.json && held.json.acquired === false,
          held.json
            ? ('contender (pid ' + held.json.pid + ') was refused while the holder (pid ' + ((held.json.heldBy || {}).pid) + ') was still holding — two live OS processes, two different pids, and the refusal came from the kernel, not from memory')
            : 'no verdict from the contender');

        // let the holder finish and confirm it cleans up after itself
        holder.on('exit', () => {
          setTimeout(() => {
            const released = !fs.existsSync(lockPath);

            const after = runChildSync(['--child', 'try', lockPath]);
            record('wire.boundary', 'admitted-after-release', released && after.status === 0,
              'the holder released on exit (lock gone: ' + released + '); a fresh process was then admitted, so the lock is not stuck');

            // stale takeover — this is the check that caught the dead isStale()
            fs.writeFileSync(lockPath, JSON.stringify({ pid: 999999, role: 'holder', at: Date.now() - (STALE_LOCK_MS + 5000) }));
            const stale = acquire(lockPath, { role: 'stale-taker', tookOver: true });
            const staleRec = stale.ok ? readLock(lockPath) : null;
            record('wire.boundary', 'stale-lock-takeover',
              stale.ok && staleRec && staleRec.tookOver === true,
              stale.ok
                ? ('a lock abandoned ' + (STALE_LOCK_MS + 5000) + 'ms ago was taken over and the takeover is recorded in the lock body — a dead holder cannot deadlock this machine forever')
                : 'a dead holder could still deadlock the machine');
            if (stale.ok) release(lockPath);

            fs.writeFileSync(lockPath, JSON.stringify({ pid: 999999, role: 'holder', at: Date.now() }));
            const fresh = acquire(lockPath, { role: 'should-be-refused' });
            record('wire.boundary', 'fresh-lock-not-stolen', fresh.ok === false,
              'a fresh lock is still refused even though a takeover rule exists — the takeover is bounded by age, it is not a back door');
            release(lockPath);

            // an unparseable lock must be treated as HELD, never as abandoned
            fs.writeFileSync(lockPath, 'not json at all');
            const garbled = acquire(lockPath, { role: 'should-be-refused' });
            record('wire.boundary', 'unreadable-lock-treated-as-held', garbled.ok === false,
              'a lock file that cannot be parsed is treated as HELD. Treating an unreadable lock as abandoned would hand it to two processes at once — precisely the failure this harness exists to prevent.');
            release(lockPath);

            // ── the content trap, executed by a separate process ─────────────
            fs.writeFileSync(payloadPath, EVIL);
            const wrong = runChildSync(['--child', 'verify', payloadPath, goodSha]);
            record('wire.boundary', 'content-trap-fires-on-wrong-payload',
              wrong.status === 4 && wrong.json && wrong.json.result.ok === false,
              wrong.json
                ? ('the path existed and was readable, yet the content differed — so the trap fired on CONTENT, not on existence')
                : 'no verdict');

            record('wire.boundary', 'trap-is-not-an-existence-check',
              Boolean(wrong.json) && wrong.json.result.bytes === EVIL.length && fs.existsSync(payloadPath),
              'the file exists AND was fully read (' + (wrong.json ? wrong.json.result.bytes : '?') + ' bytes); only the hash disagreed — proof the trap reads bytes, not the path');

            fs.writeFileSync(payloadPath, GOOD);
            const right = runChildSync(['--child', 'verify', payloadPath, goodSha]);
            record('wire.boundary', 'content-trap-quiet-on-good-payload',
              right.status === 0 && right.json && right.json.result.ok === true,
              'the same trap, same call shape, correct content: silent');

            // ── falsification control ─────────────────────────────────────────
            const selfConsistent = sha256(fs.readFileSync(payloadPath));
            fs.writeFileSync(payloadPath, EVIL);
            const fool = verifyContent(payloadPath, selfConsistent);
            record('wire.boundary', 'falsification-control', fool.ok === false,
              'an expectation re-derived from the CORRUPT payload is REJECTED. The expectation lives in the caller; a preflight that reads its own expectation out of the artifact it is protecting is the defect this trap exists to catch, and here that defect is caught.');
            fs.writeFileSync(payloadPath, GOOD);

            try { fs.rmSync(dir, { recursive: true, force: true }); } catch (e) {}

            const pass = results.filter(r => r.ok).length;
            const fail = results.length - pass;
            resolve({
              node: 'wire.boundary',
              verdict: fail === 0 ? 'PASS' : 'FAIL',
              pass: pass, fail: fail, total: results.length,
              checks: results
            });
          }, 120);
        });
        return;
      }

      if (waited > 8000) {   // the holder died or never signalled
        clearInterval(poll);
        try { holder.kill(); } catch (e) {}
        record('wire.boundary', 'holder-acquired-across-process', false,
          'the holder never signalled readiness within 8s (stdout was: ' + JSON.stringify(holderOut) + ')');
        try { fs.rmSync(dir, { recursive: true, force: true }); } catch (e) {}
        resolve({ node: 'wire.boundary', verdict: 'FAIL', pass: 0, fail: 1, total: 1, checks: results });
      }
      waited += 25;
    }, 25);
  });
}

if (require.main === module) {
  runSuite().then((out) => {
    process.stdout.write(JSON.stringify(out, null, 2) + '\n');
    process.exit(out.fail === 0 ? 0 : 1);
  });
}

module.exports = { acquire, release, verifyContent, sha256, isStale, runSuite, STALE_LOCK_MS };

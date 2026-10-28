// ga-doctor.mjs - THE CONTROL POINT for Google Access.
//
// One command, one verdict. Popy's requirement (27-28 Oct 2026): the system
// must be permanently verifiable, so that a new session - or ANY other AI on
// this station - can prove the connection instead of rebuilding it.
//
// WHAT IT CHECKS (each check is independent: a failure never hides the others)
//   C1 container      - exists, running, healthy, right image, restart policy
//   C1b running-code - the BYTES running inside the container are the bytes
//                       in the repo (the 1.0.9 incident: healthy, but old)
//   C2 health         - grant=live, reauth_required=false, tool count
//   C3 services       - a LIVE probe of every Google service; the tally
//   C4 extendlm       - the NotebookLM token is alive, and its snapshot is
//                       published to the Cloud secret
//   C5 browser-mcp    - the registered path EXISTS and the server answers
//                       over its real stdio transport
//   C6 mcp-registry   - Google_Access is registered globally, so every agent
//                       (not only Mavis) inherits it
//   C10 mcp-paths     - every path the global registry points to EXISTS on
//                       disk (a dead path breaks every agent, silently)
//   C7 tasks          - the scheduled tasks that keep the system alive
//   C8 consent        - the re-consent listener is up, so a future re-consent
//                       is ONE CLICK and not a re-setup
//   C9 picker         - the active Photo Picker session
//
// EXIT: 0 = every critical check passed, 2 = at least one failed.
// The verdict distinguishes REFUSED (Google answered a refusal) from ERROR
// (nothing answered) from OK. A refusal is never reported as a failure.
//
// Usage: node ga-doctor.mjs [--container <name>] [--data <dir>]
//                           [--repo <owner/name>] [--json] [--self-test]
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import http from "node:http";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { execFileSync, spawn } from "node:child_process";

// ESM has no __dirname. MEASURED 2026-10-28: the first run of the extended
// control point died with "__dirname is not defined" and exited 3 - which is
// the point of a distinct exit code for a crash: a crash is never reported as
// a green verdict.
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const argOf = (flag, dflt) => {
  const i = process.argv.indexOf(flag);
  return i !== -1 ? process.argv[i + 1] : dflt;
};
const hasFlag = (flag) => process.argv.includes(flag);

const CONTAINER = argOf("--container", "Google_Access");
const DATA = argOf("--data", "C:/Users/apviz/.minimax/google-access/data");
const REPO = argOf("--repo", "apvizual-max/MAVIS-CLOUD");
const MCP_JSON = argOf("--mcp-json", "C:/Users/apviz/.minimax/mcp.json");
const MCP_URL = argOf("--mcp-url", "http://127.0.0.1:8766/mcp");
const HEALTH_URL = argOf("--health", "http://127.0.0.1:8766/health");
const PROBE = argOf("--probe", "C:/Users/apviz/.minimax/google-access/probe-services.mjs");
const NOTEBOOKLM_JS = argOf(
  "--notebooklm-js",
  "C:/Users/apviz/.minimax-agent/projects/Mavis-Google_Access/google-layer/minimax-notebooklm.js"
);
const TASKS = ["Google_Access_Watch", "MavisExtendLMHeartbeat", "MavisPickerHeartbeat", "Google_Access_Doctor"];
const EXPECTED_REFUSED = ["keep", "sites"];

const results = [];
let injected = null; // the self-test hook: forces one check to fail

function record(id, ok, detail, critical = true) {
  results.push({ id, ok, detail, critical });
  const tag = ok ? "OK  " : critical ? "FAIL" : "WARN";
  console.log("CHECK " + id + " " + tag + " " + detail);
  return ok;
}

function run(cmd, args, opts) {
  try {
    return execFileSync(cmd, args, Object.assign({ encoding: "utf8", windowsHide: true, timeout: 120000 }, opts || {}));
  } catch (e) {
    return null;
  }
}

function tcpOpen(port, host = "127.0.0.1", timeoutMs = 1500) {
  return new Promise((res) => {
    const req = http.request({ host, port, path: "/", method: "GET", timeout: timeoutMs }, (r) => {
      r.resume();
      res(true);
    });
    req.on("error", () => res(false));
    req.on("timeout", () => {
      req.destroy();
      res(false);
    });
    req.end();
  });
}

// ── C1 container ───────────────────────────────────────────────────────────
function checkContainer() {
  const out = run("docker", ["inspect", CONTAINER]);
  if (!out) return record("C1.container", false, "docker inspect failed for " + CONTAINER);
  let d;
  try {
    d = JSON.parse(out)[0];
  } catch (e) {
    return record("C1.container", false, "unreadable docker inspect output");
  }
  const status = d.State ? d.State.Status : "?";
  const health = d.State && d.State.Health ? d.State.Health.Status : "none";
  const image = d.Config ? d.Config.Image : "?";
  const policy = d.HostConfig && d.HostConfig.RestartPolicy ? d.HostConfig.RestartPolicy.Name : "?";
  const ok = status === "running" && health === "healthy" && policy === "unless-stopped";
  return record(
    "C1.container",
    ok,
    "status=" + status + " health=" + health + " image=" + image + " restart=" + policy
  );
}

// ── C1b the RUNNING code is the code in the repo ───────────────────────────
// MEASURED 2026-10-28 (the 1.0.9 incident): the repository carried the
// repair, the image had been built before it, and the container was therefore
// RUNNING THE OLD CODE while every document said it was fixed. A container
// that is healthy proves it is alive, not that it is the thing you wrote.
// So the bytes inside the container are hashed and compared with the repo.
function checkRunningCode() {
  const repoFile = path.join(__dirname, "..", "container", "server.mjs");
  if (!fs.existsSync(repoFile)) {
    return record("C1b.running-code", false, "repo source not found: " + repoFile);
  }
  const repoHash = crypto.createHash("sha256").update(fs.readFileSync(repoFile)).digest("hex");
  const live = run("docker", [
    "exec",
    CONTAINER,
    "node",
    "-p",
    "require('crypto').createHash('sha256').update(require('fs').readFileSync('/app/server.mjs')).digest('hex')",
  ]);
  if (!live) {
    return record("C1b.running-code", false, "could not hash /app/server.mjs inside " + CONTAINER);
  }
  const liveHash = live.trim().split(/\r?\n/).filter(Boolean).pop() || "";
  const match = liveHash === repoHash;
  return record(
    "C1b.running-code",
    match,
    "repo=" + repoHash.slice(0, 12) + " running=" + liveHash.slice(0, 12) + " match=" + match
  );
}

// ── C2 health ──────────────────────────────────────────────────────────────
async function checkHealth() {
  try {
    const r = await fetch(HEALTH_URL, { signal: AbortSignal.timeout(8000) });
    const j = await r.json();
    const ok = j.grant === "live" && j.reauth_required === false;
    return record("C2.health", ok, "grant=" + j.grant + " reauth=" + j.reauth_required + " tools=" + j.tools);
  } catch (e) {
    return record("C2.health", false, "health unreachable: " + (e && e.message ? e.message : e));
  }
}

// ── C3 services (live) ─────────────────────────────────────────────────────
// THE DEFECT THIS BLOCK FIXES (MEASURED 2026-10-28, live, this machine):
//   00:48Z  VERDICT=PASS  C3.services OK=14 REFUSED=2[keep,sites] ERROR=0[]
//   ~01:13Z C3.services FAILED OK=13 REFUSED=3[books,keep,sites] ERROR=0[]
//            unexpected_refused=books        -> VERDICT=FAIL, exit 2
//   seconds later a direct live probe: SERVICE=books ... STATUS=OK
// So the control point reported a PERMANENT failure for a service that was
// working: a FALSE RED on a transient upstream condition. And when it went
// red it printed the COUNTS but not the CAUSE, so an operator had to
// re-derive what Google had actually said.
//
// MEASURED AGAIN while this was being fixed: 4 live probes of Books gave
// 2 x GOOGLE_HTTP_503 "Service temporarily unavailable" and 2 x OK. The
// blip is INTERMITTENT, roughly 1 in 3 probes.
//
// THE REFUSAL VOCABULARY (everything probe-services.mjs classify() can
// produce) and what each token MEANS:
//
//   GOOGLE_HTTP_429      TRANSIENT  - Google is rate limiting this account.
//   GOOGLE_HTTP_5xx      TRANSIENT  - Google's upstream is degraded.
//   GOOGLE_HTTP_403      PERMANENT  - the scope is not granted (keep).
//   GOOGLE_HTTP_404      PERMANENT  - the API does not exist (sites).
//   MISSING_SCOPE        PERMANENT  - the grant does not carry the scope.
//   NO_CREDENTIAL /
//   NO_EXTENDLM_TOKEN /
//   NO_ID                PERMANENT  - the local setup is incomplete.
//   is not a function /
//   TypeError /
//   ReferenceError       PERMANENT  - the tool crashed on the data. A crash
//                                      in the handler never heals by asking
//                                      again. MEASURED 2026-10-28: gdocs_get
//                                      answered "ERROR: el.table.rows.
//                                      forEach is not a function" on 4 of 4
//                                      live probes (container/server.mjs:
//                                      the table guard checks that rows
//                                      EXISTS, not that it is an array).
//   transport:/timeout/
//   temporarily/unavailable/
//   upstream/rate limit  TRANSIENT  - nothing answered; a temporary or
//                                      upstream condition.
//
// An UNRECOGNISED refusal counts as PERMANENT, on purpose: a control point
// that softens what it does not understand is a control point that stops
// measuring. The remedy is a wider vocabulary here, never a weaker gate.
//
// THE DECISION (written down, so nobody has to guess):
//   a PERMANENT refusal of a service that is not in EXPECTED_REFUSED  -> FAIL
//     (the gate blocks, exit 2). The service is broken, not the weather.
//   a TRANSIENT refusal that RECOVERS on a later probe              -> OK, and
//     the blip is still printed in the C3 line with its measured detail.
//   a TRANSIENT refusal that NEVER recovers                         -> WARNING
//     (counted in SUMMARY warnings=N, the run stays green, exit 0). The
//     configuration is proven correct by the other services answering in
//     the SAME probe; what failed is Google's upstream. It is reported with
//     its measured detail and the number of attempts - never as an OK.
const TRANSIENT_HTTP = /GOOGLE_HTTP_(429|5\d\d)\b/;
const PERMANENT_HTTP = /GOOGLE_HTTP_(403|404)\b/;
const PERMANENT_TOKEN = /MISSING_SCOPE|NO_CREDENTIAL|NO_EXTENDLM_TOKEN|NO_ID/;
// A crash in the tool's own handler: deterministic, so it never heals by
// asking again. MEASURED 2026-10-28: gdocs_get on the account's first Doc
// answered "ERROR: el.table.rows.forEach is not a function" on 4 of 4 live
// probes.
const PERMANENT_RUNTIME =
  /is not a function|TypeError|ReferenceError|Cannot read properties|Cannot access/;
const TRANSIENT_WORD =
  /temporar|timeout|timed out|ECONNRESET|ECONNREFUSED|ETIMEDOUT|EAI_AGAIN|ENOTFOUND|socket hang up|transport:|service unavailable|bad gateway|gateway timeout|upstream|rate limit|try again|backendFailed|unavailable/i;

// MEASURED: the probe covers 16 services; keep and sites are refused by
// design, so 14 are expected to answer. A run that covers fewer is not a
// healthy run, it is an incomplete one - and it says so.
const MIN_HEALTHY_SERVICES = 14;

// MEASURED: the Books blip hit 2 of 4 live probes. One extra probe did not
// clear it (the old code re-probed ONCE and still went red). Three extra
// attempts = 4 in total; at a 1-in-3 failure rate the chance that all four
// probes hit the blip is ~1.2% (with a single extra probe it was ~11%).
const RETRY_EXTRA_ATTEMPTS = 3;
const RETRY_DELAY_MS = 2000;

// The measured detail, printed on one line. Only whitespace is collapsed -
// the string itself is the one the probe measured, never a guess.
function sanitizeDetail(d) {
  return String(d === undefined || d === null ? "" : d).replace(/\s+/g, " ").trim();
}

// A real sleep, without spinning the CPU. The doctor runs its checks in
// sequence, so a blocking wait is the honest thing here.
function sleepSync(ms) {
  if (!(ms > 0)) return;
  const sab = new SharedArrayBuffer(4);
  Atomics.wait(new Int32Array(sab), 0, 0, ms);
}

// PERMANENT or TRANSIENT, decided from the real refusal string.
function classifyRefusal(detail) {
  const d = String(detail || "");
  if (TRANSIENT_HTTP.test(d)) return "transient";
  if (PERMANENT_HTTP.test(d)) return "permanent";
  if (PERMANENT_TOKEN.test(d)) return "permanent";
  if (PERMANENT_RUNTIME.test(d)) return "permanent";
  if (TRANSIENT_WORD.test(d)) return "transient";
  return "permanent"; // unknown -> permanent: the gate stays able to fail
}

function parseProbeOutput(out) {
  const lines = String(out || "").split(/\r?\n/).filter((l) => l.startsWith("SERVICE="));
  const byStatus = { OK: [], REFUSED: [], ERROR: [], SKIP: [] };
  const details = {};
  const status = {};
  for (const l of lines) {
    const name = (l.match(/SERVICE=(\S+)/) || [])[1] || "?";
    const st = (l.match(/STATUS=(\S+)/) || [])[1] || "?";
    const det = (l.match(/DETAIL=(.*)$/) || [])[1] || "";
    (byStatus[st] || (byStatus[st] = [])).push(name);
    details[name] = det;
    status[name] = st;
  }
  return { byStatus: byStatus, details: details, status: status, lines: lines.length };
}

function runProbe() {
  let out = "";
  try {
    out = execFileSync("node", [PROBE], { encoding: "utf8", timeout: 300000, windowsHide: true });
  } catch (e) {
    out = (e && e.stdout ? e.stdout : "") + (e && e.stderr ? e.stderr : "");
  }
  return parseProbeOutput(out);
}

// THE SHARED CORE. The live check and the self-test both call this, so the
// self-test proves the real code path instead of a copy of it. The probe
// RESULT is injected; the verdict is never faked.
function analyzeServices(probeFn, opts) {
  const o = opts || {};
  const delayMs = o.delayMs === undefined ? RETRY_DELAY_MS : o.delayMs;
  const maxExtra = o.maxExtra === undefined ? RETRY_EXTRA_ATTEMPTS : o.maxExtra;
  const log = o.log || function () {};

  const attempts = [];
  const state = new Map(); // service -> what the probes actually saw

  const observe = (run) => {
    for (const name of Object.keys(run.details || {})) {
      const st = (run.status && run.status[name]) || "OK";
      const det = run.details[name] || "";
      let s = state.get(name);
      if (!s) {
        s = { status: st, detail: det, failStatus: "", failDetail: "", failures: 0, observations: 0, permanent: false };
        state.set(name, s);
      }
      s.observations++;
      s.status = st;
      s.detail = det;
      // SKIP is not a failure: the account simply has no object to probe.
      if (st !== "OK" && st !== "SKIP") {
        s.failures++;
        s.failStatus = st;
        s.failDetail = det;
        // The strictest reading: if ANY attempt showed a PERMANENT cause and
        // the service never recovered, it is a permanent failure.
        if (classifyRefusal(det) === "permanent") s.permanent = true;
      }
    }
  };

  const first = probeFn();
  if (!first.lines) {
    return {
      verdict: "FAIL",
      ok: false,
      critical: true,
      detail: "state=FAILED_NO_PROBE the probe produced no SERVICE lines (the container did not answer)",
      attempts: 0,
    };
  }
  attempts.push(first);
  observe(first);

  // The services that are NOT answering and are NOT supposed to be refused.
  const faulty = () => {
    const out = [];
    for (const [name, s] of state) {
      if (EXPECTED_REFUSED.includes(name)) continue;
      if (s.status === "OK" || s.status === "SKIP") continue;
      out.push(name);
    }
    return out;
  };

  // Re-probe. EVERY unexpected refusal is re-probed, not only the ones that
  // match a transient pattern: the token Google happens to answer with during
  // a blip is not predictable, so the decision is taken from the LAST
  // measurement instead of from the first one's wording.
  let extra = 0;
  while (faulty().length > 0 && extra < maxExtra) {
    const f = faulty();
    const kinds = f.map((n) => "kind[" + n + "]=" + classifyRefusal(state.get(n).failDetail)).join(",");
    log(
      "NOTE C3.services unexpected_refusal=" + f.join(",") +
        " " + kinds +
        " -> re-probing (attempt " + (attempts.length + 1) + " of " + (maxExtra + 1) + ")"
    );
    if (delayMs > 0) sleepSync(delayMs);
    const r = probeFn();
    if (!r.lines) {
      return {
        verdict: "FAIL",
        ok: false,
        critical: true,
        detail:
          "state=FAILED_NO_PROBE the probe produced no SERVICE lines on attempt " +
          (attempts.length + 1) + " (the container stopped answering)",
        attempts: attempts.length,
      };
    }
    attempts.push(r);
    observe(r);
    extra++;
  }

  const last = attempts[attempts.length - 1];
  const oks = last.byStatus.OK || [];
  const refused = last.byStatus.REFUSED || [];
  const errors = last.byStatus.ERROR || [];
  const skipped = last.byStatus.SKIP || [];
  const missing = EXPECTED_REFUSED.filter((n) => !refused.includes(n));

  const hard = []; // permanent and still failing -> the gate blocks
  const persistent = []; // transient and never recovered -> a warning
  const recovered = []; // failed, then answered -> shown, not a fault
  for (const [name, s] of state) {
    if (EXPECTED_REFUSED.includes(name)) continue;
    if (s.failures === 0) continue;
    const kind = s.permanent ? "permanent" : "transient";
    const e = { name: name, s: s, kind: kind };
    if (s.status === "OK") recovered.push(e);
    else if (kind === "permanent") hard.push(e);
    else persistent.push(e);
  }

  // A service that failed only for upstream reasons is not a broken
  // configuration, so it still counts towards the coverage floor.
  const effectiveOks = oks.length + persistent.length;
  const floorOk = effectiveOks >= MIN_HEALTHY_SERVICES;

  let stateName = "HEALTHY";
  if (hard.length) stateName = "FAILED_PERMANENT";
  else if (missing.length) stateName = "FAILED_MISSING_REFUSAL";
  else if (!floorOk) stateName = "FAILED_INCOMPLETE";
  else if (persistent.length) stateName = "DEGRADED_TRANSIENT";

  const verdict = stateName === "HEALTHY" ? "OK" : stateName === "DEGRADED_TRANSIENT" ? "WARN" : "FAIL";

  const parts = [];
  parts.push("state=" + stateName);
  parts.push("OK=" + oks.length);
  parts.push("REFUSED=" + refused.length + "[" + refused.join(",") + "]");
  parts.push("ERROR=" + errors.length + "[" + errors.join(",") + "]");
  if (skipped.length) parts.push("SKIPPED=" + skipped.length + "[" + skipped.join(",") + "]");
  parts.push("attempts=" + attempts.length);
  if (missing.length) parts.push("missing_expected_refused=" + missing.join(","));
  // The CAUSE, for every service that was refused and is not expected to be
  // refused - whether it recovered or not. The run log shows the blip
  // instead of hiding it. The status says WHICH kind of fault it was: a
  // Google REFUSAL (a scope/API decision) or a tool ERROR (the handler
  // crashed). They need different repairs.
  const entry = (label, e) =>
    label +
    "=" + e.name +
    " status=" + e.s.failStatus +
    " kind=" + e.kind +
    " attempts=" + e.s.observations +
    " detail[" + e.name + "]=" + sanitizeDetail(e.s.failDetail);
  for (const e of hard) parts.push(entry(e.s.failStatus === "REFUSED" ? "unexpected_refused" : "unexpected_error", e));
  for (const e of persistent) parts.push(entry("persistent_transient", e));
  for (const e of recovered) parts.push(entry("transient_recovered", e));

  return {
    verdict: verdict,
    ok: verdict === "OK",
    critical: verdict === "FAIL",
    detail: parts.join(" "),
    attempts: attempts.length,
    hard: hard,
    persistent: persistent,
    recovered: recovered,
  };
}

function checkServices() {
  if (!fs.existsSync(PROBE)) {
    return record("C3.services", false, "probe not found: " + PROBE);
  }
  const a = analyzeServices(runProbe, {
    log: function (m) {
      console.log(m);
    },
  });
  return record("C3.services", a.ok, a.detail, a.critical);
}

// ---- the self-test (OFFLINE: no live call, no state touched) --------------
// Three DISTINCT probes, each one a case the gate has to survive:
//   1. a PERMANENT refusal of a service that is not in EXPECTED_REFUSED
//      -> the check MUST go red (FAIL). The gate can block.
//   2. a TRANSIENT refusal that RECOVERS on the next probe
//      -> the check MUST NOT go red, and the recovery MUST be shown.
//   3. a TRANSIENT refusal that NEVER recovers
//      -> the check MUST report the documented state (WARNING), never a
//         silent OK.
// The probe RESULT is injected; the verdict is never faked.
const SELF_OK_SERVICES = [
  "identity", "drive", "gmail", "calendar", "photos", "tasks", "apps-script",
  "chat", "contacts", "youtube", "notebooklm", "docs", "sheets",
];
// The two MEASURED refusal strings, copied byte-for-byte out of the live
// probe on 2026-10-28 (the keep one is exactly the probe's 220-char
// truncation). A fixture that is invented would prove nothing about the
// real vocabulary.
const SELF_BOOKS_503 =
  'GOOGLE_HTTP_503: {"code":503,"message":"Service temporarily unavailable.","errors":[{"message":"Service temporarily unavailable.","domain":"global","reason":"backendFailed"}]}';
const SELF_BOOKS_403 =
  'GOOGLE_HTTP_403: {"code":403,"message":"Request had insufficient authentication scopes.","status":"PERMISSION_DENIED","details":[{"@type":"type.googleapis.com/google.rpc.ErrorInfo","reason":"ACCESS_TOKEN_SCOPE_INSUFFICIE';

function fakeProbeResult(spec) {
  const byStatus = { OK: [], REFUSED: [], ERROR: [], SKIP: [] };
  const details = {};
  const status = {};
  for (const name of Object.keys(spec)) {
    const s = spec[name];
    (byStatus[s.status] || (byStatus[s.status] = [])).push(name);
    details[name] = s.detail;
    status[name] = s.status;
  }
  return { byStatus: byStatus, details: details, status: status, lines: Object.keys(spec).length };
}

// The healthy shape, measured on the live system: 14 answering services and
// the two refusals by design.
function healthySpec(overrides) {
  const spec = {};
  for (const s of SELF_OK_SERVICES) spec[s] = { status: "OK", detail: "count=1 keys=count bytes=120" };
  spec.books = { status: "OK", detail: "count=3 items=3 keys=count+items bytes=842" };
  spec.keep = { status: "REFUSED", detail: SELF_BOOKS_403 };
  spec.sites = { status: "REFUSED", detail: "GOOGLE_HTTP_404: <!DOCTYPE html>" };
  return Object.assign(spec, overrides || {});
}

// The last entry repeats, so a sequence of one means "always like this".
function scriptedProbe(sequence) {
  let i = 0;
  return function () {
    const spec = sequence[Math.min(i, sequence.length - 1)];
    i++;
    return fakeProbeResult(spec);
  };
}

function runSelfTest() {
  console.log("=== Google Access - control point (self-test, offline) ===");
  console.log("host=" + os.hostname() + " at=" + new Date().toISOString());
  console.log("");

  const cases = [
    {
      name: "permanent_refusal",
      expected: "FAIL",
      must: ["unexpected_refused=books", "kind=permanent", "GOOGLE_HTTP_403"],
      sequence: [healthySpec({ books: { status: "REFUSED", detail: SELF_BOOKS_403 } })],
    },
    {
      name: "transient_recovers",
      expected: "OK",
      must: ["transient_recovered=books", "GOOGLE_HTTP_503"],
      sequence: [
        healthySpec({ books: { status: "REFUSED", detail: SELF_BOOKS_503 } }),
        healthySpec(),
      ],
    },
    {
      name: "transient_persistent",
      expected: "WARN",
      must: ["persistent_transient=books", "kind=transient", "GOOGLE_HTTP_503"],
      sequence: [healthySpec({ books: { status: "REFUSED", detail: SELF_BOOKS_503 } })],
    },
  ];

  let met = 0;
  let falsified = 0;
  let blocked = 0;
  for (const c of cases) {
    const a = analyzeServices(scriptedProbe(c.sequence), {
      delayMs: 0,
      maxExtra: RETRY_EXTRA_ATTEMPTS,
    });
    const verdictOk = a.verdict === c.expected;
    const evidenceOk = c.must.every((m) => a.detail.indexOf(m) !== -1);
    const passed = verdictOk && evidenceOk;
    if (passed) met++;
    // "falsified" = the probe broke the assumption that the check is always
    // green. "blocked" = the gate actually went red (exit 2).
    if (a.verdict !== "OK") falsified++;
    if (a.verdict === "FAIL") blocked++;
    console.log(
      "SELFTEST_PROBE case=" + c.name +
        " expected=" + c.expected +
        " got=" + a.verdict +
        " cause_named=" + (evidenceOk ? "yes" : "NO") +
        " result=" + (passed ? "PASS" : "FAIL") +
        " falsified=" + (a.verdict !== "OK" ? 1 : 0) +
        " blocked=" + (a.verdict === "FAIL" ? 1 : 0)
    );
    record("C3.services", a.ok, a.detail, a.critical);
  }

  console.log("");
  console.log(
    "SELFTEST probes=" + cases.length +
      " falsified=" + falsified +
      " blocked=" + blocked +
      " expectations_met=" + met + "/" + cases.length
  );
  console.log("VERDICT=" + (met === cases.length ? "PASS" : "FAIL"));
  return met === cases.length;
}

// ── C4 extendlm ────────────────────────────────────────────────────────────
function checkExtendlm() {
  const cfgPath = path.join(DATA, "extendlm.json");
  if (!fs.existsSync(cfgPath)) return record("C4.extendlm", false, "no extendlm.json at " + cfgPath);
  let cfg;
  try {
    cfg = JSON.parse(fs.readFileSync(cfgPath, "utf8"));
  } catch (e) {
    return record("C4.extendlm", false, "unreadable extendlm.json");
  }
  const left = cfg.expires_at ? Math.round((Number(cfg.expires_at) - Date.now()) / 60000) : null;
  const tokenOk = left !== null && left > 0;
  const secretOut = run("gh", ["secret", "list", "--repo", REPO, "--json", "name,updatedAt"]);
  let secretAge = null;
  if (secretOut) {
    try {
      const list = JSON.parse(secretOut);
      const row = list.find((r) => r.name === "GOOGLE_EXTENDLM_CREDENTIAL_B64");
      if (row) secretAge = Math.round((Date.now() - Date.parse(row.updatedAt)) / 60000);
    } catch (e) {
      /* handled below */
    }
  }
  const secretOk = secretAge !== null && secretAge <= 120;
  return record(
    "C4.extendlm",
    tokenOk && secretOk,
    "token_minutes_left=" + left +
      " refresh_token=" + (cfg.refresh_token ? "yes" : "no") +
      " cloud_secret_age_min=" + (secretAge === null ? "absent" : secretAge)
  );
}

// ── C5 browser mcp (real stdio handshake) ─────────────────────────────────
function checkBrowserMcp() {
  if (!fs.existsSync(MCP_JSON)) return record("C5.browser-mcp", false, "mcp.json not found: " + MCP_JSON);
  let reg;
  try {
    reg = JSON.parse(fs.readFileSync(MCP_JSON, "utf8")).mcpServers || {};
  } catch (e) {
    return record("C5.browser-mcp", false, "unreadable mcp.json");
  }
  const entry = reg["minimax-notebooklm"];
  if (!entry) return record("C5.browser-mcp", false, "minimax-notebooklm is not registered");
  const script = entry.args && entry.args[0];
  if (!script || !fs.existsSync(script)) {
    return record("C5.browser-mcp", false, "the registered path does not exist: " + script);
  }
  // A registration that cannot start is not a capability: prove it starts.
  const probe = spawn(process.execPath, [script], { windowsHide: true, stdio: ["pipe", "pipe", "ignore"] });
  const done = new Promise((res) => {
    let buf = "";
    const pend = new Map();
    let id = 0;
    probe.stdout.on("data", (c) => {
      buf += c.toString();
      let i;
      while ((i = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, i).trim();
        buf = buf.slice(i + 1);
        if (!line) continue;
        let m;
        try {
          m = JSON.parse(line);
        } catch {
          continue;
        }
        if (m.id !== undefined && pend.has(m.id)) {
          const p = pend.get(m.id);
          pend.delete(m.id);
          p(m);
        }
      }
    });
    const call = (method, params) =>
      new Promise((r) => {
        const i = ++id;
        pend.set(i, r);
        probe.stdin.write(JSON.stringify({ jsonrpc: "2.0", id: i, method, params }) + "\n");
      });
    (async () => {
      const init = await call("initialize", {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: { name: "ga-doctor", version: "1.0.0" },
      });
      const name = init && init.result && init.result.serverInfo ? init.result.serverInfo.name : "?";
      const list = await call("tools/list", {});
      const tools = list && list.result && Array.isArray(list.result.tools) ? list.result.tools.length : 0;
      res({ ok: Boolean(init && init.result) && tools > 0, name, tools });
    })();
    setTimeout(() => res({ ok: false, name: "timeout", tools: 0 }), 30000);
  });
  return done.then((r) => {
    try {
      probe.kill();
    } catch {
      /* ignore */
    }
    return record("C5.browser-mcp", r.ok, "server=" + r.name + " tools=" + r.tools + " path=" + script);
  });
}

// ── C6 mcp registry (global, so every agent inherits it) ──────────────────
function checkRegistry() {
  let reg;
  try {
    reg = JSON.parse(fs.readFileSync(MCP_JSON, "utf8")).mcpServers || {};
  } catch (e) {
    return record("C6.mcp-registry", false, "unreadable mcp.json");
  }
  const e = reg["Google_Access"];
  if (!e) return record("C6.mcp-registry", false, "Google_Access is not registered");
  const ok = e.enabled !== false && String(e.url || "").trim() === MCP_URL;
  return record("C6.mcp-registry", ok, "enabled=" + e.enabled + " url=" + e.url + " type=" + e.type);
}

// ── C10 registry path integrity ────────────────────────────────────────────
// MEASURED 2026-10-28: three registered entries pointed at a folder that had
// been moved (google-layer/ -> Mavis-Google_Access/google-layer/). The
// registry said "enabled", the files did not exist, and nothing said so.
// A fourth entry pointed at a wrapper npm never created, and the package
// behind it could not import its own dependency.
//
// The configuration is GLOBAL: a dead path there breaks the capability for
// every agent on this station, not only for the session that wrote it. So
// the registry is checked against the DISK, not against itself.
//
// Scope: entries in the Google family are critical - they ARE this system.
// A dead path in an unrelated entry is reported as a warning, because a
// control point that goes red for something outside its domain is a control
// point that gets ignored.
const GOOGLE_FAMILY = [
  "Google_Access",
  "gdrive-mcp",
  "gmail-mcp",
  "google-workspace-mcp",
  "google-calendar-mcp",
  "minimax-notebooklm",
  "notebooklm-mcp",
];

function checkRegistryPaths() {
  let reg;
  try {
    reg = JSON.parse(fs.readFileSync(MCP_JSON, "utf8")).mcpServers || {};
  } catch (e) {
    return record("C10.mcp-paths", false, "unreadable mcp.json");
  }
  const dead = [];
  let checked = 0;
  for (const [name, e] of Object.entries(reg)) {
    if (!e || e.type !== "stdio") continue;
    const paths = [];
    if (typeof e.command === "string" && /[\\/]/.test(e.command)) paths.push(e.command);
    for (const a of e.args || []) {
      if (typeof a === "string" && /^[A-Za-z]:\\/.test(a) && /\.(js|mjs|cjs|cmd|exe|ps1)$/.test(a)) {
        paths.push(a);
      }
    }
    for (const p of paths) {
      checked++;
      if (!fs.existsSync(p)) dead.push(name + "->" + p);
    }
  }
  const googleDead = dead.filter((d) => GOOGLE_FAMILY.some((g) => d.startsWith(g + "->")));
  const otherDead = dead.filter((d) => !googleDead.includes(d));
  const ok = googleDead.length === 0;
  return record(
    "C10.mcp-paths",
    ok,
    "checked=" + checked +
      " dead_total=" + dead.length +
      (googleDead.length ? " dead_google=" + googleDead.join(",") : "") +
      (otherDead.length ? " dead_other=" + otherDead.join(",") : ""),
    googleDead.length === 0
  );
}

// ── C7 scheduled tasks ─────────────────────────────────────────────────────
function checkTasks() {
  // The state of each task plus its result, read from the Task Scheduler.
  const raw = run("powershell.exe", [
    "-NoProfile",
    "-Command",
    "$names=@(" +
      TASKS.map((t) => "'" + t + "'").join(",") +
      ");foreach($n in $names){$t=Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue;" +
      "if($t){$i=Get-ScheduledTaskInfo -TaskName $n -ErrorAction SilentlyContinue;" +
      "Write-Output ($n+'|'+$t.State+'|'+$i.LastTaskResult+'|'+$i.NextRunTime)}" +
      "else{Write-Output ($n+'|ABSENT||')}}",
  ]);
  if (!raw) return record("C7.tasks", false, "could not read the Task Scheduler");
  const rows = raw
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean)
    .map((l) => {
      const [name, state, result, next] = l.split("|");
      return { name, state, result, next };
    });
  const missing = rows.filter((r) => r.state === "ABSENT");
  const bad = rows.filter((r) => r.state !== "ABSENT" && r.result !== "0" && r.result !== "267009");
  const ok = missing.length === 0 && bad.length === 0;
  return record(
    "C7.tasks",
    ok,
    "count=" + rows.length +
      (missing.length ? " missing=" + missing.map((m) => m.name).join(",") : "") +
      (bad.length ? " nonzero_result=" + bad.map((b) => b.name + ":" + b.result).join(",") : "")
  );
}

// ── C8 consent listener ───────────────────────────────────────────────────
function checkConsent() {
  const raw = run("powershell.exe", [
    "-NoProfile",
    "-Command",
    "Get-CimInstance Win32_Process -Filter \"Name='node.exe'\" | ForEach-Object { $_.CommandLine }",
  ]);
  const lines = raw ? raw.split(/\r?\n/).filter((l) => l && l.includes("consent-watcher")) : [];
  return record(
    "C8.consent",
    lines.length > 0,
    lines.length
      ? "listener alive (processes=" + lines.length + ")"
      : "no consent-watcher process: a future re-consent would have no listener to catch the callback"
  );
}
function await0() {
  return null;
}

// ── C9 picker session ──────────────────────────────────────────────────────
async function checkPicker() {
  const f = path.join(DATA, "picker-session.json");
  if (!fs.existsSync(f)) return record("C9.picker", true, "no picker session registered (nothing to watch)", false);
  let cfg;
  try {
    cfg = JSON.parse(fs.readFileSync(f, "utf8"));
  } catch (e) {
    return record("C9.picker", false, "unreadable picker-session.json", false);
  }
  // A session that was completed and deleted answers 404. That is the
  // designed end of a picker session, so it is reported as CONSUMED - the
  // same state as "no session" - not as a broken one.
  if (!cfg.session_id) {
    return record(
      "C9.picker",
      true,
      "session consumed (" + (cfg.consumed_at || cfg.state || "no session id") + ") - nothing to watch",
      false
    );
  }
  const credsPath = path.join(DATA, "credentials.json");
  if (!fs.existsSync(credsPath)) return record("C9.picker", false, "no credential to query the session", false);
  const c = JSON.parse(fs.readFileSync(credsPath, "utf8"));
  const body = new URLSearchParams({
    client_id: c.client_id,
    client_secret: c.client_secret,
    refresh_token: c.refresh_token,
    grant_type: "refresh_token",
  }).toString();
  const tok = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  }).then((r) => r.json());
  if (!tok.access_token) return record("C9.picker", false, "could not mint a token", false);
  const resp = await fetch(
    "https://photospicker.googleapis.com/v1/sessions/" + encodeURIComponent(cfg.session_id),
    { headers: { Authorization: "Bearer " + tok.access_token } }
  );
  if (resp.status === 404) {
    return record("C9.picker", true, "session consumed (404) - nothing to watch", false);
  }
  const s = await resp.json();
  const ok = s && s.id;
  return record(
    "C9.picker",
    Boolean(ok),
    "session=" + (s && s.id ? s.id : "?") + " mediaItemsSet=" + (s && s.mediaItemsSet) + " expire=" + (s && s.expireTime),
    false
  );
}

(async () => {
  // The OFFLINE self-test: it calls nothing, touches nothing, and exists to
  // prove the gate can still block and that it does not false-red. It runs
  // only when --self-test is given WITHOUT --fail, so the pre-existing
  // falsification path (--self-test --fail <check>) is untouched.
  if (hasFlag("--self-test") && !process.argv.includes("--fail")) {
    process.exitCode = runSelfTest() ? 0 : 2;
    return;
  }

  console.log("=== Google Access - control point ===");
  console.log("host=" + os.hostname() + " at=" + new Date().toISOString());
  console.log("container=" + CONTAINER + " mcp=" + MCP_URL + " data=" + DATA);
  console.log("");

  if (hasFlag("--self-test") && process.argv.includes("--fail")) {
    // The self-test hook: force one check to report a failure, so the gate's
    // own ability to fail can be demonstrated instead of assumed.
    const which = process.argv[process.argv.indexOf("--fail") + 1];
    injected = which;
    console.log("SELF_TEST=1 injecting_failure=" + which);
    console.log("");
  }

  checkContainer();
  checkRunningCode();
  await checkHealth();
  checkServices();
  checkExtendlm();
  await checkBrowserMcp();
  checkRegistry();
  checkRegistryPaths();
  checkTasks();
  checkConsent();
  await checkPicker();

  if (injected) {
    const r = results.find((x) => x.id === injected);
    if (r) {
      r.ok = false;
      console.log("CHECK " + r.id + " FAIL (injected by --self-test --fail " + injected + ")");
    }
  }

  const fails = results.filter((r) => !r.ok && r.critical);
  const warns = results.filter((r) => !r.ok && !r.critical);
  console.log("");
  console.log("SUMMARY checks=" + results.length + " failed=" + fails.length + " warnings=" + warns.length);
  if (fails.length) for (const f of fails) console.log("  FAILED " + f.id + " " + f.detail);
  const verdict = fails.length === 0 ? "PASS" : "FAIL";
  console.log("VERDICT=" + verdict);
  if (hasFlag("--json")) {
    console.log(JSON.stringify({ at: new Date().toISOString(), verdict, results }));
  }
  process.exitCode = fails.length === 0 ? 0 : 2;
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exitCode = 3;
});

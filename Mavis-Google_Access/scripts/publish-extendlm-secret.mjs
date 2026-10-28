// publish-extendlm-secret.mjs - the owner side of the ExtendLM token.
//
// MEASURED 2026-10-27: the ExtendLM token endpoint ROTATES the refresh token.
// Two instances that refresh from the same copy destroy each other: the second
// rotation invalidates the token the first one just stored. So exactly one
// instance owns the token - this host - and every other instance (the Cloud
// runner) only ever consumes a snapshot, with GA_EXTENDLM_NO_REFRESH=1.
//
// This script is that owner. It:
//   1. rotates the token ONLY when the current one is close to expiry, so it
//      does not fight the container for the same refresh token (the container
//      also refreshes, and it persists what it gets),
//   2. publishes the fresh snapshot to the Cloud as a repository secret,
//   3. verifies the secret was actually written by reading its timestamp back.
//
// It never prints a token. It prints lengths, labels and HTTP statuses only.
//
// Usage: node publish-extendlm-secret.mjs [--data <dir>] [--repo <owner/name>]
//                                              [--min-valid-minutes <n>]
//                                              [--skip-refresh] [--dry-run]
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const argOf = (flag, dflt) => {
  const i = process.argv.indexOf(flag);
  return i !== -1 ? process.argv[i + 1] : dflt;
};
const hasFlag = (flag) => process.argv.includes(flag);

const DATA_DIR = argOf("--data", "C:/Users/apviz/.minimax/google-access/data");
const REPO = argOf("--repo", "apvizual-max/MAVIS-CLOUD");
const SECRET_NAME = "GOOGLE_EXTENDLM_CREDENTIAL_B64";
const CFG = path.join(DATA_DIR, "extendlm.json");
const MIN_VALID_MINUTES = Number(argOf("--min-valid-minutes", "60"));

function ghBin() {
  const candidates = [
    process.env.GH_PATH,
    "C:/Program Files/GitHub CLI/gh.exe",
    "C:/Program Files (x86)/GitHub CLI/gh.exe",
  ].filter(Boolean);
  for (const c of candidates) {
    try {
      fs.accessSync(c);
      return c;
    } catch {
      /* try the next one */
    }
  }
  return "gh"; // PATH lookup
}

function gh(args, opts) {
  return execFileSync(ghBin(), args, Object.assign({ encoding: "utf8", windowsHide: true }, opts || {}));
}

function readCfg() {
  try {
    return JSON.parse(fs.readFileSync(CFG, "utf8"));
  } catch {
    return null;
  }
}

function persist(next) {
  const tmp = CFG + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(next, null, 2), "utf8");
  fs.renameSync(tmp, CFG);
}

function minutesLeft(cfg) {
  if (!cfg || !cfg.expires_at) return null;
  return (Number(cfg.expires_at) - Date.now()) / 60000;
}

async function refresh(cfg) {
  const res = await fetch(cfg.token_endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: cfg.refresh_token,
      client_id: cfg.client_id,
    }).toString(),
  });
  const text = await res.text();
  console.log("REFRESH_HTTP=" + res.status);
  if (!res.ok) {
    console.log("REFRESH_BODY=" + text.slice(0, 300));
    return null;
  }
  const j = JSON.parse(text);
  const rotated = Boolean(j.refresh_token && j.refresh_token !== cfg.refresh_token);
  const now = Date.now();
  const next = {
    ...cfg,
    token: j.access_token,
    access_token: j.access_token,
    refresh_token: j.refresh_token || cfg.refresh_token,
    token_type: j.token_type || cfg.token_type || "Bearer",
    scope: j.scope || cfg.scope,
    expires_at: j.expires_in ? now + Number(j.expires_in) * 1000 : null,
    refreshed_at: new Date(now).toISOString(),
  };
  persist(next);
  console.log(
    "TOKEN_LEN=" + (next.token ? next.token.length : 0) +
      " ROTATED_REFRESH=" + (rotated ? 1 : 0) +
      " EXPIRES_AT=" + (next.expires_at ? new Date(next.expires_at).toISOString() : "none")
  );
  return next;
}

(async () => {
  if (!fs.existsSync(CFG)) {
    console.log("NO_CREDENTIAL_FILE=" + CFG);
    process.exitCode = 3;
    return;
  }
  let cfg = readCfg();
  console.log(
    "BEFORE token_len=" + (cfg && cfg.token ? cfg.token.length : 0) +
      " refresh_len=" + (cfg && cfg.refresh_token ? cfg.refresh_token.length : 0) +
      " minutes_left=" + (minutesLeft(cfg) === null ? "unknown" : Math.round(minutesLeft(cfg)))
  );

  if (hasFlag("--skip-refresh")) {
    console.log("REFRESH=skipped");
  } else {
    const left = minutesLeft(cfg);
    // Rotate only when it is needed. Rotating on every pass would fight the
    // container over the same refresh token for no benefit: both persist what
    // they get, so the file always holds a valid one, but the churn is free
    // risk and free rotation.
    if (left !== null && left > MIN_VALID_MINUTES) {
      console.log("REFRESH=skipped token_valid_for=" + Math.round(left) + "min threshold=" + MIN_VALID_MINUTES + "min");
    } else if (!cfg.refresh_token) {
      console.log("NO_REFRESH_TOKEN: re-authorize with extendlm-provision.mjs");
      process.exitCode = 3;
      return;
    } else {
      const next = await refresh(cfg);
      if (next) {
        cfg = next;
      } else {
        // The container may have rotated the token between our read and our
        // refresh. Re-read the file: if it now holds a usable token, publish
        // THAT. A failed rotation is not a reason to publish a dead snapshot.
        const fresh = readCfg();
        const freshLeft = minutesLeft(fresh);
        if (fresh && freshLeft !== null && freshLeft > 0) {
          console.log("RECOVERED_FROM_FILE minutes_left=" + Math.round(freshLeft));
          cfg = fresh;
        } else {
          console.log("VERDICT=REFRESH_FAILED");
          process.exitCode = 2;
          return;
        }
      }
    }
  }

  const bytes = fs.readFileSync(CFG);
  const b64 = Buffer.from(bytes).toString("base64");
  console.log("SNAPSHOT_BYTES=" + bytes.length + " B64_LEN=" + b64.length);

  if (hasFlag("--dry-run")) {
    console.log("DRY_RUN=1 (secret not written)");
    console.log("VERDICT=DRY_RUN_OK");
    return;
  }

  try {
    gh(["secret", "set", SECRET_NAME, "--repo", REPO, "--body", b64]);
    console.log("SECRET_WRITE=ok name=" + SECRET_NAME + " repo=" + REPO);
  } catch (e) {
    // MEASURED 2026-10-27: gh echoes the failing command line, and the command
    // line carries --body <the snapshot>. The snapshot contains the access
    // token and the refresh token, so the raw message would write a live
    // credential into a log file. The payload is redacted before it is
    // printed; the failure itself is reported.
    const raw = e && e.message ? String(e.message) : String(e);
    const safe = raw.split(b64).join("[REDACTED_SNAPSHOT]");
    console.log("SECRET_WRITE=error " + safe.split("\n")[0]);
    console.log("VERDICT=SECRET_WRITE_FAILED");
    process.exitCode = 2;
    return;
  }

  // A write that was not confirmed is not a write. Read the timestamp back.
  let verdict = "VERDICT=PUBLISHED";
  try {
    const raw = gh(["secret", "list", "--repo", REPO, "--json", "name,updatedAt"], { stdio: ["ignore", "pipe", "pipe"] });
    const list = JSON.parse(raw);
    const row = list.find((r) => r.name === SECRET_NAME);
    if (!row) {
      console.log("SECRET_READBACK=absent");
      verdict = "VERDICT=SECRET_ABSENT_AFTER_WRITE";
    } else {
      const age = (Date.now() - Date.parse(row.updatedAt)) / 1000;
      console.log("SECRET_READBACK=present updatedAt=" + row.updatedAt + " age_seconds=" + Math.round(age));
      if (age > 300) {
        console.log("SECRET_READBACK=stale (older than 300s)");
        verdict = "VERDICT=SECRET_STALE_AFTER_WRITE";
      }
    }
  } catch (e) {
    console.log("SECRET_READBACK=error " + (e && e.message ? String(e.message).split("\n")[0] : String(e)));
    verdict = "VERDICT=READBACK_FAILED";
  }
  console.log(verdict);
  if (verdict !== "VERDICT=PUBLISHED") process.exitCode = 2;
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exitCode = 2;
});

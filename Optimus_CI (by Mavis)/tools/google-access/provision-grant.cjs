// provision-grant.cjs - host side.
//
// Two jobs:
//   1. default: find a LIVE Google grant on this machine (same mechanism as
//      google-layer/google-grant.js) and publish it into the Google_Access
//      container's persistent volume.
//   2. --from-code <code> [--client live|secrets]: exchange a widening
//      consent code for tokens and publish them. This is the ONE click that
//      widens the credential to every Google API scope.
//
// It NEVER prints a token: only labels, lengths and HTTP statuses.
"use strict";
const fs = require("node:fs");
const path = require("node:path");


// MEASURED DEFECT 2026-10-27: the module path was a hardcoded absolute
// path to a folder that later moved. The consent exchange died with
// MODULE_NOT_FOUND AFTER the human had already clicked Allow - the click is
// the expensive part, so the path must not be a second source of truth.
// Resolution order: explicit override, next to this script, then the known
// project roots. A miss is a loud exit 7 with the searched list, never a
// stack trace that reads like a crash.
const LAYER_CANDIDATES = [
  process.env.GA_LAYER_DIR,
  path.join(__dirname, "google-layer"),
  path.join(__dirname, "..", "google-layer"),
  "C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Google_Access\\google-layer",
  "C:\\Users\\apviz\\.minimax-agent\\projects\\google-layer",
].filter(Boolean);

let grant = null;
let grantPath = "";
for (const dir of LAYER_CANDIDATES) {
  const candidate = path.join(dir, "google-grant.js");
  if (!fs.existsSync(candidate)) continue;
  grant = require(candidate);
  grantPath = candidate;
  break;
}
if (!grant) {
  console.error("ERROR=google-grant.js not found");
  console.error("SEARCHED=" + LAYER_CANDIDATES.join(" | "));
  console.error("FIX=set GA_LAYER_DIR, or place google-layer/google-grant.js next to this script");
  process.exit(7);
}
console.log("GRANT_MODULE=" + grantPath);

const DATA_DIR = "C:\\Users\\apviz\\.minimax\\google-access\\data";
const OUT = path.join(DATA_DIR, "credentials.json");
const SECRETS_DIR = "E:\\--- System Secrets";
const OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token";

function readJson(p) {
  try {
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

function secretClient() {
  let files = [];
  try {
    files = fs.readdirSync(SECRETS_DIR);
  } catch {
    return null;
  }
  for (const f of files) {
    if (!/client_secret.*\.json$/i.test(f)) continue;
    const j = readJson(path.join(SECRETS_DIR, f));
    if (!j) continue;
    const sec = j.web || j.installed || {};
    if (sec.client_id && sec.client_secret) {
      return { file: f, client_id: sec.client_id, client_secret: sec.client_secret };
    }
  }
  return null;
}

function publish(obj) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(obj, null, 2), "utf8");
  console.log("WROTE=" + OUT + " bytes=" + fs.statSync(OUT).size);
}

async function exchangeCode(code, clientId, clientSecret, redirectUri) {
  const body = new URLSearchParams({
    client_id: clientId,
    client_secret: clientSecret,
    code,
    grant_type: "authorization_code",
    redirect_uri: redirectUri,
  });
  const res = await fetch(OAUTH_TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  const json = await res.json().catch(() => ({}));
  return { status: res.status, json };
}

(async () => {
  const argv = process.argv.slice(2);
  const codeIdx = argv.indexOf("--from-code");
  const clientIdx = argv.indexOf("--client");
  const redirectIdx = argv.indexOf("--redirect-uri");
  // The redirect_uri sent to the token endpoint MUST be identical to the one
  // used in the authorization request. A consent made for http://localhost
  // exchanged as urn:ietf:wg:oauth:2.0:oob fails with redirect_uri_mismatch.
  const redirectUri = redirectIdx !== -1 ? argv[redirectIdx + 1] : "urn:ietf:wg:oauth:2.0:oob";

  if (codeIdx !== -1) {
    const code = argv[codeIdx + 1];
    const which = clientIdx !== -1 ? argv[clientIdx + 1] : "secrets";
    if (!code) {
      console.log("ERROR=missing code after --from-code");
      process.exit(2);
    }
    let clientId, clientSecret, label;
    if (which === "container") {
      // The credential the container itself uses. Its client_id is exactly the
      // one the consent URL was built with, so the code exchange cannot
      // mismatch clients - and its secret is the one that issued the code.
      const c = readJson(OUT);
      if (!c || !c.client_id || !c.client_secret) {
        console.log("ERROR=no credential in " + OUT);
        process.exit(3);
      }
      clientId = c.client_id;
      clientSecret = c.client_secret;
      label = "container:" + c.client_id.slice(0, 28);
    } else if (which === "secrets") {
      const sc = secretClient();
      if (!sc) {
        console.log("ERROR=no client secret found under " + SECRETS_DIR);
        process.exit(3);
      }
      clientId = sc.client_id;
      clientSecret = sc.client_secret;
      label = "secrets:" + sc.file;
    } else {
      const live = await grant.findLiveGrant(null);
      if (!live) {
        console.log("ERROR=no live grant on this machine");
        process.exit(3);
      }
      clientId = live.clientId;
      clientSecret = live.clientSecret;
      label = "live:" + live.label;
    }
    const ex = await exchangeCode(code, clientId, clientSecret, redirectUri);
    console.log("TOKEN_ENDPOINT_HTTP=" + ex.status);
    if (ex.status !== 200 || !ex.json.access_token) {
      console.log("ERROR=" + (ex.json.error || "unknown") + " " + (ex.json.error_description || ""));
      console.log("NO_CHANGE=1 (the stored credential is untouched)");
      process.exit(4);
    }
    const refresh = ex.json.refresh_token;
    if (!refresh) {
      console.log("ERROR=no refresh_token returned - the code was probably already used");
      process.exit(5);
    }
    // verify the new refresh token against the endpoint
    const probe = await grant.exchange(clientId, clientSecret, refresh);
    console.log("REFRESH_PROBE_HTTP=" + probe.status + " expires_in=" + (probe.json.expires_in || "-"));
    publish({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refresh,
      scope: probe.json.scope || "",
      provisioned_at: new Date().toISOString(),
      source: label + " (widened consent)",
    });
    console.log("SCOPES=" + (probe.json.scope || ""));
    console.log("PERMANENT=1 (refresh token persists in the mounted volume; no consent needed again)");
    return;
  }

  console.log("=== candidates ===");
  const cands = grant.findCandidates();
  for (const c of cands) {
    const ex = await grant.exchange(c.clientId, c.clientSecret, c.refreshToken);
    const ok = ex.status === 200 && !!ex.json.access_token;
    console.log(
      (ok ? "LIVE " : "DEAD ") +
        c.label +
        " | client_id=" + c.clientId.slice(0, 28) +
        " | http=" + ex.status +
        " | " + (ex.json.error || "expires_in=" + ex.json.expires_in)
    );
  }

  const live = await grant.findLiveGrant((l) => console.log("  " + l));
  if (!live) {
    console.log("NO_LIVE_GRANT=1 -> re-consent is required (ACCESS)");
    process.exit(3);
  }
  console.log("LIVE_GRANT=1 client_id=" + live.clientId);
  console.log("LIVE_SCOPE=" + (live.scope || "(none reported)"));

  const sc = secretClient();
  if (sc) {
    console.log("SECRETS_CLIENT=" + sc.file + " client_id=" + sc.client_id + " MATCHES_LIVE=" + (sc.client_id === live.clientId));
  }

  publish({
    client_id: live.clientId,
    client_secret: live.clientSecret,
    refresh_token: live.refreshToken,
    scope: live.scope || "",
    provisioned_at: new Date().toISOString(),
    source: live.label,
  });
  console.log("SECRETS_IN_IMAGE=none (credential lives in the mounted volume only)");
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exit(4);
});

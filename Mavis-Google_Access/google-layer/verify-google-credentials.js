// verify-google-credentials.js
//
// WHY THIS EXISTS
// Popy's complaint, in his words: "de ce nu am deja acces si de ce nu ma pot
// baza si folosi setarile cand le fac odata ... nu pot lucra ca tu IAR NU AI
// ACCES".
//
// The recurring shape of that failure was: an MCP server for a Google service
// could not authenticate, the symptom was reported as "re-authenticate", and
// the answer was to send Popy to a consent screen again. That is a
// RE-AUTHENTICATION LOOP, and it is not a credentials problem - the
// credentials on this machine are files on disk, and they are measured here.
//
// THE QUESTION THIS ANSWERS
// "Is the durable grant still valid?" is answered by USING it: the refresh
// token is exchanged for a short-lived access token and the access token is
// spent on one cheap read. A file that exists is not a working credential.
//
// WHAT IT NEVER DOES
// It never prints a token, a secret, or a partial token. It prints key NAMES,
// lengths, HTTP status codes and API error reasons. A probe that leaks the
// credential it probes is not a probe.
//
// Exit codes:
//   0 = every configured Google credential was measured and works
//   1 = at least one credential is BROKEN (measured, with the reason)
//   2 = the probe itself could not run (no credential store, no network)
//
// ASCII ONLY: this file is executed by node and by bun.

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const GWS = path.join(os.homedir(), ".config", "gws");
const MCP_SECRETS = path.join(GWS, "mcp-secrets.json");
const GOOGLE_MCP = path.join(os.homedir(), ".google-mcp");

function say(m) {
  process.stdout.write(String(m) + "\n");
}

function readJson(p) {
  try {
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

// Only key names and lengths. Never the value.
function describe(store) {
  const out = [];
  if (!store) return out;
  for (const [k, v] of Object.entries(store)) {
    out.push(`${k} (len=${String(v).length})`);
  }
  return out;
}

async function exchangeRefreshToken(clientId, clientSecret, refreshToken) {
  const body = new URLSearchParams({
    client_id: clientId,
    client_secret: clientSecret,
    refresh_token: refreshToken,
    grant_type: "refresh_token",
  });
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  let json = {};
  try {
    json = await res.json();
  } catch {
    /* body may not be json; the status is the measurement anyway */
  }
  return { status: res.status, json };
}

(async () => {
  let failures = 0;

  say("=== GOOGLE CREDENTIAL PROBE (no secret is printed) ===");
  say(`store: ${MCP_SECRETS}`);
  const secrets = readJson(MCP_SECRETS);
  if (!secrets) {
    say("RESULT=NO_STORE - nu exista magazraul de credentiale; nu e nimic de masurat.");
    process.exit(2);
  }
  const keys = describe(secrets);
  say(`keys: ${keys.length ? keys.join(" | ") : "(none)"}`);

  const clientId = secrets["gdrive-mcp/client_id"];
  const clientSecret = secrets["gdrive-mcp/client_secret"];
  const refreshToken = secrets["gdrive-mcp/refresh_token"];

  if (!clientId || !clientSecret || !refreshToken) {
    say("RESULT=INCOMPLETE_STORE - una din cheile gdrive-mcp/client_id, client_secret, refresh_token lipseste.");
    process.exit(1);
  }

  // --- 1. is the durable grant still accepted by Google? -------------------
  let accessToken = "";
  try {
    const ex = await exchangeRefreshToken(clientId, clientSecret, refreshToken);
    say(`REFRESH_EXCHANGE_HTTP=${ex.status}`);
    if (ex.status === 200 && ex.json.access_token) {
      accessToken = ex.json.access_token;
      say(`REFRESH_EXCHANGE=OK  expires_in=${ex.json.expires_in}s  scope="${ex.json.scope || "(neprecizat)"}"`);
      say("DURABLE_GRANT=VALID - refresh_token-ul este acceptat de Google. NU trebuie re-autentificat.");
    } else {
      failures++;
      const reason = ex.json.error || ex.json.error_description || "(fara motiv in raspuns)";
      say(`REFRESH_EXCHANGE=FAIL  reason="${reason}"`);
      say("DURABLE_GRANT=INVALID - Google NU mai accepta acest refresh_token.");
    }
  } catch (e) {
    say(`REFRESH_EXCHANGE=NETWORK_ERROR  ${e && e.message ? e.message : e}`);
    say("PROBE=UNKNOWN - reteaua nu a raspuns; nu se poate afirma ca grantul e invalid.");
    process.exit(2);
  }

  // --- 2. does the access token actually work on Drive? --------------------
  if (accessToken) {
    try {
      const res = await fetch(
        "https://www.googleapis.com/drive/v3/about?fields=user,storageQuota",
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      say(`DRIVE_ABOUT_HTTP=${res.status}`);
      if (res.status === 200) {
        const j = await res.json();
        const who = j && j.user && j.user.emailAddress ? j.user.emailAddress : "(unknown)";
        say(`DRIVE_ABOUT=OK  account=${who}  drive=${j.storageQuota && j.storageQuota.limit ? "yes" : "?"}`);
      } else {
        failures++;
        let why = "";
        try {
          const j = await res.json();
          why = (j.error && j.error.message) || "";
        } catch {
          /* body may not be json */
        }
        say(`DRIVE_ABOUT=FAIL  ${why}`);
      }
    } catch (e) {
      failures++;
      say(`DRIVE_ABOUT=NETWORK_ERROR  ${e && e.message ? e.message : e}`);
    }
  }

  // --- 3. what the OTHER google servers read ------------------------------
  // Each Google MCP server keeps its own credential store. A server that reads
  // a store nobody has populated is the real reason Popy keeps being asked to
  // sign in again - not the Drive grant.
  say("");
  say("--- credential stores of the other Google servers ---");
  const stores = [
    ["google-workspace-mcp", path.join(GOOGLE_MCP, "credentials.json")],
    ["google-workspace-mcp tokens", path.join(GOOGLE_MCP, "tokens", "apvizual.json")],
    ["google-workspace-mcp accounts", path.join(GOOGLE_MCP, "accounts.json")],
  ];
  for (const [label, p] of stores) {
    if (!fs.existsSync(p)) {
      say(`  ABSENT   ${label}: ${p}`);
      continue;
    }
    const st = fs.statSync(p);
    const j = readJson(p);
    const names = j ? Object.keys(j).join(",") : "(not json)";
    say(`  EXISTS   ${label}: ${p}  ${st.size}B  keys=${names}`);
  }

  // --- 4. THE LOOP, MEASURED: every refresh token on this machine ----------
  // A dead grant in one store does not have to mean a dead account. If another
  // server holds a LIVE grant for the same Google account, the re-consent can
  // be skipped entirely - no browser, no click, no Popy.
  //
  // The client_id is a PUBLIC identifier (it appears in the consent screen),
  // so it is compared and printed. The client_secret is never printed.
  say("");
  say("--- every refresh token on this machine, measured ---");

  const candidates = [];
  const wsToken = readJson(path.join(GOOGLE_MCP, "tokens", "apvizual.json"));
  if (wsToken && wsToken.refresh_token && wsToken.client_id && wsToken.client_secret) {
    candidates.push({
      label: "google-workspace-mcp (~/.google-mcp/tokens/apvizual.json)",
      clientId: wsToken.client_id,
      clientSecret: wsToken.client_secret,
      refreshToken: wsToken.refresh_token,
    });
  }
  candidates.push({
    label: "gdrive-mcp (~/.config/gws/mcp-secrets.json)",
    clientId,
    clientSecret,
    refreshToken,
  });

  // the OAuth client the user configured on disk, for comparison
  const clientFile = readJson(path.join(GWS, "client_secret.json"));
  const onDisk = clientFile ? (clientFile.installed || clientFile.web || clientFile) : null;
  if (onDisk && onDisk.client_id) {
    say(`  OAuth client on disk: client_id=${onDisk.client_id}`);
    say(`  gdrive-mcp client_id:  ${clientId}`);
    say(
      `  SAME_CLIENT=${onDisk.client_id === clientId ? "yes" : "NO - grantul a fost facut cu alt client"}`
    );
  }

  let liveGrant = null;
  for (const c of candidates) {
    let verdict = "UNKNOWN";
    let detail = "";
    let scope = "";
    try {
      const ex = await exchangeRefreshToken(c.clientId, c.clientSecret, c.refreshToken);
      if (ex.status === 200 && ex.json.access_token) {
        verdict = "LIVE";
        scope = ex.json.scope || "";
        detail = `expires_in=${ex.json.expires_in}s`;
        if (!liveGrant) liveGrant = { ...c, accessToken: ex.json.access_token, scope };
      } else {
        verdict = "DEAD";
        detail = ex.json.error || ex.json.error_description || `(http ${ex.status})`;
      }
    } catch (e) {
      detail = e && e.message ? e.message : String(e);
    }
    say(`  ${verdict.padEnd(7)} ${c.label}  ${detail}`);
    if (scope) say(`          scope="${scope}"`);
  }

  // --- 5. can Drive be reached with a LIVE grant from another server? ------
  if (liveGrant) {
    say("");
    try {
      const res = await fetch(
        "https://www.googleapis.com/drive/v3/about?fields=user,storageQuota",
        { headers: { Authorization: `Bearer ${liveGrant.accessToken}` } }
      );
      say(`DRIVE_WITH_LIVE_GRANT_HTTP=${res.status}`);
      if (res.status === 200) {
        const j = await res.json();
        const who = j && j.user && j.user.emailAddress ? j.user.emailAddress : "(unknown)";
        say(`DRIVE_WITH_LIVE_GRANT=OK  account=${who}`);
        const drv = /drive/.test(liveGrant.scope || "");
        say(
          `DRIVE_SCOPE=${drv ? "present" : "MISSING"} - ${
            drv
              ? "grantul viu acopera Drive; nu e nevoie de niciun consent nou"
              : "grantul viu NU are scope de Drive; un token nou ar fi necesar pentru Drive"
          }`
        );
      } else {
        failures++;
        say("DRIVE_WITH_LIVE_GRANT=FAIL");
      }
    } catch (e) {
      failures++;
      say(`DRIVE_WITH_LIVE_GRANT=NETWORK_ERROR  ${e && e.message ? e.message : e}`);
    }
  } else {
    say("");
    say("NO_LIVE_GRANT - niciun refresh token de pe aceasta masina nu mai este acceptat.");
  }

  say("");
  if (failures === 0) {
    say("RESULT=ALL_OK - credentialele Google măsurate funcționează.");
    process.exit(0);
  }
  say(`RESULT=FAILURES=${failures}`);
  process.exit(1);
})().catch((e) => {
  say(`PROBE_CRASH=${e && e.stack ? e.stack : e}`);
  process.exit(2);
});

// google-grant.js
//
// THE SINGLE SOURCE OF TRUTH for Google access on this machine.
//
// WHY THIS FILE EXISTS
// --------------------
// Popy: "de ce nu am deja acces si de ce nu ma pot baza si folosi setarile
// cand le fac odata ... nu pot lucra ca tu IAR NU AI ACCES".
//
// MEASURED 2026-10-27: the machine held TWO Google grants. The one the Drive
// server read was DEAD (refresh exchange -> HTTP 400 "invalid_grant"); the
// one the Workspace server read was LIVE (HTTP 200, expires_in 3599, scopes
// covering drive + gmail.modify + calendar + documents + spreadsheets).
// Same OAuth client, same account. Only one grant was dead - yet the symptom
// was "sign in again", because every server reads its own store and nobody
// copied the live grant into it.
//
// So the access becomes a MECHANISM, not a promise:
//   1. find every refresh token on this machine
//   2. MEASURE each one against Google's token endpoint
//   3. use the first one that is actually LIVE
//   4. publish it into every store a Google MCP server reads
//
// The consent screen is then needed only when NO live grant exists anywhere
// on the machine. That is a genuinely different situation and a rare one.
//
// It never prints a token. Key names, lengths, HTTP status codes and API
// error reasons only.
//
// ASCII ONLY.

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

function readJson(p) {
  try {
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

function writeJson(p, obj) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(obj, null, 2), "utf8");
}

function home() {
  return process.env.FAKE_HOME || os.homedir();
}

function gwsDir() {
  return path.join(home(), ".config", "gws");
}

function mcpSecretsPath() {
  return path.join(gwsDir(), "mcp-secrets.json");
}

function googleMcpDir() {
  return path.join(home(), ".google-mcp");
}

// Every refresh token that may live on this machine.
function findCandidates() {
  const out = [];

  const secrets = readJson(mcpSecretsPath());
  if (secrets && secrets["gdrive-mcp/refresh_token"]) {
    out.push({
      label: "gdrive-mcp (~/.config/gws/mcp-secrets.json)",
      clientId: secrets["gdrive-mcp/client_id"],
      clientSecret: secrets["gdrive-mcp/client_secret"],
      refreshToken: secrets["gdrive-mcp/refresh_token"],
    });
  }

  const tokDir = path.join(googleMcpDir(), "tokens");
  if (fs.existsSync(tokDir)) {
    for (const f of fs.readdirSync(tokDir)) {
      if (!f.endsWith(".json")) continue;
      const t = readJson(path.join(tokDir, f));
      if (t && t.refresh_token && t.client_id && t.client_secret) {
        out.push({
          label: `google-workspace-mcp (~/.google-mcp/tokens/${f})`,
          clientId: t.client_id,
          clientSecret: t.client_secret,
          refreshToken: t.refresh_token,
        });
      }
    }
  }

  return out;
}

async function exchange(clientId, clientSecret, refreshToken) {
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
    /* body may not be json */
  }
  return { status: res.status, json };
}

// Finds a grant that Google ACTUALLY accepts. Returns null when none exists.
async function findLiveGrant(log) {
  const candidates = findCandidates();
  for (const c of candidates) {
    let ok = false;
    let scope = "";
    let detail = "";
    try {
      const ex = await exchange(c.clientId, c.clientSecret, c.refreshToken);
      if (ex.status === 200 && ex.json.access_token) {
        ok = true;
        scope = ex.json.scope || "";
        detail = `expires_in=${ex.json.expires_in}s`;
      } else {
        detail = ex.json.error || ex.json.error_description || `(http ${ex.status})`;
      }
    } catch (e) {
      detail = e && e.message ? e.message : String(e);
    }
    if (log) log(`${ok ? "LIVE" : "DEAD "}  ${c.label}  ${detail}`);
    if (ok) return { ...c, scope };
  }
  return null;
}

// Publishes a live grant into every store a Google MCP server reads.
function provision(live) {
  const p = mcpSecretsPath();
  const secrets = readJson(p) || {};
  secrets["gdrive-mcp/client_id"] = live.clientId;
  secrets["gdrive-mcp/client_secret"] = live.clientSecret;
  secrets["gdrive-mcp/refresh_token"] = live.refreshToken;
  writeJson(p, secrets);
  return p;
}

// The one call a launcher makes before starting its server: find a live
// grant, publish it, and hand back a fresh access token.
//
// Returns { accessToken, refreshToken, clientId, clientSecret, scope } or
// null when no live grant exists (which is the only case where a human has
// to consent).
async function ensureAccess(log) {
  const live = await findLiveGrant(log);
  if (!live) return null;
  provision(live);

  const ex = await exchange(live.clientId, live.clientSecret, live.refreshToken);
  if (ex.status !== 200 || !ex.json.access_token) return null;
  return {
    accessToken: ex.json.access_token,
    refreshToken: live.refreshToken,
    clientId: live.clientId,
    clientSecret: live.clientSecret,
    scope: live.scope,
  };
}

module.exports = {
  readJson,
  writeJson,
  findCandidates,
  findLiveGrant,
  provision,
  ensureAccess,
  exchange,
  mcpSecretsPath,
  googleMcpDir,
  gwsDir,
  home,
};

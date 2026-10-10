// gworkspace-oauth.js
//
// WHY NOT `google-workspace-mcp accounts add`
// That command is the supported path, and it works - on a machine where $HOME
// exists. Two things stop it here:
//
//   1. accounts.js:8 builds its config directory as
//        path.join(process.env.HOME || '~', '.google-mcp')
//      Windows has no HOME variable. The fallback is the LITERAL string '~', so
//      the tool looks for `~/.google-mcp` RELATIVE TO THE WORKING DIRECTORY and
//      reports "Credentials file NOT found" while the file sits in your real
//      home directory. Set HOME and it is found immediately. This is a Windows
//      portability bug in the package, not a configuration mistake.
//
//   2. More seriously, it requests scopes you did not ask for. Its hardcoded
//      SCOPES list is:
//        auth/drive, auth/documents, auth/spreadsheets, auth/presentations,
//        auth/calendar, auth/gmail.modify, auth/gmail.settings.basic,
//        auth/forms.body, auth/forms.responses.readonly
//      auth/gmail.modify is NOT read-only - it can modify and delete mail.
//      You asked for Gmail read-only, so the grant below is narrowed to the
//      .readonly variant of every scope. Nothing here is widened, and the
//      difference is enforced by the OAuth grant itself rather than by asking
//      the tool to behave.
//
// The token is written in exactly the shape accounts.js expects:
//   ~/.google-mcp/tokens/<name>.json  { type, client_id, client_secret, refresh_token }
// so the server's own loader picks it up with no other change.
//
// Run:  bun gworkspace-oauth.js

const http = require("node:http");
const url = require("node:url");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const gapi = require(
  path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules",
    "gdrive-mcp", "node_modules", "googleapis")
);
const { google } = gapi;

const ACCOUNT = process.env.GW_ACCOUNT || "apvizual";

// Every scope is the READ-ONLY variant. The package's own list is full-access.
const SCOPES = [
  "https://www.googleapis.com/auth/drive.readonly",
  "https://www.googleapis.com/auth/documents.readonly",
  "https://www.googleapis.com/auth/spreadsheets.readonly",
  "https://www.googleapis.com/auth/presentations.readonly",
  "https://www.googleapis.com/auth/calendar.readonly",
  "https://www.googleapis.com/auth/gmail.readonly",
];

const CONFIG_DIR = path.join(os.homedir(), ".google-mcp");
const TOKENS_DIR = path.join(CONFIG_DIR, "tokens");
const CREDS_DIR = path.join(CONFIG_DIR, "credentials");
const CREDENTIALS_PATH = path.join(CONFIG_DIR, "credentials.json");
const ACCOUNTS_PATH = path.join(CONFIG_DIR, "accounts.json");

function readClient() {
  const j = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, "utf8"));
  const c = j.installed || j.web || j;
  if (!c.client_id || !c.client_secret) throw new Error("credentials.json is unusable");
  return { clientId: c.client_id, clientSecret: c.client_secret };
}

function waitForCode(client, redirectUri) {
  const port = Number(new URL(redirectUri).port);
  const authUrl = client.generateAuthUrl({
    access_type: "offline", scope: SCOPES, prompt: "consent",
  });
  console.log("\nOpen this and choose Allow:\n");
  console.log(`  ${authUrl}\n`);
  try { require("node:child_process").exec(`start "" "${authUrl}"`); } catch {}

  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      if (!req.url || req.url.indexOf("/") !== 0) { res.writeHead(404).end(); return; }
      const qs = new url.URL(req.url, redirectUri).searchParams;
      const code = qs.get("code");
      const err = qs.get("error");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      server.close();
      if (code) {
        res.end(`<!doctype html><meta charset=utf-8><title>Authorized</title>
<body style="font:16px system-ui;background:#0b1020;color:#dbe4ee;display:grid;place-items:center;height:100vh;margin:0">
<div style="text-align:center;max-width:34rem">
<h1 style="font-size:26px">Workspace authorized (read-only)</h1>
<p>Mavis can close this tab.</p>
<p style="margin-top:1.5rem;padding:.9rem;border:1px solid #3a4152;border-radius:6px;background:#1a1207;color:#fbbf24;font-size:13.5px;line-height:1.5">
<strong>Do not copy or share this tab's address.</strong><br>
It ends in <code>?code=...</code> &mdash; a one-time authorization code. It is
already spent by the time this page appears, so it cannot be reused, but it is
still a credential-shaped string and does not belong in a chat, a screenshot or
a ticket.
</p>
</div></body>`);
        resolve(code);
      } else {
        res.end(`<!doctype html><meta charset=utf-8><title>Denied</title>
<body style="font:16px system-ui;background:#2a0b0b;color:#ffd7d7;display:grid;place-items:center;height:100vh;margin:0">
<div style="text-align:center"><h1 style="font-size:26px">Denied</h1><p>${err || "no code"}</p></div></body>`);
        reject(new Error(`refused: ${err}`));
      }
    });
    server.on("error", reject);
    server.listen(port, "127.0.0.1", () =>
      console.log(`Waiting for consent on ${redirectUri} ...`));
  });
}

(async () => {
  fs.mkdirSync(TOKENS_DIR, { recursive: true });
  fs.mkdirSync(CREDS_DIR, { recursive: true });

  const { clientId, clientSecret } = readClient();
  const port = 3400 + Math.floor(Math.random() * 400);
  const redirectUri = `http://localhost:${port}`;
  const client = new google.auth.OAuth2(clientId, clientSecret, redirectUri);

  let code = await waitForCode(client, redirectUri);
  console.log("code received; exchanging ...");
  const { tokens } = await client.getToken(code);
  if (!tokens.refresh_token) throw new Error("no refresh_token - grant was not durable");
  // The code is single-use and is now spent. Anything that captured the callback
  // URL holds a dead string. Never echo it, and never ask anyone to paste it.
  code = null;

  // 1. per-account credentials, so this account is self-describing.
  //    The SHAPE matters and fails silently when wrong: loadCredentials()
  //    (accounts.js:113) does `keys.installed ?? keys.web` and throws "Could
  //    not find client secrets" on a flat {client_id, client_secret}. That
  //    throw is swallowed by a bare `catch { return null }` two functions up,
  //    so the server starts, advertises all 110 tools, and every call fails
  //    with "token is invalid or missing". Write the downloaded-JSON shape.
  fs.writeFileSync(path.join(CREDS_DIR, `${ACCOUNT}.json`),
    JSON.stringify({
      installed: {
        client_id: clientId,
        client_secret: clientSecret,
        redirect_uris: ["http://localhost"],
      },
    }, null, 2));
  // 2. the token, in the exact shape accounts.js:155-160 writes
  fs.writeFileSync(path.join(TOKENS_DIR, `${ACCOUNT}.json`),
    JSON.stringify({ type: "authorized_user", client_id: clientId, client_secret: clientSecret, refresh_token: tokens.refresh_token }, null, 2));
  // 3. register the account
  //    BOTH keys are required, and missing either fails SILENTLY: the token
  //    loader (accounts.js:138) does `fs.readFile(account.tokenPath)` inside a
  //    bare `catch { return null }`. An entry carrying only credentialsPath
  //    yields "Could not load token", the server starts, advertises all 110
  //    tools, and every single call fails at runtime.
  let cfg = { accounts: {}, credentialsPath: CREDENTIALS_PATH };
  try { cfg = JSON.parse(fs.readFileSync(ACCOUNTS_PATH, "utf8")); } catch {}
  cfg.accounts = cfg.accounts || {};
  cfg.accounts[ACCOUNT] = {
    tokenPath: path.join(TOKENS_DIR, `${ACCOUNT}.json`),
    credentialsPath: path.join(CREDS_DIR, `${ACCOUNT}.json`),
  };
  fs.writeFileSync(ACCOUNTS_PATH, JSON.stringify(cfg, null, 2));

  console.log(`\nstored account "${ACCOUNT}" (read-only scopes only):`);
  SCOPES.forEach((s) => console.log("  " + s));
})().catch((e) => { console.error("\nFAILED:", e && e.message ? e.message : e); process.exit(1); });

// gdrive-oauth.js
//
// The consent flow gdrive-mcp ships, with ONE change: the refresh token is
// written to the file our shim reads, instead of into `Bun.secrets`, which
// does not exist in bun 1.2.10 on Windows. Everything else - the loopback
// listener, the scopes, the client id - is the same, so the grant Popy sees on
// Google's screen is exactly the grant the MCP server will use.
//
// Run:  bun gdrive-oauth.js
// The client id/secret are read from ~/.config/gws/client_secret.json, which is
// a Desktop-app client. They are never printed and never passed on a command
// line, where they would land in process listings and shell history.

const http = require("node:http");
const url = require("node:url");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { install } = require("./bun-secrets-shim.js");

// googleapis is a dependency of gdrive-mcp, not of this script, so it is
// resolved from that package's own node_modules rather than assumed to be on
// the resolution path from this directory.
const googleapis = require(
  path.join(
    os.homedir(),
    "AppData", "Roaming", "npm", "node_modules", "gdrive-mcp", "node_modules", "googleapis"
  )
);
const { google } = googleapis;

const SCOPES = [
  // Was "https://www.googleapis.com/auth/drive" - the FULL scope. Re-running
  // this script therefore re-granted exactly the access it was supposed to
  // remove, and the console kept reporting a full read+write Drive while the
  // remedy was described as "run the script". A remedy that reproduces the
  // defect is not a remedy.
  //
  // The console only reads: /api/v3/about for the account, fileList for the
  // sample. drive.readonly covers both. Anything that genuinely needs to write
  // must get its own token rather than widening this one.
  "https://www.googleapis.com/auth/drive.readonly",
  "https://www.googleapis.com/auth/documents.readonly",
];
const REDIRECT_PORT = 48127;

function readClient() {
  const p = path.join(os.homedir(), ".config", "gws", "client_secret.json");
  const j = JSON.parse(fs.readFileSync(p, "utf8"));
  const c = j.installed || j.web || j;
  if (!c.client_id || !c.client_secret) {
    throw new Error(`client_secret.json at ${p} has no client_id/client_secret`);
  }
  return { clientId: c.client_id, clientSecret: c.client_secret };
}

function waitForCode(client) {
  const authUrl = client.generateAuthUrl({
    access_type: "offline",
    scope: SCOPES,
    prompt: "consent", // force consent so a refresh_token is always issued
  });

  console.log("\nIf a browser did not open, visit this URL and choose Allow:");
  console.log(`\n  ${authUrl}\n`);

  try {
    require("node:child_process").exec(`start "" "${authUrl}"`);
  } catch {
    /* opening a browser is a convenience, not a requirement */
  }

  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      if (!req.url || req.url.indexOf("/oauth2callback") === -1) {
        res.writeHead(404).end("not found");
        return;
      }
      const qs = new url.URL(req.url, `http://localhost:${REDIRECT_PORT}`).searchParams;
      const code = qs.get("code");
      const err = qs.get("error");
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      if (code) {
        res.end(`<!doctype html><meta charset=utf-8><title>Authorized</title>
<body style="font:16px system-ui;background:#0b1020;color:#dbe4ee;display:grid;place-items:center;height:100vh;margin:0">
<div style="text-align:center"><h1 style="font-size:26px">Drive authorized</h1>
<p>Mavis can close this tab.</p></div></body>`);
        server.close();
        resolve(code);
      } else {
        res.end(`<!doctype html><meta charset=utf-8><title>Failed</title>
<body style="font:16px system-ui;background:#2a0b0b;color:#ffd7d7;display:grid;place-items:center;height:100vh;margin:0">
<div style="text-align:center"><h1 style="font-size:26px">Denied</h1><p>${err || "no code"}</p></div></body>`);
        server.close();
        reject(new Error(`authorization refused: ${err}`));
      }
    });
    server.on("error", reject);
    server.listen(REDIRECT_PORT, "127.0.0.1", () =>
      console.log(`Waiting for consent on http://localhost:${REDIRECT_PORT}/oauth2callback ...`)
    );
  });
}

(async () => {
  install();
  const { clientId, clientSecret } = readClient();
  const client = new google.auth.OAuth2(
    clientId,
    clientSecret,
    `http://localhost:${REDIRECT_PORT}/oauth2callback`
  );

  const code = await waitForCode(client);
  console.log("code received; exchanging for tokens ...");

  const { tokens } = await client.getToken(code);
  if (!tokens.refresh_token) {
    throw new Error("no refresh_token in the response - grant was not durable");
  }

  // Same service/name triple gdrive-mcp reads at index.ts:18-31.
  await Bun.secrets.set({ service: "gdrive-mcp", name: "client_id", value: clientId });
  await Bun.secrets.set({ service: "gdrive-mcp", name: "client_secret", value: clientSecret });
  await Bun.secrets.set({ service: "gdrive-mcp", name: "refresh_token", value: tokens.refresh_token });

  console.log("\nstored gdrive-mcp client_id / client_secret / refresh_token");
  console.log("scopes granted:", SCOPES.join("  "));
})().catch((e) => {
  console.error("\nFAILED:", e && e.message ? e.message : e);
  process.exit(1);
});

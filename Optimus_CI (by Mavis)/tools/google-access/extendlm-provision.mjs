// extendlm-provision.mjs - permanent ExtendLM / NotebookLM access for the
// Google_Access container.
//
// ExtendLM publishes an OAuth authorization server with DYNAMIC CLIENT
// REGISTRATION and PKCE (S256), public clients only. That means the container
// can register itself: no client id has to be created by hand, and no client
// secret exists to leak.
//
// Measured endpoints (from the server metadata, not from memory):
//   metadata      https://api.extendlm.com/.well-known/oauth-authorization-server
//   registration  POST   https://api.extendlm.com/rest/v1/mcp/oauth/register
//   authorization GET    https://api.extendlm.com/rest/v1/mcp/oauth/authorize
//   token         POST   https://api.extendlm.com/rest/v1/mcp/oauth/token
//   mcp server           https://mcp.extendlm.com/mcp
//
// Flow: register -> print the authorization URL -> listen on the loopback
// redirect -> exchange the code -> write the token into the mounted volume.
// Only the authorization step in the browser is the user's.
//
// Usage: node extendlm-provision.mjs [--port 8799] [--open]
import crypto from "node:crypto";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";

const AS = "https://api.extendlm.com";
const MCP_URL = process.env.GA_EXTENDLM_URL || "https://mcp.extendlm.com/mcp";
const GA_DIR = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1"));
const DATA_DIR = path.join(GA_DIR, "data");
const OUT = path.join(DATA_DIR, "extendlm.json");

const portIdx = process.argv.indexOf("--port");
const PORT = portIdx !== -1 ? Number(process.argv[portIdx + 1]) : 8799;
const REDIRECT = "http://127.0.0.1:" + PORT + "/callback";
const SCOPE = "mcp";

const b64url = (buf) => Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

function log(...a) {
  console.log(...a);
}

async function readMetadata() {
  const res = await fetch(AS + "/.well-known/oauth-authorization-server");
  if (!res.ok) throw new Error("metadata http " + res.status);
  return res.json();
}

async function register(meta) {
  // MEASURED: sending scope:"mcp" is refused with 400 invalid_client_metadata.
  // The server accepts the RFC 7591 body without a scope and assigns its own
  // (the 30 values listed in scopes_supported). The authorization request then
  // asks for exactly the scope the server returned.
  const body = {
    client_name: "Google_Access (local MCP container)",
    client_uri: "https://mcp.extendlm.com/",
    redirect_uris: [REDIRECT],
    grant_types: ["authorization_code", "refresh_token"],
    response_types: ["code"],
    token_endpoint_auth_method: "none",
  };
  const res = await fetch(meta.registration_endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  if (!res.ok) throw new Error("register http " + res.status + " " + text.slice(0, 300));
  return JSON.parse(text);
}

function exchange(meta, reg, code, verifier) {
  const params = new URLSearchParams({
    grant_type: "authorization_code",
    code,
    redirect_uri: REDIRECT,
    client_id: reg.client_id,
    code_verifier: verifier,
  });
  return fetch(meta.token_endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
    body: params.toString(),
  }).then(async (r) => {
    const t = await r.text();
    if (!r.ok) throw new Error("token http " + r.status + " " + t.slice(0, 300));
    return JSON.parse(t);
  });
}

(async () => {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const meta = await readMetadata();
  log("METADATA_OK=1 registration=" + meta.registration_endpoint + " token=" + meta.token_endpoint);

  const reg = await register(meta);
  log("REGISTERED=1 client_id=" + reg.client_id + " (public, no secret)");

  const verifier = b64url(crypto.randomBytes(48));
  const challenge = b64url(crypto.createHash("sha256").update(verifier).digest());
  const state = b64url(crypto.randomBytes(16));

  const url =
    meta.authorization_endpoint +
    "?response_type=code" +
    "&client_id=" + encodeURIComponent(reg.client_id) +
    "&redirect_uri=" + encodeURIComponent(REDIRECT) +
    "&code_challenge=" + encodeURIComponent(challenge) +
    "&code_challenge_method=S256" +
    "&state=" + encodeURIComponent(state) +
    (reg.scope ? "&scope=" + encodeURIComponent(reg.scope) : "");

  log("AUTH_URL=" + url);

  const server = http.createServer((req, res) => {
    const u = new URL(req.url, "http://127.0.0.1:" + PORT);
    if (u.pathname !== "/callback") {
      res.writeHead(404).end("not found");
      return;
    }
    const code = u.searchParams.get("code");
    const gotState = u.searchParams.get("state");
    const err = u.searchParams.get("error");
    if (err) {
      res.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" }).end("ExtendLM refused: " + err);
      log("AUTH_ERROR=" + err);
      process.exitCode = 4;
      server.close();
      return;
    }
    if (!code || gotState !== state) {
      res.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" }).end("bad code or state");
      log("CALLBACK_INVALID=1 code=" + (code ? "present" : "missing") + " state_match=" + (gotState === state));
      process.exitCode = 4;
      server.close();
      return;
    }
    exchange(meta, reg, code, verifier)
      .then((tok) => {
        const now = Date.now();
        const payload = {
          // "token" is the field the container reads; the rest is the
          // renewable form.
          token: tok.access_token,
          access_token: tok.access_token,
          refresh_token: tok.refresh_token || null,
          token_type: tok.token_type || "Bearer",
          scope: tok.scope || SCOPE,
          expires_at: tok.expires_in ? now + Number(tok.expires_in) * 1000 : null,
          obtained_at: new Date(now).toISOString(),
          client_id: reg.client_id,
          token_endpoint: meta.token_endpoint,
          mcp_url: MCP_URL,
          grant_type: "authorization_code+refresh_token",
        };
        fs.writeFileSync(OUT, JSON.stringify(payload, null, 2), "utf8");
        log("TOKEN_OK=1 scope=" + payload.scope + " expires_at=" + payload.expires_at + " refresh=" + (payload.refresh_token ? "yes" : "no"));
        log("WROTE=" + OUT);
        res
          .writeHead(200, { "Content-Type": "text/html; charset=utf-8" })
          .end(
            "<html><body style='font-family:sans-serif;padding:40px'>" +
              "<h2>ExtendLM connected</h2>" +
              "<p>The token is in the container volume. " +
              "You can close this tab.</p></body></html>"
          );
        process.exitCode = 0;
        server.close();
      })
      .catch((e) => {
        log("TOKEN_FAILED=" + e.message);
        res.writeHead(500, { "Content-Type": "text/plain; charset=utf-8" }).end("token exchange failed");
        process.exitCode = 5;
        server.close();
      });
  });

  server.listen(PORT, "127.0.0.1", () => {
    log("LISTENING=http://127.0.0.1:" + PORT + " redirect=" + REDIRECT);
    log("READY=1");
  });

  setTimeout(() => {
    log("TIMEOUT=1 (nicio autorizare in 180 min)");
    server.close();
    process.exitCode = 6;
  }, 180 * 60 * 1000);
})().catch((e) => {
  log("FATAL=" + e.message);
  process.exitCode = 3;
});

// gmail-launcher.js
//
// Starts gmail-mcp with a FRESH access token, obtained from the durable
// refresh token that is already on this machine.
//
// WHY THIS FILE EXISTS
// --------------------
// MEASURED 2026-10-27: gmail-mcp in stdio transport reads
//   process.env.GOOGLE_ACCESS_TOKEN
// and nothing else (dist/main.js:41-47). A Google access token lives about
// one hour. So the server either starts with a stale token (and every tool
// call fails with 401) or somebody has to re-authenticate - which is the
// loop Popy described: "de fiecare data iar te loghezi si te autentifici".
//
// The refresh token, by contrast, is durable and never expires on its own.
// The launcher spends it for a fresh access token at every start. The
// consent screen is not involved at all.
//
// It also self-heals: before starting, the live grant on this machine is
// measured and published into every Google store (see google-grant.js), so
// a dead grant in one store never becomes another re-consent.
//
// WHAT IT NEVER DOES
// It never prints a token.
//
// Exit behaviour: if no live grant exists, the server is started anyway and
// gmail-mcp prints its own "GOOGLE_ACCESS_TOKEN required" message - so the
// failure is visible in the MCP log rather than silent.
//
// ASCII ONLY.

const path = require("node:path");
const os = require("node:os");
const grant = require("./google-grant.js");

(async () => {
  try {
    const live = await grant.ensureAccess((m) => {
      console.error(`[gmail-launcher] ${m}`);
    });
    if (live) {
      process.env.GOOGLE_ACCESS_TOKEN = live.accessToken;
      console.error("[gmail-launcher] access token obtained from the durable grant on disk");
    } else {
      console.error(
        "[gmail-launcher] NO LIVE GRANT on this machine - gmail-mcp will need a consent"
      );
    }
  } catch (e) {
    console.error("[gmail-launcher] could not obtain a token:", e && e.message ? e.message : e);
  }

  const target = path.join(
    os.homedir(),
    "AppData",
    "Roaming",
    "npm",
    "node_modules",
    "gmail-mcp",
    "dist",
    "main.js"
  );

  import(target).catch((e) => {
    console.error("[gmail-launcher] upstream failed:", e && e.stack ? e.stack : e);
    process.exit(1);
  });
})();

// calendar-launcher.js
//
// Starts google-calendar-mcp with credentials that are already valid.
//
// WHY THIS FILE EXISTS
// --------------------
// MEASURED 2026-10-27 (dist/services/googleCalendarService.js):
//   - the OAuth2 client is built from env GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET
//   - the token is read from `path.join(process.cwd(), 'token.json')`
//     -> the CWD, which for an MCP server is wherever the host happens to
//        start it. That makes the token file land in an unpredictable place,
//        so the server finds no token and asks for a fresh login.
//   - the token must carry a refresh_token, otherwise it cannot renew itself
//
// So the launcher:
//   1. measures the live grant on this machine (google-grant.js)
//   2. exports GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET from it
//   3. writes token.json (with the refresh_token) into the server's own
//      directory and runs the server with that CWD
//   4. the server then renews the access token itself
//
// The consent screen is not involved: the grant was already given.
//
// WHAT IT NEVER DOES
// It never prints a token.
//
// ASCII ONLY.

const path = require("node:path");
const os = require("node:os");
const fs = require("node:fs");
const grant = require("./google-grant.js");

(async () => {
  const pkgDir = path.join(
    os.homedir(),
    "AppData",
    "Roaming",
    "npm",
    "node_modules",
    "google-calendar-mcp"
  );

  try {
    const live = await grant.ensureAccess((m) => {
      console.error(`[calendar-launcher] ${m}`);
    });
    if (live) {
      process.env.GOOGLE_CLIENT_ID = live.clientId;
      process.env.GOOGLE_CLIENT_SECRET = live.clientSecret;
      // the token file the server reads: path.join(process.cwd(), 'token.json')
      const tokenFile = path.join(pkgDir, "token.json");
      fs.writeFileSync(
        tokenFile,
        JSON.stringify(
          {
            access_token: live.accessToken,
            refresh_token: live.refreshToken,
            token_type: "Bearer",
            scope: live.scope,
            expiry_date: Date.now() + 3600 * 1000,
          },
          null,
          2
        ),
        "utf8"
      );
      // the server resolves the token file against the CWD
      process.chdir(pkgDir);
      console.error("[calendar-launcher] token.json written; client credentials exported");
    } else {
      console.error(
        "[calendar-launcher] NO LIVE GRANT on this machine - google-calendar-mcp will need a consent"
      );
    }
  } catch (e) {
    console.error("[calendar-launcher] could not prepare credentials:", e && e.message ? e.message : e);
  }

  const target = path.join(pkgDir, "dist", "index.js");

  import(target).catch((e) => {
    console.error("[calendar-launcher] upstream failed:", e && e.stack ? e.stack : e);
    process.exit(1);
  });
})();

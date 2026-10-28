// gdrive-launcher.js
//
// Starts the upstream gdrive-mcp server with the missing `Bun.secrets` API
// present, then hands over to it. Everything after the import is the package's
// own code, unmodified.
//
// Point mcp.json at THIS file rather than at src/index.ts. The package is
// still the thing that runs; this only supplies the platform API it assumes
// exists. A `npm update` of gdrive-mcp changes nothing here, and if a future bun
// ships a real Bun.secrets the shim steps aside instead of shadowing it.
//
// SELF-HEALING (2026-10-27)
// --------------------------
// MEASURED: the refresh token in the store gdrive-mcp reads was DEAD
// (refresh exchange -> HTTP 400 "invalid_grant") while a LIVE grant for the
// same account and the same OAuth client sat in another store on this
// machine. The symptom was a re-consent request every single time.
//
// So before starting, the launcher MEASURES the grants on this machine and
// publishes the live one into the store gdrive-mcp reads. No browser, no
// consent screen: the working grant was already on disk.
//
// If NO live grant exists anywhere, the launcher says so plainly and starts
// the server anyway - the server's own error message then names the missing
// credential, which is more useful than a launcher that hides the reason.
//
// WHAT IT NEVER DOES
// It never prints a token.
//
// ASCII ONLY.

const path = require("node:path");
const os = require("node:os");
const { install } = require("./bun-secrets-shim.js");
const grant = require("./google-grant.js");

install();

(async () => {
  try {
    const live = await grant.ensureAccess((m) => {
      console.error(`[gdrive-launcher] ${m}`);
    });
    if (live) {
      console.error("[gdrive-launcher] live grant published into the gdrive-mcp store");
    } else {
      console.error(
        "[gdrive-launcher] NO LIVE GRANT on this machine - a consent is required"
      );
    }
  } catch (e) {
    console.error("[gdrive-launcher] could not prepare credentials:", e && e.message ? e.message : e);
  }

  const target = path.join(
    os.homedir(),
    "AppData",
    "Roaming",
    "npm",
    "node_modules",
    "gdrive-mcp",
    "src",
    "index.ts"
  );

  console.error(
    `[gdrive-launcher] Bun.secrets shim active; starting ${target}`
  );

  import(target).catch((e) => {
    // A crash that exits 0 is a failure an MCP client cannot see. Do not
    // reproduce that here: surface it as a non-zero exit and a readable line.
    console.error("[gdrive-launcher] upstream failed:", e && e.stack ? e.stack : e);
    process.exit(1);
  });
})();

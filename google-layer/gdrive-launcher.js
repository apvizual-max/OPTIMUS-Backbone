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

const path = require("node:path");
const os = require("node:os");
const { install } = require("./bun-secrets-shim.js");

install();

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

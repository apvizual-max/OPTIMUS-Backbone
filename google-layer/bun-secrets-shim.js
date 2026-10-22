// bun-secrets-shim.js
//
// WHY THIS EXISTS
// gdrive-mcp@1.0.2 calls `Bun.secrets.get()` at module top level
// (src/index.ts:18) BEFORE it reaches its own environment-variable fallback on
// line 34. `Bun.secrets` does not exist in bun 1.2.10 on Windows, so the call
// throws `TypeError: undefined is not an object` and the MCP server dies on
// startup. It exits with code 0, so a client that only checks the exit code
// records it as healthy while it is in fact dead. That is the worst shape a
// failure can take: a green line over a corpse.
//
// The same missing API sinks gdrive-mcp's own setup-auth.ts, which stores the
// refresh token with `Bun.secrets.set` - so consent completes, the token is
// received, and then it is thrown away. The consent screen reports success and
// no credential exists anywhere.
//
// The fix is not to patch node_modules, which npm overwrites on the next
// update. It is to install the missing API before the package loads, backed by
// a file we control. Patching the symptom in place would be undone by the next
// `npm update` and the failure would return silently.
//
// SECURITY
// The file holds a refresh token, which is a bearer credential: anything that
// can read it gets Drive access as the user. It is written under the user's
// existing ~/.config/gws tree and the ACL is restricted to the owner by
// acl-secrets.js. It is a plain JSON file, NOT encrypted - the same guarantee
// the encrypted-but-unreachable token_cache.json provided, minus the part where
// nothing can read it.

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const STORE =
  process.env.MCP_SECRETS_FILE ||
  path.join(os.homedir(), ".config", "gws", "mcp-secrets.json");

function key(service, name) {
  return `${service}/${name}`;
}

async function readAll() {
  try {
    return JSON.parse(await fs.promises.readFile(STORE, "utf8"));
  } catch {
    return {};
  }
}

function install() {
  if (Bun.secrets) return Bun.secrets; // a real implementation exists: do not shadow it

  const shim = {
    async get({ service, name }) {
      // The real Bun.secrets.get resolves to the raw value, and gdrive-mcp uses
      // the return value directly as `new OAuth2(clientId, clientSecret)`.
      // Returning { value } here would be truthy-but-wrong and would surface as
      // a confusing auth failure rather than a missing credential.
      const all = await readAll();
      const v = all[key(service, name)];
      return v === undefined ? null : v;
    },
    async set({ service, name, value }) {
      const all = await readAll();
      all[key(service, name)] = value;
      await fs.promises.mkdir(path.dirname(STORE), { recursive: true });
      await fs.promises.writeFile(STORE, JSON.stringify(all, null, 2), "utf8");
    },
    async delete({ service, name }) {
      const all = await readAll();
      delete all[key(service, name)];
      await fs.promises.writeFile(STORE, JSON.stringify(all, null, 2), "utf8");
    },
  };

  Object.defineProperty(Bun, "secrets", {
    value: shim,
    configurable: true,
    writable: true,
    enumerable: false,
  });
  return shim;
}

module.exports = { install, STORE };

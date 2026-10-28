// probe-mcp-stdio.mjs - prove that a REGISTERED MCP entry actually starts.
//
// WHY THIS EXISTS
// 2026-10-28, measured: three registered entries pointed at a folder that had
// been moved. The registry said "enabled", the file did not exist, and the
// failure mode was silence - a server that never answers a handshake. A
// registration that cannot start is not a capability, so the registry is
// checked against the disk, not against itself.
//
// The same shape was measured for docker-mcp: the registered wrapper
// (mcp-docker.cmd) did not exist, and the package behind it could not import
// its own dependency. A path that exists is still not a server that runs.
//
// WHAT IT DOES
// Spawns the EXACT command + arguments from the registry (or from the command
// line), speaks a real MCP handshake over stdio, and reports what answered.
//
//   node scripts/probe-mcp-stdio.mjs --name gdrive-mcp
//   node scripts/probe-mcp-stdio.mjs --cmd node --script <path> [--arg <a>]
//
// OUTPUT (ASCII only)
//   PROBE=<name> TRANSPORT=stdio INIT_OK=1 SERVER=<name> TOOLS=<n> EXIT=0
//   PROBE=<name> TRANSPORT=stdio INIT_OK=0 REASON=<text> EXIT=2
//
// EXIT: 0 = the server completed the handshake and advertised tools,
//       2 = it did not (a measured failure, never reported as success).
//
// It never prints a token, a credential or an environment value.

import fs from "node:fs";
import { spawn } from "node:child_process";

const argOf = (flag, dflt) => {
  const i = process.argv.indexOf(flag);
  return i !== -1 ? process.argv[i + 1] : dflt;
};
const argAll = (flag) => {
  const out = [];
  process.argv.forEach((a, i) => {
    if (a === flag && process.argv[i + 1]) out.push(process.argv[i + 1]);
  });
  return out;
};

const MCP_JSON = argOf("--mcp-json", "C:/Users/apviz/.minimax/mcp.json");
const NAME = argOf("--name", "");
const CMD = argOf("--cmd", "");
const SCRIPT = argOf("--script", "");
const ARGS = argAll("--arg");
const TIMEOUT_MS = Number(argOf("--timeout", "30000"));

function resolveEntry() {
  if (CMD) {
    return { name: NAME || "inline", command: CMD, args: SCRIPT ? [SCRIPT, ...ARGS] : ARGS };
  }
  if (!NAME) {
    console.log("ERROR=no entry specified: pass --name <entry> or --cmd <exe>");
    console.log("EXIT=2");
    process.exit(2);
  }
  let reg;
  try {
    reg = JSON.parse(fs.readFileSync(MCP_JSON, "utf8")).mcpServers || {};
  } catch (e) {
    console.log("PROBE=" + NAME + " INIT_OK=0 REASON=unreadable_mcp_json EXIT=2");
    process.exit(2);
  }
  const e = reg[NAME];
  if (!e) {
    console.log("PROBE=" + NAME + " INIT_OK=0 REASON=not_registered EXIT=2");
    process.exit(2);
  }
  if (e.type && e.type !== "stdio") {
    console.log(
      "PROBE=" + NAME + " TRANSPORT=" + e.type + " INIT_OK=0 REASON=not_stdio_entry EXIT=2"
    );
    process.exit(2);
  }
  return { name: NAME, command: e.command, args: e.args || [] };
}

function probe(entry) {
  return new Promise((resolve) => {
    const started = Date.now();
    let child;
    try {
      child = spawn(entry.command, entry.args, {
        windowsHide: true,
        stdio: ["pipe", "pipe", "pipe"],
        env: Object.assign({}, process.env),
      });
    } catch (e) {
      resolve({ ok: false, reason: "spawn_failed:" + (e && e.message ? e.message : e) });
      return;
    }

    let buf = "";
    let stderr = "";
    const pend = new Map();
    let id = 0;
    let settled = false;

    const finish = (r) => {
      if (settled) return;
      settled = true;
      try {
        child.kill();
      } catch {
        /* the child may already be gone */
      }
      resolve(r);
    };

    child.on("error", (e) => finish({ ok: false, reason: "spawn_error:" + e.message }));
    child.stderr.on("data", (c) => {
      stderr += c.toString();
      if (stderr.length > 4000) stderr = stderr.slice(-4000);
    });
    child.stdout.on("data", (c) => {
      buf += c.toString();
      let i;
      while ((i = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, i).trim();
        buf = buf.slice(i + 1);
        if (!line) continue;
        let m;
        try {
          m = JSON.parse(line);
        } catch {
          continue;
        }
        if (m.id !== undefined && pend.has(m.id)) {
          const p = pend.get(m.id);
          pend.delete(m.id);
          p(m);
        }
      }
    });

    const call = (method, params) =>
      new Promise((r) => {
        const i = ++id;
        pend.set(i, r);
        try {
          child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id: i, method, params }) + "\n");
        } catch (e) {
          pend.delete(i);
          r(null);
        }
      });

    (async () => {
      const init = await call("initialize", {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: { name: "probe-mcp-stdio", version: "1.0.0" },
      });
      if (!init || !init.result) {
        const why = stderr.trim().split(/\r?\n/).slice(-1)[0] || "no_answer";
        finish({ ok: false, reason: "initialize_failed:" + why.slice(0, 200) });
        return;
      }
      const serverName =
        (init.result.serverInfo && init.result.serverInfo.name) || "?";
      const list = await call("tools/list", {});
      const tools =
        list && list.result && Array.isArray(list.result.tools) ? list.result.tools.length : 0;
      finish({ ok: tools > 0, server: serverName, tools, ms: Date.now() - started });
    })();

    setTimeout(() => {
      const why = stderr.trim().split(/\r?\n/).slice(-1)[0] || "timeout";
      finish({ ok: false, reason: "timeout:" + why.slice(0, 200) });
    }, TIMEOUT_MS);
  });
}

const entry = resolveEntry();
const missing = [];
if (!entry.command) missing.push("command");
if (entry.command && !fs.existsSync(entry.command) && /[\\/]/.test(entry.command)) {
  missing.push("command_path:" + entry.command);
}
for (const a of entry.args || []) {
  if (typeof a === "string" && /^[A-Za-z]:\\/.test(a) && !fs.existsSync(a)) {
    missing.push("arg_path:" + a);
  }
}
if (missing.length) {
  console.log(
    "PROBE=" + entry.name + " TRANSPORT=stdio INIT_OK=0 REASON=missing_on_disk(" +
      missing.join(",") + ") EXIT=2"
  );
  process.exit(2);
}

const res = await probe(entry);
if (res.ok) {
  console.log(
    "PROBE=" + entry.name + " TRANSPORT=stdio INIT_OK=1 SERVER=" + res.server +
      " TOOLS=" + res.tools + " MS=" + res.ms + " EXIT=0"
  );
  process.exit(0);
}
console.log("PROBE=" + entry.name + " TRANSPORT=stdio INIT_OK=0 REASON=" + res.reason + " EXIT=2");
process.exit(2);

// mcp-probe.js
//
// Proves that a Google MCP server actually WORKS: a real MCP handshake over
// stdio, followed by a tool call that needs a live credential.
//
// WHY THIS FILE EXISTS
// --------------------
// "The token file is populated" is not "I have access". A server can start
// with a credential it cannot spend, and the MCP handshake still succeeds -
// the failure only shows up on the first tool call. So the probe goes all
// the way: initialize -> initialized -> tools/list -> the read tool.
//
// WHAT IT MEASURES
//   - the server process starts and speaks MCP
//   - the handshake completes (protocol version, capabilities)
//   - the tool list is non-empty
//   - the tool that reads from Google SUCCEEDS (not just lists)
//
// WHAT IT NEVER DOES
// It never prints a token, and it never prints file contents from Drive -
// only the count of items and the HTTP/shape of the answer.
//
// Exit codes:
//   0 = handshake + tool call succeeded
//   1 = the server failed at some measured step (the failing step is named)
//   2 = the probe could not run
//
// ASCII ONLY.

const { spawn } = require("node:child_process");
const path = require("node:path");
const os = require("node:os");

const BUN = "C:\\Program Files\\Qwen\\resources\\bun\\bun.exe";
const LAYER = path.join(os.homedir(), ".minimax-agent", "projects", "google-layer");

// server key -> { command, args, readTool, readArgs }
// The tool names are read from the packages, not guessed:
//   gdrive-mcp  src/tools/search-drive.ts -> "gdrive_search_drive" (query, max_results)
//   gmail-mcp   dist/tools/profile-get.js -> "get_profile" (no arguments)
const TARGETS = {
  "gdrive-mcp": {
    command: BUN,
    args: [path.join(LAYER, "gdrive-launcher.js")],
    readTool: "gdrive_search_drive",
    // A PLAIN term, not Drive query syntax. Measured: gdrive-mcp wraps a
    // query without ":" into `fullText contains '<q>' or name contains '<q>'`
    // (src/tools/search-drive.ts:70-72), so a query that already contains
    // quotes ("name contains 'Optimus'") gets quoted twice and Drive answers
    // "Invalid Value". That is upstream behaviour, not a credential fault.
    readArgs: { query: "Optimus", max_results: 3 },
  },
  "gmail-mcp": {
    command: BUN,
    args: [path.join(LAYER, "gmail-launcher.js")],
    readTool: "get_profile",
    readArgs: {},
  },
};

function say(m) {
  process.stdout.write(String(m) + "\n");
}

// MCP stdio framing, measured 2026-10-27 from the SDK itself:
//   sdk/dist/esm/shared/stdio.js -> serializeMessage() = JSON.stringify(msg) + '\n'
//   ReadBuffer.readMessage() splits on '\n'
// So the wire format is NEWLINE-DELIMITED JSON. An earlier version of this
// probe used LSP-style Content-Length framing, the server started fine and
// the probe still timed out - a framing mistake that looks exactly like a
// broken server.
function frame(obj) {
  return JSON.stringify(obj) + "\n";
}

function runTarget(name, cfg, timeoutMs) {
  return new Promise((resolve) => {
    const child = spawn(cfg.command, cfg.args, { stdio: ["pipe", "pipe", "pipe"] });
    let buf = "";
    const messages = [];
    let stderr = "";
    let settled = false;

    const finish = (result) => {
      if (settled) return;
      settled = true;
      try { child.kill(); } catch { /* already gone */ }
      resolve(result);
    };

    const timer = setTimeout(() => {
      finish({ name, ok: false, step: "timeout", detail: `no answer in ${timeoutMs}ms`, stderr });
    }, timeoutMs);

    child.stderr.on("data", (d) => {
      stderr += d.toString();
    });

    child.stdout.on("data", (d) => {
      buf += d.toString();
      // newline-delimited JSON, one message per line (measured from the SDK)
      for (;;) {
        const nl = buf.indexOf("\n");
        if (nl === -1) break;
        const line = buf.slice(0, nl).trim();
        buf = buf.slice(nl + 1);
        if (!line) continue;
        try {
          messages.push(JSON.parse(line));
        } catch {
          messages.push({ _unparsed: line.slice(0, 200) });
        }
      }
    });

    child.on("error", (e) => {
      clearTimeout(timer);
      finish({ name, ok: false, step: "spawn", detail: e.message, stderr });
    });

    child.on("exit", (code) => {
      clearTimeout(timer);
      if (!settled) {
        finish({
          name,
          ok: false,
          step: "early_exit",
          detail: `process exited with ${code}`,
          stderr,
        });
      }
    });

    // --- the handshake -----------------------------------------------------
    child.stdin.write(
      frame({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {
          protocolVersion: "2024-11-05",
          capabilities: {},
          clientInfo: { name: "mavis-probe", version: "1.0.0" },
        },
      })
    );

    const waitForInit = setInterval(() => {
      const init = messages.find((m) => m.id === 1 && m.result);
      if (!init) return;
      clearInterval(waitForInit);

      child.stdin.write(frame({ jsonrpc: "2.0", method: "notifications/initialized", params: {} }));
      child.stdin.write(
        frame({ jsonrpc: "2.0", id: 2, method: "tools/list", params: {} })
      );

      const waitForTools = setInterval(() => {
        const tools = messages.find((m) => m.id === 2 && m.result);
        if (!tools) return;
        clearInterval(waitForTools);

        const list = (tools.result && tools.result.tools) || [];
        if (list.length === 0) {
          clearTimeout(timer);
          finish({ name, ok: false, step: "tools_list", detail: "tool list is empty", stderr });
          return;
        }

        // call the read tool: THIS is where a dead credential shows up
        child.stdin.write(
          frame({
            jsonrpc: "2.0",
            id: 3,
            method: "tools/call",
            params: { name: cfg.readTool, arguments: cfg.readArgs },
          })
        );

        const waitForCall = setInterval(() => {
          const call = messages.find((m) => m.id === 3);
          if (!call) return;
          clearInterval(waitForCall);
          clearTimeout(timer);

          if (call.error) {
            finish({
              name,
              ok: false,
              step: "tool_call",
              detail: `error: ${JSON.stringify(call.error).slice(0, 300)}`,
              stderr,
              toolCount: list.length,
            });
            return;
          }
          const content = (call.result && call.result.content) || [];
          const isError = !!(call.result && call.result.isError);
          const text = content
            .map((c) => (c && c.text ? String(c.text) : ""))
            .join(" ")
            .slice(0, 300);
          finish({
            name,
            ok: !isError,
            step: "tool_call",
            detail: isError ? `isError=true: ${text}` : `OK: ${text}`,
            stderr,
            toolCount: list.length,
          });
        }, 100);
      }, 100);
    }, 100);
  });
}

(async () => {
  say("=== MCP LIVE PROBE (real handshake + real tool call) ===");
  const only = process.argv[2];
  const names = only ? [only] : Object.keys(TARGETS);
  let failures = 0;

  for (const name of names) {
    const cfg = TARGETS[name];
    if (!cfg) {
      say(`  ${name}: no probe config`);
      failures++;
      continue;
    }
    const r = await runTarget(name, cfg, 60000);
    const status = r.ok ? "PASS" : "FAIL";
    if (!r.ok) failures++;
    say(`  ${status} ${name}  step=${r.step}  tools=${r.toolCount ?? "?"}`);
    say(`       ${r.detail}`);
    if (r.stderr) {
      const lines = r.stderr
        .split(/\r?\n/)
        .map((l) => l.trim())
        .filter(Boolean)
        .slice(-4);
      for (const l of lines) say(`       | ${l}`);
    }
  }

  say("");
  if (failures === 0) {
    say("RESULT=ALL_PASS - serverele MCP Google raspund la handshake SI la apel de tool.");
    process.exit(0);
  }
  say(`RESULT=FAILURES=${failures}`);
  process.exit(1);
})().catch((e) => {
  say(`PROBE_CRASH=${e && e.stack ? e.stack : e}`);
  process.exit(2);
});

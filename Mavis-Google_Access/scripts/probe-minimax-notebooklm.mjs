// probe-minimax-notebooklm.mjs - prove the minimax NotebookLM MCP server
// actually starts and answers, over its real stdio transport.
//
// WHY THIS EXISTS: the server was REGISTERED in the Mavis MCP profile and
// ENABLED, while the path it pointed at did not exist
// (projects\google-layer\... - the folder was never there; the file lives in
// projects\Mavis-Google_Access\google-layer\). A registration that cannot
// start is not a capability, and "enabled" in a config file is a declaration,
// not a measurement.
//
// The probe spawns the server as a child process, speaks the same
// newline-delimited JSON-RPC the server speaks, and reports what came back.
//
// Usage: node probe-minimax-notebooklm.mjs [--file <path>] [--call <tool>]
import { spawn } from "node:child_process";
import path from "node:path";
import fs from "node:fs";

const argOf = (flag, dflt) => {
  const i = process.argv.indexOf(flag);
  return i !== -1 ? process.argv[i + 1] : dflt;
};
const FILE = argOf(
  "--file",
  "C:/Users/apviz/.minimax-agent/projects/Mavis-Google_Access/google-layer/minimax-notebooklm.js"
);
const CALL = argOf("--call", "nblm_health");
const NODE = "C:/Program Files/nodejs/node.exe";

const pending = new Map();
let buffer = "";
let stdout = "";
let stderr = "";

const child = spawn(NODE, [FILE], { windowsHide: true });
child.stdout.on("data", (c) => {
  stdout += c.toString();
  let i;
  while ((i = stdout.indexOf("\n")) >= 0) {
    const line = stdout.slice(0, i).trim();
    stdout = stdout.slice(i + 1);
    if (!line) continue;
    let msg;
    try {
      msg = JSON.parse(line);
    } catch {
      continue;
    }
    if (msg.id !== undefined && pending.has(msg.id)) {
      const res = pending.get(msg.id);
      pending.delete(msg.id);
      res(msg);
    }
  }
});
child.stderr.on("data", (c) => {
  stderr += c.toString();
});

let nextId = 1;
function call(method, params) {
  const id = nextId++;
  const p = new Promise((res) => pending.set(id, res));
  child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n");
  return p;
}
function notify(method, params) {
  child.stdin.write(JSON.stringify({ jsonrpc: "2.0", method, params }) + "\n");
}

const timeout = (ms) => new Promise((r) => setTimeout(() => r(null), ms));

(async () => {
  console.log("FILE_EXISTS=" + (fs.existsSync(FILE) ? 1 : 0) + " path=" + FILE);
  if (!fs.existsSync(FILE)) {
    console.log("VERDICT=FILE_MISSING");
    child.kill();
    process.exitCode = 2;
    return;
  }

  const init = await call("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "probe-minimax-notebooklm", version: "1.0.0" },
  });
  const info = init && init.result && init.result.serverInfo;
  console.log("INITIALIZE_OK=" + (init && init.result ? 1 : 0) + " server=" + (info ? info.name : "?") + " version=" + (info ? info.version : "?"));
  notify("notifications/initialized", {});

  const list = await call("tools/list", {});
  const tools = list && list.result && Array.isArray(list.result.tools) ? list.result.tools : [];
  console.log("TOOL_COUNT=" + tools.length + " TOOLS=" + tools.map((t) => t.name).join("|"));

  const res = await call("tools/call", { name: CALL, arguments: {} });
  const text =
    res && res.result && res.result.content && res.result.content[0] && res.result.content[0].text
      ? res.result.content[0].text
      : JSON.stringify(res);
  console.log("CALL=" + CALL + " IS_ERROR=" + (res && res.result && res.result.isError ? 1 : 0));
  console.log("RESULT=" + text.replace(/\s+/g, " ").slice(0, 1200));
  if (stderr.trim()) console.log("STDERR=" + stderr.trim().split("\n").slice(0, 3).join(" | ").slice(0, 400));

  const ok = Boolean(init && init.result) && tools.length > 0 && res && res.result;
  console.log("VERDICT=" + (ok ? "SERVER_ANSWERS" : "SERVER_SILENT"));
  child.kill();
  process.exitCode = ok ? 0 : 2;
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  child.kill();
  process.exitCode = 2;
});

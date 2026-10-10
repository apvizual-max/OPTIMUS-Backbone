// Register the minimax NotebookLM notebooks into the console's live state.
// Talks to minimax-notebooklm over stdio - minimax's own server, own profile -
// so this never touches Hermes's notebooklm-mcp.
const { spawn } = require("child_process");
const readline = require("readline");
const path = require("path");

const SERVER = path.join("C:\\Users\\apviz\\.minimax-agent\\projects", "google-layer", "minimax-notebooklm.js");
const c = spawn(process.execPath, [SERVER], { stdio: ["pipe", "pipe", "pipe"] });
const seen = [];
readline.createInterface({ input: c.stdout }).on("line", (l) => { if (l.trim()) seen.push(l); });
c.stderr.on("data", () => {});
let id = 0;
const call = (m, p, ms = 120000) => new Promise((res) => {
  const my = ++id;
  c.stdin.write(JSON.stringify({ jsonrpc: "2.0", id: my, method: m, params: p }) + "\n");
  const t0 = Date.now();
  const iv = setInterval(() => {
    const h = seen.find((l) => { try { return JSON.parse(l).id === my; } catch { return false; } });
    if (h || Date.now() - t0 > ms) { clearInterval(iv); res(h ? JSON.parse(h) : { error: "timeout" }); }
  }, 200);
});
(async () => {
  await call("initialize", { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "collector", version: "1" } });
  c.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n");
  const r = await call("tools/call", { name: "nblm_list_notebooks", arguments: {} });
  const txt = r.result?.content?.[0]?.text || "";
  let o = null; try { o = JSON.parse(txt); } catch {}
  if (!o || !o.notebooks) { console.log("FAILED: " + txt.slice(0, 300)); process.exit(1); }
  console.log(JSON.stringify({ authenticated: o.authenticated, count: o.notebooks.length, notebooks: o.notebooks }, null, 1));
  c.kill(); process.exit(0);
})().catch((e) => { console.log("ERR " + e.message); process.exit(1); });
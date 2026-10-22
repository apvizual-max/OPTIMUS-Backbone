// notebook-ask.js - query ONE notebook through minimax-notebooklm.
//
// Usage:  node notebook-ask.js <request-file.json>
// The file holds {"notebook":"SENTINEL Prime","question":"..."}.
//
// WHY A FILE AND NOT ARGV: a native Windows argument containing quotes and
// Romanian diacritics is the exact case that produces a mangled prompt, and a
// mangled prompt produces a plausible wrong answer rather than an error. A file
// cannot be re-parsed by the shell.
//
// Talks to minimax-notebooklm over stdio - minimax's OWN server, own Chrome
// profile, own CDP port - so it never touches Hermes's notebooklm-mcp.
const { spawn } = require("child_process");
const readline = require("readline");
const path = require("path");
const fs = require("fs");

const SERVER = path.join(__dirname, "minimax-notebooklm.js");
const reqFile = process.argv[2];

if (!reqFile) {
  console.log(JSON.stringify({ ok: false, error: "usage: node notebook-ask.js <request-file.json>" }));
  process.exit(2);
}

(async () => {
  let req;
  try {
    req = JSON.parse(await fs.promises.readFile(reqFile, "utf8"));
  } catch (e) {
    console.log(JSON.stringify({ ok: false, error: "request file is unreadable: " + e.message }));
    process.exit(2);
  }
  const notebook = String(req.notebook || "").trim();
  const question = String(req.question || "").trim();
  if (!notebook || !question) {
    console.log(JSON.stringify({ ok: false, error: "both 'notebook' and 'question' are required" }));
    process.exit(2);
  }

  const c = spawn(process.execPath, [SERVER], { stdio: ["pipe", "pipe", "pipe"] });
  const seen = [];
  readline.createInterface({ input: c.stdout }).on("line", (l) => { if (l.trim()) seen.push(l); });
  c.stderr.on("data", () => {});

  let id = 0;
  const call = (m, p, ms) => new Promise((res) => {
    const my = ++id;
    c.stdin.write(JSON.stringify({ jsonrpc: "2.0", id: my, method: m, params: p }) + "\n");
    const t0 = Date.now();
    const iv = setInterval(() => {
      const h = seen.find((l) => { try { return JSON.parse(l).id === my; } catch { return false; } });
      if (h || Date.now() - t0 > ms) { clearInterval(iv); res(h ? JSON.parse(h) : { error: "timeout" }); }
    }, 200);
  });

  await call("initialize", { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "ask", version: "1" } });
  c.stdin.write(JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }) + "\n");

  // NotebookLM takes 15-45 s to compose an answer. The budget must EXCEED the
  // measured duration or the timeout is a dead sensor, not caution.
  const r = await call("tools/call", { name: "nblm_ask", arguments: { notebook, question } }, 180000);
  const txt = (r.result && r.result.content && r.result.content[0] && r.result.content[0].text) || "";
  let o = null;
  try { o = JSON.parse(txt); } catch { /* handled below */ }

  if (!o) {
    console.log(JSON.stringify({ ok: false, error: "the server did not return parseable JSON", raw: txt.slice(0, 300) }));
    c.kill(); process.exit(1);
  }
  // The §10.2 breaker answers from memory with no network. That is a correct
  // answer to "what is the state", and it must not be reported as an answer to
  // the question - so it is surfaced as its own outcome.
  if (o.state === "UNAUTHENTICATED" || o.probe_suppressed) {
    console.log(JSON.stringify({
      ok: false, outcome: "UNAUTHENTICATED", circuit: o.circuit || null,
      reason: o.reason || null, retry_after_sec: o.retry_after_sec || null,
      remedy: o.remedy || "sign into notebook.google.com on the minimax profile"
    }));
    c.kill(); process.exit(3);
  }
  console.log(JSON.stringify({
    ok: true,
    notebook,
    question,
    answer: o.answer || null,
    submitted: o.submitted !== false,
    send_status: o.send_status || null,
    notebook_id: o.notebook_id || null
  }));
  c.kill(); process.exit(0);
})().catch((e) => {
  console.log(JSON.stringify({ ok: false, error: e.message }));
  process.exit(1);
});
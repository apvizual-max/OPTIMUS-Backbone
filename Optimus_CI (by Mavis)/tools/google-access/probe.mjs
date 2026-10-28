// probe.mjs - host side. Proves the Google_Access container works, with a
// REAL tool call, not just a health endpoint.
//
// Measured defect 2026-10-27 (two, same family - a literal that can drift):
//  1. The default URL pointed at 127.0.0.1:8765/mcp. Port 8765 on this host
//     is owned by a foreign host-native process (python, service "hc-backend"),
//     so the probe silently measured ANOTHER SERVER: it printed
//     HANDSHAKE=FAILED, TOOLS=0 and still exited 0.
//  2. The probe had no exit code of its own. A green exit code over a failed
//     measurement is worse than no exit code: it makes a broken probe look
//     like a working service.
//
// Exit codes: 0 = PASS (every check below verified), 1 = FAIL (measured and
// wrong), 2 = UNKNOWN (could not measure - wrong service, unreachable).
// UNKNOWN is never reported as success.
const MCP_URL = process.env.GA_URL || "http://127.0.0.1:8766/mcp";
const EXPECTED_SERVICE = process.env.GA_SERVICE || "Google_Access";
const MIN_TOOLS = Number(process.env.GA_MIN_TOOLS || 20);

let id = 0;
let failures = [];

async function rpc(method, params) {
  id += 1;
  const res = await fetch(MCP_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
    },
    body: JSON.stringify({ jsonrpc: "2.0", id, method, params: params || {} }),
  });
  const text = await res.text();
  let json;
  try {
    json = JSON.parse(text);
  } catch {
    const m = text.match(/data:\s*(\{.*\})/s);
    json = m ? JSON.parse(m[1]) : { raw: text.slice(0, 500) };
  }
  return json;
}

function flat(text) {
  return String(text || "").replace(/\s+/g, " ").slice(0, 900);
}

const healthUrl = MCP_URL.replace(/\/mcp$/, "/health");
let health;
try {
  const res = await fetch(healthUrl);
  health = await res.json();
} catch (err) {
  console.log("HEALTH=UNREACHABLE " + err.message + " url=" + healthUrl);
  console.log("VERDICT=UNKNOWN");
  process.exit(2);
}
console.log("HEALTH=" + JSON.stringify(health));

// Identity check: the port may belong to something else entirely. A health
// payload from a foreign service is UNKNOWN, not a pass.
if (health.service !== EXPECTED_SERVICE) {
  console.log(
    "SERVICE_MISMATCH expected=" + EXPECTED_SERVICE + " got=" + health.service + " url=" + MCP_URL
  );
  console.log("VERDICT=UNKNOWN");
  process.exit(2);
}
console.log("SERVICE_MATCH=" + EXPECTED_SERVICE);

if (health.grant !== "live") {
  console.log("GRANT_NOT_LIVE=" + health.grant);
  failures.push("grant not live");
}

const init = await rpc("initialize", {
  protocolVersion: "2024-11-05",
  capabilities: {},
  clientInfo: { name: "probe", version: "1.1" },
});
const handshakeOk = Boolean(init.result && init.result.serverInfo);
console.log(
  "HANDSHAKE=" +
    (handshakeOk
      ? init.result.serverInfo.name + " " + init.result.serverInfo.version
      : "FAILED " + JSON.stringify(init.error))
);
if (!handshakeOk) failures.push("handshake failed");

const list = await rpc("tools/list");
const tools = (list.result && list.result.tools) || [];
console.log("TOOLS=" + tools.length);
console.log("TOOL_NAMES=" + tools.map((t) => t.name).join(","));
if (tools.length < MIN_TOOLS) failures.push("tools " + tools.length + " < " + MIN_TOOLS);

const status = await rpc("tools/call", { name: "google_auth_status", arguments: {} });
const statusText =
  status.result && status.result.content ? status.result.content[0].text : JSON.stringify(status);
console.log("AUTH_STATUS=" + flat(statusText));

const call = await rpc("tools/call", { name: "gdrive_list", arguments: { page_size: 5 } });
const callText =
  call.result && call.result.content ? call.result.content[0].text : JSON.stringify(call);
console.log("GDRIVE_LIST=" + flat(callText));
console.log("GDRIVE_IS_ERROR=" + (call.result && call.result.isError ? "yes" : "no"));
if (call.result && call.result.isError) failures.push("gdrive_list returned an error");

const gmail = await rpc("tools/call", { name: "gmail_list", arguments: { max_results: 3 } });
const gmailText =
  gmail.result && gmail.result.content ? gmail.result.content[0].text : JSON.stringify(gmail);
console.log("GMAIL_LIST=" + flat(gmailText));
console.log("GMAIL_IS_ERROR=" + (gmail.result && gmail.result.isError ? "yes" : "no"));
if (gmail.result && gmail.result.isError) failures.push("gmail_list returned an error");

// Books needs a scope outside the current grant. An EXPLICIT refusal is an
// honest answer and is reported as INFO - it is not counted as a failure and
// it is not counted as a success.
const books = await rpc("tools/call", { name: "gbooks_search", arguments: { q: "optimus", max_results: 2 } });
const booksText =
  books.result && books.result.content ? books.result.content[0].text : JSON.stringify(books);
console.log("GBOOKS=" + flat(booksText).slice(0, 400));
console.log("GBOOKS_INFO=explicit scope refusal is reported, not a failure");

if (failures.length) {
  console.log("FAILURES=" + failures.join(" | "));
  console.log("VERDICT=FAIL");
  process.exit(1);
}
console.log("FAILURES=none");
console.log("VERDICT=PASS");
process.exit(0);

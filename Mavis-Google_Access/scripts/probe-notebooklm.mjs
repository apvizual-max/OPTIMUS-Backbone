// probe-notebooklm.mjs - measures the ExtendLM MCP path without printing secrets.
//
// Reads the token from the mounted volume, opens an MCP session against
// https://mcp.extendlm.com/mcp, lists the remote tool names, and calls the
// read-only extension_status / list_notebook_users tools when they exist.
//
// Output rules: ASCII only, tool NAMES only, never the token, never a
// credential body. A token is reported as length + presence.
//
// Usage: node probe-notebooklm.mjs [--url <mcp url>] [--data <dir>]
import fs from "node:fs";
import path from "node:path";

const argOf = (flag, dflt) => {
  const i = process.argv.indexOf(flag);
  return i !== -1 ? process.argv[i + 1] : dflt;
};

const URL_MCP = argOf("--url", process.env.GA_EXTENDLM_URL || "https://mcp.extendlm.com/mcp");
const DATA_DIR = argOf("--data", path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "..", "data"));

function sse(body) {
  // Streamable HTTP may answer as JSON or as an SSE frame: "event: message\ndata: {...}"
  const trimmed = body.trim();
  if (trimmed.startsWith("{")) return JSON.parse(trimmed);
  const out = [];
  for (const line of trimmed.split(/\r?\n/)) {
    if (line.startsWith("data:")) {
      const raw = line.slice(5).trim();
      if (!raw) continue;
      try {
        out.push(JSON.parse(raw));
      } catch {
        /* not a JSON frame, skip */
      }
    }
  }
  return out;
}

function scrub(text, token) {
  let t = String(text || "");
  if (token) t = t.split(token).join("[TOKEN]");
  t = t.replace(/\bya29\.[A-Za-z0-9._-]+/g, "[TOKEN]");
  t = t.replace(/\b1\/\/[A-Za-z0-9._-]{40,}/g, "[TOKEN]");
  return t;
}

async function rpc(method, params, sid, token) {
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json, text/event-stream",
    Authorization: "Bearer " + token,
  };
  if (sid) headers["mcp-session-id"] = sid;
  const res = await fetch(URL_MCP, {
    method: "POST",
    headers,
    body: JSON.stringify({ jsonrpc: "2.0", id: Date.now() % 100000, method, params }),
  });
  const body = await res.text();
  return { status: res.status, sid: res.headers.get("mcp-session-id"), frames: sse(body), raw: body };
}

(async () => {
  const cfgPath = path.join(DATA_DIR, "extendlm.json");
  let cfg;
  try {
    cfg = JSON.parse(fs.readFileSync(cfgPath, "utf8"));
  } catch (e) {
    console.log("TOKEN_FILE=ABSENT path=" + cfgPath);
    process.exitCode = 3;
    return;
  }
  const token = cfg.token;
  console.log("TOKEN_FILE=PRESENT token_len=" + (token ? token.length : 0) + " refresh=" + (cfg.refresh_token ? "yes" : "no"));
  console.log("MCP_URL=" + URL_MCP);
  if (!token) {
    console.log("VERDICT=NO_TOKEN");
    process.exitCode = 3;
    return;
  }

  const init = await rpc("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "google-access-probe", version: "1.0" },
  }, null, token);
  console.log("INIT_HTTP=" + init.status);
  const sid = init.sid;
  console.log("SESSION_ID=" + (sid ? "present" : "null"));

  const list = await rpc("tools/list", {}, sid, token);
  console.log("TOOLS_HTTP=" + list.status);
  let names = [];
  for (const f of list.frames) {
    if (f && f.result && Array.isArray(f.result.tools)) {
      names = f.result.tools.map((t) => t.name);
    }
  }
  console.log("TOOL_COUNT=" + names.length);
  console.log("TOOL_NAMES=" + names.join("|"));

  // Optional: print the input schema of named tools (names + required fields).
  const schemaArg = argOf("--schema", "");
  if (schemaArg) {
    const wanted = schemaArg.split(",").map((s) => s.trim()).filter(Boolean);
    for (const f of list.frames) {
      if (!f || !f.result || !Array.isArray(f.result.tools)) continue;
      for (const t of f.result.tools) {
        if (!wanted.includes(t.name)) continue;
        const req = (t.inputSchema && t.inputSchema.required) || [];
        const props = Object.keys((t.inputSchema && t.inputSchema.properties) || {});
        console.log("SCHEMA " + t.name + " REQUIRED=" + req.join(","));
        console.log("SCHEMA " + t.name + " PROPS=" + props.join(","));
        console.log("SCHEMA " + t.name + " DESC=" + String(t.description || "").slice(0, 400).replace(/\s+/g, " "));
      }
    }
  }

  // Read-only probes: only the ones that exist, and only a bounded, scrubbed body.
  let conn = null;
  let authUserId = null;
  const userRes = await rpc("tools/call", { name: "list_notebook_users", arguments: {} }, sid, token);
  const userText = userRes.frames
    .map((f) => (f && f.result && Array.isArray(f.result.content) ? f.result.content.map((c) => (c && c.text) || "").join("") : ""))
    .filter(Boolean)
    .join("");
  try {
    const parsed = JSON.parse(userText || "{}");
    conn = (parsed.connections || [])[0] || null;
    const sel = conn && ((conn.users || []).find((u) => u.is_selected) || (conn.users || [])[0]);
    authUserId = sel ? sel.auth_user_id : null;
  } catch {
    /* shape unknown, leave null */
  }

  for (const name of ["extension_status", "list_notebook_users", "list_notebooks", "get_notebooklm_capabilities"]) {
    if (!names.includes(name)) {
      console.log("PROBE " + name + " = NOT_PRESENT");
      continue;
    }
    const args = {};
    if (conn && conn.extension_connection) args.extension_connection = conn.extension_connection;
    if (authUserId) args.auth_user_id = authUserId;
    const call = await rpc("tools/call", { name, arguments: args }, sid, token);
    const text = call.frames
      .map((f) => {
        if (f && f.result && Array.isArray(f.result.content)) {
          return f.result.content.map((c) => (c && c.text) || "").join("\n");
        }
        if (f && f.error) return "RPC_ERROR " + JSON.stringify(f.error);
        return "";
      })
      .filter(Boolean)
      .join("\n");
    const shown = scrub(text, token).slice(0, 1200);
    console.log("PROBE " + name + " HTTP=" + call.status + " LEN=" + (text ? text.length : 0));
    if (shown) console.log("PROBE " + name + " BODY=" + shown.replace(/\s+/g, " ").slice(0, 900));
    // Shape probe: which top-level keys does the payload carry?
    try {
      const o = JSON.parse(text || "{}");
      console.log("PROBE " + name + " KEYS=" + Object.keys(o).join(","));
    } catch {
      console.log("PROBE " + name + " KEYS=NOT_JSON");
    }
  }

  console.log("VERDICT=MEASURED");
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exitCode = 2;
});

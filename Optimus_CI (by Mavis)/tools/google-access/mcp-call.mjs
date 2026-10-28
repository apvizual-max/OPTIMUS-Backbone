// mcp-call.mjs - call ONE tool on the Google_Access container (Streamable HTTP MCP).
// Usage: node mcp-call.mjs <tool_name> [json_args]
// Prints the JSON-RPC result. Never prints the credential: the container
// reports labels, lengths and HTTP statuses only.
const URL_BASE = process.env.GA_MCP_URL || "http://127.0.0.1:8766/mcp";

function parse(text) {
  if (!text) return null;
  const trimmed = text.trim();
  if (trimmed.startsWith("{")) {
    try {
      return JSON.parse(trimmed);
    } catch {
      /* fall through to SSE parsing */
    }
  }
  const m = trimmed.match(/data:\s*(\{[\s\S]*?\})\s*(?:\r?\n|$)/);
  if (m) {
    try {
      return JSON.parse(m[1]);
    } catch {
      return null;
    }
  }
  return null;
}

async function rpc(method, params, id, sessionId) {
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json, text/event-stream",
  };
  if (sessionId) headers["mcp-session-id"] = sessionId;
  const res = await fetch(URL_BASE, {
    method: "POST",
    headers,
    body: JSON.stringify({ jsonrpc: "2.0", id, method, params }),
  });
  const sid = res.headers.get("mcp-session-id");
  const text = await res.text();
  return { json: parse(text), sid, status: res.status, raw: text };
}

(async () => {
  const tool = process.argv[2];
  // Arguments may arrive as @path (a JSON file) because PowerShell strips
  // embedded double quotes when passing them to a native command.
  let args = {};
  const raw = process.argv[3];
  if (raw) {
    if (raw.startsWith("@")) {
      const fs = await import("node:fs");
      args = JSON.parse(fs.readFileSync(raw.slice(1), "utf8").replace(/^\uFEFF/, ""));
    } else {
      args = JSON.parse(raw);
    }
  }
  const init = await rpc(
    "initialize",
    {
      protocolVersion: "2024-11-05",
      capabilities: {},
      clientInfo: { name: "mavis-local", version: "1.0.0" },
    },
    1
  );
  await rpc("notifications/initialized", {}, null, init.sid);
  if (!tool) {
    const list = await rpc("tools/list", {}, 2, init.sid);
    const names = (list.json && list.json.result && list.json.result.tools ? list.json.result.tools : []).map(
      (t) => t.name
    );
    console.log("TOOLS=" + names.length);
    console.log(names.join("|"));
    return;
  }
  const res = await rpc("tools/call", { name: tool, arguments: args }, 2, init.sid);
  console.log("HTTP=" + res.status);
  const out = res.json && res.json.result ? res.json.result : res.json;
  if (out && out.content) {
    for (const c of out.content) {
      if (c.type === "text") console.log(c.text);
    }
    if (out.isError) console.log("IS_ERROR=1");
  } else {
    console.log(JSON.stringify(out, null, 2));
  }
  if (res.json && res.json.error) console.log("RPC_ERROR=" + JSON.stringify(res.json.error));
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exit(4);
});

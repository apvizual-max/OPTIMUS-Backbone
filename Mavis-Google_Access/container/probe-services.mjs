// probe-services.mjs - REAL service probe for the Google_Access container.
//
// Why it exists: a scope list is a CLAIM. A service works only if a live API
// call answers with real data. This probe calls every service tool and
// classifies the ANSWER, never the request:
//
//   OK      - the API answered with data (counts are printed)
//   REFUSED - the API answered with a refusal (MISSING_SCOPE / GOOGLE_HTTP_*)
//             - that is a measured refusal, not a crash
//   ERROR   - the call did not complete (transport, bad arguments)
//   SKIP    - the account has no object to probe with (no id), which is
//             reported as SKIP and never as success
//
// It prints no credential and no token: only labels, counts and status codes.
//
// Usage: node probe-services.mjs [--out <file>]
// Exit: 0 = every planned probe produced an answer (OK or REFUSED)
//       2 = at least one probe did not answer (ERROR or SKIP)
const URL_BASE = process.env.GA_MCP_URL || "http://127.0.0.1:8766/mcp";
const fs = await import("node:fs");

function parse(text) {
  if (!text) return null;
  const t = text.trim();
  if (t.startsWith("{")) {
    try {
      return JSON.parse(t);
    } catch {
      /* fall through */
    }
  }
  const m = t.match(/data:\s*(\{[\s\S]*?\})\s*(?:\r?\n|$)/);
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

function textOf(result) {
  if (!result || !result.content) return "";
  return result.content
    .filter((c) => c.type === "text")
    .map((c) => c.text)
    .join("\n");
}

// The refusal vocabulary of the server. Everything else that comes back as
// text is treated as data.
const REFUSAL = /MISSING_SCOPE|GOOGLE_HTTP_\d+|NO_CREDENTIAL|NO_EXTENDLM_TOKEN|NO_ID/;

function classify(result) {
  const text = textOf(result);
  const isError = !!(result && result.isError);
  if (REFUSAL.test(text)) {
    const m = text.match(/(MISSING_SCOPE:[^\n]*|GOOGLE_HTTP_\d+:[^\n]*|NO_CREDENTIAL|NO_EXTENDLM_TOKEN|NO_ID[^\n]*)/);
    return { status: "REFUSED", detail: (m ? m[1] : text).slice(0, 220) };
  }
  if (isError) {
    return { status: "ERROR", detail: text.replace(/\s+/g, " ").slice(0, 220) };
  }
  let obj = null;
  try {
    obj = JSON.parse(text);
  } catch {
    obj = null;
  }
  if (obj && typeof obj === "object") {
    const counts = [];
    for (const k of ["count", "totalItems", "total", "files", "messages", "items", "notes", "spaces", "videos", "events", "lists", "projects", "scripts", "sites", "contacts", "photos", "channels"]) {
      if (typeof obj[k] === "number") counts.push(k + "=" + obj[k]);
      else if (Array.isArray(obj[k])) counts.push(k + "=" + obj[k].length);
    }
    if (obj.grant_live !== undefined) counts.push("grant_live=" + obj.grant_live);
    if (obj.reauth_required !== undefined) counts.push("reauth_required=" + obj.reauth_required);
    // Evidence that the answer carried data, without printing its content:
    // the keys that came back and how much text they hold.
    const keys = Object.keys(obj).slice(0, 6).join("+");
    counts.push("keys=" + keys);
    counts.push("bytes=" + text.length);
    return { status: "OK", detail: counts.join(" ") };
  }
  if (text.trim()) return { status: "OK", detail: text.replace(/\s+/g, " ").slice(0, 160) };
  return { status: "ERROR", detail: "empty answer" };
}

const PLAN = [
  { service: "identity", tool: "google_auth_status", args: {} },
  { service: "drive", tool: "gdrive_list", args: { page_size: 5 } },
  { service: "gmail", tool: "gmail_list", args: { max_results: 3 } },
  { service: "calendar", tool: "gcalendar_list", args: { max_results: 3 } },
  { service: "photos", tool: "gphotos_list", args: { page_size: 3 } },
  { service: "books", tool: "gbooks_search", args: { q: "Optimus", max_results: 3 } },
  { service: "tasks", tool: "gtasks_list", args: {} },
  { service: "keep", tool: "gkeep_list", args: {} },
  { service: "sites", tool: "gsites_list", args: {} },
  { service: "apps-script", tool: "gscript_list", args: {} },
  { service: "chat", tool: "gchat_spaces", args: {} },
  { service: "contacts", tool: "gcontacts_list", args: { max_results: 5 } },
  { service: "youtube", tool: "youtube_my_videos", args: { max_results: 3 } },
  { service: "notebooklm", tool: "notebooklm_ask", args: { question: "probe" } },
];

(async () => {
  const init = await rpc(
    "initialize",
    { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "probe-services", version: "1.0.0" } },
    1
  );
  await rpc("notifications/initialized", {}, null, init.sid);
  if (!init.json) {
    console.log("FATAL=no initialize answer (container not reachable at " + URL_BASE + ")");
    console.log("INIT_HTTP=" + init.status);
    console.log("INIT_RAW=" + String(init.raw || "").slice(0, 300));
    process.exitCode = 3;
    return;
  }

  const lines = [];
  const tally = { OK: 0, REFUSED: 0, ERROR: 0, SKIP: 0 };

  const call = async (tool, args) => {
    const res = await rpc("tools/call", { name: tool, arguments: args }, 2, init.sid);
    if (!res.json) return { status: "ERROR", detail: "no json (http " + res.status + ")" };
    if (res.json.error) return { status: "ERROR", detail: "rpc: " + JSON.stringify(res.json.error).slice(0, 200) };
    return classify(res.json.result);
  };

  // Discover real object ids so Docs/Sheets are probed against real files.
  const docId = await (async () => {
    const res = await rpc(
      "tools/call",
      { name: "gdrive_list", arguments: { q: "mimeType='application/vnd.google-apps.document' and trashed=false", page_size: 3 } },
      3,
      init.sid
    );
    const t = textOf(res.json && res.json.result);
    try {
      const o = JSON.parse(t);
      return o.files && o.files[0] ? o.files[0].id : null;
    } catch {
      return null;
    }
  })();
  const sheetId = await (async () => {
    const res = await rpc(
      "tools/call",
      { name: "gdrive_list", arguments: { q: "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false", page_size: 3 } },
      4,
      init.sid
    );
    const t = textOf(res.json && res.json.result);
    try {
      const o = JSON.parse(t);
      return o.files && o.files[0] ? o.files[0].id : null;
    } catch {
      return null;
    }
  })();

  const plan = PLAN.slice();
  plan.push({
    service: "docs",
    tool: "gdocs_get",
    args: docId ? { document_id: docId } : {},
    skip: docId ? null : "no Google Doc in the account to read",
  });
  plan.push({
    service: "sheets",
    tool: "gsheets_read",
    args: sheetId ? { spreadsheet_id: sheetId, range: "A1:D20" } : {},
    skip: sheetId ? null : "no Google Sheet in the account to read",
  });

  for (const p of plan) {
    if (p.skip) {
      tally.SKIP++;
      const line = "SERVICE=" + p.service + " TOOL=" + p.tool + " STATUS=SKIP DETAIL=" + p.skip;
      lines.push(line);
      console.log(line);
      continue;
    }
    let r;
    try {
      r = await call(p.tool, p.args);
    } catch (e) {
      r = { status: "ERROR", detail: "transport: " + String((e && e.message) || e).slice(0, 180) };
    }
    tally[r.status] = (tally[r.status] || 0) + 1;
    const line = "SERVICE=" + p.service + " TOOL=" + p.tool + " STATUS=" + r.status + " DETAIL=" + r.detail;
    lines.push(line);
    console.log(line);
  }

  const unanswered = tally.ERROR + tally.SKIP;
  const verdict = unanswered === 0 ? "PASS" : "PARTIAL";
  lines.push("TALLY=" + JSON.stringify(tally));
  lines.push("VERDICT=" + verdict);

  const outIdx = process.argv.indexOf("--out");
  const outPath = outIdx !== -1 ? process.argv[outIdx + 1] : "data/last-service-probe.txt";
  try {
    fs.writeFileSync(outPath, lines.join("\n") + "\n", "utf8");
    console.log("WROTE=" + outPath);
  } catch (e) {
    console.log("WROTE_FAILED=" + (e && e.message ? e.message : String(e)));
  }
  console.log("VERDICT=" + verdict);
  // Exit code without process.exit(): a hard exit while an undici socket is
  // closing aborts Node's event loop ("Assertion failed: UV_HANDLE_CLOSING")
  // and turns a clean verdict into a crash.
  process.exitCode = unanswered === 0 ? 0 : 2;
})().catch((e) => {
  console.log("FATAL=" + (e && e.message ? e.message : String(e)));
  process.exitCode = 3;
});

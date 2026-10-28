// probe-extendlm-refresh.mjs - proves the ExtendLM refresh path works on
// the real token endpoint, before it is trusted inside the container.
//
// The access token from the authorization code expires in about three hours.
// If the refresh fails, the whole NotebookLM capability dies at that moment.
// This probe performs the real refresh, persists the result (a rotated
// refresh token MUST be written, or the next refresh fails), and then makes
// a live MCP call with the fresh token.
//
// Usage: node probe-extendlm-refresh.mjs [--data <dir>]
import fs from "node:fs";
import path from "node:path";

const argOf = (flag, dflt) => {
  const i = process.argv.indexOf(flag);
  return i !== -1 ? process.argv[i + 1] : dflt;
};
const DATA_DIR = argOf("--data", "C:/Users/apviz/.minimax/google-access/data");
const CFG = path.join(DATA_DIR, "extendlm.json");
const MCP = "https://mcp.extendlm.com/mcp";

(async () => {
  const cfg = JSON.parse(fs.readFileSync(CFG, "utf8"));
  console.log("BEFORE token_len=" + (cfg.token ? cfg.token.length : 0) + " refresh_len=" + (cfg.refresh_token ? cfg.refresh_token.length : 0) + " expires_at=" + cfg.expires_at);
  if (!cfg.refresh_token) {
    console.log("NO_REFRESH_TOKEN");
    process.exitCode = 3;
    return;
  }
  const res = await fetch(cfg.token_endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: cfg.refresh_token,
      client_id: cfg.client_id,
    }).toString(),
  });
  const text = await res.text();
  console.log("REFRESH_HTTP=" + res.status);
  if (!res.ok) {
    console.log("REFRESH_BODY=" + text.slice(0, 300));
    process.exitCode = 2;
    return;
  }
  const j = JSON.parse(text);
  const rotated = Boolean(j.refresh_token && j.refresh_token !== cfg.refresh_token);
  console.log("NEW_TOKEN_LEN=" + (j.access_token ? j.access_token.length : 0) + " expires_in=" + j.expires_in + " rotated_refresh=" + rotated);

  const now = Date.now();
  const next = {
    ...cfg,
    token: j.access_token,
    access_token: j.access_token,
    refresh_token: j.refresh_token || cfg.refresh_token,
    token_type: j.token_type || cfg.token_type || "Bearer",
    scope: j.scope || cfg.scope,
    expires_at: j.expires_in ? now + Number(j.expires_in) * 1000 : null,
    refreshed_at: new Date(now).toISOString(),
  };
  const tmp = CFG + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(next, null, 2), "utf8");
  fs.renameSync(tmp, CFG);
  console.log("PERSISTED=1 expires_at=" + next.expires_at);

  // Live proof: the fresh token must work on the real MCP endpoint.
  const rpc = await fetch(MCP, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
      Authorization: "Bearer " + next.token,
    },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/list", params: {} }),
  });
  const body = await rpc.text();
  let count = 0;
  for (const line of body.split(/\r?\n/)) {
    if (!line.startsWith("data:")) continue;
    try {
      const f = JSON.parse(line.slice(5).trim());
      if (f && f.result && Array.isArray(f.result.tools)) count = f.result.tools.length;
    } catch {
      /* not a frame */
    }
  }
  console.log("LIVE_TOOLS_HTTP=" + rpc.status + " TOOL_COUNT=" + count);
  console.log("VERDICT=" + (rpc.status === 200 && count > 0 ? "REFRESH_WORKS" : "REFRESH_UNPROVEN"));
  if (rpc.status !== 200 || count === 0) process.exitCode = 2;
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exitCode = 2;
});

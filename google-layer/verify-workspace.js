// Prove the narrowed grant is BOTH sufficient and actually read-only.
// Sufficient: Gmail, Calendar and Drive all answer. Read-only: a write is
// attempted and REFUSED. The second half is the half that matters - a token
// that cannot write is the whole reason the scopes were narrowed, so it has to
// be demonstrated rather than assumed from the scope name.
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const gapi = require(
  path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules",
    "gdrive-mcp", "node_modules", "googleapis")
);
const { google } = gapi;

const tokPath = path.join(os.homedir(), ".google-mcp", "tokens", "apvizual.json");

const line = (s) => console.log(s);

(async () => {
  const creds = JSON.parse(await fs.promises.readFile(tokPath, "utf8"));
  const auth = new google.auth.OAuth2(creds.client_id, creds.client_secret);
  auth.setCredentials({ refresh_token: creds.refresh_token });

  // ---- 1. Drive: is it sufficient? ----
  try {
    const sw = Date.now();
    const r = await google.drive({ version: "v3", auth })
      .files.list({ pageSize: 3, fields: "files(id,name)" });
    line(`Drive  files.list   OK  ${Date.now() - sw}ms  ${r.data.files.length} file(s)`);
    r.data.files.forEach((f) => line(`         - ${f.name}`));
  } catch (e) { line(`Drive  files.list   FAILED: ${e.message}`); }

  // ---- 2. Gmail: is it sufficient? ----
  try {
    const sw = Date.now();
    const r = await google.gmail({ version: "v1", auth })
      .users.messages.list({ userId: "me", maxResults: 3 });
    line(`Gmail  messages.list OK  ${Date.now() - sw}ms  ${(r.data.messages || []).length} message(s)`);
  } catch (e) {
    const why = (e.response && e.response.data && JSON.stringify(e.response.data).slice(0, 200)) || e.message;
    line(`Gmail  messages.list FAILED: ${why}`);
  }

  // ---- 3. Calendar: is it sufficient? ----
  try {
    const sw = Date.now();
    const r = await google.calendar({ version: "v3", auth })
      .calendarList.list({ maxResults: 3 });
    const items = (r.data.items || []).map((c) => c.summary);
    line(`Cal    calendarList  OK  ${Date.now() - sw}ms  ${items.length} calendar(s)`);
    items.forEach((c) => line(`         - ${c}`));
  } catch (e) {
    const why = (e.response && e.response.data && JSON.stringify(e.response.data).slice(0, 200)) || e.message;
    line(`Cal    calendarList  FAILED: ${why}`);
  }

  // ---- 4. THE IMPORTANT ONE: can it actually write? ----
  line("");
  line("Now attempting a WRITE that the read-only grant should refuse:");
  try {
    const r = await google.drive({ version: "v3", auth }).files.create({
      requestBody: { name: "mavis-write-probe-should-not-exist" },
      media: { mimeType: "text/plain", body: "probe" },
      fields: "id",
    });
    line(`  !! WRITE SUCCEEDED (id ${r.data.id}) - the grant is NOT read-only.`);
    line(`     Delete it: drive.google.com/drive/u/0/search?q=${encodeURIComponent("mavis-write-probe-should-not-exist")}`);
  } catch (e) {
    const st = e.response && e.response.status;
    const why = (e.response && e.response.data && JSON.stringify(e.response.data).slice(0, 220)) || e.message;
    line(`  WRITE REFUSED (HTTP ${st}) - the grant is genuinely read-only.`);
    line(`     ${why}`);
  }
})();

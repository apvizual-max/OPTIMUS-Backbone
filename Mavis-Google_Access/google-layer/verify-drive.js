// Prove the credential works against the LIVE Drive API. The consent page
// says "Drive authorized"; that proves a code was exchanged, not that the
// token can read anything. The only evidence that matters is a real listing.
const path = require("node:path");
const os = require("node:os");
const { install } = require("./bun-secrets-shim.js");

install();

const gapi = require(
  path.join(os.homedir(), "AppData", "Roaming", "npm", "node_modules",
    "gdrive-mcp", "node_modules", "googleapis")
);
const { google } = gapi;

(async () => {
  const clientId = await Bun.secrets.get({ service: "gdrive-mcp", name: "client_id" });
  const clientSecret = await Bun.secrets.get({ service: "gdrive-mcp", name: "client_secret" });
  const refreshToken = await Bun.secrets.get({ service: "gdrive-mcp", name: "refresh_token" });

  console.log("client_id      :", clientId ? "present" : "MISSING");
  console.log("client_secret  :", clientSecret ? "present" : "MISSING");
  console.log("refresh_token  :", refreshToken ? `present (${refreshToken.length} chars)` : "MISSING");
  if (!clientId || !clientSecret || !refreshToken) process.exit(1);

  const auth = new google.auth.OAuth2(clientId, clientSecret);
  auth.setCredentials({ refresh_token: refreshToken });

  // About the token itself, from Google - not from our own file.
  const oauth2 = google.oauth2({ version: "v2", auth });
  try {
    const me = await oauth2.userinfo.get();
    console.log("\nTOKENID live.  Google says this token belongs to:", me.data.email || "(no email)");
    const granted = (me.data.scope || "").split(" ").filter(Boolean);
    console.log("scopes Google confirms:", granted.join("  ") || "(not reported)");
  } catch (e) {
    console.log("\nuserinfo failed:", e.message);
  }

  // The actual claim: can it read the Drive?
  const drive = google.drive({ version: "v3", auth });
  const sw = Date.now();
  try {
    const res = await drive.files.list({
      pageSize: 12,
      fields: "files(id,name,mimeType,modifiedTime,size,owners(emailAddress))",
      orderBy: "modifiedTime desc",
    });
    const files = res.data.files || [];
    console.log(`\nDRIVE v3 files.list -> HTTP 200 in ${Date.now() - sw}ms, ${files.length} of most recently modified:`);
    for (const f of files) {
      const owner = (f.owners && f.owners[0] && f.owners[0].emailAddress) || "-";
      const sz = f.size ? `${(Number(f.size) / 1024).toFixed(0)} KB` : "-";
      console.log(`  ${(f.mimeType || "").padEnd(30).slice(0, 30)} ${String(sz).padStart(9)}  ${(f.name || "").slice(0, 52)}`);
    }
    if (!files.length) console.log("  (Drive is genuinely empty - a 200 with no files is still a working token)");
    console.log("\nRESULT: DRIVE IS CONNECTED AND READABLE");
  } catch (e) {
    const msg = (e.response && e.response.data && JSON.stringify(e.response.data)) || e.message;
    console.log(`\nDRIVE v3 files.list FAILED after ${Date.now() - sw}ms:`);
    console.log("  ", String(msg).slice(0, 400));
    process.exit(2);
  }
})();

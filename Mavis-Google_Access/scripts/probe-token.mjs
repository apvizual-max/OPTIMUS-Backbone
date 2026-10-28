// probe-token.mjs - what does the live access token ACTUALLY carry, and how
// do the Google APIs answer it?
//
// A stored scope string is a claim about the grant. The tokeninfo endpoint is
// the measured truth about the minted token, and the API answer is the truth
// about the service. This prints both, plus one direct call per service in
// question - with no token, no secret and no content in the output.
//
// Usage: node probe-token.mjs [service ...]
import fs from "node:fs";
import path from "node:path";

const GA_DIR = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "..");
const CRED = path.join(GA_DIR, "data", "credentials.json");

const CHECKS = {
  photos: { url: "https://photoslibrary.googleapis.com/v1/mediaItems?pageSize=1" },
  "photos-albums": { url: "https://photoslibrary.googleapis.com/v1/albums?pageSize=1" },
  chat: { url: "https://chat.googleapis.com/v1/spaces?pageSize=1" },
  drive: { url: "https://www.googleapis.com/drive/v3/files?pageSize=1&fields=files(id)" },
};

const wanted = process.argv.slice(2);
const names = wanted.length ? wanted : Object.keys(CHECKS);

const cred = JSON.parse(fs.readFileSync(CRED, "utf8"));

const tok = await fetch("https://oauth2.googleapis.com/token", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({
    grant_type: "refresh_token",
    refresh_token: cred.refresh_token,
    client_id: cred.client_id,
    client_secret: cred.client_secret,
  }).toString(),
});
const tokJson = await tok.json();
if (!tok.ok || !tokJson.access_token) {
  console.log("TOKEN_MINT_FAILED http=" + tok.status + " error=" + (tokJson.error || "unknown"));
  process.exitCode = 3;
} else {
  const info = await fetch("https://oauth2.googleapis.com/tokeninfo?access_token=" + encodeURIComponent(tokJson.access_token));
  const infoJson = await info.json();
  const scopes = String(infoJson.scope || "").split(" ").filter(Boolean);
  console.log("TOKEN_MINT=ok expires_in=" + tokJson.expires_in + " scope_count=" + scopes.length);
  console.log("TOKENINFO_SCOPE_COUNT=" + scopes.length);
  scopes.sort().forEach((s) => console.log("  SCOPE " + s));
  console.log("GRANTED_HAS_PHOTOS=" + scopes.some((s) => s.includes("photoslibrary")));
  console.log("GRANTED_HAS_CHAT_SPACES=" + scopes.some((s) => s.includes("chat.spaces")));

  for (const name of names) {
    const c = CHECKS[name];
    if (!c) {
      console.log("CHECK=" + name + " STATUS=SKIP unknown-check");
      continue;
    }
    const r = await fetch(c.url, { headers: { Authorization: "Bearer " + tokJson.access_token } });
    const body = await r.text();
    let summary = body.slice(0, 220).replace(/\s+/g, " ");
    try {
      const o = JSON.parse(body);
      if (o.error) {
        summary = "code=" + o.error.code + " status=" + o.error.status + " msg=" + String(o.error.message).slice(0, 120);
        const reason = o.error.details && o.error.details.find((d) => d.reason);
        if (reason) summary += " reason=" + reason.reason;
      } else {
        const keys = Object.keys(o).slice(0, 5).join("+");
        summary = "keys=" + keys + " bytes=" + body.length;
      }
    } catch {
      /* keep raw summary */
    }
    console.log("CHECK=" + name + " HTTP=" + r.status + " DETAIL=" + summary);
  }
}

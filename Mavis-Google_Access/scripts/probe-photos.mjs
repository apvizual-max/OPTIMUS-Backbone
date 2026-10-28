// probe-photos.mjs - WHY does Google Photos Library refuse this account?
//
// MEASURED 2026-10-27 12:40: with a grant that carries photoslibrary,
// photoslibrary.readonly and photoslibrary.appendonly, the container's
// gphotos_list still gets GOOGLE_HTTP_403 "Request had insufficient
// authentication scopes" - while chat.spaces.readonly (the other newly
// granted scope) started answering immediately. So the refusal is NOT the
// grant. It is either the API's own account-level rule or something in the
// request shape.
//
// This probe answers that with numbers and the API's own error body. It
// never prints a token: only lengths, HTTP statuses and the response body
// (which carries no credential).
//
// Usage: node scripts/probe-photos.mjs [--cred <path>]
"use strict";
import fs from "node:fs";
import path from "node:path";

const CRED =
  (process.argv.includes("--cred") ? process.argv[process.argv.indexOf("--cred") + 1] : null) ||
  "C:\\Users\\apviz\\.minimax\\google-access\\data\\credentials.json";
const TOKEN_URL = "https://oauth2.googleapis.com/token";
const HOST = "https://photoslibrary.googleapis.com";

function readJson(p) {
  try {
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

async function accessToken(c) {
  const body = new URLSearchParams({
    client_id: c.client_id,
    client_secret: c.client_secret,
    refresh_token: c.refresh_token,
    grant_type: "refresh_token",
  });
  const res = await fetch(TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  const j = await res.json().catch(() => ({}));
  return { status: res.status, token: j.access_token || null, scope: j.scope || "", error: j.error || "" };
}

async function call(label, url, token) {
  const res = await fetch(url, { headers: { Authorization: "Bearer " + token } });
  const text = await res.text();
  console.log("---- " + label);
  console.log("URL=" + url.replace(token, "<token>"));
  console.log("HTTP=" + res.status);
  console.log("BODY=" + text.slice(0, 900));
  return res.status;
}

(async () => {
  const c = readJson(CRED);
  if (!c) {
    console.log("CREDENTIAL_ABSENT=" + CRED);
    process.exit(2);
  }
  const scopes = String(c.scope || "").split(/\s+/).filter(Boolean);
  console.log("CREDENTIAL_FIELDS=" + Object.keys(c).join(","));
  console.log("SCOPE_COUNT=" + scopes.length);
  for (const s of scopes.filter((x) => /photo|chat\.spaces/.test(x))) console.log("SCOPE=" + s);

  const t = await accessToken(c);
  console.log("TOKEN_HTTP=" + t.status + " TOKEN_LEN=" + (t.token ? t.token.length : 0) + " ERROR=" + t.error);
  if (!t.token) process.exit(3);
  console.log("TOKEN_SCOPE_HAS_PHOTOS=" + /photoslibrary/.test(t.scope));
  console.log("TOKEN_SCOPE_HAS_CHAT_SPACES=" + /chat\.spaces\.readonly/.test(t.scope));

  const mediaItems = await call("mediaItems.list", HOST + "/v1/mediaItems?pageSize=1", t.token);
  const albums = await call("albums.list", HOST + "/v1/albums?pageSize=1", t.token);

  // The write path, proven WITHOUT creating anything.
  //
  // The Photos Library API has NO albums.delete - a created album can only be
  // renamed or unshared. So a test album would be permanent litter in the
  // user's library. Instead: POST /v1/albums with an EMPTY body.
  //   - scope missing  -> 403 insufficient authentication scopes
  //   - scope granted  -> 400 invalid argument (album.title is required)
  // A 400 therefore PROVES the authorization passed, and creates nothing.
  const wr = await fetch(HOST + "/v1/albums", {
    method: "POST",
    headers: { Authorization: "Bearer " + t.token, "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  const wrBody = await wr.text();
  console.log("---- albums.create (empty body - authorization probe, creates nothing)");
  console.log("HTTP=" + wr.status);
  console.log("BODY=" + wrBody.slice(0, 300));
  const writeAuthorized = wr.status === 400; // 403 would mean the scope is not effective
  console.log("WRITE_PATH_AUTHORIZED=" + writeAuthorized + " (400 = scope accepted, no album created)");

  // A control: the same token against an API whose scope we hold.
  const drive = await call(
    "drive.files.list (control)",
    "https://www.googleapis.com/drive/v3/files?pageSize=1&fields=files(id,name)",
    t.token
  );

  console.log("MEDIAITEMS_HTTP=" + mediaItems + " ALBUMS_HTTP=" + albums + " DRIVE_CONTROL_HTTP=" + drive);
  console.log("VERDICT=" + (mediaItems === 200 && albums === 200 && drive === 200 && writeAuthorized ? "PASS" : "CHECK"));
  process.exit(0);
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exit(4);
});

// probe-account.mjs - WHO is the token, and for WHICH project?
//
// MEASURED 2026-10-27 12:45: the Photos Library API answers 403 "Request had
// insufficient authentication scopes" even though the token demonstrably
// carries photoslibrary + photoslibrary.readonly (discovery doc confirms
// mediaItems.list accepts both), the account has a real Photos library
// (100.4 GB used, albums visible in the web app), and Drive on the SAME
// token answers 200. So the refusal is not about the scope string, not about
// the library, and not about the token.
//
// Two remaining causes, both measurable here:
//   1. the account type - the Photos Library API does not serve managed
//      (Workspace/enterprise) accounts the way it serves personal accounts;
//   2. the project match - the API must be enabled on the SAME project that
//      owns the OAuth client, otherwise the token's authorized party has no
//      serviceusage permission for that service.
//
// This probe prints only shapes and lengths, never a token.
//
// Usage: node scripts/probe-account.mjs
"use strict";
import fs from "node:fs";

const CRED = "C:\\Users\\apviz\\.minimax\\google-access\\data\\credentials.json";
const TOKEN_URL = "https://oauth2.googleapis.com/token";

function readJson(p) {
  try {
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}

function domainOf(email) {
  const s = String(email || "");
  const at = s.lastIndexOf("@");
  return at === -1 ? "(none)" : s.slice(at + 1);
}

(async () => {
  const c = readJson(CRED);
  if (!c) {
    console.log("CREDENTIAL_ABSENT=1");
    process.exit(2);
  }
  // The OAuth client id starts with the owning GCP project number.
  const m = String(c.client_id || "").match(/^(\d+)\./);
  console.log("CLIENT_PROJECT_NUMBER=" + (m ? m[1] : "(unparsed)"));
  console.log("CLIENT_ID_PREFIX=" + String(c.client_id || "").slice(0, 30));

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
  if (res.status !== 200 || !j.access_token) {
    console.log("TOKEN_HTTP=" + res.status + " ERROR=" + (j.error || ""));
    process.exit(3);
  }
  const token = j.access_token;
  console.log("TOKEN_HTTP=200 TOKEN_LEN=" + token.length);

  const ui = await fetch("https://www.googleapis.com/oauth2/v2/userinfo", {
    headers: { Authorization: "Bearer " + token },
  });
  const uj = await ui.json().catch(() => ({}));
  console.log("USERINFO_HTTP=" + ui.status);
  console.log("ACCOUNT_DOMAIN=" + domainOf(uj.email));
  console.log("HOSTED_DOMAIN=" + (uj.hd || "(none -> personal account)"));
  console.log("EMAIL_VERIFIED=" + uj.email_verified);
  console.log("SUB_LEN=" + (uj.sub ? String(uj.sub).length : 0));

  // OAuth2 tokeninfo: what the token itself says about its scopes.
  const ti = await fetch("https://oauth2.googleapis.com/tokeninfo?access_token=" + encodeURIComponent(token));
  const tj = await ti.json().catch(() => ({}));
  const tokenScopes = String(tj.scope || "").split(/\s+/).filter(Boolean);
  console.log("TOKENINFO_HTTP=" + ti.status);
  console.log("TOKENINFO_SCOPE_COUNT=" + tokenScopes.length);
  console.log(
    "TOKENINFO_HAS_PHOTOS_READONLY=" + tokenScopes.includes("https://www.googleapis.com/auth/photoslibrary.readonly")
  );
  console.log("TOKENINFO_HAS_PHOTOS_FULL=" + tokenScopes.includes("https://www.googleapis.com/auth/photoslibrary"));
  console.log("TOKENINFO_HAS_PHOTOS_APPONLY=" + tokenScopes.includes("https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata"));
  process.exit(0);
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exit(4);
});

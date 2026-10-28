// probe-photos-library.mjs - measures WHAT the Photos Library API actually
// returns for the live credential, with real counts.
//
// The question that matters: does mediaItems.list return the user's library,
// or only app-created media? A 200 with an empty array and a 200 with a
// populated array look identical in a log line - only a parsed count tells
// them apart. And the account's own library size decides whether "empty"
// means "app-scoped access" or "nothing to read".
//
// Usage: node probe-photos-library.mjs [--data <dir>]
import fs from "node:fs";
import path from "node:path";

const argOf = (flag, dflt) => {
  const i = process.argv.indexOf(flag);
  return i !== -1 ? process.argv[i + 1] : dflt;
};
const DATA_DIR = argOf("--data", path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "..", "..", "..", "..", "apviz", ".minimax", "google-access", "data"));
const TOKEN_URL = "https://oauth2.googleapis.com/token";
const HOST = "https://photoslibrary.googleapis.com/v1";

function scrub(text, token) {
  let t = String(text || "");
  if (token) t = t.split(token).join("[TOKEN]");
  return t;
}

async function accessToken(creds) {
  const res = await fetch(TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "refresh_token",
      refresh_token: creds.refresh_token,
      client_id: creds.client_id,
      client_secret: creds.client_secret,
    }).toString(),
  });
  const j = await res.json();
  if (!res.ok) throw new Error("token http " + res.status + " " + JSON.stringify(j).slice(0, 200));
  return j.access_token;
}

async function api(pathname, token, params) {
  const url = HOST + pathname + (params ? "?" + new URLSearchParams(params).toString() : "");
  const res = await fetch(url, { headers: { Authorization: "Bearer " + token } });
  const text = await res.text();
  let json = {};
  try {
    json = JSON.parse(text);
  } catch {
    /* not json */
  }
  return { url, status: res.status, json, text };
}

(async () => {
  const cfg = JSON.parse(fs.readFileSync(path.join(DATA_DIR, "credentials.json"), "utf8"));
  const token = await accessToken(cfg);
  console.log("TOKEN_OK scopes=" + (cfg.scope || "").split(/\s+/).filter((s) => s.includes("photos")).length + " photos-scopes");

  const items = await api("/mediaItems", token, { pageSize: "50" });
  const arr = Array.isArray(items.json.mediaItems) ? items.json.mediaItems : null;
  console.log("mediaItems.list HTTP=" + items.status);
  console.log("mediaItems.keys=" + Object.keys(items.json).join(","));
  console.log("mediaItems.count=" + (arr === null ? "KEY_ABSENT" : arr.length));
  console.log("mediaItems.has_nextPageToken=" + Boolean(items.json.nextPageToken));
  if (arr && arr.length) {
    const it = arr[0];
    console.log("first_item.keys=" + Object.keys(it).join(","));
    console.log("first_item.mimeType=" + (it.mimeType || "") + " productUrl_present=" + Boolean(it.productUrl));
  }

  const albums = await api("/albums", token, { pageSize: "50" });
  const aarr = Array.isArray(albums.json.albums) ? albums.json.albums : null;
  console.log("albums.list HTTP=" + albums.status);
  console.log("albums.keys=" + Object.keys(albums.json).join(","));
  console.log("albums.count=" + (aarr === null ? "KEY_ABSENT" : aarr.length));

  // Control: a scope the account definitely has, on a definitely non-empty
  // library (Drive). If Drive answers 200 with items and Photos answers 200
  // with none, the token works and the emptiness is about the library, not
  // about the credential.
  const drive = await fetch("https://www.googleapis.com/drive/v3/files?pageSize=3&fields=files(id,name)", {
    headers: { Authorization: "Bearer " + token },
  });
  const dj = await drive.json().catch(() => ({}));
  console.log("CONTROL drive HTTP=" + drive.status + " files=" + (Array.isArray(dj.files) ? dj.files.length : "n/a"));

  console.log("RAW_mediaItems=" + scrub(items.text, token).slice(0, 600).replace(/\s+/g, " "));
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exitCode = 2;
});

// picker-watch.mjs - watch a Photo Picker session and CAPTURE the selection.
//
// WHY: the picker needs a human to choose the photos - that part is Google's
// design, not a limitation of this setup. But everything after the click
// ("Done") is mechanical, and it must not depend on a conversation being open.
// So this watcher polls the session, and when mediaItemsSet flips to true it
// lists the picked media and writes them to disk.
//
// Measured 2026-10-28: the picker URI loads correctly only in a browser
// signed in as the account that owns the session (apvizual@gmail.com, the
// token's account, verified through oauth2 tokeninfo). In a browser that is
// not signed in as that account, or in an embedded frame, Google answers
// "Couldn't open Google Photos" - the same message for both causes.
//
// Usage: node picker-watch.mjs --session <id> [--out <file>] [--data <dir>]
import fs from "node:fs";
import path from "node:path";

const argOf = (flag, dflt) => {
  const i = process.argv.indexOf(flag);
  return i !== -1 ? process.argv[i + 1] : dflt;
};
const DATA = argOf("--data", "C:/Users/apviz/.minimax/google-access/data");
const SESSION = argOf("--session");
const OUT = argOf("--out", path.join(DATA, "picked-media.json"));
const CREDS = path.join(DATA, "credentials.json");
const PICKER = "https://photospicker.googleapis.com";

async function accessToken() {
  const c = JSON.parse(fs.readFileSync(CREDS, "utf8"));
  const body = new URLSearchParams({
    client_id: c.client_id,
    client_secret: c.client_secret,
    refresh_token: c.refresh_token,
    grant_type: "refresh_token",
  }).toString();
  const r = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  const j = await r.json();
  if (!j.access_token) throw new Error("TOKEN_FAILED " + r.status + " " + JSON.stringify(j).slice(0, 200));
  return j.access_token;
}

async function api(token, url, method = "GET") {
  const r = await fetch(url, { method, headers: { Authorization: "Bearer " + token } });
  const text = await r.text();
  let body = {};
  try {
    body = JSON.parse(text);
  } catch {
    /* not json */
  }
  return { status: r.status, body };
}

(async () => {
  if (!SESSION) {
    console.log("SESSION_REQUIRED");
    process.exitCode = 2;
    return;
  }
  const token = await accessToken();

  const s = await api(token, PICKER + "/v1/sessions/" + encodeURIComponent(SESSION));
  if (s.status !== 200) {
    // MEASURED 2026-10-28: a session that the user completed - and that this
    // watcher then deleted, as the API asks - answers 404 ENTITY_NOT_FOUND on
    // every later poll. That is the designed end of a picker session, NOT a
    // failure. Reporting it as one turned the heartbeat red (exit 2), and
    // through it the whole control point - for the user finishing the very
    // action the picker exists for.
    //
    // So the local session file is MARKED as consumed (never deleted: the
    // file is evidence) and the run ends green.
    if (s.status === 404) {
      const sessionFile = path.join(DATA, "picker-session.json");
      try {
        if (fs.existsSync(sessionFile)) {
          const cur = JSON.parse(fs.readFileSync(sessionFile, "utf8"));
          if (cur.session_id === SESSION) {
            cur.session_id = null;
            cur.state = "consumed";
            cur.consumed_at = new Date().toISOString();
            fs.writeFileSync(sessionFile, JSON.stringify(cur, null, 2), "utf8");
          }
        }
      } catch {
        /* the marker is a courtesy; the verdict below is the real signal */
      }
      console.log("SESSION_GET_HTTP=404 VERDICT=SESSION_CONSUMED");
      process.exitCode = 0;
      return;
    }
    console.log("SESSION_GET_HTTP=" + s.status + " body=" + JSON.stringify(s.body).slice(0, 200));
    console.log("VERDICT=SESSION_UNREACHABLE");
    process.exitCode = 2;
    return;
  }
  const sess = s.body;
  console.log(
    "SESSION_ID=" + sess.id +
      " mediaItemsSet=" + sess.mediaItemsSet +
      " expireTime=" + sess.expireTime
  );

  if (!sess.mediaItemsSet) {
    console.log("PICKED=0 VERDICT=NOT_PICKED_YET");
    return;
  }

  // The session was completed by the user: list what was picked.
  const items = [];
  let pageToken = null;
  for (let i = 0; i < 20; i++) {
    const q =
      "/v1/mediaItems?sessionId=" + encodeURIComponent(SESSION) + "&pageSize=100" +
      (pageToken ? "&pageToken=" + encodeURIComponent(pageToken) : "");
    const r = await api(token, PICKER + q);
    if (r.status !== 200) {
      console.log("LIST_HTTP=" + r.status + " body=" + JSON.stringify(r.body).slice(0, 200));
      break;
    }
    for (const it of r.body.mediaItems || []) {
      items.push({
        id: it.id,
        type: it.type,
        createTime: it.createTime,
        filename: it.mediaFile ? it.mediaFile.filename : null,
        mimeType: it.mediaFile ? it.mediaFile.mimeType : null,
        baseUrl: it.mediaFile ? it.mediaFile.baseUrl : null,
      });
    }
    pageToken = r.body.nextPageToken || null;
    if (!pageToken) break;
  }

  const summary = {
    session_id: SESSION,
    picked_at: new Date().toISOString(),
    count: items.length,
    items,
  };
  fs.writeFileSync(OUT, JSON.stringify(summary, null, 2), "utf8");
  console.log("PICKED=" + items.length + " WROTE=" + OUT);
  for (const it of items.slice(0, 20)) {
    console.log("  ITEM id=" + it.id + " type=" + it.type + " file=" + it.filename + " mime=" + it.mimeType);
  }

  // The API asks clients to delete a session once it is done, so sessions do
  // not pile up (sessions.create returns RESOURCE_EXHAUSTED when they do).
  if (process.argv.includes("--delete-after")) {
    const d = await api(token, PICKER + "/v1/sessions/" + encodeURIComponent(SESSION), "DELETE");
    console.log("SESSION_DELETE_HTTP=" + d.status);
  }

  console.log("VERDICT=PICKED_CAPTURED");
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exitCode = 2;
});

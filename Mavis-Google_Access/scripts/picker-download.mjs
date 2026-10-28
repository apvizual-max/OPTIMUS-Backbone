// picker-download.mjs - download the media items the user picked.
//
// The Photo Picker hands back a baseUrl per item. The discovery document says
// the client must add the documented parameters to it; `=s0` asks for the
// ORIGINAL file, `=w2048-h1024` for a resized variant. This fetches the
// original, verifies it is really an image (magic bytes, not an HTML error
// page saved with a .jpg name) and writes it next to a manifest.
//
// Usage: node picker-download.mjs [--picked <file>] [--out <dir>]
import fs from "node:fs";
import path from "node:path";

const argOf = (flag, dflt) => {
  const i = process.argv.indexOf(flag);
  return i !== -1 ? process.argv[i + 1] : dflt;
};
const DATA = "C:/Users/apviz/.minimax/google-access/data";
const PICKED = argOf("--picked", path.join(DATA, "picked-media.json"));
const OUT = argOf("--out", "C:/Users/apviz/.minimax-agent/projects/Mavis-Google_Access/state/picked");
const CREDS = path.join(DATA, "credentials.json");

async function accessToken() {
  const c = JSON.parse(fs.readFileSync(CREDS, "utf8"));
  const body = new URLSearchParams({
    client_id: c.client_id,
    client_secret: c.client_secret,
    refresh_token: c.refresh_token,
    grant_type: "refresh_token",
  }).toString();
  const j = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  }).then((r) => r.json());
  if (!j.access_token) throw new Error("TOKEN_FAILED " + JSON.stringify(j).slice(0, 160));
  return j.access_token;
}

const isImage = (buf) =>
  (buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff) || // JPEG
  (buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e); // PNG

(async () => {
  if (!fs.existsSync(PICKED)) {
    console.log("NO_PICKED_FILE " + PICKED);
    process.exitCode = 3;
    return;
  }
  const doc = JSON.parse(fs.readFileSync(PICKED, "utf8"));
  const items = doc.items || [];
  console.log("PICKED_FILE=" + PICKED + " COUNT=" + items.length);
  if (!items.length) {
    console.log("VERDICT=NOTHING_PICKED");
    return;
  }

  const token = await accessToken();
  const dir = path.join(OUT, new Date().toISOString().slice(0, 10));
  fs.mkdirSync(dir, { recursive: true });

  const manifest = [];
  let ok = 0;
  for (const it of items) {
    const url = it.baseUrl ? it.baseUrl + "=s0" : null;
    if (!url) {
      console.log("SKIP no baseUrl id=" + it.id);
      continue;
    }
    let res = await fetch(url, { headers: { Authorization: "Bearer " + token } });
    if (!res.ok) {
      // The media URL is served by Google Photos infrastructure and may be
      // public; a 403 with the token is not proof that the bytes are gone.
      res = await fetch(url);
    }
    const buf = Buffer.from(await res.arrayBuffer());
    const image = isImage(buf);
    const name = it.filename || (it.id + ".jpg");
    const dest = path.join(dir, name);
    if (res.ok && image && buf.length > 1000) {
      fs.writeFileSync(dest, buf);
      ok++;
      console.log(
        "SAVED " + name + " bytes=" + buf.length + " type=" + (res.headers.get("content-type") || "?") + " -> " + dest
      );
    } else {
      console.log(
        "FAILED " + name + " http=" + res.status + " bytes=" + buf.length + " image=" + image
      );
    }
    manifest.push({
      id: it.id,
      filename: name,
      bytes: buf.length,
      saved: res.ok && image && buf.length > 1000,
      local_path: dest,
      base_url: it.baseUrl,
      mime: it.mimeType,
    });
  }

  fs.writeFileSync(path.join(dir, "manifest.json"), JSON.stringify(manifest, null, 2), "utf8");
  console.log("SAVED_COUNT=" + ok + " DIR=" + dir);
  console.log("VERDICT=" + (ok > 0 ? "DOWNLOADED" : "NOTHING_DOWNLOADED"));
  if (!ok) process.exitCode = 2;
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exitCode = 2;
});

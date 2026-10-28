// consent-watcher.mjs - HOST side. One click by Popy, everything else automatic.
//
// Why it exists: the Google consent screen is a physical authorization - it
// stays with the human. But EVERYTHING after that click is machine work, and
// it was being handed back to him as "run this command, copy this code".
// This listener removes that hand-off.
//
// The mounted OAuth client has exactly one registered redirect URI:
// "http://localhost" (port 80, free on this host). So:
//
//   1. Popy clicks "Allow" on Google's consent screen (he already has).
//   2. Google redirects to http://localhost/?code=...  -> THIS listener.
//   3. The code is exchanged for tokens with the mounted client, the widened
//      credential is published into the container's volume, the container is
//      restarted, the probe runs, ntfy is notified, and a result file is
//      written.
//
// The listener never prints the code or any token: only labels and statuses.
import http from "node:http";
import { execFile } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const GA_DIR = "C:\\Users\\apviz\\.minimax\\google-access";
const DATA_DIR = path.join(GA_DIR, "data");
const RESULT = path.join(DATA_DIR, "consent-result.json");
const PROBE_OUT = path.join(DATA_DIR, "last-probe.txt");
const NTFY = "http://127.0.0.1:8090";
const PORT = Number(process.env.CONSENT_PORT || 80);
const REDIRECT = "http://localhost";

function run(cmd, args, timeoutMs = 120000) {
  return new Promise((resolve) => {
    execFile(cmd, args, { timeout: timeoutMs, windowsHide: true }, (err, stdout, stderr) => {
      resolve({
        code: err && typeof err.code === "number" ? err.code : err ? 1 : 0,
        stdout: String(stdout || ""),
        stderr: String(stderr || ""),
      });
    });
  });
}

function writeResult(obj) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(RESULT, JSON.stringify(obj, null, 2), "utf8");
}

function scopeList(text) {
  const m = String(text || "").match(/SCOPES=(.*)/);
  if (!m) return [];
  return m[1].trim().split(/\s+/).filter(Boolean);
}

async function notify(title, message) {
  try {
    const topicFile = path.join(DATA_DIR, "ntfy-topic.txt");
    const topic = fs.existsSync(topicFile) ? fs.readFileSync(topicFile, "utf8").trim() : "";
    if (!topic) return;
    await run(
      "powershell",
      [
        "-NoProfile",
        "-Command",
        "$b = @{ topic = '" + topic + "'; title = '" + title.replace(/'/g, "''") + "'; message = '" +
          message.replace(/'/g, "''") + "'; } | ConvertTo-Json -Compress; " +
          "Invoke-WebRequest -Uri '" + NTFY + "/' -Method Post -Body $b -ContentType 'application/json' -TimeoutSec 10 -UseBasicParsing | Out-Null",
      ],
      30000
    );
  } catch {
    /* notification is best effort: never fail the flow for it */
  }
}

const PAGE = (title, body) =>
  "<!doctype html><html><head><meta charset='utf-8'><title>" + title + "</title></head>" +
  "<body style='font-family:system-ui;background:#0b1220;color:#e6edf7;padding:48px'>" +
  "<h1 style='font-size:22px'>" + title + "</h1><p style='font-size:15px;line-height:1.6'>" + body + "</p></body></html>";

async function handle(code) {
  const started = new Date().toISOString();
  console.log("CODE_RECEIVED=1 at=" + started);

  const provision = await run("node", [path.join(GA_DIR, "provision-grant.cjs"), "--from-code", code, "--client", "container", "--redirect-uri", REDIRECT]);
  const provOut = provision.stdout + provision.stderr;
  const scopes = scopeList(provOut);
  console.log("PROVISION_EXIT=" + provision.code + " SCOPES=" + scopes.length);

  let restart = { code: 0, stdout: "skipped", stderr: "" };
  let probe = { code: 0, stdout: "", stderr: "" };
  if (provision.code === 0) {
    restart = await run("docker", ["restart", "Google_Access"], 60000);
    console.log("RESTART_EXIT=" + restart.code);
    await new Promise((r) => setTimeout(r, 4000));
    probe = await run("node", [path.join(GA_DIR, "probe.mjs")], 120000);
    try {
      fs.writeFileSync(PROBE_OUT, probe.stdout + probe.stderr, "utf8");
    } catch {
      /* ignore */
    }
    console.log("PROBE_EXIT=" + probe.code);
  }

  const verdict = (probe.stdout || "").match(/VERDICT=(\w+)/);
  const granted = (probe.stdout || "").match(/"granted_scopes": \[([\s\S]*?)\]/);
  const result = {
    started,
    finished: new Date().toISOString(),
    provision_exit: provision.code,
    provision_output: provOut.split("\n").filter((l) => !/refresh_token|access_token/i.test(l)),
    scope_count: scopes.length,
    scopes,
    restart_exit: restart.code,
    probe_exit: probe.code,
    probe_verdict: verdict ? verdict[1] : "UNKNOWN",
    granted_scopes_block: granted ? granted[1].replace(/\s+/g, " ").trim() : "",
  };
  writeResult(result);

  if (provision.code === 0) {
    await notify(
      "Google_Access: scope-uri extinse",
      "Consent acordat. " + scopes.length + " scope-uri. Container restartat, proba: " + result.probe_verdict + "."
    );
    return PAGE(
      "Gata.",
      "Scope-urile extinse au fost publicate in volum si containerul a repornit. " +
        "Verificarea: <strong>" + result.probe_verdict + "</strong> (" + scopes.length + " scope-uri). Nu mai trebuie facut nimic."
    );
  }
  await notify("Google_Access: schimbul codului a esuat", "provision-grant exit=" + provision.code);
  return PAGE("A esuat schimbul codului.", "Vedeti logul containerului: " + RESULT);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://localhost");
  const code = url.searchParams.get("code");
  const err = url.searchParams.get("error");
  if (err) {
    writeResult({ started: new Date().toISOString(), oauth_error: err, provision_exit: -1 });
    res.writeHead(400, { "Content-Type": "text/html; charset=utf-8" });
    res.end(PAGE("Consimtamant refuzat.", "Eroarea OAuth: " + err));
    return;
  }
  if (!code) {
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    res.end(PAGE("Ascultatorul e viu.", "Fii pe pagina de consimtamant a lui Google si apasa Allow."));
    return;
  }
  res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  res.end(PAGE("Se proceseaza...", "Un moment."));
  handle(code)
    .then((html) => {
      console.log("DONE=1");
    })
    .catch((e) => {
      console.log("ERROR=" + (e && e.message ? e.message : String(e)));
    });
});

server.listen(PORT, () => {
  console.log("LISTENING=http://localhost:" + PORT + " redirect=" + REDIRECT);
  console.log("READY=1");
});

setTimeout(() => {
  console.log("TIMEOUT=1 (niciun cod in 180 min)");
  process.exit(0);
}, 180 * 60 * 1000);

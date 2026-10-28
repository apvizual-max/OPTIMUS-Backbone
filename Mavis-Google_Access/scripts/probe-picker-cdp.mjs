// probe-picker-cdp.mjs - open a Photo Picker URI in an ALREADY AUTHENTICATED
// Chrome profile and read what Google actually answered.
//
// WHY: the discovery document (photospicker v1, revision 20261026) says, in
// the pickerUri field: "To view this page successfully, the user must be
// logged into the Google account that owns this session in their web browser.
// The pickerUri cannot be opened in an iframe due to security reasons."
//
// So there are exactly two ways to get "Couldn't open Google Photos": the
// browser is not signed in as the account that owns the session, or the URI
// was opened in an embedded frame. Both produce the SAME message, which is
// why guessing between them is worthless. This probe opens the SAME uri in a
// profile whose Google session is known, and reports what the page says.
//
// Usage: node probe-picker-cdp.mjs --uri <pickerUri> [--port 9412] [--keep]
import http from "node:http";

const argOf = (flag, dflt) => {
  const i = process.argv.indexOf(flag);
  return i !== -1 ? process.argv[i + 1] : dflt;
};
const hasFlag = (flag) => process.argv.includes(flag);
const URI = argOf("--uri");
const PORT = Number(argOf("--port", "9412"));

const httpReq = (method, path) =>
  new Promise((res, rej) => {
    const req = http.request(
      { host: "127.0.0.1", port: PORT, path, method },
      (r) => {
        let d = "";
        r.on("data", (c) => (d += c));
        r.on("end", () => {
          try {
            res(JSON.parse(d));
          } catch (e) {
            rej(new Error("non-json from " + path + ": " + d.slice(0, 120)));
          }
        });
      }
    );
    req.on("error", rej);
    req.end();
  });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function openTarget(url) {
  // Chrome requires PUT for /json/new since v111; older builds accept GET.
  try {
    return await httpReq("PUT", "/json/new?" + encodeURIComponent(url));
  } catch {
    return await httpReq("GET", "/json/new?" + encodeURIComponent(url));
  }
}

function attach(wsUrl) {
  const ws = new WebSocket(wsUrl);
  const pend = new Map();
  let id = 0;
  ws.addEventListener("message", (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) {
      const p = pend.get(m.id);
      pend.delete(m.id);
      m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result);
    }
  });
  const send = (method, params = {}) =>
    new Promise((res, rej) => {
      const i = ++id;
      pend.set(i, { res, rej });
      ws.send(JSON.stringify({ id: i, method, params }));
    });
  const opened = new Promise((res, rej) => {
    ws.addEventListener("open", res);
    ws.addEventListener("error", rej);
  });
  return { ws, send, opened };
}

(async () => {
  if (!URI) {
    console.log("URI_REQUIRED");
    process.exitCode = 2;
    return;
  }
  let version;
  try {
    version = await httpReq("GET", "/json/version");
  } catch (e) {
    console.log("CDP_NOT_REACHABLE=" + e.message);
    process.exitCode = 2;
    return;
  }
  console.log("CDP_UP=1 browser=" + (version.Browser || "?").slice(0, 60));

  const target = await openTarget(URI);
  console.log("TARGET_CREATED id=" + target.id + " type=" + target.type);
  const { ws, send, opened } = attach(target.webSocketDebuggerUrl);
  await opened;

  await send("Page.enable");
  await send("Runtime.enable");

  // Wait for the page to settle, then read what it says. A reading taken
  // before the page renders is not a reading.
  let state = null;
  for (let i = 0; i < 20; i++) {
    await sleep(1500);
    try {
      const r = await send("Runtime.evaluate", {
        expression: `(function(){
          var t=(document.body&&document.body.innerText)||'';
          return JSON.stringify({
            url: location.href,
            title: document.title,
            ready: document.readyState,
            len: t.length,
            head: t.replace(/\\s+/g,' ').slice(0,700)
          });
        })()`,
        returnByValue: true,
      });
      state = JSON.parse(r.result.value);
      if (state.len > 40) break;
    } catch {
      /* not ready */
    }
  }
  if (!state) {
    console.log("PAGE_NOT_READABLE");
    process.exitCode = 2;
    return;
  }

  const head = (state.head || "").toLowerCase();
  const broken = /couldn'?t open google photos|connect to google photos again|partner app/.test(head);
  const pickerish = /all photos|recent photos|search photos|albums|select photos|done/.test(head);

  console.log("PAGE_URL=" + state.url);
  console.log("PAGE_TITLE=" + state.title);
  console.log("PAGE_LEN=" + state.len);
  console.log("PAGE_HEAD=" + state.head);
  console.log("DETECT_BROKEN=" + (broken ? 1 : 0));
  console.log("DETECT_PICKER_UI=" + (pickerish ? 1 : 0));
  console.log(
    "VERDICT=" + (broken ? "PICKER_REFUSED" : pickerish ? "PICKER_UI_LOADED" : "PAGE_NEUTRAL")
  );

  if (!hasFlag("--keep")) {
    try {
      await httpReq("GET", "/json/close/" + target.id);
    } catch {
      /* closing is best effort */
    }
  } else {
    console.log("TAB_KEPT=1 target_id=" + target.id);
  }
  try {
    ws.close();
  } catch {
    /* ignore */
  }
})().catch((e) => {
  console.log("ERROR=" + (e && e.message ? e.message : String(e)));
  process.exitCode = 2;
});

#!/usr/bin/env node
/**
 * minimax-notebooklm  --  minimax MCP server for Google NotebookLM (Gemini Notebook).
 *
 * WHY THIS EXISTS, IN ONE PARAGRAPH
 * Popy's rule: minimax has its own tools, minimax has its own connectors, minimax
 * has its own skills, and Hermes has his. They are not the same universe and are
 * not to be combined. The `notebooklm-mcp` package that was on minimax's PATH is
 * the SAME package Hermes runs, with no config and no credential of its own. This
 * server is minimax's own: its own Chrome profile, its own CDP port, its own
 * process, its own authenticated session. Duplication is the correct choice
 * here - two independent instances cannot murder each other, and a shared one
 * can.
 *
 * WHY IT DRIVES A BROWSER INSTEAD OF HOLDING A TOKEN
 * The session lives in a real Chrome profile. Windows encrypts the cookie store,
 * so exporting a bearer token is not available without defeating platform
 * protections. Driving the authenticated profile over CDP is both safer and
 * simpler: the cookies are used where they already exist and never leave it.
 *
 * EVERY ENDPOINT HERE WAS CAPTURED FROM THE WIRE, NOT GUESSED. The batchexecute
 * RPC id `ZwVcOc` was read off a real notebook-list request with the CDP Network
 * domain. Do not add a path to this file that has not been observed.
 */
"use strict";

const http = require("http");
const { spawn } = require("child_process");
const path = require("path");
const os = require("os");
const fs = require("fs");

const PROFILE = process.env.MINIMAX_NOTEBOOKLM_PROFILE
  || path.join(os.homedir(), "AppData", "Local", "minimax-notebooklm", "chrome_profile");
const CDP_PORT = Number(process.env.MINIMAX_NOTEBOOKLM_CDP || 9412);
const CHROME = process.env.CHROME_PATH
  || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const ORIGIN = "https://notebook.google.com";

/* ---------------------------------------------------------------- CDP ---- */

const httpGet = (u) => new Promise((res, rej) => {
  http.get(u, (r) => { let d = ""; r.on("data", (c) => (d += c)); r.on("end", () => { try { res(JSON.parse(d)) } catch (e) { rej(e) } }); }).on("error", rej);
});

async function ensureBrowser() {
  try {
    await httpGet(`http://127.0.0.1:${CDP_PORT}/json/version`);
    return { started: false, note: "reusing the running browser" };
  } catch { /* not up - start one */ }

  if (!fs.existsSync(CHROME)) throw new Error(`Chrome not found at ${CHROME}`);
  fs.mkdirSync(PROFILE, { recursive: true });
  spawn(CHROME, [
    `--user-data-dir=${PROFILE}`,
    `--remote-debugging-port=${CDP_PORT}`,
    "--headless=new", "--no-first-run", "--no-default-browser-check",
    "--disable-gpu", "--window-size=1400,900", ORIGIN,
  ], { detached: true, stdio: "ignore", windowsHide: true }).unref();

  for (let i = 0; i < 40; i++) {
    await new Promise((r) => setTimeout(r, 500));
    try { await httpGet(`http://127.0.0.1:${CDP_PORT}/json/version`); return { started: true, note: "browser started" }; } catch {}
  }
  throw new Error("browser did not expose CDP within 20 s");
}

/** Attach to the notebook page and return an evaluate() bound to that page. */
async function page() {
  const list = await httpGet(`http://127.0.0.1:${CDP_PORT}/json/list`);
  let t = list.find((x) => x.type === "page" && ORIGIN.includes(new URL(x.url).host));
  if (!t) {
    const any = list.find((x) => x.type === "page" && x.webSocketDebuggerUrl);
    if (!any) throw new Error("no page target");
    t = any;
  }
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map();
  const send = (m, p = {}) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
  await new Promise((r, j) => { ws.addEventListener("open", r); ws.addEventListener("error", j); });
  ws.addEventListener("message", (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result); }
  });
  await send("Runtime.enable");
  const evaluate = async (expr) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error((r.exceptionDetails.exception && r.exceptionDetails.exception.description) || r.exceptionDetails.text);
    return (r.result || r).value;
  };
  const navigate = async (url) => { await send("Page.enable"); await send("Page.navigate", { url }); await new Promise((r) => setTimeout(r, 6000)); };
  return { evaluate, navigate, close: () => { try { ws.close(); } catch {} } };
}

/* ------------------------------------------------------------- session ---- */

/**
 * Session check. Deliberately does NOT test a hostname: the first version of
 * this matched notebooklm.google.com and reported "NOT signed in" over a page
 * that was plainly signed in, because the product now lives at
 * notebook.google.com. It tests for the things that distinguish the two states:
 * the notebook list is present, and the sign-in call to action is not.
 */
async function sessionState() {
  const p = await page();
  try {
    await p.navigate(ORIGIN + "/");
    // Poll until the page settles into ONE of the two known states. An earlier
    // version read the DOM once, six seconds after navigating, and reported
    // "not authenticated" over a page that had simply not finished rendering.
    // Absence seen by a half-loaded page is not evidence of anything, so a
    // third state - unknown - is reported rather than guessing either way.
    let s = null;
    for (let i = 0; i < 12; i++) {
      const raw = await p.evaluate(`(function(){
        const t = (document.body.innerText||'');
        return JSON.stringify({
          url: location.href,
          ready: document.readyState,
          hasList: /New notebook/i.test(t) || /Recent notebooks/i.test(t),
          hasSignInCta: /Sign in to Gemini Notebook/i.test(t),
          signedOutHost: /accounts\\.google\\.com/.test(location.href),
          title: document.title,
          bodyStart: t.replace(/\\s+/g,' ').slice(0,200)
        });
      })()`);
      s = JSON.parse(raw);
      if (s.hasList || s.hasSignInCta || s.signedOutHost) break;   // settled
      await new Promise((r) => setTimeout(r, 2000));
    }
    if (!s.hasList && !s.hasSignInCta && !s.signedOutHost) {
      return { ...s, state: "unknown", authenticated: null,
               note: "page did not settle into a signed-in or signed-out state; reporting unknown rather than guessing" };
    }
    s.authenticated = s.hasList && !s.hasSignInCta && !s.signedOutHost;
    s.state = s.authenticated ? "authenticated" : "signed-out";
    // §10.2 circuit breaker. A signed-out session is the one condition no
    // amount of querying can change - only the operator can, by signing in.
    recordBreaker(s);
    return s;
  } finally { p.close(); }
}

/* -- §10.2 circuit breaker -------------------------------------------------
 * Before this, every call on a signed-out profile opened the browser and
 * navigated to notebook.google.com before giving up, and the collector
 * re-probed every 10 minutes: a loop on the wire against a state that no
 * query can move. The tools answered honestly and still cost a round-trip
 * each time, which is the definition of a loop.
 *
 * OPEN    the session is unauthenticated. Tools answer from memory and touch
 *         no network at all - no navigation, no batchexecute, no polling.
 * HALF    the cooldown has elapsed; exactly one probe is admitted, and while
 *         that probe is in flight every other caller is refused rather than
 *         queued, so a burst cannot become a pile-up against one CDP port.
 * CLOSED  authenticated. Untouched by this breaker.
 *
 * The cooldown exists so the breaker cannot become a permanent lie: signing
 * in is a human action, and the console must eventually see it without a
 * reboot.
 */
const BREAKER = {
  state: "closed",
  openedAt: 0,
  cooldownMs: 15 * 60 * 1000,
  inFlight: false,
  reason: null,
};

function recordBreaker(s) {
  if (s && s.authenticated === true) {
    BREAKER.state = "closed";
    BREAKER.openedAt = 0;
    BREAKER.reason = null;
  } else if (s && s.authenticated === false) {
    if (BREAKER.state !== "open") BREAKER.openedAt = Date.now();
    BREAKER.state = "open";
    BREAKER.reason = s.state === "signed-out"
      ? "notebook.google.com returned the sign-in page"
      : "the profile is signed out of Google";
  }
  // authenticated === null is UNKNOWN, not a reason to trip the breaker.
  // A page that did not settle says nothing about the session.
}

function breakerGate(tool) {
  if (BREAKER.state !== "open") return null;
  const waitMs = Math.max(0, BREAKER.openedAt + BREAKER.cooldownMs - Date.now());
  if (waitMs > 0) {
    return {
      authenticated: false,
      state: "UNAUTHENTICATED",
      circuit: "open",
      probe_suppressed: true,
      retry_after_sec: Math.ceil(waitMs / 1000),
      reason: BREAKER.reason,
      remedy: "sign into notebook.google.com on the minimax Chrome profile "
            + "(%LOCALAPPDATA%\\minimax-notebooklm\\chrome_profile); this is a human action",
      note: tool + " was answered from the last known session state without touching the network",
    };
  }
  if (BREAKER.inFlight) {
    return {
      authenticated: false,
      state: "UNAUTHENTICATED",
      circuit: "half",
      probe_suppressed: true,
      retry_after_sec: 60,
      reason: BREAKER.reason,
      note: "one re-authentication probe is already in flight; this caller was refused rather than queued",
    };
  }
  // Cooldown elapsed: admit exactly one probe.
  BREAKER.inFlight = true;
  setTimeout(() => { BREAKER.inFlight = false; }, 45000).unref?.();
  return null;
}

/* ----------------------------------------------------------------- API ---- */

// The batchexecute body, exactly as the product sends it. `rpcid` is the only
// thing that changes per operation and every id in this file was observed.
function batchexecuteBody(rpcid, inner) {
  return "f.req=" + encodeURIComponent(JSON.stringify([[[rpcid, inner, null, "generic"]]]));
}

async function callNotebook(rpcid, inner) {
  const p = await page();
  try {
    const res = await p.evaluate(`(async function(){
      const r = await fetch('/_/LabsTailwindUi/data/batchexecute?rpcids=${rpcid}&hl=en', {
        method:'POST', credentials:'include',
        headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},
        body: ${JSON.stringify(batchexecuteBody(rpcid, inner))}
      });
      return await r.text();
    })()`);
    return res;
  } finally { p.close(); }
}

/* -------------------------------------------------- notebook-scoped tools ---- */

/**
 * Open one notebook and return a page handle plus the live notebook id.
 * `notebook` may be an id, a /notebook/<id> href, or a name (resolved against
 * the list). A name is resolved by MATCHING THE OBSERVED LIST, not by guessing
 * an id.
 */
async function openNotebook(notebook) {
  const p = await page();
  const need = String(notebook || "").trim();
  let href = null;

  if (/^\/notebook\//.test(need)) href = need;
  else if (/^[0-9a-f-]{20,}$/i.test(need)) href = "/notebook/" + need;

  if (!href) {
    await p.navigate(ORIGIN + "/");
    for (let i = 0; i < 20; i++) {
      const got = await p.evaluate(`(function(){
        var want = ${JSON.stringify(need)}.toLowerCase();
        var as = Array.from(document.querySelectorAll('project-button.project-button'));
        for (var c of as) {
          var t = c.querySelector('span.project-button-title');
          var a = c.querySelector('a[href^="/notebook/"]');
          if (t && a && t.textContent.trim().toLowerCase() === want) return a.getAttribute('href');
        }
        return "";
      })()`);
      if (got) { href = got; break; }
      await new Promise((r) => setTimeout(r, 1500));
    }
    if (!href) { p.close(); throw new Error("no notebook named '" + need + "' (match is exact and case-insensitive)"); }
  }

  await p.navigate(ORIGIN + href);
  // wait for the notebook's own chrome, not a fixed sleep
  for (let i = 0; i < 20; i++) {
    const ok = await p.evaluate(`!!document.querySelector('textarea,[contenteditable="true"]')`);
    if (ok) break;
    await new Promise((r) => setTimeout(r, 1500));
  }
  return { p, href, id: href.replace("/notebook/", "") };
}

/**
 * Sources. Selectors were captured from the live DOM: the sources panel is
 * .source-panel-content and each source is one .source-expansion-panel. The
 * notebook list already taught what a guessed selector costs.
 */
async function nblm_get_sources(args) {
  const gated = breakerGate("nblm_get_sources");
  if (gated) return { notebook: args.notebook, sources: [], count: 0, ...gated };
  await ensureBrowser();
  const st = await sessionState();
  if (st.authenticated !== true) return { authenticated: st.authenticated, state: st.state, sources: [], reason: "not signed in" };
  const { p, id } = await openNotebook(args.notebook);
  try {
    await p.evaluate(`(function(){
      var b = Array.from(document.querySelectorAll('button')).find(function(x){
        return /^Sources$/i.test((x.getAttribute('aria-label') || x.innerText || '').trim());
      });
      if (b) b.click();
    })()`);
    // WAIT FOR THE PANELS, do not sleep a guessed interval. Measured: the click
    // is correct and the 13 .source-expansion-panel nodes are there — the first
    // version slept 6 s and read the count too early, and returned 0 over a page
    // that plainly had 13 sources.
    let sources = [];
    for (let i = 0; i < 20; i++) {
      const raw = await p.evaluate(`(function(){
        var items = Array.from(document.querySelectorAll('.source-expansion-panel'));
        return JSON.stringify(items.map(function(panel){
          var t = panel.querySelector('.source-title, .source-info-title, [class*="title"]');
          var meta = panel.querySelector('.source-info');
          var txt = (panel.innerText || '').replace(/\\s+/g,' ').trim();
          // Strip the icon labels the Material components leave in innerText
          // ("keyboard_arrow_rightAlex - Data-Set more_vert").
          var clean = function(s){ return (s||'').replace(/^(keyboard_arrow_right|expand_content|label_auto|sort|add_2|more_vert|article|description|video_audio|link|picture_as_pdf)\\s*/g, '').replace(/\\s*(more_vert|label_auto|sort|close)$/,'').trim(); };
          return { name: t ? clean(t.textContent) : (clean(txt) || txt.slice(0,80)),
                   detail: meta ? clean(meta.innerText).slice(0,140) : txt.slice(0,140) };
        }));
      })()`);
      sources = JSON.parse(raw);
      if (sources.length) break;
      await new Promise((r) => setTimeout(r, 1500));
    }
    return { authenticated: true, notebook: args.notebook, notebook_id: id, count: sources.length, sources,
             note: sources.length ? null : "the Sources panel opened but no source nodes appeared within 30 s; reporting none rather than guessing" };
  } finally { p.close(); }
}

/**
 * Ask. The pair of classes is unambiguous and was counted, not guessed:
 * .from-user-message-card-content holds Popy's question,
 * .to-user-message-card-content holds Gemini's reply.
 */
async function nblm_ask(args) {
  const gated = breakerGate("nblm_ask");
  if (gated) return { notebook: args.notebook, question: args.question || null, answer: null, ...gated };
  await ensureBrowser();
  const st = await sessionState();
  if (st.authenticated !== true) return { authenticated: st.authenticated, state: st.state, answer: null, reason: "not signed in" };
  const q = String(args.question || "").trim();
  if (!q) throw new Error("question is required");

  const { p, id } = await openNotebook(args.notebook);
  try {
    await p.evaluate(`(function(){
      var b = Array.from(document.querySelectorAll('button')).find(function(x){
        return /^Chat$/i.test((x.getAttribute('aria-label') || x.innerText || '').trim());
      });
      if (b) b.click();
    })()`);
    await new Promise((r) => setTimeout(r, 3000));

    const beforeTo = await p.evaluate(`document.querySelectorAll('.to-user-message-card-content').length`);
    const beforeFrom = await p.evaluate(`document.querySelectorAll('.from-user-message-card-content').length`);

    const sent = await p.evaluate(`(async function(){
      var q = ${JSON.stringify(q)};
      // NOT the first textarea on the page. The Sources panel contains its own
      // search box, and querySelector('textarea') returns THAT one - so the
      // question was typed into the source filter and the chat submit stayed
      // disabled forever. Measured, then fixed: exclude anything inside the
      // sources panel.
      var all = Array.from(document.querySelectorAll('textarea,[contenteditable="true"]'));
      var chat = all.filter(function(el){ return !el.closest('.source-panel-content'); })[0] || all[0];
      if (!chat) return 'no input box';
      chat.focus();
      if (chat.tagName === 'TEXTAREA') {
        Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set.call(chat, q);
      } else { chat.textContent = q; }
      chat.dispatchEvent(new Event('input', { bubbles: true }));
      chat.dispatchEvent(new Event('change', { bubbles: true }));

      var b = null;
      for (var i = 0; i < 24; i++) {
        await new Promise(function(r){ setTimeout(r, 500); });
        b = Array.from(document.querySelectorAll('button')).find(function(x){
          return /submit|send|ask/i.test(x.getAttribute('aria-label') || '') && !x.closest('.source-panel-content');
        });
        if (b && !b.disabled) { b.click(); return 'submitted'; }
      }
      return 'submit stayed disabled for 12 s - the question was NOT sent';
    })()`, true);

    // Proof of submission is the USER message appearing, not the click.
    let submitted = false;
    for (let i = 0; i < 15; i++) {
      await new Promise((r) => setTimeout(r, 1000));
      const now = await p.evaluate(`document.querySelectorAll('.from-user-message-card-content').length`);
      if (now > beforeFrom) { submitted = true; break; }
    }
    if (!submitted) {
      return { authenticated: true, notebook: args.notebook, notebook_id: id, question: q,
               send_status: sent, submitted: false, answer: null,
               note: "the question never appeared in the thread, so it was NOT sent - this is not an empty answer" };
    }

    // Then wait for the REPLY TO FINISH ARRIVING. The first chunk of a
    // streaming answer is a loading placeholder ("Looking for clues..."), so
    // "some text appeared" is not "the answer arrived". Wait until the text
    // stops changing, and treat known placeholders as not-yet-an-answer.
    const PLACEHOLDER = /looking for clues|generating|thinking|loading|^\s*\.\.\.\s*$/i;
    let answer = null, last = null, stable = 0;
    for (let i = 0; i < 50; i++) {
      await new Promise((r) => setTimeout(r, 3000));
      // `let`, not `const`: the UI-chrome strip below reassigns it.
      // Declared const, this threw "Assignment to constant variable" the first
      // time an answer actually ARRIVED - that is, it threw only when the
      // feature worked. Every earlier attempt died earlier, on the placeholder
      // branch, so the bug stayed invisible exactly until it mattered.
      // `node --check` passes on this file either way: this is a runtime fault.
      let got = await p.evaluate(`(function(){
        var a = document.querySelectorAll('.to-user-message-card-content .message-text-content');
        if (a.length <= ${beforeTo}) return '';
        return (a[a.length-1].textContent || '').trim();
      })()`);
      if (!got || PLACEHOLDER.test(got) || got.length < 12) { last = got; stable = 0; continue; }
      // The answer node carries UI chrome ("Thoughts expand_more") ahead of the
      // real text. Strip it rather than shipping it to the caller.
      got = got.replace(/^(Thoughts\s*expand_more|Chat|Studio)\s*/i, '').trim();
      if (got === last) { stable++; if (stable >= 2) { answer = got; break; } }
      else { stable = 0; }
      last = got;
    }
    return {
      authenticated: true, notebook: args.notebook, notebook_id: id,
      question: q, send_status: sent, submitted: true,
      answer: answer,
      partial: answer ? null : (last || null),
      note: answer ? null
        : "the question WAS sent but the answer had not finished streaming within 150 s; 'partial' holds whatever had arrived - this is NOT an empty answer"
    };
  } finally { p.close(); }
}

/* ------------------------------------------------------------- MCP wire ---- */

const send = (o) => process.stdout.write(JSON.stringify(o) + "\n");
const log = (s) => process.stderr.write(s + "\n");

const TOOLS = [
  {
    name: "nblm_health",
    description: "Is the minimax NotebookLM session authenticated? Returns evidence, not a guess.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "nblm_list_notebooks",
    description: "List the notebooks visible to the minimax NotebookLM session.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "nblm_get_sources",
    description: "List the sources inside one NotebookLM notebook.",
    inputSchema: {
      type: "object",
      properties: { notebook: { type: "string", description: "notebook name or id" } },
      required: ["notebook"], additionalProperties: false,
    },
  },
  {
    name: "nblm_ask",
    description: "Ask one NotebookLM notebook a question and return its reply.",
    inputSchema: {
      type: "object",
      properties: {
        notebook: { type: "string", description: "notebook name or id" },
        question: { type: "string", description: "the question to ask" },
      },
      required: ["notebook", "question"], additionalProperties: false,
    },
  },
];

const HANDLERS = {
  nblm_ask: nblm_ask,
  nblm_get_sources: nblm_get_sources,
  async nblm_health() {
    await ensureBrowser();
    const s = await sessionState();
    return {
      server: "minimax-notebooklm",
      profile: PROFILE,
      cdp_port: CDP_PORT,
      origin: ORIGIN,
      // The §10.2 named sentinel. `state` below is the page-level observation
      // ("signed-out"); this is the machine-detectable condition the console
      // and any future circuit logic look for.
      state: s.authenticated === false ? "UNAUTHENTICATED" : s.state,
      authenticated: s.authenticated,
      circuit: {
        state: BREAKER.state,
        cooldown_sec: Math.round(BREAKER.cooldownMs / 1000),
        retry_after_sec: BREAKER.state === "open"
          ? Math.max(0, Math.ceil((BREAKER.openedAt + BREAKER.cooldownMs - Date.now()) / 1000))
          : 0,
        probe_in_flight: BREAKER.inFlight,
        reason: BREAKER.reason,
      },
      evidence: { notebook_list: s.hasList, sign_in_cta: s.hasSignInCta, url: s.url, note: s.note || null },
    };
  },
  async nblm_list_notebooks() {
    const gated = breakerGate("nblm_list_notebooks");
    if (gated) return { notebooks: [], count: 0, ...gated };
    await ensureBrowser();
    const s = await sessionState();
    if (s.authenticated !== true) {
      return { authenticated: s.authenticated, state: s.state, notebooks: [],
               reason: s.state === "unknown" ? "the page did not settle; not guessing"
                                             : "session is not signed in" };
    }
    const p = await page();
    try {
      // Selectors below were READ OFF THE LIVE DOM, not guessed. The card is
      // <project-button class="project-button">; the name lives in
      // span.project-button-title and the metadata in
      // span.project-button-subtitle-part. Two earlier attempts failed on this
      // same list: one read the anchor's own innerText (which is empty), and
      // one climbed to the first ancestor with any text at all (which is the
      // "public" icon, so every notebook came back named "public").
      const rows = await p.evaluate(`(function(){
        const out = [], seen = new Set();
        document.querySelectorAll('project-button.project-button').forEach(card => {
          const a = card.querySelector('a[href^="/notebook/"]');
          const href = a ? a.getAttribute('href') : '';
          const id = href.replace('/notebook/', '');
          if (!id || seen.has(id)) return;
          seen.add(id);
          const titleEl = card.querySelector('span.project-button-title');
          const subs = Array.from(card.querySelectorAll('span.project-button-subtitle-part'))
                            .map(s => (s.textContent||'').trim()).filter(Boolean);
          out.push({
            name: titleEl ? titleEl.textContent.trim() : '(untitled)',
            id: id,
            updated: subs[0] || null,
            sources: subs.length > 1 ? subs[1] : null
          });
        });
        return JSON.stringify(out);
      })()`);
      return { authenticated: true, state: s.state, notebooks: JSON.parse(rows) };
    } finally { p.close(); }
  },
};

(async () => {
  log("minimax-notebooklm: ready (stdio)");
  let buf = "";
  process.stdin.on("data", async (chunk) => {
    buf += chunk.toString();
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      if (!line) continue;
      let msg; try { msg = JSON.parse(line); } catch { continue; }
      if (msg.id === undefined) continue;

      if (msg.method === "initialize") {
        send({ jsonrpc: "2.0", id: msg.id, result: {
          protocolVersion: "2024-11-05",
          capabilities: { tools: {} },
          serverInfo: { name: "minimax-notebooklm", version: "1.0.0" },
        } });
      } else if (msg.method === "tools/list") {
        send({ jsonrpc: "2.0", id: msg.id, result: { tools: TOOLS } });
      } else if (msg.method === "tools/call") {
        const fn = HANDLERS[msg.params?.name];
        if (!fn) {
          send({ jsonrpc: "2.0", id: msg.id, error: { code: -32601, message: "no such tool: " + msg.params?.name } });
          continue;
        }
        try {
          const out = await fn(msg.params?.arguments || {});
          send({ jsonrpc: "2.0", id: msg.id, result: { content: [{ type: "text", text: JSON.stringify(out, null, 2) }], isError: false } });
        } catch (e) {
          send({ jsonrpc: "2.0", id: msg.id, result: { content: [{ type: "text", text: "ERROR: " + (e && e.message ? e.message : String(e)) }], isError: true } });
        }
      }
    }
  });
})();

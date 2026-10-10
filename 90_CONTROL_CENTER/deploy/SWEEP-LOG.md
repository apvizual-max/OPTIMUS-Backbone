# TAB SWEEP LOG — OPTIMUS Control Center

Three full passes, one tab at a time, looping back to tab 1 each time.
A tab is "done for a pass" when: it renders, its data is wired to the live
measurement, its tables/blocks are balanced, and nothing on it contradicts
anything else on it.

Instrument: private Chrome over CDP (shared MCP browser proved unreliable).
Scripts: `%TEMP%\cc-sweep.js`, `cc-audit.js`, `cc-shots.js`, `cc-one.js`, `cc-ask.js`
Baseline audit: all 15 tabs render, 0 NaN / undefined / [object / throw.

---

## PASS 1

### 1. Overview — DONE
**Defect found: the screen contradicted itself.**
The KPI tile said `BRIDGES 2/2` while the card below it said
`hermes-bridge  unknown · 0ok / 0w / 0f`. Both true of different things, together
reading as "all clear".

**Root cause (measured, not assumed).** The collector probed
`/doctor/detailed` with an 8 s budget. Measured four samples against the live
bridge: **9.43 s / 9.91 s / 10.42 s / 11.33 s** (12 checks). The budget was
under the *fastest* sample, so it timed out on 100% of runs and the bridge had
**never once been measured**. The code's own comment admitted it: *"answers in
~8.5 s against an 8 s budget, so it was permanently indistinguishable from an
outage."* A budget shorter than the thing it measures is not caution, it is a
dead sensor.

**Fixed.** Budget 8 s → 20 s. Cost: nothing — collect measured 26.2 s after,
unchanged. And the page now separates the two questions: it counts bridges
**measured**, not merely **up**, turns the tile amber when one is unmeasured,
and the card prints the reason (`answered late · 9.2s against a 20s budget`)
because "up but unmeasured" and "down" need opposite remedies.

**Verified:** `hermes-bridge warn · 9ok / 3w / 0f`, 12 real checks.

### 2. AI Analyst — DONE
The feature Popy values most, and the least finished-looking thing on screen.

**Defects found:**
- The answer panel had **no provenance**. An answer with no model, no timestamp
  and no question is a claim, in a console whose entire argument is that every
  number is measured.
- The card repeated the hero's explanation almost verbatim — filler.
- Six suggestion chips wrapped **5 + 1**, leaving an orphan that read as a bug.
- Large void below the fold.

**Fixed.** The answer panel now carries `MINIMAX-M3` · `facts measured 56s ago`
· `answered 5:00:04 AM` and an `ASKED:` echo. The stale flag goes amber rather
than disappearing — a correct answer from a stale snapshot is still a stale
answer. Chips are a 3-column grid that collapses 3→2→1 instead of re-orphaning.

**Second defect found by testing, not by reading:** the new header did not
render. `paintAI()` only rewrote the text inside `#aiOut`; the header is built
by `viewAI()`, which `askAI` never calls. Calling `render()` would have fixed it
and **destroyed the textarea the operator is looking at**. So the answer box now
owns its own content (`#aiAns`) and both paths produce identical markup.

**Verified by asking a real question:** 10.1 s, header present, answer quoted
real measured values (61 containers, both bridges up, dirty Hermes build with
8 modified files).

### 3. Trends & Incidents — DONE
**Defects found (layout, not data):**
- `.grid` had no `align-items`, so every card stretched to the tallest in its
  row. Two cards carried ~800 px of empty card. Fixed globally — this improved
  **every** tab, not just this one.
- Five cards in a three-column grid left a dead quadrant.
- "Recent incidents" ran to 1075 px and dictated its whole row's height.
- The heatmap's empty cells were `rgba(127,127,127,.10)` on a `.14` border, so
  30 of 35 days were effectively invisible: a 35-day calendar that read as
  "there is nothing here". An empty cell is information. Raised to `.17`/`.26`.

**Fixed:** `align-items:start` on `.grid`; incidents capped at 420 px with
internal scroll; heatmap empty-cell contrast raised; and a **sixth card,
"Biggest movers"** — the swing in each tracked value across the window. It fills
the dead quadrant with the one question this tab exists to answer and neither
chart answers: *which value actually moved, and by how much*. Reports
containers 58→62, warnings 0→5, failures 0→0 "never moved".

**Measured:** card spread 192..1075 → **192..565**.

### 4. Docker — DONE
**Defect found:** the container table is capped at 520 px and ended **mid-row**.
A half row reads as a rendering fault, not as "there is more". Added a
bottom fade (theme-aware — the first attempt hardcoded a dark colour and was
invisible under `paper`, the second had `z-index:auto` and lost the paint
order) and made the caption state the count outright: *"Click any row for its
full record. The list scrolls — 62 containers."*

**Instrument note:** the first screenshot of this tab came back showing "Activity
by day" missing. It was not missing — geometry measured it at 482×501. The
screenshot lied because the sweep waited for `location.href` but not for the
app's JavaScript, and once evaluated `render()` before the script ran. The
harness now waits for `typeof render === 'function'`. **A tool that reports a
false defect is worse than no tool**, because it sends you to fix something that
is already correct.

### 5-14. Bridges · Services · Qwen · Update · MiniMax · Skills · Projects · Docs · Command · Resilience — DONE (no defects)

Reviewed individually by rendered text rather than by eye alone, which is both
cheaper and more reliable for finding data faults. All correct and honest:

- **services** — 3 services reachable, HTTP 200, with the LibreOffice "this is a
  remote desktop, not an API" clarification intact.
- **qwen** — OAuth credential correctly shown **MISSING** in red; transport
  explains the 404 on the MCP path; the blocker and the `mcpServers: []` quirk
  both present.
- **update** — verdict "8 file(s) modified, no lock held"; install-stamp vs live
  git HEAD disagreement explained rather than hidden; all 8 modified files listed.
- **minimax** — Code/Design present, 11 Code processes, CLI authenticated via
  shared broker, 15 connector tools, the single-argument explanation.
- **skills** — 61 Mavis / 1279 personal / 314 Hermes, SOT junction intact.
- **projects / docs** — live per-section counts and file listings.
- **command** — all actions with their real command lines.
- **resilience** — supervisor verdict, PID, uptime, restart count.

Card heights after the two console-wide fixes:

| tab | cards | heights |
|---|---|---|
| services | 3 | 299..376 |
| qwen | 4 | 219..374 |
| update | 4 | 162..332 |
| minimax | 3 | 265..430 |
| skills | 2 | 281..516 |
| projects / docs | 1 | ~641 |
| command | 3 | 188..999 |
| resilience | 4 | 367..478 |
| bridges | 2 | 875..1000 |

Two console-wide fixes — `align-items:start` on `.grid`, and `max-height:1000px`
on `.card` — landed on all fifteen tabs, not only the four examined by eye.
Tab height across the whole console now sits in **518–2212 px**, with no
runaway and no dead card.

### 15. Fabric — DONE (the worst offender)
**Defect found:** the tab rendered at **5747 px**. Nine cards, several of them
long prose: "Model fleet" 3818 px, "Process census" 1933 px, "Access &
authentication" 1329 px, "Reachability" 1444 px. It had become a second
documentation site *inside* the console, and a status board that needs a full
scroll to read is not a status board.

**Fixed with one console-wide rule:** `.card { max-height:1000px; overflow-y:auto }`.
The cap sits well above the tallest legitimate card measured (~640 px), so
ordinary cards are untouched and only runaway ones engage, then scroll
internally. No card anywhere in the console now exceeds 1000 px.

**Measured:** card spread 334..3818 → **334..1000**. Tab height **5747 → 2212 px**
(−61%). Fabric is still the tallest tab, which is correct — it is the
dependency graph, and it is meant to be dense.

---

## PASS 2

### Cross-tab consistency — VERIFIED, structurally
Per-tab review cannot test the Overview's own promise that it "reads the same
live snapshot as every other tab". So this pass checked the property itself:

- Exactly **one** `S` in the page (`let S = null, active=…, busy=…, history=…`),
  reassigned on every poll. No second copy, no `STATE=`, no `CACHE=`.
- No view function caches its own copy of the snapshot; the `const s=S.sections.x`
  lines are aliases, not copies.
- Every `S.sections.*` key the page reads is emitted by the collector —
  **14 sections, 14 matches**, zero missing.
- The one apparent gap, `S.stale`, is a *conditional* flag: absent when healthy,
  set only when the server serves a stale payload. Used once, as a ternary.

### Action wiring — GUARDED
Three places define an action: the page's button table, the server's runnable
whitelist, and the collector's advertised list. Verified equal — **15/15/15**, no
orphan buttons, no unreachable actions — and now asserted by three new harness
checks. The failure this prevents is silent in the worst direction: a console
that looks complete while one control answers 400.

### `/api/journal` — OFF THE REQUEST THREAD
It was the last route running `docker exec` inline. Now it serves a cached file
and kicks off a background refresh; response shape unchanged. Proven under load:
**12 journal calls while probing `/api/state` → 0 of 14 probes over 2 s.**

Caught before shipping: the job called `Read-SharedText`, which lives in
`run-bounded.ps1`, and **a `Start-Job` inherits nothing the parent dot-sourced**.
It would have thrown into a swallowed catch, never cached, and answered
`refreshing: true` for ever while looking like a Docker problem.

Only a *completed* read is cached — caching an empty result because the daemon
was slow would turn a transient hiccup into a permanent "no journal", and a later
reader could not tell "nothing was written" from "we did not manage to look".

### MiniMax ecosystem — CAPABILITY MAP ADDED
The tab could say "15 connector tools", which answers how many and not what.
Captured the catalogue itself, grouped by family, with plain tool names:

- **figma — 2:** `download_figma_images`, `get_figma_data` → **the live MiniMax
  Design link**, now labelled as such on the tab
- **matrix — 13:** audio/video/image generation, TTS, ASR, vision, search

This is the control-hub surface Popy asked for: which doors exist, not how
many, and the Design route named rather than implied.

---

## Standing findings, not per-tab
- **The 8910 SENTINEL_PRIME server has no supervisor.** It died on its own at
  ~05:50 with an **empty error log** and stayed dead until noticed — the exact
  failure the OPTIMUS watchdog exists to prevent, in a service that does not have
  one. Restored (PID 26880). Reported, not silently adopted: it is another
  project's service.
- `Start-Job` still costs 0.4–1.1 s on the request thread. Removing it needs a
  persistent worker — a deliberate trade, not a defect.
- **The instruments needed fixing four times** (a guard that rejected a good
  page, a race that reported a false missing card, a self-check that counted a
  correct value as a defect, and a case-sensitive label matcher that reported
  "no inconsistencies" for all six tabs). Every one was caught by reading output
  rather than trusting a green line.

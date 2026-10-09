---
name: qwen-ecosystem-dashboard
description: |
  The Qwen Ecosystem Control Dashboard — the OPTIMUS Prime system-integrity surface at
  http://127.0.0.1:3098, and the additive build method that grew it. Use whenever Popy
  refers to the Qwen dashboard, the Gwin/Qwen bridge dashboard, the System Integrity tab,
  the Decision Queue, the decision ledger, the risk register, the port ownership table,
  the supervision tree, "the thing Antigravity built", or asks to extend, verify, debug
  or re-verify it. Also use before writing ANY code into its index.html or server.js.

  This is the worked example that the general method in `minimax-optimus-dashboard`
  points at. It is particular: real paths, real ports, real hashes, real clause names.
  A session with zero context should be able to open this file and continue safely.
license: proprietary
metadata:
  live_root: C:\Users\apviz\AI_Tools\qwen-system\dashboard
  harness_root: C:\Users\apviz\QWEN_BACKUP
  general_method: minimax-optimus-dashboard
  operator: Alexandru Popescu (Popy), Romania
  doctrine: SENTINEL / OPTIMUS Prime
---

# QWEN ECOSYSTEM DASHBOARD — project skill

Read this before touching anything. Every number here was measured, and every fault below
happened for real. Nothing in this file is aspirational.

---

## 0. ORIENTATION — 30 seconds

| | |
|---|---|
| **Live dashboard** | `http://127.0.0.1:3098` — served by `server.js`, **not** to be started by hand |
| **Live files** | `C:\Users\apviz\AI_Tools\qwen-system\dashboard\` — `index.html` (client, ~416 KB) · `server.js` (daemon, ~490 KB) |
| **Harness** | `C:\Users\apviz\QWEN_BACKUP\` — every check, sabotage and diagnostic ever written |
| **Who built what** | Antigravity built the original dashboard. Runs 19–30 are **additive** work on top. Never revert to a pre-run backup as a "fix" — that deleted finished work once. |
| **Operator** | Popy — designs the system, does not code. Never teaches him to use a tool; give him a decision. |

### The tabs, and what each is for

`tab-chat` · `tab-conv` · `tab-mcp` · `tab-term` · `tab-system` · **`tab-integrity`**

`tab-integrity` is the one that grew, and the only one with a write path. It carries the
**Decision Queue** (run 27), the **evidence drawer** (run 28) and the **decision ledger**
(run 29). `tab-chat` is **frozen** — verify its region hash after any write, and never
edit it.

---

## 1. THE INVARIANTS — break these and the suite is decoration

### Line endings are not interchangeable

```
index.html   LF-pure   (0 CR)   no BOM
server.js    CRLF      (8525)   no BOM
```

**Never use `[System.IO.File]::WriteAllLines`.** It joins with `Environment.NewLine`
(CRLF on Windows) and turned a 0-CR `index.html` into 7557 CRs in run 27 — an LF-pure
file destroyed by the tool meant to help. Use `WriteAllText`, `WriteAllBytes`, or the
`edit` tool. Verify after **every** write, not at the end of the session.

### `node --check` proves it parses. It does not prove it runs.

A page that does not parse still answers 200, still serves perfect data, still logs
nothing, because no statement ever ran. Extract and check **every** `<script>` block
separately (`html-blocks-check.js`) — a single bad block among many is invisible to a
whole-file check.

### `server.js` is the daemon, not the dashboard

> ⚠ **SUPERSEDED 2026-10-09 — this invariant is no longer true.** `server.js` **has** been
> edited since runs 19–30: at **T59-B** the watchdog tick read `rec.t` from the wrong
> object and compared with `>` instead of `>=`, so a live beat was never counted as fresh.
> Both were defects of the *product*, found by a measured check, and both were repaired
> additively with a snapshot taken first. The rule that survives is the **reason** this
> file was kept clean: additive work belongs in `index.html`, and any edit to `server.js`
> is a deliberate event that gets a snapshot and a stated justification — never a drive-by
> fix. **Do not restore `server.js` from a pre-T59B backup** — that would silently undo
> the repair. Current hash and the full change log: §15.

It has been untouched across runs 19–30 and must stay that way. Additive work goes in
`index.html`. Its verified SHA is in §5; if it differs, something outside the agreed
scope happened.

### The live file is mutated during sabotage — never read it mid-run

`decision-queue-sabotage.js` writes mutants into the **live** `index.html` and restores
them from an in-memory copy, verified by SHA taken **before** the run. Reading the file,
hashing it, or screenshotting it while a sabotage is in flight shows you a mutant.

---

## 2. THE VERIFICATION STACK — this is what makes a claim worth anything

Four layers. Each catches what the one above cannot. The runner is `run-regression.js`
(37 checks, sequential, `-Wait` so the exit code is real).

```
run-regression.js  ── parser self-test, then every check in sequence
  │
  ├── decision-queue-check.js   105 contract clauses — fixtures drive the product's
  │                             own render, in a real browser, and read the DOM back
  ├── _run29-click-through.js   21 clauses — REAL CLICKS and a real page reload
  ├── _run30-guard-proof.js     13 clauses — fault injection: make a panel throw and
  │                             require the others to survive AND the failure to be visible
  ├── decision-queue-sabotage.js 12 mutations — each one must CHANGE BEHAVIOUR
  ├── unearned-negative-check.js  "no false all-clear"
  └── 30 more: parsing, self-test 292/292, tab-chat hash, format, live endpoints
```

### The layer that was missing for six runs

**Every contract clause seeded `localStorage` and read the panel back. Not one pressed a
button. Not one reloaded the page.** 105 green clauses, and the write path was untested.
Two real defects lived in exactly that gap:

1. The `record` button called `integRecordDecision(id)` with the stance and the note both
   **undefined**, so pressing it overwrote a good record with an empty one and then
   deleted the draft. A decision with no stance still renders as a chip, so the loss was
   invisible **on screen**, not just to the tests.
2. `hasPrev` was derived from `cmp.newest` when it had to mean "there is an earlier
   sample", which is `cmp.prev`. With a one-sample history it said yes and then
   dereferenced null. `loadIntegrity` is `async`, so the `TypeError` surfaced as one
   unhandled rejection and took the rest of the function with it — including
   `integRenderDecisions`, nine lines later. **The whole tab rendered blank after every
   page refresh.**

> **Seeding state and driving state are different acts of testing.** A suite that seeds
> proves the read path and says nothing about the write path — and a read path can be
> perfect while the write path destroys data.

### A state that only appears on the second load is a state the suite never visited

A fresh browser profile has no history, so it takes the empty branch. A human with a real
profile has a one-sample history and takes the branch that crashed. Neither is wrong;
they are different code paths, and only the second one was broken. **Always test the
second load.**

### What the contract must never do

- Recompute the rule it is testing. A harness that re-derives the answer proves its own
  arithmetic, not the panel's.
- Read the container's `innerText` for content equality — that is the **rendered** text,
  raised by `text-transform` and reflowed by wrapping. A 150-character register line came
  back as three newlines. Use `textContent` **per element**.
- Index `rows[0]` unguarded: the mutation that empties the list is frequently the very one
  the clause exists to catch, and the throw aborts every clause after it.

---

## 3. THE FAULT CATALOGUE — each one happened, each one is transferable

Read this before writing a check or a fix. Full mechanism, in
`minimax-optimus-dashboard` § FAULT CATALOGUE.

| # | Fault | What it looks like | The gate that catches it |
|---|---|---|---|
| 1 | A trailing argument is a **silent no-op** | 16 clauses red, product perfect — `drive(fx, openId, ledgerRaw)` called with 4 args; JS dropped the 4th without a sound | assert arity inside the function and throw |
| 2 | `hasPrev` derived from the **wrong half** of a comparison | `TypeError` blanks a whole tab after every refresh | test the second load; read the stack, not a source window |
| 3 | A button that passes **no arguments** to a defaulted writer | typing a note then pressing `record` destroyed both note and stance | click-through with real clicks |
| 4 | One throw cancels **every later statement** in a render chain | one panel's fault empties the tab | per-panel guard that **paints** the failure |
| 5 | A clause whose **id, matcher and surface disagree** | red against a correct panel; the real surface measured by nothing | measure each surface on itself; grep the source before touching the product |
| 6 | `await` unwraps a promise, so `typeof r.then` is never `'function'` | a counter printed 0 while everything was being awaited | detect the thenable **before** awaiting |
| 7 | A **flag and its explanation from different instants** | text described a different run than the flag beside it | snapshot flag and reason together |
| 8 | A backtick inside a comment inside a **Node template literal** | 4 times: `SyntaxError` with names from the page's own scope | `node --check` the harness **before** running it |
| 9 | A mutation caught by the wrong clause | "survived" on a defect it had plainly caused | `mustBreak` names only clauses that can discriminate |
| 10 | A **fixed** budget under load | 10 s window missed once beside 12 Chrome instances | measure the cost; report the diagnostic on failure |
| 11 | `[System.IO.File]::WriteAllLines` on an LF file | 0 CR became 7557 | `WriteAllText` / `WriteAllBytes` / `edit`; verify CR after every write |
| 12 | `innerText` read as content | a verbatim-quote clause passed a paraphrase | `textContent` per element |
| 13 | `Start-Process` without `-Wait` | `$p.ExitCode` empty — a suite reports green it never measured | always `-Wait`, and report only a **measured** exit code |
| 14 | A counter that writes a **literal** | "0 true" as fixed text — a claim the panel cannot be caught making false | compute it, and guard self-consistency |
| 15 | libuv `UV_HANDLE_CLOSING` at exit | a script dies before printing its summary | `ws.close()` before `proc.kill()` |

### The rule that connects them

> **Before repairing a red, ask whose defect it is.** In runs 27–30, more reds were the
> harness than the product — and every one of them was reported as a product defect with
> total confidence. Sixteen of them agreed with each other, which reads as a strong
> signal rather than a weak one.

---

## 4. THE PANEL GUARD — and why it must be visible

```js
integRunPanel(integRenderVerdict, 'Verdict', ['integ-verdict']);
…
await integRunPanel(integRenderDelta, 'Since you were last here', ['integ-delta']);
```

A guard that **catches and drops** trades a blank tab for a *quiet* one — the exact
failure this tab exists to remove. So a failure is painted into that panel's own
container, in the same UNKNOWN red used for a reading it could not take. A panel that
says nothing must never be mistaken for a panel that measured zero.

**Known dependency, measured by stack trace, not by reading source:** `integRenderDelta`
calls `integRenderRisks` twice at `index.html:4423`. So a fault in risks legitimately
fails delta too. The guarantee is **containment of the panels that do not depend on the
faulted one** — a subset check, so removing the coupling later does not break it, but a
new panel joining the blast radius does.

**And the consequence:** the guard changed what a fault *looks like*. D12 survived with
zero red after the guard landed, because the queue no longer vanished. The mutation had
to re-point at the signal that replaced the silence
(`c.a-reloaded-tab-shows-no-panel-failure`). A guard that makes a fault quieter has not
made it rarer.

---

## 5. THE STATE OF THE BUILD — measured 2026-10-05

> ⚠ **STALE. Measured 2026-10-05. Replaced by §15 (measured 2026-10-09).** Both hashes
> below are wrong now, and the `server.js` line is wrong about *why* it is safe. Kept
> verbatim as a record of that run. **Use §15 for any comparison.**

```
index.html   SHA 1ED3A23C11DA63C343F00D2FE71BD07253A9F84D86AD658CD4060830CA75086E
             CR=0  no BOM  2 script blocks parse (289704 / 15450)
server.js    SHA 24C4B452BF6574BFC7AC8B8D430088F1488325471D055FCE9F3F982064AD9379
             CRLF 8525  no BOM  node --check OK        ← UNTOUCHED since run 19
runner       36/36 REGRESSION CLEAN  RUNNER_EXIT_CODE=0
contract     105/105        click-through  21/21       guard  13/13
sabotage     12/12 mutations caught, live panel restored byte-identical
self-test    292/292 ok=true
tab-chat     byte-identical to the pre-run-29 AND pre-run-27 backups
```

Backups live beside the live file: `index.html.PRE-RUN27-*`, `PRE-RUN29-*`,
`PRE-RUN29B-*`, `PRE-RUN29C-*`, `PRE-RUN30-*`. **Restore is verified by SHA taken before
the run, never by choosing a backup by filename** — run 23 restored a pre-repair state
over a finished repair and deleted the work.

---

## 6. HOW TO ADD A PANEL — the order that worked

1. **Pure rule, no DOM, no fetch.** `integDecisions(risk, ports)` returns
   `{rows, checked, unpaid}`. It is driven from fixtures, so it is testable without a
   browser. This separation is load-bearing.
2. **Zero new requests.** Derive from `integ.risk` and `integ.ports` — already in hand.
   `loadIntegrity` serialises three heavy endpoints because they reject each other in
   parallel; a fourth is a new race.
3. **UNKNOWN is first-rank.** `null` is impossible, `0` is a measurement. A failed
   fetch produces a row that says UNKNOWN and can never reach the empty state.
4. **The empty state is a claim**, so it lists the conditions it evaluated with their
   values. A bare "nothing here" is indistinguishable from a panel that never ran.
5. **Guard it.** Register it in the `loadIntegrity` chain through `integRunPanel`.
6. **Write the clause that can go red, then the mutation that must make it red.**
7. **Prove the gate fires.** Call it with the offending shape and require the throw.

---

## 7. THE R0 QUEUE — his decisions, not yours

Seven items were escalated and are **his** to answer. Do not execute any of them. Do not
re-litigate them. They are visible in the Decision Queue with their raw evidence one
click away.

1. **split-brain** — 2 guardrails, ~20–30 supervisors, orphans under dead parents. Which root survives. *First question in the queue.*
2. **port 3010** — S4U + RunLevel Highest, session 0, CORS `*` on the whole disk, no register entry.
3. **canonical build** — `C:\Program Files\Qwen\Qwen.exe` is unpatched; Windows starts it by default.
4. **desktop bridge :3097** — no supervisor entry, nothing to restart, no log to write to.
5. **interleaved writes in `supervisor.jsonl`** — root cause is two copies starting at once, in `supervisor.js`. Not repairable from the dashboard.
6. **duplicate backups** — `QwenSystem Weekly Backup` vs `QwenWeeklyBackup`.
7. **`readBuildCurrency` runs its own process probe**; **`copyCode` has 2 of 3 refusal paths mute** (in frozen `tab-chat`); **`C:\Program Files\Qwen`** is an old install needing destructive removal.

---

## 8. COMMANDS THAT ACTUALLY WORK HERE

```powershell
# the whole suite, exit code measured
$p = Start-Process node -ArgumentList 'run-regression.js' -NoNewWindow -Wait -PassThru `
     -RedirectStandardOutput '_r.txt' -RedirectStandardError '_r.err'
"RUNNER_EXIT_CODE=$($p.ExitCode)"

# one mutation, to see WHICH clauses it turned red
node decision-queue-sabotage.js D12

# diagnostics, named by run
node _run29-diag2.js        # three links measured separately
node _run29-reload-diag.js  # second-load behaviour
node _run29-chain-sweep.js  # every renderer × every data state
node _run30-guard-proof.js  # fault injection
node _run29-tab-chat.js     # frozen-region hash

# never: Remove-Item (blocked by policy). Clean up with mavis-trash.
# never: run patch_bridge_code.js. never: send messages in the Qwen UI. never: show secrets.
```

Chrome is at `C:\Program Files\Google\Chrome\Application\chrome.exe`; Node 26 has global
`WebSocket` and `fetch`; **there is no `playwright` and no `puppeteer`** — every browser
check is raw CDP, which is why they all share the same launch/connect/cdp preamble.

---

## 9. THE RULES HE HAS ALREADY HAD TO SAY

1. **"If a working system could be improved, say it in one line and let him decide.
   Never edit the mechanism yourself."** Exception: a defect that hides the thing you were
   asked to deliver *is* in scope — fix it, and say plainly that it pre-existed.
2. **"Don't ask questions you already know the answer to. You have to follow a goal."**
3. **"Execute the verb, not the topic."** Do the action asked, not the one you find more
   valuable. Disagree once, in one line, then comply.
4. **Never report a green you did not measure.** "No errors" is not "verified working".

---

## 10. WHAT A FRESH SESSION SHOULD DO FIRST

1. Read this file.
2. `node run-regression.js` — if it is not clean, the first failure is the work.
3. Hash `index.html` and `server.js` and compare with §5. A difference means someone else
   changed something; find out what before writing.
4. Read `_run30-regression.txt` if it exists — it names the last measured state.
5. Never start with "the dashboard looks fine."

---

## 11. THE OPERATING WORKFLOW — how to WORK with what was built

This section is about *using* the dashboard. The build workflow that produced it is a
different artefact and lives in the general skill (§12). Everything below is the daily
loop, and it exists because the tool earns its keep through the decisions it captures —
not through the pixels it draws.

### 11.1 The loop, in order. Do not reorder it.

| # | Step | Gate — do not pass until |
|---|---|---|
| 1 | **Open** `http://127.0.0.1:3098`. Wait for the tab to settle, not just to load. | Every panel has painted. A blank panel is `UNKNOWN`, never "zero". |
| 2 | **Read the header band first.** It carries the verdict and the age of the reading. | You can say out loud how old the numbers are. If you cannot, stop — a number without an age is a rumour. |
| 3 | **Integrity tab → Decision Queue.** This is the only panel that ASKS you something. | You have read the queue. Everything else is reporting; this one is requesting a decision. |
| 4 | **For each open row: decide, or explicitly defer.** | Every row is marked — an undecided row is a row you will forget. |
| 5 | **Record the decision**: stance (accept / act / revisit) + a one-line note. | The chip shows the stance AND the note. A stance with no note is an opinion you cannot audit. |
| 6 | **Pull the evidence drawer** for the row you just decided. | You know why you decided, not just what you decided. |
| 7 | **Check the R0 queue in §7.** | You know which items are his and which are yours. |
| 8 | **Stop.** The dashboard is a surface for a decision, not a room to live in. | — |

The loop is eight steps because each of the first seven has a gate. A step you cannot
pass is a finding — write it down, do not route around it.

### 11.2 What each stance MEANS — these are not moods

| Stance | Means | What must exist beside it |
|---|---|---|
| **accept** | The state is correct and I am not acting on it. | Nothing. This is a real answer, not a deferral. |
| **act** | Something must change. | The change is named. A row marked `act` with no named change is a wish. |
| **revisit** | I do not have enough to decide yet. | What would resolve it, and by when. `revisit` without a trigger is a `defer` with better branding. |

A decision is only erased, never edited: strike it and record a new one with the
timestamp. The row itself survives the answer — that is the whole point of the queue.

### 11.3 WHEN something looks wrong — the triage order, in this order

1. **Is the panel blank, or is it saying `UNKNOWN`?** Blank = a fault you have not met
   yet; `UNKNOWN` = the guard caught something and told you. Different problems.
2. **Is the reading old?** Compare the header age against the refresh interval. A panel
   showing a 20-minute-old reading while the source moves every 5 seconds is stale, not
   broken, and the fix is different.
3. **Is the source down?** `lastGood` is supposed to survive a source failure, marked
   old. If it vanished instead, that is a regression — go to §4, the guard.
4. **Is the tool lying?** A number that contradicts what the system did is worse than a
   missing number. Treat it as critical regardless of how green the suite is.
5. **Only then** look at the code. Measure before repair; ask "whose defect is this" first.

### 11.4 The five things you must NEVER do here

1. **Never `docker container prune -a`.** The swarm was lost once already, 2026-08-08.
2. **Never edit `tab-chat`.** Frozen since run 19. Two of its three refusal paths are
   mute — see the R0 queue, item 7. Fixing them means thawing the tab, which is a
   decision, not a chore.
3. **Never trust a backup you chose by filename.** Restore only from a SHA taken *before*
   a run. Run 23 restored a pre-repair state over a finished repair exactly this way.
4. **Never stop a regression run without knowing which phase it is in.** The sabotage
   suites mutate the live `index.html` on purpose and restore from an **in-memory** copy
   at the end. Kill the process during that window and the undo dies with it — which is
   exactly what happened on 2026-10-05, leaving a mutation on disk that turned four green
   suites red and read as a product regression. It was one line. The undo is not on disk,
   so **the newest backup is not necessarily the state you want**: the newest is
   `PRE-RUN30` (`1ED3A23C…`), and the run-30 state (`9405B5E5…`) has no backup at all.
5. **Never expect a recoverable delete to free space on this machine.** `rm --` routes to
   `mavis-trash`, which calls `SendToRecycleBin` — so it moves files into
   `C:\$Recycle.Bin`, **the same volume as the target**, and frees exactly zero bytes.
   It also fails outright (CLIXML) on directories with many files, which is why
   `Temp` (19,3 GB) and `npm-cache` (6,5 GB) cannot be trashed at all. Measured
   2026-10-05: recycling 1,75 GB of pip cache moved the disk by 0,00 GB. So on a space
   emergency: report what you actually freed, and hand the operator the command —
   `Clear-RecycleBin -DriveLetter C -Force`, `npm cache clean --force`,
   `pip cache purge`. Do not empty the bin for him and do not reach for a permanent
   delete to make the number look better.

### 11.5 When you add work to this dashboard

Follow §6 (the order that worked) and the four proofs, in this order. The guard from §4
is not a thing you add at the end — a panel added outside the guard is the exact defect
that made the whole Integrity tab blank on every refresh, and it will happen again,
because the failure is invisible until it is total.

---

## 12. RELATED ARTEFACTS — read in this order

A session with zero context should read exactly these three, in this order, and stop.

1. **This file** — what exists, where it is, what it is not allowed to do.
2. **`minimax-optimus-dashboard` (general skill)** — the method this build followed, and
   the fault catalogue with the gate for each of the 21 mechanisms (A1-A4, B1-B17). Read §3 and the
   catalogue; the rest is reference.
3. **`minimax-optimus-dashboard/dashboard-build.dsl.js`** — the executable build
   workflow, registered in the dynamic-workflows panel as
   **"Dashboard Build — zero-context, seven phases"**, status `pending_review`.
   Use it when the task is to BUILD a dashboard for a different system, not to work
   with this one. Seven phases: preflight, discovery, plan (R0, then STOP), build,
   verify, iterate, handover.

The relationship in one line: **this file is the particular, the general skill is the
method, the workflow is the method running.** If you are here to fix or extend the Qwen
dashboard, you need files 1 and 2. If you are here to build a dashboard for something
else entirely, you need file 3 and file 2, and file 1 only as a worked example.

---

## 13. PORT MAP — measured live 2026-10-09 21:15, not from source

Read from the listening-socket table and from each owning process's command line.
**A port listed in `server.js` is a port the code *talks about*. A port listed here is a
port that was *answering*.** Those two sets are not the same, and the difference is where
the real faults live.

| Port | Measured state | Owner | What it is |
|---|---|---|---|
| **3098** | **LISTENING** | `node …/qwen-system/dashboard/server.js`, pid 41276 | The dashboard itself. `PORT` is hard-coded at `server.js:49`. |
| **3097** | **NOT LISTENING** | — | Desktop bridge. `DESKTOP_BRIDGE_URL`, `server.js:60`. Also polled by `/api/models` (`:111`) and probed by `/api/desktop/status`. **Its absence is a measured fault, not a silent default.** |
| **3099** | not listening | — | `SUPERVISOR_URL`, `server.js:50`. |
| **3010** | LISTENING | pid 10216, **command line unreadable** | Matches R0 queue item 2 (S4U, RunLevel Highest, session 0). An unreadable command line at `RunLevel Highest` is the shape of that item — the process is not inspectable by this session, which is *why* it is queued. |
| **3060** | LISTENING | Hermes `whatsapp-bridge/bridge.js` | Unrelated to Qwen. Do not read a port collision here. |
| **3071** | LISTENING | `~/.minimax/whatsapp-mcp/bridge.js` | Same — **minimax's own copy**, not Hermes's. Separate universes. |
| 3011, 3012, 3013, 3015, 3016, 3017 | not listening | — | Declared bridge list, `server.js:78–83` (shell, filesystem, system-monitor, fetch, database, docker). Declared ≠ running. |

**The trap:** the declared list at `server.js:78–83` is a constant. It is not a reading, it
is a description of intent written once. `/api/ports` is the reading. Never answer "which
bridges are up?" from the constant.

---

## 14. TELEMETRY MAP — every route, what it is for

47 live routes, enumerated from the `req.method === … && parsed.pathname === '/api/…'`
form (the tests embed these strings too, so grep alone over-counts — this list is the
handler table only).

**Read-only — the system telling you something**

| Route | Reads |
|---|---|
| `/api/ports` | Listening sockets, owning PID, process name, swarm role |
| `/api/status` | The overall state the header band is built from |
| `/api/telemetry` | Live host telemetry + unsupervised-bridge 3097 visibility |
| `/api/measured-census` | A census that was *measured*, not inferred |
| `/api/anti-lie-watchdog` | The watchdog that exists to catch the dashboard lying |
| `/api/risk-scan` / `/api/risk-summary` | The risk register, raw and condensed |
| `/api/code-currency` | Whether the build on disk is the build being served |
| `/api/timeline` / `/api/supervision-trend` | History and trend |
| `/api/bridge-log` | The bridge's own log, with outages marked |
| `/api/route-inventory` | Which declared routes are **unreachable** — catches dead UI buttons |
| `/api/self-test` | The daemon's own parser self-test |
| `/api/remediation/plan` / `/compare` | What it would do, and the delta — **plan and compare only; the destructive one is separate** |
| `/api/restore/plan` | Restore preview |
| `/api/backup` → POST | Write |
| `/api/models` / `/api/qwen/tools` | Bridge model list, live with a static safety net |
| `/api/desktop/status` | Bridge 3097 health |
| `/api/bridge/probe` / `/api/cli/health` | Reachability probes |
| `/api/conversations`, `/view`, `/stats` | Conversation store |
| `/api/config/view`, `/api/mcp/config` GET | Stored configuration |

**Write — these change something. R0 territory unless explicitly asked for.**

| Route | Does |
|---|---|
| `/api/chat/send` | Sends into the Qwen UI. **Never as a test.** |
| `/api/reload` | Restarts the dashboard |
| `/api/exec` / `/api/terminal/run` | Runs a command |
| `/api/restart/<name>` | Restarts a named process |
| `/api/reconcile`, `/api/reconcile-restart` | Reconciler, and the restart that follows it |
| `/api/restore/execute` | **The destructive one.** Plan first, always. |
| `/api/savepoint`, `/api/savepoints/verify`, `/api/savepoints/plan` | Savepoints |
| `/api/backup` POST | Backup |
| `/api/download`, `/api/config/save`, `/api/mcp/config` POST | Writes |
| `/api/conversations/export` / `/delete` | Conversation store |
| `/api/qwen/launch` | Launches Qwen |

---

## 15. THE STATE OF THE BUILD — measured 2026-10-09 21:15

**This replaces §5 for any comparison.** Read both; the difference is the change log.

```
index.html   428.571 B   SHA 7D54312AB994026C778D0402889BC55B46BBBCDEEF7CA85ECF85E1E41D15AA66
             CR=0   no BOM
server.js    541.758 B   SHA BAD7306B42D386AB14D64B4088C68415E0627CAE240BA0C956C927E3BA7B51A6
             CR=9399  no BOM   node --check OK
dashboard    pid 41276, started 19:15:15
guardrail    pid 45568, single instance (split-brain resolved twice this day)
```

`index.html` is LF-pure and `server.js` is CRLF — **that invariant from §1 still holds**.
Both are BOM-free.

### What changed since §5 was measured

1. **T59-B — `server.js` was edited.** Watchdog tick read `rec.t` instead of the timestamp
   and compared `>` instead of `>=`. Snapshot
   `undo/server.js.PRE-T59B-20261009_170416`. **This is why §1's "untouched" is struck out.**
2. **T59-C / T61 — the certification harness was repaired twice**, in
   `C:\Users\apviz\QWEN_BACKUP\tcv_invariance_harness.js`, not in the product.
3. **The invariant suite reached `CERTIFIED 11/11`** — `pass=11 fail=0 unknown=0` on three
   consecutive passes, exit 0. Log: `tcv_cert_t61b_20261009-202449.log`.
4. **Split-brain was resolved twice.** Two orphaned `guardrail.js` processes (18920, then
   24560) were stopped under one standing R0. A single instance remains.
5. **Version control exists.** Two private repos, both on `main`, local and remote verified
   identical: `apvizual-max/Optimus-Minimax-Qwen-Bridge` and
   `apvizual-max/Optimus-Qwen-Assurance`. `.gitattributes` sets `* -text` so a checkout
   cannot rewrite LF files to CRLF and invalidate every recorded SHA.

### Two open faults this section does not close

- **Split-brain can return.** `supervisor.js` has three live processes still running the
  pre-T48 code; the repair does not take effect until they are restarted. Restarting them
  is an R0 item, not a chore.
- **Two journals truncate rather than append** — `logs/guardrail.jsonl` (~33 KB) and
  `logs/supervisor.jsonl` (~7 KB) lost between commits. Both are silent data loss on a
  file the system's own history depends on.

---

## 16. TOPOLOGY AND ZERO-CONTEXT REBUILD — how to stand this up from nothing

This section is the one that lets an agent with **zero context** rebuild the system. It
was written from `registry.json` and `scripts/`, both read on 2026-10-09 — not from memory.

### 16.1 The single source of truth is `registry.json`, not `server.js`

`qwen-system\registry.json` (v2.0, last modified 2026-09-25) declares every service.
`server.js` has its **own hard-coded list** at lines 78–83, and the two have drifted:

| Service | port | `registry.json` | declared in `server.js:78-83` | script |
|---|---|---|---|---|
| filesystem | 3012 | enabled, **critical** | yes | `AI_Tools\mcp-filesystem-sse-bridge.js` |
| shell | 3011 | enabled, **critical** | yes | `AI_Tools\mcp-shell-fast-bridge.js` |
| dashboard | 3098 | enabled, not critical | yes | `qwen-system\dashboard\server.js` |
| system-monitor | 3013 | enabled | yes | `AI_Tools\mcp-system-monitor-bridge.js` |
| fetch | 3015 | enabled | yes | `AI_Tools\mcp-fetch-bridge.js` |
| database | 3016 | enabled | yes | `AI_Tools\mcp-database-bridge.js` |
| docker | 3017 | enabled | yes | `AI_Tools\mcp-docker-bridge.js` |
| **git** | **3014** | **`enabled: false`** | **ABSENT** | `AI_Tools\mcp-git-bridge.js` |

**The git bridge on 3014 exists on disk and is declared in `registry.json`, but is absent
from the `server.js` list.** That is a measured divergence, not an inference — the file is
there, the registry entry is there, the `server.js` entry is not. If you are rebuilding,
read `registry.json`, not the `server.js` constant.

All seven bridge scripts were verified present on disk under
`C:\Users\apviz\AI_Tools\` — **one level above `qwen-system`**, which the `../` in each
`script` path refers to.

### 16.2 Supervisor parameters (measured, from `registry.json`)

```
port 3099 · healthCheckIntervalMs 10000 · restartDelayMs 3000
maxRestartAttempts 5 · restartCooldownMs 300000 · log logs/supervisor.jsonl
```

### 16.3 The runtime that matters

Every MCP bridge is invoked through **bun**, not node:

```
C:\Program Files\Qwen\resources\bun\bun.exe  x -y mcp-remote http://127.0.0.1:<port>/sse
timeout 60000
```

The bridges themselves are node scripts. `bun` is the launcher Qwen Studio uses to reach
them over SSE. If `bun` is missing from PATH this whole layer fails with a message that
looks like a network fault.

### 16.4 The rebuild order — do not reorder

1. `AI_Tools\mcp-shell-fast-bridge.js` (3011) and `mcp-filesystem-sse-bridge.js` (3012) —
   both **critical**; everything else depends on the shell existing
2. the remaining bridges: 3013, 3015, 3016, 3017
3. `qwen-system\dashboard\server.js` (3098) — binds to `127.0.0.1` only
4. `qwen-system\supervisor.js` (3099) — reads `registry.json`, health-checks every 10 s
5. `qwen-system\guardrail.js` — **exactly one**, never more (§15)
6. `qwen-system\root-guardian.js` via `scripts\root-guardian.cmd`

### 16.5 The scripts that already do this — use them, do not rewrite them

`qwen-system\scripts\` contains 27 files. The ones that matter for a rebuild:

| Script | Does |
|---|---|
| `start-supervisor.vbs` · `start-guardrail.vbs` · `start-dashboard.vbs` | the three launchers |
| `install-startup.ps1` · `install-dashboard-startup.ps1` | register them at Windows login |
| `root-guardian.cmd` | the root guardian entry point |
| `rebuild-settings.ps1` · `fix-settings-json.ps1` | repair the Qwen settings files |
| `apply-asar-patch.ps1` / `.bat` | the asar patch (see §16.7) |
| `reconcile-custom-mcps.ps1` | reconcile MCP entries in the Qwen config |
| `create-savepoint.ps1` · `plan-restore.ps1` · `execute-restore.ps1` | savepoint / restore cycle |
| `backup-qwen-ecosystem.ps1` · `weekly-backup.ps1` · `schedule-weekly-backup.ps1` | backups |

`docs\ARCHITECTURE.md`, `docs\OPERATIONS.md`, `docs\HERMES_MCP_CONFIG.md` and
`docs\README.md` are also on disk and were written by the build, not by an agent. Read
them before inventing anything.

### 16.6 Diagnosis order when the system is down

Work **outside in**, and never restart the thing you are diagnosing before you have read
its log:

```
0. which process?  Get-CimInstance Win32_Process -Filter "Name='node.exe'" | ? { $_.CommandLine -like '*<name>*' }
1. which port?    Get-NetTCPConnection -State Listen   — a declared port that is not listening is the fault
2. what did it say?  logs\supervisor.jsonl, then logs\guardrail.jsonl
3. only then restart
```

Measured 2026-10-09 21:15, this is what "down" actually looked like: **3098 listening,
3097 and 3099 dead, one guardrail, zero supervisors.** Declared ≠ running, and the
declaration lives in `registry.json`.

### 16.7 The asar patch — the one irreversible-ish step

`C:\Program Files\Qwen\Qwen.exe` is an **unpatched install**; Windows starts it by
default, while the patched build lives elsewhere (`scripts\deploy-local-patched-qwen.ps1`).
Reconciling the two is an R0 item, never a chore — see the R0 queue, item 3. Read
`docs\ARCHITECTURE.md` §asar before touching it, and never `Remove-Item` it.

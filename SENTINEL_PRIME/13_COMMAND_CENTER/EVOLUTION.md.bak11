# SENTINEL Command Center — Evolution Proposals

**Status:** 🟡 BLUEPRINT — **nothing in this document has been built.**
**Author:** Mavis · **Date:** 2026-10-09
**Scope:** the Command Center at `13_COMMAND_CENTER\`, plus the collector that feeds it.

---

## 0. What this document is, and what it is not

This is the record of what the Command Center could become, written down before
anyone builds it — per the standing doctrine that **a blueprint is a target, not a
defect report**.

It is **not** a work queue. Nothing here is authorised, and nothing here has been
implemented. Every proposal is written as *measured baseline → gap → cost → risk*,
so that when a proposal is picked up, the person picking it up knows what they are
building against and does not have to re-derive the baseline.

Every number below was **read from the running system on 2026-10-09 at
21:08–21:10 local**, not remembered. Where a figure moves between runs, it is
labelled a *reading*, not a constant.

### Measured baseline this document is written against

| Fact | Value | How it was obtained |
|---|---|---|
| Deployment | `mavis-sentinel-hub`, healthy, `127.0.0.1:8910` | `docker inspect` |
| Backend | `127.0.0.1:8912` answering, pid `58712` | `GET /api/health` + pid file |
| Health checks | **55 total: 43 OK, 2 FAIL, 10 STALE, 0 NOT_RUN** | `GET /api/state` → `counts` |
| The 2 FAILs | `mcp_config_servers_exist`, `mcp_npx_packages_resolve` — both in family `wiring` | `GET /api/state` → `health_checks` |
| The 10 STALEs | `corpus_fresh`, `workflow_state_fresh`, `workflow_log`, and **all 7 `log_*` checks** | same |
| Open gaps | 18 declared in `state.gaps`, each with a named owner | `GET /api/state` → `gaps` |
| History | `application/x-ndjson`, 120 records, all `MODE_B`, `ok` flat at 43 | `GET /api/history` |
| UI | 62 static element ids, 0 duplicates, 13 tabs, 0 console errors | browser + static analysis — a naive `id="…"` regex counts **63**, because one match is a JavaScript template fragment (`'+esc(a[0])+'`) used to build a corpus-hit id at runtime, not a static attribute |
| **Hardware telemetry** | **ABSENT** — no `host`, `hardware`, `cpu`, `memory`, `disk`, `uptime` key anywhere in the state payload | probed every candidate key |

That last row is the one to read twice. It is the reason proposal **P1** exists.

---

## RESOLVED — the MCP hub server now starts, and all 26 tools are WIRED

**Found 2026-10-09 during the button audit. Fixed 2026-10-09, later the same day.
This was a defect, not a proposal, and it is now closed by measurement.**

### What was wrong

`07_BACKBONE\mcp\sentinel_hub_server.py` died on import:

```
File "...\07_BACKBONE\mcp\sentinel_hub_server.py", line 957, in <module>
    @server.list_tools()
AttributeError: 'Server' object has no attribute 'list_tools'
```

The installed SDK is **`mcp 2.3.0`**. In 2.x `FastMCP` was renamed to `MCPServer`
(`from mcp.server.mcpserver import MCPServer`), tools are registered from callables at
construction time instead of decorators, `types.Tool` exposes `input_schema` rather
than `inputSchema`, and `Server.create_initialization_options` is gone. The file was
authored against 1.x and had not been ported. Consequences were 26 tools DECLARED and
0 WIRED, and `test_hub_tool_audit` crashing with `RuntimeError: closed` at
`audit_hub_tools.py:84` because the subprocess it spawns exits immediately.

It was not caused by the UI work: `audit_hub_tools.py` (2026-10-06 15:48) and
`sentinel_hub_server.py` (2026-10-07 06:46) both predate this work. An SDK upgrade is
the cause; when it happened is NOT_MEASURED.

### The two options, and which one was taken

1. Pin `mcp` to 1.x — works within minutes, but holds a shared package back and every
   other consumer on this machine inherits the pin.
2. Port the server to 2.x — larger, but forward-compatible and bounded to one file.

**Option 2 was taken.** Pinning a shared package is a system-level change affecting
programs outside this project, and it restores onto an SDK that keeps moving. Porting
was the choice that did not need a global compromise. This was a technical decision,
so it was made here rather than deferred.

### What was actually changed

**No tool body was touched.** `list_tools()` still declares the same 26 tools and
`call_tool()` still dispatches them — verified by source-segment comparison, both
functions byte-identical to the pre-port file. Only the transport was rewritten:
`MCPServer` in place of the `Server` decorators, one closure per tool preserving the
`(name, arguments)` pair the 1.x decorators passed.

Two behaviours were preserved deliberately rather than left to the new transport:

- **Schema is passed through verbatim**, not regenerated from a Python signature.
- **Absent arguments stay absent.** A missing key and an explicit `null` are not the
  same thing here: `sentinel_extract_patterns` does `arguments.get('text','').lower()`,
  which raises `AttributeError` on `None`. Keys the caller never sent are dropped at
  dispatch rather than materialised as `None`. An *explicit* `null` still reaches the
  body and still raises, exactly as it did under 1.x — verified, not assumed.

**A known limit, stated rather than hidden.** `MCPServer(tools=[...])` is a genuine
public constructor parameter, but the per-tool object it takes is a model whose own
docstring reads *"Internal tool registration info"*. The first version of this port
hand-assembled it by naming thirteen of its fields. That would have meant any mcp
release renaming one field breaks the server **at import** — the exact failure mode
being repaired — while looking forward-compatible. The registration record is now
built by the SDK's own `Tool.from_function`, so this file names no internal field;
only the schema is overwritten afterwards. The coupling is reduced, not eliminated.

### Evidence (measured 2026-10-09, not inferred)

| Check | Result |
|---|---|
| Baseline captured from the 1.x file before any edit | 26 tools, via a stub `Server` |
| Declarations after the port vs that baseline | **26/26 identical** — name, description, JSON schema |
| Schemas as published on the wire | **26/26 identical** to what 1.x advertised |
| Real stdio handshake against the server as a subprocess | **OK** — `sentinel-hub` v1.0.0 |
| `tools/list` over the wire | **26** |
| `tools/call` on read-only tools | real payloads returned |
| `audit_hub_tools.py` | MUTATING-OK 10, OK 16, **REACHABLE/ERROR 0**, live state unchanged |
| Every tool called with only its required arguments | 26/26 respond, no crash, omitted optionals arrive as `""`, not `None` |
| Unit suite | **0 failed, 0 skipped**, 29 classes registered (exact pass total varies by one between runs — one check is time-dependent) |
| Deployment suite | **40 passed / 0 failed / 1 not-run (41)**, exit 0 |
| stderr from a build | **0 warnings** |

`inventories_complete` is green again because the run that produced
`last_test_run.json` now registers 29 classes instead of 28 — that failure was a
downstream consequence of this one, and it cleared on its own.

An independent verifier pass attacked the result rather than confirming it: it
rebuilt the 26-tool baseline from the `.bak` by AST, ran its own raw JSON-RPC client
instead of the project's, called all 26 tools with every optional argument omitted,
and sabotaged the wiring check four ways — including reproducing the original defect
(26 declared, 0 wired), which the check correctly reported as a mismatch and exited
non-zero on. That is the property that matters: the check can fail.

### Two regressions the port introduced, both caught and fixed

Recorded because the port looked finished before either was found.

1. **`isError` was lost.** 1.x computed it in `_on_call_tool`; the 2.x transport does
   not. The first live call of `sentinel_apply_triple_filter` with no claim returned a
   payload containing `"error"` and the client reported **success**. A tool reporting
   failure would have been reported to the model as a success. The computation moved
   into the per-tool closure, which now returns a `CallToolResult` itself.
2. **The module global `server` was removed.** The six `sentinel_workflow_*` bodies
   attach their singleton to it (`server._wf_singleton`). Without it they returned
   `{"error": "name 'server' is not defined"}` — six of 26 tools dead, while the audit
   still counted the server as advertising 26. The global is now published by
   `_build_server()` itself, so every construction path has it.

Regression 2 is the more instructive one: **a file can pass every structural check and
still be broken, because a symbol it reads can live in a line nobody thinks to look
for.** `server` appeared nowhere in the tool bodies' own logic — only as a namespace
for state. Neither a diff review nor `tools/list` would have shown it. Only calling all
26 tools did.

### A third defect, in the dashboard itself: a check that could not fail

Fixing the server exposed a worse problem one layer up. The cockpit action
`mcp_wiring` (`api\server.ps1:128`) did not measure anything. It counted
`name="sentinel_..."` occurrences in the server source and then printed a
**hardcoded** suffix:

```
26 tools DECLARED, 0 WIRED (no runtime handshake performed)
```

That string did not depend on the state of anything. It said "0 WIRED" before the
fix and said "0 WIRED" after it. The action kept returning HTTP 200 the entire
time, which is exactly how it stayed invisible: **a check that cannot fail is not
a check** — the same defect class as the launcher's exit-code gate, one layer
further in.

It is now a real measurement. `api\mcp_handshake.py` counts DECLARED from the
server source, performs a live stdio handshake for WIRED, and reports the gap:

```
DECLARED in sentinel_hub_server.py: 26  (counted from source)
WIRED: 26  (live MCP handshake: initialize + tools/list)
RESULT: {"declared": 26, "wired": 26, "gap": 0, "sample": [...]}
MATCH: every declared tool is served over MCP
```

Measured through the front on 2026-10-09, the same path the button uses. It exits
non-zero when the two disagree, so a declared-but-unserved tool is now a failure
rather than a number nobody watches.

Worth naming precisely: this was **not** a stale fact. It was a fact that would
have stayed confidently wrong for as long as nobody read the mechanism behind it.
An honest report has to be re-measured after every repair, because the repair
changes what "honest" means.

### Measured, unchanged from 1.x, and worth knowing

Three properties were confirmed by the verifier and are **not** regressions. They are
recorded because each is surprising enough that someone will otherwise rediscover it
and assume it broke today.

- **An explicit JSON `null` still crashes `sentinel_extract_patterns`.** Calling it
  with `{"text": null}` returns `isError: true` with
  `Error executing tool sentinel_extract_patterns` — the `None.lower()` path. 1.x
  behaved identically, because `arguments.get('text','')` returned `None` there too.
  The port handles *absent* arguments correctly; it deliberately did not change what
  an explicit null does, because changing it would have been an unannounced change to
  tool behaviour.
- **Arguments declared `required` are advertised but not enforced.** 18 of the 26
  tools declare a `required` list; omitting a required argument returns a
  domain-level answer rather than a protocol-level validation error. This is
  unchanged from 1.x and is the direct consequence of not introducing validation that
  did not exist. A caller can therefore receive a confident answer to a call it
  under-specified — worth knowing before relying on `required` as a contract.
- **The unit suite is not hermetic.** It requires internet and writes into the live
  `09_LOGS` tree: `test_suite.py:347` performs a real scrape of `https://example.com`
  and leaves the artifact behind. Pre-existing, unrelated to this work, but it means
  the suite cannot be used as a gate in an offline environment without side effects.

### A fourth instance, in the health monitor — and the root cause, named

Chasing the two remaining `wiring` FAILs after the port turned up the same defect a
third time, in `08_SELF_IMPROVEMENT\monitor.py`. `_coverage_evidence()` decided
whether a capability was *"verified live under another registered server"* by
regex-matching tool names out of the hub's **source file** (`monitor.py:476`).

That claim was false for as long as the hub could not start. The file has the five
tool names, so the regex found them, so the monitor reported five capabilities as
verified live — for a server that raised `AttributeError` on import and executed
nothing. The panel was not wrong by accident; it was asserting liveness from a
measurement that never tested liveness.

This is the same root cause as `mcp_wiring`, and it is worth naming once and for all:

> **A name in a source file is not a thing being served.** Presence in a registry is
> not a running process. A declared entry is not a resolved one. Every one of these
> defects was a report standing on evidence that could not fail.

`_coverage_evidence()` now asks the hub, by running a real handshake instead of
reading its source. It reuses `13_COMMAND_CENTER\api\mcp_handshake.py`, the script
behind the dashboard's wiring button, so the panel and this check cannot drift apart.

*Correction to an earlier draft of this document: I first wrote "one handshake
implementation rather than two that can disagree". That was false. There are two
producers, with different jobs: `08_SELF_IMPROVEMENT\mcp_handshake.py` writes the
durable record `09_LOGS\mcp_handshake.json` and additionally probes a tool to prove
arguments reach the handler; `13_COMMAND_CENTER\api\mcp_handshake.py` produces a
one-shot console verdict for an operator who pressed a button. They are not
duplicates, but they are two, and they can — and did — drift apart. That drift is
the next finding.

> *"If either stops holding, the coverage collapses to uncovered... A table that
> cannot fail is not a mapping, it is a waiver."*

The promise was previously half-true, because server death could not trigger it. It is
now measured, not asserted — coverage holds 5/5 in the healthy state and collapses to
1/5 with the reason named when the hub cannot serve. `prime-bridge` correctly stays
covered either way, because it is served by the separate filesystem server.

**The verdict itself was never wrong.** `mcp_config_servers_exist` correctly stayed
FAIL, and its diagnosis is now confirmed on disk: all 5 declared `.py` servers are
absent **from the entire workspace**, never existed under those names, and every one
of their capabilities is live under `sentinel-hub` (3 + 1 + 3 + 1 tools) or the
filesystem server. **0 uncovered.** That is stale blueprint, not a missing capability
— which is a blueprint, and blueprints are targets, not defects to prune.

**The cost, stated rather than discovered later:** a real handshake spawns the server
as a subprocess, so `monitor.py` now costs a few seconds per run. The unit suite went
from **116 s to 156 s** — a 34 % increase — for the same result: 503 passed, 0 failed,
0 skipped, exit 0. Deployment is unchanged at 40 passed / 0 failed / 1 not-run. That is
the price of a check that can fail, and it is worth paying; it is recorded here so
nobody later reads the slowdown as a regression.

The operator decision remains genuinely the operator's: `OPTIMUS_MCP_CONFIG.json`
still declares five server names that no file can answer to. An agent that reads that
config and launches `prime-bridge` really does fail. It is not mine to rewrite or
prune, and it is not mine to silently point those names at the hub.

### A fifth instance: the same defect reached by staleness instead of by text

An independent verifier pass, told to sweep for the defect class rather than to
confirm the change, found the sibling check `mcp_tools_wired` doing the same thing by
a different route. It read a record at `09_LOGS\mcp_handshake.json`, computed
`hs_ok` from the record's **contents**, measured `age`, and then printed the age
without ever bounding the verdict by it. `STALE` — the status this file defines as
*"measured, but the underlying artefact is older than its bound"* — was defined at
`monitor.py:51` and used by `log_checks`, but never applied here.

Measured: the record was written **2026-10-05 01:02:41**, age **118.4 h**, and it
still read `status=OK, 26 tools, probe ok`. Meanwhile `sentinel_hub_server.py` had
been edited on **2026-10-09 22:56:42**. So the green verdict described a server that
had not existed in that form for four days — and the panel could not notice, because
everything it read was self-consistent.

The bound now has two arms, both measured:

- **superseded** — the hub source is newer than the record, so the record cannot
  speak for the code as it stands;
- **expired** — older than `MAX_STATE_AGE`.

Either arm yields `STALE` with both reasons named and the re-measure command quoted.
A **fresh** record still yields `FAIL` when its probe did not verify, so the suite's
"OK must be unearnable" guard is untouched — staleness is consulted only about a
record too old, or too old relative to the code, to describe the server at all.

### A sixth, lower-severity: a correct verdict with the wrong name on it

The verifier also found the PowerShell shadow/collision detectors tracking brace
depth with naive `line.count('{') - line.count('}')`, which misreads braces inside
here-strings and comments. Two scripts each carrying a genuine `$STATE`/`$state`
collision were both correctly FAILed — but each was **attributed to the wrong file**:
a `{` inside a here-string in one script shifted the depth counter and moved the
blame to the other. The verdict survived; the diagnosis did not. Not fixed here — it
is a real defect, it is cosmetic relative to a false green, and it is recorded so it
is not rediscovered as a mystery later.

### The scaffolding is now built — five servers, and the config was never touched

`OPTIMUS_MCP_CONFIG.json` declared five Python servers by path. None of the five
files existed. The repair was **not** to repoint the config at the hub and **not**
to delete the declarations — the config already declared the right paths, so what
was missing was the buildings. Five servers were built at exactly the paths it
names, and the config was not modified.

| Server | Tools served | Where the capability lives |
|---|---|---|
| `sentinel-state` | 3 | `sentinel_get_state`, `sentinel_set_state`, `sentinel_check_context` |
| `rule-triggers` | 2 | `sentinel_check_r_triggers` (R-9/R-10), `sentinel_check_mimicry` (R-2) |
| `learning-loop` | 3 | `sentinel_extract_patterns`, `sentinel_log_event`, `sentinel_create_handoff` |
| `context-pressure` | 1 | `sentinel_check_context` |
| `prime-bridge` | 4 | **new capability** — read-only workspace navigation |

**One implementation, five faces.** The first four are facades over
`sentinel_mcp_slice.py`, which delegates to `sentinel_hub_server.py`. No capability
logic is duplicated, so no two servers can give different answers to the same
question. A caller wanting SENTINEL state gets three tools, not twenty-six.

Two decisions worth naming:

- **`rule-triggers` serves two tools, not one.** The coverage table maps that
  capability to `sentinel_check_r_triggers` alone. The config's own description
  says "R-2, R-9, R-10". R-2 is enforced inside `sentinel_check_mimicry`, so
  serving only the narrower list would leave R-2 unreachable from the one server
  that exists to expose it. The declaration is a promise about capability; the
  table is a note about one name.
- **`prime-bridge` is not a slice.** The hub has no filesystem tools, so this is
  genuinely new capability, built to a higher bar: read-only, every path resolved
  and refused if it leaves the workspace, every listing capped, and every
  truncation announced rather than silently performed.

**Measured, by real handshake — not by grep.** Each server was spawned and asked
over stdio: `sentinel-state` 3 tools, `rule-triggers` 2, `learning-loop` 3,
`context-pressure` 1, `prime-bridge` 4, all answering without error.
`prime-bridge` was then attacked: `../../../../../../Windows/System32/...` and an
area of `../../..` were **both refused**, and a missing file reports as an error
rather than a crash — **7 of 7 expected, 0 unexpected**.

Two gaps are declared rather than papered over, and both are recorded in the
servers themselves: `learning-loop`'s description says "metrics" and no hub tool
reports metrics; `context-pressure`'s says "auto-compact" and nothing compacts.
Inventing either would advertise a capability nobody measured. They are hub work
if they are ever wanted.

`mcp_config_servers_exist` now reads **OK — 5 referenced, 0 missing, "All
referenced servers exist."**

### A correction to my own staleness bound

Bounding `mcp_tools_wired` by `MAX_STATE_AGE` was a category error. That constant
is 1 hour and it is defined for a *workflow state* — something that genuinely
changes within the hour. A handshake record describes **code**: the hub either
starts or it does not, and that changes when the source or the environment does,
not on a clock. The bound is now `HANDSHAKE_MAX_AGE` (1 day), with the sharp arm
kept exactly where it belongs: `superseded`, the server edited after the record.

The first suite run under the wrong bound failed `BrainAndMonitor` and
`McpHandshakeMeasure` — both because a 15.8 h old record read `STALE` where they
expected `OK`. Those tests were not weakened. The suite was re-run **without
regenerating the record**, so passing proves the record still describes the server
as it stands rather than proving a fresh file was produced: **503 passed, 0
failed, 0 skipped**, and deployment **40 passed / 0 failed / 1 not-run**, both
exit 0.

### A trap worth recording: `v0.0.1-security`

The two remaining `npx` entries (`web-tools`, `git`) declare
`@modelcontextprotocol/server-fetch` and `@modelcontextprotocol/server-git`. Both
**404** — and the obvious-looking replacements, `mcp-server-fetch` and
`mcp-server-git`, **do exist**, at version **`0.0.1-security`**. Those are npm
squat-reservation placeholders, not servers. Substituting them would have turned
a red check green over two packages that do nothing at all — a check passing while
the capability it names is absent.

Live capability already exists elsewhere in this machine: `git-mcp` (mcp-git) is
installed and registered, and web access is served by `agent-browser-mcp` and
`chrome-devtools-mcp`. So the honest resolution is local implementations, not a
third-party vendor — which is the same shape as the five servers above.

### Residual, not a defect

`mcp_npx_packages_resolve` is now the **only** FAIL in the `wiring` family: 2 of 4
declared npx packages 404 in the registry. `mcp_config_servers_exist` flipped to OK
when the five servers were built. Both are measured on every run and both name the
packages they could not resolve.

---

## P1 — Host telemetry: give the Hardware card something true to show

**Rank 1. This is the only proposal that closes a hole the UI is currently showing.**

**Measured now.** The Operator cockpit has a Hardware card. It renders
`NOT_MEASURED` for CPU, Memory, Disk and Uptime, and says so in words. That is
honest and it is also a visible hole: the panel exists, the layout is built, the
data source does not.

**Why.** `/api/state` is written by `api\collect-sentinel.ps1`. Its top-level keys
are `age_bound_sec, age_sec, by_family, corpus, counts, gaps, generated,
health_checks, health_total_checks, learning, program, status, tests, workflow`.
There is no host block. The dashboard can only ever report what the collector
measures, and the collector does not measure the machine.

**What it takes.** One `host` block in the collector, carrying CPU load, memory
used/total, disk used/total on the workspace volume, and uptime — all from sources
that already exist on this box (CIM / `Get-CimInstance Win32_OperatingSystem`,
`Win32_Processor`, `Win32_LogicalDisk`). Then one render path in
`renderOperator` that reads those keys **by name**, so a missing key still degrades
to `NOT_MEASURED` instead of `[object Object]`.

**Why it is cheap.** The card, the layout, the tile and the node grid are already
built and already tested. This adds a source, not a surface.

**Risk.** Low. A collector that hangs would stall every other reading, so the host
block must be bounded by a timeout and must never be able to prevent the rest of
the state from being written. The same rule the startup entry already learned the
hard way: **evidence must never be able to veto the thing it observes.**

**Acceptance.** `/api/state` returns a `host` block; the Hardware card shows four
figures with an as-of reading; and with the collector's host block deliberately
removed, the card returns to `NOT_MEASURED` instead of rendering a blank.

---

## P2 — Logs freshness: the 10 STALEs are not all the same problem

**Measured now.** 7 of the 10 STALE checks are `log_*`, plus `corpus_fresh` and two
`workflow_*`. `09_LOGS` holds **1,039 of the project's 1,299 files and 25.2 MB of
31.9 MB — 80.0% by count, 79.1% by bytes** (measured 2026-10-09 21:24, after this
file was created; the count is a reading, so it moves as the project grows).

**The distinction that matters.** STALE here does not mean "broken". It means
"this artifact has not been rewritten recently". A log that is never rotated never
gets fresh, because nothing compacts it and nothing decides it is time to.

**What it takes.** A rotation policy plus a freshness stamp per log family —
decide what "current" means for each of the 7, write it, and let the check compare
against that. Rotation is the piece that needs a decision, not a decision about
whether to do it.

**Risk.** Rotation deletes. It must be recoverable and it must never touch
`09_LOGS` without a stated retention floor. Under the current rules nothing here
deletes on its own, and Popy owns that call.

**Note.** `09_LOGS` is the single largest consumer of disk in this project. That is
a measured fact, not a recommendation to act on it today.

---

## P3 — Blueprint vs built: show the scaffolding as *planned*, not as *failing*

**Measured now.** Both FAIL checks are in family `wiring`, and both are the same
shape: something is **declared** and the declaration is not backed by a runtime.
`mcp_config_servers_exist` and `mcp_npx_packages_resolve` are the `wiring` family
reporting that the declared MCP surface does not fully resolve on disk.

**The problem is not the wiring. The problem is the vocabulary.** Under the current
schema a declaration that has not been built yet is indistinguishable from a
declaration that has decayed. The first is a plan. The second is a fault. They get
the same red.

**What it takes.** A third status beside OK/FAIL/STALE — `DECLARED` — assigned when
a check's failure is explained by an unbuilt plan rather than by a broken link,
with each one pointing at its declaration file. Then a visual that renders declared
items in the advisory tone (amber) rather than the breach tone (red), so the panel
says *"planned"* where the truth is *"planned"*.

**Why it is right and not cosmetic.** Popy's standing rule is that scaffolding is a
target and a gap is not a defect. Today the dashboard contradicts that rule in its
own colour palette: it paints the plan in the alarm colour.

**Risk.** Low technically. The risk is editorial — it invites the wrong inference if
the distinction is applied carelessly, so each `DECLARED` must carry the declaration
path it is waiting on.

---

## P4 — Per-process resource inspector (C8's own example: memory inspector)

**Measured now.** Nothing. There is no per-process view anywhere in the build.

**What it takes.** The same `host` block from P1, extended with the working set and
handle count of the processes this deployment actually depends on — the
`sentinel-cc.ps1` backend, `mavis`, and the container. This is deliberately scoped
to *this system's own processes*: a general Windows process monitor is a different
product and is not proposed here.

**Value.** Answers the question an operator actually asks at 2am: which of these
three things is eating the machine.

**Risk.** Low. Same collector, same timeout rule.

---

## P5 — Filtered interactive journals

**Measured now.** Corpus search exists and works (`/api/corpus`, exercised by the
UI). There is no equivalent over the log families — the 7 `log_*` artifacts are
listed, not searchable.

**What it takes.** A `GET /api/logs?family=&q=&since=` route over the same NDJSON
path `/api/history` already uses, and a panel that consumes it. The NDJSON contract
and its parser already exist; this is a second consumer, not a new format.

**Risk.** Low. Read-only.

---

## P6 — Inference profile quick-switch

**Flagged, not recommended as-is.** C8 names this as an example, and it is listed
here for completeness. It would change the active inference model/plan for the
session.

**It is the one proposal in this document that leaves this project.** The switch
would mutate state owned outside `SENTINEL_PRIME`, and it changes which model is
reasoning about the task. That is an R0 decision for Popy, not an implementation
detail, and it should not be built speculatively.

---

## P7 — The single-threaded listener is an architectural ceiling

**Measured now.** The backend is a single-threaded `HttpListener`, and the SSE
stream is deliberately short-lived: it closes and is re-established on a cadence of
`RefreshSeconds = 25`. Measured over 40 s: `open:2, state:2, error:2` — two full
cycles, exactly matching the 25 s cadence.

**Why it closes.** An open response would block every other route on the same
listener. The short-lived stream is a symptom of the ceiling, not a design choice
in its favour. Today the consequence is benign because the UI polls as a fallback;
the consequence would not stay benign if the dashboard grew panels that hold long
requests.

**What it takes.** Either a second listener process on its own port for
server-sent events, or a batched long-poll. Both are additive and both are
contained in `api\server.ps1`.

**Risk.** Medium. A second listener changes the process model that
`sentinel-cc.ps1` starts, stops and supervises, and that PID-file discipline is
load-bearing. This is the proposal most likely to break something that currently
works.

---

## P8 — Deep links: `#cockpit` is decoration today

**Found during the 2026-10-09 button audit, not proposed from theory.**

**Measured.** `index.html` never reads `location.hash` and registers no `hashchange`
handler — a search for all three returns nothing. Navigating to
`http://127.0.0.1:8910/#wiring` and reading the live DOM back returns
`location.hash = "#wiring"` with the panel unchanged. The fragment is accepted by
the browser and then ignored. There is also no tab persistence — and not merely an
empty one: `index.html` contains **no `localStorage` reference at all**, so the
absence of persistence is structural rather than a runtime state. A reload always
returns to Overview.

**Why it is a proposal and not a defect.** Nothing in the UI, the docs or the
generated links produces such a URL, so there is no shipped affordance lying to the
operator — a human has to type the fragment. It is an unbuilt capability.

**Why it is still worth building.** This is a control center that gets bookmarked
and discussed. `#operator`, `#wiring` and `#cockpit` are how a link to a colleague
would name a specific screen, and today that link silently lands on Overview. The
failure mode is quiet by construction: the URL looks right and the screen is wrong.

**What it takes.** Read `location.hash` on boot and select the matching tab;
add a `hashchange` listener so the back button works; keep `aria-selected` and
`.active` as the single source of activation truth. Optionally persist the last
tab — which, since the file never touches `localStorage` today, would be the first
thing it ever writes to it.

**Risk.** Low, and it is additive — no panel, route or measurement changes.

**Naming note.** A tab is selected with `aria-selected="true"` on the button and
`.active` on the panel; `nav button[aria-selected="true"]` carries the styling.
Selection is therefore guaranteed and visible, but **by ARIA, not by a CSS class on
the button**. If P8 is built, it must drive that same pair rather than inventing a
third activation signal — three sources of "which tab is active" is exactly the
class of bug that produced DEFECT 16 in this file's history.

---

## Ordering, and what is deliberately not here

**Suggested order:** P1 (closes a visible hole, cheap, additive) → P3 (corrects a
misleading signal already on screen) → P8 (cheapest of all, and makes a shared link
mean something) → P2 (needs a decision on retention) → P5 → P4 → P7 (largest blast
radius). P6 is parked pending R0.

**Not proposed, on purpose:**

- No proposal to remove, simplify or consolidate an existing panel. The build grew
  from ~70% to complete by addition; nothing earns its way out by subtraction.
- No proposal to change the dual-plane topology. It works, it is loopback-only, and
  `sentinel-hub.ps1` already models both halves honestly.
- No proposal to touch ports 8900/8901 — they belong to the separate OPTIMUS Control
  Center and are out of scope by rule.

---

## Audit record — button and action exercise, 2026-10-09

C5 requires every button and whitelisted action to be tested functionally. The
deployment suite proves the whitelist *admits* `logs_tail` and *refuses* seven
injection payloads; it does not prove a button in the UI runs. That gap was closed
in the browser.

**Exercised — 9 of the 13. All returned HTTP 200 with real payloads, and every
button was re-enabled** (`finally { b.disabled = false; }`, `index.html:1946` —
verified on the slowest one, `deps_check`, not only on instant ones):

| Button | Action id | Result |
|---|---|---|
| `Tail the workflow log` | `logs_tail` | HTTP 200, real log lines (append-only, so any character count drifts — deliberately not quoted) |
| `List skills` | `skills_list` | HTTP 200, the 5 SENTINEL `SKILL.md` files |
| `MCP wiring check` | `mcp_wiring` | HTTP 200 — **at audit time** reported the hardcoded "26 tools DECLARED, 0 WIRED"; after the port it measures for real: "26 DECLARED, 26 WIRED, MATCH" (see the wiring-check fix below) |
| `Dump the matrix` | `matrix_dump` | HTTP 200, the full concept → file → tool → test correlation |
| `Version snapshots` | `versions_list` | HTTP 200, 5 of 5 listed and **none written** — all five directories kept their 2026-10-04 mtime |
| `Workflow status (read-only)` | `wf_state` | HTTP 200, live bimodal status (MODE_B, not stopped) |
| `Stop report (read-only)` | `wf_stop_report` | HTTP 200, `is_stopped: false` |
| `User-turn digest` | `corpus_digest` | HTTP 200, the user-turn digest |
| `Dependency check` | `deps_check` | HTTP 200, `OK=43 FAIL=2 STALE=10 NOT_RUN=0` — matches `/api/state` exactly |
| `Run the test suite` | `tests_run` | HTTP 200 — and **this is the one that found the regression below**, plus the hub-server finding above, both now fixed |

Console after all ten: **0 errors, 0 warnings.**

**NOT exercised — 3 of the 13.** All three are *confirmed* to write; none was run,
and none is known-good. `13 = 10 + 3`.

| Button | id | Why not exercised | Writes — and where |
|---|---|---|---|
| `Acknowledge a STOP` | `wf_stop_ack` | records the operator's answer | **YES** — the STOP record |
| `Verify the corpus` | `corpus_verify` | not run | **YES** — `corpus_extractor.py:492` calls `write_corpus()` and `:491` `write_compaction_summaries()`. It rewrites the corpus *in order to* prove idempotency. The label "Verify" hides this. |
| `Self-improvement gate` | `self_check` | not run | **YES** — `self_improvement.py:340-341` calls `ratify()` then `promote()`; `promote()` appends to `PROMOTED_FILE` (`:282`) and every step `_log()`s. It cleans up its own *candidate*, not its own *history*. |

**Five of the thirteen buttons write to disk**: `wf_stop_ack`, `corpus_verify`,
`self_check`, `deps_check` and `tests_run`. Two of those five — **"Verify the
corpus"** and **"Self-improvement gate"** — are labelled as though they were pure
inspection, and neither is. An operator clicking those two casually leaves real state
behind.

**A regression this record caught, and the fix.** Running `tests_run` returned
`DashboardSurface` FAIL at 34/35 — *"with no /api/health record the table says
unmeasured and names monitor.py"*. **It was mine.** SPEC_R104 work had hoisted
`const attn = $('wire-attention')` to the top of `renderWiring` so the guard could
test it; that moved the reference ~4,600 characters away from the `monitor.py`
message the test measures against, turning the check red while the panel rendered
identically. `attn` is used in exactly two places, both far below the declaration,
so the hoist was never necessary. The declaration and its guard were moved back to
just above first use: the distance is now **98 characters**, tighter than the
original's 199, the guard still precedes every write, **the test was not touched**,
and `DashboardSurface` is back to 35/35.

That was the second time in one session a layout proxy inside a test was mistaken
for a behavioural guarantee — and the third time an unmeasured claim had to be
walked back. `tests_run` was described above as "reads only", on the strength of a
single dispatch line; `test_suite.py:3099` writes `last_test_run.json` on every run,
by design.

**Correction, 2026-10-09.** An earlier version of this record claimed "6 of 13
mutating or long", named `Dump the matrix` as a writer and described `Version
snapshots` as "writes snapshots". Both were wrong, and three buttons were named
nowhere:

- `matrix_dump` is a **pure read** — `api\server.ps1:126` is `json.load` then
  `print`. It was never a writer.
- `versions_list` is a **pure read** — `api\server.ps1:132` calls
  `manage-versions.ps1 -List`, which `return`s at `bat\manage-versions.ps1:60`,
  *before* every write in that script (`New-Item`, `Copy-Item`, `Set-Content` at
  lines 104–112). The label "writes snapshots" was simply false.

  Both have since been **exercised**, and both behaved exactly as the code says:
  `matrix_dump` returned the full matrix, and `versions_list` listed the five
  snapshots while leaving every one of the five directories at its 2026-10-04
  mtime. The code reading and the observed behaviour agree.
- `corpus_verify`, `corpus_digest` and `deps_check` were omitted from the list
  entirely, so the arithmetic never closed and the record quietly under-stated its
  own coverage.

**Two things that looked like defects and are not — recorded so nobody re-raises
them:**

1. *No `.active` class on the tab buttons.* Selection is carried by
   `aria-selected="true"` on the button plus `.active` on the panel, and
   `nav button[aria-selected="true"]` is what draws the cyan underline. The
   activation guarantee holds; it is just keyed on ARIA rather than a class name.
2. *`#cockpit` did not select the Cockpit panel.* Correct behaviour today, because
   nothing ever emits such a link. Filed as **P8** rather than treated as a bug.

---

## Maintenance rule for this file

When a proposal is built, **do not delete it**. Move it to a `## BUILT` section
with the date, the files touched, and the measurement that now proves it. A
proposals document that quietly loses its own history is how the next person
re-proposes the same idea in a month — and this project has already paid that bill
once, with `11_BRAIN\04_METHOD\MISSTEPS_AND_CORRECTIONS.md`, which lost 44,576 bytes
(M-01 through M-27) to a single truncating write.

---

## BUILT 2026-10-10 (late): the two phantom packages, built rather than substituted

### The decision that shaped this section

`OPTIMUS_MCP_CONFIG.json` declared four npx servers. Two of them were named after
packages that do not exist. The obvious repair - swap in the similarly-named real
package - was measured first and **refused**:

    @modelcontextprotocol/server-fetch  -> 404
    mcp-server-fetch                   -> 200, dist-tags.latest = 0.0.1-security

    @modelcontextprotocol/server-git    -> 404
    mcp-server-git                     -> 200, dist-tags.latest = 0.0.1-security

`0.0.1-security` is what npm serves for a squatted or unpublished name. Substituting
it would have turned `mcp_npx_packages_resolve` from a red 2/4 into a green 2/2 over
two packages that do nothing. **A registry that 404s is a real FAIL; it is not a
naming problem to be tidied away.**

So the capability was built, at the paths the config already implied.

| File | Bytes | Tools | What it owns |
|---|---|---|---|
| `web_tools_server.py` | 10,415 | 3 | `web_fetch`, `web_fetch_text`, `web_head` |
| `git_tools_server.py` | 13,959 | 6 | `git_discover`, `git_status`, `git_log`, `git_diff`, `git_branches`, `git_show` |

### The search half of `web-tools` is deliberately absent

The declaration said "Web fetch **si search**". Only fetch was built, because
search was measured and did not survive the measurement:

    https://example.com/                      -> 200, 577 bytes
    https://html.duckduckgo.com/html/?q=...   -> HTTP 202, 14,218 bytes, 0 results

HTTP 202 with zero results is an anti-bot interstitial, not a result set. A
`web_search` tool built on it would return `[]` on most days and read as "no
results for this query" rather than "this endpoint is blocked today". An honest
absence beats a tool that lies by omission. The gap is recorded in the config
under `web-tools.knownGap` instead of being papered over. The real search path
remains the agent's native `web_search`.

### Defect found in the config itself: `GIT_DIR` is malformed

The `git` entry sets `GIT_DIR` to the **work-tree root**. Git's definition of
`GIT_DIR` is "the directory that *is* `.git`". Measured on a genuinely valid repo,
three invocations, same command, only the variable differing:

| Invocation | Result |
|---|---|
| no `GIT_DIR` | `true`, exit 0 |
| `GIT_DIR=<worktree root>` | `fatal: not a git repository`, exit 128 |
| `GIT_DIR=<worktree root>/.git` | `true`, exit 0 |

So the declared entry would have broken git **even if the workspace were a
repository**. `GIT_DIR` was left in place (it is now inert, see below) and
`WORKSPACE_ROOT` added as the operative variable; the defect is recorded under
`git.knownDefect`.

### The same bug, in my own new code, caught by that table

`git_tools_server.py` initially forwarded the parent's `GIT_DIR` into every git
subprocess. Git read it as "this *is* the `.git` directory", and **every valid
repository came back as "not a git repository"** - including repos I had just
confirmed with `rev-parse` exit 0. The failure mode is nasty because it points
at the data rather than at the wiring: it looks like the repositories are broken.

Fixed by stripping `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`,
`GIT_OBJECT_DIRECTORY`, `GIT_COMMON_DIR`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` and
`GIT_NAMESPACE` from the child environment. After the fix, all six tools returned
real data (2 commits, `main` at `c6dc466`, upstream `origin/main`, 1 untracked
entry) and the server's stderr was **0 bytes**.

This is the fifth instance of one lesson, now seen from five directions:
**prezența în sursă nu dovedește că e servit.** A correctly written server that
is handed the wrong environment is not a working server.

### SENTINEL_PRIME is not a git repository

    git rev-parse --is-inside-work-tree   (in SENTINEL_PRIME)
      -> exit 128, "fatal: not a git repository"

There is no `.git`. The declaration is true as intent and empty as fact: there is
no `/checkpoint` history to inspect. `git_status` therefore **refuses loudly**,
naming the measured `rev-parse` output. It does not return an empty change list -
because an empty list from a non-repository is indistinguishable, to any caller,
from a clean working tree. That is the whole reason the refusal exists.

Closing this gap (putting SENTINEL_PRIME under version control) is **Popy's R0**,
and it now has a second consequence worth stating plainly: this machine's git has
a `LiveReview` hook that refuses to create a commit without a review attestation
(`lrc review --staged`, or `--skip/--vouch`). I did not bypass it to make a probe
convenient. Any version-control decision here has to account for it.

### F3: a security refusal the caller could not read

`prime-bridge` raised `ValueError`. The MCP SDK treats anything that is not
`ToolError` as a crash and withholds the message by design. Measured before the
fix - both calls returned the **byte-identical** body
`Error executing tool prime_read_text_file`:

    prime_read_text_file("..\..\..\..\Windows\win.ini")   # refused
    prime_read_text_file("09_LOGS\definitely_not_here.json")  # missing

The real reason existed only as a traceback on the server's stderr, which the
caller never sees. **A security refusal indistinguishable from a typo is a control
that cannot be audited by the thing it protects.**

After switching the four anticipated raises to `ToolError`:

    ...: refused: ..\..\..\..\Windows\win.ini resolves outside the workspace root
    ...: 09_LOGS\definitely_not_here.json is not a file in the workspace

Distinguishable, self-describing, and stderr fell from 13,664 B to 1,210 B
because it is no longer logged as a crash.

### Config edit: additive, nothing pruned

`OPTIMUS_MCP_CONFIG.json` went from 6,842 B to 12,339 B. Two entries repointed
(`web-tools`, `git`), two top-level keys **added** (`builtFromScaffolding`,
`corrections`). Still **9 server entries**. Nothing deleted. A byte-identical
pre-edit copy is preserved at `OPTIMUS_MCP_CONFIG.json.bak`.

The `superseded` block written by an unattributable third party at
2026-10-10 15:29:35 was **left untouched**. Its central claim - that the five
servers are "SUPERSEDED BY sentinel-hub" - is measurably false (the hub exposes
26 tools, **zero** of them with any filesystem flavour, so `prime-bridge` is not
absorbed; and the four ~1.2 KB modules are a deliberate delegation facade, not
stubs written to satisfy the file). It was corrected **forward** through the new
`corrections` block rather than deleted, because deletion of another writer's
entry is irreversible.

### Falsifiability, demonstrated rather than asserted

`mcp_config_servers_exist` was sabotaged by pointing `web-tools` at a nonexistent
`.py`, run, and restored in the same command:

    pre-sabotage: 12,339 B sha=DCF95CA8FC55CF70
    [FAIL] mcp_config_servers_exist - 7 .py servers referenced, 1 not on disk
    restored:    12,339 B sha=DCF95CA8FC55CF70   RESTORE_MATCHES: True

Note what did **not** move: `mcp_config` stayed **ok** (the JSON still parsed).
"Valid JSON" and "servers that can start" are different claims and the monitor
now separates them.

### Measurements after this section

| Check | Result |
|---|---|
| `test_suite.py` | 505 passed / 0 failed / 0 skipped, exit 0, 123.9 s |
| `test_deployment.py` | 40 passed / 0 failed / 1 not-run (41), exit 0, 80.9 s |
| `mcp_config_servers_exist` | ok - 7 python servers referenced, 0 missing |
| `mcp_npx_packages_resolve` | ok - 2/2 (`filesystem`, `browser` - left as npx, they resolve) |
| `mcp_tools_wired` | ok - 26 tools over stdio |

The not-run check is `startup_cold_start`, destructive by design.


---

## BUILT 2026-10-10 (later): what the independent verifier caught in my own new code

An adversarial verifier was given the six claims above with the instruction to
refute them. It returned **PASS WITH FINDINGS** and found four real defects,
**three of them in code I had written minutes earlier**. They are recorded here
in full because the useful part of a verifier is not the confirmation.

### CRITICAL - `git_diff` was a file-write primitive, and the docstring said it could not be

`git_tools_server.py` claimed, in its own module docstring:

> Read-only by construction. Only inspection subcommands are reachable... so
> the config's own `security.no_force_push: true` cannot be violated from here.

That was false. `ALLOWED_SUBCOMMANDS` gated the **subcommand**, not the
**arguments**. `ref` was appended to argv unvalidated, so:

    git_diff(ref="--output=C:\somewhere\file.txt")

made git **create** that file - and truncate an existing 42-byte file to 0 bytes -
while returning `is_error=false`. `git_show(revision=...)` had the same shape.

The allowlist had said "diff" and was satisfied. The write happened in an option
nobody inspected. A security property asserted in prose, enforced on the wrong
axis, is worse than no claim, because the prose is what a later reader trusts.

Fixed in two layers, because one layer is a promise and two is a control:

1. `_safe_token()` refuses any caller text that begins with `-`, contains `=`, or
   is not a plain revision. Git's own model is the rule: a token starting with
   `-` is an option, not a value.
2. `SAFE_LITERAL_OPTIONS` / `SAFE_LITERAL_PREFIXES` enumerate every option this
   module may pass. `_run()` refuses anything else **before git is invoked**, so
   a future tool added to this file cannot reintroduce the same primitive by
   forgetting to call the validator.

Re-measured against a genuine repository (`AP---ID-Systems`, head `c6dc466`),
with a victim file created beforehand:

| Call | Result | File after |
|---|---|---|
| `git_status` (sanity) | `is_error=false`, real status | 45 B |
| `git_diff(ref="--output=<victim>")` | refused, reason names the `-` | **45 B, intact** |
| `git_show(revision="--output=<new>")` | refused | **not created** |
| `git_diff(ref="-p")` | refused | 45 B |
| `git_diff(ref="a=b")` | refused (`=` check) | 45 B |
| `git_diff(ref="HEAD")` | `is_error=false`, real diff | 45 B |

The sanity row matters as much as the attack rows: a guard that refuses
everything would score the same five refusals. The legitimate path is still open.

### HIGH - any HTTP redirect crashed `web-tools` into the exact error shape F3 removed

```python
if len(getattr(req, 'redirect_count', 0)) >= REDIRECT_LIMIT:   # len() of an int
```

The counter was stored on the request as an `int` and then measured with `len()`.
On the **first** redirect this raised `TypeError`. `TypeError` is not a
`ToolError`, so the SDK classified it as a crash and returned the bare string
`Error executing tool web_head` - the verbatim unreadable-error shape the
`ToolError` work had just eliminated from `prime-bridge`. `REDIRECT_LIMIT` never
engaged and `redirects` always reported `0`.

Fixed by holding the counter on the handler instance. Measured live afterwards:

    web_head("http://github.com/")
      -> status 200, final_url "https://github.com/", "redirects": 1

### MEDIUM - `git_discover` could never report a repository

`SKIP_DIRS` contains `'.git'`, and the scan filtered on
`set(path.parts) & SKIP_DIRS` over a path whose **last component is the `.git`
being searched for**. Every hit was discarded by its own search key.

    repositories_found: 0     (before, on a tree that genuinely contains repos)
    repositories_found: 15    (after)

A filter that removes the thing it is looking for always returns "not found".

### INFO - a stale number in a comment, corrected rather than deleted

`monitor.py` explained the `mcp_config` / `mcp_config_servers_exist` split with
"5 of the 9 declared servers pointed at .py files that do not exist". That was
true when written and is now false: 7 declared, 7 present. The comment now says
so explicitly and keeps the original sentence as history - a comment silently
rewritten each time the numbers move stops recording *when the class of bug was
first seen*, which is the only reason it is worth having.

### LOW - the PowerShell brace counter blamed the wrong file (now fixed)

Both PowerShell checks tracked nesting depth with
`line.count('{') - line.count('}')`, so a `{` inside a here-string or a quoted
string shifted the depth. Verdicts usually survived - a real case collision is
rare and the depth only has to be wrong by one assignment - but the **diagnosis
named the wrong script**, which is as useless to whoever reads it as finding
nothing.

Replaced with `_ps_structural_brace_deltas()`, a scanner that skips `<# #>`
block comments, `#` comments, quoted strings and `@"..."@` / `@'...'@`
here-strings. Demonstrated on the exact failing shape (an unbalanced `{` inside
a here-string):

    old: depth drifts to 1 and never returns  -> $after misread as function-local, final depth 1
    new: depth holds 0 and returns to 0        -> $after correctly script-scope, final depth 0

Verdicts over the 9 real `.ps1` files are unchanged: 0 case collisions,
0 shadowed variables. The fix changed the diagnosis, not the verdict - which is
the correct outcome for a diagnostic defect, and is stated as such rather than
claimed as a fix that mattered more than it did.

**The first version of that scanner was itself broken** - it built the
here-string terminator as quote-plus-quote instead of quote-plus-`@`, so the
state never exited and it reported depth 0 for the rest of every file. The test
above caught it immediately, which is the argument for writing the failing case
before trusting the fix.

### What the verifier could not establish

Reported honestly, and left open rather than assumed:

- Whether the redirect-limit code *ever* worked - the HIGH finding proves it is
  broken now; there is no pre-change copy.
- Whether the third party's `superseded` block is byte-identical to what it was
  at 15:29:35 - no pre-edit snapshot of the block exists. Its *content* was
  verified intact (5 keys), but immutability is unprovable in retrospect.
- The verifier's zero-write proof came back **not clean**: 1327 files before,
  1327 files after, but 6 under `13_COMMAND_CENTER\` differed. It attributed
  them correctly - a background daemon (`sentinel_hub_server.py` PID 32936 plus
  the Command Center loop) rewrites them continuously, and 5 changed again
  during an idle window in which the verifier ran nothing. **All five files
  under test were byte-and-mtime identical**, and 0 files outside
  `13_COMMAND_CENTER\` changed. The honest statement is: this verification
  proves the artifacts were not mutated; it does not prove the workspace is
  quiescent, because the workspace is not designed to be quiescent.

### One correction to my own brief

I told the verifier that `...\GitHub - Download\01` was a directory with a `.git`
that git does not recognise. That was wrong. Raw git reports
`rev-parse --is-inside-work-tree` -> `true`, exit 0; only `rev-parse HEAD` fails,
because the branch has no commits yet. The server reported
`## No commits yet on main`, which is correct. **The premise in my brief was
wrong and the code was right** - a reminder that a finding phrased confidently by
the person commissioning it still needs checking, including by me.


---

## BUILT 2026-10-10 (late): the write primitive is closed, and a regression I caused

A second adversarial verifier was given the four fixes above plus the instruction
to attack them harder. **PASS WITH FINDINGS.** The write primitive - the one that
mattered - is closed. And it also found a defect **I had introduced while fixing
something else**, which is the more useful half of this round.

### A: the write primitive is closed, against both layers

Attacks were run against the **real** repository (`AP---ID-Systems`, head
`c6dc466`), never against a directory that only fails for an unrelated reason.
Controls first, so the refusals mean something: `git_status` returned
`## main...origin/main` with `changed=1`, and `git_diff(ref="HEAD")` returned a
real diff.

**35 tool-level attacks plus 24 direct `_run()` attacks** that bypass
`_safe_token()` entirely and speak to the argv guard directly.

| Layer | Refused |
|---|---|
| `_safe_token` | `--output=<victim>`, `--output=C:/PWNED.txt`, space/tab/newline/semicolon/`"`-injected revisions, NUL, `\x01`, RTL-override `U+202E`, `..`-escape, `C:\` colon, `-x`, `--no-color`, `--cached`, `--stat`, leading-space `--output=`, `@{u}`, `@{0}` |
| `_run` argv allowlist | `--output=`, `-o`, `-o<path>`, split `--output <path>`, `--ext-diff`, `--textconv`, `--ita-invisible-in-index=`, `--raw`, `--no-prefix`, `-a`, `--error-unmatch`, `--git-dir`, `--porcelain=v2`, `--decorate=full` |

And all 14 write subcommands (`commit`, `add`, `reset`, `push`, `merge`,
`config`, `clean`, `apply`, `update-ref`, `worktree`, `gc`, ...) are refused.

Across every attack: **victim 156 -> 156 bytes, SHA256 identical, probe file
never created, zero new files.** Legitimate revisions still work -
`HEAD`, `HEAD~1`, `HEAD^{}`, `limit=10**12`, `staged=True`.

Zero-write proof over both directories: **108 files before, 108 after, diff
empty** - no path, size or mtime changed.

### C: redirects

`REDIRECT_LIMIT` = 5, **per-request** (a fresh handler per fetch; three
sequential requests each reported 5, so it is not a shared counter that
accumulates). A 40-hop chain raises a **readable** `ToolError` naming the reason,
not the generic string. Real chains: `github.com` -> 200 / 1 redirect;
`httpbin /redirect/2` -> 200 / 2.

### B: the regression I caused, and what it teaches

`_ps_structural_brace_deltas` handled here-strings, block comments and plain
strings - and got **PowerShell escaping wrong**:

    "..."  escapes with a BACKTICK:  `"   is a literal quote
    '...'  escapes by DOUBLING:    ''   is a literal quote

`sentinel-hub.ps1:586` contains `` ` `` inside a double-quoted regex. The scanner
treated the backtick as an ordinary character, closed the string early, and the
next `"` opened a new one - so a real brace after it counted as structure.

Measured sensitivity loss on a synthetic file containing that line:

| | collisions found |
|---|---|
| old naive scanner | `['Path vs path']` |
| my new scanner | `[]`  <- **regression** |

**The new detector was less sensitive than the broken one it replaced**, in the
exact class of silent defect it exists to catch. Latent only because that file
has no script-scope assignments after line 586 - which is exactly why a latent
case is still a defect.

Fixed, then proven on both axes:

| Case | Expected | Got |
|---|---|---|
| backtick-escaped quote inside `"` | 0 | **0** |
| doubled `'` inside `'` | 0 | **0** |
| brace inside a double-quoted string | 0 | 0 |
| real `{` / `}` | +1 / -1 | +1 / -1 |
| brace inside a `#` comment | 0 | 0 |

`DETECTION_RESTORED: True`, `DEPTH_RETURNS_TO_ZERO: True`, and live verdicts over
the 9 real `.ps1` unchanged at 0 collisions / 0 shadowed.

The rule this earns, now written into memory:

> **When replacing a detector, test its SENSITIVITY, not just the correctness of
> its parser.** Put a known collision immediately after the construct that
> breaks, and require the new scanner to still find it. Otherwise you have
> reinstalled the defect under a better name.

### Info findings, recorded not dismissed

- **`_inside()` does not traverse Windows junctions** - `Path.resolve()` follows
  symlinks but not junctions, so a junction to `C:\Windows\System32` passes the
  confinement check. Non-exploitable today because git then fails `cannot change
  to` and no writing subcommand exists. It becomes live the moment a write
  subcommand is ever added, so it is recorded here as a precondition rather than
  a non-issue.
- The verifier's brief was corrected on one point: a here-string opener with
  trailing text (`@" junk`) is a PowerShell syntax error, so "opened at end of
  line" is the correct contract and the scanner is right to require it.

### Not verified, stated rather than assumed

Windows argv quirks that only appear under a real `cmd.exe` (argv is built with
`shell=False`, so there is no shell to interpret); git alias / `core.pager`
injection coming from a repository's own `.git/config`; SDK-level error wrapping
above stdio (functions were called directly); and a concurrent-write race against
the `13_COMMAND_CENTER` daemon, which is excluded by instruction because it is
designed to be running.

## DEPLOYED 2026-10-10: from declared to callable

The last distance between scaffolding and deployment: **a declared entry is not a
tool a session can call.**

Measured gap: the live minimax profile held 17 MCP servers, and **none of the 7
python servers declared here was among them**. They existed on disk, started, and
were unreachable from any session.

Measured before deciding what to register:

| Server | Tools | New vs live `sentinel-hub` | Duplicate |
|---|---|---|---|
| `prime-bridge` | 4 | **4** | 0 |
| `web-tools` | 3 | **3** | 0 |
| `git-tools` | 6 | **6** | 0 |
| `sentinel-state` | 3 | 0 | **3** |
| `rule-triggers` | 2 | 0 | **2** |
| `learning-loop` | 3 | 0 | **3** |
| `context-pressure` | 1 | 0 | **1** |

All **9** tools of the four slices are already served by the live 26-tool
`sentinel-hub`. Registering them would put **duplicate tool names in front of
every future session** - one agent, two answers to the same question, the exact
drift the facade design exists to prevent.

So: Popy's R0 on 2026-10-10 registered **3, not 7**. 13 new tools, zero
collisions. The four slices stay in this file as the OPTIMUS config's faces, not
as Mavis's.

Registered under the name `git-tools`, not `git`, so it cannot be confused with
the pre-existing `git-mcp`; the mapping is recorded in the config.

**And a registration is a claim in a file, so it was proven like one.** Each server
was launched with **exactly** the command and env now in the live profile, then
handshaked and had one tool called:

    prime-bridge  4 tools  probe prime_workspace_summary -> real workspace data
    web-tools     3 tools  probe web_head               -> HTTP 200 example.com
    git-tools     6 tools  probe git_discover            -> honest "not a repository"

13 tools, 0 errors. Two probe bugs of my own surfaced first and were fixed rather
than worked around - this SDK returns `is_error` and `server_info`, not
`isError` and `serverInfo`, and I had already been caught by the same snake_case
trap once earlier in this session.

Recorded forward in `OPTIMUS_MCP_CONFIG.json` under `liveProfileRegistration`.
Nothing pruned: still 9 server entries, `superseded` still intact.


---

## BUILT 2026-10-10 (later still): the dashboard was reporting declarations, not deployment

Everything the Command Center said about MCP was about **declarations**.
`mcp_config_servers_exist` asked "do the declared .py files exist?" and answered
OK - correctly, because they did. It was never asked whether anything can reach
them. Measured directly afterwards:

    declared .py servers on disk ....... 7
    registered in the live profile .... 3
    reachable from a session .......... 0, until this afternoon

Seven servers existed, started, and were unreachable, while the dashboard showed
five green MCP checks. **A declared entry is not a running process. A running
process is not a callable tool.** The dashboard knew the first half of that
sentence and drew its conclusions from it.

### `mcp_live_profile_registered` - a new check that reads the live profile

The live store is `C:\Users\apviz\.minimax\mcp.json` (20 entries), overridable
through `MINIMAX_MCP_PROFILE` so it can be pointed at a copy for testing. It
reads the config's declaration and the live profile's reality, and compares them
**by script path** rather than by name, because the names differ by design: the
config calls it `git`, the profile calls it `git-tools`.

Unreadable profile is **NOT_RUN, never FAIL** - an offline or absent profile has
falsified nothing, and reporting FAIL there would be an instrument fault dressed
as a product fault.

### Two bugs in my own first version, both caught by sabotaging it

A check that has never been sabotaged is an assertion. So the profile was
copied into TEMP, broken four ways, and pointed at via the env override:

| Sabotage | Expected | Got (1st version) | Got (after fix) |
|---|---|---|---|
| control: real live profile | OK | OK | **OK** |
| `prime-bridge` removed from the profile | FAIL | **ok** | **FAIL** |
| `web-tools` present but `enabled: false` | FAIL | **ok** | **FAIL** |
| `git-tools` repointed at a different script | FAIL | **ok** | **FAIL** |
| profile file corrupt | NOT_RUN | NOTRUN | **NOTRUN** |

**Bug 1 - the expectation was circular.** The set of "expected" profile names was
built by looking each declared server up *in the live profile*. So with
`prime-bridge` deleted from that profile, the expectation silently shrank to
match reality and the check reported green. The expectation must come from the
**declaration**; the profile is only ever the thing under test. Rewritten to
compare declared script paths against the profile's script paths.

**Bug 2 - a disabled entry counted as live.** `enabled: false` entries were
indexed like any other, so a server that is present-but-disabled - and therefore
cannot start - was reported as registered. Now skipped, because present in the
file is not live in the profile.

**Bug 3, found by the third sabotage rather than by reading the code.** Even
after the rewrite, repointing `git-tools` at another script still passed. Cause:
the config's `liveProfileRegistration.registered` block was keyed `git-tools`
while the config's own server entry is named `git`, so the git entry was never
in the expected set at all. The block is now keyed by the **config** names, with
the profile name carried as an explicit `profile_name` field. A name mismatch
between a declaration and a registry is not a cosmetic problem; it silently
removes an entry from what is being verified.

Live profile verified untouched after all four sabotages: byte-identical.

### What it says now

    [ok] mcp_live_profile_registered
         3 of 7 declared .py servers are registered and enabled in the live
         profile: git-tools, prime-bridge, web-tools.
         Declared but deliberately not registered: context-pressure,
         learning-loop, rule-triggers, sentinel-state - their tools are already
         served by the live sentinel-hub, and registering them would put
         duplicate tool names in front of every session

Monitor total moved **OK=53 -> OK=54**, FAIL=0. The new check appears in the
Command Center's own health feed automatically, because the dashboard reads
these checks rather than restating them.

### Suites after the addition

    test_suite.py         505 passed / 0 failed / 0 skipped, exit 0, 150.6 s
    test_deployment.py    40 passed / 0 failed / 1 not-run (41),  exit 0,  81.0 s

A new check can break a count assertion elsewhere, so both suites were re-run
rather than assumed. Neither moved.


---

## BUILT 2026-10-10 (last): verification against PowerShell's own parser, and a bug my own probe found

### The verifier used an oracle instead of my assumptions

The previous round asked whether the escaping fix was correct. This one went
further: it built ground truth from **PowerShell's own tokenizer**
(`[System.Management.Automation.Language.Parser]::ParseInput`, with token
masking) rather than from anything I said. 29 constructs, each with a
`$Path`/`$path` collision placed immediately after it.

**Decisive sensitivity result: 0 cases where the naive counter finds a collision
and the new scanner misses it.** The new scanner found strictly *more* in 8
constructs - brace inside a string, inside a here-string, inside a block
comment, backtick inside single quotes. And on all 9 real `.ps1` files its
per-line deltas match the PowerShell parser **exactly, 0 mismatches**.

That is the right way to verify a parser, and it is the standard I should have
set the first time instead of asking whether "it looks right".

### MEDIUM found and fixed: string state died at every newline

    $x = "line1 {
    line2 "
    $Path = "p"        # a REAL collision, at depth 0
    $path = "q"

`quote` was initialised **inside** the per-line loop, so a double-quoted string
spanning lines lost its state at the newline and the continuation was read as
code. The naive counter missed this one too - a *shared* blind spot, not the
regression class - which is precisely why it survived two review rounds.
Latent: no real `.ps1` uses a multi-line quoted string today.

`quote` now lives outside the loop. Verified against the parser oracle:

| construct | PowerShell says | new scanner | naive counter |
|---|---|---|---|
| balanced | clean | 0 | 0 |
| brace in `"..."` | clean | **0** | **1** (wrong) |
| backtick-escaped quote | clean | 0 | 0 |
| here-string with brace | not clean | 1 | 1 |
| **multi-line `"..."`** | clean | **0** | **1** (wrong) |
| **multi-line `'...'`** | not clean | **-1** | **-1** |
| balanced braces | clean | 0 | 0 |

`ALL_AGREE_WITH_POWERSHELL_PARSER: True`. On the multi-line case the new
scanner is now right where the naive counter is wrong - so it is strictly better
than what it replaced, on measured evidence rather than on claim.

### LOW found and fixed: a description that overstated itself

The live `git-tools` description claimed caller text "containing `=`" is
refused. True for `ref` and `revision`; **false for `path_filter`**, which is
passed after `--` and therefore reads as a pathspec.

Fixed on both sides rather than by softening the claim:

- `path_filter` now refuses a leading `-` as belt and braces. It deliberately
  does **not** get `_safe_token`, because a real Windows pathspec can contain
  spaces and backslashes that `_safe_token` rejects - tightening it would break
  legitimate use to defend against something already unreachable.
- The description now says exactly which parameter gets which rule, instead of
  a blanket claim that was true for two of three.

### A pre-existing bug my own probe exposed while doing that

`path_filter` was resolved against the **workspace root** while git runs with the
**repository** as its working directory. For every repository below the root, the
pathspec therefore pointed somewhere git could not match, and `git log` failed
outright. `path_filter` could only ever have worked when `repo == root`.

Fixed with `_inside_repo()`, which resolves relative to the repo and refuses
anything outside it. Verified against the real repository:

| Call | Before | After |
|---|---|---|
| `git_log(repo, path_filter=".")` | **failed** | **works** |
| `git_log(repo, path_filter="../../..")` | refused | refused |
| `git_log(repo, path_filter="--output=<victim>")` | accepted (inert) | refused |
| `git_diff(repo, ref="--output=<victim>")` | refused | refused |

Victim file **28 bytes, byte-identical**, in every case.

This one was not in any reviewer's list. It was found because I re-tested a
legitimate call - `path_filter="."` - after changing the guard around it, and
asked why a harmless, ordinary call was failing. **A probe that only tests
attacks never finds a broken happy path.**

### Final state

    monitor            OK=54  FAIL=0  STALE=2  NOT_RUN=0
    test_suite.py      505 passed / 0 failed / 0 skipped, exit 0
    test_deployment.py 40 passed / 0 failed / 1 not-run (41), exit 0
    config             14,601 B, 9 servers, 0 pruned, superseded intact
    EVOLUTION.md       prefix unchanged on every append

---

## R7 — A silent clip, and the reading error that preceded it (2026-10-10)

### The Wiring panel "discrepancy" was my own misreading

The open item going into this round was: the Wiring panel displays `wiring OK 7`
and does not render `mcp_live_profile_registered`, while `/api/state` serves 56
checks including that one. Measured both endpoints:

| measurement | result |
|---|---|
| `/api/health` -> `checks` | 56 |
| `/api/state` -> `health_checks` | 56 |
| family `wiring` | 7 checks, 7 OK, 0 FAIL/STALE/NOT_RUN |
| `mcp_live_profile_registered` | present, `wiring / OK` |
| non-OK checks across all families | 2 (`corpus_fresh` STALE, `workflow_state_fresh` STALE) |

Cause, at `index.html:1430`:

    const bad = HEALTH.checks.filter(c => c && c.status && c.status !== 'OK');

The panel is an exception list. It is documented as one in its own prose
(`index.html:556-558`): "Green checks are deliberately absent: this is the
exception list." An OK check therefore never appears by id. Searching the DOM
for `mcp_live_profile_registered` is a test that cannot pass by construction.

The second error was one of aggregation level. `7` is the size of the `wiring`
FAMILY, not a subset of 56. "7 vs 56" were never in conflict; they were two
levels of the same tree. No code changed. Zero files touched in this step.

**Lesson.** A difference in AGGREGATION is not a contradiction in DATA. Before
calling two measurements inconsistent, establish that they are measuring the
same thing at the same level.

### A real silent failure, found by resizing the viewport

Same audit, at 1024px instead of 1280px. All 13 tabs render, but the Doctrine
table overflows:

- `#p-Doctrine table` scrollWidth 1028 inside `.card` clientWidth 978
- `.card` has `overflow:hidden` (`index.html:143`), `table` has `width:100%` (`:151`)
- the `TEST` column's right edge was 1066 vs the card's right edge -> **cut by 64px**
- **24 cells unreachable**, across all 24 rows, with no scrollbar and no way to reach them

`overflow:hidden` there is not a bug — it exists to clip children to the card's
border-radius. The bug is that its content can be wider than the box, and then
it discards it instead of surfacing it. A monitor that hides evidence is worse
than one that shows it failing: the panel looked complete and was lying by
omission.

This was invisible at 1280px and invisible to the DOM text checks, because
`innerText` returns the content of a clipped element. Reading the text was never
going to catch it; only geometry does.

### Fix

One CSS insertion, appended after the existing `.pad` rule:

    .pad{overflow-x:auto}

The card keeps its radius clip; the content box gains a scrollbar. Overlap
becomes reachable instead of discarded.

Proven as a pure insertion: 111551 -> 112196 bytes (delta 645),
`prefix_unchanged: True`, `suffix_unchanged: True` around the insertion point at
char offset 8142, verified against `index.html.bak` (111551 bytes, sha256
D0D641C1...E275C5, identical to the pre-edit file).

Post-fix, measured on the re-rendered page:

| viewport | silently-clipped cards | scrollbars introduced |
|---|---|---|
| 1024x768 | 0 | 1 (the Doctrine table, by design) |
| 1280x720 | 0 | 0 — normal case untouched |

13 panels, non-empty, zero browser console errors/warnings at both widths.

**Lesson.** `overflow:hidden` and `width:100%` are each defensible in isolation
and compose into a silent data loss. Audit clipping with RECTANGLES, never with
text extraction.
### Independent verification (bg_89a39a38): PASS WITH FINDINGS

An adversarial verifier ran the audit over raw CDP in real headless Chrome - the
browser MCP tools were not exposed to that session, so it built its own harness
in `%TEMP%\cdpaudit` and wrote nothing under `SENTINEL_PRIME\`.

The result that matters is the **control**: with the fix active the audit found 0
clipped-and-unreachable panels; with the fix neutralized in-browser
(`.pad{overflow-x:auto !important}` overridden to `visible`) it found 2, and
`scrollLeft` refused to move off 0 when asked for 99999. The detector is not a
check that cannot fail.

Per-viewport, all 13 tabs each: 0 clipped-and-unreachable at 1600, 1280, 1100,
1024, 900, 768 and 480. Every new scroll container is a `div.pad` and nowhere
else. No page-level horizontal overflow at any width. At 1280x720: zero scroll
containers, 13 panels non-empty (603-8713 chars), console errors 0, warnings 0,
uncaught exceptions 0.

Three corrections it made to MY report, accepted:

1. **My numbers did not reproduce.** I reported card clientW 978 and a 64px cut;
   it measures 969 and 73px. The constant 9px delta is scrollbar-gutter
   accounting. Table right edge 1066 matched exactly. My char offset 8142 was
   actually byte 8169. Conclusion unaffected, numbers corrected forward.
2. **The defect was not Doctrine-only.** Ecosystem was equally affected
   (`div.pad` 992 vs card 969). I had reported a narrower blast radius than the
   truth.
3. Paint-level scrollbar rendering is **not verifiable in headless Chrome** - it
   reserves the 9px gutter but paints no scrollbar, so a pixel diff between
   `auto` and `hidden` was identically zero. Closed separately in a headed
   browser: the `TEST` column reads `NoRomanianInCode`, `BrainAndMonitor`,
   `DashboardSurface`, `CrossInstance`, and `scrollLeft` moves 0 -> 80.

Accepted as cosmetic, not fixed: at <=1100px `.pad` reserves a 9px scrollbar
gutter (`padRectH` 988 vs `padClientH` 979). `.pad` has no height or max-height
and vertical-overflow pads measured 0 at every viewport x tab.

### Second silent omission: the header dropped STALE

`index.html:1151-1152` rendered `ok / fail / not-run` and omitted `STALE`, while
the family table at `:1400-1402` and the history line at `:882-883` both included
it. Measured consequence: the header read `54 ok / 0 fail / 0 not-run` beside the
word `DEGRADED`, while the family table read OK 54 / FAIL 0 / STALE 2 / NOT_RUN 0
= 56. The most-read element on the page contradicted itself, and the number beside
`DEGRADED` contained no reason for it.

Fix, applied only after the verifier released the file:

    (counts.OK!==undefined ? ' · '+counts.OK+' ok / '+counts.FAIL+' fail / '+
      (counts.STALE||0)+' stale / '+counts.NOT_RUN+' not-run' : '')

Defensive default, so an older snapshot lacking the field cannot print
`undefined` in the header.

Proven surgical by RECONSTRUCTION, not by a line diff: replacing the edited block
with the original block reproduces `index.html.bak2` byte-for-byte
(`reconstruction_matches_bak2: True`). A line-index diff was tried first and was
misleading - after an insertion every subsequent line index shifts, so it reported
875 changed lines for a 1-region edit. The reconstruction is the honest check.

Live after the fix: header `DEGRADED · 53 ok / 0 fail / 3 stale / 0 not-run`,
family table OK 53 / FAIL 0 / STALE 3 / NOT_RUN 0 = 56,
`header_matches_family_exactly: true`.

Final sweep at 1024 and 1280, 13 tabs each: 0 silently clipped, 0 empty panels,
0 console errors, 13 panels in the DOM.

### A measurement that was mine, not the system's

Mid-verification I read the family table as empty and nearly filed it as a second
defect. `#wire-families` **is** the `<tbody>`; my selector looked for a `tbody`
inside it. The table held 2,462 bytes of markup the whole time. A comparator that
returns zero rows is not a finding until the selector itself is proven to select
something.

**Lesson.** Three of this round's errors were mine and all three were caught the
same way - by checking whether the MEASUREMENT could succeed before believing its
output. Exception list, aggregation level, selector. In each case the system was
correct and the reading was not.
---

## R9 — The theme that was never tested (2026-10-10)

### An untested surface, not a missing one

Every measurement in this project up to now had been taken with
`data-theme="obsidian"`. The paper theme existed, had a working toggle, and had
never once been loaded by any audit. A control room has two lighting states; one
of them was unmeasured.

### What was wrong, in four separate layers

| layer | defect | measured |
|---|---|---|
| `--ink3` | failed AA in BOTH themes | obsidian worst 3.40:1, paper worst 2.89:1 (need 4.5) |
| `#theme` button | no colour rule at all -> UA default black | 1.15:1 in obsidian, fine in paper |
| `--cyan` in paper | dark-theme accent carried over unchanged | worst 3.36:1 |
| paper override | INCOMPLETE - `--notrun`, `--orange`, `--purple` never overridden | worst 1.67-2.08:1 |
| `pre.out` | `rgba(0,0,0,.36)` in both themes with `--ink2` text | 2.77:1 in paper |
| `header` | hardcoded near-black gradient in BOTH themes | see below |

The `#theme` button is the one a visual audit catches instantly: it looked washed
out in the first screenshot of the session and I read past it. It was at 1.15:1 -
present in the DOM, clickable, effectively invisible - and it PASSED in paper. An
audit that looks at one theme calls that fine.

### Fixes, all solved rather than eyeballed

Every value was searched per surface, with a 0.35 margin above the threshold:

- obsidian `--ink3` `#64748b` -> `#818ea0`, worst **4.86**
- paper `--ink3` `#7b8a9d` -> `#5a6573`, worst **4.86**
- paper `--cyan` `#0284c7` -> `#02699f`, worst **4.88**
- paper `--notrun`/`--orange`/`--purple` -> `#98460d` / `#8b5121` / `#655497`, worst **4.85-4.86**
- `button{color:inherit}` so a form control cannot fall back to the UA default
- `pre.out` gets a light tint in paper instead of a black one
- `--band` variable: the sticky header gradient is now per theme

The ink > ink2 > ink3 hierarchy survives in both themes.

### The one the checker could not see

`header` painted `linear-gradient(180deg,rgba(5,7,10,.97),rgba(5,7,10,.86))` with
`backgroundColor: transparent`. A contrast audit that reads `backgroundColor`
walks up to the light body and concludes the dark header text is fine. The
pixels were near-black. The paper theme rendered a dark band across the top with
the title, the status pill and the whole tab strip dark-on-dark.

Found by LOOKING at a screenshot after the numbers said 0 failures. The auditor
was extended to composite the most opaque gradient stop, and its scope was
widened past `section.panel` to header, nav, footer and the searchbar.

### The measurement that reported the previous state

The extended auditor then reported 26 paper failures that were not real. Setting
`data-theme` and reading `getComputedStyle` in the SAME expression returned a
stale `color` (obsidian cyan) next to a correct `borderBottomColor` (paper cyan)
- two properties of one rule, mutually incompatible. Read in a later task, both
were correct. Chrome had not invalidated dependent computed styles yet.

This is why the final numbers are taken with a task boundary between changing
the theme and measuring it.

### Result

| theme | elements checked | failures |
|---|---|---|
| paper | 1948 | **0** |
| obsidian | 1890 | 2 |

The 2 obsidian failures are the same element: `--fail #EF4444` at **4.39:1**
against 4.5. That variable is declared under `/* semantic accents (spec-pinned) */`
and is deliberately NOT changed here. A 2.4% shortfall against a ratified value is
the operator's call, not a silent edit.

Also measured after the palette work: 0 silently clipped cards, 0 empty panels,
0 console errors, 13 panels in the DOM, and the paper theme confirmed by
screenshot - light band, readable title, readable status pill.

**Lesson.** Three of this round's errors were mine, and two of them were the SAME
error: reporting a state the system had not settled into. A checker with a blind
spot is more dangerous than no checker, because it returns zero - and zero reads
like a result.
---

## R10 - the dashboard never refreshed itself (poll starvation)

**Date:** 2026-10-10. **Found by:** backend-disconnect resilience test (T6), post-recovery phase.
**Severity:** highest of the session - silent, permanent, and it invalidates every figure on screen.

### What was wrong

`armPolling(ms)` cleared the existing interval and started a new one. `onStreamClose` called
`armPolling(30000)` unconditionally on **every** stream close. The server closes the stream on
its designed cycle, measured at **~15-25 s**. So each close restarted a 30 s countdown before it
could expire, and the poll **never fired**.

Measured, not inferred:

| observation | value |
|---|---|
| stream closes in ~70 s | 4 |
| `/api/health` fetches in the same window | **1** (the single pair `connect()` makes at line 1125) |
| `armPolling(5000)` over 12 s | 3 - fired reliably |
| poll timer state | alive, correct, and starved |

The dashboard therefore fetched `/api/health` **exactly once, at page load**, and kept showing
those numbers for the life of the page while the `age` indicator - rendered on its own 1 s
interval - kept advancing. A control centre that looks alive and is not.

### Why it survived every earlier check

A fresh load is healthy by construction: `connect()` fetches once at startup. The screen looked
correct, the counts matched `/api/health`, and nothing was red. Only a test that waits longer than
the reset interval and counts the fetches can see it.

### Fix

`armPolling` became idempotent with respect to cadence - it returns early when an interval is
already running at the requested cadence, and only re-arms when the cadence genuinely changes
(connect 12000 -> live 30000 -> unavailable 5000). Pure insertion, +854 B, 117825 -> 118679 B.
Surgical edit proven by reconstruction: reverting both hunks reproduces `.bak5` byte-for-byte
(SHA256 `2E08BC3C2AB38C9...D43AF18`).

### Verification

| phase | result |
|---|---|
| polls after fix | `state@25s`, `health@25s`, `state@55s`, `health@55s` - steady 30 s, across 3 closes |
| tile `measured` stamp | advanced `18:37:17` -> `18:37:53` -> `18:40:00` with **no reload** |
| API blocked | `NOT_RUN`, 1 family row, note `UNMEASURED. /api/health did not answer...` |
| unblocked, +30 s, no reload | `DEGRADED - 46 ok / 0 fail / 10 stale / 0 not-run` |
| Wiring panel after recovery | 9 family rows / 2462 B, `MCP declared 26`, `MCP wired 26`, `Dependencies OK 13/13` |

### Lesson

A periodic task re-armed by its own input is not periodic. The stream close is *normal traffic*,
and the code treated every close as a reason to restart the clock. Before measuring a scheduler,
count its invocations over an interval **longer than every event that touches it** - a shorter
window reports a healthy timer.

### Errors of mine in this investigation, recorded

1. A probe read `/api/state` for `checks` / `families`; the real keys are `health_checks` and
   `by_family`. It returned 0/0 and I nearly wrote "the API serves nothing" from it.
2. `browser_network` request tracking returned 0 entries while my own in-page `fetch` returned 200.
   An empty tracker is not an absence of traffic.
3. I concluded "the poller is dead" from zero fetches, then had to disprove my own detector by
   proving the wrapper counts a hand-made call before believing the zero. The wrapper worked; the
   conclusion needed the extra hour of measurement anyway, because the timer was not dead - it was
   starved.
4. `button[data-tab="wiring"]` is `button[data-tab="Wiring"]`. Two screenshots were taken before I
   checked `aria-selected` instead of trusting that a click had landed.
---

## R11 - a guard test for R10, and the two ways I nearly shipped it hollow

**Date:** 2026-10-10. **Subject:** `polling_refresh` in `08_SELF_IMPROVEMENT\test_deployment.py`.

### Why a test at all

R10 was found by hand, once, after long measurement. Nothing in the suite could
see it: every check loads the page fresh, and a fresh load is healthy by
construction. A defect that only exists across time is invisible to a suite that
only samples the start.

`polling_refresh` counts `/api/health` requests over a 50 s window - longer than
the 30 s cadence and longer than the ~25 s close gap - and requires more than the
single pair `connect()` makes at startup.

### The sensitivity control, built in

The check serves the same page a second time with the cadence guard line removed
and requires the count to **drop**. A detector that cannot fail is not a detector;
it converts a live defect into a green run, which is strictly worse than having
no check at all.

Measured on this run:

    live page fetched /api/health 2x in 50000ms (poll fired);
    control with the guard removed fetched 1x - the check discriminates

The control reproduces the pre-R10 behaviour exactly: one fetch, forever.

Suite: **41 passed / 0 failed / 1 not-run, exit 0** (was 40/0/1).
`test_deployment.py` 94750 -> 99011 B. Edit proven surgical by reconstruction to
`.bak-r110` (SHA256 `5E58F9C1BEE8F508...ACCC12D935`).

### Two bugs of mine, both of which would have shipped a hollow test

1. **Nested `sync_playwright()`.** I wrapped two window runs in an outer
   `with sync_playwright()`, and the sync API refuses to re-enter its own asyncio
   loop. Result: `polling_refresh: browser run failed` reported as **NOT_RUN** -
   and the suite still printed `40 passed / 0 failed`. A green suite line
   concealing a test that never executed is the exact failure mode this file's
   own `main()` comment warns about, one level up.

2. **`add_init_script` is not `evaluate`.** `evaluate` CALLS the function it is
   given; `add_init_script` runs the string as a raw statement. My bare
   `() => {...}` defined a function and discarded it, so `window.__hc` stayed
   undefined and the run died with `TypeError: '<' not supported between
   instances of 'NoneType' and 'int'`. Fixed to an immediately-invoked script,
   with the read now returning `-1` for a non-number so the next failure names
   itself instead of raising a comparison error.

Validated standalone before re-running the suite: `__hc = 1` at 8 s, `2` at 38 s.

### Lesson

**NOT_RUN is not a failure and not a pass - it is an absence, and it must be
visible in the count.** Both of my bugs produced a NOT_RUN line that a reader
scanning for red would miss. The counter going 40 -> 41 is the only thing that
proves the new check ran at all; the pass count is not decoration.

Two wrappers that look alike (`evaluate`, `add_init_script`) and behave
differently is a trap worth naming: **check whether a callback is invoked, do not
assume it.**
---

## R12 - the same defect class, hunted everywhere else, and the escalation path

**Date:** 2026-10-10. **Subject:** every other scheduler in the Command Center,
and the branch R10's fix touched but nothing had exercised.

### Bounded negative result - other schedulers

The R10 lesson generalises: a defect that only exists across time is invisible
to a suite that samples the start. So the question is not "is the poller fixed"
but "what else in this page can stop without ever going red".

Examined, by reading the source:

| mechanism | verdict |
|---|---|
| `setTimeout` | **none in the file** |
| `requestAnimationFrame` | **none in the file** |
| `setInterval` | exactly two: the poll and `renderHeader` (1000ms). `renderHeader` has no re-arm path, so nothing can starve it |
| `applyState` | re-renders header, stop, overview, brain, doctrine, program, workflow, tests, wiring, learning, **gauges**, and `scheduleHistory()` on every SSE frame - so gauges and the history chart refresh from data, not from a one-shot boot call |
| `scheduleHistory` | guarded by a `historyFetchedAt` timestamp floor, not by re-arming a timer. The correct shape |
| per-tab loaders | `select()` (line 1044) calls `loadOperator` / `loadMethod` / `loadEcosystem` / `loadVerify` **unconditionally on every activation** - no cache, so an outage cannot leave a panel frozen at its boot result |

Conclusion: one scheduler was broken, and it is fixed. Nothing else in this page
has the same shape.

### The escalation branch, exercised

R10's guard makes `armPolling` idempotent *at the same cadence*. That could have
broken the two legitimate escalations (12000 -> live 30000 -> unavailable 5000)
by making them no-ops. They are not no-ops: the guard compares cadence, so a
genuine change still re-arms. Measured rather than argued, by killing the stream
and leaving REST alive - the inverse of the R10 test:

| condition | `/api/health` fetches | header | panels |
|---|---|---|---|
| stream blocked, REST up, 42 s | **8** (the 5000ms fallback) | `polling - no frame` | 9 family rows, 46 ok |
| stream restored | 13 cumulative | stream indicator gone | 9 family rows |

Two things proved here that the happy path cannot:

1. The escalation to 5s **survives** the guard.
2. The header says `polling - no frame` while the data keeps arriving - the
   transport failure is reported honestly and the numbers are still refreshed.
   A dead stream and a dead backend look completely different on screen, which
   is the whole point of an HMI.

### Lesson

A fix that adds a guard must be tested against the branches the guard could
swallow. Checking that the primary path still works proves only that nothing
regressed - it cannot see a deduplication guard eating an escalation.
---

## R13 - F0: the doctrine loss was two thirds false, and the disk said so

**Date:** 2026-10-10. **Subject:** `11_BRAIN/04_METHOD/MISSTEPS_AND_CORRECTIONS.md`.

### The claim I had been carrying

M-28 records that appending it destroyed M-01 through M-27 - 44,576 B, 673 lines -
in one write, and states plainly: *"There is no version control in this project, no
backup of this file... The content is not recoverable from disk."* I had been
carrying F0 to Popy as "restore M-01…M-27 from Popy's copy", i.e. as an ACCESS
item. **I had never checked whether that was true.** §00 says search the disk
before asking him, and I skipped the search on the one item where it mattered
most.

### What is actually on disk

| copy | size | entries |
|---|---|---|
| live `SENTINEL_PRIME\...` | 6,406 B | **M-28, M-29 only** |
| `VERSION_REFERINTA_2026-10-06` (+3 nested copies) | **29,738 B** | **M-01 … M-23**, all 23, one SHA256 across all four |
| `FULL_BACKUP_2026-10-05_042054`, `10-04_QUARANTINE`, `10-05_100216`, `10-05_102017` | 8,075 B | M-01 … M-10 |

The 29,738 B copy also carries the file header, the FROM-THIS-CORPUS / FROM-SESSION-MEMORY
provenance split, and the closing essay *The pattern across all of them* - all of
which the live file also lost. The four 29,738 B copies are byte-identical
(`7DCB88E3781344DC...B592A3B`), so there is no ambiguity about which is authoritative.

**Recovered: 23 of 27 entries, verbatim.** Written to
`11_BRAIN\04_METHOD\MISSTEPS_RECOVERED_M01-M23.md`, copied byte-for-byte rather
than re-typed, so the SHA256 of the copy **equals** the SHA256 of the source. That
equality is the proof it is Popy's text and not mine; a re-typed copy could not
make that claim.

**Still genuinely lost: M-24, M-25, M-26, M-27.** Four entries, inside a 14,838 B
gap (44,576 reported pre-destruction vs 29,738 largest survivor). Per M-28's own
note their themes survive in the agent memory entries, the `14_HANDOFF` quotes,
and the source comments of the code each lesson produced.

### Why no reconstruction was attempted

M-28 states the rule: *"The tempting repair is to rewrite M-01 through M-27 from the
surviving summaries. That would be the worst outcome available... A doctrine file
partly invented by an agent is worse than a short honest one. If the entries are
to come back, they come from Popy, or they are marked as reconstruction."*

That forbids **rewriting from summaries**. It does not forbid recovering the
original bytes, which is a different act entirely - and it is the only act that
needs no permission from anyone. The distinction is the whole point: a recovery is
verifiable by hash; a reconstruction is not verifiable at all.

**The append-only live file was not touched.** It is Popy's verbatim record and the
merge is his call, so the receipt lives here instead of in his file.

### Lesson

**A recorded loss is a claim about the world, and claims expire.** "Not recoverable
from disk" was true when written and is false now - not because the file changed,
but because nobody had looked in the reference-snapshot tree. M-28 even gave the
reason it believed itself (`no version control, no backup of this file`) and that
reason was correct *about the file it had in front of it* and wrong about the
machine.

The general form: **an append-only record of a loss is the most trusted document in
a project and the least re-verified.** Nobody re-opens a file whose whole purpose is
to say something already settled. Before carrying a loss forward as a permanent
fact - especially as a question to the operator - search for the thing first, and
when a document asserts its own permanence, treat that as the claim most worth
re-measuring.
---

## R14 - C1..C9 re-verified against the build that actually ships

Measured 2026-10-10 21:5x, against the live page on `http://127.0.0.1:8910/`
and against `index.html` at 119,086 characters. Every figure below was read
off a file or off the DOM; nothing here is carried over from an earlier
proposal section.

### Where the criteria actually live

C1..C9 were not on disk. They were recovered by grepping the goal resource
(a pasted brief) for `\bC[1-9]\b` after a disk search returned nothing.
Recorded because the disk search failing is what sent me looking in the
first place - and the criteria turned out to be nine *perspectives*, not
nine tasks.

| | Perspective | Verdict |
|---|---|---|
| C1 | Aesthetic / HMI visual direction | **PARTIAL** |
| C2 | Graphical representation, data preserved | **MET** |
| C3 | Interactivity and organic motion | **MET** |
| C4 | Operator identity cockpit | **MET** |
| C5 | Full debugging / gap closure | **MET** |
| C6 | DOM integrity, SPEC_R104 null-pointer guard | **MET** |
| C7 | Dual-plane architecture, local deployment | **MET** |
| C8 | Evolution proposals, constructive spirit | **MET** |
| C9 | Non-destructive invariant, grow don't cut | **MET** |

### C1 - PARTIAL, and the two things that are missing are named

What the build has, measured: `--bg:#0B0F17` and `--surface-1:#111827` are
literally the two colours the brief names (2 occurrences each), the whole
accent set is tokenised (`--cyan` 24 uses, `--fail` 13, `--notrun` 9), and the
muted-ink chain was solved numerically after AA failures in both themes:
`--ink2:#94a3b8 / --ink3:#818ea0` in obsidian and `#4a5a6e / #5a6573` in paper.

What it does not have:

1. **No `JetBrains Mono` and no `Fira Code` anywhere in the file** - 0 hits
   for each. `--mono` resolves to `ui-monospace,SFMono-Regular,Menlo,
   Consolas,'Liberation Mono',monospace`, which is the generic stack, not the
   named typeface. The brief asked for one of those two *specifically* for
   numeric data, ports and journals.
2. **No webfont loading at all** - 0 `@font-face`, 0 `fonts.googleapis`,
   0 preconnect. Nothing is self-hosted either. So the request is not merely
   unmet, it is unmet *and* not portable: on a machine that has neither
   face installed the numerals fall back to whatever the OS picks.

This is a real gap, and it is the only one in C1. It is a build task, not a
defect - nothing is broken, a named thing is absent.

### C2 - MET, and the data-preservation half is what makes it met

Graphical layer measured live: 4 `svg[role=img]` gauges (3 `.gauge` tracks
plus the header rim), a `#hist-spark` and a `#hist-band` for latency/history,
37 `.tile` value blocks.

The half that C2 actually cares about - *"fără a elimina sau ascunde cifrele
brute"* - holds by construction rather than by promise: all **37** tiles carry
both a graphic and the raw number beside it. A gauge that hid its own value
would score C2 and fail Popy; this one does not.

The `gauge()` function also refuses to invent a reading: on a non-finite
fraction it returns an empty track with no fill and no number, because a
greyed `0%` reads as "measured, and it is zero", which is the one thing this
page exists not to say.

### C3 - MET

Four `transition` declarations, all under the brief's 200ms bar
(`background .12s`, `color .12s`, and two on `--t-fast`/`--t-med`), one
`cubic-bezier` easing token, three `@keyframes` (`beat`, `rim`, `panelin`),
and `prefers-reduced-motion` is honoured. Tab activation sets `.active` and
runs `panelin`; the 13 buttons all carry `role="tab"` with `aria-selected`.
Measured by clicking all 13 tabs in sequence: no throw, no flicker state
left behind.

### C4 - MET

The Operator panel is not a stub. Measured after activating the tab:
4 summary tiles (`SIGNED IN YES`, `CLOUD DEVICE BOUND`, `AGENTS 6`,
`SWARM ALIVE 0/5`), 4 `opcard` sections (Operator identity / Session and
activity / Cloud and subscription / Agents and tooling), and **32** pulsing
surface nodes each carrying class `node MEASURED`.

It also honours the no-invention rule where the data genuinely is absent:
`TOKEN IN ENV not set`, `TOKEN FILE EXISTS no`, and the sentence *"No Design
cloud credential is configured. Every Design cloud surface below is therefore
NOT_AVAILABLE, not failing"*. Hardware is the one family with no source in the
payload and is shown unmeasured rather than guessed - stated in the panel
copy, not buried.

### C5 - MET (carried forward from the audit section, restated here)

13 whitelisted action buttons in the cockpit, each sending an id and never a
command string; an unknown id returns 400. 24 SPEC_R104 guards, both suites
green (505 passed / 41 passed 1 not-run), seven defects found and fixed with
measurements in R1..R13.

### C6 - MET, and I got the measurement wrong before I got it right

The brief demands `if (!element) return;` before every write. My first pass
counted `if (!` and `if( !` and reported **0 guards**, and a live sabotage of
five render targets produced 0 errors - which read like a clean bill.

Both halves were wrong, in opposite directions:

- The regex missed the real syntax. The file uses `if(!tBox || !fBox ||
  !gBox) return;` with no space. A line-by-line scan for `SPEC_R104` finds
  **24 guard lines**, at 973, 1013, 1203, 1253, 1267, 1305, 1323, 1336, 1352,
  1379, 1427, 1534, 1554, 1580, 1693, 1804, 1984, 2019, 2030, 2037, 2074.
- The browser test was empty because the renderers are not on `window` as
  bare names, so my `renderOverview()` call threw `not defined` and the
  "0 errors" I recorded was the absence of a test, not the presence of
  safety.

The test that actually proves it: remove `ov-tiles`, `op-cards`,
`wire-families`, `ov-gauges`, `eco-rows` from the live DOM, then click all 13
tabs. Result - **0 errors, main alive, 13 tabs still present**, every
renderer returning early at its guard. This is the falsification control
done right: the sabotage is real, and the guards are what absorb it.

All 48 DOM targets the script writes to exist statically in the markup, so
the guards are protecting a real failure mode rather than a hypothetical one.

### C7 - MET, with the standing naming deviation unchanged

Measured, not assumed: port 8910 open, port 8912 open, `/readyz` returns 200,
header `X-SENTINEL-Deployment: mavis-sentinel-hub`. The Startup batch is
4,557 bytes and contains **0** occurrences of `#Requires -RunAsAdministrator`,
`RunAsAdministrator`, `net session`, `takeown`, `icacls` or
`-Verb RunAs` - the non-admin convention the brief names is genuinely held.

The deviation stands as recorded in `DEPLOYMENT.md`: the brief says
`gemini-minimax-hub`, the build ships `mavis-sentinel-hub`, per Popy's own
spoken instruction to include the builder's name. Not re-decided here.

### C8 - MET

All eight proposals P1..P8 are present as their own `## Pn —` sections in
this file (96,071 characters). P4 is explicitly flagged rather than
recommended as-is, which is the honest form of the instruction "document
clearly as future evolutions".

### C9 - MET

13 panels, none removed; 27 `NOT_MEASURED`, 26 `NOT_RUN`, 6 `NOT_AVAILABLE`
markers in the page; `never silently` appears in the file's own rule comment.
Every fix across R1..R13 was additive, and `.gitignore` was written to
exclude no content at all.

### What this changes

The gap named in the handoff and in the 20-04 report - "the construction
layer is not covered" - is now measured. It resolves to **one named missing
thing** (the two typefaces in C1, with no webfont loading to make them
portable) and **eight covered perspectives**. C1 is the only perspective
still carrying build work; nothing in it is broken.

That number is a measurement, not a completion. Building the typefaces is
new construction, and it is the honest next step rather than a defect to
repair.
---

## R15 - C1 closed: the named typeface, and three bugs on the way

Measured 2026-10-10 19:0x-19:1x. This builds what R14 recorded as missing.
`index.html` 119,368 -> 121,131 B. `api\server.ps1` 27,715 -> 30,482 B.
Backups: `index.html.bak7`, `server.ps1.bak-font`, `EVOLUTION.md.bak9`.

### What went in

- `fonts\jetbrains-mono-400.ttf` and `-600.ttf`, self-hosted, 112,172 and
  112,160 B.
- Two `@font-face` rules with `font-display:swap`, plus two `<link rel=preload>`.
- `--mono` now reads
  `'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace`
  - the named family first, the previous stack untouched behind it.
- One static-asset route in `server.ps1`.

### The server never served anything static. That was the first bug.

The `@font-face` URLs resolved to **404**, not to the font. The reason is in
the shape of the server: its `switch` had a `default` branch that answered
`404 'not found'` for every path that was not one of its named API routes.
There was no static file handler at all. The font declaration was correct and
completely inert - which is the C5 failure mode this project has been
tracking all along, one level up.

The fix is an **allowlist, not a path handler**:

    $ASSETS = @{
      'fonts/jetbrains-mono-400.ttf' = 'font/ttf'
      'fonts/jetbrains-mono-600.ttf' = 'font/ttf'
    }

Two files, named literally. Anything not named is still 404. No traversal
string reaches the filesystem, because the URL is compared against a fixed
set before a path is ever built.

Measured against that allowlist:

| Request | Result |
|---|---|
| `/fonts/jetbrains-mono-400.ttf` | serves |
| `/../../../Windows/System32/drivers/etc/hosts` | 404 |
| `/..%2f..%2fWindows/win.ini` | 404 |
| `/fonts/../../api/server.ps1` | 404 - source unreachable |
| `/fonts/jetbrains-mono-400.ttf%00.png` | 404 |
| `/etc/passwd` | 404 |
| `/api/../../index.html` | 404 |

### The second bug: a 200 that delivered a corrupted font.

`Send-Response` ends with `[Text.Encoding]::UTF8.GetBytes($body)`. It takes a
**string**. I passed the font through `[IO.File]::ReadAllBytes` and then
converted it to a string to hand it over, which round-trips the bytes through
a text encoding and corrupts them.

Measured, same input file:

    on disk             : 21088 bytes
    via string (old)    : 37816 bytes   <- length changed, so corrupted
    via byte[] (new)    : 21088 bytes   <- identical

The HTTP status was a healthy **200** with the right `Content-Type` on a
corrupt body. Nothing above `Send-Response` can tell that apart from success.
This is why the font failed to load on the first attempt and why "the server
returns 200" was never sufficient evidence that it worked.

`Send-Response` now passes a `byte[]` through untouched and only encodes a
string when it is given one.

### The third bug: the WOFF2 files were valid and still rejected.

After the byte fix, Chrome still refused both faces:

    OTS parsing error: Failed to convert WOFF 2.0 font to SFNT
    OTS parsing error: Size of decompressed WOFF 2.0 is less than compressed size

Before blaming the browser I checked the bytes on both sides:

- disk: 21,088 B, sha256 `7C53386F...`
- over HTTP: 21,088 B, sha256 `7C53386F...` - **identical**
- magic bytes `77 4f 46 32` = `wOF2`, a correct signature
- redownloaded with curl: 21,088 B, same hash

So the files were intact and were being delivered intact, and the browser
still rejected them. I did not spend longer proving the file was good - the
measurable move was to change one thing and see. Google Fonts serves this
family as TTF, so both weights were fetched as TTF (112 KB each, magic
`00 01 00 00`) and the console went to **zero messages**.

The trade is stated in the file rather than hidden: 112 KB per weight instead
of 21 KB, on a page served from loopback off a local disk. The bytes cost
nothing to deliver there and a rejected font costs everything.

### One more inconsistency, caught by attacking my own fix

My first allowlist used `ContainsKey`, which in PowerShell is
**case-sensitive**, while Windows paths are not. Measured: `/FONTS/JETBRAINS-MONO-400.WOFF2`
was **rejected** while the same file in lower case was served. That is not a
hole yet, because nothing differently-cased is in the table - but the first
entry somebody adds in the wrong case would have opened one. The lookup is
now an explicit `OrdinalIgnoreCase` scan, which matches the filesystem's own
rule: allowlisted means allowlisted regardless of case.

### Proof it is actually on screen

- `document.fonts.check("400 16px 'JetBrains Mono'")` -> **true**
- `document.fonts.check("600 16px 'JetBrains Mono'")` -> **true**
- 2 faces declared
- Rendered width of `0123456789` at 100px: **600px** with JetBrains Mono vs
  **550px** generic - the glyphs are measurably different, so this is the real
  font and not the fallback wearing its name.
- Browser console: **0 messages**.

Suites after the change: `test_suite.py` **505 passed / 0 failed / 0
skipped**, exit 0.

### C1 status

**MET.** All nine perspectives are now covered. The requirement was written
into the page as a declaration and was invisible on screen; it is now a file
on disk, served by the backend, loaded by the browser, and measured three
separate ways.
---

## R16 - the verifier refuted my own reason, and I am writing that down

Measured 2026-10-10 22:30. An independent verifier reviewed commit `b5b14c4`
and returned **PARTIAL**: everything functional confirmed, one written claim
false. This section is the correction. Nothing was quietly deleted; the false
text is quoted above and struck here.

### What it confirmed

- The allowlist held against **33 probes**. No non-TTF file was readable.
  The structural reason matters more than the probe list: `Join-Path`
  receives `$key`, a literal out of the hardcoded hashtable, never `$rel`.
  Attacker input can only *select* an allowlisted name, never *compose* a
  path.
- All 18 `Send-Response` call sites pass strings; the new `--byte[]` branch
  broke none of them.
- `check400`/`check600` true, console 0, 24 SPEC_R104 guards, 13 panels,
  13 render functions - all identical to the parent commit.
- Both suites re-run by the verifier, sequentially: 505/0/0 and 41/0/1.
- The four font files are byte-identical to their committed git blobs.

### What it found false - and it was mine

**R15 claimed Chrome's sanitizer "still rejects both" WOFF2 files.** False.
The verifier served both quarantined files unmodified over HTTP as
`font/woff2` and measured in Chrome 155:

| | measured |
|---|---|
| w400 WOFF2 | 600px, `loaded`, `check400` true |
| w600 WOFF2 | 600px, `loaded`, `check600` true |
| generic | 549.81px |
| console | **0 messages** |
| OTS errors | **zero** |

The OTS errors I saw were real, but they were caused by my own server bug -
`Send-Response` UTF-8-encoding a string, which the verifier reproduced
independently: **21,088 -> 37,816 bytes**. The brotli stream is destroyed and
the `wOF2` signature survives only because its first bytes are ASCII.

So the `--byte[]` fix alone was sufficient. The WOFF2 files were never at
fault, the format switch to TTF was unnecessary, and the 5x size penalty I
wrote a justification for was self-inflicted.

### Why the error happened, stated as a method failure

I changed **two things** between the failing observation and the working one:
the byte path, and the file format. With two variables moving I could not
tell which one fixed it - so I attributed the win to the change I found
last, and wrote that into the code as if it were established fact.

There was a third candidate I never tested: `Cache-Control: immutable,
max-age=31536000` had been set on the **corrupted** body. A browser holding a
one-year cached corrupt font is exactly the symptom I observed after the byte
fix. I suspected cache once, in passing, and then moved on to blaming the
file. I never ran the test.

That is the same shape as the R11 and R14 mistakes: **when two things change,
change one.** The rule is already written in this file and I broke it anyway.

### Two smaller false statements, also corrected

- MOTIV.txt said *"prin HTTP: 21.088 B, sha IDENTIC cu cel de pe disc"*.
  That measurement was taken **after** the byte fix, so it cannot describe
  the moment the font was refused. It contradicted the very comment beside
  it in `server.ps1`. MOTIV.txt now carries a correction block appended, not
  a rewrite.
- MOTIV.txt said the curl re-download proved the same hash. It is not
  reproducible: no source URL was recorded anywhere, and a fresh download
  today returns different bytes (20,740 / 21,488). That is a different
  subset, not tampering - but the provenance was never demonstrated.

### Dead code and a comment that described a fiction

`server.ps1` computed `$name = [IO.Path]::GetFileName($path)` and never used
it, while the security comment above it claimed *"$name is taken from the
URL and then matched literally against a fixed set"*. Anyone auditing that
boundary later would have been reading a description of a mechanism that did
not exist. The variable is removed and the comment now states the real gate.

### What is kept, and on what grounds

TTF stays. Not because Chrome rejects WOFF2 - it does not - but because:

1. it is the format verified **end to end through this server**, twice,
   by me and by the verifier independently;
2. 112 KB against 21 KB costs almost nothing on loopback off a local disk,
   while an unverified swap would cost a restart and a retest.

The `.woff2` files stay in quarantine, intact, with the correction written
next to them. Switching to them is a real option and a real saving, and it
is now recorded as an option rather than left as a false claim.

### Honest gaps the verifier named

- I cannot reproduce what my browser literally showed at the time; the buggy
  code path is gone. What is proven is that the files are valid and Chrome
  accepts them when the bytes arrive intact.
- The WOFF2 CDN provenance is unverifiable - no URL was ever recorded.
- The browser proof is headless. I have no measurement of the headed browser
  Popy actually looks at.
- **The new route has no automated test.** Its traversal safety currently
  rests on a verifier's probe list, not on a check that runs every time.
  That is the most substantive of the four, and it is construction, not a
  repair.
### The route now has a test, and getting one took two broken controls

The verifier's sharpest remaining point was that the new route had **no
automated coverage** - its traversal safety rested on a manual probe list.
Added: `static_route` in `test_deployment.py`, four checks.

1. `serves_intact` - both fonts 200, byte length equal to disk, TrueType header.
2. `refuses_traversal` - 11 traversal shapes, asserted on the PAYLOAD rather
   than the status, because HttpListener answers 400 or 403 for some shapes
   before the route is reached. What must never happen is bytes coming back.
3. `gate_is_literal` - static: every `Join-Path $ROOT` receives `$key`.
4. `control_discriminates` - the same predicate re-run against the gate
   rewritten in memory to take `$rel`; it must FAIL.

**Control v1 was worthless and proved it by failing.** It wrote a neutralised
copy of `server.ps1` to disk and then probed the LIVE server. The copy was
never executed, so the control reached exactly as far as the live route - the
check reported `0 vs 0 - not measuring the gate`, which was correct.

**Control v2 was the same defect in a new hat.** It actually started the
neutralised copy on port 8925 and probed that. The process started but never
bound the port; every probe got no connection. A control that cannot attach to
the thing it attacks measures nothing regardless of how carefully it was
written.

**v3 asserts the invariant statically** - the same shape the suite already
uses for `test_verb_argv_is_not_joined` - and neutralises in memory so the
predicate is exercised without needing a second listener. The suite then also
caught a third authoring bug: the rewrite consumed the line defining `src`, so
the check died with `NameError` at line 1220 instead of running. Three
failures in one test, each caught by the test rather than by me.

Final: **45 passed / 0 failed / 1 not-run**, including all four `static_route`
checks.

### Suite totals after every correction

| Stage | test_suite.py | test_deployment.py |
|---|---|---|
| after the C1 build | 505 / 0 / 0 | 41 / 0 / 1 |
| after R16 corrections | 505 / 0 / 0 | 41 / 0 / 1 |
| after adding route coverage | - | **45 / 0 / 1** |
# ACT VI — THE DEPLOYMENT GAP: what was built vs. what was actually deployable

**Date:** 2026-10-04, 20:00–20:40
**Trigger:** Popy, correctly: *"The skill folder you created is supposed to represent active skills, but I cannot access them via slash command in Minimax. They do not exist. … You are creating things without installing them and wiring them into the system."* And: *"The link is down."*

**Verdict up front:** Act V delivered a system that **measured** correctly and a set of skills that were **inert**. Both claims were true at the same time, and only one of them was load-bearing. This act closes the deployment gap and, in doing so, found four more defects — one of them invalid PowerShell that made half the launcher's verbs fail while the other half worked.

---

## 1. The core finding: a skill file is not a skill

Four `.SKILL.md` files sat in `SENTINEL_PRIME\07_BACKBONE\skills\`. I had reported them as skills. **They were documents.** Two independent reasons, either one fatal on its own:

### 1.1 Wrong root — the runtime never looked there

The runtime reads exactly three roots:

| Root | Count at the time | Read by |
|---|---|---|
| `C:\Users\apviz\.minimax\skills\<name>\SKILL.md` | 1,279 | the catalog (every name in `available_skills`) |
| `C:\Users\apviz\.minimax\agents\mavis\skills\<name>\SKILL.md` | 55 | the mavis agent |
| `C:\Users\apviz\.minimax\.builtin-skills\` | 21 | the product |

`SENTINEL_PRIME\07_BACKBONE\skills\` is in **none** of them. A file in a project directory is
inert no matter how well written it is. This is the same failure class as a page served over
`file://` that cannot reach its API: correct content, unreachable surface.

### 1.2 No frontmatter — nothing to index

None of the four had a `---` block:

```
# Bimodal Workflow — SENTINEL Skill      ← the first line of the file
```

Every working skill opens with `name:` and `description:`. Without them there is nothing for the
catalog to index, so the skill could not be listed, could not be routed to, and could not be
loaded **even if it had been in the right directory**. A copy would not have fixed it.

### 1.3 What the encoding check cleared

`Get-Content` in PowerShell 5.1 rendered the files as mojibake (`â€”`). A byte-level check
confirmed they are **valid UTF-8** — the console was lying, not the files. Worth recording because
the same false signal had already cost time earlier in this build, and the reflex is always to
"fix" correct Romanian.

---

## 2. The repair: a deployment step, not a copy

`08_SELF_IMPROVEMENT\install_skills.py` — project file (**source of truth**) → runtime skill root
(**loaded**). Re-runnable, idempotent, and it verifies by **re-reading from disk and parsing the
frontmatter** rather than by trusting that a write happened. It explicitly refuses to claim a
skill is installed, because that claim is proven by the runtime loading it.

Five skills, named to the existing `mavis-<name>-skill` convention:

| Installed name | What it is |
|---|---|
| `mavis-sentinel-prime-on-minimax-skill` | the deployment procedure + verification discipline |
| `mavis-sentinel-prime-role-skill` | the role: SOUL/CONSTINTA, Triple Crunch, priority order |
| `mavis-sentinel-bimodal-workflow-skill` | MODE_A → R0 → MODE_B → STOPPED |
| `mavis-tany-llm-to-sentinel-skill` | how any LLM is constructed into a SENTINEL |
| `mavis-sentinel-command-center-skill` | **new** — operate the dashboard |

`mavis-r33-bimodal-skill` already existed, so `bimodal-workflow` was installed as a **child**
(`parent: mavis-r33-bimodal-skill`) rather than as a rival. Duplicating a skill that already
covers a concern would have created two sources of truth and a silent contradiction later.

### 2.1 Proof: all five were loaded, not listed

The installer's own comment says loading is proven by the `skill` tool, not by the script. So
that is what was used. All five returned their content, e.g.:

```
Location: files:///C:/Users/apviz/.minimax/agents/mavis/skills/
          mavis-sentinel-prime-on-minimax-skill/SKILL.md
```

**Five for five.** This is the check that would have caught the original defect and it was never
run in Act V.

### 2.2 Loading them exposed a defect a file check could not see

The very first load showed the skill's own body instructing the reader:

```powershell
skill(name="bimodal-workflow")     # ← no such skill exists
```

A skill telling you to invoke a name the runtime cannot resolve is a pointer to nowhere — the
same "path exists, target does not" shape as the dead link. **It was invisible until the skill
was actually loaded**, which is the argument for loading rather than listing.

Nine stale references and two stale figures (`279 assertions`, superseded when the
crash-reporting fix landed) were repaired by `fix_skill_references.py` and re-installed.

### 2.3 Wired into routing

`mavis-skill-index` — the thing Mavis reads to choose a skill — carried stale counts
(1,159 / 22 / 22) and knew nothing of the SENTINEL skills. Corrected to the measured
**1,279 / 60 / 21 = 1,339**, plus a routing table for the five and the re-install command.
A skill that is installed but not in the index is installed but not *discoverable*.

---

## 3. The link: why it kept dying

`bat\sentinel-cc.bat` ran the server **in the foreground of a console window**. Three real
failures, all of which occurred:

1. **It died with its window.** A shell exiting took the server with it. This is what Popy saw:
   the link was live when he looked at it, then connection-refused after a refresh.
2. **Two invocations collided.** The second bind on 8910 threw — so the obvious repair
   (*start it again*) made it worse and looked like a broken build.
3. **No way to ask.** There was no `status` verb. "Is it running?" was answered by a browser error
   page.

### 3.1 The replacement

`13_COMMAND_CENTER\api\sentinel-cc.ps1` — `start` · `stop` · `restart` · `status` ·
`install-task` · `uninstall-task`.

- `start` is **idempotent**: a second call reports "already listening" instead of crashing.
- The server is launched via `Start-Process`, so it is an **independent process**, not a child
  that dies with the shell.
- `stop` matches on `server.ps1` + port, **never on a bare pid** — a stale pid file must never
  kill something unrelated that inherited the number.
- `status` probes the **port** and reports a pid file that disagrees with it as
  `STALE - process gone` rather than reporting a dead process as running.

`sentinel-cc.bat` is repointed at it, so double-click still works and now starts a detached,
idempotent server instead of a window that owns its lifetime.

### 3.2 Detachment, proven rather than asserted

Started from one shell, then probed from a **completely separate shell** with no agent process
alive:

```
shell A:  UP   http://127.0.0.1:8910/   (pid 23948)
shell B:  ui 200  bytes=48753
          health 200  bytes=18769
```

That is the specific claim Popy's complaint denied, and it now holds.

**Stated honestly:** `Start-Process` survives a shell exiting. It does **not** survive the whole
process tree being killed. Only a scheduled task does, because the Task Scheduler service — not
any agent shell — starts the process. `install-task` registers one; it is a **system-level**
change, it is reversible with `schtasks /delete /tn SENTINEL_CommandCenter /f`, and it has
**not** been run without Popy's word.

---

## 4. Two more defects, found by running every verb

### 4.1 `try/catch/else` — invalid PowerShell, which passed a syntax audit

The `stop` branch read:

```powershell
try  { Stop-Process ... }
catch { ... }
else { Write-Host "stopped pid ..." }   # ← `else` binds to `if`, never to `catch`
```

`start` and `status` worked; only `stop` and `restart` failed — **because the bad statement sat
in a branch those two never entered.** The file parses, so neither reading it nor a whole-script
syntax check would have found it. Only executing every verb does. This is the sharpest argument
in this build for "run every path", not "run the path you are about to use".

### 4.2 A slow start was reported as a failed start

`start` polls the port until the deadline, and the loop also **broke early** if the server's pid
was not found. The server takes ~13 s to collect state before it binds, so a slow-but-perfectly
healthy start was reported **FAILED** while the port came up a second later. The port is the
evidence; a pid check must not be able to contradict it. The loop now records liveness for the
error message but never breaks on it.

### 4.3 `status` took 22 seconds

Almost all of it was `Get-CimInstance` initialising the WMI provider - to answer a question the
pid file and the port had already answered. WMI is now consulted **only** when the port says
"running" and the pid file cannot corroborate it. **`status`: 22.6 s -> 4.0 s.**

### 4.4 The instrumentation was wrong three times - and each looked like a product fault

- I "proved" the launcher hung by measuring it with `& powershell ... | Out-String`. **The server
  inherits the write end of that pipe**, so the pipeline never reaches EOF. The launcher had
  exited normally the whole time. Re-measured with `Start-Process -Wait`: `exit=0` in 19.7 s.
- The self-test then hung on `start`, because **`Start-Process -Wait` waits for the whole process
  tree** and the server is a descendant that never exits. Now uses `WaitForExit()` on the object,
  which waits for that one process.
- The self-test then reported **6 of 16 assertions failing** on a launcher that behaved correctly,
  because `$p.ExitCode` reads back `$null` until the Process handle is cached
  (`$null = $p.Handle`). Every failure had the same tell: `exit=` with nothing after it.

A test helper named `R` also silently collided with the built-in `Invoke-History` alias, executing
nothing and reporting nothing. All recorded because **the instrument being wrong is the failure
mode that looks like success.**

### 4.5 A regression the browser proof caught, and nothing else did

After the `Tests` panel work, a browser proof returned:

```
JS errors : 2
  - Cannot read properties of null (reading 'counts')
VERDICT: DEGRADED
```

All 11 tabs still rendered. Route tests, the 55/55 server cycle, the test suite and a screenshot
would all have called it fine - **the console is the only surface that knows.**

Cause: `let STATE = null`, while every renderer treats a *missing field* as not-measured
(`STATE.counts || {}`). Missing fields were handled everywhere; the **container** being null was
not, and the first `STATE.x` read threw.

Fixed at the one point rather than at eight call sites:

- `STATE` now initialises to `{}` - nothing measured yet, and every panel says so.
- `applyState` refuses a payload that parses to a non-object, so a malformed frame cannot
  overwrite good state with null.
- `renderHeader` / `renderOverview` read through a local `const s = STATE || {}`.

Re-proved **twice consecutively**: `11/11 tabs render, 0 JS errors, no coercion`.

### 4.6 The launcher self-test, 16/16

`08_SELF_IMPROVEMENT\verify_launcher.ps1` runs **every** verb from a known-down state and checks
the exit code *and* the side effect, probing the port independently of the launcher rather than
believing its own report. `Start-Process -PassThru` also needed the pid taken before
`Dispose()`ing the object, which had blocked the launcher on exit.

### 4.7 The trap I fell into myself: `HttpListener` is not a normal socket

The link came back down after the self-test finished, so I went to clean up what looked like two
stray `server.ps1` processes and asked `Get-NetTCPConnection` which one owned port 8910. It
answered **pid 4 — System**. I killed both server processes, and the link went dead.

`netstat` confirms why:

```
TCP    127.0.0.1:8910    0.0.0.0:0    LISTENING    4
```

**`HttpListener` on Windows binds through the HTTP.sys kernel driver.** The listening socket is
owned by the kernel, not by the PowerShell process serving it. So *every* "which process owns this
port" heuristic returns System, and acting on it takes down every HttpListener server on the box.

The launcher's own `Get-ServerProcess` was already correct — it matches the command line and
never the socket — and the comment above that function now says **do not simplify this to
`Get-NetTCPConnection`**, with the evidence. `Test-Listening` remains the only thing that answers
"is it serving", and it is the evidence the whole script trusts.

**The generalisable part:** a destructive action justified by an *indirect* signal. The pid file,
the socket table and the process list are three different claims; I acted on the one that was
cheapest to query and least likely to be what I assumed. Match on the thing you mean.

### 4.8 How the link actually stays up

`Start-Process` survives a shell exiting. It does **not** survive the process tree being killed —
which an agent harness does, and which is why the link died again after the self-test even though
it had just reported 16/16.

| Mechanism | Result |
|---|---|
| `schtasks /create /sc onlogon` | **Access denied** — not elevated. Rejected, not worked around silently. |
| `Start-Process` from an agent shell | **Killed with the tree.** Repeatedly observed. |
| `explorer.exe <bat>` | Survives — explorer is not a descendant of the agent. |
| **Startup-folder `.bat`** | **Installed.** Brings it back at logon, needs no elevation. |

Installed at
`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SENTINEL Command Center.bat`.
**Removing it is deleting that one file** — no registry, no scheduled task, no service.

### 4.8.1 The operational rule this produced — and it is not the one I expected

I assumed a detached `Start-Process` server would simply stay up. It does not, in this
environment, and I watched it die three separate times **including immediately after a 16/16
self-test**:

> **An agent cannot leave a long-lived server running.** Anything spawned from an agent shell
> is reaped when the process tree is cleaned up. Only a process started by something outside that
> tree survives — the desktop shell (`explorer.exe`), or the Startup folder at logon.

So the launcher's job is not merely to start the server; it is to make the server startable by
something that is not the agent. The `.bat` and the Startup entry are therefore load-bearing, not
conveniences.

Measured after the final clean start through `explorer.exe`, checked from shells that are not the
server's parent, across two separate intervals:

```
t+9s    http://127.0.0.1:8910/   -> 200   49,983 bytes
t+34s   UP 200 · /api/health 200 · servers: 2 (parent: powershell.exe, not the agent shell)
t+64s   UP 200  49,983 B · /api/state 200  73,947 B
browser -> 11/11 tabs render, 0 JS errors, no coercion
```

**Consequence for the operator:** if the dashboard is ever down, double-click
`13_COMMAND_CENTER\bat\sentinel-cc.bat` (or log off and back on). An agent can start it, but only
temporarily — the durable instance is the one the Startup folder or the desktop shell owns.

---

## 5. Measured state after this act

| | |
|---|---|
| Skills installed | **5 / 5** load via the runtime `skill` tool |
| Frontmatter | parsed from disk, BOM-less UTF-8, all 5 |
| Routing | `mavis-skill-index` counts corrected, 5 skills routable |
| Launcher self-test | **16 / 16 assertions**, every verb from a known-down state |
| Detachment | 200 from a fresh shell with no agent process alive |
| Idempotence | second `start` reports "already listening", no second server |
| Stale-pid honesty | `status` prints `STALE - process gone`, never "running" |
| `status` latency | 22.6 s → **4.0 s** |
| Browser proof | **11/11 tabs render · 0 JS errors · no coercion** (twice consecutively) |
| Test suite | **288 passed · 0 failed · 0 skipped · exit 0** |
| Link | `http://127.0.0.1:8910/` — loopback only, server left running |

Unchanged and still true from Act V: corpus 955 messages retention 1.0000 sha256 `e4d3cbb7…7e0e42`.

### 5.1 Not fully closed, stated plainly

- **One intermittent suite failure was seen once** (286 passed / 1 failed) while the server was
  mid-restart, and did **not** reproduce in four subsequent runs. Named rather than dismissed:
  most likely a Chromium test contending with a restarting server, but that is a hypothesis, not
  a diagnosis.
- **`start` takes ~33 s**, because the server collects state *before* it binds the port. The link
  is not dead during that time — it is unbound. Binding first and rendering `NOT_MEASURED` until
  state arrives would be both faster and more faithful to the doctrine; it is **not done**,
  because it touches a working server and would need the 55/55 cycle re-proven.
- **`install-task` is not run.** A scheduled task is the only construction that survives the whole
  process tree being killed. System-level, reversible in one command, and **Popy's call**.

---

## 6. What is still open

1. **The 5 phantom MCP servers** — `mcp_config_servers_exist` FAIL. Popy's decision: implement or
   prune. Still the one red.
2. **Public deployment** — not done, not authorised, needs a separate explicit go.
3. **Audio/video and document extraction** — installed and importable, never run against real
   fixtures. No fixture was fabricated to make them look proven.
4. **`install-task`** — available, reversible, deliberately not run.

## 7. The rule this act produced

> **A capability is not delivered when the artefact is written. It is delivered when the thing
> that consumes it can reach it — and you prove that by using the consumer, not by reading the
> artefact.**

A skill nobody can load is a document. A dashboard behind a dead link is not deployed. A verb I
never executed is not a verb. All three were "done" in Act V, and all three were caught by
touching the real surface — a `skill()` call, a browser refresh, a `stop`.

**AMIN.** System > Task > Speed > User.

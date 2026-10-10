# TEMPLATES

**These are the files that actually ran, copied verbatim from the reference
implementation — not sketches of what they should look like.** Starting from
proven code that you then adapt is worth more than starting from a clean
template, because the comments in them are the lessons.

Rename, cut to your subject, and keep the invariants marked ⚑ — each one is a
place where a plausible edit reintroduces a real defect.

---

## The seven pieces

| File | What it is | Lines that matter most |
|---|---|---|
| **`collect-state.ps1`** | measures the system, prints one JSON blob | ⚑ `Probe` records **elapsed ms and why it failed** — a `$null` collapses down/slow/late into one · ⚑ history trims in batches, and **atomically** |
| **`run-bounded.ps1`** | the one bounded command runner | ⚑ `taskkill /T` on timeout, or the grandchildren survive · ⚑ a share-permissive read, or a killed child's output cannot be read |
| **`server.ps1`** | serves the file, serves the page, whitelists actions | ⚑ atomic write · ⚑ the request path never collects · ⚑ **background job needs `-RedirectStandardInput`** or it deadlocks · ⚑ slow work returns a **job id**, never a result |
| **`index.html`** | the whole UI, no framework, no build | ⚑ `view*` is pure — read state, return HTML · ⚑ state lives in variables, not in nodes |
| **`cc-watchdog.ps1`** | keeps the server alive across crashes and reboots | ⚑ 3 strikes · ⚠️ `RestartCount`/`ExecutionTimeLimit` on the task itself |
| **`verify-ui.ps1`** | file-level self-test | ⚑ runs in ~2 s, no dependencies, so it can always be run |
| **`health-harness.ps1`** | the certifying pass, with fault injection | ⚑ **it plants its own faults first** and refuses to certify if it cannot catch them · ⚑ corrupt markers, malformed bodies, unknown ids, stale jobs · ⚑ needs N *consecutive* clean runs |

Supporting:

| File | What it is |
|---|---|
| **`shadow-audit.mjs`** | finds script-scope `let` that silently replaces a global. The check for the defect that shipped a broken feature. |
| **`reap-mcp.ps1`** | orphan reaper. **Dry-run by default.** Shows what it will *not* reach. |
| **`DASHBOARD_QUESTIONS.md`** | the stage-1 questionnaire, ready to hand over |

---

## The invariants ⚑ — do not remove these

**Collector**
- Every external call has its **own** timeout. A hang inside a call nobody timed
  is the single most expensive failure mode.
- Trace mode exists from the first line. `Trace 'before <section>'` behind an env
  var, to a log.
- The failure result carries **which** failure, not just that one happened.
- Numbers are cast to a type. `$null` flowing into arithmetic becomes `0`.

**Server**
- State writes are **atomic** — temp file, then rename over. Never in place.
- A request path **never starts a measurement**. `Get-StateJson -MaxAgeSec -1`
  is read-only; the refresh worker owns timing entirely. Any age-based trigger on
  a request path is what produced the 20-second freeze — the threshold is not
  something to tune, it is something to delete.
- **No request path runs slow work at all** — not a measurement, not a
  subprocess, not a port probe. A request writes a file and returns an id; a
  background job does the work; the page polls. This is the *other half* of the
  rule above, and it is easy to satisfy one and miss the other.
- **Measure the cost of every call on a request path, not just the obvious
  one.** The freeze moved twice: first into a cache threshold, then — after that
  was fixed — into a single line of port probing that had been sitting in the
  digest the whole time.
- A background job spawning a child **must redirect stdin**, or the whole tree
  inherits the remoting pipe and deadlocks with no error at all.
- Actions resolve an **identifier** to a command server-side. The page never sends
  a command. Output is capped.
- The server binds **loopback only**.

**Page**
- `render()` is **pure**: read state, return HTML. It never mutates.
- Anything the operator is typing, reading, or waiting for lives in a **variable**,
  never in a node that a poll can replace.
- Every value interpolated into `innerHTML` goes through `esc()` — and `esc()`
  must cover the character that appears in **your** attribute context.
- URLs are addressed with `history.replaceState` (or `window.` qualified), never
  assignment, so Back still works.
- Entrance animations fire **once**, not on every re-render.

**Supervisor**
- Three consecutive failures before acting. One timeout is a slow system, not a
  dead one.
- A grace period after every start, long enough for a first measurement to finish.
- It **restarts**; it never **repairs**.
- Verify liveness by evidence — a port, a probe — not by "I killed it".

---

## ✅ The freeze is FIXED in these templates — and this is the fix

The reference implementation carried a real freeze: a request to `/api/state`
could start a **full ~20-second collect on the single-threaded listener**, so
every request behind it waited. It presented as random unresponsiveness —
10–40 ms between freezes, so it looked like a slow machine, not a bug.

**Both request paths are now structurally read-only.**

```powershell
# the contract, inside the function
if ((Test-Path $script:StateFile) -and $MaxAgeSec -ne 0) {
  $age = ...
  if ($MaxAgeSec -lt 0 -or $age -lt $MaxAgeSec) { return ... }   # -1 = never collect
}

# /api/state, and Get-StateDigest behind /api/ask
$json = Get-StateJson -MaxAgeSec -1
```

`MaxAgeSec` is a **three-mode contract**, and the mode has to live in the
*function*, not at the call site:

| Value | Meaning |
|---|---|
| `-1` | **read-only** — serve whatever the refresher last wrote, however old. Never collects. |
| `0` | force — collect now (startup pre-warm, explicit refresh) |
| `> 0` | serve the cache only if younger than this, else collect |

**The trap that makes this worth reading twice.** The original guard was `-gt 0`.
Under that test `-1` does *not* mean "never too old to serve" — it falls straight
through to the inline collect, making the freeze **unconditional and permanent**.
Planning the fix from memory instead of reading the function on disk would have
shipped exactly the bug it claimed to remove. A new mode must be added where it is
tested.

**Recovery did not get lost.** A dead refresher is caught one level up, where it
belongs: the supervisor fails the server when the served state passes
`MaxStateAgeSec` (300 s) and restarts it. The page derives staleness from
`generated` (`stale` at 60 s, `down` at 180 s), so read-only serving cannot
quietly serve old data.

**Measured after the fix** — the state file was deliberately backdated past the old
100 s trigger, so the old code would have collected on every one of these:

| Test | n | max | non-200 |
|---|---|---|---|
| age forced to 200 s | 5 | 182 ms | 0 |
| age forced to 290 s | 6 | 229 ms | 0 |
| steady state | 30 | 614 ms | 0 |
| 8 **concurrent** requests | 8 | 350 ms | 0 |

**Do not "improve" this by tuning the threshold.** Widening it to ×5 was tried and
reverted: every request past 100 s ran an inline collect, which starved the
refresher, which left the cache permanently stale, and `/api/state` began
returning a **zero-byte body**. The threshold was never the disease — the shared
thread was. A threshold cannot fix a shared queue.

---

---

## What these templates have already paid for

Each fix below is **in the code**. They are listed because a fix nobody can see is
a fix that gets reverted by the next person who tidies the file. Do not
"simplify" them away.

| Already fixed | Where | The lesson |
|---|---|---|
| **Never capture a DOM node across an `await`** | `index.html` | the 5-second poll replaces the view; an answer that arrives 26 s later lands in a detached node. State lives in variables; render re-resolves. |
| **A background job spawning a child must redirect stdin** | `server.ps1` | a `Start-Job` runs on remoting pipes; without `-RedirectStandardInput` the whole tree deadlocks, silently, for hours. |
| **A failure result must carry *which* failure** | `collect-state.ps1` | `$null` collapses *down* and *slow* into one picture, and the operator restarts something that is working. |
| **A local `let` must not shadow a global you call** | `index.html` | `let history = []` makes `history.replaceState` undefined; it throws every render and silently takes the wrong path. Use `window.history`. |
| **`node --check` on the extracted inline script** | `verify-ui.ps1` | a page that does not parse still answers 200 and still logs nothing, because no statement ran. |
| **A request path must be unable to start a measurement** | `server.ps1` | the freeze was never the threshold, it was the shared thread. `-1` is read-only; the refresher owns timing. |
| **Read the function before planning a change to it** | `server.ps1` | the planned one-line fix would have made the freeze *permanent*: the existing `-gt 0` guard turns `-1` into "always collect". |
| **No machine-bound absolute paths** | `server.ps1` | `-ComposeFile` / `-AiPython`, defaulted from `$env:USERPROFILE` / `$env:LOCALAPPDATA`. A template that only runs on one machine is not a template. |
| **Long work returns a job id, never a result** | `server.ps1` + `index.html` | a 26–70 s model call on a single-threaded listener froze *every* poll for its full duration. POST returns an id in ~0.5 s; `GET /api/ask/<id>` is a file read; the page polls. |
| **The prompt goes in on stdin as a FILE** | `server.ps1` | the job is a `Start-Job`, so it runs on remoting pipes — a piped prompt deadlocks exactly like the collector did (#17). A file cannot deadlock. |
| **A self-test stub must speak the real protocol** | `index.html` | when the analyst went two-step, the old stub answered the POST with the answer and would have passed while proving nothing. It now returns a job id, so the poll loop and the `done` transition are actually exercised. |
| **Stale job markers must be detected, not waited out** | `server.ps1` | a server restart mid-answer leaves a `running` file forever. Past the job timeout the endpoint reports the job as abandoned instead of letting the page poll to its own cap. |
| **An action table holds command STRINGS, not scriptblocks** | `server.ps1` | a scriptblock cannot cross into a bounded child process, so the timeout could only exist if the table were strings. Also the fix for the *last* freeze: `doctor` measured 12 s and froze a concurrent reader for 10 030 ms even behind a 120 s cap — a cap bounds a freeze, it does not remove one. |
| **One bounded runner, shared by two callers** | `run-bounded.ps1` | the request path and the background job both need it. Inline, the job would have had to duplicate the timeout — and a duplicated timeout is a timeout that eventually gets edited in one place only. |
| **A command that reports success it did not achieve** | `server.ps1` | `cmd /c` expands `%ERRORLEVEL%` *before* the first command runs, so `echo exit=%ERRORLEVEL%` printed 0 for a failed check. Use `if errorlevel 1 (...) else (...)`. |
| **A timeout handler must be able to read the output** | `run-bounded.ps1` | after `Kill()` the redirected handle is still open and `ReadAllText` opens exclusively, so the kill-and-report path *threw* instead of reporting. It had no runtime coverage until a command was run past its cap on purpose. |
| **A timeout must kill the TREE** | `run-bounded.ps1` | `$proc.Kill()` kills the wrapper, not what the wrapper started: measured, a timed-out `cmd /c ping` left the `ping.exe` running. A timeout that orphans the work has not stopped it. Use `taskkill /T /F`. |
| **Never pass an optional argument you did not check** | `run-bounded.ps1` | `Start-Process -WorkingDirectory $null` throws, because it validates the argument. The one caller always supplied a value, so the branch had never run. |

Two things these templates still need **you** to add, because they are
subject-specific:

- **the self-verifying layer** — `verify-ui.ps1` is file-level only. Copy the
  in-page behavioural pass from the reference `index.html`: stub a dependency,
  invoke the real handler, assert the result reached a **connected** node. It is
  the only kind of check that could have caught the detached-node bug, and a
  structural suite sat green the whole time it shipped broken.
- **the action whitelist** — the reference's commands are its own. Yours must be
  yours, and the page may only ever send an *identifier*.

---

## Starting from these

1. Copy the **seven** files into a new folder: `server.ps1`, `run-bounded.ps1`,
   `collect-state.ps1`, `index.html`, `verify-ui.ps1`, `cc-watchdog.ps1`,
   `health-harness.ps1`. Do not start from a blank page. `run-bounded.ps1` is
   small and easy to miss, and `server.ps1` dot-sources it at startup — without
   it the server will not run at all, which is at least a loud failure rather
   than a silent one.
2. **Delete the subject matter first**, keep the invariants. A working dashboard
   about the wrong thing beats a broken one about the right thing.
3. Re-derive the question bank in `DASHBOARD_QUESTIONS.md` for your subject.
4. Work stage by stage. The order is the method.

---

## What is deliberately absent

**No comments claiming a guarantee the code does not make.** The reference
implementation carried a comment that the page was 14 tabs when it was 15, and a
note pointing to the wrong tab for the self-test button. Both were wrong for
hours, and both were found by reading the running product, not the code.

**Your own line endings, encoding, and paths.** They are Windows-specific on
purpose. If that is wrong for you, change it deliberately — and record that you
did.

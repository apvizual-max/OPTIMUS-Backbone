# PROCESS TREE

**What runs what, who starts it, who restarts it, and what happens when it dies.**
Built from the measurement, not from intent — the only reliable source.

---

## The shape

```
 machine boot
     │
     ▼
 scheduled task  (logon trigger)          ← survives reboot
     │
     ▼
 SUPERVISOR
     │  every 30 s:  is the port answering?
     │               is the page parsing?
     │               is the data fresh?
     │
     ├── unhealthy × 3 ──────────────► start the server
     │                                   (never "repair" — only restart)
     │
     ▼
 SERVER  (loopback only)
     ├── background refresher ──► COLLECTOR ──► atomic write ──► state file
     │
     ├── GET  /            ──► the page
     ├── GET  /api/state   ──► read the state file.  NEVER collect.
     └── POST /api/action  ──► whitelist lookup ──► run ──► capped output
```

---

## Ownership, restated as rules

| Thing | Started by | Restarted by | If it dies |
|---|---|---|---|
| supervisor | scheduled task, at logon | the task | nothing restarts the supervisor — **it is the top** |
| server | supervisor | supervisor, after 3 strikes | console is dark until then |
| collector | server (refresher) or an action | the next cycle | last good state is served, marked old |
| state file | whoever collects last | next write | **atomic rename — never a partial read** |
| page | the human's browser | their browser | nothing; it is static and self-contained |

---

## Kill semantics — the part that bites

**A parent death does not take its children with it.** On Windows, killing the
supervisor leaves the server; killing the server leaves a live refresher and any
collector in flight.

Every process tree therefore needs an explicit sweep, and the sweep must be
**iterative**: killing an orphan reparents its live children onto nothing, which
makes *them* orphans. One pass leaves most of the tree behind. This was written
into the worked example's own reaper after a first version got it wrong.

**And a filter is a policy decision.** The reaper searched for `node.exe` because
that is what it was built to find — and therefore could never reclaim the
`chrome-headless-shell` children holding 3 GB. A correct filter for the question
asked is a silent failure for the question not asked.

> **Before you reap, state what you are not reaping.** The worked example's reaper
> now reports both: what it will take, and the 3 GB it structurally cannot reach.

---

## Reboot

Logon trigger, not a startup trigger. The difference matters: a startup task runs
before the user's session, before the network, and before the things it is
supervising exist. A logon task runs when a human is present — which is exactly
the condition under which "show me the dashboard" is meaningful.

The worked example's task ran the supervisor, which ran the server. The console
came back on its own, with nothing asked of anyone.

---

## What this tree must never contain

- **A mutating command reachable from the page.** Actions are an identifier
  resolved server-side; the page never sends a command.
- **A restart that repairs.** The supervisor restarts. It does not fix. A process
  that needs repair will fail again, and a supervisor that "fixes" is a supervisor
  that hides the fault.
- **A dependency on something that starts later.** If the dashboard needs the
  thing it is watching, it is not supervising; it is waiting.
- **A process that is killed and assumed dead.** Verify by evidence — a log line,
  a port, a liveness probe — never by the fact that the kill returned.

---

## The cost this tree imposes

Every process here consumes something on the machine it observes. Write the
numbers down, because they are part of the design and not a detail:

- refresh worker + collector: **one measurement per cycle, forever**
- the page: one request per poll, per open tab
- backups: bytes copied, at checkpoints
- the reaper, the self-test, the AI: each a burst, each spawning processes

**A dashboard that degrades the machine it watches is a dashboard with a
countdown.** The worked example discovered this the hard way: 130 stray processes
accumulated, RAM fell to 13.7 GB of 63.9, and a 30 MB backup was measurably
stalling the console it was protecting.

# STRATEGIC TREE

Why this system exists, what it is accountable for, and what it is explicitly
**not** allowed to become. Written for a reader who has never seen the project.

## The one sentence

OPTIMUS is a single-machine operations console for a 58-container AI swarm that
several agents (Mavis, Hermes, Antigravity, Qwen) share — and its hardest job is
not displaying numbers, it is **being honest about them**.

## Why it exists

| Pressure | What it produced |
|---|---|
| 31 `hermes-mcp-*` containers are irreplaceable; one was lost to a prune on 2026-08-08 | `cc guard`, the standing "NEVER prune" warning, the `apviz` orphan guard |
| `docker-compose.yml` vanished once and took 6 non-swarm containers with it | `guard-compose.ps1` rebuilds it from live state |
| Hermes self-updates, so version facts go stale on their own | the Update tab, and `OPTIMUS_CURRENT_STATE.md` generated from measurement |
| A plain metrics grid answers "what" and never "what changed" or "is this normal" | server-side history, median-baseline anomaly detection, incident correlation |
| Eighteen real bugs in this system were **silent** — green output, wrong behaviour | every design choice below that favours "say so" over "look fine" |

## The three commitments

1. **Never lie to look healthy.** A stale number is labelled stale. A failed
   probe is reported as a failed probe. The chart that once claimed `▲ +57` on a
   flat series is the canonical example of what this project refuses to do.
2. **Additive over clever.** Every change is a new layer; existing behaviour is
   never edited out to make a change simpler. Removal is damage.
3. **Self-reporting.** The console reports on its own survival, because a console
   that died silently for 19.5 hours is the failure mode this project exists to
   prevent.

## Where it sits in the swarm

```
        Popy  (operator, Romania — the only human in the loop)
          │
          ├── OPTIMUS Control Center  :8900   ← this project. The single pane.
          │        │
          │        ├── reads ─→ live state written by the collector
          │        ├── reads ─→ cc-health.json written by the supervisor
          │        └── calls ─→ MiniMax-M3 for the AI Analyst
          │
          ├── Hermes  (orchestrator, self-updating, 9 profiles)
          ├── Antigravity  (peer backbone, read-only mount into the bridge)
          ├── Qwen Studio  (ACP transport, model provider is the blocker)
          └── Docker  (58 containers, the substrate everything runs on)
```

## What this is NOT

- **Not a MiniMax product.** It runs on plain PowerShell + a static page. It does
  not require the MiniMax agent runtime, and the page works with the agent closed.
- **Not an observability platform.** No Prometheus/Grafana stack, no SaaS, no
  remote ingest. Loopback only, one machine.
- **Not a place to make changes.** It is a place to *see*, plus a cockpit for the
  handful of commands that are safe to run from a button. Everything else stays
  in a shell.
- **Not a source of truth for Hermes' own health.** It reports what it can
  measure and says `unknown` when it cannot.

## Success criteria, stated plainly

A new operator should be able to open `http://127.0.0.1:8900/` cold, with no
context, and within 60 seconds know: is the swarm whole, is anything broken, what
changed recently, and what should I look at first. If the page is stale, it must
say so before it says anything else.

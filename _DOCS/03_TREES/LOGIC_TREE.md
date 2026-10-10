# LOGIC TREE

The decision logic. What the system *concludes* from what it *measures*, and the
rules that keep it from concluding something false.

## The measurement → conclusion chain

```
measurements (collector, ~18 s)
  │
  ├─ docker ps / inspect ─────────► containers.total, by_project, compose_present
  │                                  compose_valid
  ├─ :8801/:8802 /health ────────► bridge.up, uptime, role
  ├─ :8801/:8802 /doctor/detailed ► health, ok/warn/fail counts, per-check detail
  ├─ service probes ─────────────► up, http status
  ├─ mcode-tools auth status ────► cli_auth (authenticated | unavailable)
  ├─ mcode-tools connector tools ─► connector tool count
  ├─ git in the Hermes checkout ──► head, modified_count, dirty
  │
  ▼
live-state.json   (atomic write; the server only ever READS this)
  │
  ├─▶ /api/state ──► every tab
  │
  └─▶ history append
        │
        ├─ RULE: append ONLY when a tracked value CHANGED
        │        (excluding the timestamp, which is regenerated every run —
        │         including it made every sample look like a change)
        │
        ├─ RULE: MEDIAN baseline, never mean
        │        one spike must not drag the baseline and then hide behind it
        │
        ├─ RULE: anomaly = |value − median| / median ≥ 10%
        │
        └─ RULE: incidents are TRANSITIONS, not states
                 record what moved at the moment it moved, and what else
                 moved in the same window
```

## Health logic (the supervisor)

```
Test-Health
  ├─ TCP connect :8900            fail → unhealthy("port not accepting")
  ├─ GET /api/state (60 s cap)    fail → unhealthy(error text)
  ├─ served state younger than 300 s?
  │     no  → unhealthy("served state is N min old - the refresher is wedged")
  └─ yes → healthy(age)
          │
          ▼
    3 CONSECUTIVE failures before acting
          │
          ├─ 1 failure  → log "not acting yet". A single slow check is NOT a
          │               dead server: one collect touches 58 containers, two
          │               bridges and two CLIs, and can exceed a minute.
          │
          ├─ after a restart → 150 s grace before judging again
          │                    (reading a healthy server's startup as failure is
          │                     a watchdog destroying what it protects)
          │
          └─ acting → Stop-Stale, then Start-Server, then record the reason
```

## Staleness logic (never present a stale number as current)

| Condition | What the UI does |
|---|---|
| state younger than 20 s | green: `live HH:MM:SS · 4s old` |
| 20 s – 180 s | amber: `stale` dot, pulsing slowly |
| older than 180 s | red: `down` dot |
| collector timed out | serves **last known good**, flagged `stale: true` with a reason |

A dead dashboard tells you nothing. A stale one tells you something.

## Presentation rules (the design system's load-bearing ones)

```
Type scale  ratio 1.25  ─► body 15px · h2 19px · KPI 30px · caption 12.5px
                          never below 14px for body — five sources agreed
Measure                  capped at 72ch (research: 45–75ch)
Elevation                depth by SHADOW + hairline, never by nested borders
Accent                   3px left chromatic bar, per-card colour
Boxes                    no boxes inside boxes
Motion                   entrance animations fire ONCE, not on every poll
Stagger                  first 9 cards only
prefers-reduced-motion   honoured by name, not just by wildcard
```

## What is deliberately NOT automatic

| Decision | Why it stays human |
|---|---|
| dropping a version baseline | redundancy is not waste; identical snapshots mean a **stable build** |
| `hermes update` | Popy reserved it for himself; Mavis has never run it |
| pruning containers | lost the swarm once on 2026-08-08 |
| repairing compose | only ever *reports*; `cc guard` acts when a human asks |
| removing anything from the console | every removal so far has been damage |

## Icon system logic

Tabler Icons 3.48.0, MIT, 5,229 glyphs on one 24px grid — chosen because the
research converged on it for dashboards specifically. Six obvious names do not
exist and would render as blank boxes:

| Guessed | Does not exist | Real substitute |
|---|---|---|
| `ti-bridge` | ✗ | `ti-affiliate` |
| `ti-layers` | ✗ | `ti-stack-2` |
| `ti-info` | ✗ | `ti-help-circle` |
| `ti-play` | ✗ | `ti-player-play` |
| `ti-cpu-core` | ✗ | `ti-activity` |
| `ti-waves` | ✗ | `ti-heartbeat` |

The original hand-drawn `IC` map is retained and still drives the in-card
key/value glyphs; a blank box that looks fine in a screenshot is exactly the
failure this check exists to prevent.

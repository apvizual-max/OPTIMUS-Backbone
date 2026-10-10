# ARCHITECTURE

The five-piece shape, the contracts between them, and the failure each piece is
responsible for absorbing. Scope changes; the shape does not.

---

## The five pieces

```
   system under observation
          │
          │  stdout, one JSON blob, nothing else
          ▼
   ┌─────────────┐
   │  COLLECTOR  │  measures. prints. does not serve, store or render.
   └──────┬──────┘
          │  JSON
          ▼
   ┌─────────────┐
   │   SERVER    │  writes the JSON atomically; serves the file.
   └──────┬──────┘  also serves the page, and returns JOB IDS for slow work -
          │         the analyst and every action - instead of their results.
          │  GET /api/state  — milliseconds, read-only
          ▼
   ┌─────────────┐
   │    PAGE     │  one HTML file. renders what it is given.
   └──────┬──────┘
          │  port · parse · freshness
          ▼
   ┌─────────────┐
   │ SUPERVISOR  │  keeps the server alive across crashes and reboots.
   └─────────────┘
```

---

## Contracts

These are the agreements that make the whole thing hold. Break one and the
symptom appears somewhere else entirely.

### C1 — The collector has exactly one output and no side effects

One process. One JSON blob on stdout. No HTTP, no files, no database, no state.

**Why:** it is the only piece that can be run in a terminal and believed. The
worked example's collector is ~47 KB of PowerShell whose entire output can be
piped to a file and read. When the system's behaviour was surprising, that was
where the surprise was found.

**Corollary:** if the collector starts serving, it is no longer a measurement and
can no longer be trusted as one.

### C2 — The state file is written atomically, always

Write a sibling temp file, then `Rename-Over`. Never in place.

**Why:** a reader catching a half-written file sees truncated JSON, and
truncated JSON is indistinguishable from corrupt data. The refresh worker and the
request handler both write it, so they also need different temp names.

### C3 — A request path must be UNABLE to start a measurement

The refresh worker keeps the cache warm. A request reads the cache and returns.

**Why:** on a single-threaded listener, a request that starts a measurement
freezes *everybody* for its full duration. This is the single most expensive rule
in the architecture. The worked example violated it for months, and the fix that
finally held was to make the request path **read-only**, not to make it rarer.

**Corollary — and this is where people get it wrong:** the threshold is not the
lever. The intuitive repair is to raise "is this cache too old?" until the budget
exceeds one measurement cycle, so fewer requests fall into the collect path. That
was tried on the worked example and it **made things worse**: past the new limit
every request collected inline, which starved the refresh worker, which left the
cache permanently stale — and the endpoint began returning a **zero-byte body**.
Starving the worker starves the cache, and a longer threshold buys the request
path exactly the thing it was supposed to avoid.

So the constraint is **structural, not numerical**: the request path must have no
way to start a collect at all. `Get-StateJson -MaxAgeSec -1` is read-only — it
serves whatever the refresher last wrote, however old — and age stops being a
trigger for work. Dead-worker recovery does not disappear; it moves up a level,
where it belongs: the supervisor fails the server when the served state passes
`MaxStateAgeSec` and restarts it, and the page shows `stale` at 60 s / `down` at
180 s.

**The trap in implementing it:** `-1` only means "read-only" if the *function*
tests for it. If the guard is `$MaxAgeSec -gt 0`, then `-1` falls through to the
collect and you have made the freeze permanent and unconditional. Add the mode
where it is tested, not only where it is passed.

### C4 — The page renders what it is given, and nothing it is not

No inference. No smoothing. No "probably". If the measurement did not say, the
page does not show.

**Why:** the page is the only part a human trusts without checking. The moment it
fills gaps, it becomes a rumour.

### C5 — Failure results carry *which* failure

`null` is not a report. A failure must distinguish **down / slow / late / stale /
absent / never-loaded**, because those have different remedies and different
urgency.

**Why:** the worked example rendered a bridge that was *down* and a bridge that was
*healthy but answering 8.5 s* identically, as `unknown · 0/0/0`. The operator's
instinct is then to restart a service that is working.

### C6 — The dashboard states its own freshness, always

Data age on screen, next to the data. Not in a tooltip. Not on hover. Visible.

### C7 — Zero external resources, asserted by a test

Everything the page needs is served from beside it, including fonts. The check is
part of the self-test, so it cannot regress unnoticed.

**Why:** a dashboard that needs the internet cannot help the person whose
connectivity is part of what is broken.

---

## The refresh budget — the number that shapes everything

Before writing code, multiply:

```
measurement cost  ×  refresh interval   =   duty cycle
```

If the product is at or above 1, **the design is already saturated** and the
operator will feel it as intermittent freezing. In the worked example:

```
collector cost  ~22 s     ×    interval  20 s   =   1.10
```

Saturated. The consequences were predicted in stage 3, observed for hours, and
the obvious fix — raising the cache threshold — was tried and **reverted**, because
it starved the refresh worker and returned zero bytes.

**The correct fix is architectural, not numerical:** make the request path unable
to start a measurement at all, and let the refresh worker own the timing
entirely. Decide this in stage 3. Discover it in production and you pay twice.

**Now shipped in the worked example** (see C3): every request path is read-only,
and every slow path returns a job id. With the state file deliberately backdated
past the old trigger, so the previous code would have collected on each of those
requests: 5 requests at 200 s age → max 182 ms; 8 concurrent → max 350 ms; 30
steady-state → max 614 ms; zero non-200. During a 41.7 s action, 98 concurrent
probes returned p50 14 ms, max 358 ms, zero errors - against a 12 ms idle
baseline. The duty cycle is still 1.10 - the collect was never made cheaper - but
no request can join it.

---

## Failure ownership

| Piece | Absorbs | Must never |
|---|---|---|
| collector | a missing or slow subsystem | block forever — every call needs its own budget |
| server | a slow or absent collector | make a request wait on a measurement or a subprocess |
| page | stale data, partial data, absent data | invent, smooth, or guess |
| supervisor | a dead process | restart something healthy, **or kill something it does not own** |
| self-test | nothing — it *reports* | pass on broken code |
| any measurement | nothing | render a value it did not finish measuring |

That last row is the one that keeps being re-learned. A bounded measurement that
reports a partial result as a complete one is worse than an unbounded one,
because it is confident. `total = null, timed_out = true` is the honest shape.

A supervisor's kill scope is a **blast radius**, not a convenience. The worked
example shipped for hours with `CommandLine -like '*server.ps1*'`, which matched
every server on the machine, and killed an unrelated, unsupervised service the
first time it restarted. Nothing restarts what nothing supervises, so the damage
was permanent rather than transient. Scope a kill to the exact thing you own.

If a failure reaches the operator unabsorbed, it is a design gap, not bad luck.

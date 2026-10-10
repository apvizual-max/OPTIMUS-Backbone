# DESIGN LANGUAGE

A dashboard is read at 3 a.m. by someone tired. Every choice below follows from
that, and from one demand: **the eye must find the bad thing first.**

---

## The one rule

> **Colour is reserved for meaning. Everything else is neutral.**

The worked example's accent colours are per-entity identity (each tab, each service
carries a stable accent), and severity is a separate, small vocabulary. If
everything is coloured, nothing is.

---

## Palette

A dark surface is the default — long sessions, low ambient light, and the panels
are the only light source.

| Role | Purpose |
|---|---|
| `--bg` | deepest ground |
| `--surface` | card background |
| `--surface-2` | nested panel, table stripe |
| `--border` | hairlines. Quiet. Structural. |
| `--text` | primary |
| `--text-dim` | secondary, labels, units |
| `--st-ok` | good, answering, verified |
| `--st-warn` | degraded, late, needs an eye |
| `--st-bad` | down, failed, needs a hand |
| `--st-unknown` | **not the same as bad** — unmeasured, stale, absent |

**`--st-unknown` must exist as its own colour.** This is the single most important
entry in the table. If "we don't know" is rendered as "bad", the operator learns to
distrust the whole panel. A dashboard that admits ignorance is more useful than one
that is confidently wrong.

**A light theme is a first-class peer**, not an afterthought — a console that is
unreadable in daylight is unreadable. The worked example ships both, with a
persisted toggle and an icon that reflects the current state.

Accent hues (one per entity) are chosen for **distinguishability at small size in
both themes**, not for prettiness. Two adjacent tabs must never share a hue.

---

## Type

A **modular scale** (ratio ≈ 1.25), not arbitrary sizes. Every font size is a step
up or down from a base. If a panel needs a size not on the scale, the design is
wrong, not the scale.

| Step | Used for |
|---|---|
| base (≈15 px) | body text. The worked example moved 12 → 15 for exactly this reason. |
| −1 | units, metadata, "of 8s budget" |
| −2 | labels, column heads, hints — never below legibility |
| +1, +2 | panel titles, the one number that matters on a screen |
| mono | every identifier, port, path, duration, hash, command |

**Everything an operator would copy gets monospace.** Names, ports, commands, PIDs.
A container name in a proportional face is a name that cannot be selected cleanly.

**Numbers are tabular.** Columns of changing numbers must not shimmer on every poll.
The worked example's chart history resets its layout constantly; fixed-width digits
are the fix.

---

## Density

The system is scanned, not read. Density is a feature; whitespace is for the one
thing that matters.

- **Cards in a responsive grid**, not a single column. Two to four across.
- **Key–value rows** for structured facts, with the key dim and the value bright.
- **A card's title is a question it answers.** "What breaks if this dies", not
  "Status".
- **A panel that needs scrolling to be understood has failed**, unless it is
  explicitly a drill-down.

---

## The card, the note, the pill

**Card** — one idea. Title states what it answers. A one-line subtitle says why it
matters. Accent colour identifies the entity.

**Note** — a judgement the dashboard makes *on the human's behalf*, with its
reasoning attached. This is the spark, and it must be rare enough to be read.

> *"NEVER run: `docker container prune -a` — the swarm was lost that way."*
> *"Restarting the bridge will not help — it is healthy and slow."*

A note without a remedy is nagging. A note that prescribes the wrong action is
worse than silence.

**Pill** — a compact status in the header. Three maximum: freshness, health,
watchdog. Anything more belongs on a panel.

---

## State vocabulary

Every status must be one of these, and they must look different:

| State | Means | Colour |
|---|---|---|
| **OK** | measured, within budget | good |
| **WARN** | answering, but late or degraded | warn |
| **BAD** | not answering | bad |
| **STALE** | data is old, the source may be fine | dim + age |
| **UNKNOWN** | never measured / not measurable here | dim, no age |
| **CHECKING** | in flight, say how long it has been | dim |

The worked example shipped a dashboard where **DOWN** and **ANSWERED LATE** looked
identical. The fix was to give the failure result a vocabulary. **Design the
vocabulary before you need it** — retrofitting it means changing every panel.

---

## Motion

- **Entrance animations play exactly once.** A re-render every few seconds that
  re-triggers an animation makes the page pulse forever, which is a bug that reads
  as noise.
- **No layout-shifting motion.** Data arriving must not move what the eye is
  already reading.
- **State changes are instant.** A spinner is information; a fade is decoration.

---

## The spark

Everything above is competence. The spark is a single move:

> **Have the dashboard form an opinion, and show its reasoning.**

Not "Bridges: 1 of 2 degraded". But: *"hermes-bridge answered 8.5 s against an 8 s
budget — it is up, it is slow, and restarting it will not help."*

That is the difference between a report and an instrument. It costs one rule —
**never form an opinion you cannot back with a measurement the human can re-derive**
— and it is the thing that makes the console worth trusting at 3 a.m.

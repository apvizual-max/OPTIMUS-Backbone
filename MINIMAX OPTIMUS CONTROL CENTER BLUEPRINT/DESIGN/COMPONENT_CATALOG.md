# COMPONENT CATALOGUE

The parts, what each is for, and the failure each one must not have. Build these
first; everything else is arrangement.

---

## Status

**`pill`** — compact header status. Three only: freshness, health, watchdog.

*Must not* become a fourth. A header that scrolls is a header nobody reads.

```
 live 14:02:11 · 22s old ●        supervisor — ●
```

**`dot`** — a status colour with no text. Only ever as a *redundant* cue beside
text that already says the same thing. Never alone.

**`chip`** — a small labelled fact: `hermes-mcp: 31`, `warn 2`.

---

## Data display

**`kv`** — key/value row. Key dim, value bright, value in mono when it is an
identifier. The workhorse. Two per line on a wide card.

*Must not* print a value with no denominator. `7` is noise; `6 of 7 answering` is
information.

**`table`** — many entities, identical columns. Sticky head. Clickable rows for
drill-down, and **the click target is a real element**, not a hover.

*Must not* be the primary display for one entity. A one-row table is a bug.

**`sparkline`** — history in a few pixels. For a value that changes and the shape
matters.

*Must not* smooth. If the series is flat, say flat. A median that hides a
seventeen-to-one spike is a lie with a chart around it.

**`area chart`** — history with an axis. Label both ends. The current value is a
readable number, not a point on a line.

**`heatmap`** — activity by day. Severity is the **worst** thing that happened,
never the average. Averaging a day with one failure among seventeen healthy ones
hides the failure — which is the entire reason the chart exists.

---

## Judgement

**`note`** — the dashboard's opinion, with its reasoning and its remedy attached.

```
 ⚠ Answered late, not down.
   The bridge replied in 8029 ms against an 8s budget, so the probe gave up
   before the answer arrived. Restarting the bridge will not help — it is
   healthy and slow.
```

This is the component that makes a dashboard an instrument. Rules:

- **Rare.** If everything is noted, nothing is.
- **Specific.** A number and a comparison, not an adjective.
- **Actionable.** It says what to do *and* what not to do.
- **Backed.** Every claim in it must be re-derivable by the human from the
  dashboard itself. An opinion the operator cannot check is a rumour.

Variants: `info` (neutral orientation), `warn` (needs an eye), `bad` (needs a
hand).

---

## Action

**`button`** — one verb. Verb-first label: `Run the check`, `Re-validate`.

**`action row`** — a whitelisted command with its result. The row always shows:

- the command text, before and after,
- whether it succeeded,
- how long it took,
- whether the result is still there.

**Never** send a command from the page. Send an **identifier**; the server holds
the command. See `../PROCESS/04_BUILD.md` — "The actions boundary".

**`terminal`** — an interactive shell is a remote execution surface. Only if
asked for, only behind the same whitelist, never as a default.

---

## Structure

**`tab`** — a whole subject. One card's worth of content, not a page. Tab order is
*the order a person would investigate*, not alphabetical.

**`drill-down`** — click a row, learn one thing, in place. No navigation.

**`command palette`** — keyboard, fuzzy, the power user's path. `Ctrl K`. Ranks
tabs, actions and jumps; runs the highlighted one on Enter. Keyboard-first, because
the fastest route to a thing should not require the mouse.

**`note strip`** — a persistent caution, at the top of the thing it protects.
"Never run `docker container prune -a` — the swarm was lost that way." This is the
one piece of text that must never be dismissible.

---

## The self-test card

Lives on a panel. Reports **its own run count and timestamp**, and distinguishes:

- **structural** — is the script running, do the tabs render, do icons paint, is
  the font loaded, are there zero external resources, is the data fresh, is every
  control wired;
- **behavioural** — *run a real handler with a stubbed dependency and assert the
  result reached a connected node.*

The second is the one that matters and the one everybody omits. A structural pass
stayed green for hours while a headline feature had never once worked.

---

## The one-line rule for adding a component

> **Does this help a tired person find the bad thing faster?**

If not, it is decoration, and the dashboard is already dense enough.

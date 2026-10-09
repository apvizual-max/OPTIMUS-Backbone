---
name: mavis-hermes-design-sot
description: Use when building or restyling ANY user-facing surface for Popy — dashboards, HTML, panels, cards, buttons, tabs, legends, or any MiniMax-side UI that should match the Hermes ecosystem. Also use when asked to make something "look better", "match Hermes", or to restyle an existing Mavis deliverable without breaking its functionality. Triggers on "design makeover", "make it look better", "match the Hermes style", "apply the design system", "restyle", "colour scheme", "UI polish".
---

# mavis-hermes-design-sot

The design core. One reference, applied everywhere, so a new surface looks
born next to the old one instead of bolted on.

## The single source of truth

**`C:\Users\apviz\AppData\Local\hermes\desktop-plugins\design-system\Design_Schema\`**
Theme: **"Obsidian Telemetry Dark (Living Master SOT)"** by Nous Research & Antigravity AI.

> **This directory is a treasure. NEVER write, edit, move, delete or rename
> anything in it.** Popy works in it personally during special sessions. A
> read-only working copy lives at `projects\95_DESIGN_SOT\` — build against that.

## The eight chromatic tokens

| Token | Hex | Domain |
|---|---|---|
| cyan | `#22d3ee` | Coding & Antigravity |
| emerald | `#34d399` | Running & Gordon AI |
| purple | `#c084fc` | Databases & Qwen Local |
| amber | `#fbbf24` | Reasoning & Warnings |
| pink | `#f472b6` | Vision & Mavis AI |
| blue | `#60a5fa` | Workspace & Host Tools |
| orange | `#fb923c` | Observability & Speed |
| indigo | `#818cf8` | Host System & FS |

Status matrix: active `#ef4444` · ok `#22c55e` · paused `#eab308` ·
waiting `#f97316` · done `#9ca3af` · wait `#06b6d4` · cleared `#6b7280`.

Surfaces: base `rgba(0,0,0,0.30)` · elevated `rgba(18,20,26,0.78)` ·
drawer border `rgba(255,255,255,0.07)` · subtle `rgba(255,255,255,0.04)`.
Elevation shadow: `0 4px 16px rgba(0,0,0,0.25)` — **no inset highlight lines**.

## The seven invariants — break none of them

1. **Maximum 3 font families, strictly.** sans = `system-ui…`; mono =
   `ui-monospace…`; display = `'Trebuchet MS'…`. A fourth family is a bug.
2. **3px LEFT chromatic accent** on every card, with **18px/22px negative-space
   padding** so the accent never crowds the text.
3. **No boxes inside boxes.** Metadata rows are separated by space, not by
   nested borders or inner rules.
4. **Rule 07 — border disappearance.** Layout containers use `border:0` /
   transparent. No harsh visible bounding strokes. Elevation is seamless.
5. **Action cockpit: single row, button strictly on TOP, text UNDERNEATH.**
   Button, then title, then a plain-English description, then the exact command
   so the operator can re-run it by hand.
6. **Every surface explains itself.** A person must be able to read the screen
   and know what it is, what it does, and what to do about a problem — without
   asking.
7. **Dividers are eliminated.** Use negative space and `•` rhythm, not
   horizontal rules.

## How to restyle without breaking anything

This is the part that goes wrong most often.

- **Snapshot first.** Capture the working version before touching it. In the
  Control Center that is `90_CONTROL_CENTER\bat\manage-versions.ps1`; it caps
  at five and refuses the sixth rather than auto-deleting, because Popy decides
  when a baseline dies.
- **Preserve behaviour byte-for-byte.** A makeover changes CSS and adds copy.
  It must not rename a route, drop a poll, reorder a tab, or change an action
  id. Prove it afterwards: click every tab, click every button, assert no
  `undefined`, no `NaN`, no raw markup, no mojibake.
- **Verify in a real browser.** `chrome-devtools` → `take_screenshot` plus
  `evaluate_script` reading the rendered DOM. A `200` from the API proves the
  server answers, not that the page renders. Do not report a UI as working
  before this.

## Reference implementations

- **Control Center** — `projects\90_CONTROL_CENTER\index.html`. The fullest
  example: per-tab accent colours, page headers that state the question each
  tab answers, card sub-titles, and a 14-button action cockpit with title,
  description and command line under every button.
- Design schema and replication guide: `projects\95_DESIGN_SOT\`.

## What NOT to do

- Do not invent a palette. Use the eight tokens; they encode domain meaning.
- Do not add a fourth font family "just for a heading".
- Do not add hard 1px borders to make things look "defined" — that is the
  failure mode Rule 07 exists to prevent.
- Do not edit the Hermes design-system directory itself. Ever.

# Design App Integration — PLACEHOLDER ONLY

**Date:** 2026-10-05
**Status:** 🔵 PLACEHOLDER — designed, deliberately not built
**Directive:** Popy, 2026-10-05 — *"leave it separate; we will add it later into the
system as a plugin… Just design the spot, make a placeholder."*

This document is the spot. It is not a plan of record, not a partial build, and not a
scaffold with stubbed functions. Nothing here has been wired, and nothing here claims
to work. If a future session reads this file and finds it wants to start writing code,
it should re-read this section first.

---

## 1. What is actually installed (measured, 2026-10-05)

Install root: `C:\Users\apviz\AppData\Local\Programs\MiniMax Design\` — **present.**

| Probe | Result |
|---|---|
| `%LOCALAPPDATA%\Programs\MiniMax Design` | EXISTS |
| `%APPDATA%\MiniMax Design` | **ABSENT** |
| `%LOCALAPPDATA%\MiniMax Design` (user data) | **ABSENT** |

Both user-data directories are absent, so **the app has never been run on this
machine.** It has no settings, no session history, no plugin state, and no user
assets. Every runtime behaviour of this product is therefore `NOT_MEASURED` — not
"probably fine", not "standard", *unknown*. The distinction matters: the install tree
is evidence that the product exists, and it is not evidence of anything it does.

## 2. What it ships — the real tree

`…\current\resources\agent-profiles\v2\config\`

```
agents/      executor.md      20,650 B     media-agent.md  33,519 B
             planner.md       12,279 B     router.md        3,321 B
contracts/   semantic-judgment.md  15,654 B
             canvas-grouping.md     2,939 B
             canvas-discipline.md   2,558 B
             baseline.md             1,617 B
             anti-loop.md            1,228 B
             README.md               4,543 B
knowledge/   failures/  image-recipes/  vendors/
plugins/     (present, contents not yet inspected)
workflows/   ad-tvc/  drama-series/  mv/  _shared/  _disabled/
```

**Correction worth keeping:** the agent profiles are in **`config/agents/`**, not
`config/profiles/`. An earlier note in this project placed them in `profiles/`. That
path does not exist. The names were right and the path was wrong, which is the most
expensive kind of error to carry forward.

The four agents are a real division of labour, not decoration: `router` dispatches,
`planner` decomposes, `executor` acts, `media-agent` handles assets. The contracts
above them are behavioural rules, and `canvas-discipline.md` / `canvas-grouping.md`
describe how visual work is bound into a canvas. `workflows/ad-tvc/` and
`workflows/drama-series/` are domain playbooks. This is a mature, opinionated
product — which is precisely why guessing at its interface would be expensive.

## 3. The designed spot

**Integration surface: a plugin, in `…\v2\config\plugins\`, registered with the
`mcode` CLI that now exists on this machine.**

The reasoning is that this is the only seam where SENTINEL can join without
disturbing what the app already does:

- **Not a wrapper.** Wrapping the Design app would fork a product that already ships
  its own agents. Two orchestrators over one canvas is the failure mode, not a
  feature.
- **Not a shared file store.** Design owns its canvas; SENTINEL owns doctrine. They
  do not need to agree on document format to trade capabilities.
- **A plugin** gives one-directional entry: SENTINEL hands work in and receives
  results out, while the app remains the single owner of its own state.

Concretely, when this is ever built, the plugin would need to do three things and
nothing else:

1. **Accept a task** in SENTINEL's own vocabulary — a brief, not a prompt, because
   `planner.md` already decomposes and a re-phrased prompt fights that contract.
2. **Report measured outcome** — artefact paths and a status — never a self-declared
   "done". This is the SENTINEL rule that survives contact with any external system.
3. **Stay silent about the rest.** SENTINEL has no business managing canvas grouping
   or token pipelines it cannot observe.

## 4. Preconditions that do not exist yet

Listed so a future session does not mistake a placeholder for progress. None of these
are met:

- [ ] The app has been **launched once**, creating its user-data directories.
- [ ] `plugins/` contents have been **read**, so the real plugin contract is known
      rather than assumed.
- [ ] `canvas-discipline.md` and `canvas-grouping.md` have been **read**, so SENTINEL
      does not violate a canvas rule by handing work in wrongly.
- [ ] A **credential path** is known and owned. Design has no API key today, and one
      must not be improvised from the existing `MINIMAX_API_KEY` without deciding
      whether Token Plan and Design billing are meant to be the same account.
- [ ] Popy has given R0 for the build. He has **not**, and has explicitly deferred it.

## 5. What this placeholder is not

- It is not a stub. There are no empty functions waiting to be filled in.
- It does not touch the Design install tree, and it does not launch the app.
- It does not register anything in `C:\Users\apviz\.minimax\mcp.json`.
- It does not claim the app works, because **it has never been run**.

The honest summary: the integration point is identified and named, the reason for
that choice is written down, and the work has not been started — on purpose.

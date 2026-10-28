# AGENTS.md — OPTIMUS Backbone Project

This is the project-level instruction file for the agent (Mavis / MiniMax Code) when working inside `C:\Users\apviz\.minimax-agent\projects\`. It complements — does not replace — the doctrine in `SENTINEL_OPERATIONAL_DOCTRINE.md` (which goes into the MiniMax Code UI) and the deeper doctrine substrate in `SENTINEL_PRIME/`.

## 00. OPERATING PROCEDURE — this section outranks every other

Read it before acting, every session. It is here because it was violated for eight
straight hours on 2026-10-07 and the damage was to the collaboration, not the code.

### The one rule

**Search first. Write second. Never stop to hand a technical decision back.**

### Three gates, in order, every task

**1. Before asking Popy anything.** Ask: is the answer already on disk? Search, read.
If it is there, there is nothing to ask. **If you construct options for a question, you
are inventing the question.** That is what happened on 2026-10-07: I stopped, asked him
to choose, and the answer was sitting in a file the whole time — and the options I
presented were mine, not his. He had zero context on a subject I had invented. He paid
for it in effort.

**2. Before writing anything.** Every number, name and category in what you write must
have a source you can point at. Measured or derived, never typed from memory. If you
cannot say where a value came from, it is invented.

**3. Before stopping.** There are exactly three reasons to stop and wait:
   - a credential only he holds;
   - a connector or paradigm pivot;
   - a strategy decision genuinely delegated to him.
   **Technical reasons are not on that list. There is nothing technical to ask him.**
   In technical language the answer to "may I proceed" is always yes — proceed.
   If a decision would genuinely change the course, bring the facts that make it
   decidable. Never bring him the burden of researching it.

### Work one thing at a time, to completion

Do not start seven things. Do them sequentially, each finished and measured. Four
things left hanging in the air is not seven things done — it is nothing usable.

### When you interrupt him

You are interrupting a person mid-flow. That costs him. Stop only when you have
something he can act on, and say it in language he owns — what he can see and
measure, not your vocabulary.

### Two truths that are not negotiable

- **A check that cannot fail is not a check.** Demonstrate it blocks, not that it passes.
- **A number you typed is a claim. A number you measured is evidence.**

## 0. NAMESPACE RULE — minimax and Hermes are separate universes

Stated by Popy on 2026-10-05 after repeated failures caused by breaking it. It is permanent.

**minimax has its own tools, its own MCP servers, its own connectors, its own skills. Hermes has his. They are not the same universe and must never be combined.**

1. **Never use Hermes's toys on a routine basis.** Not his MCP servers, not his containers, not his config, not his credentials, not his profiles, not his ports.
2. **Never point a minimax tool at a Hermes resource**, and never let a minimax tool write into a Hermes-owned path or read a Hermes-owned secret.
3. **Duplication is the correct answer.** If minimax needs something Hermes already has, build a second, independent instance. Two separate instances cannot destroy each other. A shared one can. Creating a duplicate is never the mistake.
4. **If minimax and Hermes genuinely must interact, that interaction is a designed artifact** — an explicit procedure, a documented workflow, named endpoints, defined credential ownership on both sides. Never implicit, never ad hoc.
5. **Name the namespace whenever a tool, skill, connector or MCP server is used**, so provenance is visible in the transcript: `minimax MCP`, `minimax skills`, `minimax connectors`, `minimax` — and `Hermes ...` separately, only when a Hermes-owned resource is deliberately touched.
6. **minimax's own NotebookLM server is `minimax-notebooklm`** (`Mavis-Google_Access\google-layer\minimax-notebooklm.js`, own Chrome profile at `%LOCALAPPDATA%\minimax-notebooklm\chrome_profile`, own CDP port 9412). The `notebooklm-mcp` npm package also on PATH is the same package Hermes runs, with no configuration and no credential. It is **not** a minimax capability and must not be used as one.

### Google Access - the permanent connection (27-28 Oct 2026)

Google is **not** a capability that gets re-set-up per session. It is one container, one credential, one MCP endpoint, kept alive by the operating system:

| | |
|---|---|
| MCP endpoint | `http://127.0.0.1:8766/mcp` — registered globally in `C:\Users\apviz\.minimax\mcp.json` as `Google_Access`, so **every** agent on this station inherits it, not only Mavis |
| Control point (one command) | `node C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\ga-doctor.mjs` → `VERDICT=PASS` / `FAIL`, exit 0 / 2 / 3, 11 checks |
| CLI harness (no MCP client needed) | `node C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\container\mcp-call.mjs <tool> @args.json` |
| Project | `C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access` (public repo `apvizual-max/Mavis-Google_Access`) |
| Bridge spec | `10_BRIDGES\10_google_access.md` |

Rules that follow from it:

1. **Never rebuild the settings.** The grant, the scopes, the token rotation, the re-consent listener and the verification already exist and run on their own. A session that "needs Google again" means something broke - run the control point, read the failing check, repair that.
2. **The human action is ONE click** (the consent screen), and only when Google itself demands it. The listener that catches the callback is kept alive by a scheduled task.
3. **`keep` and `sites` are refused by Google** and stay refused. They are not defects; Popy imports that content through other tools into Drive.
4. **The credential never leaves the volume** - not into a repo, not into a log, not into a chat message.
5. **`google-layer\` has one home**: `Mavis-Google_Access\google-layer\`. (Measured 28 Oct 2026: the references in the control center and in the skill were repaired in place, the same day.)
6. **A dead path in `mcp.json` disables the capability for EVERY agent on the station**, not just the session that wrote it - the MCP configuration is global. (Measured 28 Oct 2026: three `google-layer\` entries were broken by a move and nothing said so; `docker-mcp` pointed at a wrapper npm never created. Repair through the `mavis` interface, then **probe the real handshake** with `scripts\probe-mcp-stdio.mjs --name <entry>` - a file that exists is not a server that runs.)
7. **A file that is present but older is not a migration, it is a regression.** When content moves between repos, compare it - not just its presence: `scripts\compare-layer-versions.py`. (Measured 28 Oct 2026: the `google-layer\` move left three optimizations merged on 24 Oct behind; `gdrive-mcp` answered in 29.452 ms instead of 2.264 ms.)


### Tool before words

Use a tool, read its output, report that. A claim not produced by a tool, a file on disk, a command, or an observed artefact is a guess, and a guess is an error.

Specifically banned — each of these actually happened on 2026-10-05:
- reporting a system unsupervised because its process has no live parent, without checking whether anything restarts it
- naming a supervision mechanism never checked against the real owner of the port
- reporting "not signed in" from a check that tested a hostname the product no longer uses
- reporting "no notebooks" from a selector never run against the live DOM

When a check cannot complete, say **unknown**. An empty result and a failed measurement are different types and must never be reported as the same thing.

## Two-layer model

- **Doctrine substrate** (`SENTINEL_PRIME/`, built 2026-09-12): the deep pattern — A_FI_DOCTRINE, TRIPLE FILTER, ANTI-MIMICRY, rituals, sentinel_hub MCP, sentinel-prime-role skill. **Source of truth for doctrine.**
- **Mavis orchestration layer** (this directory, built 2026-09-18): bridges, registries, workflows, blueprints. **Consumes the doctrine; doesn't redefine it.**

Doctrine wins when the two layers disagree.

## Scope

This directory is the **Mavis orchestration layer** of the OPTIMUS Prime backbone. It contains:
- The doctrine that goes into MiniMax Code's Custom instructions box
- Per-AI bridge specs
- Operational protocols (Mavis-specific, complements `SENTINEL_PRIME/01_FOUNDATION/`)
- Source material registries across D:, E:, C:
- Templates for extending the system
- Skill and Connector blueprints

## Read order on session open

1. `README.md` — orientation, two-layer model
2. `OPTIMUS_INDEX.md` — cheat sheet
3. `SENTINEL_OPERATIONAL_DOCTRINE.md` — the paste-into-UI doctrine
4. `00_INDEX/00_master_map.md` — what's where
5. `00_INDEX/00_bridge_registry.md` — bridge status
6. `40_REGISTRIES/40_partition_E_aiwork.md` — where the SENTINEL manuals live on disk
7. Any JURNAL_OGLINDA entries in `40_REGISTRIES/` (append-only)
8. **If the task touches deep doctrine** → also read `SENTINEL_PRIME/01_FOUNDATION/doctrine/A_FI_DOCTRINE.md` and `SENTINEL_PRIME/02_OPERATIONAL/rituals/RITUAL_3_PROPOZITII.md`

Skip steps that are irrelevant to the user's current request.

## Conventions

- **File naming**: `NN_topic.md` with NN as zero-padded section number
- **Status badges**: ✅ WIRED · 🟡 BLUEPRINT · 🔴 BLOCKED
- **Citations**: `path:line` Markdown links
- **Prose**: Romanian at Popy + Prime + Assist tier, English elsewhere
- **Append-only**: `40_REGISTRIES/` and any file marked JURNAL_OGLINDA

## Hard rules (project-local)

- Never delete from `40_REGISTRIES/` — it is JURNAL_OGLINDA territory (append-only). Corrections are new entries referencing the old.
- Never invent tool names, CLI flags, MCP server identifiers, or prices.
- Every bridge activation goes through R33: analyze → Popy ratifies → execute.
- If unsure whether DRAG or DRAC applies, ask before acting.
- The doctrine file (`SENTINEL_OPERATIONAL_DOCTRINE.md`) is the source of truth for behavior — never fork it silently; propose amendments with rationale.

## Out of scope

- Direct manipulation of files outside this directory unless Popy explicitly authorizes (e.g., writes to the Obsidian vault on `E:\`).
- Wholesale scans of `C:\` — too broad, hits OS files. Use targeted scans only.
- Auto-installing software (CLI tools, MCP servers) without Popy R0.

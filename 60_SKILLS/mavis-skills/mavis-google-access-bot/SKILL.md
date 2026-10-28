---
name: mavis-google-access-bot
description: The hub of the permanent Google Access ecosystem on this station - one Docker container, one credential, one MCP endpoint, one control point, and the member skills that own each piece of it. Load this FIRST for anything that touches Google, Google Access, NotebookLM, the Photo Picker, the browser layer, the MCP registry, or a handoff of this work to another session or another machine. It dispatches to the right member skill, owns the naming and placement contract, owns the registry and its verifier, and owns the update loop that keeps every member honest. It holds the roadmap: the Browser MCP plans, the future MCPs on the central Docker access point, and the deferred Keep/Sites automations.
role: hub
kind: bot
bot: mavis-google-access-bot
---

# Mavis Google Access Bot

**Role.** The hub of one idea: **Google on this station is a mechanism, not a
promise.** One container holds the credential; one MCP endpoint serves it to
every agent on the machine; one command proves it; and a family of small
member skills each owns one piece, so no single session has to remember the
whole thing.

**Purpose.** The bot itself owns no Google logic. It owns four things — the
**list** of member skills, the **contract** they obey, the **registry** that
makes the list executable and verifiable, and the **update loop** that keeps
each member sharper than yesterday.

---

## 1. The personality

**SOUL — the operator who would rather be caught out than smooth.**
Literal about what was measured, unwilling to round a number it can measure,
unwilling to call a gap "empty" when it is "unknown", and willing to say "that
file was never written" instead of letting a receipt stand in for the thing.

**CONSTANTA — the four rules that make it that operator.**

1. **Tool before words.** Every number in this ecosystem is read from a tool, a
   file on disk, or a command. A claim that was not produced by one is a guess.
2. **A check that cannot fail is not a check.** Every member ships a verifier
   that re-queries the system and can genuinely go red. Run it; quote its exit
   code.
3. **No silent loss.** A gap is declared, never quietly dropped.
4. **The credential never leaves the volume.** Not into a repo, not into a log,
   not into a chat message, not into a handoff.

---

## 2. The contract — what every member owes

| # | Obligation | Proof it was met |
|---|---|---|
| C1 | The capability is **live**, not declared | a real API call / a real handshake answered with data |
| C2 | A **refusal is reported as a refusal** | `REFUSED` (Google answered) is never `OK` and never `ERROR` |
| C3 | The verifier is **independent** and can go red | verifier exit 0 on the good state, exit 1 on a corrupted one |
| C4 | Nothing is silently lost | a gap is declared in the docs and in `runs.md` |
| C5 | The **credential never leaves the volume** | no secret in an image layer, a repo, a log, a chat or a handoff |
| C6 | The member **records its run** | `runs.md` of that member gains an entry, with the measured numbers |
| C7 | **The namespace stays separate** | minimax and Hermes never share a container, a profile, a port or a credential |

If an obligation cannot be met, the member reports **which one**, with the
measurement that proves it. It does not ship a partial artifact and call it
done.

---

## 3. THE LIST — the linked skills

The authoritative list is `registry.json` (machine-readable) and
`scripts/bot-registry.mjs` (executable). This table is its human face and
**must stay in sync** — the registry verifier fails if a registered skill is
missing from it.

### 3.1 The members (owned by this bot)

| Skill | Role | Status | What it owns |
|---|---|---|---|
| [`mavis-skill-google-access-control-point`](../mavis-skill-google-access-control-point/SKILL.md) | functional | ✅ WIRED | The control point: one command, 11 checks, one verdict, exit 0/2/3 — and the permanence contract |
| [`mavis-skill-docker-access-point`](../mavis-skill-docker-access-point/SKILL.md) | functional | ✅ WIRED | The container: image build, three volumes, the port rule, and "the running bytes are the repo bytes" |
| [`mavis-skill-browser-mcp`](../mavis-skill-browser-mcp/SKILL.md) | functional | ✅ WIRED | The browser layer: `minimax-notebooklm` (own profile, CDP 9412), the picker window, and the browser-side roadmap |
| [`mavis-skill-mcp-development`](../mavis-skill-mcp-development/SKILL.md) | functional | ✅ WIRED | How the next MCP joins the central access point: the route, the registry contract, the proof |
| [`mavis-skill-photo-picker`](../mavis-skill-photo-picker/SKILL.md) | functional | ✅ WIRED | The only door to the user's photo library: the two causes of the same error, the capture cycle, the consumed-session state |
| [`mavis-skill-notebooklm-extendlm`](../mavis-skill-notebooklm-extendlm/SKILL.md) | functional | ✅ WIRED | The API route to NotebookLM: single-owner rotation, snapshot publication, and the honest limits |
| [`mavis-skill-google-keep-sites`](../mavis-skill-google-keep-sites/SKILL.md) | functional | ✅ WIRED | The two refused services: the measured reason, and the deferred automation plan |
| [`mavis-skill-access-handoff`](../mavis-skill-access-handoff/SKILL.md) | meta | ✅ WIRED | The handoff protocol: location contract, priming-prompt shape, verification before "ready" |
| [`mavis-skill-background-task-verdict`](../mavis-skill-background-task-verdict/SKILL.md) | meta | ✅ WIRED | How a long measurement is judged: by the MARKERS it printed, never by the shell's exit code — the instrument that makes a successful probe stop looking like a failed task |

### 3.2 The references (read, not owned)

These exist on the station and matter to this ecosystem. They are **references**:
this bot does not own their files, does not require them to carry its
frontmatter, and does not claim their run logs.

| Skill | What it is |
|---|---|
| [`mavis-google-access-skill`](../mavis-google-access-skill/SKILL.md) | the pre-existing micro-skill on the Google connection (history, the four prohibitions) |
| [`mavis-google-workspace-skill`](../mavis-google-workspace-skill/SKILL.md) | the Workspace-side Google access |
| [`mavis-notebooklm-bridge-skill`](../mavis-notebooklm-bridge-skill/SKILL.md) | the NotebookLM bridge, from the bridge family |
| [`mavis-mcp-management-skill`](../mavis-mcp-management-skill/SKILL.md) | MCP management across the station |
| [`mavis-docker-gordon-skill`](../mavis-docker-gordon-skill/SKILL.md) | Docker operations and diagnosis |
| [`mavis-antigravity-docker-admin-skill`](../mavis-antigravity-docker-admin-skill/SKILL.md) | Docker administration from the Antigravity side |
| [`mavis-chrome-browser-skill`](../mavis-chrome-browser-skill/SKILL.md) | browser automation, generally |
| [`mavis-shared-local-mcp-swarm-skill`](../mavis-shared-local-mcp-swarm-skill/SKILL.md) | the shared local MCP swarm |
| [`mavis-autonomous-operator-skill`](../mavis-autonomous-operator-skill/SKILL.md) | how the operator acts without being asked |
| [`mavis-full-intent-execution-skill`](../mavis-full-intent-execution-skill/SKILL.md) | carrying an intent to the end |
| [`mavis-session-lifecycle-skill`](../mavis-session-lifecycle-skill/SKILL.md) | session lifecycle, and the handoff it serves |
| [`mavis-memory-curator-skill`](../mavis-memory-curator-skill/SKILL.md) | keeping memory curated and non-duplicated |
| [`mavis-search-before-write`](../mavis-search-before-write/SKILL.md) | the standing rule: search first, write second |
| [`mavis-backbone-skill`](../mavis-backbone-skill/SKILL.md) | the backbone this ecosystem is part of |
| [`mavis-cloud-bridge-skill`](../mavis-cloud-bridge-skill/SKILL.md) | the Local↔Cloud bridge |
| [`mavis-local-to-cloud-reporting`](../mavis-local-to-cloud-reporting/SKILL.md) | reporting from Local to Cloud |
| [`mavis-skill-index`](../mavis-skill-index/SKILL.md) | the master index of every skill Mavis can call |
| [`mavis-bundle-operations`](../mavis-bundle-operations/SKILL.md) | the bundle this bot is dispatched from |
| [`mavis-minimax-index-folder-update`](../mavis-minimax-index-folder-update/SKILL.md) | keeping the index folders true |
| [`mavis-jules-contract-skill`](../mavis-jules-contract-skill/SKILL.md) | the Jules contract, consumed by the Cloud side |
| [`mavis-doc-bridge-skill`](../mavis-doc-bridge-skill/SKILL.md) | document bridging |
| [`mavis-instruction-fidelity-skill`](../mavis-instruction-fidelity-skill/SKILL.md) | executing an instruction as written |
| [`mavis-git-autonom-skill`](../mavis-git-autonom-skill/SKILL.md) | autonomous git, and the push gate |
| [`mavis-triple-crunch-skill`](../mavis-triple-crunch-skill/SKILL.md) | the triple-filter discipline |
| [`mavis-r33-bimodal-skill`](../mavis-r33-bimodal-skill/SKILL.md) | the bimodal workflow contract |
| [`mavis-antigravity-ecosystem-integrations-skill`](../mavis-antigravity-ecosystem-integrations-skill/SKILL.md) | cross-ecosystem integrations |
| [`mavis-skill-repair-manifest-skill`](../mavis-skill-repair-manifest-skill/SKILL.md) | recovery path when a member's installation failed: repairs the installed files and updates `manifest.json` |

### 3.3 Commands

```powershell
# the dispatch table, and its health
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\scripts\bot-registry.mjs" list
node "...\bot-registry.mjs" list --json
node "...\bot-registry.mjs" verify          # exit 1 if any linked skill is unhealthy
node "...\bot-registry.mjs" show --name mavis-skill-google-access-control-point

# register a new member (refuses if the skill is not on disk yet)
node "...\bot-registry.mjs" link --name <skillName> --role functional --source <sourceId> --purpose "<one line>"

# log a run into a member
node "...\scripts\log-run.mjs" --skill <skillName> --status success|error \
     --task "<what was done>" --outcome "<measured result>" [--error "<verbatim error>"]

# the logger's own self-test (fixture only; it never touches a real member's log)
node "...\scripts\log-run-selfcheck.mjs"
```

**The logger resolves the skill by the registry first**, then by folder, and it
probes the folder three times before believing it is missing — a single failed
`existsSync` on a present directory was measured on this station, and a run log
must never be lost to a blip. When it cannot resolve, it exits **2** and prints
the registered members and the folders actually on disk, so the mismatch is
visible instead of guessed. It also accepts `--skills-root <dir>` and
`--registry <file>` so the self-test can run on a fixture.

### 3.4 How a measurement is judged (the exit code is not the verdict)

**Measured 2026-10-28:** roughly 100 background tasks on this station were
reported as "failed" while their output was complete and correct. One batch of
six live probes printed all six result lines and was then reported as failed
with exit code `4294967295`. A falsification probe whose entire purpose was to
fail (`--self-test --fail C1.container` -> `VERDICT=FAIL`, exit 2) was
reported as a failed task although the falsification WORKED.

That is not noise to be ignored — it is how real failures get trained out of
attention. So the rule of this bot is:

> **The verdict of a measurement is the MARKERS in its output. The exit code of
> the command is a detail of the inner command.**

Two consequences, both enforced by `mavis-skill-background-task-verdict`:

- A measurement is run through `scripts\bg-verdict.mjs`, which captures the
  output, checks the required and forbidden markers, and exits **0** when the
  measurement produced what it should — even when the inner command exited
  non-zero. A successful probe stops looking like a failed task.
- A falsification is run the same way with `--expect-exit 2 --expect
  "VERDICT=FAIL"`: the wrapper exits **0** because the falsification worked.

The wrapper's own exit codes are distinct on purpose: `0` = the verdict is PASS,
`1` = the verdict is FAIL, `2` = you called the wrapper wrong.

**Why this is a member and not a habit:** a habit is decoration, an instrument
is a fact. The same reasoning that produced the control point.

---

## 4. Naming format

| Kind | Format | Example |
|---|---|---|
| Functional (owns one capability of the ecosystem) | `mavis-skill-<capability>` | `mavis-skill-google-access-control-point` |
| Meta (a process the bot runs) | `mavis-skill-<process>` | `mavis-skill-access-handoff` |
| Reference (read, not owned) | any existing name | `mavis-mcp-management-skill` |

- The folder name, the frontmatter `name:` and the registry entry are **the
  same string**. The verifier fails if they drift.
- Every member's frontmatter carries: `name`, `description`, `role`
  (`functional` | `meta`), `bot: mavis-google-access-bot`.
- **The naming format here is `mavis-skill-<capability>`, specified by Popy**
  on 2026-10-28. It deliberately differs from the Session Extract Bot's
  `mavis-session-<artifact>-skill` — two bots, two contracts, and the verifier
  of each reads its own registry.

---

## 5. The location contract

When a request names **where the output goes**, that location is binding. The
bot does not choose its own folder, does not move the result afterwards, and
does not write the output in two places "to be safe".

The ecosystem's own handoff lives in the project it describes:

```
Mavis-Google_Access\.handoff\
  README.md  HANDOFF-GOOGLE-ACCESS.md  PRIMING-PROMPT.md
  SKILLS-INDEX.md  STATE-MEASURED.md  MANIFEST.json
```

**Hazard rule (measured, 2026-10-28):** a handoff is personal operational
context. If the folder sits inside a **public** git repository, write the
ignore rule **before** the first commit and prove it
(`git check-ignore -v <file>`; `git add -A --dry-run` must not list it).

---

## 6. The run protocol — what happens on a request

1. **Read the request.** Identify the piece of the ecosystem it touches.
2. **Load the member** that owns that piece. Do not re-implement its logic.
3. **Run it**, with its verifier.
4. **Quote the verifier's exit code.** A success without its number is a story.
5. **Log the run** into the member's `runs.md` (§7).
6. **Update the member** if the run taught it something (§7).
7. **Report**: what was produced, where, with the measured numbers, and any
   declared gap.

---

## 7. The update loop — how a skill gets better

| What | Where | Why |
|---|---|---|
| the **success**, with its measured numbers | the member's `runs.md` (append-only) | a success without its numbers is not evidence |
| the **error**, verbatim | the member's `runs.md` (append-only) | a paraphrased error is a different error |
| the **lesson** — the wrong path, the silent failure, the source that lied | the member's `SKILL.md`, edited in place | the next run must not repeat the mistake |

```powershell
node "...\scripts\log-run.mjs" --skill <skillName> --status success|error `
     --task "<what was done>" --outcome "<measured result>"
```

The log is **append-only**. A correction is a *new* entry that references the
old one.

**The loop, in one line:** act → verify → log what happened → make the next run
better.

---

## 8. The measured state of the ecosystem

Measured 2026-10-28 00:03Z by the control point itself:

```
CHECK C1.container    OK   running / healthy / google-access:1.0.9 / unless-stopped
CHECK C1b.running-code OK  repo=8429fa512919 running=8429fa512919 match=true
CHECK C2.health       OK   grant=live reauth=false tools=32
CHECK C3.services     OK   OK=14 REFUSED=2[keep,sites] ERROR=0
CHECK C4.extendlm     OK   token_minutes_left=220 refresh_token=yes
CHECK C5.browser-mcp  OK   server=minimax-notebooklm tools=4
CHECK C6.mcp-registry OK   enabled=true url=http://127.0.0.1:8766/mcp
CHECK C10.mcp-paths   OK   checked=23 dead_total=0
CHECK C7.tasks        OK   count=4
CHECK C8.consent      OK   listener alive (processes=1)
CHECK C9.picker       OK   session consumed - nothing to watch
SUMMARY checks=11 failed=0 warnings=0
VERDICT=PASS
```

**The two refusals are by design** (`keep` 403 — no grantable scope; `sites`
404 — the API was retired). They are the only two.

**The human actions that remain:** the consent click, when Google demands it,
and the selection of photos in the picker. Everything else is automatic.

---

## 9. The roadmap

| What | Status | The condition to start |
|---|---|---|
| **Browser MCPs on the central point** — picker window automation, NotebookLM source ingestion, an explicitly-owned shared browser profile, CDP health as a control-point check | 🟡 PLANNED | see `mavis-skill-browser-mcp` §4 |
| **A second Docker-based MCP** on the same access point | 🟡 PLANNED | the interface must be decided per capability: the same `/data` volume and credential, or its own OAuth client |
| **New tools inside the container** | 🟡 PLANNED | the route in `mavis-skill-mcp-development` §3; a new Google scope is verified before it is added |
| **Keep** automation | ⏭ DEFERRED BY THE USER | a grantable scope must exist in the current Google directory; if it does, it costs one consent click |
| **Sites** automation | ⏭ DEFERRED BY THE USER | nothing to automate — the API is retired; only a migration to Drive remains |
| **A Drive-side import** for the content Popy imports by hand today | 🟡 PLANNED | belongs to the Drive side, not to this container |
| **Google Cloud** | ⛔ OUT OF SCOPE | excluded by Popy's instruction |

---

## 10. The error taxonomy

| Code | Meaning |
|---|---|
| `SOURCE_NOT_FOUND` | the store or path for a piece could not be located |
| `NOT_TRACEABLE` | it exists but the specific thing cannot be reached inside it |
| `REGISTRATION_DEAD` | a registry entry points at a path that does not exist (measured 2026-10-28, three times) |
| `HANDSHAKE_FAILED` | the server started but did not answer an MCP handshake |
| `SCOPE_INVALID` | the scope does not exist in Google's registry — it invalidates the **whole** consent request |
| `REFUSED_BY_GOOGLE` | Google answered with a refusal; this is a measured answer, not a failure |
| `VERIFY_FAILED` | the independent verifier rejected the state (this is the gate working) |
| `CREDENTIAL_LEAK` | a secret reached a place it must never reach |
| `UNKNOWN` | not measurable — report it as unknown, never as empty |

---

## 11. Dependencies and environment contract

| Dependency | Why | State |
|---|---|---|
| **Node >= 22** | the verifiers and probes use only Node builtins | ✅ measured on this machine |
| **Docker** | the access point is a container | ✅ `Google_Access`, healthy |
| **The global MCP registry** `C:\Users\apviz\.minimax\mcp.json` | how every agent inherits the access point | ✅ 21 servers registered |
| **The container volume** `C:\Users\apviz\.minimax\google-access\data` | the credential and the live source | ✅ present |
| **Windows Task Scheduler** | five tasks keep the system alive | ✅ all green |
| **`gh` CLI** | the Cloud secret readback | ✅ available |

**Hard rules**

- **No third-party npm packages** in the verifiers — Node builtins only.
- **No fabricated interfaces.** If a path cannot be located, say
  `NOT LOCATED — here is how to confirm by another route`.
- **Namespace separation (Popy, 2026-10-05):** minimax and Hermes are separate
  universes. Never point one at the other's container, profile, port or
  credential. **Duplication is the correct answer** — two independent
  instances cannot destroy each other; a shared one can.
- **The credential never leaves the volume.**

---

## 12. Files in this skill

| File | What it is |
|---|---|
| `SKILL.md` | this document — the role, the personality, the contract, the list, the loop |
| `SPEC.md` | the technical contract: the member shape, the registry schema, the verifier contract |
| `registry.json` | the machine-readable list: members + references + roadmap |
| `scripts/bot-registry.mjs` | `list` · `verify` · `show` · `link` — the list, executable |
| `scripts/log-run.mjs` | appends a run record to a member's `runs.md` |
| `logs/bot-runs.md` | the bot's own run log |

---

## 13. Cross-references

- `mavis-skill-google-access-control-point` — the control point; the first member
- `mavis-skill-docker-access-point` — the container the ecosystem runs in
- `mavis-skill-access-handoff` — how this work travels to a session with no memory
- `mavis-session-extract-bot-skill` — the sibling bot whose **structure** this one follows
- `mavis-skill-index` — the master index of every skill Mavis can call
- Doctrine: `C:\Users\apviz\.minimax\AGENTS.md` §12.5, `SENTINEL_OPERATIONAL_DOCTRINE.md` §12.5

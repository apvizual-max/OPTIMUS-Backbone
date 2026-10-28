<!-- SOT-STATUS-BANNER
  Added 2026-10-02 10:46 by scripts\stamp-doc-status.ps1

  THIS IS A POINT-IN-TIME DOCUMENT: the original gap analysis that defined the P0/P1/P2 work queue.

  It is deliberately NOT rewritten -- rewriting it would destroy the record of
  what was true when it was written. For the CURRENT system state read:

    POPY_MiniMax_OPTIMUS_Status_Report-10-02-2026.md   <- current state, for Popy
    mavis-minimax-optimus-system                        <- skill: restore + config SOT
    mavis-minimax-index-folder-update                   <- skill: how to index this folder
    optimus status   /  cc start   /  cc guard          <- live truth, measured
-->
> ### ARCHIVED BODY - current truth is in OPTIMUS_CURRENT_STATE.md
> The body below is a record of what was true when it was written and is left
> intact on purpose. Do not read its claims as current.
>
> The one thing to know about `qwen-mcp-http`: the body says it works against
> `localhost:8765/mcp`. That path returns 404 - Qwen 0.19.2 exposes ACP at
> `/acp` and has no MCP transport, so this entry cannot connect.
> **It is nonetheless enabled, by Popy's explicit decision of 2026-10-02**, kept
> alongside `qwen-acp-adapter` (the working path, 6 tools). Enabled does not
> mean functional here. Current truth: `projects\OPTIMUS_CURRENT_STATE.md`,
> regenerated from live state by `scripts\build-current-state.ps1`.
**Date**: 2026-10-02
**Author**: Mavis (MiniMax Code orchestrator)
**Operator**: Popy (Alexandru Popescu)
**Scope**: What is still missing from full MiniMax integration into the OPTIMUS Prime system, and what the complete target state looks like.
**Status**: ðŸ”´ GAPS CONFIRMED — integration is ~55% complete

---

## Summary

Over 3 days of work (2026-09-18 → 2026-10-02) I wired Mavis into the OPTIMUS ecosystem: 13 MCP servers, 23 skills, a 1,159-skill autonomous router, a self-healing cron classifier, and the `SENTINEL_OPERATIONAL_DOCTRINE.md` for MiniMax Code's Custom instructions.

**But the brief is bigger than what I built.** Popy's actual target is:

> *Run Hermes as the orchestration + user-interaction layer, Wayland for agentic cowork, Docker for Sentinel role AIs, Obsidian as the Second Brain (Karpathy LLM-wiki pattern), and MiniMax Code + Hub as the coding/capability substrate — then power Hermes with MiniMax models.*

Three findings from tonight's investigation change the assessment materially:

1. ✅ **MiniMax M3 is ALREADY wired as Hermes's default model.** This was on Popy's wishlist and is done.
2. ðŸ”´ **MiniMax Hub is NOT installed.** This blocks 8 of 9 MiniMax H3 skills and all multimodal generation.
3. ðŸ”´ **Wayland was never explored** in 3 days of work, despite Popy naming it a core pillar. It is installed and has an unexploited workflow engine.

The gap is not "more wiring." It is **4 uninstalled/never-touched pillars** and **1 misaligned layer**.

---

## Part 1 — What is DONE (verified live 2026-10-02)

| # | Deliverable | Evidence | Status |
|---|---|---|---|
| 1 | MiniMax Code app + CLI | `C:\Users\apviz\AppData\Local\Programs\MiniMax Code\MiniMax Code.exe`; `~\.minimax\` data dir live | ✅ |
| 2 | MiniMax Design app | `C:\Users\apviz\AppData\Local\Programs\MiniMax Design\MiniMax Design.exe` | ✅ |
| 3 | **MiniMax M3 as Hermes default model** | `hermes-agent\cli-config.yaml:1-5` → `default: MiniMax-M3`, `provider: minimax-oauth`, `base_url: https://api.minimax.io/anthropic`, `api_mode: anthropic_messages`; 6 profile bindings to M3/M2.7/M2.7-highspeed | ✅ **NEW FINDING** |
| 4 | MiniMax Code MCP fleet | 13 servers wired via `mcp.json`, 13 enabled | ✅ |
| 5 | Mavis skill system | 23 skills + 4 bundles + `mavis-skill-index` Pillar skill | ✅ |
| 6 | Personal-skill autonomous router | 1,159 skills classified, 4 categories, 281,669-byte index, self-healing weekly cron (`ae94ec45-…`, `0 4 * * 1` Europe/Bucharest) | ✅ |
| 7 | Doctrine (Custom instructions) | `SENTINEL_OPERATIONAL_DOCTRINE.md` ~16.5 KB, §0–§18.5 | ✅ |
| 8 | Code-review rules | `code_review_rules.md` 15.3 KB, 11 sections, 42 examples | ✅ |
| 9 | Memory export | `memory_summary.md` 7 KB, 8 entries canonical format | ✅ |
| 10 | Hermes bridge | `hermes-mcp-router` + `mavis-hermes-bridge-skill`; 31 `hermes-mcp-*` containers visible | ✅ |
| 11 | Obsidian bridge | `obsidian-mcp` wired; vault at `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\` (8,190 md files @ depth 4) | ✅ |
| 12 | Docker bridge | `docker-mcp` + `mavis-docker-gordon-skill`; Docker Desktop 4.91.0 / CLI 29.8.0 | ✅ |
| 13 | bun runtime located | `C:\Program Files\Qwen\resources\bun\bun.exe` v1.2.10 — unblocks 4 Google MCPs | ✅ |
| 14 | SACRU corpus located | `SF_IA - 963_PROVERBE_COMPLET.md` (25-axe decision matrix) | ✅ |
| 15 | H3 prompt writing | `minimax-h3-skills:h3-prompt-writing` works (portable skill) | ✅ partial |

---

## Part 2 — What is MISSING (the gaps)

### GAP-1 ðŸ”´ CRITICAL — MiniMax Hub not installed

**Popy's words**: *"including Minimax HUB app, meaning the desktop app for minimax design"*

**Reality**: Not installed. Probed:
- `C:\Program Files\MiniMax Hub` → absent
- `C:\Users\apviz\AppData\Local\Programs\MiniMax Hub` → absent
- `C:\Users\apviz\.minimax\.minimax-hub-agent` → absent
- `minimax-hub` / `hub` / `mhub` CLIs → not on PATH

**Consequence**: 8 of 9 skills in the `minimax-h3-skills` plugin are permanently dormant. Each declares in its own `compatibility:` frontmatter:

> *"Requires the MiniMax Hub agent (canvas workspace and hub_* tools); not portable to generic agent harnesses."*

Dormant skills: `3d-animation-short-generator`, `brand-promo-video-generator`, `co-op-game-intro-generator`, `handdrawn-live-video-generator`, `minimalist-product-ad-generator`, `music-video-subtitle-generator`, `paper-collage-explainer-generator`, `papercraft-stop-motion-explainer`.

**Missing tools Hub would provide**: `hub_canvas_get_node`, `hub_canvas_group_recent_outputs`, `hub_generate_image`, `hub_generate_video`, `hub_analyse_media`, `hub_image_search`.

**This is the single largest gap.** It blocks: video generation, image generation, TTS, music, and all 8 video workflow skills. Popy's `D:\Alex_Knowlege_Vault\03_Resources\03_7-SENTINEL_Character\` has AUDIO (4 m4a), VIDEO (17+ clips), BRAIN (design docs), CHARACTER (8 portraits), SCENES (4 renders) — all of which are natural Hub inputs.

**Fix**: Install MiniMax Hub, then re-run the `minimax-h3-skills` assessment. Popy R0 required (software install).

---

### GAP-2 ðŸ”´ CRITICAL — Wayland never explored

**Popy's words**: *"the Wayland platform for agentic cowork and agentic workflows"*

**Reality**: Installed, but I have never touched it in 3 days of work. This is the most under-served pillar relative to its stated importance.

**What exists (probed tonight)**:

| Path | Contents |
|---|---|
| `C:\Program Files\Wayland\resources\bundled-workflows\` | `routines.json` (scheduled routines), `index.json` (workflow catalog), `skill-bodies.bin`, `skill-bodies.offsets.json` |
| `C:\Program Files\Wayland\resources\managed-cli-shims\` | `officecli`, `officecli.cmd` — only 2 shims |
| `C:\Program Files\Wayland\resources\bundled-officecli\` | `win32-x64\` |
| `C:\Program Files\Wayland\resources\bundled-fuigo\` | `win32-x64\` |
| `C:\Program Files\Wayland\resources\bundled-tvcontrol\` | `node_modules\` |
| `C:\Program Files\Wayland\resources\skills-library\` | **EMPTY — 0 directories** |
| `C:\Program Files\Wayland\resources\classic-recovery-tools\` | present |
| `C:\Users\apviz\AppData\Roaming\Wayland\` | `.cursor`, `.github`, `.ijfw`, `.vscode`, `bun-cache`, `bun-tmp`, `config` |

**What `routines.json` reveals** — a working scheduled-workflow engine:

```json
{
  "id": "daily-launch-status",
  "name": "Daily launch status",
  "schedule": "0 9 * * *",
  "workflow": "wayland-launch-status-batch",
  "inputs": {
    "active_launch_path": "~/wayland/state/active-launch.yaml",
    "data_dirs": "~/wayland/inbox/sales,~/wayland/inbox/ads,~/wayland/inbox/support"
  }
}
```

Also present: `weekly-listing-audit` (`0 10 * * 3`), `weekly-content-batch` (`0 18 * * 0`), `weekly-copy-review`.

**What `index.json` reveals** — a versioned, security-scanned skill catalog:
- `business-ops-monthly-review` v1.0.0, author `wayland`, tags `[business-ops, monthly-review, metrics, reporting, deterministic]`
- `depends: ["ops-report"]` — a dependency graph
- `security.verdict: "clean"`, `scannerVersion: 1` — automated security scanning built in

**Gaps**:
1. **No Wayland CLI on PATH** — `wayland`, `wl`, `wayland-cli` all not found. Only `officecli` is shimmed.
2. **No `~/wayland/` state dir wired to Mavis** — routines reference `~/wayland/state/`, `~/wayland/inbox/`, `~/wayland/voice-notes.md`. Mavis has no bridge skill, no MCP, no awareness.
3. **`skills-library/` is empty** — the install is either incomplete or the library populates on first launch.
4. **`bundled-workflows` never inventoried** — index.json has a catalog; I don't know how many workflows, what `skill-bodies.bin` contains, or which are relevant to OPTIMUS.
5. **No Wayland↔Mavis cron bridge** — Wayland has its own routine scheduler; Mavis has its own. Two schedulers, no reconciliation.

**Recommended fix**: Full inventory of `bundled-workflows/index.json` (count + categories), identify the `~/wayland/` contract, build `mavis-wayland-bridge-skill`, and decide whether Mavis crons or Wayland routines own each scheduled job.

---

### GAP-3 ðŸ”´ HIGH — Sentinel role AIs not on Mavis's radar

**Popy's words**: *"Docker platform running system local containers for software tools and custom Sentinel role AI implementations"*

**Reality**: The containers exist, but I have never inventoried the non-Hermes ones. Probed tonight:

| Container | Role | Images backing it |
|---|---|---|
| `hermes-sentinel-daemon` | **Sentinel role AI** | — |
| `apviz-dashboard-monitor` | monitoring | — |
| `Antigravity_Ecosystem_Terminal` | Antigravity surface | `apviz/antigravity-ecosystem-terminal:latest` |
| `camofox-browser` (+ `-beta`, `-latest`) | browser automation | `camofox-browser:latest`, `camofox-browser:152.0.4-beta.28-x86_64` |
| `whatsmeow-v4`, `whatsmeow-bui` | WhatsApp | `whatsmeow-bui:latest` |
| `selenium-chrome` | browser | `selenium/standalone-chrome:latest` |
| `redis` | state | `redis:7-alpine` |
| `elasticsearch` | search | `elasticsearch:8.15.0` |
| `vault` | secrets | `hashicorp/vault:latest` |
| `postgres` | DB | `postgres:15` |
| `prometheus` | metrics | `prom/prometheus:latest` |
| `searxng` | metasearch | `searxng/searxng:latest` |
| `stirling-pdf` | PDF ops | `stirlingtools/stirling-pdf:latest` |
| `open-webui`, `aion-ui` | UIs | `ghcr.io/open-webui/open-webui:main`, `aion-ui:latest` |
| `libreoffice` | doc conversion | `lscr.io/linuxserver/libreoffice:latest` |
| `mystifying_chaplygin` | orphaned compose default | — |

**Gaps**:
1. `hermes-sentinel-daemon` — never documented. What is it? Which SENTINEL roles does it implement? How does it relate to the 9 Hermes profiles?
2. `camofox-browser` × 3 variants running simultaneously — 3 browsers is likely accidental. DRAC candidate (needs Popy R0).
3. `stirling-pdf`, `libreoffice`, `open-webui`, `aion-ui` — no MCP bridge from Mavis to any of these. Popy can do PDF/Office/UI work through them; Mavis cannot.
4. `mystifying_chaplygin` — orphaned container from a `docker-compose up` with no service name. Cleanup candidate.
5. No registry file documenting the non-Hermes container fleet. `40_REGISTRIES/40_partition_C_system.md` only records the CLI binaries and the Hermes fleet.

**Recommended fix**: Full non-Hermes container inventory → `70_CONNECTORS/70_docker_fleet_inventory.md`, with role mapping, MCP bridge recommendations, and DRAC candidates flagged for Popy R0.

---

### GAP-4 ðŸ”´ HIGH — Obsidian: Karpathy LLM-wiki pattern not implemented

**Popy's words**: *"Obsidian as the second brain local custom memory system that also opperates based on karpathy's LLM wiki concept but cutom adapted for our needs based on cutom folder indexations and canonical docuemt headers"*

**Reality**: The vault exists and is large. The *pattern* does not.

**Verified**:
- 8,190 markdown files at depth 4
- INDEX files exist but are **scattered across 12+ locations**, e.g.:
  - `SF_DSL_SC - Scoala_Source\INDEX.md`
  - `SF_MKVA_KN - Knowledge_General\INDEX.md`
  - `SF_RS_RA - Reflex_Archive\INDEX_GLOBAL.md`
  - `SF_PR_VV\INDEX_ARHIVA.md`
  - `Archive - OLD System\reflex_archive\INDEX_GLOBAL.md`
- **No unified index at the vault root**
- **No canonical document header convention enforced or verified**

**What the Karpathy LLM-wiki pattern requires** (per Popy's description):
1. **Custom folder indexation** — a navigable hierarchy where every folder has an index
2. **Canonical document headers** — every note carries a consistent frontmatter/header block

**Gaps**:
1. No vault-root index — a new session (Mavis or Popy) has no single entry point
2. No canonical header schema — inconsistent or absent frontmatter across 8,190 files
3. No index-completeness audit — which folders lack an INDEX?
4. No link-graph health check — Karpathy's pattern depends on dense cross-linking
5. Mavis's `obsidian-second-brain-skill` only says "propose before writing" — it doesn't enforce or verify the pattern

**Recommended fix** (staged, needs Popy R0 on the header schema):
1. Design the canonical header (YAML frontmatter: `type`, `sacru`, `tier`, `tags`, `canonical`, `source`, `created`, `updated`, `cross-links`)
2. Audit which folders lack an INDEX
3. Build a vault-root `00_CANONICAL_INDEX.md`
4. Add a Mavis skill that writes the header on every new note
5. Add a periodic audit cron: header compliance + index coverage

---

### GAP-5 ðŸŸ¡ MEDIUM — Google OAuth bootstrap never done

4 MCP servers are wired and enabled but return nothing:

| MCP | State | Needs |
|---|---|---|
| `gdrive-mcp` | ✅ wired, ⛔ no data | Browser OAuth (via `gdrive-mcp-auth.cmd`) |
| `gmail-mcp` | ✅ wired, ⛔ no data | Browser OAuth |
| `google-workspace-mcp` | ✅ wired, ⛔ no data | Browser OAuth |
| `google-calendar-mcp` | ✅ wired, ⛔ no data | Browser OAuth |

Also: Hermes-side `gmail` MCP is **disabled** (the only disabled one in its 36-server fleet).

**This is the only gap I can close without Popy** — but the OAuth consent screen requires a human click. 5 minutes of Popy's time unlocks 4 MCPs.

---

### GAP-6 ðŸŸ¡ MEDIUM — Qwen OAuth not bootstrapped

`qwen auth qwen-oauth` never run. The Qwen HTTP daemon is wired (`qwen-mcp-http` on :8765) but the model won't answer without auth. Hermes reports `Qwen OAuth: NOT logged in`.

---

### GAP-7 ðŸŸ¡ MEDIUM — Claude Code, OpenClaw, Copilot, Droid, Trae, Kiro not installed

Popy mentioned these as "AI Coding CLIs" in the context of the MiniMax app integration. Probed: **none are on PATH.** Currently installed AI apps are:

`a0-launcher`, `antigravity`, `Antigravity IDE`, `Cua`, `LM Studio`, `lrc`, `MiniMax Code`, `MiniMax Design`, `Qwen`, `space-agent`

If Popy wants any of the other five, they need installing. I have not been told they're required — flagging for confirmation.

---

### GAP-8 ðŸŸ¡ MEDIUM — Token Plan / credit headroom

A cron-triggered session on 2026-09-21 died with:

```
Token Plan usage limit reached: Upgrade your Token Plan or purchase Credits for more usage. (2056)
errorCode: 42212
```

**Operational risk**: any scheduled Mavis run that hits the token limit leaves work un-refreshed. The self-healing classifier would silently stop refreshing.

**Note**: Hermes `cli-config.yaml` shows M3 wired via `minimax-oauth` — that's the *model* wiring, which is separate from the *Token Plan* subscription for MiniMax Code itself. Both may be needed.

---

### GAP-9 ðŸŸ¢ LOW — `hermes status` now hangs

Tonight, `hermes status` and `hermes mcp list` began hanging (earlier in the session they responded). Per my own diagnostic memory entry: this is a **dependency-currency** issue, not an application-code issue. Read-only probe:

```powershell
python -I -B -c "import sys; sys.path.insert(0, r'C:\Users\apviz\AppData\Local\hermes\hermes-agent'); from hermes_cli.venv_sync import main; sys.exit(main(['--project-root', r'C:\Users\apviz\AppData\Local\hermes\hermes-agent', '--check', '--json']))"
```

`{"state": "current"}` = healthy · `{"state": "would-sync"}` = out of date.

**Not yet run.** This is the known Hermes install failure mode and needs attention before it blocks the bridge.

---

## Part 3 — The four pillars, assessed

Popy's stated architecture: *Hermes = orchestration + user interaction · Wayland = agentic cowork · Docker = Sentinel role AIs · Obsidian = Second Brain (Karpathy LLM-wiki)*

| Pillar | Installed | Mavis integrated | Gap depth |
|---|---|---|---|
| **Hermes** (orchestration) | ✅ v0.21.3 | ✅ 13 MCPs, 31 containers, M3 model, bridge skill | **Shallow** — surface wired, `status` now hanging, no profile-deep integration |
| **Wayland** (agentic cowork) | ✅ (undocumented by me) | ❌ **zero** | **Deep** — never inventoried, no CLI, no bridge, no `~/wayland/` awareness, routines unknown |
| **Docker** (Sentinel role AIs) | ✅ Desktop 4.91.0 | ⚠️ partial — Hermes fleet yes, non-Hermes fleet no | **Medium** — 18 non-Hermes containers uninventoried, no MCP bridges to PDF/Office/UI, cleanup candidates |
| **Obsidian** (Second Brain) | ✅ 8,190 files | ⚠️ partial — MCP works, pattern not implemented | **Medium** — no vault-root index, no canonical headers, Karpathy LLM-wiki unimplemented |
| **MiniMax Code + Design** (capability substrate) | ✅ both | ✅ 13 MCPs, 23 skills, 1,159-skill router, doctrine | **Shallow-complete** — Mavis's own layer is well-built |
| **MiniMax Hub** (multimodal) | ❌ **NOT INSTALLED** | ❌ blocked | **Deep** — blocks 8 skills, all video/image/audio/music generation |

---

## Part 4 — Priority queue (Popy R0 required for items 1–4)

### P0 — Unblock multimodal (the single biggest win)

| # | Action | Effort | Unblocks |
|---|---|---|---|
| 1 | Install **MiniMax Hub** | ~10 min download + install | 8 H3 video skills, all image/video/audio/music generation, canvas workspace |
| 2 | Re-run H3 assessment after install | 5 min (Mavis) | Confirms 9/9 skills live |
| 3 | Generate first real H3 prompt for a SENTINEL_Character asset | 10 min (Mavis) | Proof the pipeline works end-to-end |

### P1 — Close the never-explored pillar

| # | Action | Effort | Unblocks |
|---|---|---|---|
| 4 | **Wayland inventory** — count workflows in `index.json`, map `routines.json`, identify `~/wayland/` contract | 30 min (Mavis, R0 only) | Bridge design for the agentic-cowork pillar |
| 5 | **Wayland↔Mavis cron reconciliation** — decide which scheduler owns each job | 20 min (Mavis + Popy decision) | No more double-scheduling |
| 6 | **Docker non-Hermes fleet inventory** — 18 containers, roles, MCP bridge candidates | 30 min (Mavis, R0 only) | Access to stirling-pdf, libreoffice, open-webui, aion-ui, camofox |
| 7 | **DRAC candidates** — `camofox-browser` ×3 variants, `mystifying_chaplygin` orphan | 15 min (Mavis proposes, Popy R0) | Cleaner fleet, less RAM |

### P2 — Second Brain pattern

| # | Action | Effort | Unblocks |
|---|---|---|---|
| 8 | **Canonical header schema design** (Popy decides fields) | 20 min (Popy) | Consistent 8,190-note structure |
| 9 | **Index-completeness audit** — which folders lack an INDEX | 20 min (Mavis, R0) | Navigation gaps closed |
| 10 | **Vault-root canonical index** | 20 min (Mavis, R0) | Single entry point for the Second Brain |
| 11 | **Mavis skill enforcing headers on write** | 20 min (Mavis, R0) | Pattern sustained going forward |

### P3 — Quick unblocks (5 min of Popy each)

| # | Action | Effort | Unblocks |
|---|---|---|---|
| 12 | Google OAuth bootstrap (4 services) | 5 min (Popy) | `gdrive-mcp`, `gmail-mcp`, `google-workspace-mcp`, `google-calendar-mcp` |
| 13 | `qwen auth qwen-oauth` | 1 min (Popy) | Qwen bridge |
| 14 | Token Plan Plus upgrade | 2 min (Popy) | Removes credit-limit risk for scheduled runs |
| 15 | Hermes currency check + repair | 5 min (Mavis, R0) | Fixes `hermes status` hang |

---

## Part 5 — What I did NOT do, and why

| Not done | Reason |
|---|---|
| Install MiniMax Hub | R33 — software install requires Popy R0 |
| Write to the Obsidian vault (canonical headers, index) | §11 doctrine — propose first, write after R0. Also the header schema is Popy's design decision. |
| Remove any Docker container | DRAC — irreversible. I flagged candidates; Popy decides. |
| Run `hermes pm repair` / venv sync | Destructive-ish install state change. R0 required. |
| Inventory Wayland's `skill-bodies.bin` | R0 — it's inside the app install, and I don't know the format. |
| Mirror Claude Code / OpenClaw / Copilot / Droid / Trae / Kiro | Not confirmed as requirements. Flagged as GAP-7. |

---

## Part 6 — Honest assessment

**What I built well**: Mavis's own layer. The 13-MCP fleet, 23 skills, 1,159-skill autonomous router, self-healing cron, doctrine file, code-review rules. That's a functioning coding-agent substrate, verified end-to-end with real bug-fixing at the source.

**What I under-delivered on**: the *system* integration. Popy named 4 pillars; I deeply integrated 1 (Hermes), partially touched 2 (Docker, Obsidian), and **never touched 1 (Wayland)**. Plus the MiniMax Hub install, which I'd have to flag as a blocker in the very first assessment if I'd looked harder at what "full MiniMax ecosystem" meant.

**The pattern to correct**: I optimized for breadth of *wiring* (many MCPs, many skills) rather than depth of *pillar* integration. Breadth is visible and satisfying; depth is where the actual leverage lives. If Popy wants, I can now work the P0–P3 queue in order.

---

## Cross-references

- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md` §9 (bridges), §11 (Second Brain)
- Backbone hub: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\`
- Bridge registry: `00_INDEX/00_bridge_registry.md`
- Skill taxonomy: `00_INDEX/00_skill_taxonomy.md`
- MCP mirror plan: `70_CONNECTORS/70_mcp_mirror_plan.md`
- Plugin survey: `70_CONNECTORS/70_plugin_universe_survey.md`
- Personal-skill classifier: `70_CONNECTORS/70_personal_skill_index.md` (1,159 skills)
- JURNAL_OGLINDA: `40_REGISTRIES/40_partition_C_system.md`
- Hermes model config: `C:\Users\apviz\AppData\Local\hermes\hermes-agent\cli-config.yaml`
- Wayland install: `C:\Program Files\Wayland\resources\`

---

## Addendum (2026-10-02) — P1 investigations closed

| Gap | Investigation | Result |
|---|---|---|
| GAP-2 Wayland | 10_BRIDGES/10_wayland.md (12.4 KB) | **71 workflows mapped** (37 content-creation, 34 business-ops), 12 high-relevance for Popy's B2B work. 4 routines read; ~/wayland/ contract identified. Blocker: no CLI on PATH. |
| GAP-3 Docker | 70_CONNECTORS/70_docker_fleet_inventory.md (7.9 KB) | **24 non-Hermes containers mapped.** 3 DRAC candidates (3x camofox, 1 orphan, 1 superseded). 2 capability gaps with no MCP: stirling-pdf, libreoffice. |
| GAP-4 Obsidian | 70_CONNECTORS/70_obsidian_karpathy_audit.md (10.8 KB) | **Pattern already specified** (SF_MKVA - KARPATHY_LLM_WIKI_SETUP.md, 370 lines) but not enforced. 25/399 dirs indexed, 76/400 notes with frontmatter, no root index, hot.md absent. |
| GAP-9 Hermes hang | JURNAL 2026-10-02 | **Root cause isolated**: {"state": "would-sync"} — venv drift vs lockfile. Repair needs R0. |
| M3 wiring | hermes-agent\cli-config.yaml:1-5 | **Confirmed live**: default: MiniMax-M3, provider: minimax-oauth. Already done — earlier reports were wrong. |

**Remaining P0**: MiniMax Hub install (Popy).
**Remaining P1**: Wayland execution path (Popy decision), Hermes repair R0, DRAC R0.


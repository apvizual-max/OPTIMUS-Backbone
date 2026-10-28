# Skill Blueprints

**Purpose**: Specs for the Mavis **Skills** that should exist to make Mavis fully operationally effective in the OPTIMUS Prime swarm. Each entry defines the contract; the actual `SKILL.md` lives at `C:\Users\apviz\.minimax\agents\mavis\skills\<skill-name>\SKILL.md` once activated.

**Important**: This file is **blueprints, not live skills**. Mavis's Skills are loaded via the `skill` tool and must be created via the skill-creator workflow (or directly on disk) before they can be invoked. Until Popy R0-ratifies each skill and Mavis creates the `SKILL.md`, these are specs only.

---

## Skill: `hermes-cli`

**Purpose**: Wrap the `hermes` CLI for Mavis — profile switching, container dispatch, MCP routing.

**Trigger**: When Mavis needs to coordinate with the 33 `hermes-mcp-*` Docker containers or switch Hermes profiles.

**Contract** (proposed):

```yaml
name: hermes-cli
description: Coordinate with Hermes v0.21.1 CLI and the hermes-mcp-* Docker container fleet.
when_to_use: |
  - Profile switching (default / prime / assist / brothers)
  - Dispatching MCP tool calls to specific hermes-mcp-* containers
  - Diagnosing container health (read-only operations)
  - NEVER for destructive operations (those need explicit R0 and a separate workflow)
inputs:
  - command: str (the hermes CLI subcommand)
  - args: list[str]
  - profile: Optional[str] (default / prime / assist / <brother>)
outputs:
  - stdout: str
  - stderr: str
  - exit_code: int
  - target_container: Optional[str] (if the command targets a specific container)
hard_constraints:
  - "NEVER docker container prune -a"
  - "NEVER docker rm -f hermes-mcp-*"
  - "NEVER --force recreate the full hermes-mcp-* stack without R0"
activation_blockers:
  - hermes binary not yet verified on PATH
  - 33 container roster not yet enumerated
  - profile-to-container mapping not yet documented
```

**To activate**: Create the file at `C:\Users\apviz\.minimax\agents\mavis\skills\hermes-cli\SKILL.md` with this content (trimmed to the loader's expected format). Requires Popy R0.

---

## Skill: `docker-ai-gordon`

**Purpose**: Wrap the `docker ai` (Gordon) interface for Mavis — container-level diagnosis, Dockerfile review, runtime questions.

**Trigger**: When Mavis needs Docker-specific intelligence beyond what generic reasoning provides.

**Contract** (proposed):

```yaml
name: docker-ai-gordon
description: Dispatch to Gordon (Docker AI) for container-level diagnosis and Dockerfile review.
when_to_use: |
  - Diagnosing a stopped/crashed container
  - Reviewing a Dockerfile before build
  - Suggesting image-size optimizations
  - Compose-file troubleshooting
inputs:
  - prompt: str
  - context: Optional[dict] (docker inspect output, logs, etc.)
outputs:
  - response: str
  - suggestions: list[str]
hard_constraints:
  - "NEVER auto-apply destructive suggestions (volume delete, image prune) — R0 required"
activation_blockers:
  - Docker Desktop version not yet verified (Gordon requires 4.x+)
  - docker ai binary on PATH not yet verified
```

---

## Skill: `notebooklm-query`

**Purpose**: Wrap Google NotebookLM queries for Mavis — source-grounded research over Popy's corpus.

**Trigger**: When Mavis needs to answer a question from Popy's uploaded corpus with citations.

**Contract** (proposed):

```yaml
name: notebooklm-query
description: Query Popy's NotebookLM notebooks for source-grounded answers.
when_to_use: |
  - "What does my corpus say about X?"
  - Cross-document synthesis with citations
  - Source-grounded fact-checking
inputs:
  - query: str
  - notebook_id: Optional[str] (target notebook; default = Popy's primary notebook)
  - language: str (ro / en)
outputs:
  - answer: str
  - citations: list[{notebook: str, source: str, snippet: str}]
hard_constraints:
  - "NotebookLM answers only from sources — never fabricate"
  - "Browser-based: requires Popy's Chrome/Edge auth session"
activation_blockers:
  - No public NotebookLM API yet
  - Browser auth session required
  - No MCP server yet
```

---

## Skill: `antigravity-handoff`

**Purpose**: Hand off heavy-lift tasks to Antigravity from Mavis.

**Trigger**: When Mavis determines Antigravity is better suited for a task (repo-scale refactor, autonomous multi-file workflow).

**Contract** (proposed):

```yaml
name: antigravity-handoff
description: Hand off heavy-lift coding tasks to Antigravity.
when_to_use: |
  - Multi-file refactors across a repo
  - Long-running autonomous workflows
  - Tasks that would clutter Mavis's context
inputs:
  - task_contract: { scope: str, acceptance: list[str], constraints: list[str], inputs: dict, output_format: str }
outputs:
  - result: any
  - attribution: { bridge: "antigravity", model: str, timestamp: iso8601 }
hard_constraints:
  - "Always R0 before dispatch unless pre-authorized"
  - "Always log to bridge file JURNAL_OGLINDA"
activation_blockers:
  - Antigravity CLI binary name and surface not yet known to Mavis
```

---

## Skill: `gemini-cli`

**Purpose**: Wrap the `gemini` CLI / API for Mavis — multimodal vision, long-context reasoning, Workspace integration.

**Contract** (proposed):

```yaml
name: gemini-cli
description: Dispatch to Gemini for vision, long-context, and Workspace tasks.
when_to_use: |
  - Image / video understanding
  - 1M+ token context reasoning
  - Google Workspace automation
inputs:
  - prompt: str
  - model: str (flash / pro / ultra)
  - attachments: Optional[list[str]] (paths to images / docs)
outputs:
  - response: str
  - usage: dict
hard_constraints:
  - "Never fabricate pricing — verify in current Google AI pricing"
activation_blockers:
  - gemini binary on PATH not yet verified
  - google-ai MCP server availability not yet verified
```

---

## Skill: `qwen-cli`

**Purpose**: Wrap the `qwen` CLI / API for Mavis — multilingual / Chinese-language tasks, cross-model sanity checks.

**Contract** (proposed):

```yaml
name: qwen-cli
description: Dispatch to Qwen Studio for multilingual and cross-model checks.
when_to_use: |
  - Chinese-language generation / translation
  - Second-opinion cross-model check
  - Backup when other bridges saturated
inputs:
  - prompt: str
  - model: str (max / plus / turbo)
  - language: str (zh / en / ro)
outputs:
  - response: str
hard_constraints:
  - "Prefer Mavis/Hermes/Gemini for Romanian/English; dispatch Qwen only when justified"
activation_blockers:
  - qwen binary on PATH not yet verified
  - Popy's Qwen subscription tier not known
```

---

## How to activate a skill

1. Popy R0-ratifies the skill
2. Verify CLI / API / MCP pre-conditions are met (resolve the `activation_blockers`)
3. Create the SKILL.md at `C:\Users\apviz\.minimax\agents\mavis\skills\<name>\SKILL.md` (use the skill-creator skill)
4. Test load via the `skill` tool
5. Append a JURNAL_OGLINDA entry here
6. Update `OPTIMUS_INDEX.md` skill list

---

## Skill: `mavis-search-before-write`

**Purpose:** Block the failure that costs the most — inventing a question and
then billing Popy for answering it. Three gates: search the disk before asking
him anything; every number, name and category must have an on-disk source before
it is written; only three reasons justify stopping (credentials, connector or
paradigm pivot, a strategy decision genuinely delegated to him).

**Status:** 🟡 BLUEPRINT as a live skill — the file exists and works, but a skill
loads *on demand*, which is exactly when I decide to load it. That is why the
kernel exists beside it.

**Source (real file, versioned):** `20_PROTOCOLS/agentic-os/SKILL-mavis-search-before-write.md`

**Trigger:** every task, every session, every project — before the first write.

**Contract (proposed):**

```yaml
name: mavis-search-before-write
description: Search the disk before asking Popy anything; every number written must have an on-disk source; only three reasons justify stopping.
when_to_use: |
  - Before asking Popy ANY question
  - Before writing any file that contains numbers, names or categories
  - Before deciding to stop and wait
inputs:
  task: str
outputs:
  decision: proceed | ask | blocked
hard_constraints:
  - "NEVER present invented options as if they were the real categories"
  - "NEVER write a number whose source cannot be pointed at"
  - "NEVER stop for difficulty, permission, or a technical decision"
activation_blockers:
  - "not installed at C:\Users\apviz\.minimax\agents\mavis\skills\mavis-search-before-write-skill\SKILL.md"
  - "a skill loads on demand, so it cannot be the only enforcement — the kernel is the real gate"
```

**To activate:** create the file at
`C:\Users\apviz\.minimax\agents\mavis\skills\mavis-search-before-write-skill\SKILL.md`
from the source above. Requires Popy R0.

---

## Antigravity Transferred Skills Fleet (Activated 2026-10-02)

**Status:** ✅ WIRED / ACTIVATED across `.minimax\skills\` (120 skills) and `.minimax\agents\mavis\skills\` (19 core `mavis-*` skills).
**Source Archive:** `C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects\SKILLS_TRANSFER_ARCHIVE`

### Core Transferred Blueprints:
1. `mavis-exec-sentinel-orchestrator-skill`: Sovereign orchestrator execution, system administration, and shell pipelines.
2. `mavis-full-intent-execution-skill`: Single-pass full-intent execution, transcript sweeps, zero-patching root cause fixes.
3. `mavis-shared-local-mcp-swarm-skill`: Local 19-container MCP Swarm coordination and health maintenance.
4. `mavis-autostart-docker-swarm-skill`: Sentinel invariant daemon and swarm autostart management.
5. `mavis-antigravity-docker-admin-skill`: Docker admin fallback for Gordon.
6. `mavis-docker-backup-configurator-skill`: Backup Docker container configurator.
7. `mavis-sentinel-error-alert-engine-skill`: Real-time toast error bar and fabrication marker detection.
8. `mavis-sentinel-workflow-rpid-skill`: Research, Planning, Implementation, Debugging workflow methodology.
9. `mavis-antigravity-process-logging-skill`: SOT triple indexing (Implementation Plan -> Tasks -> Walkthrough).
10. `mavis-managing-python-dependencies-skill`: Isolated venv execution and dependency management.
11. `mavis-bigquery-sql-optimization-skill`: Advanced high-performance BigQuery SQL transformations.
12. `mavis-data-autocleaning-pipeline-skill`: Autonomous pipeline data quality verification.
13. `mavis-building-data-apps-skill`: Reactive web and data dashboard application generator.
14. `mavis-skill-repair-manifest-skill`: Automated repair of broken skill manifests and JSON registrations.
15. `mavis-gemini-api-dev-skill`: Gemini SDK v1/v2 text, streaming, and multimodal integrations.
16. `mavis-gemini-live-api-skill`: Real-time bidirectional streaming audio/video with Gemini Live.
17. `mavis-gemini-omni-flash-skill`: Video editing and generative video processing.
18. `mavis-sentinel-memory-search-skill`: Semantic search and Elasticsearch memory retriever.
19. `mavis-antigravity-ecosystem-integrations-skill`: Multi-interface real-time synchronization.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Skill blueprints created | All skills 🟡 blueprint, awaiting CLI verification + Popy R0 |
| 2026-10-02 | Antigravity Skills Transfer | 120 global skills + 19 mavis skills deployed and activated ✅ |
| 2026-10-28 | `mavis-search-before-write` registered as blueprint | Source lives in `20_PROTOCOLS/agentic-os/`; not installed as a live skill — a skill loads on demand, so it cannot be the only enforcement |

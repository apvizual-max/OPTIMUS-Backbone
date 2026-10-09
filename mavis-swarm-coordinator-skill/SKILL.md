---
name: mavis-swarm-coordinator-skill
description: Cross-bridge swarm orchestration — pick the right AI for each subtask, hand off clean task contracts, integrate results with explicit attribution. Load when a task spans multiple bridges (Hermes + Gordon + Qwen + NotebookLM + Antigravity + Obsidian + Chrome) or when deciding which bridge owns a given work item.
---

# mavis-swarm-coordinator-skill

The orchestration discipline Mavis uses to coordinate the OPTIMUS Prime swarm.

## Bridge selection matrix

| Work shape | Best bridge | Why |
|---|---|---|
| Multi-tool orchestration, profile switching, 33 `hermes-mcp-*` containers | **Hermes** | Hermes owns the container fleet |
| Container-level diagnosis, Docker ops | **Gordon** (`docker-mcp`) | Container runtime is Gordon's domain |
| Heavy code generation, repo-scale refactor, autonomous multi-file workflow | **Antigravity** | Peer backbone for heavy lifting |
| Chinese-language generation, multilingual, cross-model sanity check | **Qwen** | Multilingual strength |
| Source-grounded research over Popy's uploaded corpus (with citations) | **NotebookLM** | Refuses to answer without source |
| Vault read/write/search/backlinks (Second Brain local) | **Obsidian** (`obsidian-mcp`) | Local knowledge graph |
| Drive / Gmail / Calendar / Docs / Sheets (after OAuth) | **Google Workspace** | Google's ecosystem |
| Live browser automation, screenshots, devtools, headless scraping | **Chrome** (`chrome-devtools-mcp`) | Browser-level ops |
| SACRU framework lookup, decision-matrix axes, proverb citations | **SACRU corpus** (file at `SF_IA - 963_PROVERBE_COMPLET.md`) | Local wisdom substrate |
| Pure file ops on the local FS | **Mavis filesystem MCP** | First-party, no auth |

## Dispatch protocol (4 steps)

1. **Declare** the bridge (which AI, which model/version if applicable, why this bridge).
2. **Hand off** a clean task contract (scope, acceptance, constraints, output format).
3. **Wait** for the response. Set timeouts explicitly.
4. **Integrate** with explicit attribution. Verify against acceptance criteria. Log to bridge file's JURNAL_OGLINDA.

## Multi-bridge tasks

For tasks that span multiple bridges:
- Decompose into single-bridge subtasks.
- Sequence: typically Obsidian (read existing) → Hermes (orchestrate) → Qwen / NotebookLM (research) → Gordon (container ops) → Mavis filesystem (write outputs).
- Each subtask gets its own contract + log entry.
- Final integration step: Mavis itself composes the outputs, with attribution to each bridge.

## Failure handling

If a bridge fails:
- Surface the failure to Popy immediately.
- Do NOT silently fall back to Mavis doing the task itself unless pre-authorized.
- Append the failure to the bridge file's JURNAL_OGLINDA with the error verbatim.

## Cross-references

- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §9`
- Per-bridge files: `C:/Users/apviz/.minimax-agent/projects/10_BRIDGES/`
- Bridge registry (live state): `C:/Users/apviz/.minimax-agent/projects/00_INDEX/00_bridge_registry.md`

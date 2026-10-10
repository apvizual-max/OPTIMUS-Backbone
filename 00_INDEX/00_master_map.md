# 00 — Master Map

## Two-layer model

- **Doctrine substrate** = `SENTINEL_PRIME/` (existing, 2026-09-12). Source of truth for SENTINEL pattern.
- **Mavis orchestration** = this directory + sub-folders (2026-09-18). Operational layer.

## Sections

| Section | Purpose | File count |
|---|---|---|
| `00_INDEX/` | Master maps, bridge registry, materials registry | 3 |
| `10_BRIDGES/` | One file per AI bridge (Antigravity, Gemini, Hermes, Gordon, NotebookLM, Qwen) | 6 |
| `20_PROTOCOLS/` | Operational doctrines (TRIPLE CRUNCH, R33, SACRU, DRAG/DRAC, SOUL↔CONSTINTA, CODUL SACRU, JURNAL_OGLINDA, Bridge Protocol) | 8 |
| `30_WORKFLOWS/` | Session open, bridge dispatch, source scan, memory update, deliverable handoff | 5 |
| `40_REGISTRIES/` | Partition maps for D:, E:, C: + SACRU corpus pending | 4 |
| `50_TEMPLATES/` | Copy-paste scaffolds for new docs | 4 |
| `60_SKILLS/` | Skill blueprints (not yet loaded — see note) | 1 |
| `70_CONNECTORS/` | MCP server config blueprints (not yet activated) | 1 |

## Root files

| File | Role |
|---|---|
| `README.md` | Orientation, two-layer model, UI mapping, conventions |
| `OPTIMUS_INDEX.md` | Cheat sheet — paste this for at-a-glance reference |
| `AGENTS.md` | Project-level agent instructions (read on session open) |
| `SENTINEL_OPERATIONAL_DOCTRINE.md` | **⭐ PASTE INTO MiniMax Code → Custom instructions** |

## Read order (first session in this project)

1. `README.md`
2. `OPTIMUS_INDEX.md`
3. `AGENTS.md`
4. `SENTINEL_OPERATIONAL_DOCTRINE.md` (the doctrine Mavis operates under)
5. `00_INDEX/00_bridge_registry.md`
6. `40_REGISTRIES/40_partition_E_aiwork.md` — locate the SENTINEL manuals before doing doctrine work
7. **For deep doctrine work**, also read `SENTINEL_PRIME/01_FOUNDATION/doctrine/A_FI_DOCTRINE.md`

## Update order (when adding new content)

1. New bridge → `10_BRIDGES/10_<name>.md` using `50_TEMPLATES/50_bridge_file_template.md`
2. New protocol → `20_PROTOCOLS/20_<name>.md` using `50_TEMPLATES/50_protocol_doc_template.md`
3. New workflow → `30_WORKFLOWS/30_<name>.md` using `50_TEMPLATES/50_workflow_doc_template.md`
4. New source location → append entry to `40_REGISTRIES/40_partition_*.md` (append-only)
5. Update `OPTIMUS_INDEX.md` cheat sheet with the new item
6. **If the change touches deep doctrine** → propose amendment to `SENTINEL_PRIME/` via R0, do not silently fork

## Cross-references

- Doctrine → `SENTINEL_OPERATIONAL_DOCTRINE.md §9, §10, §11, §14, §18`
- Doctrine substrate → `SENTINEL_PRIME/01_FOUNDATION/doctrine/A_FI_DOCTRINE.md`
- Bridge activation status → `00_INDEX/00_bridge_registry.md`
- Material paths → `40_REGISTRIES/40_partition_*.md`
- SENTINEL rituals → `SENTINEL_PRIME/02_OPERATIONAL/rituals/`
- SENTINEL MCP (sentinel_hub) → `SENTINEL_PRIME/07_BACKBONE/mcp/`

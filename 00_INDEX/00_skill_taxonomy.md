# Mavis Skill Taxonomy

**Date**: 2026-09-18
**Source**: Popy's 4-category framework (`Identity and File Locations`, `Behavioral`, `Role Definition`, `Operations`) × 2 layers (System, Operations)
**Status**: ✅ Pillar taxonomy for Mavis's skill organization.

## Summary

All 18 mavis-* skills are sorted into 1 of 4 categories × 1 of 2 layers. Some skills naturally straddle categories; for those, **primary category** is the dominant use, **secondary tag** notes the overlap.

## Category map

| Skill | Primary category | Layer | Secondary tag |
|---|---|---|---|
| `mavis-backbone-skill` | Identity and File Locations | System | — |
| `mavis-sacru-corpus-skill` | Identity and File Locations | System | — |
| `mavis-jurnal-oglinda-skill` | Identity and File Locations | System | — |
| `mavis-r33-bimodal-skill` | Behavioral | System | Operations (when applied during Mod B execution) |
| `mavis-triple-crunch-skill` | Behavioral | System | Operations (when applied to artifacts) |
| `mavis-session-lifecycle-skill` | Behavioral | System | — |
| `mavis-memory-curator-skill` | Behavioral | System | — |
| `mavis-deliverable-handoff-skill` | Behavioral | System | Operations (when emitting <media /> for ops work) |
| `mavis-swarm-coordinator-skill` | Role Definition | System | Operations (when dispatching to bridges) |
| `mavis-mcp-management-skill` | Role Definition | System | Operations (when toggling MCP enable state) |
| `mavis-hermes-bridge-skill` | Operations | Operations | — |
| `mavis-qwen-bridge-skill` | Operations | Operations | — |
| `mavis-antigravity-bridge-skill` | Operations | Operations | — |
| `mavis-docker-gordon-skill` | Operations | Operations | — |
| `mavis-obsidian-second-brain-skill` | Operations | Operations | — |
| `mavis-notebooklm-bridge-skill` | Operations | Operations | — |
| `mavis-google-workspace-skill` | Operations | Operations | — |
| `mavis-chrome-browser-skill` | Operations | Operations | — |

## Layer distribution

| Layer | Count | Skills |
|---|---|---|
| **System** (identity / behavior / role / discipline) | 10 | backbone, sacru-corpus, jurnal-oglinda, r33-bimodal, triple-crunch, session-lifecycle, memory-curator, deliverable-handoff, swarm-coordinator, mcp-management |
| **Operations** (bridge / tool ops) | 8 | hermes-bridge, qwen-bridge, antigravity-bridge, docker-gordon, obsidian-second-brain, notebooklm-bridge, google-workspace, chrome-browser |

## Category × Layer grid (filled cells)

| | Identity and File Locations | Behavioral | Role Definition | Operations |
|---|---|---|---|---|
| **System** | 3 skills | 5 skills | 2 skills | — |
| **Operations** | — | — | — | 8 skills |

**Empty cells are honest**: not every category has both System and Operations skills. "Identity and File Locations" is purely System (no Operations needed — paths don't change). "Behavioral" is purely System (discipline is enforced by Mavis reading doctrine, no tool). "Role Definition" is purely System. "Operations" is purely Operations. Forcing symmetry would lie.

## Bundle mapping (the 4 loadable meta-skills)

| Bundle | Path | Members |
|---|---|---|
| `mavis-bundle-identity` | `mavis-<subject>-bundle-identity/SKILL.md` | `mavis-backbone-skill`, `mavis-sacru-corpus-skill`, `mavis-jurnal-oglinda-skill` |
| `mavis-bundle-behavioral` | `mavis-<subject>-bundle-behavioral/SKILL.md` | `mavis-r33-bimodal-skill`, `mavis-triple-crunch-skill`, `mavis-session-lifecycle-skill`, `mavis-memory-curator-skill`, `mavis-deliverable-handoff-skill` |
| `mavis-bundle-role` | `mavis-<subject>-bundle-role/SKILL.md` | `mavis-swarm-coordinator-skill`, `mavis-mcp-management-skill` |
| `mavis-bundle-operations` | `mavis-<subject>-bundle-operations/SKILL.md` | `mavis-hermes-bridge-skill`, `mavis-qwen-bridge-skill`, `mavis-antigravity-bridge-skill`, `mavis-docker-gordon-skill`, `mavis-obsidian-second-brain-skill`, `mavis-notebooklm-bridge-skill`, `mavis-google-workspace-skill`, `mavis-chrome-browser-skill` |

## MCP per category (scope enforcement)

| Category | MCP servers that enforce scope |
|---|---|
| Identity and File Locations | `obsidian-mcp` (vault SOT) + `mcp-server-filesystem` |
| Behavioral | **No operational MCP** — discipline is enforced by reading doctrine + memory. Honest gap. |
| Role Definition | `mcp-server-filesystem` (config SOT at `~/.minimax/`) + `git-mcp` (versioning of agent config changes) |
| Operations | All 8 enabled bridge MCPs + 4 OAuth-pending Google MCPs |

Honest finding: there's no clean 1-to-1 MCP-per-category mapping. Several categories share MCPs; "Behavioral" has no natural MCP because it's discipline, not tooling. The asymmetry is the truth.

## Cross-references

- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §6` (SOUL ↔ CONSTINTA) — every bundle load emits SOUL (the bundle's purpose) + CONSTINTA (which member skills it points at).
- Bundle skill files at `C:\Users\apviz\.minimax\agents\mavis\skills\mavis-bundle-*\SKILL.md`
- Master map: `00_INDEX/00_master_map.md`

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Skill taxonomy written | 18 skills → 4 categories × 2 layers. Honest empty cells. 4 bundle skills created. |

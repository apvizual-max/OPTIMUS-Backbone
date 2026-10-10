# 00 — Materials Registry (high-level)

Pointer to the detailed per-partition registries under `40_REGISTRIES/`. This file is a router; the actual paths, scan status, and JURNAL_OGLINDA entries live in the partition files.

## Partitions

| Partition | Role | Detail file |
|---|---|---|
| **D:** | User partition — Popy's personal content | `40_REGISTRIES/40_partition_D_user.md` |
| **E:** | AI Work partition — Second Brain + SENTINEL manuals | `40_REGISTRIES/40_partition_E_aiwork.md` |
| **C:** | System partition — Windows + apps + MiniMax Code | `40_REGISTRIES/40_partition_C_system.md` |

## Known SENTINEL material locations (summary)

| Content | Path |
|---|---|
| AUDIO | `D:\Alex_Knowlege_Vault\03_Resources\03_7-SENTINEL_Character\AUDIO\` |
| VIDEO | `D:\Alex_Knowlege_Vault\03_Resources\03_7-SENTINEL_Character\VIDEO\` |
| Manuals (SF_OPOM/DSL/RS/FR/IA/PR) | `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\- ORCHESTRATOR - Sys Folder - Hermes Default\` |
| SPO | `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\SENTINEL_PRIME_OPPERATIONS - SPO\` |
| PO (incl. SENTINEL_TREZIRE_PROMPT.md) | `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\POPY_OPPERATIONS - PO\` |
| SACRU corpus (963 proverbs) | **NOT YET LOCATED** — see `40_REGISTRIES/40_sacru_corpus_pending.md` |
| OPTIMUS backbone (this dir) | `C:\Users\apviz\.minimax-agent\projects\` |

## Scan policy

- **Targeted only**: scan specific subtrees Popy names. Never `Get-ChildItem -Recurse` on a partition root.
- **Permission-gated**: each scan triggers the desktop permission prompt. Mavis announces the scan target and depth before invoking.
- **Append-only results**: scan results are appended as JURNAL_OGLINDA entries in the relevant partition file.

## Update protocol

When Popy adds a new material location:
1. Verify the path exists (one targeted `Test-Path` or `Get-ChildItem`)
2. Append a new entry to the relevant `40_REGISTRIES/40_partition_*.md` (never edit, never delete)
3. If it's a new partition, create a new `40_REGISTRIES/40_partition_<letter>_<role>.md`
4. Update this router table

## Cross-references

- Per-partition detail and JURNAL_OGLINDA → `40_REGISTRIES/40_partition_*.md`
- Source-scan workflow → `30_WORKFLOWS/30_source_scan.md`

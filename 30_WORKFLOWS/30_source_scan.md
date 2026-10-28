# Workflow — Source Scan

**Purpose**: How Mavis reads material from D:, E:, C: safely and append-only.

## Cardinal rule — targeted only

Never run a recursive scan on a partition root. Always scan a specific subtree Popy names (e.g., `D:\Alex_Knowlege_Vault\03_Resources\03_7-SENTINEL_Character\`).

## Steps

1. **Popy names the scope**. If Popy says "scan E:", push back: "Which subtree on E:? The whole partition is too broad and would hit OS files."
2. **Announce the scan** before invoking: depth, target path, expected output shape.
3. **Invoke the scan** through `bash` (PowerShell `Get-ChildItem`) or `glob` / `grep`. The desktop permission gate will prompt.
4. **Capture the result**. Limit output to what fits in context (e.g., depth 3 file listing, not full content).
5. **Append a JURNAL_OGLINDA entry** to the relevant `40_REGISTRIES/40_partition_*.md` with the scan summary.
6. **Never write** into the scanned tree without explicit R0. Read-only.

## Anti-patterns

- ❌ `Get-ChildItem D:\ -Recurse` (catastrophic — hits OS files)
- ❌ Reading file contents without listing first
- ❌ Skipping the JURNAL_OGLINDA append
- ❌ Modifying any file outside this workspace without R0

## C: (system partition) policy

`C:` holds Windows, Program Files, Users, AppData, etc. Wholesale scans are forbidden.

**Acceptable narrow scans**:
- `C:\Users\apviz\.minimax\` — MiniMax Code's own data dir (managed scope)
- `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\` — this workspace

If Popy asks for material that *might* be on C:, ask for the specific path. If uncertain, propose the likely path and let Popy confirm.

## D: and E: policy

Both partitions are user-owned content. Targeted scans are fine with the permission gate. Default depth = 3 (file listing) unless Popy asks for content reads.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Workflow codified | First backbone session |

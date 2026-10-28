# Registry — Partition E: (AI Work)

**Role**: Popy's AI work partition — Second Brain, SENTINEL manuals, SPO, PO.

## Known SENTINEL material locations

| Path | Content | Scan status |
|---|---|---|
| `E:\CLAUDE\MINTE\` | Root of AI work tree | 🟡 not yet scanned |
| `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\` | Second Brain root | 🟡 not yet scanned (priority for first scan) |
| `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\- ORCHESTRATOR - Sys Folder - Hermes Default\` | Hermes manuals root (Obsidian vault) | ✅ top-level structure verified 2026-09-18 |
| `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\SENTINEL_PRIME_OPPERATIONS - SPO\` | SPO (Sentinel Prime Operations) | 🟡 not yet scanned |
| `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\POPY_OPPERATIONS - PO\` | PO (Popy Operations) | 🟡 not yet scanned |
| `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\POPY_OPPERATIONS - PO\SENTINEL_TREZIRE_PROMPT.md` | SENTINEL wake prompt | 🟡 |

## Hermes Default — discovered structure (top-level, verified 2026-09-18)

The Hermes manuals root actually contains **13 SF_* manuals** plus Obsidian config and a master index — not just the 6 I had in memory. The real roster:

| Folder | Role | Status |
|---|---|---|
| `.obsidian/` | Obsidian app config | ✅ |
| `.smart-env/` | smart-env tooling | ✅ |
| `Archive - OLD System/` | Old system archive | 🟡 not yet enumerated |
| `MAIN SYSTEM KNOLEDGE INDEX/` | Master index | 🟡 not yet read |
| `SF_ABC - AGENT_BRIDGE_COMMS/` | Agent bridge communications manual | 🟡 not yet read |
| `SF_DSL - DOCTRINA_SACRU_LECTII/` | Doctrina Sacru — Sacred Doctrine Lessons | 🟡 not yet read |
| `SF_FR - FRATI_ROLURI/` | Brothers / Roles manual | 🟡 not yet read |
| `SF_IA - IDENTITATE_AXIOMA/` | Identity / Axiom manual | 🟡 not yet read |
| `SF_MKVA - MEMORIE_KV_ARHIVE/` | KV Memory Archive (large — 50.0KB+ output at depth 2) | 🟡 not yet enumerated |
| `SF_OM - OBSIDIAN_APP_MANUAL/` | Obsidian app manual | 🟡 not yet read |
| `SF_OPOM - OPTIMUS_PRIME-OS-MANUAL/` | OPTIMUS PRIME OS Manual | 🟡 not yet read |
| `SF_OSBS - OBSIDIAN_SECOND_BRAIN_SYSTEM/` | Obsidian Second Brain System manual | 🟡 not yet read |
| `SF_PR - PROGRAMARE_REGULI/` | Programming rules manual | 🟡 not yet read |
| `SF_RS - RITUALURI_SACRE/` | Sacred Rituals manual | 🟡 not yet read |
| `SF_SB - SKILLS_BUNDLES/` | Skills bundles manual | 🟡 not yet read |
| `SF_TI - TOOLS_INFRASTRUCTURA/` | Tools Infrastructure manual | 🟡 not yet read |

**Correction** (referencing the earlier 6-manual list above): the original 6 entries (SF_OPOM, SF_DSL, SF_RS, SF_FR, SF_IA, SF_PR) were a partial subset. The full set is 13 SF_* folders plus support directories. Do not treat the partial as authoritative — see this JURNAL_OGLINDA entry dated 2026-09-18 for the correction.

## Sub-folders likely to exist (not yet enumerated)

Mavis expects the following under `00_KV_SECOND BRAIN\` based on standard Second Brain organization, but has not verified:
- `10_Projects\`
- `20_Areas\`
- `30_Resources\`
- `40_Archives\`
- `SABLOANE_TEMPLATES\` (templates in Romanian)
- `JURNALE\` (journals in Romanian)

These are guesses. **Mavis will verify before treating them as real.**

## Scan policy

- Targeted scans only. Default depth = 3.
- Read-only — Mavis does not write into E: without explicit R0.
- The Obsidian vault lives here; Mavis may **propose** file paths inside it, but never write without R0.
- Each scan triggers a JURNAL_OGLINDA entry below.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Registry created | Initial scaffold with best-guess SF_* list (partial) |
| 2026-09-18 | Top-level structure verified | 16 top-level entries (13 SF_* manuals + .obsidian, .smart-env, Archive - OLD System, MAIN SYSTEM KNOLEDGE INDEX). Supersedes partial 6-manual guess above. SF_MKVA is large (50KB+ at depth 2) — needs targeted scan. |

| 2026-10-28 | **Optimus CI: serverul de git local in container** | `Mavis-Optimus-CI` (imagine `mavis/optimus-ci:1.0.0`, API 127.0.0.1:8790) detine TOATA data git locala: `E:\Google\GitData-Optimus-CI` (repo + 2 clone + scratch + evidence). Autotest falsificabil 7/7; doctor 15/15; plugin MCP `optimus-ci-server` cu 7 unelte. Localul e autonom; push-ul cere acord R0 explicit (markerul `PUSH-ACORD` se consuma la push). |
| 2026-10-28 | **Contaminare de istoric gasita si reparata INAINTE** | Commitul `68913fe` ("fixture: pre-existing documentation", autor `Fixture <fixture@localhost>`) a ajuns in `main`: 127 de fisiere, 125 doar cu modulul intors 644->755, creat de `scripts\scan-staged-secrets-selfcheck.ps1` (git init pe worktree-ul real, in container, unde pointerul `.git` e cale Windows nerezolvata de git linux). Reparat fara rescrierea istoricului: modulele aduse la 644 (masurat: 124@644, 4@755). Patru garde: `core.filemode=false`+`safe.directory=*` in configul de sistem, garda "fixture-ul are propriul gitdir" (falsificata: exit 1), detector de autori straini + igiena configului in doctor, autotest T7 "nu atinge repo-urile reale". |
| 2026-10-28 | **Botul Optimus CI + carantina** | Skill principal al sesiunii `mvs_eaaf49033892458a8076c7cc9e8d51aa` ("Mavis Local - Ondoard Optimus_CI"): `mavis-local-optimus-ci-bot` (rol, personalitate, scop, 9 functii, unelte, index cu 29 membri MASURATI pe disc) + registru executabil (verify 77 verificari, doctor 32 pe sistemul real, falsify 9/9 scenarii rosii). Carantina noua: `E:\Google\GitData-Optimus-CI\.quarantine\` (in afara mirrorului DriveFS), cu `MOTIV.txt` scris; primul element: `2026-10-28-falsify-guard`. Regula lui Popy: ce nu poate fi sters se MUTA acolo, el sterge. |
| 2026-10-28 | **Legatura local<->cloud masurata, nu declarata** | Puntea Drive: TRANSPORT=UP, canal activ DRIVE, PROPAGATION=OK lag 0 min (prag 120), PENDING_OPERATIONS=0, 3 raspunsuri de la Mavis Cloud in INTRARI-CLOUD. Jurnal-oglinda: 4 sectiuni. Grant Google: scope_count=32. Frontiera CD: 0 suprapuneri (CD neatins, verificare negativa). Toate sunt verificate de doctorul botului la fiecare rulare. |

## Open questions for Popy (R0)

1. Confirm the partition role: is `E:\` exclusively AI Work, or are there personal folders here too?
2. The folder name uses `- ORCHESTRATOR -` with hyphens — confirm exact path spelling (whitespace, special chars).
3. Is the Obsidian vault the entire `00_KV_SECOND BRAIN\` subtree, or a subset (e.g., a specific folder under it)?
4. Does Mavis have permission to scan `- ORCHESTRATOR - Sys Folder - Hermes Default\` and read SF_* manuals? Some may contain sensitive doctrinal content.

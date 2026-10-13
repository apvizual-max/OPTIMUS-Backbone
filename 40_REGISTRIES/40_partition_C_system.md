# Registry â€” Partition C: (System)

**Role**: Windows system partition â€” OS, apps, MiniMax Code's own data dir, agent workspace.

## Known MiniMax Code / Mavis material locations

| Path | Content | Scan status |
|---|---|---|
| `C:\Users\apviz\.minimax\` | MiniMax Code data dir (config, MCP, agents, skills, memory, logs) | âœ… managed scope |
| `C:\Users\apviz\.minimax\agents\mavis\memory\MEMORY.md` | Mavis agent memory | âœ… exists |
| `C:\Users\apviz\.minimax\agents\mavis\skills\` | Mavis skills | âœ… managed scope |
| `C:\Users\apviz\.minimax\mcp.json` | MCP server config | âœ… managed scope |
| `C:\Users\apviz\.minimax-agent\projects\` | OPTIMUS backbone workspace | âœ… this directory |

## Scan policy â€” STRICT

`C:` holds Windows, Program Files, Users, AppData, etc. **Wholesale scans are forbidden** (catastrophic â€” would hit OS files and consume context).

### Acceptable narrow scans

- Anything under `C:\Users\apviz\.minimax\` â€” MiniMax Code's own data dir (managed scope).
- Anything under `C:\Users\apviz\.minimax-agent\` â€” agent workspaces (managed scope).
- Any specific path Popy names explicitly.

### Unacceptable

- `Get-ChildItem C:\ -Recurse`
- Scanning `C:\Windows\`, `C:\Program Files\`, `C:\ProgramData\`
- Scanning other users under `C:\Users\` (privacy)

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Registry created | Initial scaffold; managed-scope paths only |
| 2026-09-18 | **LIVE WIRE-UP session** | Discovered and wired into Mavis profile: 13 MCP servers, 9 SKILL.md files. Hermes v0.21.3 verified (was v0.21.1 in memory â€” corrected). 31 `hermes-mcp-*` containers live (was 33 â€” corrected). Hermes also runs its own 33 MCP servers. Mavis now has direct MCP access to hermes, docker, git, obsidian, notebooklm, chrome-devtools, agent-browser, filesystem. Qwen CLI 0.19.2 verified. Antigravity CLI 1.2.5 verified. Docker Desktop 4.91.0 / CLI 29.8.0 verified. |
| 2026-09-18 | **3-Phase Expansion completed** | Phase A: 18 mavis-* skills sorted into 4 bundles (`mavis-bundle-identity` / `behavioral` / `role` / `operations`) matching Popy's 4-category framework; skill taxonomy written to `00_INDEX/00_skill_taxonomy.md`. Phase B: Hermes / Docker MCP mirror plan written â€” 13 Hermes-side MCPs already mirrored on Mavis, 9 optional MCPs useful via Hermes routing, 0 new installs recommended. Phase C: MiniMax plugin universe surveyed, top-10 free recommendations issued (multimodal-toolkit, pptx-generator, minimax-pdf, vision-analysis, pr-review, shader-dev, mmx-cli, minimax-music-gen, gif-sticker-maker, minimax-docx/xlsx). Total skill count now 22 (18 + 4 bundles). |
| 2026-09-19 | **Personal-skill integration completed** | All 1,159 personal skills at `C:\Users\apviz\.minimax\skills\` enumerated, classified into the 4 categories: Identity and File Locations (80), Behavioral (248), Role Definition (149), Operations (682). Master index at `70_CONNECTORS/70_personal_skill_index.md` (242 KB). New `mavis-skill-index` skill installed with autonomous routing + self-update procedure. All 4 bundles updated to reference the index. Skill count now 23 (22 + skill-index). |
| 2026-09-19 | Classifier rebuilt (cron) | All 1159 skills reclassified; `70_personal_skill_index.md` updated; distribution: Identity=80, Behavioral=248, Role=149, Operations=682 |
| 2026-09-23 | Classifier rebuilt (cron) | All 1159 skills reclassified; `70_personal_skill_index.md` updated; distribution: Identity=80, Behavioral=248, Role=149, Operations=682 (zero drift since 2026-09-19 rebuild) |
| 2026-09-25 | Classifier rebuilt (cron) | All 1159 skills reclassified; `70_personal_skill_index.md` updated; distribution: Identity=80, Behavioral=248, Role=149, Operations=682 (zero drift; script now self-appends Inferred purposes section + uses backticks correctly) |
| 2026-09-26 | Classifier rebuilt (cron) | All 1159 skills reclassified; `70_personal_skill_index.md` updated; distribution: Identity=80, Behavioral=248, Role=149, Operations=682 |
| 2026-09-28 | Classifier rebuilt (cron) | All 1159 skills reclassified; `70_personal_skill_index.md` updated; distribution: Identity=80, Behavioral=248, Role=149, Operations=682 |
| 2026-09-28 | Classifier rebuilt (cron) | All 1159 skills reclassified; `70_personal_skill_index.md` updated; distribution: Identity=80, Behavioral=248, Role=149, Operations=682 |
| 2026-09-28 | Classifier rebuilt (cron) | All 1159 skills reclassified; `70_personal_skill_index.md` updated; distribution: Identity=80, Behavioral=248, Role=149, Operations=682 |
| 2026-10-02 | Hermes currency drift detected | Read-only probe returned `{"state": "would-sync"}` â€” venv out of date vs lockfile. This is the known cause of `hermes status` / `hermes mcp list` hanging. Repair requires R0 (calls `pm.sync_venv`). M3 remains wired as default model in `cli-config.yaml` (`default: MiniMax-M3`, `provider: minimax-oauth`). |
| 2026-10-02 | Obsidian Karpathy audit complete | Vault pattern is SPECIFIED (`SF_MKVA - KARPATHY_LLM_WIKI_SETUP.md`, 370 lines, sacru:true) but not ENFORCED. Measured: 25/399 dirs have an index (6.3%), 76/400 notes have canonical frontmatter (19%), 0 files at vault root (no index), `hot.md` HOT CACHE absent. Vault diagnosed its own gap on 2026-05-12; still open. Report: `70_CONNECTORS/70_obsidian_karpathy_audit.md`. Execution needs R0 (doctrine Â§11). |
| 2026-10-02 | **Sentinel role AI mapped** | `hermes-sentinel-daemon` (image `hermes-mcp-base:latest`, cmd `python /app/sentinel_daemon.py`, created 2026-09-18) is a Sentinel Invariant & Guardrail Daemon. Self-heals 3 subsystems (config.yaml, Electron sandbox markers, WhatsApp), enforces 4 boolean invariants (enabled/guardian_strict/trigger_detection/auto_recalibrate), and runs `SentinelGuardianAuditor.audit_text` which **inspects live agent responses** for forbidden paths, `CONSTINTA.md` Romanian diacritic integrity, and rule deviations â€” surfacing violations as red markdown alerts in Desktop App UI + CLI. Binds `C:\Users\apviz\AppData\Local\hermes` -> `/hermes` (full install write access). **Mavis has been operating without knowing this daemon may rewrite its output.** Report: `70_CONNECTORS/70_sentinel_role_ai_inventory.md`. |
| 2026-10-02 | **Minimax bridge group deployed** | Two containers in compose project `optimus-minimax`: `minimax-hermes-bridge` (:8801, rw mounts â€” doctor+delegate+centralize) and `minimax-antigravity-bridge` (:8802, ro â€” council+memory). Uniform HTTP contract (/health /schema /doctor /doctor/detailed /audit /delegate /heal). 3 new skills: `mavis-minimax-hermes-bridge-skill`, `mavis-minimax-antigravity-bridge-skill`, `mavis-sentinel-daemon-skill`. **Both verified healthy, 0 doctor failures.** Doctor found 3 real Hermes defects: venv drift after self-update to v0.21.5+5397.g105e876.dirty (Python 3.11->3.14, 219 commits behind, .dirty tree), `cli-config.yaml` broken symlink to obsolete WSL path, Docker actually 29.8.1 not 29.8.0. **Corrections to prior reports**: M3 IS wired (default=MiniMax-M3, provider=minimax-oauth); MiniMax Hub IS installed with 16 live connector tools (not absent); `HERMES_OPTIMUS` pre-existed this work. Report: `OPTIMUS_MINIMAX_HERMES_ANTIGRAVITY_INTEGRATION_REPORT.md`. |
| 2026-10-05 | Classifier rebuilt (cron) | All 1279 skills reclassified; `70_personal_skill_index.md` updated; distribution: Identity=86, Behavioral=259, Role=155, Operations=779 |
| 2026-10-12 | Classifier rebuilt (cron) | All 1297 skills reclassified; `70_personal_skill_index.md` updated; distribution: Identity=86, Behavioral=259, Role=156, Operations=796 |

## Installed CLI binaries (verified 2026-09-18)

| CLI | Path | Version |
|---|---|---|
| `hermes` | `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe` | 0.21.3 |
| `qwen` | `C:\Users\apviz\AppData\Local\qwen-code\bin\qwen.cmd` | 0.19.2 |
| `agy` (Antigravity) | `C:\Users\apviz\AppData\Local\agy\bin\agy.exe` | 1.2.5 |
| `docker` | `C:\Program Files\Docker\Docker\resources\bin\docker.exe` | 29.8.0 |
| `hf` (HuggingFace CLI, inside Hermes venv) | `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hf.exe` | (Hermes-bundled) |

## Open questions for Popy (R0)

1. Are there other user folders on this machine Mavis should know about (e.g., a service account for the swarm)?
2. Does Mavis have write access to `C:\Users\apviz\.minimax\` for managing its own config? â€” **YES** (verified by writing SKILL.md files in this session)
3. Should Mavis maintain a separate registry for installed CLI binaries? â€” **DONE** (table above)

# OPTIMUS Backbone — Mavis Project Hub

This directory is the **central audit point for the whole MiniMax ecosystem on
this machine.** Popy's standing instruction: keep it current.

**Start here:**
```powershell
cc start        # Control Center dashboard  -> http://127.0.0.1:8900/
optimus status  # one screen, every pillar
cc guard        # is docker-compose.yml still present and valid?
```

## Two layers, one backbone

| Layer | Path | Role |
|---|---|---|
| **Doctrine substrate** | `SENTINEL_PRIME/` (existing, built 2026-09-12) | The deep SENTINEL doctrine — A_FI_DOCTRINE, TRIPLE FILTER, ANTI-MIMICRY, partnership, rituals, the sentinel_hub MCP, sentinel-prime-role skill. **Source of truth for doctrine.** |
| **Mavis orchestration** | this directory | The operational layer — bridges, registries, workflows, skill and connector source-of-truth, scripts, and the Control Center. **Consumes the doctrine, doesn't redefine it.** |

When the doctrine and the orchestration layer disagree, the **doctrine wins**. Propose amendments to `SENTINEL_PRIME/` via R0; do not silently fork.

## The four source-of-truth roots

Everything OPTIMUS builds is reachable from one of these. Never copy — link.

| SOT | Path | Holds |
|---|---|---|
| **Scripts** | `scripts\` | All custom scripts. `hermes-custom\` holds 75 NTFS **hard links** (same inode, not copies) to the custom Hermes scripts; `external\` holds junctions to the large script trees. |
| **Skills** | `60_SKILLS\_links\` | Junctions to `mavis-skills` (32), `personal-skills` (1159), `hermes-skills`, `builtin-skills`. |
| **Connectors** | `70_CONNECTORS\_links\` | Junctions to `hermes-mcp-servers`, `minimax-integrations`, `minimax-bin`, `hermes-desktop-plugins`. |
| **Docs** | this folder | Specs, protocols, workflows, registries, reports. |

Rebuild the index with `optimus sot build` (or `cc refresh`). It only creates
what is absent and never deletes.

> Symbolic links need elevation and the agent is not elevated, so **junctions**
> (folders) and **hard links** (files) are used instead. Both are transparent and
> add zero duplicate storage.

## Directory map

```
.
├── README.md                                # this file — orientation
├── OPTIMUS_INDEX.md                         # cheat sheet
├── AGENTS.md                                # project-level agent instructions
├── SENTINEL_OPERATIONAL_DOCTRINE.md         # ⭐ PASTE INTO CUSTOM INSTRUCTIONS
├── POPY_MiniMax_OPTIMUS_Status_Report-10-02-2026.md   # ⭐ current state, for Popy
├── OPTIMUS_MINIMAX_HERMES_ANTIGRAVITY_INTEGRATION_REPORT.md  # technical detail
├── 00_INDEX/                                # master maps
├── 10_BRIDGES/                              # bridge SPECIFICATIONS
├── 20_BRIDGES/                              # bridge IMPLEMENTATION (code, compose)
├── 20_PROTOCOLS/                            # operational protocols
├── 30_WORKFLOWS/                            # session-by-session procedures
├── 40_REGISTRIES/                           # D:/E:/C: source paths (append-only)
├── 50_TEMPLATES/                            # copy-paste scaffolds
├── 60_SKILLS/                               # skill SOT (_links\) + blueprints
├── 70_CONNECTORS/                           # connector SOT (_links\) + inventories
├── 90_CONTROL_CENTER/                       # ⭐ live dashboard + command center
├── logs/                                    # runtime logs
├── scratch/                                 # test artefacts
└── SENTINEL_PRIME/                          # doctrine substrate
```

`10_BRIDGES` vs `20_BRIDGES`: **spec vs implementation.** The Hermes bridge
specification is in `10_BRIDGES`; the code, compose file and shared core are in
`20_BRIDGES\minimax\`.

## The one command

`optimus` is the single front door for the whole ecosystem. It is on the user
PATH.

```
optimus status | doctor        health across every pillar
optimus ai auth|tools|call     MiniMax Connector tools
optimus app status|code        MiniMax Code / Design
optimus minimax doctor|ask     MiniMax from Python
optimus bridge health|doctor   the two MiniMax bridges
optimus doc convert|pdfa|merge document bridges
optimus qwen status|serve|auth Qwen via ACP
optimus docker census|ps       container counts (never prune)
optimus sot list|build         source-of-truth index
optimus skills list            Mavis skills
```

`cc <command>` is the Control Center equivalent and is also on PATH.

There is **no separate "MiniMax CLI" product.** `mcode-tools` is a shim that runs
`MiniMax Code.exe` in node mode and authenticates through the running app's
shared broker — Code and the CLI are already one binary and one identity.
`optimus` is the single interface over that, not a third product.

## Control Center

`cc start` → `http://127.0.0.1:8900/`

Live daemon monitors with clickable whitelisted commands. A `file://` page cannot
execute PowerShell, so live data needs a local HTTP origin — the server binds
**127.0.0.1 only** and actions are resolved from a whitelist keyed by id, so a
crafted request cannot execute arbitrary shell.

- `GET /` dashboard · `GET /api/state` live JSON · `POST /api/action` run an action
- `90_CONTROL_CENTER\api\collect-state.ps1` — measured fresh on every request
- `90_CONTROL_CENTER\bat\` — `start-dashboard.bat`, `guard-compose.bat`, `cc.bat`

## Safety rules — permanent

- **NEVER** `docker container prune -a`. The swarm was lost this way 2026-08-08.
- **NEVER** `docker rm -f hermes-mcp-*`. The 31 containers are load-bearing.
- **NEVER** `--remove-orphans` on the `apviz` compose project —
  `Antigravity_Ecosystem_Terminal` shares the project name but has its own
  compose file, and would be deleted.
- `C:\Users\apviz\docker-compose.yml` was found deleted on 2026-10-02, leaving 18
  containers as orphans. `cc guard` now detects and rebuilds it from live state.

## Status legend

- ✅ **WIRED** — live and exercised
- 🟡 **BLUEPRINT** — documented, not yet activated
- 🔴 **BLOCKED** — needs Popy decision or an external dependency

## What is NOT in this layer

- **SENTINEL doctrine** — `SENTINEL_PRIME/01_FOUNDATION/doctrine/A_FI_DOCTRINE.md`
- **SENTINEL rituals** — `SENTINEL_PRIME/02_OPERATIONAL/rituals/`
- **SENTINEL scripts** — linked at `scripts\external\sentinel-operational`
- **SENTINEL MCP server** — `SENTINEL_PRIME/07_BACKBONE/mcp/`
- **SENTINEL skill** — `SENTINEL_PRIME/07_BACKBONE/skills/sentinel-prime-role.SKILL.md`

## How to extend

1. **New AI bridge** → spec in `10_BRIDGES/`, code in `20_BRIDGES/`
2. **New protocol** → `20_PROTOCOLS/`
3. **New workflow** → `30_WORKFLOWS/`
4. **New source location** → append to `40_REGISTRIES/40_partition_*.md` (append-only)
5. **New script** → put it in `scripts/`, then `optimus sot build`
6. **New skill** → `mavis-<subject>-skill` in the Mavis skills dir, then `optimus sot build`
7. **New connector** → `70_CONNECTORS/`, then `optimus sot build`

Then load the `mavis-minimax-index-folder-update` skill and follow its
four-step close-out.


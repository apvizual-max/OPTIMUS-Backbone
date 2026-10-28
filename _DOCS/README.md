# QUARANTINE — OPTIMUS Control Center, complete restore point

Created 2026-10-04. **This folder is a rebuild point.** If the machine is lost,
or the project is handed to an AI with no context, everything needed to stand it
back up is here.

---

## 📍 Address

```
C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\FULL_BACKUP_2026-10-04_QUARANTINE
```

---

## Start here, in this order

| # | File | What it gives you |
|---|---|---|
| 1 | **`00_REBUILD_FROM_SCRATCH.md`** | ⭐ **You have no idea what this is. Read this first.** Step-by-step rebuild, the traps, how to know you got it right. |
| 2 | `03_TREES\STRATEGIC_TREE.md` | why this exists, and what it is forbidden from becoming |
| 3 | `03_TREES\PROCESS_TREE.md` | what is actually running, what started it, kill semantics |
| 4 | `03_TREES\LOGIC_TREE.md` | the decision rules — what it concludes from what it measures |
| 5 | `03_TREES\OPERATIONS_TREE.md` | day-zero bring-up, everyday commands, escalation ladder |
| 6 | `02_DEPENDENCIES.md` | every tool + version **measured at generation time** |
| 7 | `05_POSTMORTEMS.md` | ⭐ **18 real bugs, all of which shipped green. Read before writing code.** |
| 8 | `03_TREES\FILE_TREE.md` | generated from disk — where every file is |
| 9 | `06_REFERENCE_COMPARISON.md` | the `:3098` dashboard read read-only — what it does that we don't, and what we do that it doesn't |

---

## What is in the code tree

The **entire `projects\` root**, at the state of 2026-10-04:

- `90_CONTROL_CENTER\` — the dashboard: `index.html`, `api\server.ps1`,
  `api\collect-state.ps1`, `bat\cc.bat`, `bat\manage-versions.ps1`,
  `backups\versions\v0.2…v0.5`, the live `live-state.json`, `cc-health.json`,
  `state-history.jsonl`, and the logs
- `scripts\` — including **`cc-watchdog.ps1`** (the supervisor),
  `optimus.cmd`, `make-full-backup.ps1`, `verify-full-backup.ps1`,
  **`verify-ui.ps1`** (`cc selftest` — parses the page, checks encoding, assets,
  API and supervisor), **`gen-icon-subset.ps1`** (regenerates the local icon
  subset; run it after adding any icon)
- `SENTINEL_PRIME\` (154 files) — the doctrine substrate
- `95_DESIGN_SOT\` — the read-only Hermes design system working copy
- `10_BRIDGES` · `20_PROTOCOLS` · `30_WORKFLOWS` · `40_REGISTRIES` ·
  `50_TEMPLATES` · `60_SKILLS` · `70_CONNECTORS` · `00_INDEX`
- every root document: the doctrine, the timeline, the integration reports

### Integrity

`BACKUP-MANIFEST.json` carries a SHA-256 for every file, plus:

- **520 files**, 18 directories, **3,594,046 bytes**
- **13 junctions** — recreated as junctions, with every target recorded so a
  restore can repoint them (they point *outside* this root: the Hermes script
  trees, the MCP servers, the skill libraries)
- **76 hard links** — archived as **real file content**. A hard link is an
  ordinary file sharing an inode; copying its target would drag in tens of
  thousands of foreign files, and skipping it would lose data silently.
- **0 nested backups** — a backup never archives another backup

Verify it yourself:

```powershell
scripts\verify-full-backup.ps1 -Name FULL_BACKUP_2026-10-04_QUARANTINE -Sample 200
```

It compares **source against backup**, not the manifest against itself, and
reports per-file mismatches, missing files, broken junctions and nested backups.

---

## ⚠ Five rules that are not negotiable

1. **NEVER `docker container prune -a`.** The 31 `hermes-mcp-*` containers are
   load-bearing and the swarm was lost this way on **2026-08-08**.
2. **NEVER `docker rm -f hermes-mcp-*`.**
3. **NEVER `--remove-orphans` against the `apviz` project** — it owns
   `Antigravity_Ecosystem_Terminal`.
4. **NEVER run `hermes update`.** Popy reserved it for himself.
5. **Never edit the design SOT at**
   `~\AppData\Local\hermes\desktop-plugins\design-system` — it is the read-only
   origin. The working copy is `95_DESIGN_SOT\`.

---

## Current live state at seal time

```
console      http://127.0.0.1:8900/        supervised, healthy
containers   58   (hermes-mcp-*: 31)
bridges      2    both up
services     3    8080 / 8082 / 3001
qwen         ACP on :8765 (model provider is the blocker, not the protocol)
supervisor   cc-watchdog.ps1, 30 s check, 3 consecutive failures to act
logon task   OPTIMUS_ControlCenter  (registered; fires at next sign-in)
dashboard    15 tabs, no build step, no network dependency
```

### Stand-alone

The console has **no external dependency at all**. Measured from the live page:
`externalResources: []`, `externalDocRefs: []`, 34/34 icon glyphs rendering, font
served from `90_CONTROL_CENTER\assets\`. It runs on plain Windows PowerShell and
a static page — close the MiniMax agent and nothing breaks.

### Tabs

Overview · AI Analyst · Trends & Incidents · Docker · Bridges · Services · Qwen ·
Hermes Update · MiniMax · Skills · Projects Sections · Documentation · Command
Center · **Resilience** · **Fabric**

`Resilience` reports whether anything is keeping this console alive, and
**whether the page itself still parses** — a healthy API behind a dead page is
the failure that hides best, so the supervisor checks both.

`Fabric` is the reachability matrix, the supervision tree, the port map, the
**model fleet** (what every agent is actually pointed at, read from each tool's
own config) and a **live front-end self-test** you can run from the page.

### Verify it yourself

```powershell
cc selftest    # 7 checks, ~2 seconds: parse, encoding, assets, API, supervisor
```

It asserts **effects, not the absence of symptoms** — `node --check` on the
extracted script, and a `typeof render === 'function'` probe. A JavaScript parse
error leaves the page rendering its skeleton with an HTTP 200 and an empty
console, so "no errors" proves nothing; those two do.

---

## Related, not included

The **Qwen Ecosystem Control Dashboard** at `http://127.0.0.1:3098/` is a
*separate* project used as design inspiration. It is **not** copied here and was
**not modified** — it is live ongoing work of its own.

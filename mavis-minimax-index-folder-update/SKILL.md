---
name: mavis-minimax-index-folder-update
description: Use when adding, moving, renaming, or deleting anything under C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard — then this skill defines what must be re-indexed and in which folder. Also use to audit that folder for drift, refresh the Master Map, refresh the SOT links, or answer "where does X live / which doc covers Y". Triggers on "update the index", "projects folder", "Master Map", "registry", "new bridge file", "document this change", "SOT", "60_SKILLS", "70_CONNECTORS", "40_REGISTRIES".
---

# mavis-minimax-index-folder-update

`C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\` is the **central audit point for the
whole MiniMax ecosystem on this machine.** Popy's standing instruction: it must
stay current as the build progresses.

This skill says what goes where and what to refresh after any change. Invoke it
**after** making a change, not before — it is the closing step of a work unit.

## The folder contract

| Folder | Holds | Never holds |
|---|---|---|
| `00_INDEX/` | Master maps, registries of registries | operational content |
| `10_BRIDGES/` | Bridge *specifications* (what a bridge should do) | running code |
| `20_BRIDGES/` | Bridge *implementation* (code, compose, workflows) | specifications |
| `20_PROTOCOLS/` | Operational protocols | narrative reports |
| `30_WORKFLOWS/` | Session-by-session procedures | one-off task notes |
| `40_REGISTRIES/` | Source locations on D:/E:/C: — **append-only** | anything that changes often |
| `50_TEMPLATES/` | Copy-paste scaffolds | live artefacts |
| `60_SKILLS/` | Skill source of truth (`_links\`) + blueprints | skill *source code* (that lives in `.minimax`) |
| `70_CONNECTORS/` | Connector source of truth (`_links\`) + inventories | connector *source code* |
| `scripts/` | **Central SOT for all custom scripts** | vendored third-party trees |
| `90_CONTROL_CENTER/` | Dashboard code, API, bat files, backups | general docs |
| `logs/`, `scratch/` | Runtime output and test artefacts | anything authoritative |

`10_BRIDGES` vs `20_BRIDGES` is the distinction people get wrong: **spec vs
implementation.** The Hermes bridge spec is in `10_BRIDGES`; the code, compose
and shared core are in `20_BRIDGES\minimax\`.

## After ANY change to this folder, run these four steps

### 1. Refresh the SOT index
```powershell
optimus sot build
```
Creates only what is absent; never deletes. It builds junctions in
`60_SKILLS\_links` and `70_CONNECTORS\_links`, and hard links in
`scripts\hermes-custom\`.

### 2. Update the section index
`00_INDEX\00_master_map.md` must list every file in its section. If you added a
file, it needs a line. If you renamed one, the old line is now wrong.

### 3. Update the affected registry
`40_REGISTRIES\` is **append-only**. Never edit or delete an existing entry — a
correction is a *new* entry that references the old by path and date. This
mirrors git history and the JURNAL_OGLINDA discipline.

### 4. Refresh the dashboard
The Control Center reads this folder live, so it needs no manual step — but if
you added a whole new *section folder*, add it to the `$sections` map in
`90_CONTROL_CENTER\api\collect-state.ps1`, otherwise the new tab never appears.

## Which registry owns what

| Registry | Scope |
|---|---|
| `40_partition_E_*.md` | E: drive — Second Brain vault, SENTINEL manuals, SACRU corpus |
| `40_partition_D_*.md` | D: drive — audio/video, SENTINEL character assets |
| `40_partition_C_*.md` | C: drive — app installs, Hermes, MiniMax, Docker data |

A new file that lives outside `projects\` gets a registry line so the next
person can find it without searching the whole disk.

## Adding a new script

1. Prefer putting it in `projects\scripts\` in the first place — that folder is
   the SOT.
2. If it must live elsewhere (it belongs to Hermes, e.g.), add the source to the
   `$folders` or per-file hard-link list in `scripts\build-sot-index.ps1` and
   re-run `optimus sot build`. Do **not** copy the file.
3. Give every script a comment-based help block with `.SYNOPSIS`,
   `.DESCRIPTION` and `.EXAMPLE`, and state any verified limitation in the
   description rather than letting it fail cryptically later.

## Adding a new bridge

1. Spec first → `10_BRIDGES\` (what it does, endpoints, mount policy, failure modes).
2. Implementation → `20_BRIDGES\` (code, compose, shared core).
3. Register it in `00_INDEX\00_bridge_registry.md` with a status badge:
   ✅ WIRED · 🟡 BLUEPRINT · 🔴 BLOCKED.
4. Add a healer/skills entry if it exposes actions.
5. Add it to the Control Center if it should be monitored.

## Adding a new skill

Skills live at `C:\Users\apviz\.minimax\agents\mavis\skills\<name>\SKILL.md`.

- Directory name **must equal** the frontmatter `name:`.
- The convention is `mavis-<subject>-skill`. This is the only coordination that
  exists between concurrent writers — a non-conforming name can be swept up by
  another session's tidy pass and the skill disappears.
- Then run `optimus sot build` so `60_SKILLS\_links\mavis-skills` shows it.
- **Re-verify the file in a later turn, not the same one.** A skill written and
  verified in the same turn has been observed vanishing before.

## Documentation hygiene

- Lead with the conclusion. Evidence after.
- Reference code as `path:line` — clickable.
- **Never fabricate** a tool name, path, version, price, or flag. If unverified,
  say so and give the verification command.
- Mark speculation as **SPECULATION** so Popy can ratify or reject it.
- Status badges: ✅ WIRED · 🟡 BLUEPRINT · 🔴 BLOCKED.
- Romanian at Popy + Prime + Assist tier; English below the translator gate.

## Quick audit

```powershell
optimus status                # is the system actually healthy
optimus sot list              # are the links intact
cc compose                    # is docker-compose.yml present and valid
```

To check the index for drift by hand: list every file in a section and compare
it against that section's entry in `00_master_map.md`. Anything in the folder
but not in the map is drift; anything in the map but not on disk is a broken
reference.

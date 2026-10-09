---
name: mavis-minimax-antigravity-bridge-skill
description: Operate the minimax-antigravity-bridge container (port 8802) — Mavis's Antigravity COUNCIL bridge. Use when reading Antigravity's past work/memory, asking Antigravity for a second opinion, or delegating a small leaf task to the Antigravity CLI agent. Triggers on "ask Antigravity", "what did Antigravity work on", "get a second opinion", "delegate to agy".
---

# mavis-minimax-antigravity-bridge-skill

Antigravity is the **small-tasks / AI-council** back-up. This skill drives `minimax-antigravity-bridge`.

## Container

| Property | Value |
|---|---|
| Name | `minimax-antigravity-bridge` |
| Image | `optimus/minimax-antigravity-bridge:1.0.0` |
| Port | `127.0.0.1:8802` |
| Network | `optimus-minimax_optimus` |
| Mounts | Antigravity roaming (**ro**), agy bin, IDE, App, host bins (ro) |

**Read-only by design.** Antigravity is a second opinion, not a system of record. The bridge has no mutation powers except a read-only log-size report.

## Start / stop

```powershell
cd C:\Users\apviz\.minimax-agent\projects\20_BRIDGES\minimax
docker compose -f docker-compose.yml up -d --build
```

## The four calls

```powershell
Invoke-RestMethod http://127.0.0.1:8802/health
Invoke-RestMethod http://127.0.0.1:8802/schema
Invoke-RestMethod http://127.0.0.1:8802/doctor | ConvertTo-Json -Depth 6
Invoke-RestMethod http://127.0.0.1:8802/audit | ConvertTo-Json -Depth 6
```

## Reading Antigravity's past work

`/audit` returns the Antigravity state tree. Two sources matter:

| Source | What it gives |
|---|---|
| `agy_app_storage` | `AppData\Roaming\Antigravity\app_storage.json` — projects, layouts, session keys |
| `agy_logs` | `AppData\Roaming\Antigravity\logs` |
| `agy_local_storage` / `agy_session_storage` | Chromium storage for the IDE/App |

Checks `agy.memory` (readable, file count + bytes) and `agy.past_work` (parses `app_storage.json`,
counts conversation/session keys) tell you whether there is history to read at all.

## Delegating

```powershell
# Council opinion
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8802/delegate `
  -ContentType 'application/json' -Body '{"prompt":"Review this diff for null-safety issues only. Be terse.","timeout":180}'

# Resume Antigravity's own past conversation
... -Body '{"prompt":"continue","project":"<project id>","timeout":300}'
```

## Antigravity CLI flags worth knowing

From `agy --help` (v1.2.5):

| Flag | Use |
|---|---|
| `--print` / `-p` | one prompt, non-interactive, print response |
| `--output-format` | `text` \| `json` \| `stream-json` |
| `--conversation <id>` | **resume a previous Antigravity conversation** — how you continue its past work |
| `--project` | project id or name |
| `--add-dir <path>` | grant a workspace (repeatable) |
| `--model` | model override |
| `--effort` | `low`\|`medium`\|`high`\|`max` |
| `--sandbox` | run sandboxed with terminal restrictions |
| `--mode` | `accept-edits` \| `plan` |
| `--dangerously-skip-permissions` | auto-approve all tool permissions — **use only on throwaway worktrees** |
| `--remote-control` | create a remote connection for the CLI session |
| `--input-format stream-json` | NDJSON, one message per line from stdin, runs a turn each |

Subcommands: `agent`, `agents`, `changelog`.

## Popy's operating rule

Antigravity is the **council and small-task back-up**. It is no longer the main back-up AI.
Reserve it for: second opinions, narrow leaf tasks, and reading its own past work.
Do **not** route orchestration, long-running builds, or system-of-record work here.

## Anti-patterns

- ❌ Reaching for this bridge for identity/location questions — use `mavis-bundle-identity`.
- ❌ Delegating multi-step orchestration — that's Hermes territory.
- ❌ `--dangerously-skip-permissions` on a real workspace.

## Cross-references

- Bridge source: `20_BRIDGES/minimax/minimax-antigravity-bridge/`
- Group README: `20_BRIDGES/minimax/README.md`
- CLI inventory: `mavis-antigravity-bridge-skill` (the raw shell path)

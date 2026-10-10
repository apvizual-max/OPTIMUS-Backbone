# OPTIMUS - CURRENT STATE (single source of truth)

> **GENERATED FILE.** Rebuilt from live measurement on 2026-10-05 01:56 by
> `projects\scripts\build-current-state.ps1`. Do not hand-edit it: it is stale
> the moment anything changes. Regenerate it with:
>
> ```powershell
> powershell -NoProfile -ExecutionPolicy Bypass -File projects\scripts\build-current-state.ps1
> ```
>
> If any other document in `projects\` disagrees with this one, **this file is
> right** and the other is stale. 3 file(s) currently carry a
> SUPERSEDED banner for exactly that reason.

## Fleet

| Thing | Measured |
|---|---|
| Containers running | **60** |
| `hermes-mcp-*` | **31** |
| `hermes-sentinel-daemon` | 1 |
| MiniMax bridges | 2 |
| Mavis skills | **61** |
| Personal skills | 1279 |
| Hermes MCP servers in config | 0 |
| Bridge doctor | warn, 3 warn, 0 fail |
| Ports | 3001:UP  8080:UP  8082:UP  8765:UP  8801:UP  8802:UP  8900:UP |
| Control Center tabs | **0** |
| Root `.md` files | 15 |

## Qwen - the entry most often got wrong

| MCP entry | Live state in `mcp.json` |
|---|---|
| `qwen-mcp-http` | **true** |
| `qwen-acp-adapter` | **true** |

- `qwen-mcp-http` points at `localhost:8765/mcp`. Qwen 0.19.2 **never served that
  path** - it returns 404 and is logged as 404. Qwen exposes ACP at `/acp`; it
  has no MCP transport. Kept enabled by Popy's explicit decision of 2026-10-02;
  it will not connect.
- `qwen-acp-adapter` is the working path: 6 tools, all returning real data.
  `qwen_prompt` / `qwen_doctor` / `qwen_session_probe` run over stdio;
  `qwen_auth_status` / `qwen_auth_device_flow_start` / `qwen_workspace_tools`
  must use the daemon WebSocket, because the `_qwen/*` extensions answer
  `-32601` on stdio.
- The live blocker is the model provider, not the protocol: Qwen's active model
  is `qwen2.5-coder:1.5b` on local Ollama `127.0.0.1:11434` and **Ollama is not
  installed**. `session/prompt` returns `Connection error.`
- ACP gotcha: `session/new` requires `mcpServers: []`.

## Hermes source - measured, and NOT a stable fact

Hermes self-updates (`updateMechanism: self`), so this section changes without
anyone asking. Read it, never assume it.

| | |
|---|---|
| `install-stamp` version | `0.21.5+6666.gaea016e.dirty` |
| `install-stamp` says dirty | True |
| Live `git status` modified files | **8** |
| Live `git HEAD` | `aea016e1a6 Merge branch 'main' of https://github.com/NousResearch/hermes-agent` |
| `.hermes-update-in-progress` | absent |

The stamp and live git legitimately disagree: the stamp is a snapshot from
whenever the last install ran, git is now.

> **Self-inflicted deadlock, worth remembering.** A hung `hermes mcp list`
> registers *its own PID* as owner of `.hermes-update-in-progress`, then waits
> on that lock. Every later call says: `hermes: source-update completion
> failed: an update is still running`. Fix: kill the hung CLI process. It is not
> a stale marker.

> Mavis has never run `hermes update`; Popy reserved that for himself.

## The three doctor warnings that are CORRECT on a healthy system

1. `hermes.version` - Windows NTFS symlink, unresolvable from a Linux container
2. `hermes.venv_currency` - reports the Hermes source state above
3. `hermes.status` - host-side probe by design

**Do not "fix" these.** If anything else shows warn or fail, that is a real finding.

## MiniMax

- There is **no separate "MiniMax CLI" product.** `mcode-tools` runs
  `MiniMax Code.exe` in node mode and authenticates through the running app's
  shared broker, so Code and CLI are one binary and one identity. Auth reads
  `authenticated` **only while MiniMax Code is running.**
- There is **no official Python SDK.** The PyPI package named `minimax` is an
  unrelated name-squat; `minimax-python` is unofficial v0.2.0 against a
  different surface. Use `projects\scripts\minimax_client.py`, which speaks the
  same `anthropic_messages` endpoint Hermes uses.

## Safety

- **NEVER** `docker container prune -a` - the swarm was lost this way 2026-08-08.
- **NEVER** `docker rm -f hermes-mcp-*` - 31 load-bearing containers.
- **NEVER** `--remove-orphans` on the `apviz` compose project:
  `Antigravity_Ecosystem_Terminal` shares the project name but has its own
  compose file and would be deleted.
- `C:\Users\apviz\docker-compose.yml` was found deleted on 2026-10-02. `cc guard`
  detects that and rebuilds it from live state (verified 18/18 services, with
  containers untouched).

## Check it yourself

```powershell
optimus status
optimus doctor --deep
cc start
cc guard
optimus minimax ask "say OK"
optimus sot list
docker ps --format '{{.Names}}' | Measure-Object
```
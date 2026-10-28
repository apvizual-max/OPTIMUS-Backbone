---
name: mavis-minimax-optimus-system
description: Use when rebuilding, restoring, diagnosing, or re-verifying the MiniMax → OPTIMUS integration on this machine — the 53-container Docker layer, the 31 hermes-mcp-* fleet, the sentinel daemon, the two minimax bridges, the unified `optimus` CLI, the Stirling-PDF and LibreOffice document bridges, the Qwen ACP adapter, or the Second Brain vault. Triggers on "restore the system", "OPTIMUS state", "is the system healthy", "what is wired", "rebuild compose", "bridge doctor", "system inventory", "after a reboot".
---

# mavis-minimax-optimus-system

The permanent restore + config source of truth for the MiniMax → OPTIMUS
integration. Everything here was measured on this machine; nothing is assumed.
**Re-verify with `optimus status` before trusting any number in this file** —
the system moves.

## 60-second orientation

```powershell
optimus status          # one screen, every pillar
optimus doctor          # deep, 12+ checks
cc guard                # is docker-compose.yml still there and valid?
```

Both commands live in `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\scripts\` and are
on the user PATH. `cc` is the Control Center command bar.

## The architecture in one paragraph

Hermes is the main orchestration and user layer. Mavis (this agent) is the
**Hermes doctor** and the MiniMax support/delegation layer — it diagnoses and
repairs Hermes rather than replacing it. Antigravity is retained only for small
tasks and AI-council work. Wayland provides agentic workflows, Obsidian is the
Second Brain, and Docker carries local tool containers plus custom SENTINEL role
AI. MiniMax Code is the host application; `mcode-tools` is its CLI surface.

## Fixed facts about this machine

| Thing | Value |
|---|---|
| Container count (post-DRAC baseline) | **53** |
| `hermes-mcp-*` fleet | **31** |
| Sentinel daemon | 1, invariants must be 4/4 |
| MiniMax bridges | 2 (`8801` hermes, `8802` antigravity) |
| Mavis skills | 30 (dir `C:\Users\apviz\.minimax\agents\mavis\skills`) |
| Personal skills | 1159 (`C:\Users\apviz\.minimax\skills`) |
| Hermes MCP servers in config | 34 |
| Hermes model | MiniMax-M3 via `minimax-oauth` → `https://api.minimax.io/anthropic` |
| Hermes version | 0.21.5+5397, tree dirty, ~219 commits behind |
| Docs services | Stirling-PDF `8082`, LibreOffice `3001` |
| Qwen ACP daemon | `8765` |

### Permanent safety rules — never violate

- **NEVER** `docker container prune -a`. The swarm was lost this way on 2026-08-08.
- **NEVER** `docker rm -f hermes-mcp-*`. The 31 containers are load-bearing.
- **NEVER** use `--remove-orphans` on the `apviz` compose project.
  `Antigravity_Ecosystem_Terminal` shares that project name but is defined by
  its own compose file, and `--remove-orphans` deletes it.
- Never touch Hermes or Docker config without explicit R0 from Popy.

## The two bridges

Linux containers **cannot execute Windows `.exe` files**. So `/delegate` is a
command-spec emitter: it validates the request and returns the exact host
command for Mavis to run. This is a design constraint, not a limitation to work
around.

Hermes is mounted read-write (the bridge must repair it). Antigravity is mounted
read-only (council only, never a mutator).

Endpoints on both: `/health` `/schema` `/doctor` `/doctor/detailed` `/audit`
`/journal` `/delegate` `/heal`

Hermes healers: `sync_venv`, `heal_enforcement`, `restart_container`.

## The three doctor warnings that are NOT faults

A healthy system reports exactly these. Do not "fix" them.

1. `hermes.version` — `cli-config.yaml` is a Windows NTFS link and cannot resolve
   from inside a Linux container. The link is healthy on the host.
2. `hermes.venv_currency` — the Hermes source tree is genuinely `dirty`.
3. `hermes.status` — a host-side probe by design; the bridge cannot exec `hermes.exe`.

Anything else showing as `warn` or `fail` is a real finding.

## Document bridges

Both are **host-side scripted**; the containers expose no usable API layer.

- `optimus doc convert <file> [fmt]` → LibreOffice via
  `docker exec libreoffice soffice --headless`
- `optimus doc pdfa|img|word|merge <files>` → Stirling-PDF via HTTP multipart

**Verified capability matrix (LibreOffice 25.8.7.3):** a `.pdf` source is only
usable for an **html** export. `pdf → docx/odt/txt` has no export filter. All
document→document and document→pdf conversions work.

**Stirling-PDF auth is disabled via `SECURITY_ENABLELOGIN=false`** in
`C:\Users\apviz\docker-compose.yml`. `SECURITY_ENABLED=false` — the name in most
guides — does nothing and leaves the API at 401.

**Route verification trap:** the Angular SPA returns `index.html` with HTTP 200
for *any* unknown path, so a 200 proves nothing. Probe with a POST carrying a
non-multipart body: **415** = route exists, **404** = no route, **401** = login
returned.

## Qwen — the three-layer diagnosis

`optimus qwen status` or the `qwen_doctor` MCP tool.

- **Transport: ACP, not MCP.** Qwen 0.19.2 exposes `/acp` (WebSocket) and
  `/health`. It does **not** serve `/mcp` — that 404s. The old `qwen-mcp-http`
  MCP entry was built on that misconception and is now **disabled**.
- **The working integration is `scripts\qwen_acp_mcp.py`**, registered as MCP
  server `qwen-acp-adapter` (6 tools: `qwen_prompt`, `qwen_doctor`,
  `qwen_auth_status`, `qwen_auth_device_flow_start`, `qwen_workspace_tools`,
  `qwen_session_probe`). It requires the Hermes venv python (it uses the `mcp`
  package).
- **The live blocker is the model provider, not the protocol.** Qwen's active
  model is `qwen2.5-coder:1.5b` pointing at a local Ollama endpoint on
  `127.0.0.1:11434`, and **Ollama is not installed** on this machine.
  `session/prompt` therefore returns `Connection error.` Two ways out: install
  and start Ollama, or complete `qwen-oauth` for the cloud
  `coder-model` (Qwen 3.6 Plus, 1M context).

**ACP gotcha worth keeping:** `session/new` **requires** `mcpServers: []`.
Omit it and Qwen answers a bare `Internal error`; the real validation message
(`expected array, received undefined`) only appears on the stdio transport. The
daemon additionally kills the child with SIGTERM and reports a 10 s timeout.

## MiniMax ecosystem — one interface, not three

There is **no separate "MiniMax CLI" product.** `mcode-tools` is a shim that runs
`MiniMax Code.exe` in node mode and authenticates through the running app's
shared auth broker — so Code and the CLI are already the same binary and the same
identity. Design is a separate desktop app; it has no CLI.

`optimus` is the single front door over all of it (`status`, `doctor`, `ai`,
`app`, `bridge`, `doc`, `qwen`, `docker`, `sot`, `skills`).

`mcode-tools auth status` returning `shared-broker` / `authenticated` requires
**MiniMax Code to be running**. If it is closed, the CLI loses auth.

## Source-of-truth index

`optimus sot build` (or `cc refresh`) rebuilds the index in `projects\`:

- `scripts\hermes-custom\` — 75 NTFS **hard links** to the custom Hermes scripts
- `scripts\external\` — junctions to the large Hermes/SENTINEL script trees
- `60_SKILLS\_links\` — junctions: mavis-skills, personal-skills, hermes-skills, builtin-skills
- `70_CONNECTORS\_links\` — junctions: hermes-mcp-servers, minimax-integrations, minimax-bin, hermes-desktop-plugins

Symlinks need elevation and this agent is not elevated, so **junctions** (folders)
and **hard links** (files) are used instead. A hard link shares the inode, so it
is genuinely not a copy.

**Junctions cannot be deleted by this agent** — mavis-trash refuses reparse
points and the shell policy blocks `Remove-Item`/`rmdir`. To repoint one, delete
it in Explorer and re-run the builder. The builder is idempotent: it creates only
what is absent and never deletes.

## Control Center

`cc start` → `http://127.0.0.1:8900/` — live daemon monitors with clickable
whitelisted commands, plus `/api/state` and `/api/action`. Loopback only.
Source in `projects\90_CONTROL_CENTER\`.

## The compose guard

`cc guard` validates `C:\Users\apviz\docker-compose.yml` and, if it has been
deleted again, rebuilds it from live container state via
`scripts\rebuild-compose-from-state.ps1`. This exists because the file was found
deleted on 2026-10-02, leaving 18 containers as orphans with no way to recreate
them. It never stops or recreates a container.

## Still blocked on Popy (do not re-derive these)

1. **Google OAuth** — `gdrive-mcp` ships `GOCSPX-YourSecretHere`. Needs a real
   OAuth 2.0 client. Note the four Google MCPs use three *different* auth models.
2. **Qwen OAuth** — `qwen auth qwen-oauth`, one browser consent.
3. **Token Plan Plus** — billing decision; prior runs failed with `2056`.

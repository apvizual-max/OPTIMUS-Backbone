# Bridge — Antigravity

**Status**: ✅ WIRED — CLI on PATH (v1.2.5) + `antigravity-bridge` skill installed. IDE also installed for visual work.

## Role in the swarm

Antigravity is Mavis's **peer backbone** — a separate AI coding agent that runs heavy code generation, repo-scale refactors, and autonomous multi-file workflows. Mavis coordinates, Antigravity executes. Think: Mavis = orchestrator/architect, Antigravity = heavy-lift engineer.

## Surface (live-verified 2026-09-18)

- **CLI**: `C:\Users\apviz\AppData\Local\agy\bin\agy.exe` — **v1.2.5** confirmed
- **IDE**: `C:\Users\apviz\AppData\Local\Programs\Antigravity IDE` (Electron app)
- **MCP equivalent**: Hermes-side `antigravity-bridge` MCP server is already running (Hermes's own routing layer)
- **Mavis-side MCP**: not wired (Antigravity is a peer backbone — calling it via Mavis-direct MCP would be redundant; use `antigravity-bridge` skill for shell invocation or dispatch through Hermes)
- **Skill**: `antigravity-bridge` installed at `C:\Users\apviz\.minimax\agents\mavis\skills\antigravity-bridge\`

## Activation (CLI + IDE active)

- ✅ `agy.exe --version` returns `1.2.5`
- ✅ `antigravity-bridge` skill installed
- [ ] Determine the canonical prompt-injection flag for `agy.exe` (likely `--prompt` or positional; `agy.exe --help` exits noisily — needs careful probing)

## Use cases

- Repo-scale refactors across many files
- Multi-PR autonomous workflows
- Generating code when Mavis's context would be too cluttered
- Long-running background tasks (delegated, polled via cron)

## Dispatch protocol

When Mavis hands a task to Antigravity:
1. State the task contract: scope, acceptance criteria, constraints
2. Hand off only the context Antigravity needs (Mavis retains the swarm-level state)
3. Receive the result with explicit attribution
4. Integrate into the swarm output with full CONSTINTA (evidence chain)

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Bridge wired | ✅ CLI 1.2.5 confirmed. Skill installed. Hermes already has `antigravity-bridge` MCP server running. |

## Open questions for Popy (R0)

1. Canonical prompt-injection flag for `agy.exe`? (Run `agy.exe --help` in a controlled shell — it exits noisily on Windows.)
2. Does Antigravity expose an MCP server (and at what URL/command)?
3. What is the canonical task format Antigravity expects (JSON, markdown, plain prose)?

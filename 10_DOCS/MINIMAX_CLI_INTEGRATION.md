# MINIMAX CLI Integration — measured record

**Date:** 2026-10-05
**Status:** WIRED (both CLIs installed, authenticated, and proven by execution)
**Namespace:** `minimax`. Not Hermes. These are MiniMax-owned packages and are not
shared with, proxied to, or dependent on any Hermes resource.

---

## 1. What was actually true before this work

A previous conversation contained a claim that the MINIMAX CLI had been installed.
**That claim was not substantiated by anything on disk.** Measured before acting:

| Probe | Result |
|---|---|
| `Get-Command mavis` | not on PATH |
| `Get-Command mcodectl` | not on PATH |
| `Get-Command minimax` | not on PATH |
| `Get-Command mcode` | not on PATH |
| `Get-Command mmx` | not on PATH |
| `npm ls -g --depth=0` | 32 packages, **no MiniMax package of any kind** |

`mmx` was on neither the earlier check list nor the global package list. **No MINIMAX
CLI existed on this machine.** The memory of a prior installation was mistaken, and
the mistake traces to an unverified claim rather than to a removed artefact.

## 2. There are two distinct products, and the name is ambiguous

Both are official MiniMax packages. They do different jobs. The name "MINIMAX CLI"
applies to both, which is why the question "which CLI?" has no single answer.

| | **MINIMAX Code CLI** | **MiniMax CLI** |
|---|---|---|
| npm package | `@minimax-ai/code` | `mmx-cli` |
| Executable | `mcode` | `mmx` |
| Installed version | `0.6.2` | `1.0.27` |
| What it is | a coding **agent** | a **capability** client |
| Interactivity | interactive TUI | none (scriptable) |
| Orchestration surface | `mcode exec` (headless), `mcode acp` (Agent Client Protocol over stdio) | `mmx <resource> <command>` |
| Capabilities | repo-aware agent work, sessions, plugins, providers | text, image, video, speech, vision, web search, file storage, quota |
| This machine needs it for | **agent-to-agent delegation** | **multimodal capability on the Token Plan** |

## 3. Install — both, exit 0

```
npm install -g mmx-cli --registry=https://registry.npmjs.org/
npm install -g @minimax-ai/code@latest --registry=https://registry.npmjs.org/ \
  --ignore-scripts=false --include=optional \
  --allow-scripts=@minimax-ai/code,better-sqlite3
```

Result: `added 33 packages` and `added 43 packages`, both `MEXIT=0`. Resolvers:
`C:\Users\apviz\AppData\Roaming\npm\mmx.ps1` and `...\mcode.ps1`.

**Node precondition:** v26.5.1, npm 12.0.2. `@minimax-ai/code` requires Node 22.19+,
or 24.2+/25/26. v26.5.1 satisfies this; no runtime had to be prepared.

## 4. Credential — the existing subscription key, never printed

`MINIMAX_API_KEY` was already present at **User** scope (125 chars), so it survives
reboot and is inherited by every child process. That is the subscription key Popy
referred to. **Its value was never read into a report, a file in this repo, or a log.**

Two different routes were required, because the two CLIs do not share an auth model:

**`mcode` — non-leaky route, used.** Names the environment variable; never reads it.

```
mcode provider set-minimax-key --api-key-env MINIMAX_API_KEY
-> "MiniMax API Key saved and selected."   exit=0
-> mcode provider list
   minimax_oauth  enabled  managed login
  *minimax_api    active   sk-c****49fg      (masked by the CLI itself)
```

**`mmx` — no non-leaky route exists, measured.** `mmx search query` with the env var
present and no stored credential fails `code 3 "No credentials found"`, and its own
error names only `MMX_CONFIG_DIR` as an env-var input. The `mmx auth status` hint
suggesting `MINIMAX_API_KEY` is **inaccurate for 1.0.27** — a docs/behaviour divergence
worth remembering. The only non-interactive path is `--api-key`, so the value was
supplied by shell expansion and never typed as a literal into a command:

```
mmx auth login --api-key $env:MINIMAX_API_KEY    -> exit=0
C:\Users\apviz\.mmx\config.json -> {"region":"global","api_key":"sk-<REDACTED>"}
```

Residual exposure, stated plainly: for roughly two seconds the key was present in a
process command line, which on Windows is readable by any process running as the same
user. This is a known, bounded, single-user trade-off — not an undisclosed one.

## 5. Proof by execution, not by presence

A check that cannot fail is not a check. Both CLIs were made to do real work.

**Delegation — the capability Popy actually asked for.**

```
mcode exec --cwd <SENTINEL_PRIME> --permission off --max-steps 3 --timeout 150s \
           --output-format text -o <file> \
           "Reply with exactly this line and nothing else: SENTINEL_DELEGATION_OK"
-> SENTINEL_DELEGATION_OK      exit=0
```

A second MiniMax agent, running headless in this repo, obeyed a delegation prompt.
That is agent-to-agent invocation, measured.

**Plan liveness.** `mmx auth login` printed a live Token Plan panel:
week `2026-10-01 — 2026-10-08`, general `85%` left, week `48%` left, 5h reset `1h 50m`.

**Inference.**

```
mmx text chat --message "Reply with exactly: MMX_GENERATION_OK" --max-tokens 32
-> model "MiniMax-M3", content "MMX_GENERATION_OK", stop_reason "end_turn", exit=0
   usage: 44 input / 6 output tokens
```

## 6. Documented interface that does not exist

`agent.minimax.io/docs/cli/reference` advertises `mcode auth status`,
`mcode auth refresh`, and `mcode auth logout`. **None of them exist in 0.6.2.**
`mcode auth status` returns `error: too many arguments. Expected 1 argument but got 2` —
`auth` is parsed as the positional `prompt`. The real commands are `mcode login`,
`mcode logout`, and `mcode provider`.

Recorded because the installed build is the final contract, and because a future
session that trusts the docs will draw a false conclusion from a real-looking error.

## 7. What this does and does not do

**Does:** give this project a callable second agent (`mcode exec` / `mcode acp`), and
give the swarm first-party access to MiniMax image, video, speech, vision and search
on the subscription Popy already pays for.

**Does not:** register either CLI as an MCP server, and does not touch the live
`C:\Users\apviz\.minimax\mcp.json` profile. That is a separate decision — see
`11_PLANS/MCP_DECISION_BRIEF.md` for why the "prune 7 dead entries" plan turned out
to describe a file that no runtime loads.

**Cost control:** `mcode exec` is bounded by `--max-steps`, `--timeout` and
`--permission off`, so a delegation probe cannot hang or prompt. `mmx` calls are
metered against the same Token Plan the agent itself uses; heavy generation belongs
in a deliberate call, not in a collector.

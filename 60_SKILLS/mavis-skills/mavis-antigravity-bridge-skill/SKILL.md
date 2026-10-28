---
name: mavis-antigravity-bridge-skill
description: Bridge to Antigravity CLI v1.2.5 (agy.exe). Antigravity is a peer backbone for heavy code generation, repo-scale refactors, and autonomous multi-file workflows. Currently bridged via shell — the Antigravity IDE is also installed at C:\Users\apviz\AppData\Local\Programs\Antigravity IDE for visual work.
---

# Antigravity Bridge

Antigravity CLI v1.2.5 (`agy.exe`) is Mavis's **peer backbone** for heavy-lift coding. Use for repo-scale refactors, multi-file autonomous workflows, and tasks that would clutter Mavis's context.

## Two ways to call Antigravity

### 1. Via shell (CLI)

```powershell
# Invoke antigravity CLI
& 'C:\Users\apviz\AppData\Local\agy\bin\agy.exe' --help
& 'C:\Users\apviz\AppData\Local\agy\bin\agy.exe' version

# Run with a prompt (depends on agy's input mode — read its docs / --help)
& 'C:\Users\apviz\AppData\Local\agy\bin\agy.exe' --prompt "your task here"
```

**Note**: agy.exe accepts `--help` and `--version` but main invocation may be interactive. Check the CLI's help output for the exact prompt-injection flag (commonly `--prompt`, `--task`, or positional). If unsure, run `agy.exe --help` first.

### 2. Via the Antigravity IDE

The IDE is installed at `C:\Users\apviz\AppData\Local\Programs\Antigravity IDE`. For visual / interactive work, open the IDE separately.

## When to dispatch Antigravity

- ✅ Repo-scale refactor across many files
- ✅ Autonomous multi-file workflow
- ✅ Long-running background task (delegate, poll via cron)
- ❌ Single-file edit — Mavis does this directly
- ❌ Read-only ops — use Mavis's own tools

## Hard rules

- R0 before dispatch unless pre-authorized.
- Always log to `10_BRIDGES/10_antigravity.md` JURNAL_OGLINDA.
- Never invoke agy.exe destructively without R0.

## Reference

- Bridge file: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\10_BRIDGES\10_antigravity.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §9`

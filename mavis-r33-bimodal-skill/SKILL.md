---
name: mavis-r33-bimodal-skill
description: R33 Bimodal execution discipline — Mod A (analyze) → R0 (Popy ratifies) → Mod B (execute). Load when a task has any of: state mutation, external messaging, destructive ops, external service commit, artifact publish, cross-AI dispatch. Default to R33 unless pre-authorized.
---

# mavis-r33-bimodal-skill

The 3-mode execution discipline of OPTIMUS Prime.

## When to use

- ✅ Anything mutating persistent state (files outside scratch, DBs, configs)
- ✅ Sending messages (email, chat, notifications, X/Twitter, LinkedIn)
- ✅ Destructive operations (delete, prune, force-overwrite)
- ✅ Committing to external services (publish, deploy, API write, OAuth consent)
- ✅ Bridging between AIs (dispatching to Antigravity / Hermes / Gordon / Qwen / NotebookLM)
- ❌ Pure reads
- ❌ In-session scratch work
- ❌ Calculations / proposals / analyses
- ❌ Anything trivially reversible

## The three modes

### Mod A — Analyze

Plan, design, architect, evaluate, compare, research. **Output**: evidence + reasoning + counter-arguments + stop. Wait for R0.

### R0 — Popy ratifies

Popy is the human-in-the-loop. The "R0" is the ratification step. Without R0 → no execution.

### Mod B — Execute

After R0, execute exactly what was ratified. **Hard rules**:
- Execute the ratified scope — nothing more.
- No "while I'm at it" additions.
- If something in scope needs fixing, fix it and report it; do not bundle unrelated work.
- Report faithfully: succeeded / failed / skipped / unverified.

## Pre-authorization exception

If Popy pre-authorizes a class of actions (e.g., "auto-fix lint in workspace"), R0 can be implicit. Mavis still logs every execution. **Silent execution is the anti-pattern**, not proactive execution of pre-authorized scope.

## Anti-patterns

- ❌ Executing without R0 → forbidden
- ❌ Expanding scope in Mod B → forbidden
- ❌ Skipping Mod A when the task is non-trivial → forbidden
- ❌ Treating Mod A output as Mod B → forbidden

## Cross-references

- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §2`
- Protocol file: `C:/Users/apviz/.minimax-agent/projects/20_PROTOCOLS/20_r33_bimodal.md`

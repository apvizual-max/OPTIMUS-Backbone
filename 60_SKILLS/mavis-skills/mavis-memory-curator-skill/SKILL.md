---
name: mavis-memory-curator-skill
description: Manage Mavis's Memory layer (user / agent / project). Load when deciding whether a lesson is worth saving long-term, when appending to memory, or when correcting an existing entry. Uses the `memory` tool inside MiniMax Code.
---

# mavis-memory-curator-skill

How Mavis uses the Memory layer — separate from Custom instructions.

## Layer routing (3-question test)

Before appending, ask:

1. **Will the answer change for a different user?** → User Memory (`~/.minimax/memory/user.md`)
2. **Does it hold across projects?** → Agent Memory (`~/.minimax/agents/mavis/memory/MEMORY.md`)
3. **Only relevant to this project?** → Project file (edit `AGENTS.md` or a topic file in `20_PROTOCOLS/` / `30_WORKFLOWS/`)

Default to agent memory; promote to user memory only when the evidence is durable cross-user preference.

## The three-question test before saving

**Will a future Mavis session plausibly act better because of this?** If no, don't save.

## When to update Memory

✅ Popy's identity, collaboration style, professional context
✅ OPTIMUS Prime architecture summary
✅ Operational code (TRIPLE CRUNCH, R33, SACRU, DRAG/DRAC)
✅ Pricing / buying lessons
✅ Material location pointers
✅ Stable cross-project behavior patterns

❌ One-off task status ("I built a feature today")
❌ Transient state ("the bridge is currently down")
❌ Speculative conclusions
❌ Routine session activity
❌ Anything recoverable from the current repo or official docs

## Append format

```
<!-- mem-append-reason: <why this is worth saving>. -->
### <topic> (<date>)
Type: <identity | architecture | rules | pointers | collaboration rules | professional context | project reference>

<content>
```

## Anti-patterns

- ❌ Saving routine session activity
- ❌ Saving secrets, tokens, credentials
- ❌ Saving without `mem-append-reason` justification
- ❌ Editing existing Memory entries silently — Memory is itself append-only in spirit; corrections are new entries
- ❌ Saving facts that are easy to recover from the current repository or official documentation

## Cross-references

- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §17` (Memory is NOT paste-into-instructions material)
- Workflow file: `C:/Users/apviz/.minimax-agent/projects/Mavis-Optimus-Dashboard/30_WORKFLOWS/30_memory_update.md`

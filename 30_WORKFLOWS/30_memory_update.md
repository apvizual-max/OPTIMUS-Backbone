# Workflow — Memory Update

**Purpose**: When and how Mavis updates the MiniMax Code Memory layer.

## The Memory layer (recap)

Memory in MiniMax Code is read programmatically by Mavis via the `memory` tool. It is **separate** from the Custom instructions text box:

- **Custom instructions** = system-prompt-style prose (the doctrine file)
- **Memory** = structured entries with `<!-- mem-append-reason -->` HTML comments + `###` topic headers

Popy's earlier confusion was pasting Memory entries into Custom instructions — that breaks because Memory entries are not prose; they are structured records with metadata comments.

## When Mavis updates Memory

Mavis updates Memory when it has learned something **durable and cross-session**:

- ✅ Popy's identity, collaboration style, professional context
- ✅ OPTIMUS Prime architecture summary
- ✅ Operational code (TRIPLE CRUNCH, R33, SACRU, DRAG/DRAC, etc.)
- ✅ Pricing / buying lessons
- ✅ Material location pointers
- ❌ One-off task status ("I built a feature today")
- ❌ Transient state ("the bridge is currently down")
- ❌ Speculative conclusions

## Layers

Pick the narrowest layer that fits:

1. **Only true in this repo/project?** → Edit `AGENTS.md` or a topic file under `20_PROTOCOLS/`, `30_WORKFLOWS/`, etc.
2. **True on a different project?** → **Agent Memory** (`~/.minimax/agents/mavis/memory/MEMORY.md`)
3. **Would the conclusion change for a different user?** → **User Memory** (`~/.minimax/memory/user.md`)

Default to agent memory; promote to user memory only when the evidence is durable cross-user preference.

## Append format

```
<!-- mem-append-reason: <why this is worth saving>. -->
### <topic> (<date>)
Type: <identity | architecture | rules | pointers | collaboration rules | professional context>

<content>
```

## Anti-patterns

- ❌ Saving routine session activity ("we discussed X today")
- ❌ Saving secrets, tokens, credentials
- ❌ Saving without `mem-append-reason` justification
- ❌ Editing Memory entries silently — Memory is itself append-only in spirit; corrections are new entries

## Before saving

Ask: **"Will a future Mavis session plausibly act better because of this?"** If no, don't save.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Workflow codified | First backbone session |

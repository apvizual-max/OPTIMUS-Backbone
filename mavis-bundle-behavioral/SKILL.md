---
name: mavis-bundle-behavioral
description: Bundle — Behavioral. Load when Mavis needs discipline: how to analyze, how to write, how to start/end sessions, what to save in memory, how to deliver files. Triggers on every non-trivial task. Routes to mavis-r33-bimodal-skill, mavis-triple-crunch-skill, mavis-session-lifecycle-skill, mavis-memory-curator-skill, mavis-deliverable-handoff-skill.
---

# mavis-bundle-behavioral

The **Behavioral** bundle. Discipline skills — how Mavis acts, decides, writes, opens/closes sessions, saves memory, and delivers outputs.

## When to load

- Every non-trivial task (default-on discipline)
- "How should I approach this?"
- "Is this decision right?"
- "What's the quality gate for this output?"
- "Should this go in memory?"
- "Am I done / how do I close this session?"

## Member skills

Load via `skill({ name: "<member>" })`:

| Member | When to load |
|---|---|
| `mavis-r33-bimodal-skill` | Every task that mutates state / sends messages / bridges AIs / commits externally. R33 = analyze → R0 → execute. |
| `mavis-triple-crunch-skill` | Before finalizing any artifact. Triple Crunch = Eminescu ABBA ∧ Eliade Realitate ∧ Musashi Taiere. |
| `mavis-session-lifecycle-skill` | At session open (read order) and session close (JURNAL append). |
| `mavis-memory-curator-skill` | Before saving anything to Memory (3-question test) and before discarding a memory candidate. |
| `mavis-deliverable-handoff-skill` | Whenever creating a file Popy needs to use (use `<media />`, not bare paths). |

## MCP servers that enforce scope

**No operational MCP for this category.** Discipline is enforced by Mavis reading doctrine + memory + the relevant project files. This is honest — behavior is not a tool.

The closest MCPs this category *uses* (but doesn't own):
- `mcp-server-filesystem` (read doctrine/memory)
- `git-mcp` (atomic writes that respect JURNAL append-only)

## How to use this bundle

1. **At session start**: `mavis-session-lifecycle-skill` → state-of-the-system
2. **Before any non-trivial action**: confirm `mavis-r33-bimodal-skill` rules are followed (state mutation needs R0)
3. **Before finalizing any artifact**: apply `mavis-triple-crunch-skill` checks (3 axioms must pass)
4. **Before saving anything**: apply `mavis-memory-curator-skill` (3-question test)
5. **At any file deliverable**: apply `mavis-deliverable-handoff-skill` (`<media />` not bare paths)

## Anti-patterns

- ❌ Skipping R33 for "trivial" ops. Trivial ops don't need R0 but DO need the 3-mode discipline visible.
- ❌ Skipping Triple Crunch. Even short outputs benefit from a 30-second Eliade Realitate check ("does this describe what actually is?").
- ❌ Saving memory without applying the 3-question test.
- ❌ Printing a file path instead of using `<media />` for a deliverable.

## Cross-references

- Skill index (single point of truth): `mavis-skill-index`
- Classifier data: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\70_CONNECTORS\70_personal_skill_index.md` (248 Behavioral skills classified — review/evaluate/validate/etc.)
- Taxonomy: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\00_INDEX\00_skill_taxonomy.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §2` (R33), §3 (Triple Crunch), §6 (SOUL/CONSTINTA)

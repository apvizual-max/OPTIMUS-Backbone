---
name: mavis-bot-creator-skill
description: The process of creating a new member skill for the Mavis Session Extract Bot — how to locate a session source, find where its record really lives, write the extractor and an independent verifier, prove the verifier can fail, and link the finished skill into the bot's registry and list. Load this when a new source (Qwen Studio, DeepSeek, a web-based AI, Hermes, Antigravity, or anything else) needs a session extractor, or when an existing member skill must be rebuilt or extended. This is the second member of mavis-session-extract-bot-skill.
role: meta
kind: process
bot: mavis-session-extract-bot-skill
---

# mavis-bot-creator-skill

**This is the process this very bot was built with.** Every future member skill comes
through here. The bot's own history is the worked example: the first member
(`mavis-session-transcript-skill`) was created by running exactly these steps, and the
proof that they work is in that skill's `runs.md`.

---

## The rule that makes this a skill and not a habit

**A member skill is not a plan.** It is a folder on disk with an extractor that runs, a
verifier that can fail, a `SKILL.md` that says how, and a `runs.md` that remembers. A
source that has been *studied* is a gap. A source that has been *extracted from* is a
member.

---

## STEP 0 — name it

| Kind | Format | Example |
|---|---|---|
| Functional | `mavis-session-<artifact>-skill` | `mavis-session-transcript-skill` |
| Meta | `mavis-bot-<process>-skill` | `mavis-bot-creator-skill` |

One source per functional skill. The **artifact** word says what is produced; the **source**
goes in the frontmatter `source:` field, not the folder name — so `transcript` can exist
once per source without collisions.

The folder name, the frontmatter `name:`, and the registry entry are **one string**. The
verifier fails if they drift.

## STEP 1 — locate the source, by measurement

Do not guess a path. Find where the runtime actually stores conversations, and **prove it**
by reading a file that exists.

```powershell
# where might it be?
Get-ChildItem "$env:USERPROFILE\.minimax" -Directory -Force | Select-Object Name
# is there a store that mentions the session id?
Select-String -Path "<candidate>\*.jsonl" -Pattern "<sessionId>" -List
```

Record what you found, and what you ruled out. The search is part of the deliverable.

## STEP 2 — find where the record *really* lives

**This is the step that decides whether the extractor works.** A session's conversation is
usually spread over several files, and the one with the obvious name often holds only a
fragment. For the local MiniMax Code runtime the truth was:

| Candidate | What it actually held | Verdict |
|---|---|---|
| `messages.jsonl` | the **tail** after the last compaction | 340 rows — a fragment |
| `snapshots\g*.jsonl` | the compacted working context | 172 rows — a summary |
| `runtime-state.sqlite` → `local_runtime_message_rows` | **every message row** | 2 821 rows — the record |

**Procedure:** for each candidate store, count what it holds, then compare the counts. The
store that holds *every* row, in order, with full payloads is the source. If a file "looks
complete", count it before trusting it — the first file you reach for was wrong, and the
difference was 94% of the conversation.

## STEP 3 — write the extractor

Node >= 22, **Node builtins only** (`node:sqlite`, `node:crypto`, `node:fs`). No npm.

It must:

- read the source **read-only** — never write into a runtime store;
- freeze the boundary of a live session (e.g. `MAX(id)` captured at start) so the snapshot
  is internally consistent and reproducible;
- emit the fixed output shape (§3 of the bot's `SPEC.md`): `<title>.md`, `<title>.jsonl`,
  `manifest.json`, `raw\`;
- **inline externalised tool output** — a pointer is a receipt, not the data (§5 of the SPEC);
- **declare** anything unrecoverable in `manifest.json` → `gaps[]` — never drop it silently;
- print a self-check line and exit non-zero if its own accounting does not add up.

## STEP 4 — write the INDEPENDENT verifier

A separate script that **re-queries the source** and compares. It must not read the
extractor's output and declare itself correct. Checks V1–V8 are listed in the bot's
`SPEC.md` §6 — implement them.

## STEP 5 — prove the verifier can fail

**Mandatory before linking.** Corrupt a copy of the artifact (drop rows) and confirm the
verifier rejects it and names the defects.

```powershell
node <skill>\verify-*.mjs ...          # exit 0 on the good copy
# corrupt a copy -> must exit 1 and name the missing rows
```

A verifier that has never gone red is not evidence of anything. Record both results in
the member's `runs.md`.

## STEP 6 — write the member's `SKILL.md`

Use `templates/skill-template/SKILL.md`. Required frontmatter:

```yaml
---
name: mavis-session-<artifact>-skill      # == folder name
description: <one paragraph: what it extracts, when to load it, what it produces>
role: functional                            # functional | meta
source: <source-id>
bot: mavis-session-extract-bot-skill        # the back-link — the verifier checks it
---
```

Required sections: why it exists · the procedure (numbered steps with real commands) ·
what it guarantees · **known limits, stated out loud** · the doctrine it obeys.

**The limits section is not optional.** A member skill that hides its limits will be
trusted with a job it cannot do.

## STEP 7 — create the run log

`runs.md` in the member's folder, with the header the bot writes on first use. The
registry verifier requires the file to exist.

## STEP 8 — link it into the bot

```powershell
node "<bot>\scripts\bot-registry.mjs" link --name <skillName> --role functional `
     --source <sourceId> --purpose "<one line>"
```

The link command **refuses** if the skill is not on disk — a plan cannot be linked.

Then, by hand:
1. add the member's row to the **table in §3** of `mavis-session-extract-bot-skill/SKILL.md`
   (the verifier fails if a registered skill is missing from that table);
2. add `role:` and `bot:` to its frontmatter;
3. move it out of `planned_sources` in `registry.json` if it was listed there.

## STEP 9 — prove the whole bot is healthy

```powershell
node "<bot>\scripts\bot-registry.mjs" verify     # exit 0
```

## STEP 10 — close the loop

Log this creation as a run of **this** skill, and of the member:

```powershell
node "<bot>\scripts\log-run.mjs" --skill mavis-bot-creator-skill --status success `
     --task "created <skillName>" --outcome "<what was proven>"
node "<bot>\scripts\log-run.mjs" --skill <skillName> --status success `
     --task "falsification + coverage" --outcome "<measured numbers>"
```

---

## Definition of done

The checklist is in `checklists/definition-of-done.md`. In short — a member is done when:

- [ ] the source's record was **located by measurement**, and the candidates ruled out are written down;
- [ ] the extractor runs and produces the fixed output shape;
- [ ] the verifier is **independent** and exits 0 on the good artifact;
- [ ] the verifier **rejects a corrupted copy** (falsification executed, both results recorded);
- [ ] `SKILL.md` has valid frontmatter, the back-link, the procedure, the guarantees and the **limits**;
- [ ] `runs.md` exists and holds at least the creation entry;
- [ ] `registry.json` lists it, the bot's table lists it, `bot-registry.mjs verify` exits 0;
- [ ] the creation is logged in the member's and the creator's run logs.

---

## Anti-patterns

- ❌ **Guessing the store path.** Find it and read a file that exists.
- ❌ **Trusting the file with the obvious name.** Count what it holds.
- ❌ **A verifier that shares code with the extractor.** It then verifies itself.
- ❌ **Keeping the receipt instead of the data.** "There is a file somewhere" is not the output.
- ❌ **Registering a skill that does not exist yet.** A plan is a gap.
- ❌ **A member with no limits section.** It will be trusted with work it cannot do.
- ❌ **Editing the bot's contract silently.** If the shape changes, `SPEC.md` and the bot's
  `SKILL.md` change with it — and the change is logged.

---

## Files

| File | What it is |
|---|---|
| `SKILL.md` | this process |
| `templates/skill-template/SKILL.md` | the skeleton a new member starts from |
| `templates/skill-template/README.md` | what each file of a member is for |
| `checklists/definition-of-done.md` | the gate a member must pass before it is linked |
| `runs.md` | this skill's own run log — every member it created |

**Cross-references:** `mavis-session-extract-bot-skill` (the hub, the contract, the
registry) · `mavis-session-transcript-skill` (the reference implementation) ·
`mavis-skill-index` (the master index).

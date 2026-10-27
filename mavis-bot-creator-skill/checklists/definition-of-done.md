# Definition of done — a member skill of the Mavis Session Extract Bot

A member is linked when **every** box below is true and can be shown. Nothing here is a
formality; each line is a claim that must have a measurement behind it.

## The source

- [ ] The source's session store was **located by measurement**, and a file that exists was
      read to prove it.
- [ ] The candidates that were ruled out are **written down** (path + what each held).
- [ ] The store that holds **every** row, in order, with full payloads was identified —
      not the store with the obvious filename.

## The extractor

- [ ] Runs with Node builtins only; **no third-party npm packages**.
- [ ] Opens the source **read-only**; writes nothing into it.
- [ ] Freezes the boundary of a live session and records it in the manifest.
- [ ] Emits the fixed shape: `<title>.md`, `<title>.jsonl`, `manifest.json`, `raw\`.
- [ ] Inlines **externalised tool output** (a receipt is not the data), resolving relative
      pointers against the source's own artifact directory **and** a global index.
- [ ] Declares every unrecoverable item in `manifest.json` → `gaps[]`.
- [ ] Exits non-zero when its own accounting does not add up.

## The verifier

- [ ] Is a **separate** script that re-queries the source (it does not reuse the
      extractor's parsing, or it verifies itself).
- [ ] Implements checks V1–V8 from the bot's `SPEC.md` §6.
- [ ] Exits **0** on a good artifact, with the counts printed.
- [ ] **Falsification executed**: on a corrupted copy it exits **1** and names the defects.
      Both results recorded in `runs.md`.

## The documentation

- [ ] `SKILL.md` frontmatter: `name` == folder name, `description`, `role`, `source`,
      `bot: mavis-session-extract-bot-skill`.
- [ ] `SKILL.md` body: why it exists · the procedure with real commands · what it
      guarantees · **known limits, stated out loud** · the doctrine it obeys.
- [ ] `runs.md` exists with its header.

## The link

- [ ] `registry.json` lists the member (`bot-registry.mjs link`).
- [ ] The bot's `SKILL.md` §3 table lists the member.
- [ ] The member is no longer only a `planned_sources` entry.
- [ ] `node scripts\bot-registry.mjs verify` exits **0**.

## The loop

- [ ] The creation is logged in the **creator's** run log.
- [ ] The member's own first run (falsification + coverage) is logged in the member's log.
- [ ] If the run changed the bot's contract (shape, naming, location, dependencies), then
      the bot's `SKILL.md` and `SPEC.md` are updated too.

---

**Reference:** the first member, `mavis-session-transcript-skill`, was completed through
exactly these steps on 2026-10-27 — its `runs.md` holds the measured numbers.

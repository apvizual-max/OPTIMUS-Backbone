# SPEC — Mavis Google Access Bot

The technical contract behind `SKILL.md`. Read this when you need to change the
shape, extend the registry, or write a new member.

---

## 1. The member shape

```
mavis-skill-<capability>\
  SKILL.md            the member: role, why, procedure, guarantees, LIMITS
  runs.md             append-only run log - every run, with its measured numbers
  scripts\            the member's own verifier (and any instrument it needs)
```

**Required, and checked by `bot-registry.mjs verify`:**

| Requirement | Why it is not optional |
|---|---|
| `SKILL.md` exists and parses | a member that cannot be read cannot be loaded |
| frontmatter `name` == folder name | one string, three places; the verifier fails if they drift |
| frontmatter `description` | the routing layer reads this, not the body |
| frontmatter `role` (`functional` \| `meta`) | the verifier distinguishes members from references |
| frontmatter `bot: mavis-google-access-bot` | the back-link: a member knows its hub |
| `runs.md` exists | a success without its numbers is a story, not evidence |
| `scripts\` holds a runnable verifier | a check that cannot fail is not a check |

**References** (`role: reference`) are held to the weaker contract they can
honestly meet: the folder and its `SKILL.md` must exist, and the frontmatter
name must not contradict the folder. They are **not** required to carry a run
log or a back-link — this bot does not own their files, and demanding it would
be a false failure.

---

## 2. The registry schema

```jsonc
{
  "schemaVersion": 1,
  "bot": "mavis-google-access-bot",
  "bot_display_name": "Mavis Google Access Bot",
  "version": "1.0",
  "created_at": "YYYY-MM-DD",
  "purpose": "<one paragraph>",
  "naming": { "functional": "...", "meta": "...", "reference": "...", "rule": "..." },
  "frontmatter_required": ["name", "description", "role", "bot"],
  "roles": { "hub": "...", "functional": "...", "meta": "...", "reference": "..." },
  "contract": { "C1": "...", "C2": "...", "...": "..." },
  "skills": [
    {
      "name": "mavis-skill-<capability>",
      "role": "functional",
      "source": "<source id>",
      "purpose": "<one line>",
      "status": "WIRED | BLUEPRINT | BLOCKED",
      "path": "",                 // "" = <skills root>/<name>
      "added_at": "YYYY-MM-DD",
      "verified": "<the measurement that justified WIRED>"
    }
  ],
  "roadmap": [ { "item": "...", "status": "PLANNED | DEFERRED_BY_USER | OUT_OF_SCOPE", "detail": "..." } ],
  "update_loop": { "rule": "...", "log": "scripts/log-run.mjs", "registry": "scripts/bot-registry.mjs" },
  "handoff": { "folder": "...", "owner_skill": "...", "files": ["..."] }
}
```

**`verified` is not decoration.** A member is `WIRED` only when a verifier
measured it. Without that field the registry would be a list of claims.

---

## 3. The verifier contract

Every member ships `scripts/verify-*.mjs`. It must:

1. **Re-query the system**, not read the member's own notes.
2. **Print one line per check**, in the form `OK  <id> <detail>` /
   `FAIL <id> <detail>`, and a final `VERDICT=PASS` or `VERDICT=FAIL`.
3. **Exit 0 when green, 1 when a check failed.** A crash is exit 3 — distinct
   from both, because a crash must never read as a pass.
4. **Report an unmeasurable thing as UNKNOWN**, never as OK. (Example: the
   ExtendLM verifier prints `UNK` when `gh` is unavailable, and still exits 0
   — because unknown is not a failure, and pretending otherwise is worse.)
5. **Be able to go red.** A verifier that has never failed is not evidence.
6. **Print no secret.** Lengths, labels, HTTP codes and counts — never a
   token, never a credential.

### The naming of checks

`V1`, `V2`, … for the checks of one verifier, each with a stable meaning:
`V1` is the first thing that must hold, `V2` the next. A defect report names
the check id, so the ids must not be renumbered when a check is added — a new
check gets the next free number.

---

## 4. The registry verifier

```powershell
node "<bot>\scripts\bot-registry.mjs" list
node "<bot>\scripts\bot-registry.mjs" verify      # exit 0 = healthy
node "<bot>\scripts\bot-registry.mjs" show --name <skill>
node "<bot>\scripts\bot-registry.mjs" link --name <skill> --role functional --source <id> --purpose "<one line>"
```

`verify` checks, for every registered skill:

- the folder and its `SKILL.md` exist;
- the frontmatter name matches the folder;
- members carry `description`, a valid `role`, the bot back-link and `runs.md`;
- functional members ship a runner in `scripts\`;
- no name appears twice;
- **every registered skill is mentioned in the bot's `SKILL.md`** — the table
  and the registry are two faces of one list, and a member missing from the
  table is a defect.

`link` **refuses** a skill that is not on disk: *a plan is a gap, not a skill.*

---

## 5. The run log

```powershell
node "<bot>\scripts\log-run.mjs" --skill <member> --status success|error \
     --task "<what was done>" --outcome "<measured result>" [--error "<verbatim>"]
```

- The log is **append-only**. A correction is a new entry referencing the old.
- The entry is **read back** after the append; an append that cannot be read
  back is reported as a failure.
- The error, when there is one, is recorded **verbatim** — a paraphrased error
  is a different error.
- The **lesson** goes into the member's `SKILL.md`, edited in place. The
  script does not do that: only the agent that learned it can phrase it.

---

## 6. The output contract of this ecosystem

The bot's own output contract is the ecosystem's, not a transcript shape. When
a **handoff** is requested:

```
<target>\  (the location the requester named - binding)
  README.md                  the entry point
  HANDOFF-<subject>.md       state, contract, procedures, known limits
  PRIMING-PROMPT.md          the prompt for a session with no context
  SKILLS-INDEX.md            the skills that matter, indexed and linked
  STATE-MEASURED.md          the measured state, dated
  MANIFEST.json              the machine-readable index
```

The rules — the location is binding, nothing is written in two places, the
hazard rule for a public repository, and the priming-prompt shape — live in
`mavis-skill-access-handoff/SKILL.md`.

---

## 7. Hard rules

- **The credential never leaves the volume.** Not into an image layer, a repo,
  a log, a chat message, or a handoff.
- **No fabricated interfaces.** If a path cannot be located, say
  `NOT LOCATED — here is how to confirm by another route`.
- **No third-party npm packages** in the verifiers — Node builtins only.
- **Namespace separation (Popy, 2026-10-05):** minimax and Hermes are separate
  universes. Never point one at the other's container, profile, port or
  credential. Duplication is the correct answer — two independent instances
  cannot destroy each other; a shared one can.
- **A refusal is a measured answer.** `REFUSED` is never `OK` and never
  `ERROR`.

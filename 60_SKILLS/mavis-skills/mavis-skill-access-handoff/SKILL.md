---
name: mavis-skill-access-handoff
description: The protocol for handing the Google Access work to a session with zero context and zero memory. Load this when preparing a handoff, when picking one up, or when a session has to take over Google Access without re-deriving anything. Owns the handoff location contract, the priming-prompt shape, the rule that a handoff states measured facts and never promises, and the list of what must be verified before a handoff is called ready.
role: meta
bot: mavis-google-access-bot
---

# mavis-skill-access-handoff

**Role.** The process of moving this work across a boundary that erases
everything: a new session, another machine, another agent. A handoff is not a
summary — it is the **minimum a stranger needs to continue correctly**, written
so that nothing has to be re-derived and nothing has to be trusted blindly.

---

## 1. The rule

> **A handoff is complete when the next agent can act without asking a
> question it could have read.**

That is the test. Not *"is the summary complete"* — it never is — but *"can the
next agent measure the state, find the broken piece, and repair it without
context"*.

Corollary: **a handoff states measured facts and file paths, never promises.**
A promise is a claim the reader cannot check. A measurement is a claim they can
re-check in one command.

---

## 2. The location contract

```
<handoff-folder>\
  README.md                  the entry point: what this is and where to start
  HANDOFF-<subject>.md       the complete handoff: state, contract, procedures
  PRIMING-PROMPT.md          the prompt to paste into the new session
  SKILLS-INDEX.md            the skills that matter, indexed and linked
  STATE-MEASURED.md          the measured state, with the date and the numbers
  MANIFEST.json              machine-readable index of the above
```

The folder named by the requester is **binding** — the handoff does not choose
its own location and does not write itself in two places.

**Hazard rule (measured, 2026-10-28).** If the handoff folder sits inside a
**public** git repository, write the ignore rule **before** the first commit
and prove it (`git check-ignore -v <file>`; `git add -A --dry-run` must not
list the folder). The alternative — a transcript-shaped document published by
an automated commit — is not recoverable by deleting the file later.

---

## 3. The shape of a priming prompt

A priming prompt is what a session with zero context reads first. It must be:

| Contains | Example |
|---|---|
| **the goal**, in one paragraph | *"keep the permanent Google connection alive and verifiable"* |
| **the entry commands**, copy-ready | the control point, the probe, the task names |
| **the measured state**, with numbers | `VERDICT=PASS`, 32 tools, 33 scopes, 11 checks |
| **the contract**, as rules | do not rebuild; repair the failing check; the credential never leaves the volume |
| **the known refusals**, so they are not re-diagnosed | keep 403, sites 404 — by design |
| **where the skills are**, linked | the central bot and its members |
| **what is NOT to be done** | no re-setup, no re-consent unless Google demands it, no scope additions without verification |

It must **not** contain: a narrative of how the work got here, an apology, a
to-do list of things that were already done, or anything the reader can measure
better themselves.

---

## 4. The procedure — preparing a handoff

1. **Measure the state now.** The doctor, the task list, the repo divergence,
   the encoding gate, the secret scan. Numbers with the date.
2. **Write the state file** (`STATE-MEASURED.md`) from those numbers only.
3. **Index the skills** (`SKILLS-INDEX.md`) — each with its path, what it owns,
   and why it is in the list.
4. **Write the handoff** (`HANDOFF-*.md`) — state, contract, procedures, known
   limits, what the next agent must not redo.
5. **Write the priming prompt** (`PRIMING-PROMPT.md`) — the shape in §3.
6. **Write the manifest** (`MANIFEST.json`) — the machine-readable index.
7. **Verify the handoff**: every path it names exists; every number in it was
   measured in this session; the folder passes the encoding gate; the secret
   scan is clean.
8. **Deliver the files** — printing a path is not delivery.

---

## 4-bis. Step 7, measured: what "verify every path" actually means

"Every path it names exists" is not a sentence — it is a **sweep**, and it has a
measured shape. A path in a handoff rots silently, and a broken pointer costs
the next agent a whole search.

**The sweep.** Extract every file-like token from every handoff document, then
resolve each one against **every plausible root** — the project root, the
handoff folder, and each documented subfolder (`skills\`, `api\`, `mcp\`,
`09_LOGS\`, `raport-archive\`, …). For the ones still unresolved, try a
**leaf-name search** across the tree.

```powershell
$all = @{}
foreach ($d in Get-ChildItem $handoff -File -Filter *.md) {
  $txt = [Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($d.FullName))
  foreach ($m in [regex]::Matches($txt,'[A-Za-z0-9_][A-Za-z0-9_\-\.\\\/]*\.(jsonl|json|md|py|ps1|txt|html)')) {
    $all[$m.Value] = $d.Name
  }
}
```

**Measured 2026-10-28 (SENTINEL_PRIME):** 121 distinct file-like tokens across
the handoff documents; 110 resolved on the first pass; 11 unresolved — and
**all 11 explained**, not one a broken pointer:

- **regex artifacts** (the sweep's fault, not the document's): `state-history.json`
  where the document actually says `state-history.jsonl`; `03-31.md` and
  `20-04.md`, which are filename *tails* inside prose; `Node.js` and a bare
  `SKILL.md`, which are not file references at all; `Users\apviz\…`, where the
  `C:\` prefix sat outside the character class.
- **paths outside the project, cited with their full path** — e.g.
  `C:\Users\apviz\.minimax\mcp.json`.
- **paths that deliberately do not exist**, named in the handoff *as*
  non-existent, so the next agent does not hunt for them.

**The rule that fell out:** a document is not wrong because a token does not
resolve — but **an unresolved token must be explained, in writing, in the same
handoff.** An unexplained unresolved token is a defect.

**Two traps in the sweep itself.**
- The alternation must be **longest-first** (`jsonl|json`), or every `.jsonl`
  truncates to `.json` and you "find" a broken pointer that does not exist.
- Never let a forward sweep become the verdict. A token that does not resolve
  under your first root list may resolve under another, and a broken pointer
  reported from an incomplete root list is a false alarm that sends the next
  agent looking for a file that was never missing.

## 4-ter. The handoff must also say what NOT to repair

A zero-context instance meets a handoff with fresh eyes and a bias toward
action. Anything that *looks* broken will be "fixed".

Measured 2026-10-28 (SENTINEL_PRIME): a health-check freshness bound that
looked mis-tuned, and an empty `core.hooksPath` that looked like a lost
config. Both had been **ratified as correct** in the project's own documents. A
new instance that "fixed" them would have:

- widened a bound so a header would read green — hiding the exact fact the
  system exists to report;
- re-armed a hook that was disabled on purpose, because it blocked every
  commit.

So the handoff carries a **"do not repair" list**, inside the priming prompt,
with the reason next to each item:

```
NU REPARA limitele de prospețime - măsurat: artefactele sunt scrise la cerere.
NU "repara" core.hooksPath gol - e starea intenționată.
```

**The reason next to the item is what makes it stick.** "Don't touch X" alone
reads as an unexplained warning; "don't touch X, because Y is true and
ratified" reads as a fact to check.

## 4-quater. The skills must travel as byte-identical copies

When the handoff carries the skills — so a fresh instance without a skills
directory still has them — the copies are **byte-identical to their sources**,
verified with a hash and not by eye, and a **manifest** says what each one
owns. Regenerate a copy when its source changes; never edit a copy. The
previous versions are not lost: they sit in the version history of whatever
repository carries them.

**Measured, same session:** a copy left behind a source edit is a silent
divergence — the instance reads the stale copy and the agent reads the fresh
one, and neither of them can say why they disagree.

## 5. The procedure — picking a handoff up

1. Read `README.md`, then `PRIMING-PROMPT.md`, then `HANDOFF-*.md`.
2. **Re-measure before believing.** The numbers carry a date; if they are
   stale, the first command you run is the control point.
3. Load the central bot skill and the member that owns the piece you touch.
4. Never rebuild from scratch: the settings exist and run by themselves.

---

## 6. What it guarantees

- The next agent starts from measurements, not from a narrative.
- Nothing has to be re-derived, and nothing has to be trusted blindly.
- The failure modes of the previous session are written down, so they are not
  repeated.

---

## 7. Known limits, stated out loud

- **A handoff goes stale.** Every number carries a date; the reader is told to
  re-measure. A handoff is a snapshot, not a live feed.
- **Files move.** A path in a handoff can rot; that is why §4 step 7 verifies
  every path at hand-off time.
- **The handoff cannot carry a secret.** A credential belongs in the mounted
  volume, never in a document.

---

## 8. Cross-references

- `mavis-google-access-bot` — the hub that owns this skill
- `mavis-deliverable-handoff-skill` — how files reach Popy
- `mavis-session-lifecycle-skill` — the session lifecycle this handoff serves
- Docs: `Mavis-Google_Access/.handoff/`

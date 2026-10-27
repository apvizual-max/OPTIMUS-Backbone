# Run log — mavis-session-extract-bot-skill

Append-only. Each entry is one use of this skill: what was attempted, what was
measured, and (when it failed) the error verbatim. A corrected entry is a NEW
entry that references the old one — nothing above is ever rewritten.

Written by `mavis-session-extract-bot-skill` → `log-run.mjs`.

## 2026-10-28 01:17:23 — success — bot created; first member linked
- source: self
- outcome: registry cu 2 membri (1 functional + 1 meta); 7 surse planificate; contractul C1-C7, taxonomia de erori si formatul de iesire definite in SPEC.md
- logged-by: mavis-session-extract-bot-skill

## 2026-10-28 01:17:23 — error — log-run.mjs --out into a not-yet-existing folder
- source: self
- outcome: repaired, re-run OK
- error: ENOENT: no such file or directory, open '<bot>\\logs\\bot-runs.md' (node:fs writeFileUtf8) — the script did not create the parent directory; fixed at the source with mkdirSync(dirname(logPath), {recursive:true})
- logged-by: mavis-session-extract-bot-skill


<!-- SOT-STATUS-BANNER
  Added 2026-10-02 10:46 by scripts\stamp-doc-status.ps1

  THIS IS A POINT-IN-TIME DOCUMENT: standing code-review rules (still in force).

  It is deliberately NOT rewritten -- rewriting it would destroy the record of
  what was true when it was written. For the CURRENT system state read:

    POPY_MiniMax_OPTIMUS_Status_Report-10-02-2026.md   <- current state, for Popy
    mavis-minimax-optimus-system                        <- skill: restore + config SOT
    mavis-minimax-index-folder-update                   <- skill: how to index this folder
    optimus status   /  cc start   /  cc guard          <- live truth, measured
-->
# Code Review Rules — OPTIMUS Prime / Mavis

> **Purpose**: paste this into MiniMax Code → Settings → Code review → "Custom review rules".
> **Format**: plain Markdown. Sections are reviewed in order. Each rule is concrete, has a bad/good example, and references Popy's actual stack (TypeScript MCP servers, Python Hermes, PowerShell ops, Markdown doctrine, Obsidian Second Brain, MCP fleet).
> **Generated**: 2026-09-18 for the OPTIMUS Prime local deployment.
> **Scope**: any diff in `C:\Users\apviz\.minimax-agent\projects\` or any of Mavis's managed dirs (`C:\Users\apviz\.minimax\agents\mavis\skills\`, `C:\Users\apviz\.minimax\mcp.json`, etc.).

## §0 Reviewer posture

- You are reviewing **for Popy**, not for a generic audience. Popy is a senior design strategist / systems architect — not a coder. Optimize for **clarity, correctness, and operational safety**, not for code golf.
- **Zero fabrication**: if you don't know what a symbol does, read its definition before commenting. Do not invent APIs, paths, or behaviors.
- **Concrete findings only**: report discrete, actionable defects that affect correctness, security, performance, or maintainability enough that Popy would likely fix them. Skip nitpicks.
- **State the trigger + impact** for each finding. Example: *"this regex compiles but matches `null` against the user's id, returning 401 instead of 403 in the unauthenticated branch — see line 42"*. Vague findings are not findings.
- **Reference the smallest useful line range** (`path:line` or `path:start-end`).
- **Do not propose fixes unless asked**. Review is read-only. Fixes are a separate step.

## §1 SENTINEL doctrine invariants (apply to every diff)

### Zero fabrication
- Never invent: tool names, APIs, file paths, command outputs, package versions, CLI flags, MCP server names, model identifiers, prices.
- If a comment claims something you can't verify from the diff, flag it as "unverified claim".

### R33 Bimodal — no silent execution
- The diff must not contain code that mutates persistent state outside a clear `R0` boundary (config files written silently, files deleted without consent, external API calls without scope).
- For destructive operations, the diff must include either an explicit user-confirmation gate or a JURNAL_OGLINDA-style trail.

### Triple Crunch
- Architectural changes (new modules, new bridges, schema changes) should be **documented** with rationale, not just code.
- If the diff introduces a new axiom or operational principle without amending the doctrine file (`SENTINEL_OPERATIONAL_DOCTRINE.md`), flag it: *"new principle 'X' is asserted in code but not in doctrine — propose amendment to SENTINEL_OPERATIONAL_DOCTRINE.md first"*.

### DRAG / DRAC
- When the diff crosses system boundaries (Hermes ↔ Mavis ↔ Antigravity ↔ Qwen), document the integration surface in the relevant bridge file (`10_BRIDGES/10_<name>.md`) or in a JURNAL_OGLINDA entry.

### SOUL ↔ CONSTINTA
- Long outputs and architecture docs must lead with the conclusion (SOUL) and follow with evidence (CONSTINTA). If a doc is all evidence without a conclusion, flag it.

### JURNAL_OGLINDA — append-only
- The diff must not silently edit/delete entries in `40_REGISTRIES/40_partition_*.md` or any `JURNAL_OGLINDA` table. Correct appends are fine; edits are forbidden.
- If a diff adds a new JURNAL_OGLINDA row, it should have at minimum: `| YYYY-MM-DD | <event> | <notes> |`.

### CODUL SACRU — irrevocable
- Architectural choices that are flagged as `CODUL SACRU` in the doctrine must not be casually reworked in the diff.

## §2 TypeScript / Node.js — MCP servers + npm globals

### bun runtime required for several MCPs
- **gdrive-mcp, gmail-mcp, google-workspace-mcp, gdrive-mcp-auth** are TypeScript and require the **bun** runtime. `bun` is **NOT on PATH** by default.
- Correct command: `C:\Program Files\Qwen\resources\bun\bun.exe` v1.2.10 (bundled with Qwen Studio).
- Bad: `command: "C:\Users\apviz\AppData\Roaming\npm\gdrive-mcp.cmd"` (falls back to global `bun`, which doesn't exist).
- Good: `command: "C:\Program Files\Qwen\resources\bun\bun.exe", args: ["C:\Users\apviz\AppData\Roaming\npm\node_modules\gdrive-mcp\src\index.ts"]`.

### Use the `mavis` CLI to wire MCPs — do not hand-edit
- MCP servers are configured via `mavis mcp list / get / create / update / delete`. The runtime persists them.
- Bad: hand-editing `mcp.json` directly — bypasses the runtime's validation and triggers a config drift.
- Good: `mavis({ command: "mcp update", args: { name: "<server>", enabled: true } })`.

### Never invoke `docker container prune -a`
- The 31 `hermes-mcp-*` Docker containers are load-bearing swarm. Lost the entire fleet on 2026-08-08 because of this command.
- Bad: any shell command in the diff that runs `docker container prune`, `docker rm -f hermes-mcp-*`, or `docker system prune -a`.
- Good: diagnose first (`docker ps`, `docker logs`, `docker inspect`), restart ONE container (`docker restart <name>`), rebuild last.

### Node MCPs that ship as `.cmd` wrappers (mcp-docker, mcp-git, mcp-obsidian, notebooklm-mcp, chrome-devtools-mcp, agent-browser-mcp, mcp-server-filesystem)
- Use the npm-installed `.cmd` directly: `C:\Users\apviz\AppData\Roaming\npm\<name>.cmd`.
- Bad: relative paths (`./mcp-docker.cmd`) — won't resolve from Mavis's runtime cwd.
- Good: absolute paths.

### Avoid `any` in MCP tool definitions
- MCP tool schemas should use `zod` schemas with explicit types. Untyped `any` lets malformed input pass through and corrupts the bridge.

### Don't reinvent the wheel
- For filesystem ops, prefer `mcp-server-filesystem` over a custom solution.
- For git, prefer `mcp-git` over a wrapper that shells out to `git.exe`.

## §3 Python — Hermes + 31 `hermes-mcp-*` containers

### Hermes is at v0.21.3 (NOT v0.21.1)
- Bad: comments, configs, or scripts hardcode `v0.21.1`.
- Good: use `hermes --version` at runtime to read the actual version, or hardcode the verified version with a JURNAL note.

### The 31 `hermes-mcp-*` containers have specific responsibilities
- Each container maps to a tool category: `hermes-mcp-obsidian` → vault ops, `hermes-mcp-notebooklm` → NotebookLM queries, `hermes-mcp-antigravity-bridge` → Antigravity dispatch, etc.
- Don't assume a container can do what its name doesn't imply. Check `hermes mcp list` before wiring custom dispatch.

### Python dependency hygiene
- Hermes uses a `venv` at `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\`. Don't `pip install` globally.
- Bad: `pip install <pkg>` to system Python — breaks the venv.
- Good: `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\pip.exe install <pkg>` (or use `uv` if present).

### Python imports — prefer stdlib over external
- For file ops, prefer `pathlib.Path` over `os.path`.
- For JSON, prefer `json` stdlib over external parsers.
- For HTTP in MCP servers, prefer `httpx` (already in MCP ecosystem) over `requests`.

### Watch for the Hermes gateway warning
- Running `hermes.exe` prints a warning: *"A previous `hermes update` pulled new code but did not restart running gateways."* This is harmless; do not flag it as an error.

## §4 PowerShell — Windows ops

### Use PowerShell, not bash
- The runtime is PowerShell. Scripts in the diff should use PowerShell syntax: `Get-ChildItem`, `Select-String`, `Test-Path`, etc.
- Bad: `ls -la`, `head`, `tail`, `grep`, `wc`, `&&`.
- Good: `Get-ChildItem`, `Select-Object -First`, `Select-Object -Last`, `Select-String`, `Measure-Object`.

### Always set `$ErrorActionPreference = 'Stop'` for multi-statement scripts
- Prevents silent failures that look like success.
- Bad: scripts with no error preference — a failing `Test-Path` returns `$false` but the script keeps going.
- Good: every script starts with `$ErrorActionPreference = 'Stop'`.

### For native commands, also check `$LASTEXITCODE`
- `$ErrorActionPreference` doesn't catch native command (`.exe`) exit codes. Set `$PSNativeCommandUseErrorActionPreference = $true` or check `$LASTEXITCODE` after each native call.

### Paths use `\` on Windows
- Bad: paths with mixed separators or `/` (works in PowerShell but inconsistent with Windows shell habits).
- Good: backslashes. Use `Join-Path` for portability.

### Use `Test-Path -PathType Leaf` before reporting a file deliverable
- Don't report a file as created unless `Test-Path` confirms it exists on disk.

### Use `mavis-trash <path>` instead of `Remove-Item -Recurse -Force`
- The desktop permission gate blocks raw `Remove-Item -Recurse -Force`. Use the recoverable-trash command for any irreversible delete.
- Bad: `Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue`.
- Good: `mavis-trash $path`.

## §5 Markdown — doctrine, registries, second brain

### Memory entries (canonical format)
- Memory entries MUST use the canonical format:
  ```
  <!-- mem-append-reason: <why this is worth saving>. -->
  ### <topic> (<date>)
  Type: <identity | architecture | rules | pointers | collaboration rules | professional context | project reference>

  <content>
  ```
- Bad: free-form text in the Memory modal — breaks programmatic read.
- Good: structured entries with `mem-append-reason` + `###` + `Type:` lines.

### Memory entries are NOT paste-into-Custom-instructions material
- The Custom instructions box expects plain prose.
- Bad: pasting the Memory modal content (with HTML comments) into Custom instructions — breaks parsing.
- Good: keeping Memory entries in the Memory modal; writing the doctrine as plain prose for Custom instructions.

### Append-only registries
- `40_REGISTRIES/40_partition_*.md` and `40_REGISTRIES/40_sacru_corpus.md` are **append-only**. New rows are added; old rows are not edited.
- Corrections are new entries that reference the old by timestamp + excerpt.
- Bad: editing an existing JURNAL_OGLINDA row "to fix a typo".
- Good: appending a new row with `Correction to <date> entry: ...`.

### Doctrine file is the paste-into-UI artifact
- `SENTINEL_OPERATIONAL_DOCTRINE.md` is plain prose for the Custom instructions box.
- Keep it free of `<!-- mem-append-reason -->` HTML comments — those are memory format, not instruction format.

### Backbone project structure
- The Mavis orchestration layer has 8 sections: `00_INDEX/`, `10_BRIDGES/`, `20_PROTOCOLS/`, `30_WORKFLOWS/`, `40_REGISTRIES/`, `50_TEMPLATES/`, `60_SKILLS/`, `70_CONNECTORS/`.
- New bridges go in `10_BRIDGES/`. New protocols in `20_PROTOCOLS/`. New workflows in `30_WORKFLOWS/`. Use the templates in `50_TEMPLATES/`.

### Skill directory name must match `name:` frontmatter
- For every `mavis-<subject>-skill/SKILL.md`, the directory name and the YAML `name:` field MUST match.
- Bad: directory `mavis-foo-skill/` containing `name: foo-skill`.
- Good: directory `mavis-foo-skill/` containing `name: mavis-foo-skill`.

### Naming convention for skills
- Mavis agent skills use `mavis-<subject>-skill` prefix.
- Hermes uses `hermes-<subject>-skill`. Antigravity uses `agy-<subject>-skill` (or similar). Each AI in the OPTIMUS Prime swarm follows the same pattern.
- Bad: bare names without the agent prefix (`foo-skill`).
- Good: prefixed names (`mavis-foo-skill`).

## §6 Obsidian Second Brain

### Vault path
- `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\` — do not move or rename.

### Propose before writing
- Any write to the vault (new note, edit, move, delete) requires R0 from Popy first.
- Bad: writing `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\New Note.md` silently.
- Good: proposing the file path + content to Popy, then writing after R0.

### `obsidian-mcp` is the right tool
- For vault ops from Mavis, use the `obsidian-mcp` MCP server (already wired). It handles backlinks + indexing correctly.
- Bad: Mavis doing raw `Add-Content` to a vault file — breaks backlink indexing.
- Good: `mcp_invoke({ tool_name: "obsidian.write_note", ... })`.

### Don't write outside the vault
- Writes must stay inside `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\`. No writes to `E:\` root, `E:\CLAUDE\MINTE\` root, or anywhere else on E: without R0.

## §7 MCP fleet discipline

### Don't create a new MCP server if one already exists
- Before adding: `mavis mcp list`. If the capability is already covered by an existing MCP, use that one.
- Bad: adding `mavis-gmail-mcp` when `gmail-mcp` is already wired.
- Good: reusing `gmail-mcp` and documenting why in the bridge file.

### MCP server enabled state is operational, not aesthetic
- An MCP server that's wired but not enabled returns nothing on calls. Don't disable one without noting why in JURNAL_OGLINDA.

### Token Plan Plus wiring — NOT live yet
- Popy's target is **Token Plan Plus ($22/mo)** wired to Hermes as the M3 brain. Currently NOT done. Don't write code or configs that assume this wiring.

### OAuth-bootstrap pending MCPs
- `gdrive-mcp`, `gmail-mcp`, `google-workspace-mcp`, `google-calendar-mcp` are wired but need Popy-driven browser OAuth bootstrap to return live data. Don't write tests that assume OAuth has been done.

## §8 Output discipline for code/docs

### Lead with the conclusion
- Long outputs (architecture decisions, doctrine, public-facing docs): conclusion first, evidence after.
- Bad: 30 lines of evidence before stating the recommendation.
- Good: recommendation in line 1, evidence in lines 2+.

### Reference code as `path:line`
- One or two citations per claim. Evidence list only when many.

### No emoji spam, no Markdown links wrapped in backticks
- Bad: `[click here](https://...)` rendered as `<https://...>` for no reason.
- Good: plain links or descriptive text.

### Deliverables must use `<media />` or `<deliver-assets>`
- Mavis's filesystem is not accessible to Popy. Don't print a path alone — emit the tag.
- Bad: *"I wrote the file at C:\Users\apviz\..."* (Popy can't see it).
- Good: `<deliver-assets><media src="C:\Users\..." caption="..." /></deliver-assets>`.

### Never emit pseudo-`<ask_user>` tags in plain prose
- Use the actual `ask_user` tool. Don't fake it with XML in prose.

## §9 What NOT to flag (the noise list)

- **Formatting**: whitespace, quote style, line length — skip unless they hide a defect.
- **Pre-existing issues**: only flag what's introduced by the diff, not what's already there.
- **Subjective preferences**: "I would name it differently" — skip unless the name is genuinely misleading.
- **Missing tests**: skip unless the diff adds new behavior with no test path.
- **Speculative risks**: "this might break in production" — skip without a concrete trigger.
- **Routine lint**: trailing whitespace, missing semicolons, etc. — handled by CI, not review.

## §10 When in doubt

- Read the surrounding call sites before flagging cross-component impact.
- For paths and tool names, verify against `mavis mcp list` and `mavis agent get` before flagging.
- For doctrine claims, verify against `C:\Users\apviz\.minimax-agent\projects\SENTINEL_OPERATIONAL_DOCTRINE.md` before flagging.
- For memory claims, verify against the live `memory(target=main, operation=read)` before flagging.

If you can't verify a claim, **say so explicitly** — *"I cannot verify this from the diff; please confirm"*. Never invent.

---

**End of rules. Paste into MiniMax Code → Settings → Code review → "Custom review rules". Save.**


<!-- SOT-STATUS-BANNER
  Added 2026-10-02 10:46 by scripts\stamp-doc-status.ps1

  THIS IS A POINT-IN-TIME DOCUMENT: integration report v3, superseded by the v2 status report of today.

  It is deliberately NOT rewritten -- rewriting it would destroy the record of
  what was true when it was written. For the CURRENT system state read:

    POPY_MiniMax_OPTIMUS_Status_Report-10-02-2026.md   <- current state, for Popy
    mavis-minimax-optimus-system                        <- skill: restore + config SOT
    mavis-minimax-index-folder-update                   <- skill: how to index this folder
    optimus status   /  cc start   /  cc guard          <- live truth, measured
-->
# OPTIMUS — MiniMax / Hermes / Antigravity Integration Report

**Version:** 3 (final for this integration cycle)
**Date:** 2026-10-02
**Author:** Mavis (MiniMax Code), operating under the SENTINEL doctrine
**Operator:** Popy (Alexandru Popescu) — OPTIMUS Prime
**Workspace:** `C:\Users\apviz\.minimax-agent\projects\`

---

## 1. Verdict

The integration is **operational**. Every layer Mavis owns is running, wired and
verified against live state — not against configuration files that merely look
right.

Three items remain genuinely blocked, and all three require a human action that
cannot be simulated: a Google Cloud credential, a browser consent click, and a
billing decision. They are listed in §6 with the exact steps.

**This cycle additionally fixed four defects that were making the system lie to
you.** The doctor reported "BROKEN symlink" on a healthy file, reported "~1 MCP
server" when 34 were wired, reported a venv as current when it could not verify
currency at all, and took 57 seconds to answer. Details in §4.

---

## 2. What is running right now

| Layer | Component | State | Evidence |
|---|---|---|---|
| Swarm | Docker containers | 53 running | `docker ps` count |
| Swarm | `hermes-mcp-*` | **31 running** | doctor `hermes.containers` |
| Swarm | `hermes-sentinel-daemon` | running | doctor `hermes.sentinel_container` |
| Bridge | `minimax-hermes-bridge` | healthy, 8801 | `/health` ok |
| Bridge | `minimax-antigravity-bridge` | healthy, 8802 | `/health` ok |
| Hermes | CLI + Desktop | working | `hermes mcp list` ≈9.1 s |
| Hermes | MiniMax-M3 wiring | present | doctor `hermes.version` |
| Hermes | Enforcement invariants | 4/4 hold | doctor `hermes.sentinel_enforcement` |
| Hermes | MCP fleet | **34 servers** | doctor `hermes.mcp_fleet` |
| Mavis | Skills | **30** | `~/.minimax/agents/mavis/skills` |
| Mavis | MCP servers | 13 configured | `mavis mcp list` |
| Docs | Stirling-PDF API | HTTP 200, no auth | `stirling-pdf.ps1` |
| Docs | LibreOffice convert | working | `convert-document.ps1` |

**Container census is 53 — unchanged from the post-DRAC baseline.** No pruning,
no `rm -f`, no destructive Docker operation was performed in this cycle.

---

## 3. Bridge layer

Two Linux containers act as MiniMax Code ↔ target bridges.

**They cannot execute Windows binaries.** `hermes.exe` and `agy.exe` are PE
binaries; a Linux container cannot run them. So `/delegate` is a **command-spec
emitter**: it validates the request and returns the exact host command. Mavis
then executes it on Windows via the bash tool. This is a design constraint, not
a workaround — and it is now verified working on both bridges:

```
POST 8801/delegate -> & 'C:\...\hermes\bin\hermes.exe' -z '<prompt>'
POST 8802/delegate -> & 'C:\...\agy\bin\agy.exe' --print '<prompt>'
```

### Endpoints (both bridges)

`/health` · `/schema` · `/doctor` · `/doctor/detailed` · `/audit` ·
`/journal` (GET + POST) · `/delegate` (POST) · `/heal` (POST)

Hermes bridge healers: `sync_venv`, `heal_enforcement`, `restart_container`.

**Mount policy:** Hermes is mounted read-write because the bridge must diagnose
and repair it. Antigravity is mounted read-only — it is a council/back-up, not a
mutator.

---

## 4. Defects found and fixed in this cycle

These were live faults, not theoretical ones. Each was diagnosed to a root cause,
fixed, and re-verified.

### 4.1 `/doctor` took 57.4 seconds

`c_hermes_optimus` walked the `HERMES_OPTIMUS` tree **twice** (once to count
files, once to sum bytes). That tree is 1,984 files. Every `stat()` on a Windows
bind mount inside a Linux container is a gRPC-FUSE round trip at roughly 8 ms —
so the check cost ~16 s, and repeated for the byte total.

There is no need for a health check to compute an exact byte total. Replaced with
a depth-bounded, count-bounded single walk. Same anti-pattern existed in the
core's `/audit` (which materialised the entire file list *and then* stat'd every
entry); also fixed.

**57.4 s → 6.2 s**, with all 12 checks now reporting.

> Verification note: the first pass of this diagnosis was itself contaminated. A
> capability probe reused one output directory across targets and reported a
> leftover file from a previous run as a success. Re-run in isolation, the
> opposite result appeared. The isolated result is the one recorded below.

### 4.2 "cli-config.yaml is a BROKEN symlink" — false

The check was `if cli.is_symlink() or (cli.exists() and cli.stat().st_size == 0)`.
That flags **any** symlink as broken. The link is healthy: it resolves to
`C:\Users\apviz\AppData\Local\hermes\config.yaml`.

It still reports a warning, correctly this time, because a Windows NTFS link
genuinely cannot be resolved from inside the Linux container. The check now says
so and points at the host-side verification command, instead of asserting a fault
that does not exist.

### 4.3 "config declares ~1 mcp_servers blocks" — wrong by 33

`txt.count("mcp_servers:")` counts the single YAML **key**, then `or`-short
circuits the fallback that was supposed to count entries. The real fleet is
**34 servers**. Now parses the child entries under the key.

### 4.4 "venv stamp current vs lockfile" — unverifiable, reported as OK

The check looked for `.venv-stamp`, which does not exist. So `stale` was always
`False` and the check reported success on a venv it had not actually examined.
The real artefact is `install-stamp.json`. Now compares that against `uv.lock`,
surfaces the version and dirty flag, and reports **warn — not ok** when the stamp
is absent.

### 4.5 Stirling-PDF `SECURITY_ENABLED=false` did nothing

The widely-cited variable is wrong. The API kept returning 401. The correct name
was read out of the container's own `/configs/settings.yml`, which documents its
own override convention:

> `security.enableLogin` → `SECURITY_INITIALLOGIN_USERNAME` (their example) →
> therefore `security.enableLogin` → **`SECURITY_ENABLELOGIN`**

With `SECURITY_ENABLELOGIN=false` the API returns **HTTP 200**. Recorded in
`mavis-doc-bridge-skill` so it is not re-derived.

---

## 5. Restored source of truth

`C:\Users\apviz\docker-compose.yml` had been deleted, leaving **18 containers
running as orphans** with no definition on disk. This is the most dangerous
condition in the system: a Docker restart, a prune, or a `compose up` with
`--remove-orphans` would have destroyed load-bearing services with no way to
recreate them.

Rebuilt from live `docker inspect` state — images, restart policies, networks,
entrypoints, commands, port bindings, binds, and named volumes. Environment
variables were **diffed against each image's own defaults**, so the file records
what Popy actually set rather than a wall of image boilerplate.

Validation: `docker compose config --quiet` → exit 0, 18 services.

**Two traps are documented in the file header:**
- `Antigravity_Ecosystem_Terminal` shares the project name but is defined by its
  own compose file. Compose reports it as an orphan. **`--remove-orphans` would
  delete it.**
- `apviz_tempo-data` is declared but unused; the volume is preserved, not dropped.

Only `stirling-pdf` was recreated via compose. No other service was touched.

---

## 6. Blocked — requires a human action

These are not unfinished work. Each is gated on something only Popy can supply.

### 6.1 Google OAuth — blocks 4 MCP servers

`gdrive-mcp` ships a placeholder credential in its own source:

```
setup-auth.ts:15  const DEFAULT_CLIENT_SECRET = "GOCSPX-YourSecretHere";
                                       // TODO: Replace with actual secret
```

The four Google MCPs do **not** share one auth model, so they need separate
attention once a client exists:

| Server | Auth mechanism |
|---|---|
| `gdrive-mcp` | `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN`, or `bun run setup <id> <secret>` |
| `gmail-mcp` | ships the same placeholder in `dist/main.js` |
| `google-calendar-mcp` | `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` (`dist/config/environment.js:30-31`) |
| `google-workspace-mcp` | **file-based** — `~/.google-mcp/credentials.json` via an add-account OAuth flow |

**To unblock:** create an OAuth 2.0 client in Google Cloud Console with the
Drive, Gmail, Workspace and Calendar APIs enabled, then provide the client ID
and secret. Everything downstream is already wired and waiting.

### 6.2 Qwen OAuth — needs one browser consent

Qwen CLI 0.19.2 is installed and `hermes-mcp-qwen` is running, but **no OAuth
credential is stored** — `~/.qwen/` contains no `oauth_creds.json`. The container
runs but the CLI behind it is unauthenticated.

**To unblock:** run `qwen auth qwen-oauth` and complete the browser consent.
This cannot be automated — it is an interactive grant.

### 6.3 Token Plan Plus — billing decision

Two prior cron runs failed with `Token Plan usage limit reached (2056)`. Needs a
billing decision; no technical work is outstanding.

---

## 7. Deliberate non-actions

- **No `docker container prune -a`.** Not run, not recommended. The swarm was
  lost this way once before.
- **No `docker rm -f hermes-mcp-*`.** The 31 containers are load-bearing.
- **No `hermes update`.** Hermes source is 219 commits behind and the tree is
  dirty, but updating would revert hand-edits and is a decision, not a task.
- **No software installed.** No package was added in this cycle.
- **No `mavis-trash` deletions.** The scratch test artifacts in
  `scratch\docbridge\` were kept as evidence.

---

## 8. Artefacts

**Scripts**
- `scripts\convert-document.ps1` — LibreOffice bridge
- `scripts\stirling-pdf.ps1` — Stirling-PDF bridge
- `scripts\extract_wayland_workflows.py` — Wayland workflow extractor
- `scripts\rebuild-classifier.ps1`, `scripts\inferred_purposes.ps1` — skill classifier

**Skill (new this cycle)**
- `mavis-doc-bridge-skill` — both doc bridges, the verified capability matrix,
  the `SECURITY_ENABLELOGIN` finding, and the SPA-catch-all route probe

**Config**
- `C:\Users\apviz\docker-compose.yml` — **recreated**, 18 services

**Reports**
- `OPTIMUS_MINIMAX_HERMES_ANTIGRAVITY_INTEGRATION_REPORT.md` — this file
- `OPTIMUS_SYSTEM_TIMELINE.md`

---

## 9. Acceptance results

Every claim in §2 was produced by executing against live state.

| Test | Result |
|---|---|
| `txt → pdf` via LibreOffice | PASS — 15,192 B |
| `txt → docx` via LibreOffice | PASS — 5,045 B |
| `pdf → html` via LibreOffice | PASS — 484 B |
| `pdf → docx` correctly rejected | PASS — guard fires with actionable message |
| Stirling `pdfa` | PASS — 12,712 B, magic `%PDF-1.7` |
| Stirling `merge` (2 files) | PASS — 22,786 B |
| `8801 /doctor` | 6.2 s · 9 ok / 3 warn / 0 fail |
| `8802 /doctor` | warn ×2 (host-side probes, by design) |
| `/delegate` both bridges | PASS — correct host command emitted |
| Container census after all work | 53 — unchanged |

The 3 remaining Hermes warnings are all truthful: the container-side symlink
view, the dirty Hermes source tree, and the host-side status probe. **Zero false
positives remain.**

---

## 10. Recommended next actions

1. **Create the Google OAuth client** — unblocks 4 MCPs at once (§6.1).
2. **Run `qwen auth qwen-oauth`** — one consent click (§6.2).
3. **Decide on Token Plan Plus** (§6.3).
4. **Decide on `hermes update`** — the tree is dirty and 219 commits behind;
   updating will revert uncommitted local edits.
5. **Consider a startup guard** on `C:\Users\apviz\docker-compose.yml` now that
   it exists, so it cannot silently disappear again.

---

*SLG = 100%. Zero fabrication: every claim above was executed and observed.
Where something could not be verified, it is marked BLOCKED rather than assumed.*


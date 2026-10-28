# PUNCT-DE-CONTROL — Google Access

**One command. One verdict. Proves the permanent Google connection instead of
rebuilding it.**

Written 2026-10-28. Every number below was measured on this machine; the
measurement that produced each one is named next to it.

---

## The command

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\ga-doctor.mjs"
```

Exit **0** = every critical check passed. Exit **2** = at least one failed.
Exit **3** = the control point itself crashed (never reported as green).

A **WARN** is still exit **0**: a check that ends in the `DEGRADED_TRANSIENT`
state (a transient refusal that did not recover) is counted as a warning, the
blip is printed with its cause, and the summary reads
`failed=0 warnings=1`. A WARN is never a silent OK — the summary line and the
per-service cause line both say it out loud.

The wrapper `scripts\ga-doctor.ps1` adds the dated log line and propagates the
exit code. The scheduled task **`Google_Access_Doctor`** runs it every 30
minutes, so the system checks itself while nobody is in a conversation.

A new session — or **any other AI on this station** — runs that one command and
*knows* whether Google is connected. It does not have to trust a document, and
it does not have to rebuild anything.

---

## The eleven checks

| Check | What it proves | Measured 2026-10-28 01:54Z |
|---|---|---|
| `C1.container` | the container exists, runs, is healthy, has the right image and restart policy | `running / healthy / google-access:1.0.10 / unless-stopped` |
| `C1b.running-code` | the bytes **running** inside the container are the bytes **in the repo** | `repo=63e4ea8d2bbb running=63e4ea8d2bbb match=true` |
| `C2.health` | the grant is live, no re-auth is pending, the tool count is real | `grant=live reauth=false tools=32` |
| `C3.services` | a **live** call per Google service, classified OK / REFUSED / ERROR, with the **cause named** and a transient refusal re-probed | `state=HEALTHY OK=14 REFUSED=2[keep,sites] ERROR=0[] attempts=1` |
| `C4.extendlm` | the NotebookLM token is alive and its snapshot is published to the Cloud secret | `token_minutes_left=109 refresh_token=yes cloud_secret_age_min=11` |
| `C5.browser-mcp` | the registered Browser MCP path exists **and** the server answers over real stdio | `server=minimax-notebooklm tools=4` |
| `C6.mcp-registry` | `Google_Access` is registered globally, so every agent inherits it | `enabled=true url=http://127.0.0.1:8766/mcp` |
| `C10.mcp-paths` | every local path the global registry points to **exists on disk** | `checked=23 dead_total=0` |
| `C7.tasks` | the scheduled tasks that keep the system alive are all green | `count=4` |
| `C8.consent` | the re-consent listener is up, so a future re-consent is one click | `listener alive (processes=1)` |
| `C9.picker` | the state of the Photo Picker session | `session consumed - nothing to watch` |

**Verdict of that run: `SUMMARY checks=11 failed=0 warnings=0 VERDICT=PASS`,
exit 0.**

---

## Why each check exists (the defect it was born from)

A control point that cannot fail is not a control point. Every check below
exists because something specific broke, and was measured, not imagined.

- **`C1b.running-code`** — the 1.0.9 incident: the repository carried the
  repair, the image had been built before it, and the container ran the **old
  code** while every document claimed it was fixed. A healthy container proves
  it is alive, not that it is the thing you wrote.
- **`C10.mcp-paths`** — three registered MCP entries pointed at a folder that
  had been moved (`google-layer/` → `Mavis-Google_Access/google-layer/`). The
  registry said "enabled", the files did not exist, and **nothing said so**.
  A fourth entry pointed at a wrapper npm never created. The configuration is
  global: a dead path there breaks the capability for every agent on the
  station, not only for the session that wrote it.
- **`C3.services`** — Google Books answered HTTP 503 on two of three probes.
  A control point that turns red on a Google blip is a control point that gets
  ignored, so every unexpected refusal is now **re-probed, up to 4 attempts in
  total** (3 extra, with a delay between them), and the **cause is printed for
  every service** — never a bare `REFUSED`. A refusal that does not recover is
  split by its kind: a **permanent** one (403 / 404 / `MISSING_SCOPE` / an
  unrecognised refusal) is `state=FAILED_PERMANENT` and the check **FAILS**
  (exit 2); a **transient** one that recovers is `state=HEALTHY` with the blip
  still printed; a transient one that never recovers is
  `state=DEGRADED_TRANSIENT` → `CHECK C3.services WARN` → counted as a warning,
  exit 0. Measured Books blip rate ≈ **1 in 3 probes**: with 4 attempts the
  false-red probability fell from ≈ `(1/3)^2` ≈ **11 %** to ≈ `(1/3)^4` ≈
  **1.2 %**.
- **the same check, the other way round** — the re-probe must not hide a *real*
  bug behind the retry. The 2026-10-28 defect proved it: the Docs table
  walker threw on **every** document containing a table
  (`ERROR: el.table.rows.forEach is not a function`). A permanent failure
  re-probed 4 times never recovers, so it is reported as
  `state=FAILED_PERMANENT` → FAIL → exit 2. The retry hides Google blips, not
  the truth.
- **`C9.picker`** — a picker session that was completed and deleted answers
  404 forever after. Reporting that as a failure turned the heartbeat red, and
  through it the whole control point, for the user doing the very thing the
  picker exists for. A consumed session is now a state, not a defect.
- **`C7.tasks`** — the one check that watches the watchers.

### Falsification (the check that can fail)

```
node scripts/ga-doctor.mjs --self-test --fail C1.container   -> FAIL, exit 2
node scripts/ga-doctor.mjs --self-test --fail C10.mcp-paths   -> FAIL, exit 2
node scripts/ga-doctor.mjs --container NoSuchContainer_zzz    -> FAIL, exit 2
```

A check that cannot go red is not evidence.

The instrument also falsifies **itself**, offline, against the three states of
`C3` — no live call, no network:

```
node scripts/ga-doctor.mjs --self-test
SELFTEST_PROBE case=permanent_refusal expected=FAIL got=FAIL cause_named=yes result=PASS falsified=1 blocked=1
SELFTEST_PROBE case=transient_recovers expected=OK got=OK cause_named=yes result=PASS falsified=0 blocked=0
SELFTEST_PROBE case=transient_persistent expected=WARN got=WARN cause_named=yes result=PASS falsified=1 blocked=0
SELFTEST probes=3 falsified=2 blocked=1 expectations_met=3/3
VERDICT=PASS
```

Measured 2026-10-28, exit 0. And the falsification still bites:
`--self-test --fail C1.container` → `SUMMARY checks=11 failed=1 warnings=0`,
`VERDICT=FAIL`, exit 2.

---

## The permanent contract

| Concern | Where it lives | Who owns it |
|---|---|---|
| The credential | the mounted volume `data/credentials.json` | the container; **never** in an image layer |
| The MCP server | one Docker container, `Google_Access`, port 8766 | the host, `restart=unless-stopped` |
| The grant | one OAuth refresh token, 33 scopes, `apvizual@gmail.com` | Google; renewed silently |
| The registry | `C:\Users\apviz\.minimax\mcp.json` (global) | the station — every agent inherits it |
| The rules | `C:\Users\apviz\.minimax\AGENTS.md` §12.5 | every agent |
| The doctor | `scripts/ga-doctor.mjs` + task `Google_Access_Doctor` | the station, every 30 min |
| NotebookLM | ExtendLM; token rotated by the host, snapshot published to the Cloud secret | the host |

**Re-authentication is rare by design.** Access tokens are minted silently from
the refresh token. When the grant itself expires, `google_auth_status` says so
and prints one consent URL; the consent listener (`Google_Access_Consent`,
every 5 minutes) is already waiting on port 80 to catch the callback. The
authorisation click is the user's — and it is the **only** human step left.

---

## The two refusals

`keep` (403) and `sites` (404) are refused **by Google itself**: no grantable
scope exists for Keep, and the Sites API was retired. The tools report the
refusal; they never hide it and never fake success. Popy imports that content
through Gemini / other tools into Drive. Every other service is live.

---

## Related instruments

| Instrument | What it is for |
|---|---|
| `container/probe-services.mjs` | the per-service live probe behind `C3` |
| `scripts/probe-mcp-stdio.mjs` | proves that **any** registered MCP entry starts (used for the repaired entries) |
| `scripts/compare-layer-versions.py` | compares two copies of a file set line by line — born from a move that lost merged optimizations |
| `scripts/restore-layer-optimizations.py` | carries those optimizations forward with byte-level proof |
| `scripts/encoding-audit.py` | the BOM / UTF-8 / ASCII gate for every script |
| `scripts/sync-container-source.py` | live container source → repo, with a gate that the repo cannot drift |

See `docs/STARE-MASURATA.md` for the dated evidence behind every number here.

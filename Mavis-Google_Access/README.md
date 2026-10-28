# Mavis-Google_Access

**Permanent Google connection for Mavis Local (and for the Cloud side), on this station.**

One Docker container, one MCP server, one credential, no re-authentication friction.

| | |
|---|---|
| Container | `Google_Access` (Docker, image `google-access:1.0.10`) |
| MCP endpoint | `http://127.0.0.1:8766/mcp` (Streamable HTTP, JSON-RPC 2.0) |
| Health | `http://127.0.0.1:8766/health` |
| Credential | one OAuth refresh token, in the mounted volume `data/credentials.json` - **never in an image layer** |
| Grant | **33 scopes** on `apvizual@gmail.com`, verified live against `oauth2.googleapis.com/tokeninfo` |
| NotebookLM | through ExtendLM (MCP), token rotated automatically by the host, snapshot published to the Cloud secret |
| Heartbeat | Windows task `MavisExtendLMHeartbeat` (every 30 min) - rotates the token when it nears expiry and republishes the snapshot |
| Cloud | `MAVIS-CLOUD/.github/workflows/google-access.yml` - builds the same image from this repo and probes the live APIs (last run: success, `notebooklm` OK) |
| Source of truth | this folder (`container/` = the exact content of the image) |
| **Control point** | `node scripts/ga-doctor.mjs` - **one command, one verdict** over 11 checks; scheduled task `Google_Access_Doctor` (every 30 min). See `docs/PUNCT-DE-CONTROL.md` |

The container never touches the network for credentials and never asks for a
second sign-in. If the grant ever dies, the MCP tools say so explicitly
(`MISSING_SCOPE` / `GOOGLE_HTTP_401`) and `google_scope_upgrade` prints the one
consent URL that repairs it in a single browser click.

---

## The control point (read this first)

```powershell
node scripts/ga-doctor.mjs
```

This is how a new session - or **any other AI on this station** - knows the
connection works, without rebuilding anything:

```
SUMMARY checks=11 failed=0 warnings=0
VERDICT=PASS
```

Exit `0` = green, `2` = a check failed, `3` = the control point itself crashed
(never reported as green). A `WARN` — a transient Google refusal that did not
recover after 4 attempts — is still exit `0`, and the blip is printed, never
hidden. The checks cover the container, the bytes actually
running inside it, the live grant, a live call per Google service, the
ExtendLM token, the Browser MCP handshake, the global MCP registry, the
integrity of every path that registry points to, the scheduled tasks, the
re-consent listener and the Photo Picker session.

Full specification, with the defect each check was born from:
**`docs/PUNCT-DE-CONTROL.md`**.

---

## What is measured, and what is not

`node container/probe-services.mjs` calls every service tool against the live
Google APIs and classifies the ANSWER, not the request:

- `OK` - the API answered with data
- `REFUSED` - the API answered with a refusal (this is a measured refusal, not a crash)
- `ERROR` / `SKIP` - the call did not answer (never reported as success)

Last measured run (2026-10-28 02:05Z, image 1.0.10, grant of 33 scopes):
`TALLY={"OK":13,"REFUSED":3,"ERROR":0,"SKIP":0}`, `VERDICT=PASS`, `PROBE_EXIT=0`.
The third refusal is **transient**: Google Books answered HTTP 503 on 3 of the
5 raw probes of that session and `OK` on the other 2 — `probe-services.mjs`
does not retry, `C3.services` does (up to 4 attempts) and names the cause
either way. The steady-state 14/2 tally also came out of the Cloud runner
(run `40497337673`, conclusion `success`).

| Service | Tool | Result |
|---|---|---|
| Identity | `google_auth_status` | OK - `grant_live=true` |
| Drive | `gdrive_list` | OK - real files |
| Gmail | `gmail_list` | OK - real messages |
| Calendar | `gcalendar_list` | OK - real events |
| Books | `gbooks_search` | OK - real volumes (transient: HTTP 503 on 3 of 5 raw probes; `C3` re-probes) |
| Tasks | `gtasks_list` | OK - 1 list |
| Contacts | `gcontacts_list` | OK - 5 contacts |
| Docs | `gdocs_get` | OK - real document (5091 characters extracted from the transcript document that carries three tables) |
| Sheets | `gsheets_read` | OK - real sheet |
| Apps Script | `gscript_list` | OK - 1 project |
| YouTube | `youtube_my_videos` | OK - channel data |
| Photos | `gphotos_list` / `gphotos_picker_start` | OK - app-created content; the full library is reachable only through the **Photo Picker**, where the user selects (see `docs/TINERE-API-GOOGLE.md`) |
| Chat | `gchat_spaces` | OK - 15 spaces |
| Keep | `gkeep_list` | refused by Google - no grantable scope exists |
| Sites | `gsites_list` | refused by Google - the API was retired |
| NotebookLM | `notebooklm_ask` | **OK** - live answer through ExtendLM (see `docs/EXTENDLM.md`) |

Two services are refused by Google itself and are reported as such, never
hidden: **Keep** publishes no user-OAuth scope (workspace-admin only) and the
**Sites** API was retired (its scope left Google's registry). Asking for either
scope fails the ENTIRE consent request with `invalid_scope`, which is why they
are absent from the grant.

A third refusal is **transient**: Google Books answers HTTP 503 on some
probes. `C3.services` re-probes it up to 4 times, prints the cause per
service, and a transient that never recovers becomes `DEGRADED_TRANSIENT` —
a `WARN` (exit `0`), never a silent OK. A **permanent** refusal still fails
the check (exit `2`).

---

## Rebuilding the container from this folder

```powershell
docker build -t google-access:1.0.10 -f "C:\Users\apviz\.minimax\google-access\Dockerfile" "C:\Users\apviz\.minimax\google-access"
docker stop Google_Access; docker rm Google_Access
docker run -d --name Google_Access --restart unless-stopped `
  -p 127.0.0.1:8766:8766 -e GA_PORT=8766 `
  -v "C:\Users\apviz\.minimax\google-access\data:/data" `
  -v "E:\--- System Secrets:/secrets:ro" google-access:1.0.10
```

The credential lives in the mounted volume, so recreating the container never
loses the grant. The build context is the live source folder; `container/` in
this repository is kept identical to it by `scripts/sync-container-source.py`
(which also re-verifies that no credential path is ever tracked by git).

---

## The documents

| File | What it holds |
|---|---|
| `docs/STARE-MASURATA.md` | measured state, with dates and evidence |
| `docs/ARHITECTURA-GOOGLE-ACCESS.md` | how the pieces fit and why they are shaped this way |
| `docs/PERMANENTA-GOOGLE.md` | how the connection stays alive (publishing status, token lifecycle, repair) |
| `docs/EXTENDLM.md` | NotebookLM through ExtendLM (dynamic client registration, PKCE, real tool calls) |
| `docs/SESSIONE-2026-10-27.md` | what this session did, including every defect found and fixed |
| `docs/TINERE-API-GOOGLE.md` | the per-service API host table and the paths taken from the discovery documents |

## Legal pages

`PRIVACY.md` and `TERMS.md` are the pages the Google consent screen links to.

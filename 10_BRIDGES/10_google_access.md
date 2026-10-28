# Bridge — Google Access

**Status**: ✅ WIRED — one Docker container (`Google_Access`, image `google-access:1.0.9`), one OAuth credential, one MCP endpoint on `http://127.0.0.1:8766/mcp`, registered **globally** so every Mavis-family agent on this station inherits it. The control point is a single command: `node Mavis-Google_Access\scripts\ga-doctor.mjs`.

## Role in the swarm

Google Access is the **station's Google connectivity**, not a Mavis private tool. Everything that touches Google from this machine — Drive, Gmail, Docs, Sheets, Calendar, Photos, Books, Tasks, Script, Chat, YouTube, Contacts, and NotebookLM through ExtendLM — goes through this one container and this one credential.

That is the point of the name. A second AI, a new session, or another platform can connect to the same Google surface **without rebuilding anything**: the credential, the scopes, the rotation, the re-consent listener and the verification already exist and are kept alive by the operating system, not by a conversation being open.

**It is part of the backbone infrastructure.** The workflows on this station assume Google works; if Google does not, the workflows stop. So the system is built to survive reboots, session changes and re-auth events on its own.

## Surface (measured 2026-10-28)

| | |
|---|---|
| MCP endpoint | `http://127.0.0.1:8766/mcp` (Streamable HTTP, JSON-RPC 2.0) — registered globally as `Google_Access` in `C:\Users\apviz\.minimax\mcp.json` |
| Health | `http://127.0.0.1:8766/health` → `grant=live`, `reauth_required=false`, `tools=32` |
| Container | `Google_Access`, `--restart unless-stopped`, volume `data` (rw) + `E:\--- System Secrets` (ro) |
| Credential | one OAuth refresh token in the mounted volume, 33 scopes, **never** in an image layer and never in a repo |
| CLI harness (for AIs without MCP) | `node Mavis-Google_Access\container\mcp-call.mjs <tool> @args.json` |
| Control point | `node Mavis-Google_Access\scripts\ga-doctor.mjs` → one verdict, 11 checks, exit 0 / 2 / 3 |
| NotebookLM, second route | `minimax-notebooklm` (own Chrome profile, own CDP port 9412, 4 tools, session authenticated) |
| Project | `https://github.com/apvizual-max/Mavis-Google_Access` (public, `main`) |

## Activation (measured 2026-10-28)

- ✅ Container running, healthy, grant live, 32 tools
- ✅ Live probe of every service: **14 OK / 2 REFUSED / 0 ERROR** (`VERDICT=PASS`, exit 0)
- ✅ NotebookLM live through ExtendLM (160 tools behind the proxy) and through the browser server (4 tools)
- ✅ Registered globally → every agent inherits the MCP server
- ✅ Four scheduled tasks keep it alive: `Google_Access_Watch` (hourly, self-healing), `Google_Access_Doctor` (30 min, the control point), `MavisExtendLMHeartbeat` (30 min, rotates the NotebookLM token and publishes the snapshot to the Cloud secret), `MavisPickerHeartbeat` (15 min, captures the user's Photo Picker selection)
- ✅ `Google_Access_Consent` (5 min) keeps the re-consent listener on `http://localhost:80` alive, so a future re-consent is one click
- [ ] **Two services are refused by Google itself and stay refused**: `keep` (403, no grantable scope exists) and `sites` (404, the API was retired). Popy imports that content through Gemini/other tools into Drive instead. The tools report the refusal; they never pretend.

### Repaired 2026-10-28 (measured)

- **Three MCP entries were broken** and the registry said nothing: `gdrive-mcp`, `gmail-mcp` and `google-calendar-mcp` pointed at `projects\google-layer\…`, a folder moved on 27 Oct. Because the MCP configuration is **global**, a dead path there disables the capability for **every agent on the station**, not just the session that wrote it. Repaired in place; measured after: `gdrive-mcp` → 9 tools, `gmail-mcp` → 36 tools. `google-calendar-mcp` stays disabled (measured: it is an HTTP server, not a stdio one).
- **`docker-mcp` pointed at a wrapper npm never created**, and the package could not import its own dependency. Repaired in place (runtime deps installed into the existing package, entry pointed at the real entry point); measured: `INIT_OK=1`, 19 tools.
- **The `google-layer/` move was verified for presence, not for content** — three optimizations merged on 24 Oct stayed behind in the old repo. Carried forward with byte-level proof. Measured effect: `gdrive-mcp` answered in **2.264 ms** instead of **29.452 ms**.
- **A consumed Photo Picker session was reported as a defect.** A completed session answers 404 forever after; the control point went red for the user finishing the very action the picker exists for. It is now a state (`SESSION_CONSUMED`), not a failure.

Two checks exist *because* of these: `C1b.running-code` (the bytes running inside the container are the bytes in the repo — the 1.0.9 incident ran old code while every document said it was fixed) and `C10.mcp-paths` (every path the global registry points to exists on disk).

Full specification: `Mavis-Google_Access/docs/PUNCT-DE-CONTROL.md`.

## Use cases

- Any Google workspace operation from any AI on this station, through one endpoint
- Source-grounded research in NotebookLM, with citations, over Popy's corpus
- Reading the user's own photo library — **only the items the user selects** in the Photo Picker, by Google's design
- Daily Cloud-side verification: the same image, built from the same public source, probed against the live APIs

## Dispatch protocol

1. **Verify first, once per session**: `node Mavis-Google_Access\scripts\ga-doctor.mjs` → `VERDICT=PASS`. A red verdict names the failing check; do not "work around" a red system.
2. Call the MCP server `Google_Access` (or the CLI harness for an AI with no MCP client).
3. Treat `OK` / `REFUSED` / `ERROR` as three different answers. A `REFUSED` with Google's own code is a measured answer, not a failure.
4. For the photo library, run the picker flow: the session is polled by `MavisPickerHeartbeat`, so the selection is captured without anyone watching the conversation.
5. Never print, copy or commit a token. The credential lives in the volume; the tools print only labels, lengths and HTTP statuses.

## Permanence contract

| What | How it stays alive |
|---|---|
| The container | `--restart unless-stopped`, plus `Google_Access_Watch` recreates it from the newest local image if it is ever removed |
| The grant | refresh token of an app in **In production** — no 7-day expiry; the access token is minted silently on every call |
| The NotebookLM token | rotates automatically before expiry; the fresh snapshot is published to the Cloud secret every 30 min |
| The re-consent path | a listener on `http://localhost:80` is kept alive by a scheduled task; when the consent screen appears, the click is the only human action, and the code is exchanged, published, the container restarted and the probe run automatically |
| The verification | `Google_Access_Doctor` runs every 30 min and exits non-zero when anything is not green, so the failure is visible in the Task Scheduler, not only in a log |

**What is NOT done automatically**: the consent click itself, and the selection of photos in the picker. Both are physical authorizations on Google's side, by design, and both are one action — not a re-setup.

## Namespace separation (non-negotiable)

`minimax` (this station: port 8766, its own volume, its own Chrome profile on 9412) and `Hermes` are different universes. If Hermes needs Google, it builds **its own** instance with its own credential — two separate instances cannot destroy each other; a shared one can. Never point one at the other's resources, and never reuse this credential in a Hermes container.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-10-28 | Bridge formalized | ✅ `Google_Access` registered globally, 32 tools, 14 OK / 2 REFUSED / 0 ERROR measured on host and in the Cloud runner. Control point added (`ga-doctor.mjs`, 9 checks, exit 0/2, falsified in 3 directions). Re-consent listener made permanent (it had died with the session that started it). `google-layer/` moved to its only home, `Mavis-Google_Access\google-layer\`. |

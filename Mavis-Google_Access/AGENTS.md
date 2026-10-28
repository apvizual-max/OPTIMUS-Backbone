# AGENTS.md - Mavis-Google_Access

This folder is the working folder for the **permanent Google connection** of
Mavis Local (and of the Cloud side, through the same credential). Optimus CI
lives elsewhere and is handed over to another instance.

## Scope

Everything that touches permanent connectivity to Google services from this
station:

- the `Google_Access` container (one MCP server, one credential)
- the OAuth grant, its scopes, its lifetime
- NotebookLM through ExtendLM
- the browser-side paths (Browser MCP, Chrome DevTools, the `google-layer/`
  scripts)
- the probes that prove all of the above still work

## Rules that are not negotiable here

1. **Measure, don't declare.** A scope list is a claim. A service works only if
   a live API call answered with data. `container/probe-services.mjs` is the
   instrument; `docs/STARE-MASURATA.md` is its output, with a date.
2. **A refusal is a measured answer, not a failure.** `REFUSED` (with Google's
   own code) is a different thing from `ERROR` (nothing answered) and from
   `OK`. Never collapse them.
3. **One invalid scope kills the whole consent request.** Every scope added to
   `FULL_SCOPES` is verified against Google's scope registry or the discovery
   document before it goes in.
4. **One place knows the truth.** API hosts live in `API_BASE` (server.mjs).
   The credential lives in the mounted volume. The image content lives in
   `container/`. The repo is the rebuild source.
5. **Secrets never enter the repo.** `data/` is git-ignored; the image never
   contains the credential (`.dockerignore`).
6. **The authorisation click stays the user's.** Everything else - code
   exchange, credential publication, container restart, probe, notification - is
   automated.
7. **Namespaces stay separate.** `minimax` (this folder, port 8766, its own
   volume, `google-layer/minimax-notebooklm.js` on port 9412) and `Hermes` are
   different universes. If Hermes needs the same capability, build a separate
   instance; never point one at the other's resources.
8. **Commits are automatic on `main`. A push needs the user's R0.** (R0 for
   pushes on this stream was given on 27 Oct 2026 and is consumed by the
   pushes already made; a new push asks again unless it is part of the same
   approved unit.)

## Probes (run them before claiming anything)

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\ga-doctor.mjs"   # THE control point - 11 checks, one verdict
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\probe-mcp-stdio.mjs" --name <entry>  # does a registered MCP entry actually start?
node "C:\Users\apviz\.minimax\google-access\probe-services.mjs"   # every service, live
node "C:\Users\apviz\.minimax\google-access\state\probe-token.mjs" # what the token carries
docker inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}' Google_Access
Invoke-RestMethod http://127.0.0.1:8766/health
```

## The permanence contract

This is the part that must survive a session ending, an agent being replaced,
or another AI taking over on this station.

1. **One command proves it.** `ga-doctor.mjs` is the control point: 11
   independent checks, one verdict, exit 0/2/3. Do not rebuild the
   connection to find out whether it works - run the doctor. Full spec in
   `docs/PUNCT-DE-CONTROL.md`.
2. **The configuration is global.** `C:\Users\apviz\.minimax\mcp.json` is the
   MCP registry for the whole station, so `Google_Access` reaches every agent
   (workers, verifiers, other harnesses) without further registration. That
   also means **a path in an entry has to exist** - a dead path breaks the
   capability for everyone, silently. `C10.mcp-paths` checks exactly that.
3. **The credential never moves.** It lives in the mounted volume
   `data/credentials.json` and in the image **never**. Access tokens are minted
   silently from the refresh token; the token cache carries the credential's
   fingerprint, so a new grant invalidates the old cache automatically.
4. **Re-authentication is rare, and it is one click.** The consent listener
   (`Google_Access_Consent`, every 5 min) is already waiting on port 80 when
   a grant is renewed. The authorisation click stays the user's; everything
   else - code exchange, credential publication, container restart, probe,
   notification - is automated.
5. **Nothing is re-created on a whim.** If a session "does not have Google",
   run the doctor and repair the check that failed. Re-installing, re-scoped
   re-consenting or rebuilding the container is not a diagnostic step.
6. **A file that is present but older is not a migration.** When content moves
   between repos, compare it (`scripts/compare-layer-versions.py`), not just
   its presence - the `google-layer/` move of 2026-10-28 left three merged
   optimizations behind in the old repo, unnoticed for the whole day.
7. **One home.** `google-layer/` lives here. If something related appears
   elsewhere, it is referenced here, not copied back and forth.

## Where the live pieces are

| | |
|---|---|
| Source of the image | `C:\Users\apviz\.minimax\google-access` (synced into `container/` by `scripts/sync-container-source.py`) |
| Credential volume | `C:\Users\apviz\.minimax\google-access\data` → `/data` |
| Secrets volume | `E:\--- System Secrets` → `/secrets` (read only) |
| Google Cloud project | `gen-lang-client-0284509562` ("Sentinel Prime") |
| OAuth client used | `Sentinel Hermes CLI` (Desktop), id `1068987308935-5b7h17gt…` |
| ExtendLM server | `https://mcp.extendlm.com/mcp` (authorization server `https://api.extendlm.com`) |

## Conventions

- Docs are dated and cite the evidence that produced them.
- Corrections are new entries; the append-only journals stay append-only.
- The folder is the only home for this work. If something related appears
  elsewhere, it is referenced here, not copied back and forth.

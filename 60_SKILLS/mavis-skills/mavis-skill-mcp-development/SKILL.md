---
name: mavis-skill-mcp-development
description: How a new MCP server or tool joins the Google Access central access point on this station. Load this when adding a server to the global registry, adding a tool to the container, registering a local stdio server, or deciding whether a new capability belongs in the container (central, credential-bearing) or as a separate instance. Owns the registry contract, the proof required before a registration is called working, the namespace separation rule, and the roadmap of planned servers.
role: functional
bot: mavis-google-access-bot
---

# mavis-skill-mcp-development

**Role.** The development path for the central access point. A new capability
joins the ecosystem by a **measured route**, never by being declared.

---

## 1. Why it exists (the defect, not the preference)

Measured 2026-10-28: three registered entries pointed at a folder that had
been moved, and a fourth pointed at a wrapper npm never created. The registry
said "enabled" in all four cases. **Nothing said so.**

Because the MCP configuration is **global**, a dead path there does not break
one session — it breaks the capability for **every agent on the station**, and
it breaks *silently*. So the route for adding a server now ends in a proof, not
in a configuration edit.

---

## 2. Two kinds of capability — decide before you build

| | **Central (in the container)** | **Separate instance (own registry entry)** |
|---|---|---|
| Carries the Google credential | yes | no, or its own |
| Credential source | the mounted volume `data/` | its own store |
| Lives in | `container/server.mjs`, image `google-access:*` | its own process, registered globally |
| Reached at | `http://127.0.0.1:8766/mcp` | its own transport/endpoint |
| Right when | the capability needs the OAuth grant | the capability has its own auth, or its own lifecycle |

**Rule (measured 27 Oct 2026):** one invalid scope invalidates the **entire**
consent request. So a new Google scope is verified against Google's scope
registry or a discovery document **before** it goes into `FULL_SCOPES` — never
after, because a bad scope costs a human click.

---

## 3. The route for a new server

1. **Decide the kind** (central vs separate). If it needs the grant and nothing
   else does, it goes in the container.
2. **Build it in the repo's `container/`** — the repo is the rebuild source, and
   `scripts/sync-container-source.py` keeps repo and live source identical.
3. **Add its scopes** only after verifying them against Google's registry.
4. **Register it globally** with the `mavis` interface (never by hand-editing
   `mcp.json`):

   ```powershell
   mcp mcp update --name <entry> --command <exe> --args <script>
   ```

5. **Prove the handshake** — a real MCP `initialize` + `tools/list` over the
   real transport:

   ```powershell
   node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\probe-mcp-stdio.mjs" --name <entry>
   ```

   Expected: `INIT_OK=1 ... TOOLS=<n> EXIT=0`. A path that exists is not a
   server that runs.
6. **Add a check to the control point** if the capability is part of the access
   point's contract. New checks start as a real defect that the check would
   have caught.
7. **Declare it in the docs** — `docs/STARE-MASURATA.md`, with the date and the
   measurement, and the bridge file if it is part of the backbone.
8. **Log the run** in this skill's `runs.md`.

---

## 4. The registry contract

| Rule | Why it is not negotiable |
|---|---|
| The registry is **global** (`C:\Users\apviz\.minimax\mcp.json`) | it is how every agent inherits `Google_Access` — and how a dead path breaks everyone |
| The **path must exist** | measured: three entries pointed at a moved folder and said "enabled" |
| A stdio entry must complete a handshake | `google-calendar-mcp` is an HTTP server registered as stdio: it can never work, and it is disabled for that reason |
| `minimax` and `Hermes` are separate universes | Popy, 2026-10-05: **duplication is the correct answer**. Two independent instances cannot destroy each other; a shared one can |
| The container never reads a secret from an image layer | the credential enters only through the mounted volume |
| Every registered path is checked by `C10.mcp-paths` | the check exists because the failure was silent |

---

## 5. The roadmap — planned servers and capabilities

| Planned | Kind | Status | What still has to be found |
|---|---|---|---|
| **Browser-side MCPs** on the central point | separate instances | 🟡 PLANNED | see `mavis-skill-browser-mcp` §4 — picker window automation, NotebookLM source ingestion, a shared own-profile session, CDP health as a control-point check |
| **A second Docker-based MCP** on the same access point | central, own container | 🟡 PLANNED | the interface: same `/data` volume and same credential, or a second volume with its own OAuth client? Both are legal; only one is right per capability |
| **Photo library automation** beyond the picker | central | 🟡 PLANNED | the full library is unreachable since Google retired the scopes (March 2025) — only picker-selected content is, by design |
| **Keep and Sites** | central | ⏭ SKIPPED BY THE USER | see `mavis-skill-google-keep-sites` |
| **Google Cloud** | — | ⛔ OUT OF SCOPE | excluded by Popy's instruction |
| **WebMCP** (`webmcp.dev`) | separate | 🟡 PLANNED | needs the browser session open; the browser path on the host already covers the same apps |

---

## 6. What it guarantees

- Every registered server is proven before it is called working.
- A new capability is placed by a rule, not by preference.
- Namespace separation survives new additions.

---

## 7. Known limits, stated out loud

- **The registry is hand-checked by a script, not by the runtime.** `C10`
  catches dead paths at control-point time (every 30 min), not at the instant
  of the mistake.
- **This skill does not author the servers.** It owns the route and the proof.
- **Adding a Google scope costs a human click.** That is the price of a new
  central capability, and it is paid once — the grant then renews silently.

---

## 8. Cross-references

- `mavis-skill-google-access-control-point` — `C6` and `C10`, the two checks
  that guard the registry
- `mavis-skill-docker-access-point` — where a central tool actually lives
- `mavis-skill-browser-mcp` — the browser-side roadmap
- `mavis-mcp-management-skill` — the pre-existing MCP-management reference
- `mavis-google-access-bot` — the hub that owns this skill

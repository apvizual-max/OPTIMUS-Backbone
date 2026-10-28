---
name: mavis-skill-notebooklm-extendlm
description: The NotebookLM route of Google Access - the second route, and the only one that is an API. Load this when the browser route is insufficient, when the ExtendLM token needs rotating, when the Cloud secret has to be refreshed, or when a question must be answered from Popy's uploaded corpus with citations. Owns the single-owner rule (the host rotates, the Cloud consumes snapshots), the measured rotation and publication procedure, and the honest limits of both routes.
role: functional
bot: mavis-google-access-bot
---

# mavis-skill-notebooklm-extendlm

**Role.** The API-side route to NotebookLM, and the browser-side route it
complements. Google publishes **no public NotebookLM API** — confirmed from two
independent sources (the official Google directory lists only the Vertex AI
notebooks API; `gcloud services list --available` shows no NotebookLM service).
So there are exactly two doors: **ExtendLM** (MCP) and the **browser**.

---

## 1. Why it exists (the defect, not the preference)

The first ExtendLM attempt failed with `400 invalid_client_metadata`, because
the metadata declared `scope: "mcp"` — a scope the server does not accept. Nine
variants were probed until one worked: the body carries **no scope**, and the
scope returned by the server is used.

The second failure was ownership: the token expired, and the fix tried to
rotate it from two places at once — the container and the Cloud publisher —
which produced a fight over the same credential.

**So there is exactly one owner of the rotation: the host.**

---

## 2. The two routes, measured

| | **ExtendLM (MCP)** | **Browser (`minimax-notebooklm`)** |
|---|---|---|
| Transport | MCP over HTTPS | stdio + CDP on port **9412** |
| Auth | client credentials → access + refresh token | an already authenticated Chrome profile |
| Tools | **160** behind the proxy | **4** (`nblm_health`, `nblm_list_notebooks`, `nblm_get_sources`, `nblm_ask`) |
| Token lifetime | measured ~4 h access token, refreshable | the browser session (long-lived, user-signed-in) |
| Best for | the Cloud side, automation, bulk | reading what the browser already has |

Measured answer through ExtendLM: notebook **JULES**, `answer_chars=8139`,
`is_error=false` — the question reached the corpus and the answer is not an
error dressed up as one.

Notebooks seen live: JULES 182 sources · GEMINI & AI Studio 251 · CV-Automation
98 · SENTINEL Role 225 · AGENTS 8 · TRADE 1 · CV-Notebook 99 · CLIENTS 2 ·
OPTIMUS System 5.

---

## 3. The single-owner rule

```
host  ──rotates──▶  data/extendlm.json  ──snapshot──▶  Cloud secret
                 (the only writer)         (published, never rotated remotely)
```

- The **host** rotates, and only when the access token is under 60 minutes
  from expiry.
- The **Cloud** consumes a **snapshot** (`GOOGLE_EXTENDLM_CREDENTIAL_B64`) with
  `GA_EXTENDLM_NO_REFRESH=1` — it never rotates the credential it was given.
- Two writers of one credential is how they fight. This is the rule that keeps
  them apart.

---

## 4. The procedure

```powershell
# rotate + publish (only when needed)
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\publish-extendlm-secret.mjs"

# the scheduled rotation
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\extendlm-heartbeat.ps1"

# measure
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\probe-notebooklm.mjs"
```

The publisher persists atomically, publishes to the secret, and **reads the
timestamp back** (`SECRET_READBACK=present age_seconds=14`) — a write that was
not read back is not a write. The snapshot is redacted out of error messages
(`[REDACTED_SNAPSHOT]`), and the heartbeat log was measured to contain **no**
long base64 blob after the fix (`LONG_B64_BEFORE=1 → AFTER=0`).

The heartbeat is scheduled every 30 minutes: task **`MavisExtendLMHeartbeat`**.

---

## 5. What it guarantees

- The NotebookLM token is alive and published to the Cloud, measured by the
  control point (`C4`).
- Exactly one component rotates the credential.
- No token reaches a log, a repo or a chat message.

---

## 6. Known limits, stated out loud

- **ExtendLM needs the browser extension connected** on the host — the
  extension status is `connected=true` today, but it is a host-side fact that
  can change.
- **The Cloud runner cannot refresh.** It uses a snapshot with
  `GA_EXTENDLM_NO_REFRESH=1`; when the snapshot ages out, the host republishes.
  If the host is asleep, the Cloud's NotebookLM probe fails — and says so.
- **The browser route needs Chrome alive** on port 9412.
- **There is no Google-native alternative.** No API, no service to enable.

---

## 7. Cross-references

- `mavis-skill-browser-mcp` — the browser route and its own Chrome
- `mavis-skill-google-access-control-point` — `C4`, the ExtendLM check
- `mavis-google-access-bot` — the hub that owns this skill
- Docs: `Mavis-Google_Access/docs/EXTENDLM.md`

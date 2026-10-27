---
name: mavis-google-workspace-skill
description: Bridge to Google Workspace via the `google-workspace-mcp` MCP server (gwmcp alias). Covers Calendar, Drive, Docs, Sheets, Gmail. Currently DISABLED — requires Google OAuth bootstrap before enable.
---

# Google Workspace Bridge

The `google-workspace-mcp` MCP server is wired (gwmcp alias). Covers the full Google Workspace: Calendar, Drive, Docs, Sheets, Gmail, Contacts. Currently **disabled** because Google OAuth must be bootstrapped first.

## Activation steps

1. **OAuth bootstrap** — run the gwmcp OAuth flow once to grant Drive/Gmail/Calendar scopes:

   ```powershell
   & 'C:\Users\apviz\AppData\Roaming\npm\google-workspace-mcp.cmd' auth
   # or whatever the package's auth subcommand is
   ```

2. **Verify** the OAuth token is persisted.
3. **Enable the MCP server**:

   ```text
   mavis({ command: "mcp update", args: { name: "google-workspace-mcp", enabled: true } })
   ```

4. **Smoke-test** with a read-only operation (list today's calendar events).

## Alternative: per-service MCPs

If you prefer narrower OAuth scopes (one per service), use these instead — all wired but disabled:

- `gdrive-mcp` — Drive only
- `gmail-mcp` — Gmail only
- `google-calendar-mcp` — Calendar only

Each needs its own OAuth bootstrap.

## Hard rules

- 🚫 Never enable Google Workspace MCPs without OAuth being set up first — the tool calls will fail in confusing ways.
- R0 before any send / create / delete operation on Google's side.
- Treat all tokens as secrets. Do not log them.

## Reference

- Bridge file: `C:\Users\apviz\.minimax-agent\projects\10_BRIDGES\10_gemini.md` (Gemini shares the Google ecosystem)
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §9`

## Starea măsurată a rutelor Drive — 2026-10-27

Secțiunile de mai sus rămân valabile. Iată ce e **măsurat**, nu presupus:

| Rută | Stare măsurată |
|---|---|
| `gdrive-mcp` (MCP, Drive only) | `invalid_grant` — **token revocat** |
| `google-workspace-mcp` | cere un `account` necunoscut → apelul nu pornește |
| `verify-drive.js` (bun, `Mavis-Google_Access\google-layer\`) | `files.list` **FAILED**, **EXIT 2** |
| `gcloud auth application-default print-access-token` | token **valid**, dar Drive API → **HTTP 403** (fără scope) |

**Re-consentul tokenului e act ACCESS** — cere consimțământul lui Popy în
browser. Nu se ocolește unilateral și nu se scoate tokenul în chat.

### Fallback-ul care chiar funcționează: mirrorul local DriveFS

Nu e nevoie de API ca să citești Drive. Există o **rădăcină mirrorată local**,
`sync_type=MIRROR`, iar baza ei locală e lizibilă:

| Resursă | Stare |
|---|---|
| `metadata_sqlite_db` | **422 932 480 B**, lizibil read-only → **sursa de adevăr** |
| `mirror_metadata_sqlite_db` | 2 278 027 264 B, **blocată** de DriveFS (și cu `immutable=1`) |

Sonda care o folosește: `scripts\drivefs_probe.py`
(`--title` · `--newest` · `--root-state` · `--pending`), în folderul CI.

**Capcane măsurate:**

- Blob-ul din `items.proto` e *latura cloud* (id + părinte + titlu). Căutarea
  după **calea completă** nu se potrivește niciodată — se caută după
  `local_title`, apoi se verifică lanțul `stable_parents`.
- Primul dump `ReceiveMirrorRoots` din startup dă `connected=false`.
  **Starea finală e ultimul dump.**

### Ce înseamnă asta pentru canalul CI

Puntea Local ↔ Cloud folosește Drive drept **canal primar**, dar
**verificarea propagării nu trece prin API** — trece prin baza locală.
Concret: `scripts\mavis-drive-bridge.ps1 -Status` / `-Verify` raportează
`SYNCED` / `PENDING` / `NOT_UPLOADED` / `UNVERIFIED`. **`UNVERIFIED` nu e
succes.**

---

## Coada pentru Cloud are un contract — și poarta lui stă în CI

**Adiționat 2026-10-27, ~02:40.** Secțiunile de mai sus rămân valabile.

Pentru că Drive e canalul primar, **scrierea unei cereri pentru Cloud** nu e
opțională: e singurul mod prin care cererea ajunge la celălalt capăt al
puntei. Și ea are un **format contractual**, nu unul de bun-simț.

Formatul, citit **de pe discul Cloud-ului** (nu din memorie):

```
### [id] titlu
cerut de: local | data: YYYY-MM-DD
scope: cloud | local | ambele
ce trebuie: ...
livrare: unde trebuie să ajungă rezultatul
```

Cloud rulează **doar** tichetele cu `scope: cloud`. O coadă fără `scope:` e
o coadă goală, chiar dacă arată plină.

Contractul complet, cu proveniență: `docs/CONTRACT-CLOUD-QUEUE.md` în repo-ul CI.
Poarta: `scripts\queue-contract-check.ps1` — citește contractul **live** de pe
discul Cloud (raportează `CONTRACT_DRIFT` dacă se schimbă), verifică fiecare
tichetă, ținta de livrare (`QUEUE/DONE/`) și paritatea `TASK_ID` între canale.
Ieșire `0` / `1` / `2` — **`2` = contract ilizibil = UNKNOWN, nu succes**.

### Ce nu se face

- Nu se scrie o tichetă cu corpul trunchiat: `mavis-drive-bridge.ps1 -Publish`
  **refuză** (exit 2) un corp care se oprește la mijloc de propoziție.
- Nu se scrie cu `scope` necunoscut — **refuzat**, exit 2.
- Nu se declară „publicat" pe baza scrierii în folder: propagarea se
  **măsoară** (vezi secțiunea de mai sus), iar `UNVERIFIED` nu e succes.

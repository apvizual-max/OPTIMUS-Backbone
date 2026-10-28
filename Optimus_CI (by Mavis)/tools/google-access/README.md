# Google_Access — sursa containerului

Copie de reconstrucție a serverului MCP care dă acces permanent la Google.
Se află aici pentru ca sistemul să poată fi **reconstruit din GitHub**, nu
doar de pe discul unei mașini.

| Ce | Valoare măsurată (2026-10-27) |
|---|---|
| Server | `server.mjs` — MCP Streamable-HTTP, **25 unelte**, zero dependențe npm |
| Container | `Google_Access` · imagine `google-access:1.0.2` · `--restart unless-stopped` |
| Endpoint | `http://127.0.0.1:8766/mcp` (doar loopback) · transport `streamable-http` |
| Port | `GA_PORT=8766`. **8765 e ocupat** pe această mașină de un proces host-native strain (serviciul `hc-backend`) |
| Credential | refresh token în volumul montat `/data` (`data/credentials.json`) — **nu intră niciodată într-un layer de imagine** |
| Secrete externe | `E:\--- System Secrets` montat **read-only** la `/secrets` |
| Probe | `node probe.mjs` → exit **0** = PASS, **1** = FAIL, **2** = UNKNOWN |
| Notificare re-auth | `watch-reauth.ps1` → ntfy `mavis-google-access` + `REAUTH-NOTICE.md` |

## Reconstrucție

```powershell
docker build -t google-access:1.0.2 .
docker run -d --name Google_Access --restart unless-stopped `
  -p 127.0.0.1:8766:8766 -e GA_PORT=8766 `
  -v "C:\Users\apviz\.minimax\google-access\data:/data" `
  -v "E:\--- System Secrets:/secrets:ro" google-access:1.0.2
node probe.mjs
```

## Ce NU e aici — și de ce

`data/`, `logs/` și `state/` sunt **excluse prin `.gitignore`**. `data/` conține
refresh token-ul. Nu se comite nimic care poate autentifica.

## Trei defecte măsurate, reparate la sursă (2026-10-27)

Toate trei erau **porturi scrise ca literal** — adică o a doua sursă de adevăr
despre același lucru.

1. **Healthcheck-ul mințea.** `HEALTHCHECK` proba `127.0.0.1:8765`, dar
   containerul rula cu `GA_PORT=8766`. Rezultat: `unhealthy` la 9 intervale
   consecutive, în timp ce serviciul răspundea HTTP 200 cu `grant=live`.
   Reparare: proba își derivează portul din `process.env.GA_PORT`.
2. **Proba măsura alt serviciu.** `probe.mjs` avea implicit
   `http://127.0.0.1:8765/mcp` — un proces **strain** (python, serviciul
   `hc-backend`). Proba tipărea `HANDSHAKE=FAILED`, `TOOLS=0` și **ieșea cu
   cod 0**. O poartă care nu poate eșua nu e o poartă.
   Reparare: implicitul e 8766, plus verificare de identitate
   (`SERVICE_MISMATCH` → UNKNOWN) și coduri de ieșire proprii (0/1/2).
3. **Fallback-ul serverului** era tot 8765. Reparat la 8766, ca în imagine.

Proba a fost falsificată în ambele sensuri: pe portul strain → exit 2
(`SERVICE_MISMATCH`), pe port inaccesibil → exit 2 (`HEALTH=UNREACHABLE`),
pe portul corect → exit 0 (`VERDICT=PASS`).

## Scope-uri

Grantul viu acoperă: Drive, Gmail, Docs, Sheets, Calendar, Presentations,
Forms. Pentru Photos, Keep, Tasks, Books, Sites, Script, Chat, YouTube —
scope-urile sunt în afara grantului, iar uneltele raportează `MISSING_SCOPE`
explicit. Extinderea cere un singur click: `google_scope_upgrade` →
consimțământ → `provision-grant.cjs --from-code <code> --client secrets`.

---

*Copie de reconstrucție · sursa vie e `C:\Users\apviz\.minimax\google-access\`*

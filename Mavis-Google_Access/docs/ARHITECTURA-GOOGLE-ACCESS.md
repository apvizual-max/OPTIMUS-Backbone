# ARHITECTURA - Google_Access

## Forma

```
                      ┌──────────────────────────────────────────────┐
  Mavis Local ────────►│  container Google_Access (Docker)            │
  (orice AI, orice     │  server.mjs - un singur server MCP           │
   tool de pe stație)  │  http://127.0.0.1:8766/mcp                 │
                      │  http://127.0.0.1:8766/health                │
                      └───────┬──────────────────────────────┬───────┘
                              │ volum rw                   │ volum ro
                    /data (credential)              /secrets (E:\--- System Secrets)
                              │                              │
                    ┌─────────▼──────────┐        ┌──────────▼─────────┐
                    │ credentials.json   │        │ client_secret.json │
                    │ refresh_token      │        │ (clientul Mavis_Cloud)│
                    │ extendlm.json      │        └────────────────────┘
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Google APIs        │
                    │  (16+ servicii)     │
                    └────────────────────┘
```

**Un server. Un container. Un credential.** Nu există un al doilea server
MCP pentru același cont, și nu există credential duplicat pe disc.

## Părțile

| Fișier | Rol |
|---|---|
| `container/server.mjs` | serverul MCP: unelte, tabel scope-uri, tabel gazde API, tokenizare |
| `container/provision-grant.cjs` | schimbă codul de consimțământ → refresh token → `data/credentials.json` |
| `container/consent-watcher.mjs` | ascultă redirect-ul, apelează provisionerul, repornește containerul, rulează proba |
| `container/mcp-call.mjs` | apelant MCP reutilizabil (o unealtă per invocare) |
| `container/probe-services.mjs` | proba pe fiecare serviciu, cu verdict pe răspuns |
| `container/probe.mjs` | proba de identitate a serviciului (coduri 0/1/2) |
| `container/extendlm-provision.mjs` | dynamic client registration + PKCE + token ExtendLM |
| `container/watch-reauth.ps1` | watchdog: detectează `reauth_required` și notifică (ntfy) |
| `container/Dockerfile` | imaginea; `data/` e exclusă prin `.dockerignore` |

## Decizii de proiectare (și ce le-a măsurat)

**1. Server MCP stateless.** Clientul de probe a presupus inițial că serverul
trimite `mcp-session-id`; nu trimite. Corectat în probe, nu în server -
serverul funcționa.

**2. Tabelul de gazde API (`API_BASE`), nu un prefix unic.** Măsurat: cu un
prefix `https://www.googleapis.com` unic, **8 din 14 servicii** răspundeau
404. Fiecare API are gazda lui. Tabelul e singura sursă de adevăr; în cod nu
mai există niciun drum relativ într-un `gfetch()`.

**3. Scope-urile se cer împreună, sau deloc.** Google respinge o cerere de
consimțământ **în întregime** dacă un scope nu e valid. Deci lista de scope-uri
e verificată înainte de a fi folosită, iar două scope-uri moarte
(`sites`, `keep`) au fost scoase cu dovezi, nu cu presupuneri.

**4. Fiecare refuz e măsurat și afișat.** Uneltele pentru Keep/Sites raportează
refuzul real al API-ului, cu codul lui. Nu tac, nu mint.

**5. Consimțământul e fizic, restul e automat.** Singurul lucru pe care nu îl
fac automat este clickul de autorizare (politica runtime + e corect etic).
Codul, schimbul, publicarea, restartul, proba și notificarea sunt automate.

**6. Secretul nu intră în imagine.** `.dockerignore` exclude `data/`;
`credentials.json` trăiește în volum montat. Containerul poate fi recreat
fără să piardă grantul.

**7. Reparare într-un minut, nu o procedură.** `google_scope_upgrade` tipărește
un singur URL; ascultătorul face restul.

## Namespaces (regula din memorie)

`minimax` și `Hermes` sunt universuri separate. Tot ce e în `container/` e
**minimax**: serverul MCP propriu, portul 8766, volumul propriu, profilul
`google-layer/minimax-notebooklm.js` cu portul 9412. Nimic din acest stack nu
atinge configurația, containerele sau secretele lui Hermes. Dacă e nevoie de
aceeași capabilitate în Hermes, se construiește o **instanță separată** -
copia nu poate distruge originalul, originalul poate distruge copia.

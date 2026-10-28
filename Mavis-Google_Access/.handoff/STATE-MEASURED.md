# STATE MEASURED — Google Access

**Măsurat:** 2026-10-28, între 00:03Z și 01:54Z (UTC+2).
**Cifrele au o dată.** Ele se re-verifică cu comanda din dreapta; dacă o
cifră nu mai corespunde, cifra e cea greșită, nu realitatea.

---

## 1. Punctul de control

```
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\ga-doctor.mjs"
```

```
=== Google Access - control point ===
host=OPTIMUS_PRIME at=2026-10-28T01:54:00.065Z
container=Google_Access mcp=http://127.0.0.1:8766/mcp data=C:/Users/apviz/.minimax/google-access/data

CHECK C1.container OK   status=running health=healthy image=google-access:1.0.10 restart=unless-stopped
CHECK C1b.running-code OK   repo=63e4ea8d2bbb running=63e4ea8d2bbb match=true
CHECK C2.health OK   grant=live reauth=false tools=32
CHECK C3.services OK   state=HEALTHY OK=14 REFUSED=2[keep,sites] ERROR=0[] attempts=1
CHECK C4.extendlm OK   token_minutes_left=109 refresh_token=yes cloud_secret_age_min=11
CHECK C5.browser-mcp OK   server=minimax-notebooklm tools=4 path=C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\google-layer\minimax-notebooklm.js
CHECK C6.mcp-registry OK   enabled=true url=http://127.0.0.1:8766/mcp type=streamable-http
CHECK C10.mcp-paths OK   checked=23 dead_total=0
CHECK C7.tasks OK   count=4
CHECK C8.consent OK   listener alive (processes=1)
CHECK C9.picker OK   session consumed (2026-10-27T23:48:10.291Z) - nothing to watch

SUMMARY checks=11 failed=0 warnings=0
VERDICT=PASS
```

Exit **0**. Verificări falsificate: `--self-test --fail C1.container` →
`VERDICT=FAIL` exit 2; `--self-test --fail C10.mcp-paths` → `VERDICT=FAIL`
exit 2.

Auto-verificarea instrumentului (offline, fără apeluri live):
`node scripts\ga-doctor.mjs --self-test` → `SELFTEST probes=3 falsified=2
blocked=1 expectations_met=3/3`, `VERDICT=PASS`, exit 0.

---

## 2. Containerul

| | Valoare | Comanda |
|---|---|---|
| Nume / imagine | `Google_Access` / `google-access:1.0.10` | `docker ps` |
| Stare | `Up 13 minutes (healthy)`, `127.0.0.1:8766->8766/tcp` — măsurat la 04:03 local, la 13 min după recrearea din build-ul 1.0.10 | `docker ps` |
| Restart | `unless-stopped` | `docker inspect` |
| Volum rw | `C:\Users\apviz\.minimax\google-access\data` → `/data` | `docker inspect` |
| Volum ro | `E:\--- System Secrets` → `/secrets` | `docker inspect` |
| Secret în imagine | **niciunul** | verificatorul Docker, `V4` |
| Octeți rulați | `server.mjs` sha256 `63e4ea8d2bbb…` | `docker exec … node -p` |
| Octeți în repo | `server.mjs` sha256 `63e4ea8d2bbb…` | `Get-FileHash` |

Cele două hash-uri sunt **egale** — containerul rulează codul din repo.

---

## 3. Grantul și serviciile

| | Valoare |
|---|---|
| Cont | `apvizual@gmail.com` |
| Client OAuth | `1068987308935-5b7h17gt1c5hc4i1m6eginads37o3m2h.apps.googleusercontent.com` |
| Scope-uri | **33** |
| Unelte MCP | **32** |
| Probe live | **OK=14 · REFUSED=2[keep,sites] · ERROR=0** (C3, la 01:54Z) |

Refuzurile, cu răspunsul măsurat:

| Serviciu | Răspuns | Motiv |
|---|---|---|
| `keep` | `GOOGLE_HTTP_403` — `PERMISSION_DENIED`, `ACCESS_TOKEN_SCOPE_INSUFFICIENT` | Google nu publică scope acordabil pentru Keep |
| `sites` | `GOOGLE_HTTP_404` | API-ul Google Sites a fost retras |

**`books` refuză TRANZITORIU — măsurat, nu presupus.** Proba live fără
re-probare a răspuns `GOOGLE_HTTP_503` la **01:59:41Z**, la **02:01:48Z** și la
**02:05:26Z**, și `OK` la **02:02:49Z** — 3 din 5 probe-uri brute rulate în
această sesiune. Nu e refuz permanent: `C3.services` re-probează până la **4
încercări**, iar un refuz tranzitoriu care nu se recuperează rămâne
`state=DEGRADED_TRANSIENT` → `CHECK C3.services WARN` → exit **0**, cu cauza
afișată per serviciu. Comanda: `node container\probe-services.mjs`.

---

## 4. Taskurile programate

Măsurat la 2026-10-28 04:05 (local, 02:05Z). „Următorul" se recalculează la
fiecare cadență; „ultimul rezultat" e cel măsurat.

| Task | Cadență | Ultimul rezultat | Ultima rulare | Următorul (la măsurare) |
|---|---|---|---|---|
| `Google_Access_Watch` | oră | **0** | 03:47 | 04:47 |
| `Google_Access_Consent` | 5 min | **0** | 04:02 | 04:07 |
| `Google_Access_Doctor` | 30 min | **0** | 04:03 | 04:33 |
| `MavisExtendLMHeartbeat` | 30 min | **0** | 03:43 | 04:13 |
| `MavisPickerHeartbeat` | 15 min | **0** | 04:03 | 04:18 |

Toate cinci: `lastResult=0`, stare `Ready`.

---

## 5. Extensia MCP și registry-ul

| | Valoare |
|---|---|
| Server înregistrat | `Google_Access`, `type=streamable-http`, `enabled=true` |
| Endpoint | `http://127.0.0.1:8766/mcp` |
| Health | `http://127.0.0.1:8766/health` → `grant=live`, `reauth_required=false`, `tools=32` |
| Serveri în registry | **22** |
| Căi verificate | **23**, moarte **0** |
| `minimax-notebooklm` | handshake real: `server=minimax-notebooklm`, **4 unelte** |
| `gdrive-mcp` | handshake real: **9 unelte** |
| `gmail-mcp` | handshake real: **36 unelte** |
| `docker-mcp` | handshake real: `server=docker-agent`, **19 unelte** |

---

## 6. NotebookLM

| | Valoare |
|---|---|
| Token ExtendLM | viu, **109 minute** rămase la ultima măsurătoare |
| Refresh token | prezent, lungime **87** |
| Secret Cloud | `GOOGLE_EXTENDLM_CREDENTIAL_B64`, vârstă **11 minute** |
| Notebookuri | JULES 182 surse · GEMINI & AI Studio 251 · CV-Automation 98 · SENTINEL Role 225 · AGENTS 8 · TRADE 1 · CV-Notebook 99 · CLIENTS 2 · OPTIMUS System 5 |
| Browser | profil propriu `%LOCALAPPDATA%\minimax-notebooklm\chrome_profile`, CDP **9412** |

---

## 7. Poze

| | Valoare |
|---|---|
| Fișiere capturate | **6**, toate JPEG reale (magic bytes `ff d8 ff`) |
| Locație | `Mavis-Google_Access\state\picked\2026-10-27\` |
| Sesiune | `f4587e83-c9c0-4779-8584-01f7c94d7b6d` — expiră 2026-11-03; marcată `consumed` |
| Captură automată | task `MavisPickerHeartbeat`, la 15 minute |

---

## 8. Repository

| Repo | HEAD | origin/main | Divergență | Arbore |
|---|---|---|---|---|
| `Mavis-Google_Access` | `87f963b` | `87f963b` | 0 / 0 | curat la ultimul commit (87f963b); modificările de documentație erau necomitate la măsurare |
| `OPTIMUS-Backbone` | `267ef3c` | `267ef3c` | 0 / 0 | curat (3 foldere de scratch ale altui agent, neatinse) |

Folderul `.handoff\` este **versionat pe `main`** (introdus în `3c97e18`, cifrele
corectate în commitul imediat următor) și împins pe GitHub: predarea se face
prin `git pull`, nu prin copierea unui folder local. Verificat cu
`git ls-remote origin refs/heads/main` → `87f963b…` la momentul măsurătorii,
divergență 0/0.

Scanări: secrete pe diff indexat `SCANNED=883 BLOCKS=0 WARNS=0` · secrete pe
**tot repo-ul** (index, măsurat la 02:09Z) `SCANNED=105 BLOCKS=4 WARNS=0` — cele
4 blocaje erau **pre-existente și deja publicate**, în documente Cloud-side
(`Mavis-Cloud - GOOGLE_Setup_Session/`) care conțin cheile-exemplu oficiale
(`AKIA-EXEMPLU-AWS`, `xoxb EXEMPLU`); **nu** erau în niciun
fișier modificat de această actualizare — scanate individual, toate cele 8
fișiere modificate dau `BLOCKS=0 WARNS=0` · encoding `FILES_CHECKED=105
PROBLEMS=0`, zero BOM.

**Corecție, 02:12Z:** cele 4 blocaje pre-existente au fost **mascate** în sursă
(`AKIA-EXEMPLU-AWS`, `xoxb EXEMPLU`), deci poarta de secrete pe tot repo-ul a
devenit **utilizabilă** în loc să fie permanent roșie pe material vechi. Iar
aceeași regulă s-a aplicat și acestui document: un raport care **citește**
cheia-exemplu cu litere devine el însuși un blocaj — de aceea exemplele se
numează, nu se transcriu.

---

## 9. Botul central și membrii

| | Valoare |
|---|---|
| Bot | `skills\mavis-google-access-bot\` |
| Membri | **9** (6 funcționali + 2 meta + registrul) |
| Referințe | **27** |
| Registrul | `bot-registry.mjs verify` → `VERDICT=PASS` (36 skills checked) |
| Verificatoare ale membrilor | **8**, toate `VERDICT=PASS` |

---

## 10. Busola

Actualizată **pe loc** (nu rescrisă): 811 → 879 rânduri adăugate, conținutul
anterior intact, zero caractere stricate (`U+FFFD`). Instrumentul care o face:
`scripts/append-busola.py`, care refuză să trunchieze și raportează numărul de
rânduri înainte și după.

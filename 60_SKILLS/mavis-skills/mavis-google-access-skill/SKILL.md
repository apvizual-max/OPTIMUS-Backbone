# MAVIS — GOOGLE ACCESS (acces Google permanent, un server, un container)

**Tip:** micro-skill în cadrul suitei `mavis-optimus-continuous-integration-skill`
**Scop:** cum ajunge orice AI de pe această mașină la **tot** ce ține de Google,
fără re-autentificare la fiecare sesiune.
**Stare:** ✅ WIRED — containerul `Google_Access` rulează, grantul e **viu**,
iar accesul a fost dovedit cu **apeluri reale**, nu cu healthcheck.
Grantul a fost **lățit la 28 de scope-uri** pe 2026-10-27, 10:35 (un singur
click de consimțământ al lui Popy); proba a dat `VERDICT=PASS`. Azi grantul
e lățit la **32** de scope-uri, iar containerul a ajuns la `1.0.9` — sesiunea
sursă continuă să lucreze, deci **cifrele din §2 sunt volatile**: remeasurează
(cf. §2, „Cum se remeasurează").

## 1. De ce există (defectul real, nu preferința)

Popy: *„DE CE PULA MEA NU AI DEJA ACCES si de ce nu ma pot baza si folosi
setarile cand le fac odata! ... nu pot lucra ca tu IAR NU AI ACCES"*.

Măsurat: pe această mașină au existat **două** granturi Google. Cel citit de
serverul Drive era **mort** (`invalid_grant`), cel al serverului Workspace era
**viu**. Aceleași cont, același client OAuth. Simptomul era totuși „sign in
again" — pentru că fiecare server Google își ținea **propriul** magazin de
credentiale, și un grant mort într-un magazin arăta identic cu un grant
mort în toate.

Deci accesul devine un **mecanism**, nu o promisiune: se găsește fiecare
refresh token de pe mașină, se **măsoară** fiecare, iar primul viu e
publicat în toate magazinele. Consimțământul e nevoie doar când **niciun**
grant viu nu există — o situație diferită și rară.

**Containerul `Google_Access` duce principiul la capăt:** un singur
credential, un singur server MCP, un singur volum.

## 2. Ce e, măsurat

| Ce | Valoare măsurată | Cum |
|---|---|---|
| Container | `Google_Access`, imagine `google-access:1.0.9` (măsurat 13:28) | `docker ps` |
| Endpoint | `http://127.0.0.1:8766/mcp` (doar loopback) | `mcp get Google_Access` |
| Unelte | **32** | `/health` + handshake MCP + `tools/list` |
| Grant | **LIVE**, `client_id 1068987308935-5b7h17gt1c5hc4…` | `google_auth_status` |
| Scope granted | **32** — drive · gmail (full) · calendar · documents · forms · presentations · spreadsheets · photoslibrary · tasks · books · script · chat · youtube · contacts | `consent-result.json` → `scope_count` |
| Sursă vie ≡ container ≡ repo | `server.mjs` sha256 `8429fa51…` — **identic în toate trei** | `tools\google-access\sync-source.py` |
| Probe reale | Drive: 5 fișiere reale · Gmail: 3 mesaje reale · Books: **403 explicit**, nu eșec tăcut | `probe.mjs` |
| Secret în imagine | **niciunul** — credentialul trăiește în volumul montat `/data` | `docker inspect` + `.dockerignore` |
| Notificare re-consent | `Google_Access_Watch` (task orar) → ntfy `mavis-google-access` + `REAUTH-NOTICE.md` | falsificat: exit **3** + mesaj livrat |

**Cum se remeasurează (cifrele din tabel sunt volatile).** Măsurat 2026-10-27:
**8 build-uri de imagine într-o zi** (`1.0.2` 07:57 → `1.0.9` 13:26) — sesiunea
sursă continuă să lucreze. Nu citi tabelul ca adevăr permanent:

```powershell
python "<CI>\tools\google-access\sync-source.py"
# -> PROBLEMS=0 COPIED=10 ; MATCH=true (sursa vie ≡ container ≡ repo)
docker exec Google_Access node -e "fetch('http://127.0.0.1:8766/health').then(r=>r.json()).then(j=>console.log(j.tools,j.grant,j.reauth_required))"
docker exec Google_Access node -e "const j=require('/data/consent-result.json');console.log(j.scope_count||j.scopes.length)"
```

Ultima rulare (13:28): `PROBLEMS=0 COPIED=10`, `MATCH=true`, `LEAKED_PATHS=0`,
tools **32**, scopes **32**, grant **live**, `reauth_required=false`.

## 3. Cum se folosește

```powershell
# starea credentialului (PRIMUL apel dacă ceva Google eșuează)
Invoke-RestMethod http://127.0.0.1:8766/health

# unelte, prin clientul MCP
mcp get Google_Access
```

Din orice alt AI de pe mașină: endpointul e `http://127.0.0.1:8766/mcp`,
transport `streamable-http`. Hermes îl poate folosi la fel — dar **cu
instanța lui proprie**: nu se atingă containerele unii ale celorlalți
(regula namespace-ului).

## 4. Când e nevoie de un singur click (și numai atunci)

Scope-ul granted acoperă acum **32 de scope-uri**, inclusiv Photos, Tasks,
Books, Script, Chat, YouTube și Contacts. **Doar două rămân inaccesibile**, și
nu pentru că nu au fost cerute:

- `https://www.googleapis.com/auth/sites` — API-ul Google Sites **nu mai
  există**; a rămas doar `siteverification`.
- `https://www.googleapis.com/auth/keep` — Google nu publică niciun scope
  acordabil pentru Keep.

Măsurat 2026-10-27: aceste două scope-uri **invalidau întreaga cerere** de
consimțământ (`invalid_scope`), deci celelalte 28 de atunci, deși erau valide, nu
treceau. Au fost scoase din `FULL_SCOPES`, iar motivul e scris în sursă, la
liniile 24 și 27. Uneltele `gkeep_list` și `gsites_list` **există în continuare**
în server: n-au scope, deci raportează `MISSING_SCOPE` — nu tac.

Uneltele ale căror scope lipsește **nu tac**: raportează `MISSING_SCOPE` cu
scope-ul cerut și trimit la `google_scope_upgrade`.

Procedura, o singură dată:

```powershell
# 1. URL-ul de consimțământ (cu clientul al cărui secret e în E:\--- System Secrets)
#    -> unealta google_scope_upgrade cu argumentul client="secrets"
# 2. Popy deschide URL-ul în browserul deja logat -> Allow -> copiază codul
# 3. pe host:
node C:\Users\apviz\.minimax\google-access\provision-grant.cjs --from-code <code> --client secrets
# 4. containerul reia automat: credentialul nou e în volum, tokenurile se mintesc singure
```

**După acel click, nu se mai cere nimic.** Refresh tokenul trăiește în volum
și e reînnoit automat; consimțământul nu se repetă.

## 5. Cele patru interdicții

1. **Nu citi și nu tipări credentialul** din `data/credentials.json`. Se
   citește lungimea și starea, nu valoarea.
2. **Nu pune secretele în layer-ul imaginii.** Ele intră doar prin volum
   montat (`/data`) sau prin montaj read-only (`/secrets`).
3. **Nu folosi `docker container prune -a`** — a pierdut swarm-ul pe
   2026-08-08. Containerul `Google_Access` e unul nou, cu `--restart
   unless-stopped`.
4. **Nu confunda un `403` de scope cu un eșec de autentificare.** `403
   insufficientPermissions` = scope; `invalid_grant` = credential.

## 6. Ce NU e acoperit de API (și de ce)

- **NotebookLM**: merge prin `notebooklm_ask` (proxy ExtendLM) — dar ExtendLM
  are nevoie de extensia din browser conectată și de un token de client. Până
  când Popy creează client ID-ul în pagina ExtendLM, calea vie e
  `minimax-notebooklm` (profil Chrome propriu, port 9412, sesiune deja
  autentificată).
- **WebMCP** (`webmcp.dev`): are nevoie de browserul cu sesiunea Google
  deschisă. API-ul e mai puternic decât interfața, dar pentru aplicațiile care
  n-au API (Stadia, Creative Labs, Pics) calea rămâne browserul din gazdă
  (`chrome-devtools-mcp`, `agent-browser-mcp`).
- **Google Cloud**: exclus prin cerință.

## 7. Fișiere

| Cale | Ce e |
|---|---|
| `C:\Users\apviz\.minimax\google-access\server.mjs` | serverul MCP (fără dependențe) |
| `C:\Users\apviz\.minimax\google-access\Dockerfile` | imaginea |
| `C:\Users\apviz\.minimax\google-access\provision-grant.cjs` | găsește grantul viu și îl publică în volum |
| `C:\Users\apviz\.minimax\google-access\watch-reauth.ps1` | automatismul de notificare |
| `C:\Users\apviz\.minimax\google-access\probe.mjs` | proba cu apel real |
| `C:\Users\apviz\.minimax\google-access\consent-watcher.mjs` | așteaptă codul de consimțământ, apoi îl publică |
| `C:\Users\apviz\.minimax\google-access\data\credentials.json` | **singurul** secret — în volum, nu în imagine |
| `C:\Users\apviz\.minimax\google-access\logs\watch-reauth.log` | jurnalul automatismului |

**Oglinda în repo.** `Optimus_CI (by Mavis)\tools\google-access\` e copia
**reconstruibilă** din GitHub: sursa care rulează pe mașină, fără secret.
Ea se resincronizează cu **un instrument**, nu cu o copie manuală:

```powershell
python "<CI>\tools\google-access\sync-source.py"
```

Instrumentul copiază o listă albă, verifică SHA256 după copiere, scanează
destinația de secrete **și** compară `server.mjs` cu cel din containerul care
rulează. Ultima comparație e cea care contează: o sursă editată după
build-ul imaginii înseamnă că repo-ul nu mai descrie sistemul care rulează.
Măsurat 2026-10-27 13:28: sursa vie, containerul și copia din repo erau
**identice** (`sha256=8429fa51…`, `MATCH=true`), deci repo-ul e reproductibil.
Reverifică cu instrumentul — sursa se schimbă des.

---

*Măsurat 2026-10-27 · Mavis Local · namespace minimax · fără trunchiere*

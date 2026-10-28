# Intenții — de la POPY, prin agentul local, către cloud

Canalul prin care cerințele ajung de la om la Mavis, fără să fie nevoie de
sesiune deschisă.

## Cum se folosește

1. POPY scrie ce vrea aici
2. Agentul local face `git pull`, citește, face ce poate local
3. Agentul local notează ce a făcut aici
4. Mavis face `git pull` la următoarea sesiune și continuă

## Înregistrări

### [2026-10-10] Livrare, agenți și registru

**POPY a cerut:**
- corectarea numelui „Smite" — făcută, era corect din start
- rezolvarea etichetelor Gmail goale — **diagnoză găsită: fereastra 1–3 ani
  pe care am pus tot sistemul excludea newsletter-urile AI, care vin zilnic**
- un Sentinel — raport de stare complet, cu dată, permanent
- un registru al tot ce vine de pe GitHub/GitLab
- o punte între cloud și agentul local
- flux CI cu pull request, ca Live Review să aibă ce verifica

**Mavis a răspuns:**
- toate mai sus, în repo
- 3 skill-uri noi: `sentinel-report`, `registru-extern`, `puntea-agenti`
- eticheta `MAVIS/AI si comunitati`: **0 → 2.000+**
- flux CI: ramură + PR + merge, scris în `AGENTS.md`

**Rămâne de făcut de POPY:**
- activează GitHub Copilot și Jules din interfața web (contul e pe plan free,
  API-ul răspunde `Not Found`)
- trimite linkul la „Mavis Apple Design", dacă e alt repo decât `emilkowalski/skills`
- email și telefon pentru site — sunt încă `[EMAIL]` și `[TELEFON]`

---

*Adaugă aici, în ordine, cu dată. Nu șterge intrările vechi.*
---

### [2026-10-12] NotebookLM — acces și sinteză

**POPY a cerut:**
- să intri în notebook-urile lui și să fac sinteză de lucruri
- prin remote, folosind Mavis

**Ce e nevoie:**
Localul are deja Hermes, cookie-urile și browserul. Intră în notebook-uri,
face sinteza cerută, o scrie în repo.

**Mavis Cloud nu face asta și nu încearcă.** Nu are browser, nu are sesiune.
Nu instalez nimic, nu ating configurația lui Hermes, nu schimb nimic.

**Un singur lucru de la POPY:** spune ce sinteză vrei, într-un rând.

### [2026-10-22] Google — consimțământ OAuth, fără secrete prin chat

**POPY a cerut:**
- ca tot ce ține de Google să fie sincronizat în repo, fără să-i cer permisiune
- să nu mai treacă prin chat niciun secret, pentru că platforma îl maschează

**Ce e nevoie:**
Clientul OAuth Desktop e corect și verificat din cloud. Lipsește **un singur
consimțământ** în browser — de aici lipsește `GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD`.

**Cum se rezolvă, fără secrete prin chat:**
1. Linkul de autorizare e generat în repo: `18-GOOGLE/AUTORIZARE-LINK.txt`
   (script: `mavis-tools/google-link-file.js`). POPY îl deschide din browser.
2. POPY copiază bara de adresa cu `?code=...` și o trimite la Mavis Cloud.
3. Mavis Cloud face schimbul: `node mavis-tools/google-connect.js "<url>"`,
   scrie tokenul în secret manager, apoi verifică live:
   `node mavis-tools/google-verify.js`.

**Varianta Local**, dacă POPY vrea sa nu atinga browserul manual:
`node mavis-tools/google-local.js` — flux complet pe calculatorul lui, cu
`~/.google-mcp/credentials.json`. POPY pune refresh tokenul în secret manager
direct, nu prin chat.

**Apoi:** Testing → In production, ca tokenul să nu moară în 7 zile.
Checklist: `docs/GOOGLE-PRODUCTION-CHECKLIST.md`.

**Mavis Cloud nu pune secrete în repo și nu cere POPY să le trimită în chat.**

### [2026-10-22] Repo-ul a devenit PUBLIC

**POPY a cerut:**
- ca MAVIS-CLOUD să fie public, altfel aplicațiile conectate nu-l pot analiza
- ca tot ce ține de proiect să fie sincronizat în repo, fără aprobări
- ca procedura livrării linkului să fie documentată, ca să nu o mai batem în cap

**Ce am făcut:**
- Audit înainte de publicare: **zero secrete** în tot istoricul git, **zero
  date personale ale terților** (doar contorizări și documentație). Verificat
  cu scanare de `GOCSPX`, `ghp_`, `1//…`, `AIza`, chei private, adrese email.
- Repo: `private: false` → **visibility: public**, confirmat cu acces anonim.
- Procedura scrisă în `docs/PROCEDURA-LIVRARE-SECRETE.md` + skill nou
  `.skills/mavis-secure-delivery/` + Regula 1 și Regula 2 în `AGENTS.md`.
- **Skills-ul din repo erau vechi** — le-am sincronizat din runtime. Localul ar
  fi continuat să lucreze cu proceduri greșite.

**Ce rămâne de făcut de POPY:** trimite codul de autorizare (din bara de adresa
a paginii `127.0.0.1:8976`). Restul îl face Mavis Cloud.

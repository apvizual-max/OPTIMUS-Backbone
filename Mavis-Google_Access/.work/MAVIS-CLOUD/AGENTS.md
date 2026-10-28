# Cum lucrez în acest repo

**Sunt Mavis Cloud.** Voi lucrez în cloud, pe main, cu commit și push automat.
Celălalt agent, **Mavis**, lucrează pe calculatorul lui POPY.

## REGULA GENERALĂ — nu se negociază

**Tot ce fac ajunge în repo. AUTOMAT. Fără aprobări, fără întrebări, fără limite.**

```bash
nohup ./mavis-tools/mavis-cloud-autosave.sh &    # pornește bucla
```

Scriptul: ia ce a scris Local → rulează R0 → comitează → împinge pe `main`.
**Dacă R0 pică, nu comitează și scrie în log.** Mă opresc singur înainte să stric.

Verificarea înainte de orice raport:
> „e gata" înseamnă „POPY poate să vadă", nu „există în repo".

## Regula 0 — nu se negociază

**Un singur deployment:**
```
https://da15e9yb994ps.space.minimax.io
```
**Niciodată altul**, fără cerere explicită de la POPY. Fiecare deploy creează
un site nou în panoul lui. Am făcut asta de trei ori și l-am stricat.

**Ramuri: nu.** Se lucrează pe `main`. Ramură se face **doar** când POPY o cere.

**Version control este git**, nu deployment-uri. Deployment-ul e doar un website.

## Regula 1 — nu se negociază: valorile din secret manager NU trec prin chat

Platforma **maschează** valorile din secret manager în mesajele mele:
`{{ARCHON_SECRET:NUME}}`. Ce ajunge la POPY e un placeholder, nu valoarea.

**2026-10-22:** un link de autorizare OAuth trimis în chat a ajuns în browser
cu `client_id=%7B%7BARCHON_SECRET%3A...%7D%7D` → *Error 401: invalid_client*.
Trei runde de diagnostic până am citit bara de adresa a browserului.

```bash
# TEST: valoarea e mascat sau reala?
node -e 'console.log(process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD)'   # real -> complet
# aceeasi valoare in chat                                        # -> {{ARCHON_SECRET:...}}
```

**Dacă bash-ul arată valoarea și chatul arată placeholder → problema e
livrarea, nu credentialul.** Nu cere lui POPY să schimbe chei.

### Cum se livrează corect

1. **Identificatorii publici** (`client_id`, project number) → în repo, ca sursă
   unică: `mavis-tools/google-client.json`.
2. **Scriptul generează artefactul în repo**, nu în chat:
   `node mavis-tools/google-link-file.js` → `18-GOOGLE/AUTORIZARE-LINK.txt`.
3. **Comit + push. Fără aprobare.**
4. **Livreză URL de repo** (nu conține secret, nu se maschează):
   `https://github.com/apvizual-max/MAVIS-CLOUD/blob/main/18-GOOGLE/AUTORIZARE-LINK.txt`
5. **Codul de autorizare** poate veni prin chat. **Secretele nu** — vin prin
   panoul de secrete sau prin tool-ul `secret`.

Procedura lungă: `docs/PROCEDURA-LIVRARE-SECRETE.md` ·
Skill: `.skills/mavis-secure-delivery/`


## Regula 2 — nu se negociază: comit și push fără aprobare

POPY a cerut explicit: *„niciodată să ceri permisiune pentru comit și push,
orice lucru am face"*. **Un livrabil care stă doar în conversație e un
livrabil pierdut.** Fiecare document, cod, status și plan intră în repo, în
folderul potrivit, și se împinge pe `main`.

Repo-ul este **public** (2026-10-22) — ca aplicațiile conectate să-l poată
analiza. Audit făcut înainte: **zero secrete** în istoric, **zero date
personale ale terților**, doar contorizări și documentație.

## Regula 3 — nu se negociază: regulile vaultului, când atingi Drive

Din 2026-10-22 am acces la vaultul live din Drive (`GDrive-Second_Brain_PKMS`,
51.157 de fișiere). **Regulile lui, întregi, în `19-GDRIVE/REGULI-VAULT.md`.**

Scurt: **nu se șterge nimic. Nu se mută fără R0 și fără decizia lui POPY.**
`00_INDEX.md` nu se editează manual (se regenerează). Nu se scriu căi de reper
în mână — se descoperă. Nu se atinge ramura Knights Templar, `_SYSTEM`,
`.obsidian`, `.trash`, `.vault-intelligence`, `.claudian`, `.neural_memory`.

**Unelta:** `mavis-tools/drive-vault.js` — read-only, cu o singură excepție:
`quarantine` mută (nu șterge) și cere `--confirm` + motiv scris.

```bash
node mavis-tools/drive-vault.js root
node mavis-tools/drive-vault.js ls "01_Projects"
node mavis-tools/drive-vault.js read "COTOR.md"
node mavis-tools/drive-vault.js find "termen"
```

**Interdicție:** nu scanezi niciodată tot arborele ca să găsești un fișier.
Cotorul răspunde în sub o secundă — căutarea se face în `00_INDEX.md`.

## Fluxul la fiecare schimbare

```bash
cd /workspace/Mavis
git add -A
git commit -m "ce s-a făcut"     # fără întrebare
# R0: verifică înainte de push
node --check <js-uri>
python3 -c "import ast,io; ast.parse(io.open('<py>',encoding='utf-8').read())"
git diff --cached --name-only | grep -iE "secret|token|credential"   # trebuie gol
git push origin main              # fără întrebare
```

**Comit și împing mereu**, ca POPY să vadă în panoul Environmental Information
(`Changes` / `Commit or push` / `Git Graph`) că lucrez.

**Îl avertizez** dacă se adună mai mult de 5 commituri nepushate.

Ce decide singur

## Regula 4 — nu se negociază: arhivezi înainte să tai din memorie

**POPY, 2026-10-24:** optimizarea memoriei fără arhivarea a ce ai tăiat se
cheamă **EROARE**, nu optimizare. Cât timp versiunea precedentă e păstrată
în **repo, în secțiunea de arhivă**, atunci e optimizare. Altfel e trunchiere
de memorie și pierdere de context — și așa se pierd detalii care uneori contează.

**Fluxul, în ordine:**

```
SNAPSHOT → MANIFEST → COMMIT → PUSH → APOI tai din memorie → COMMIT → PUSH
```

**Push-ul arhivei se întâmplă ÎNAINTE de tăiere.** Dacă push-ul pică, nu tai
nimic. Un topic șters se arhivează **înainte** de `memory_topic_delete`.

```bash
node mavis-tools/memory-snapshot.js --from <dir> --label <etichetă>   # snapshot
node mavis-tools/memory-snapshot.js --verify <etichetă>               # R0: există?
```

Arhiva: `docs/arhiva/memorie/` · procedura: `docs/PROCEDURA-OPTIMIZARE-MEMORIE.md`
· snapshot săptămânal: task cloud, duminica 23:00 (doar arhivează, nu taie).

**Secretele se elimină din memorie ÎNAINTE de arhivare** — repo-ul e public,
arhiva nu poate conține chei.

## REGULI DE PLATFORMĂ — citește asta la fiecare pornire

Fișierul complet: `docs/REGULI-PLATFORMA.md`

1. **CRON → verific pe platforma ONLINE.** Cronurile Cloud și cronurile Local sunt în locuri diferite. Programat în cloud și căutat în interfața Local = concluzie greșită.
2. **NotebookLM → browser.** API-ul oficial există DOAR pe Enterprise (licențe plătite). Cloud pregătește documentele, Local creează notebook-ul și le încarcă.
3. **DEPLOY → Local.** Instrumentul cloud creează nod nou la fiecare rulare, nu actualizează.
4. **VARIABILE → verifică ce există, nu inventa.** `LINKEDIN_EMAIL` nu există; e `GOOGLE_EMAIL`.
5. **SECRETE → sertar.** O cheie, un scop. Nu în chat, nu în repo, nu prin Jules.
6. **Nu cere date pe care le verific deja.** Nu întreb cine are notebook-ul. Nu întreb ce se vede în Drive.
7. **VALORI DIN SECRET MANAGER → NU PRIN CHAT.** Platforma le maschează în `{{ARCHON_SECRET:...}}`. Livrare prin repo (fișier + URL). Vezi Regula 1.
8. **COMIT + PUSH, fără aprobare.** Repo-ul e public; un livrabil care stă doar în conversație e un livrabil pierdut.

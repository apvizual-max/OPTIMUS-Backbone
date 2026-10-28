# PROCEDURI Git ↔ GitHub — cum lucrăm, măsurat

> Regula de aur a proiectului CI. **Nu se schimbă fără R0.**
> Oglinda `DOCTRINA-CD.md` §5, dar cu mecanismul și măsurătorile.

---

## 1. Cele trei reguli, într-un tabel

| Acțiune | R0? | Cine |
|---|---|---|
| `git add` | nu | agentul |
| `git commit` pe `main` | **nu — automat, mereu, fără întrebare** | agentul |
| `git push` spre GitHub | **DA — singurul lucru care cere R0** | agentul, după R0-ul lui Popy |
| merge de pull request | **DA — merge = push = R0** | agentul, după R0-ul lui Popy |
| fork / ramură nouă | doar la cerere explicită, ca GOAL + CRITERIA | Popy cere |
| `reset --hard` · `clean -fdx` · force-push | **interzise, fără excepție** | — |
| ștergere definitivă | **interzisă**; Trash recuperabil numai | — |

**La 50 de commituri neîmpinse** apare alerta de prag la fiecare răspuns,
până dă R0.

**Instanța Cloud** e singura care împinge fără R0 — container volatil,
altfel pierde datele la oprire. **Nu aparține CD.**

---

## 2. De ce R0 se cere doar la push

Măsurat, nu auzit: un `core.hooksPath` **global** a făcut ca toate
repo-urile de pe mașină să moștenească un folder de hook-uri. `git commit`
a eșuat cu **exit 128 în ~70 din 76 repo-uri**, și **12 comituri au ajuns pe
GitHub fără acord** — pentru că poarta exista doar ca un **switch** într-un
script, iar un `git push` direct o ocolea.

> **O poartă care stă în prohă, sau într-un flag pe care eu îl pot pasa,
> nu e o poartă.** Mecanismul trebuie să mă oprească și când vreau să trec.

De aici cele trei lecții implementate:

1. **Poarta trăiește în hook**, nu într-un switch de script.
2. **Poarta e per-repo**, setată cu `core.hooksPath` **local**. **Niciodată
   global.** Măsurat 2026-10-24: globalul e gol.
3. **Un acord = o împingere.** Martorul se consumă.

---

## 3. Mecanismul, exact

### 3.1 Hookul

```
C:\Users\apviz\.minimax-agent\projects\scripts\git-hooks\pre-push
```

```sh
marker="$(git rev-parse --git-dir)/PUSH-ACORD"
if [ -f "$marker" ]; then
    rm -f "$marker"
    exit 0
fi
echo "  POARTA: acest repo nu se impinge fara acordul lui Popy."
exit 1
```

### 3.2 Scriptul unică de push

```
C:\Users\apviz\.minimax-agent\projects\scripts\git-autopush.ps1
```

`git-autopush.ps1:189` scrie martorul **chiar înainte** de apelul `git push`,
iar hookul îl consumă. Ordinea fixă:

```
1. masoara   HEAD local, server prin git ls-remote, comituri neimpinse
2. decide    sub prag? NU se atinge nimic. peste prag? cere acord
3. push      git push PUR. Fara LiveReview. Fara review. Fara poarta.
4. verifica  git ls-remote; SHA server == SHA HEAD
5. review    LiveReview, DOAR DUPA ce push-ul e confirmat pe GitHub
```

| Parametru | Implicit | Ce face |
|---|---|---|
| `-Remote` | `origin` | remote-ul |
| `-Branch` | `main` | ramura |
| `-Prag` | 25 | sub prag → nu se atinge nimic |
| `-Acord` | — | **declarația de acord: o singură împingere** |
| `-FaraReview` | — | calea 2: push fără Live Review |
| `-DryRun` | — | doar măsoară |

**Coduri de ieșire:** `0` = împins și verificat / nimic de urcat · `1` = push
nu a ajuns sau serverul nu corespunde · `2` = mediu invalid · `3` = sub
prag, nu s-a atins nimic.

### 3.3 Peretele

```
C:\Users\apviz\.minimax-agent\projects\scripts\push-status.ps1
```

Rapoartează câte comituri neîmpinse sunt, per repo. Ieșire `1` = există
comituri neîmpinse (peretele e aprins).

### 3.4 Instalarea, per repo

```powershell
git -C <repo> config core.hooksPath C:/Users/apviz/.minimax-agent/projects/scripts/git-hooks
```

**Măsurat 2026-10-24:** poarta era **neinstalată** în ambele repo-uri
(`core.hooksPath` absent, fișierul de hook absent). **Instalată acum** în
`MAVIS-OPTIMUS-CI` și `MAVIS-OPTIMUS-CD`. Globalul a rămas gol.

### 3.5 Proba falsificare — poarta, în ambele sensuri

O poartă care nu poate eșua nu e o poartă. S-a probat **în ambele sensuri**:

| Probe | Rezultat așteptat | Rezultat măsurat |
|---|---|---|
| Fără martor | ieșire **1** + mesajul „POARTA" | **1** + mesajul afișat ✓ |
| Cu martor | ieșire **0**, martor consumat | **0**, consumat ✓ |

Probe rulată cu `C:\Program Files\Git\bin\sh.exe` — `sh` **nu** e pe PATH
în PowerShell, dar hookul e executat de git prin shell-ul propriu.

---

## 4. Latura commit

**COMMIT = automat, pe `main`, fără R0.** Popy nu aprobă comituri. Nu
aprobă nimic tehnic.

**Poarta pre-commit** citește **index-ul**, nu arborele de lucru:

```
powershell -NoProfile -File scripts\scan-staged-secrets.ps1 -RepoPath <repo>

> **Reparat 2026-10-27.** Comanda de mai sus indica `jules-scan-staged.ps1`,
> care a plecat în CD odată cu platforma Jules — **în CI nu mai există**, iar
> procedura indica un fișier dispărut. CI are acum **scannerul propriu**:
> `scripts\scan-staged-secrets.ps1`, cu auto-proba
> `scripts\scan-staged-secrets-selfcheck.ps1`.
```

| Cod | Ce înseamnă |
|---|---|
| `0` | nimic blocat (`BLOCKS=0 WARNS=0 SCAN_OK`) |
| `1` | cel puțin un `BLOCK` |
| `2` | poarta nu a putut citi index-ul |

**Ce blochează scannerul din CI:** secrete — forme fixe (cheie privată, cheie
AWS, token GitHub, cheie Google API, cheie OpenAI, token Slack, token
Telegram, JWT) și atribuiri cu valoare (`api_key = "..."` și rude).
**Ce doar avertizează:** valori-c substituent (`your-key-here`, `changeme`,
`<TOKEN_AICI>`).

**Ce NU mai blochează aici:** emailuri necanonice, brandul interzis, căi de
date personale. Verificările astea aparțineau scannerului din platforma
Jules, care a plecat în CD, și vizează **build-ul de portofoliu din
`MAVIS-CLOUD`** (`SITE/`), nu repo-ul CI. Acolo ele rămân o **regulă de
revizuire**, nu o poartă automată: verificarea e făcută de platforma CD,
care deține scannerul.

**Regulă, nu excepție:** într-un lanț de porți, codul de ieșire al unei porți
trebuie să fie **propriu**, nu mostenit. O poartă fără `exit` are o valoare
moștenită, iar verdictul ei aparține porții precedente.

### 4.1 Topologia hook-urilor — măsurată 2026-10-27

| Repo | `core.hooksPath` (local) | Hook-uri |
|---|---|---|
| **CI** | `E:/Google/GitData-Optimus-CI/repo/hooks` | `pre-commit` (scanner) + `pre-push` (**delegat**) |
| **CD** | `C:/Users/apviz/.minimax-agent/projects/scripts/git-hooks` | `pre-push` (definiția comună) |

**De ce CI are director propriu, dar nu copiază poarta de push:** definiția
porții R0 rămâne **una singură**, partajată cu CD — două copii se pot
diverga. Hook-ul `pre-push` din CI **delegă** (`exec sh <poarta-comună>`), nu
copiază. Dacă poarta comună nu poate fi atinsă, push-ul e **refuzat**: o
poartă care pică deschis nu e poartă.

**Ce câștigă CI:** `pre-commit` — o poartă de secrete care rulează la **fiecare**
commit, fără să poată fi ocolită printr-un flag. O poartă în prohă sau
într-un switch pe care eu îl pot pasa nu e o poartă.

### 4.2 Falsificarea întregului lanț — măsurată 2026-10-27

Repo de probă izolat în `state/tmp/`, remote = repo bare local. **Nu s-a
atingut GitHub și nici repo-ul real.**

| Probă | Așteptat | Măsurat |
|---|---|---|
| commit curat | permis | **exit 0** ✓ |
| commit cu cheie plantată | **refuzat** | **exit 1**, `BLOCKS=1`, `aws-access-key-id` ✓ |
| secretul în istoric după refuz | absent | **absent** ✓ |
| push fără `PUSH-ACORD` | **refuzat** | **exit 1**, mesajul porții comune ✓ |
| push cu `PUSH-ACORD` | permis | **exit 0** ✓ |

Verdict: `GATE_PROBLEMS=0`, **EXIT 0**.

**Defect măsurat și reparat în acest proces:** scannerul arunca excepție
pe un fișier cu **linii goale** — un parametru `[string[]]` obligatoriu
respinge șirul vid. Excepția ieșea cu **1**, adică *acuză* un bloc care nu
exista: poarta bloca un fișier fără niciun secret. Reparat: `AllowEmptyString`
pe parametru, plus `try/catch` în jurul scanării, unde o excepție dă
**2 (eroare)**, niciodată **1 (bloc)**. O poartă care *acuză* trebuie să
dovedească imputabilitatea; o aruncare nu e o dovadă.

Proba de regresie: `proba-linii-goale` în `scan-staged-secrets-selfcheck.ps1`
— trebuie să dea `EXIT 0` cu `SCAN_OK`.

---

## 5. Verificarea unui push

**`git ls-remote`**, niciodată codul de ieșire:

```powershell
git -C <repo> ls-remote origin main
```

`git` scrie progresul pe **stderr** și poate arunca o eroare roșie chiar
când a mers bine. Un cod de ieșire citit greșit e un fals verdict.

**Criteriul:** SHA server **==** SHA HEAD local.

---

## 6. Live Review — după push, niciodată înainte

Cele 5 detalii sunt în `docs/CI-POLICY.md` (repo-ul CD) și în
`docs/POLITICA-LIVE-REVIEW-JULES.md` (folderul CD).

**Pe scurt:** `on: push` e interzis. Triggerul e `schedule: cron '0 3 * * *'`
sau `workflow_dispatch`. Rolul lui e să raporteze, nu să oprească.

### Starea reală a review-ului LiveReview — măsurat 2026-10-27

`lrc review` se execută **după** ce push-ul e confirmat. La rularea de pe
27 octombrie, 11:52, pe intervalul `d041fc4..efed54f`:

- **review-ul S-A TRIMIS** — `Review submitted, ID: 13388`,
  `https://livereview.hexmos.com/#/reviews/13388`
- dar **review-ul a eșuat la evaluare**, cu mesajul scris de lrc:
  *"the Free plan requires you to configure your own LLM API key (BYOK) for
  your organization."* — plan `free_30k`, `ai_mode: BYOK required on free plan`

Deci `lrc` **nu e limită de rată**: contul LiveReview al lui Popy nu are un
cheie LLM configurată. E o setare de cont, în afara repo-ului — și nu
înseamnă că nimic nu s-a trimis: trimiterea e dovedită de **ID-ul** din
ieșire, nu de codul de ieșire.

`git-autopush.ps1` tratează asta corect: raportează `review: limita` și
continuă pe **calea 2** (push fără review), pentru că **push-ul era deja
confirmat pe server**. Un review lipsă nu e o eroare și nu se prezintă ca una.

---

## 7. Ce nu se face niciodată

- `git clean -fdx` · `git reset --hard` · force-push · ștergere definitivă
- dezactivarea unui hook local ca să treacă un comit
- `core.hooksPath` **global**
- `git push` direct în loc de `git-autopush.ps1 -Acord`
- merge automat al unui PR fără R0

**Dacă o poartă blochează comiturile, defectul e poarta, nu comitul.**
Se repară poarta, nu se comentează comitul.

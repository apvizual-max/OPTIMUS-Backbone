# PROMPT DE PRIMARE — sesiune nouă, context zero, memorie zero

> **Cum se folosește:** copiază tot ce urmează (blocul `PROMPT DE PRIMARE`) în prima
> mesaj a sesiunii noi. Nu e nevoie de nimic din sesiunea veche: nu citi
> memory, nu cauți chat-uri, nu presupun că știi ceva. Tot ce trebuie e în
> acest folder și în repo.
>
> **Sesiune nouă = proiect nou.** Rulează în directorul
> `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard`.
> Acesta e *rădăcina git*. Nu mai există un folder de lucru deasupra lui.

---

## PROMPT DE PRIMARE

Sunt Popy. Începem un proiect nou, într-un context nou: **tu nu știi nimic
despre mine, despre sistemele mele sau despre ce am construit**. Tot ce trebuie
să știi e în acest repo. Citește, măsoară, apoi lucrează.

### 1. Cine ești și unde ești

- Proiectul: **OPTIMUS Backbone** — sistemul meu personal de control, monitorizare
  și integrare AI.
- Rădăcina unică (SOT): `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard`
- Este **rădăcina git**. Branch `main`. Remote: `https://github.com/apvizual-max/OPTIMUS-Backbone.git`
- În acest director lucrezi. Nu crea un folder nou, nu crea o a doua rădăcină
  git, nu clona în altă parte.

### 2. Ce ai de citit, în ordine

| # | Fișier | Ce îți spune |
|---|---|---|
| 1 | `handoff/00_README.md` | ce e acest folder și cum se folosește |
| 2 | `handoff/01_PRIMING_PROMPT.md` | acest document |
| 3 | `handoff/02_STRUCTURA_SOT.md` | harta arborelui, modelul oglindă, junction-urile |
| 4 | `handoff/03_ISTORIC_MIGRARE.md` | ce s-a întâmplat, cu măsurători, nu cu povești |
| 5 | `handoff/04_SISTEME_SERVICII.md` | sistemele, daemonii, porturile, lanțul de supraveghere |
| 6 | `handoff/05_GIT_GITHUB.md` | starea git, poarta de push, regulile de commit/push |
| 7 | `handoff/06_LICENSIUNI.md` | lecțiile care trebuie să rămână |
| 8 | `handoff/07_DECIZII_DESCHISE.md` | deciziile care îmi aparțin, nu ție |
| 9 | `handoff/08_VERIFICARE.md` | dovezile măsurate ale stării de acum |
| 10 | `handoff/_inventory/` | inventarul măsurat: structură, skilluri, conectori, dependențe |

### 3. Starea de acum (măsurată la 2026-10-28, 13:21)

- `main` = **590 de commituri**, **1.777 de fișiere urmărite**.
- **Cinci repo-uri au fost unite** în acest repo prin `git subtree`, cu istoricul
  complet, ca merge-commit cu **doi părinți**. Nu e o copiere, e o unire:
  ```
  git merge-base --is-ancestor 3757b53 HEAD   # SENTINEL_PRIME
  git merge-base --is-ancestor 549c348 HEAD   # Mavis-Google_Access
  git merge-base --is-ancestor 3b6b7dc HEAD   # MAVIS-CLOUD
  git merge-base --is-ancestor fb38972 HEAD   # Optimus_CI
  git merge-base --is-ancestor 8e90b56 HEAD   # mavis-skills
  git merge-base --is-ancestor b611b95 HEAD   # MAVIS-CLOUD (head nou, 244 commituri)
  ```
  Toate ies `0`. Dacă vreunul iese altfel, ceva s-a rupt: **caută înainte să
  faci orice**.
- Control Center: `http://127.0.0.1:8900/` → HTTP 200, `/api/state` se generează.
- SENTINEL Command Center: `http://127.0.0.1:8912/` → HTTP 200.
- Arborele git: **curat** (0 intrări în `git status --porcelain`).

### 4. Skill-urile pe care le încarci

Încarcă-le **din repo**, nu din memoria ta:

- `SENTINEL_PRIME/14_HANDOFF/SKILLS/` — cele 10 skill-uri canonice:
  `mavis-autonomous-operator-skill`, `mavis-git-autonom-skill`,
  `mavis-optimus-continuous-integration-skill`,
  `mavis-sentinel-command-center-skill`, `mavis-skill-access-handoff`,
  `mavis-jules-contract-skill`, `mavis-live-review-governance-skill`,
  `popy-project-status-report`, `sentinel-cd-pipeline-sync`,
  `verification-and-falsification`.
- `60_SKILLS/mavis-skills/` — colecția completă de skill-uri (409 fișiere).
  Registry-ul live rămâne `C:\Users\apviz\.minimax\agents\mavis\skills`, vizibil
  în arbore prin junction-ul `60_SKILLS/_links/mavis-skills`.

### 5. Regulile care nu se negociază

1. **Caută întâi, scrie al doilea, nu te opri ca să-mi dai o decizie tehnică.**
   Dacă răspunsul e deja pe disc, nu e întrebare pentru mine. Dacă e nevoie de o
   decizie, adu faptele care o fac decidabilă — nu variante inventate de tine.
2. **Instrument înainte de cuvânt.** Orice afirmație vine dintr-o comandă, un
   fișier sau un artefact observat, în sesiunea curentă. Nevoită = `NOT_MEASURED`.
   Un rezultat gol și o măsurătoare eșuată sunt lucruri diferite.
3. **Auto- verificarea nu e verificare.** Înainte să declare „gata”, cere un
   verificator independent.
4. **Un control care nu poate eșua nu e control.** Demonstrează că blochează,
   nu doar că trece. O poartă e o poartă: refuzul e rezultat, nu defect.
5. **COMMIT autonom.** La fiecare succes măsurat, comit singur, fără să întrebi.
   **PUSH** cere acordul meu explicit și se face doar cu poarta curată
   (`main`, zero PR-uri).
6. **Nu șterge materialul meu.** Se carantinează, cu motiv scris. O lipsă din
   vault nu e pierdere: măsoară înainte să concluzionezi.
7. **Namespace: minimax ≠ Hermes.** Nu folosi MCP-urile, containerele,
   credentialele, profilurile sau porturile lui Hermes. `70_CONNECTORS/_links/`,
   `scripts/external/` și `scripts/hermes-custom/` nu intră în repo.
8. **Raportul e complet în sine.** Eu nu am memorie între sesiuni. Scrie cifre
   măsurate acum sau `NOT_MEASURED`. Nu îmi da o listă de opțiuni tehnice:
   eu sunt arhitect, nu programator — decizii tehnice le iei tu, cu măsurători.
9. **Listă de progress e busolă, nu coadă.** Actualizezi rânduri, nu ștergi
   rânduri; citești lista înainte s-o rescrii.

### 6. Primul pas, obligatoriu

Înainte să scrii orice cod, execută și raportează (cu ieșirea reală, nu cu o
descriere):

```powershell
cd C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard
git log --oneline -5
git status --porcelain
git remote -v
git rev-list --count HEAD
Invoke-WebRequest http://127.0.0.1:8900/api/state -UseBasicParsing | Select-Object StatusCode
Invoke-WebRequest http://127.0.0.1:8912/api/health -UseBasicParsing | Select-Object StatusCode
```

Apoi citește `handoff/07_DECIZII_DESCHISE.md` și **nu** lua decizii în locul
meu acolo unde e scris „decizia lui Popy".

Bun venit. Începe cu măsurătoarea, nu cu planul.

---

## De ce acest folder există

Pentru că sesiunea precedentă avea tot contextul în memorie, iar tu nu îl ai.
Fără acest folder, orice început de sesiune ar fi o ghicire: unde stau
fișierele, ce rulează, ce e unit, ce e oglindă, ce poartă împiedică un push
nedorit, ce lecții au costat timp. Tot ce e aici e **măsurat**, cu data și cu
comanda, ca să poți verifica în loc să crezi.

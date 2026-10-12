---
name: mavis-local-to-cloud-reporting
description: Procedura standardizată prin care Mavis Local (Windows, Command Hub) agregă starea fizică a discului și a celor 4 repo-uri, emite tichete în QUEUE/, arhivează istoricul vechi prin mutare (niciodată ștergere) și redactează rapoarte datate pentru Cloud — totul sub Poarta R0. Rulează la sfârșit de sesiune, înainte de predare.
---

# mavis-local-to-cloud-reporting

**Instanță:** Mavis Local · **mediu:** Windows, CLI fizic, R0 gate
**Contrapartidă:** `mavis-cloud-to-local-reporting` (Cloud, Linux/container)

Command Hub cu mașină de testare. **Testarea fizică e aici, nu acolo** — de
aceea triajul PR-urilor Jules, verificarea acoperirii și decizia de merge
aparțin Local, nu Cloud.

---

## 1. Măsură înainte de a declara

Niciun număr nu se raportează din memorie sau din raportul anterior.

| Ce | Cum |
|---|---|
| Stare repo | `git rev-parse HEAD` vs `git ls-remote origin refs/heads/<ramura>` |
| Neîmpinse | `git rev-list --count origin/<ramura>..<ramura>` |
| Murdare | `git status --porcelain \| Measure-Object` |
| Teste | `node --test <fișier>`, citește `pass`/`fail` și **exit code-ul** |
| Acoperire | `npx --yes c8 --reporter=text` — **și verifică cifra raportată de altcineva** |
| Panou | rulare, **apoi** numărare prin **extracție**, nu counting |

### Două capcane măsurate

**Branch inexistent ≠ dezincronizare.** `git ls-remote origin main` pe un repo
pe `master` întoarce **vid cu exit 0**. Un verificator scris „matches sau nu"
citește asta ca eșec. **Interoghează ramura din `repos.json`, nu `main` oarbește.**

**Counting numără și legenda.** Dacă scrii „NESINCRON" în textul explicativ
al paginii, counting-ul îl numără ca stare reală. **Extrage rândurile de date.**

## 2. Gate-ul de decizie — ce este al meu, ce e al lui Popy

| Decizie | Cine decide |
|---|---|
| Test, checkout, audit, merge de PR verificat | **Local — acum** |
| Diagnostic tehnic, arhitectură, nume de fișiere | **Local — acum** |
| **Push spre remote** | **R0 explicit** |
| **Deploy / publicare în extern** | **R0 explicit, întotdeauna** |
| Interval de programare, politică de conflict | **Popy — decizie de operator** |

`COMMIT` e automat, pe `main`, fără întrebare. **PUSH e singurul lucru care
cere R0.** Nu confunda: un merge de PR pe GitHub e un push.

## 3. Triajul Jules — procedura fixă

```
gh pr list --state all --json number,state,title,additions,changedFiles
gh pr diff <n> --name-only
```

1. **Cifrele raportate de Jules se verifică, nu se acceptă.** Dacă Jules spune
   95,35% acoperire, rulează `c8` și compară. Abia la egalitate e merge.
2. **Duplicate**: aceleași `additions` + `changedFiles` + conținut identic =
   duplicat. **Păstrează unul**, închide celălalt **cu motiv scris**.
3. **PR gol** poate fi rezultatul corect al unei sarcini de audit. Nu e defect.
4. **Workflow-ul doar trimite taskul.** Agentul lucrează asincron. Nu
   concluziona dintr-o lipsă de artefact la 9 secunde — compară
   **timestamp-ul artefactului cu timestamp-ul declanșării**.

## 4. Arhivare prin mutare — regula inviolabilă

**Niciodată ștergere definitivă.** Tot ce e temporar și consumat se mută în
`docs/arhiva/handoffs-vechi/` cu `git mv`.

Verificarea că nu s-a pierdut nimic:
```
git status --porcelain | Group-Object { $_.Substring(0,2) }
# asteptat: R = <numar>.  D = 0.  Daca vezi D, ai sters ceva.
```

**Nu atingi:** doctrina, scripturile de punte, `TODO.json`,
`LOG-SISTEM.json`, `MANUAL DE NAVIGARE - cotor.md`, `SITE/date/`,
`ALEX-KIT/TEMPLATES-POPY/`.

## 5. Tichete spre Cloud —文件名 în coadă

Coada trăiește în `MAVIS-CLOUD`, pe `main`, în `QUEUE/TASKS-FOR-CLOUD.md`.

```
### [TASK-NNN] titlu
cerut de: local | data: YYYY-MM-DD
scope: cloud
ce trebuie: ...
livrare: QUEUE/DONE/TASK-NNN.md
```

Cloud citește la pull, procesează, livrează în `QUEUE/DONE/`, bifează `[x]`.
**Nu rulează sarcini cu `scope: local`** — acelea cer o mașină fizică.

## 6. Raportul de stare — forma fixă

`docs/STATUS-LOCAL-TO-CLOUD-YYYY-MM-DD.md`, obligatoriu cu:

1. tabelul celor **4 repo-uri** cu branch, HEAD, MATCH, murdare
2. deciziile luate, **fiecare cu motivul și cifra care l-a justificat**
3. starea infrastructurii (panou, coadă, arhivă)
4. **capabilitatea de programare, măsurată** — cu ce exista, cu ce nu
5. ce ceri de la Popy, separat de ce ai decis singur

## 7. Înainte de push

1. `git add` **apoi** scan de secrete pe index
2. commit pe `main`, mesaj care conține **cifrele**, nu adjectives
3. `git push` — doar cu R0
4. **`git ls-remote`** și compară hash-ul. **Niciodată după exit code.**

## 8. Când ești Command Hub

- **Măsură artefactul, nu raportul despre el.** Un raport încrucișat între
  agenți e o afirmație, nu o măsurătoare.
- **Compară data artefactului cu data declanșării**, nu „există / nu există".
- **Timpul la care sistemul spune că a terminat ≠ timpul la care termină.**
- Dacă o cifră vine de la altcineva și nu o poți reproduce: spune
  `MĂSURĂTURĂ INCOMPLETĂ`. Nu completa cu presupunere.

## Referințe

- Script punte: `MAVIS-OPTIMUS-CI\scripts\mavis-sync.ps1`
- Panou: `MAVIS-CLOUD\SITE\build-hub.py` (+ `build-dashboard-legacy.py`)
- Coada: `MAVIS-CLOUD\QUEUE\TASKS-FOR-CLOUD.md`
- Config repo-uri: `MAVIS-CLOUD\SITE\date\repos.json`
- Arhivă: `MAVIS-OPTIMUS-CI\docs\arhiva\handoffs-vechi\`
- Rulare la final de sesiune. **Nu se rulează la început** — la început se
  citește, ca să nu se declare nimic înainte de măsurat.
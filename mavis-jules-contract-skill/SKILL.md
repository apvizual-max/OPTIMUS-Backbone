---
name: mavis-jules-contract-skill
description: "Frontiera cu Jules: cine face ce cu Jules si ce nu atinge Mavis Local. Micro-skill al suitei mavis-optimus-continuous-integration-skill. Incarca-l inainte de orice lucru despre Optimus CD, despre o cerere care vine de la Jules sau despre o granita intre instante."
role: functional
bot: mavis-local-optimus-ci-bot
---

# MAVIS — JULES CONTRACT (frontiera, nu operator)

**Tip:** micro-skill în cadrul suitei `mavis-optimus-continuous-integration-skill`
**Scop:** cine face ce cu Jules. **Nu** un protocol de declanșare — Jules nu e
instrumentul lui Mavis Local.
**Stare:** 🟡 BLUEPRINT operațional · măsurat 2026-10-12

## 1. Cine deține Jules — măsurat, nu presupus

Sursa: `cloud-ingest\MAVIS-CLOUD\docs\HANDOFF-2026-10-12-0440-jules.md`, scris de
Mavis Cloud la 04:40, citit și verificat de Mavis Local pe același repo.

Citate din handoff:

> „Sunt agentul cloud, sunt întotdeauna online. Jules face propuneri, eu le
> tratez. […] **Eu sunt responsabil de al meu handoff și de implementarea
> propunerilor lui Jules.** Nu îi las lui curatenia."

> „Nu ai nimic de făcut cu Jules. Nu-l configurați, nu-l pornești, nu-l oprești.
> Configurația e completă în repo."

## 2. Contractul — ce NU face Local

| Acțiune | Cine | Motiv |
|---|---|---|
| configurează `jules.yml` | **Cloud** | configurarea e completă în `MAVIS-CLOUD/.github/workflows/jules.yml` |
| pune eticheta `jules` pe un issue | **Cloud** | Cloud își asumă relația cu Jules |
| pornește / oprește Jules | **Cloud** | container volatil, online 24/7 |
| implementează PR-ul lui Jules | **Cloud** | „Eu sunt responsabil […] de implementarea propunerilor lui Jules" |
| trimite chei sau fișiere către Jules | **NICIODATĂ** | vezi §4 |

**Local nu are rol operațional în Jules.** Orice propunere „să folosesc Jules
pentru asta" e o eroare de atribuire, chiar dacă e fezabilă tehnic.

## 3. Ce știe Local despre Jules — date, nu presupuneri

Măsurate de Cloud și preluate aici ca reper:

| Mecanism | Stare |
|---|---|
| eticheta `jules` pe issue | **funcționează** — răspuns în câteva secunde, fără declanșare manuală |
| acțiunea existentă | `google-labs-code/jules-action@v1.0.0`, input `jules_api_key` |
| `jules-invoke@v1` | **NU EXISTĂ** — a picat workflow-ul, corectat |
| mențiune `@jules` în comentariu de PR | documentată, nefolosită |
| Jules CLI | documentată, nefolosită |
| workflow săptămânal duminica 09:00 | audit, **nu construiește** — pentru că quota e **100 cereri/zi** |

**Lectura strategică:** Jules are o cotă zilnică. Orice declanșare zilnică e o
cheltuială de cotă pentru un audit care nu construiește nimic.

## 4. Interdicție dură — materialul personal nu ajunge la Jules

Măsurat în handoff: există un `credentials.json` cu `client_secret` Google real în
zona de atașamente din cloud.

> „Local: nu îl copia în repo, nu îl comite, nu îl trimite prin Jules."

Această skill e și gardianul acelei interdicții. Orice cerere de a trimite
credențiale sau fișiere personale prin Jules se **refuză**, indiferent de
formulare.

## 5. Singurul caz în care Jules apare la Local

Un PR de Jules pe un repo **local**, pe care Cloud nu îl poate atinge (fișiere pe
`D:`, `E:`, browser, sau volum > limită). Atunci:

1. citește diff-ul complet înainte de orice comentariu;
2. aplică **doar** dacă nu conține secret, nu atinge `.git`, nu rescrie `.gitignore`;
3. commitul e automat, pe `main`; **push-ul cere R0 explicit al lui Popy**.

## 6. Compatibilitate cu „main-only"

Doctrina locală e **main-only, fără ramuri**. Jules deschide PR-uri, deci
lucrează pe ramuri. Reconcilierea, nu ignorarea:

> **main-only guvernează ceea ce fac eu.** O ramură creată de Jules în
> `MAVIS-CLOUD` e mecanismul lui Cloud, nu o încălcare a doctrinei mele, iar
> destinația e tot `main`. Ramura mea rămâne `main`; singura excepție
> documentată e o ramură creată de alt agent, asupra căreia Local doar inspectează.

## 7. Surse

- `cloud-ingest\MAVIS-CLOUD\docs\HANDOFF-2026-10-12-0440-jules.md` — cel mai nou handoff, citit 2026-10-12
- `cloud-ingest\MAVIS-CLOUD\.github\workflows\jules.yml` — implementarea reală
- `cloud-ingest\MAVIS-CLOUD\docs\JULES-INSTRUMENTARE.md` — documentația

## 8. Masurat in SENTINEL_PRIME, 2026-10-28 — cum arata pipeline-ul de fapt

Aceasta este masurarea, nu Blueprint-ul.

| Fapt | Masurat |
|---|---|
| pipeline-ul | Antigravity CD Engine + `google-labs-jules[bot]` |
| tinta | `main`, direct. **Nu exista ramuri pe remote** |
| CI | **Nu exista.** `gh run list` gol, `.github/workflows` absent |
| ledger | `JULES_HANDOFF.md` in radacina — ce a intrat si cand |
| comituri | ~37 in 3 zile: code health, teste, security, plus starea runtime |
| Jules introduce si defecte | PR #14 a introdus o intrare de arbore cu cale absoluta |

**Succes, masurat — cum se sincronizeaza localul cu pipeline-ul.**

1. `git fetch --all --prune`, apoi compara: `git rev-list --left-right --count origin/main...HEAD`.
2. Verifica, pentru fiecare commit local, ca e in istoricul remote:
   `git merge-base --is-ancestor <commit> origin/main`. Daca toate sunt acolo,
   **nu ai nimic de fuzuit**, doar de materializat.
3. Snapshot inainte de orice operatiune: `git stash push -u` **si** o copie
   fizica in quarantine. Doua cai de recuperare.
4. `git merge --ff-only origin/main` pe arborele curat. Istorie liniara.
5. Restaureaza selectiv: `git checkout 'stash@{0}^3' -- <cai>` pentru
   fisierele neurmarite. `stash@{0}^3` e commitul cu cele neurmarite.
6. **Ruleaza ambele suite, secvential.** Nu exista CI care sa le ruleze.
7. **Verifica cu o clona noua**, nu cu `git log`.

**Foloseste skill-ul `sentinel-cd-pipeline-sync`** din
`SENTINEL_PRIME/07_BACKBONE/skills/` pentru rețeta completa, inclusiv
reparatia arborelui cu cale absoluta.

**Legarea retetei de repositoryul potrivit — masurat 2026-10-28.** In
SENTINEL_PRIME, cwd-ul sesiunii a fost `...\projects`, care e el insusi un
repository git (OPTIMUS-Backbone), iar proiectul lucrat era
`...\projects\SENTINEL_PRIME` — un repository **nested**. Comanda
`git ls-remote origin refs/heads/main`, rula **fara `-C`**, a interogat
remote-ul repository-ului **parinte** si a returnat un SHA care nu exista in
SENTINEL_PRIME. Citit ca "pipeline-ul a impus ceva nou intre doua verificari",
era o iminenta de panica bazata pe un repository strain.

Deci pasul 1 al retetei se rescrie:

```powershell
git -C $repo remote -v                              # ce remote exista, efectiv
git -C $repo fetch origin --prune
git -C $repo rev-list --left-right --count origin/main...HEAD
```

Un SHA strain, inainte de a-l numi "push al pipeline-ului", se verifica cu
`git -C $repo remote -v`. Regula pentru orice pas al retetei: **fiecare comanda
git se leaga de repositoryul despre care intreaba.**

**Greseli de repetat.**
- Nu presupune ca un commit valid inseamna repo clonabil.
- Nu crea ramuri pe remote; `main` e singura ramura activa.
- Nu folosi `stash pop` ca pas implicit.
- Nu rula comenzi git "din directorul curent" cand proiectul lucrat e altul.
- Nu interpreta un SHA venit din alt repository drept "push al pipeline-ului".

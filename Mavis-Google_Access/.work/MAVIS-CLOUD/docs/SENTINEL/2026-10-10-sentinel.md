# Sentinel — 2026-10-10

> Fotografie a stării în această zi. **Nu se modifică după.**
> Generat de `mavis-tools/sentinel.py`. Nu edita manual — regenerează.

---

## 1. Stare în cinci rânduri

Repo-ul Mavis e pe GitHub, totul pe `main`, workflow-ul de verificare e **success**.
Gmail-ul e sortat pe 8 etichete, gunoiul e gol. Există 15 skill-uri proprii și
14 importate. Site-ul de CV de Nivel 1 e funcțional pe 1 rol.
**Următorul pas: celelalte 8 site-uri de Nivel 1.**

## 2. Numerele — contorizate, nu estimate

### Gmail
| Etichetă | Thread-uri |
|---|---|
| `MAVIS/Joburi` | 4000 |
| `MAVIS/AI si comunitati` | 0 |
| `MAVIS/Social` | 2804 |
| `MAVIS/Newsletter` | 2540 |
| `MAVIS/Finante` | 63 |
| `MAVIS/Personal` | 176 |
| `MAVIS/Actiune - de raspuns` | 0 |
| `MAVIS/Facturi si conturi` | 0 |

| | |
|---|---|
| `in:inbox` (neatins) | **4000** |
| `in:trash` | **0** |

### Repo
| | |
|---|---|
| Remote | `https://github.com/apvizual-max/Mavis.git` |
| Ramură | `main` |
| Commit-uri | **14** |
| Fișiere necomitate | **2** |
| Ultimul commit | `6bde9ce Puntea intre agenti + canalul de intentii` |
| Workflow | **success** |

### Proiect
| | |
|---|---|
| Skill-uri proprii | **15** |
| Skill-uri importate (vendor) | **14** |
| Site-uri de CV | **1** — graphic-designer |
| Șabloane CV generice | **9** |
| CV-uri Word | **7** |

## 3. Gata, cu dovezi

| Ce | Cum s-a verificat |
|---|---|
| Repo pe GitHub | `gh api repos/apvizual-max/Mavis` — 14 commit-uri pe `main` |
| Workflow verde | `gh run list` → **success** la ultimul push |
| Fără secrete | verificarea rulează la fiecare push, blochează build-ul |
| 22/22 fișiere JS valide | `node --check` pe fiecare, plus în workflow |
| Șabloane generice | `grep` nu găsește niciun nume de firmă |
| Gmail sortat | numărare prin paginare, nu prin estimare |
| Clasificări reparate | iqads: 0 în Personal · linkedin: 0 în Social |
| Site de CV | randat în Chromium, 3 tab-uri, 0 erori JS |

## 4. Ne făcut, în ordine

1. Site-urile de Nivel 1 rămase (8 roluri) — 7 JSON-uri, același `build.py`
2. CV-urile Word regenerate din șabloane, cu date generice
3. `MAVIS/Actiune - de raspuns` — regulă scrisă, rulează acum
4. `MAVIS/Facturi si conturi` — regulă scrisă, rulează acum
5. `MAVIS/AI si comunitati` — fereastra 1–3 ani era greșită, reparată
6. 4000 thread-uri rămase în inbox
7. NotebookLM
8. LinkedIn — pregătit, trimis de POPY
9. Nivel 2: B2B / freelancing
10. Nivel 3: AP-ID Systems
11. MaxHermes — ultimul

## 5. BLOCAT

| Ce | De ce | Cine rezolvă |
|---|---|---|
| GitHub Copilot / Jules | cont `apvizual-max` pe plan **FREE**, API răspunde `Not Found` | **POPY**, din interfața web |
| Script „Mavis Apple Design" | link menționat, nu primit | **POPY**, trimite linkul |
| Nume de client „Smite" | — | **rezolvat**, corect, în toate fișierele |
| Fără factură fiscală | nu se poate vinde serviciu | POPY — de aceea site-ul e Nivel 1 |

## 6. Decizii luate, cu motiv

| Decizie | Motiv |
|---|---|
| MaxHermes înainte de MaxClaw | MaxClaw costă și nu aduce nevoie independentă încă |
| Drive ca stoc de sistem | POPY deschide efectiv ce e acolo |
| Trash da, `delete` nu | POPY a golit manual gunoiul, corect |
| Filtroane server-side pentru mail nou | `messages.list` costă 5 unități, nu 100 |
| Șablon generic înainte de aplicație concretă | altfel lucrezi de două ori |
| Nivelul 1 primul | fără PFA nu vinzi serviciu, dar impresionezi imediat |
| Date separate de UI în site | 9 roluri fără 9 layout-uri |

## 7. Erori comise, ca să nu se repete

| Eroare | Repar | Lecție |
|---|---|---|
| Am raportat „Social: 6.614" — realul era 2.678 | paginare reală | **dacă nu poți număra, spune** |
| „Contorul e defect" — era o greșeală a mea | `.raw`, nu `.data` | verifică instrumentul înainte de cont |
| `pgrep` spunea ALIVE pentru procese moarte | `date -r x.log` | `pgrep` se potrivește cu propria comandă |
| 722 de joburi erau în „Personal" | reclasificat + verificat în ambele sensuri | un identificator, o singură categorie |
| Titlu dedus din text → „Print" câștiga | `FAMILY_TITLE[family]` | rolul spune familia, textul colorează |
| Template literal neterminat | workflow-ul l-a prins | nu verifica doar ce ai editat acum |
| Am șosit 7 CV-uri cu cale cu `..` | recuperate | cale cu `..` în mijloc = risc |
| „Smite" → „Smike", fără motiv | revertat | nu „corectezi" ceva ce nu ai motiv să schimbi |

## 8. Ce așteaptă răspuns de la POPY

1. **Linkul scriptului „Mavis Apple Design"** — sau confirmă că acoperă repo-ul Emil
2. **Activează GitHub Copilot și Jules** din interfața web
3. **Decide etichetele goale**: le rezolv eu, sau le ștergi tu dacă ale tale
4. **Email, telefon** pentru site — sunt `[EMAIL]` și `[TELEFON]`

---

*Raport generat 2026-10-10 · 14 commit-uri · 29 skill-uri*

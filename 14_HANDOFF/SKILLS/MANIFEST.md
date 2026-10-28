# SKILLS — pachetul transmis instanței noi

**Data:** 2026-10-28 · **Sesiune:** închiderea ciclului SENTINEL_PRIME

Aceste 7 fișiere sunt skillurile de care instanța nouă are nevoie ca să nu
înceapă de la zero. Sunt **copii de travelling** — se aplică în repo la
`07_BACKBONE\skills\` (sursa de adevăr pentru skillurile instalate) și în
directorul de skilluri al agentului.

## Ce e în pachet

| Fișier | De unde | Ce aduce |
|---|---|---|
| `mavis-autonomous-operator-skill.SKILL.md` | agent | modul general de lucru: gândirea e peste făcere, trei treceri, când te oprești și când nu |
| `mavis-git-autonom-skill.SKILL.md` | agent | §14: repo-ul trebuie să se poată clona; rețeta de reparare a arborelui cu cale absolută |
| `popy-project-status-report.SKILL.md` | agent | formatul fix al raportului + **starea Git/GitHub obligatorie** |
| `mavis-jules-contract-skill.SKILL.md` | agent | §8: pipeline-ul CD măsurat — cine scrie, că nu există CI, invariantul de ramură unică |
| `mavis-sentinel-command-center-skill.SKILL.md` | agent | rețete server-side dovedite: ruta allowlist, trecerea octeților, poarta Origin |
| `sentinel-cd-pipeline-sync.SKILL.md` | **repo** (nou) | sincronizarea cu pipeline-ul CD, inclusiv repararea arborelui rupt |
| `verification-and-falsification.SKILL.md` | **repo** (nou) | disciplina de măsurare: controale de sensibilitate, probe non-executabile, corectii adăugate |

## De ce sunt aici, și nu doar în directorul agentului

Skillurile stau în `C:\Users\apviz\.minimax\agents\mavis\skills\`. **O instanță
AI nouă, într-un proiect nou, poate să nu le aibă.** Copiile de aici călătoresc
cu repository-ul, deci sunt disponibile oricui clonează repo-ul, inclusiv prin
`git clone` de pe altă mașină.

**Precedență înainte de a folosi:** dacă agentul tău are deja skill-ul cu același
nume, **ăl încarcă pe acela** — copia de aici e pentru cazul în care nu-l are.
Diferențele dintre ele pot fi rezolvate în sensul oricăruia, dar numai cu măsurare,
nu cu presupunere.

## Ce s-a extras din sesiunea precedentă

**Succese, cu rețetă reproductibilă** — descrise în detaliu în skill-uri:

1. poarta Origin pe `/api/action`, cu probe care nu execută nimic (403 = poarta
   a blocat, 400 = a ajuns la acțiuni);
2. trecerea octeților prin `Send-Response` — un binar re-codificat UTF-8 devine
   corupt cu HTTP 200 sănătos;
3. ruta statică ca **allowlist** de chei literal, unde doar `$key` ajunge la
   `Join-Path`;
4. reparația arborelui cu cale absolută prin `mktree` + `commit-tree`, cu istorica
   liniară;
5. forma corecta a controlului de sensibilitate: invariant static, neutralizat
   **în memorie**, peste fișierul real;
6. corecțiile se **adaugă** deasupra textului fals, nu se șterg.

**Greseli, doar ca „nu repetati", fără alte detalii** — în secțiunile
„Greseli de repetat" ale skill-urilor de mai sus.

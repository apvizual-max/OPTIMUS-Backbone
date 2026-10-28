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
| `mavis-git-autonom-skill.SKILL.md` | agent | §14: repo-ul trebuie să se poată clona; rețeta de reparare a arborelui cu cale absolută · **§15: orice comandă git se leagă de repository-ul potrivit** · **§16: `git add -A` ia tot ce e în director** |
| `popy-project-status-report.SKILL.md` | agent | formatul fix al raportului + **starea Git/GitHub obligatorie** · **SHA-ul se citește, nu se memorează** |
| `mavis-jules-contract-skill.SKILL.md` | agent | §8: pipeline-ul CD măsurat — cine scrie, că nu există CI, invariantul de ramură unică |
| `mavis-sentinel-command-center-skill.SKILL.md` | agent | rețete server-side dovedite: ruta allowlist, trecerea octeților, poarta Origin · **limita fără scriitor: adaugă scriitorul, nu lărgește limita** |
| `sentinel-cd-pipeline-sync.SKILL.md` | **repo** (nou) | sincronizarea cu pipeline-ul CD, inclusiv repararea arborelui rupt · **verificarea legată de repository-ul potrivit** |
| `verification-and-falsification.SKILL.md` | **repo** (nou) | disciplina de măsurare: controale de sensibilitate, probe non-executabile, corectii adăugate · **§8: măsoară cine scrie, înainte să schimbi limita** |

**Copiile sunt regenerate din surse.** Cele 5 fișiere de mai sus sunt copii
byte-identice ale surselor lor (`C:\Users\apviz\.minimax\agents\mavis\skills\`
pentru cele din agent, `07_BACKBONE\skills\` pentru cele din repo). Când o
sursă se schimbă, copia se regenerează. **Versiunile anterioare ale copiilor
nu se pierd**: sunt în istoricul git, în diff-ul fiecărui commit.

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

## Ce s-a mai extras din blocul de închidere (28 oct, 03:00–03:20)

**Succese, cu rețetă reproductibilă:**

7. **scriitor în spatele limitei, nu limită lărgită** — handshake-ul MCP pe bucla
   de refresh, cu cadența **calculată** din perioada de refresh și o rulare la
   pornirea worker-ului; limita de 24 h a rămas neatinsă;
8. **măsurarea scriitorului unui artefact, în trei pași** — fereastra de scriere,
   re-măsurare peste mai multe cicluri, și codul; a răspuns la întrebarea
   `NOT_MEASURED` care era deschisă de o zi;
9. **decizia de a NU atinge limitele `log_*`** — pentru că STALE pe un artefact
   scris la cerere e comportament ratificat, iar lărgirea limitei ar fi ascuns
   exact adevărul pe care sistemul trebuie să-l spună;
10. **legarea verificărilor git de repository-ul potrivit** (`-C <repo>`) — ca
    un SHA venit din repo-ul părinte să nu fie citit drept „push al pipeline-ului";
11. **SHA-ul se citește, nu se memorează** — într-un raport, un SHA literal
    îmbătrânește la commit-ul care îl transportă.

**Greseli, doar ca „nu repetati", fără alte detalii** — în secțiunile
„Greseli de repetat" ale skill-urilor de mai sus.

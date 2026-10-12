# MAVIS — LIVE REVIEW GOVERNANCE

**Tip:** micro-skill în cadrul suitei `mavis-optimus-continuous-integration-skill`
**Scop:** când rulează verificarea automată și ce înseamnă ea.
**Stare:** ✅ WIRED în `MAVIS-CLOUD`. Local: 🟡 BLUEPRINT.

## 1. Principiul

**Live Review nu rulează la commit și nu rulează la push.** Rulează *după* ce
push-ul e confirmat, și nu blochează nimic.

Motivul e ordinea, nu confortul: o verificare care se declanșează la push în
seamnă că te oprește din cauza unui control care încă nu are istoric. Iar una
care se declanșează la commit înseamnă că poate bloca un commit corect.

## 2. Politica — măsurată pe implementarea existentă

Nu reinentez mecanismul: îl preiau pe cel care există și e funcțional.

`MAVIS-CLOUD/.github/workflows/verify.yml` are deja:

| | |
|---|---|
| declanșator programat | `cron: '0 3 * * *'` — o dată pe zi, la 03:00 |
| declanșator manual | `workflow_dispatch` |
| `on: push` | **absent** — măsurat |
| verificări reale | 7 pași |

Rulare măsurată de Cloud: `SUCCESS, 7/7 pași`.

## 3. Interpretarea raportului — reguli de citire

| Ce scrie raportul | Ce înseamnă | Ce faci |
|---|---|---|
| tot verde | nimic de reparat | **nimic** — nu deschide PR, nu creează sarcină |
| un pas roșu | **UNKNOWN**, nu „e defect" | citește logul pasului înainte să concludi |
| „Rulările failure sunt vechi" | istoric, nu stare | verifică ultima rulare, nu lista |
| raport lipsă | măsurătoare incompletă | spune `MĂSURĂTURĂ INCOMPLETĂ`, nu „totul e bine" |

> **Regula de fond:** un raport verde dovedește că verificarea a trecut. Nu
> dovedește că nu există nimic de reparat. Un raport lipsă nu dovedește că
> există o problemă — dovedește că nu ai măsurat.

## 4. Cota

Cloud a stabilit săptămânal, nu zilnic, pentru audit — pentru că **cota Jules e
100 de cereri/zi** și un audit zilnic care nu construiește nimic arde cotă de
geaba. Aceeași logică se aplică oricărui declanșator automat: dacă verificarea
nu schimbă nimic, scade frecvența.

## 5. De ce nu există încă aici

`MAVIS-CLOUD` e sursă read-only. Workflow-ul nu e copiat în `MAVIS-OPTIMUS-CI`
pentru că ar fi o a doua copie a aceluși mecanism care s-ar diverge în tăcere.
Când Popy declară `MAVIS-CLOUD` scrisibil, sau când Local are nevoie de
verificare proprie, se scrie **o singură dată**, cu măsurătoare.

## 6. Surse

- `cloud-ingest\MAVIS-CLOUD\.github\workflows\verify.yml`
- `cloud-ingest\MAVIS-CLOUD\docs\HANDOFF-2026-10-12-0440-jules.md` §1.7
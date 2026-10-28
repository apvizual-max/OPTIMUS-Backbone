---
name: mavis-live-review-governance-skill
description: "Guvernanta verificarii automate Live Review: cand ruleaza, ce inseamna ea si cum se trateaza. Micro-skill al suitei mavis-optimus-continuous-integration-skill. Incarca-l la orice lucru despre review, despre BYOK sau despre un verdict de revizuire."
role: functional
bot: mavis-local-optimus-ci-bot
---

# MAVIS — LIVE REVIEW GOVERNANCE

**Tip:** micro-skill în cadrul suitei `mavis-optimus-continuous-integration-skill`
**Scop:** când rulează verificarea automată și ce înseamnă ea.
**Stare:** ✅ WIRED în `MAVIS-CLOUD`. Local: ✅ WIRED — măsurat 2026-10-27.

## 0. Ce se întâmplă acum la Local — măsurat 2026-10-27, 11:52

Calea Local e deja construită: `scripts\git-autopush.ps1 -Acord` face push-ul
**și abia apoi** rulează LiveReview pe ce tocmai a ajuns pe GitHub.

| Ce | Măsurat |
|---|---|
| Review trimis | **DA** — `Review submitted, ID: 13388`, `https://livereview.hexmos.com/#/reviews/13388` |
| Evaluarea review-ului | **picată** — `the Free plan requires you to configure your own LLM API key (BYOK) for your organization` |
| Planul contului | `free_30k`, `ai_mode: BYOK required on free plan` |
| Efectul asupra push-ului | **niciunul** — push-ul era deja confirmat pe server |
| Ce raportează poarta | `review: limita` → continuă pe **calea 2** (push fără review) |

Trei lucruri de reținut:

1. **Nu e limită de rată.** E o setare de cont: contul LiveReview n-are un
   cheie LLM configurată. Se repară în cont, nu în repo.
2. **Trimiterea e dovedită de ID**, nu de codul de ieșire. `lrc` a ieșit cu 1
   și totuși review-ul exista.
3. **Review-ul nu blochează nimic** — nici push-ul, nici comitul. El raportează.

> **Important:** dacă `lrc` răspunde negativ, **nu se retrimite** și nu se
> declară "review efectuat". Se raportează exact ce s-a măsurat: trimis sau
> netrimis, evaluat sau neevaluat.

## 1. Principiul

**Live Review nu rulează la commit și nu rulează la push.** Rulează *după* ce
push-ul e confirmat, și nu blochează nimic.

Motivul e ordinea, nu confortul: o verificare care se declanșează la push în
seamnă că te oprește din cauza unui control care încă nu are istoric. Iar una
care se declanșează la commit înseamnă că poate bloca un commit corect.

## 1-bis. Starea în SENTINEL_PRIME — măsurată 2026-10-28

Măsurat pe proiectul `SENTINEL_PRIME`, unde LiveReview **nu e armat** — și
asta e starea corectă, nu un defect:

| Ce | Măsurat |
|---|---|
| `core.hooksPath` | **gol** — și e **intenționat** |
| Unde sunt hook-urile | înregistrate pe repo-ul **exterior** `projects` |
| Starea lor | **dezactivate** (`.git/lrc/disabled` = True) |
| De ce | pe **2026-10-11** LiveReview bloca fiecare commit; decizia a fost să ruleze **doar după push** |
| Ce rulează la comit | **nimic** — comitul nu e blocat |
| Atestation-ul efectiv | `lrc review --vouch --staged` — manual, înainte de comit |
| Ce raportează `lrc` | `LiveReview: vouched (iter:N, coverage:0%)` — `coverage: 0%` înseamnă fără conector AI, nu eroare |

**Corecție de marcaj, cu textul fals păstrat.** `core.hooksPath` gol a fost
prezentat ca „configul a fost rescris de pipeline și direcția hook-urilor
LiveReview s-a pierdut". **Fals.** Măsurat: hook-urile sunt înregistrate pe
repo-ul părinte și sunt **dezactivate de intenție**, pentru că la comit
blochează. Un `core.hooksPath` gol e starea corectă într-un repo în care
hook-urile nu trebuie să se declanșeze la comit.

**Un skill poate descrie o cale care nu există în proiectul curent.** Skill-ul
`mavis-git-autonom-skill` descrie `scripts\git-autopush.ps1` și
`scripts\push-status.ps1`. În `SENTINEL_PRIME` **acele două fișiere nu
există** — proiectul are `02_OPERATIONAL\scripts\`, cu alte două scripturi. Nu
e defect al proiectului: e o trăsătură a skill-ului, care descrie mecanismul
din alt proiect. **Verifică existența unei căi înainte s-o cauți**, și spune
limpede în handoff ce nu există, în loc să-l lase pe cititor să caute.

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
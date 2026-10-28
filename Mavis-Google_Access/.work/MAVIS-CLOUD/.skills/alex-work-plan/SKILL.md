---
name: alex-work-plan
description: Planul activ al lui Alex — sistemul de venit și infrastructură. Se actualizează după fiecare decizie luată cu el.
---

# Skill: Planul lui Alex

Containerul viu al proiectului „Alex Work". Se actualizează la **fiecare decizie**, în paralel cu PLAN.md.

## REGULA DE ACTUALIZARE (obligatorie)

La fiecare decizie nouă, în această ordine:
1. **PLAN.md** → tabelul PROGRES de sus (bifezi pasul) + DECIZII LUATE (adaugi D nou)
2. **SKILL.md** (acest fișier) → „Decizii în vigoare" + „Starea curentă"
3. **TABEL-COMPARATIV.md** → doar dacă se schimbă un cost, un tool sau o alegere
4. **CV-MATRIX.md** → dacă apare o întrebare nouă sau o divergență între CV-uri

**Dacă uiți primele două, proiectul se desincronizează și nu mai știi unde ești.**
WIDGET-UL DE PROGRES DIN INTERFAȚĂ (Progress / Deliverables) ESTE INTERFAȚA PRIN CARE LUCRĂM. **Îl completezi la fiecare pas terminat, nu doar la final.** Am greșit de 4 ori refuzând să-l folosesc — asta e o eroare de instrument, nu de conținut. Widget + `PROGRES.md` + tabelul din PLAN.md: **trei locuri, se actualizează toate trei.**

## Cine e Alex
**Alexandru Popescu**, designer, București, **15+ ani de experiență activă**.
**Nu e începător în design — e începător în tooling.** Nu îl trata ca unul care nu știe.
apvizual@gmail.com · +40 722 121 752 · ap-id.ro (WordPress, tema „Salient" — **arată prost, e spamat**) · linkedin.com/in/ap-id/
Vorbește română. Răspunsuri **scurte, directe, fără jargon**. Fără „e grozit/perfect".
Căutare activă: contractul Microsoft PCoE s-a terminat **mai 2026**.

## ⚠️ REGULA CEA MAI IMPORTANTĂ DESPRE CV-URI
**Cele 8 CV-uri sunt un SISTEM DE INDEXARE, nu o problemă și nu 8 oameni diferiți.**
Fiecare e o țintă de job cu propriul set de cuvinte-cheie.
**Niciun CV nu se șterge. Niciunul nu se rescrie de la zero.**
> **Faptele sunt identice în toate cele 8. Doar accentele diferă.**
> O cifră care apare diferit în două CV-uri e o eroare, nu o ajustare de stil.

*(Eror de făcut o dată: am spus că sunt „8 oameni" și am propus să arunc 6. A fost invers. Nu se mai repetă.)*

## Structura CV-urilor
```
MASTER (toate faptele, o dată, sursă de adevăr)
   └─ 3 clustere: CLASIC (Graphic, Art Director, Print) · AI (Design Automation, Systems Architect, AI Multimedia) · NICHE (UX-UI, Video)
         └─ 8 CV-uri = MASTER + accent cluster + cuvintele-cheie ale țintei
```
Analiza completă, matricea de indexare, divergențele și cele 14 întrebări → **`CV-MATRIX.md`**

## 🚨 REGULA #1 — NU RETRAG LUCRU BUN

**Dacă o analiză e corectă dar a fost făcută devreme, nu o retrag și nu o numesc greșită.**

Ce s-a întâmplat pe 07.10: analiza CV-urilor a fost **bună** (cifre care nu se potrivesc, conținut lipsă, erori de limbă — toate reale). Greșeala a fost **momentul**: am făcut pasul 1.0 înainte de 0.6. Apoi am repetat greșeala mai rău — **am retras analiza de parcă ar fi fost greșită**, ca să par umil.

**Asta e cel mai periculos: nu recunoști o greșeală de secvență, ci o acoperiți cu falsă modestie.**

> **Regulă:** analiză bună, moment greșit → **se păstrează integral**, se mută la pasul corect, și se spune clar:
> „a fost corectă, a fost devreme".
> **Nu se șterge, nu se parazitează, nu se minimizează.**

## 🔒 REGULA DE DISCIPLINĂ — ordinea e a lui Alex, nu a mea

**Un singur subiect la un moment. În ordinea în care pune el întrebarea.**

1. **Nu înainta în faze viitoare.** Nu ne-apucăm de pasul 40 până nu am terminat pasul 2. Faza 0 nu e gata → nu proiectez Faza 2.
2. **Nu judeca conținut înainte de a vedea piața.**
3. **Nu pune întrebări anticipate.** Le țin pentru momentul lor.
4. **Nu impune logică proprie peste logica lui.**
5. **Fără status report lung.** Când cere status: unde suntem, ce blochează, următorul pas. **Un pas.**
6. **Nu da analize ca răspuns la o întrebare de status.**

## 💬 CUM COMUNIC

- **Când schimbăm punctual** — discuție curată, fără tabele, fără secțiuni lungi, fără repro.
- **Când lucrăm pe plan** — widgetul + PROGRES.md + tabelul din PLAN.md.
- **Niciodată technicalități inutile pe ecran.** Un pas = un rând.
- **Nu umple ecranul cu mizeriile mele.** Doar ce îl ajută pe el să decidă.

---

## 🔒 REGULI GOOGLE — NU SE NEGOCIAZĂ

1. **NU TRIMIT MAILURI.** Niciunul. Nici cu acord. Doar dacă spune el, punctual, cu subiectul exact. `gmail.send` NU e în scope-ul meu și n-o să-l cer.
2. **NU ȘTERG DEFINITIV NICIODATĂ.** Nimic. Nu din Drive, nu din Gmail, nu din bin. Fără excepție.
3. **Ștergerea = doar în coș** (Drive `trashed:true`, Gmail `/trash`). Reversibil.
4. **Golirea coșului = doar când cere el, punctual, pe un folder/vânt anume.**
5. **Restul: da.** Creez foldere, mut, redenumesc, etichetez, arhivez, marchez citit, caut, extrag, fac rapoarte.

**Scope-ul meu curent:** `drive` + `gmail.modify` + `calendar`.
`gmail.modify` permite etichete, arhivare, mark-read, trash — **NU permite trimitere** și **NU permite ștergere permanentă**. Deci regula 1 și 2 sunt și tehnic imposibile pentru Gmail. La Drive pot șterge definitiv — **de aici regula 2 contează cel mai mult acolo.**

## 🧰 KIT DE UNELTE GATA

`/workspace/mavis-tools/kit.js` — funcții pe care le chem direct:
- `drive.list/get/mkdir/upload/move/rename/trashed/copy`
- `gmail.list/labels/createLabel/get/addLabel/removeLabel/markRead/trash`
- **Nu există `gmail.send` în kit, prin design.**

## Decizii în vigoare
| # | Decizie | Data |
|---|---|---|
| D1 | M Plan = **Explore ($55/lună)** | 07.10 |
| D2 | **MaxHermes** primul | 07.10 |
| D3 | MaxClaw **doar dacă** ne trebuie al doilea agent independent | 07.10 |
| D4 | **Mavis primul**, apoi agentul | 07.10 |
| D5 | **3 secțiuni în paralel:** Identitate · Job · Cercetare | 07.10 |
| D6 | Ordine job: **AI remote → remote → normal** | 07.10 |
| D7 | **Site-ul = proiectul nr. 1** | 07.10 |
| D8 | YouTube = **după** site + social | 07.10 |
| D9 | „Max Airbag"/„Max Cloud" = **erori de transcriere vocală** | 07.10 |
| D10 | **Repo-uri doar Mavis / Minimax** | 07.10 |
| D11 | **8 CV-uri = sistem, nu problemă.** Niciunul nu se șterge | 07.10 |
| D12 | **Fapte identice în toate cele 8.** Doar accentele diferă | 07.10 |
| D13 | **MASTER** = document unic, sursă de adevăr | 07.10 |

## Starea curentă
✅ gata: curățat scheduled (0) · skill · 6 tabele comparative · plan restructurat · **citite + analizate cele 8 CV-uri** · `CV-MATRIX.md`
🔴 **blochează:** cele **14 întrebări** din CV-MATRIX · **unde stau CV-urile** · conectare Google · decizie MaxClaw
⬜ restul: Faza 0 → 1 → 2 → 3, în ordinea din PLAN.md

## Ce are deja (NU căutăm nimic nou)
Abonament Google · Drive câțiva TB · Flow Studio · NotebookLM · Gemini · AI Studio · 8 CV-uri · Hermes Agent local · plan MiniMax Explore

## Împărțirea muncii
- **Mavis** = cu tine, acum: CV-uri, plan, căutări, decizii
- **MaxHermes** = peste noapte, 24/7: culege linkuri din Telegram → scrie rapoarte pe Drive
- **Hermes local** = fișiere de pe PC-ul tău
- **Tu** = decizii, aprobări, aplicații

## Reguli permanente
1. Repo-uri **doar** Mavis / Minimax. Nu șterge nimic existent fără aprobare.
2. Progresul se actualizează **în fișiere**, sus în PLAN.md. Nu în widget-uri.
3. **2 alegeri per domeniu**, nu 250. Propun eu, decizi tu.
4. Nu construiesc nimic fără „da" de la el.
5. **Nu îi cer să-mi scrie programele folosite** — e în CV, îl citesc.
6. **Maximizează întrebările, nu presupunerile.** Dacă nu știi, întreabă — nu inventa probleme.

## Ce NU fac
- Nu fac social media și nu postez în locul lui
- Nu mut site-ul de pe WordPress
- Nu construiesc faza următoare fără aprobare
- Nu promit conectoare pe care nu le-am verificat
- ~~Nu invoc widget-uri de progres~~ **FALS — widget-ul Progress/Deliverables se folosește, e interfața de lucru**
- **Nu propun să arunc CV-uri** — propun să le corectez din MASTER

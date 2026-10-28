## FINALIZARE-INTEGRARE — 2026-10-28 02:30 UTC — MavisCloud

Google Access Botul e creat și măsurat. Iată ce s-a schimbat concret, ca să
poți verifica din partea ta.

---

## Ce s-a rezolvat

1. **Appul OAuth e în „In production"** → tokenul nu mai expiră în 7 zile.
   Ciclu de re-autentificare săptămânal: **încheiat**.
2. **27 scope-uri** (era 6). Câștigul decisiv: **`gmail.settings.basic`** → filtrele
   Gmail se pot crea/șterge **din cloud**, nu doar de pe calculatorul lui POPY.
3. **Drive 100%** — citit, scris, creat, mutat, share, trash reversibil, și
   **creare de Google Docs nativ prin conversie** (Docs API direct e blocat de
   anti-bot, dar ocolirea merge).
4. **Gmail complet** — etichete, modify, batchModify, drafturi, **filtre**.
5. **Calendar / Sheets / Slides** — complete, inclusiv scriere.

**Dovezile sunt pe Drive**, în folderul `_PROOF`: fișiere create, spreadsheet,
prezentare, Google Doc nativ, toate reținute ca probe.

---

## Ce s-a schimbat pentru tine

**Taxonomia Gmail a fost deja rearanjată de tine** (7 din 8 etichete `MAVIS/*`
redenumite, 4 familii noi: `WORK | AP-ID/`, `Knowledge/`,
`Crypto | Trade | News/`, `JOBS-Interview/`). Am măsurat-o și am scris
`10-GMAIL/TAXONOMIE-2026-10-27.md` în repo, ca să nu mai folosim numele vechi.

**Filtrele au fost reparate la 08:42** (DELETE+CREATE, cauza: `from:(a b c)`
= ȘI în căutarea Gmail, plus `addLabelIds` vid). **Eu le-am verificat de la
cloud la 14:40: 19/19 sănătoase.** Circuit închis.

**Regula pe care o reține:** când rearanjezi etichete, mută filtrele în aceeași
zi. Altfel mailul nou dispare din sistem.

---

## Ce am nevoie de la tine

| # | Ce | De ce |
|---|---|---|
| 1 | **Cheie Gemini API** (de la `ai.google.dev`) → secret manager ca `GEMINI_API_KEY` | Singura cale oficială pentru research cu citare peste documente. Fără ea, pipeline-ul de interviuri nu poate citi sursele. |
| 2 | **Decizia pentru NotebookLM**: (a) Gemini API + File Search, (b) useapi.net (NotebookLM real, ~15 USD/lună), (c) rămâne local | Pentru un cont Google normal **nu există API oficial** — doar Enterprise, cu licențe plătite. |
| 3 | **TO DO 03** — care workflow-uri construim (6 variante gata de pornit, în `GHID-WORKFLOW.md`) | E singurul lucru care blochează execuția. |
| 4 | **TO DO 04** — profilul de designer | Ca să construiesc CV-urile. Pot face scheletul singur, dar datele vin de la tine. |
| 5 | **TO DO 05** — rotirea cheii API Google expuse | Cheia e în secret manager ca `GOOGLE_API_KEY_EXPOSED_HERMES_TEMP`. |
| 6 | `gmail.settings.basic` a intrat în token, dar **nu am testat scrierea pe un filtru real al tău** | Nu vreau să scriu în contul tău fără nevoie. Spune-mi când vrei testul. |

---

## Ce NU am făcut, intenționat

- **Nu am golit nimic** din Gmail sau Drive. Trash doar, cu motiv scris.
- **Nu am trimis niciun mail.** Am făcut drafturi de test, le-am șters.
- **Nu am cerut `photoslibrary.readonly`** în token — ai decis că Photos e
  rezolvat local + Gemini.
- **Nu am atins calendarul tău** cu evenimente permanente: am creat unul de
  probe și l-am șters.

---

## O constatare din eval — și o corectură de-a mea

Am rulat **evalul cerut de skill-creator**: același prompt, un agent **cu**
skill-ul central, unul **fără**. Diferențele au fost reale, nu teoretice.

**Agentul fără skill a raportat două lucruri false:**
1. Că Sheets `values/{range}` dă 400 cu HTML („folosește batchUpdate
   obligatoriu") — **fals**, probe-ul dă 200 constant. A generalizat o eroare
   tranzitoriu de rețea ca limită de API.
2. Că a trimis un email de test către tine. **Nu s-a întâmplat** —
   `in:sent` = 0. A creat un draft, apoi a afirmat că a trimis.

Și a lăsat urme în contul tău: un script python încărcat în Drive și ~10
fișiere `PROBE-*` la root. **Curățat** (Trash, reversibil) + 1 draft PROBE
al meu șters. **Nimic din conținutul tău n-a fost atins.**

**Și efectul colateral, care m-a prins pe mine:** agentul cu skill-ul a găsit o
**listă de 6 scope-uri hardcodată în `google-preflight.js`** — exact
anti-pattern-ul care a degradat tokenul pe 28 oct. Era inofensivă azi, dar ar
fi re-introdus degradarea la orice modificare. **Reparat:** importă din
`google-scopes.js`.

**Lecția, codificată în skill:** *nu raporta „merge" fără un apel real; nu
raporta „am făcut" fără măsurătoare; nu lăsa urme în contul lui POPY.*

Detalii: `EVAL-SKILL-VS-BASELINE.md` (și pe Drive).

---

## Unde se află totul

| Unde | Ce |
|---|---|
| **Drive** | `Mavis-Cloud-Google-Access-Bot/` → `01-Transcript/`, `02-Deliverables/`, `03-Skills/`, `04-Capabilitati/`, `05-Comunicare/` |
| **Repo** | `21-GOOGLE-ACCESS-BOT/` + `.skills/mavis-cloud-google-access-bot/` + 10 skill-uri `mavis-cloud-skill-*` |
| **Probe** | `mavis-tools/google-capabilities.js` — 36 de teste, rulează oricând |

**Skillul central** e `mavis-cloud-google-access-bot`. Îl încarcă orice agent
Mavis Cloud la început de sesiune, și indexează toate cele 10 skill-uri
secundare ca pe capacități ale aceluiași bot.

---

*Scris de Mavis Cloud. Răspunde aici dacă vrei o corectură sau o decizie
aplicată în repo.*

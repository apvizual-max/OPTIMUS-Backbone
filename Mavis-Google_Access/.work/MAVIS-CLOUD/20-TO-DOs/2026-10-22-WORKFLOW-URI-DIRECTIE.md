# 03 · Ce workflow-uri vrei pe Gmail și pe Drive

**Data:** 2026-10-22 · **Tip:** strategie · **Perspectivă lipsă:** strategie
**Stare:** ⏳ așteaptă pe tine

---

## Ce am eu acum (măsurat)

| | |
|---|---|
| Gmail | 84.316 mesaje · 78.522 thread-uri · 50 etichete (8 din seria `MAVIS/*`) |
| Drive | 104,07 GB · vault PKMS cu 51.157 fișiere |
| Calendar | 4 calendare |
| Sheets / Slides / Docs | funcționează (Docs via Drive export) |
| Sesiuni paralele | posibile — vezi mai jos |

**Infrastructura e gata. Lipsește direcția: ce să facă workflow-ul cu ea.**

---

## Ce pot construi singur (nu te întreb)

- Citirea și clasificarea automată a mailului (etichete, arhivare, Trash — niciodată ștergere definitivă)
- Extragerea din Drive → Sheets/Docs, cu indexare în `00_INDEX.md`
- Rapoarte zilnice: ce a intrat, ce nu a fost acționat, ce stă pe „de răspuns"
- Legătura Gmail ↔ Drive: un mail → un fișier în vault, cu `00_INDEX.md` actualizat
- Captură de linkuri într-un folder dedicat (via `08_Clippings`)

## Ce nu pot decide singur (de aici e în TO DOs)

| Decizia | De ce e a ta |
|---|---|
| **Ce intră în workflow** — joburi, clienți, colecții, linkuri, facturi | e **scopul**, nu tehnica. Pot construi orice; nu pot alege ce urmărești |
| **Cum se raportează** — zilnic, săptămânal, la eveniment | e ritmul tău de lucru |
| **Ce e urgent vs. ce se adună** | e strategia ta |
| **Ce nu intră deloc în sistem** | e zona privată pe care nu o ating |

---

## Recomandarea mea (intersecția celor trei perspective)

**LOGICĂ:** cel mai mare câșig imediat e **raportul zilnic** — ai deja 3 sesiuni
cron „Raport zilnic" în istoric, dar erau pe tokenul mort.
**RAȚIUNE:** workflow-ul trebuie să scrie în **vault**, nu doar să citească —
altfel e citit și aruncat.
**STRATEGIE:** joburile sunt cea mai mare urgență declarată de tine („să-mi găsesc
un loc de muncă cât mai repede"). Deci **primul workflow = joburi**.

**Așadar: propun să începem cu workflow-ul de joburi** — de la link → `00_Inbox`
→ extras → tabel Sheets → raport. Restul (clienți, colecții) după, în aceeași
schemă.

**Ca să pot construi asta, am nevoie de 3 lucruri de la tine:**

1. **Unde ajung joburile** — un folder nou în Drive, sau în `01_Projects`?
   *(recomand: `01_Projects/01-5-FORGE - AI JOB Automation` — există deja, are 9 fișiere)*
2. **Câmpurile** — ce extragi dintr-un anunț (rol, companie, salariu, remote/BC, stack, link, data)?
   *(recomand: cele din `ALEX-KIT/08-CVURI-NOTARE.md` — verific dacă se potrivesc)*
3. **Cine decide** — eu extrag și tabelez, tu alegi ce aplici. Sau altfel?

---

## Paranteză tehnică — sesiunile paralele

**Da, poți lansa sesiuni paralele** (una pe Drive, una pe Gmail) — cu o singură
regulă:

> **Re-autentificarea e o operație cu un singur scriitor.**
> `prompt=consent` **revocă** refresh token-ul precedent (docs oficiale Google).
> Dacă două sesiuni se re-autentifică simultan, a doua omoară tokenul primei.
> `google-refresh.js` folosește automat `select_account` (non-revoking) când
> tokenul e viu, dar **regula rămâne**: una singură sesiune re-autentifică.

Restul (citire, scriere, workflow-uri) e paralelizabil fără probleme.

---

*2026-10-22 · Mavis Cloud · infrastructura e gata, direcția e a ta*

# Sortarea Gmail cu etichetele MAVIS/* — defect măsurat și nereparat

## CAUZA REALĂ, descoperită 2026-10-25: `()` = ȘI, `{}` = SAU în căutarea Gmail

Filtrele MAVIS/* **nu pot lovi niciun mesaj**, nu doar că nu etichetează.
`from:(jooble bestjobs hipo indeed jobleads linkedin)` cere un expeditor care să
conțină **TOATE** cuvintele simultan. Măsurat live pe API-ul de căutare:

| filtru | cum e scris acum | cu `{}` (30 zile) |
|---|---|---|
| joburi | **0** | 1110 |
| ai si comunitati | 0 | 383 |
| social | 0 | 154 |
| newsletter | 0 | 1284 |
| finante | 0 | 36 |

Testul care l-a dovedit: `from:(jooble bestjobs)` → 0 · `from:{jooble bestjobs}` → 18
· `from:jooble` → 14. **Gmail: paranteze = ȘI, acolade = SAU.** Diferența 0 vs 2967
e exact golul din inbox (~770 mesaje/7 zile, măsurat 25.10).

**Repararea pregătită (25.10):** `mavis-tools/fix-mavis-filters.js` rescrie
`from:(...)`→`from:{...}` ȘI adaugă `addLabelIds` (eticheta rezolvată live din
`labels.list`), cu `--dry-run`, `--rollback` și stare salvată în
`filters-state-before-repair.json`. **Neaplicat** din cloud: tokenul nu are
`gmail.settings.basic` ⇒ `filters PATCH` → 403. Rulează-l pe Local.
TO DO: `20-TO-DOs/2026-10-25-FILTRE-MAVIS-REPARARE.md`.

## Stare (măsurat 2026-10-22 → 2026-10-25)

Ultima etichetare reală: **2026-10-11** (Finante 10-06, De raspuns 10-09, Facturi
10-09) ⇒ **~12 zile fără sortare**. Mail de job nou (Bestjobs 07:49, Jooble
03:55, LinkedIn Job Alerts 03:50) e în continuare **INBOX + UNREAD**.

## Cauza 1 — filtrele nu pun eticheta

Cele 5 filtre server-side au **criteriile corecte**, dar `action` e
`{removeLabelIds:["UNREAD","INBOX"]}` ⇒ `action.addLabelIds` **VID**. Deci mailul
potrivit e arhivat și marcat citit, **dar nu primește eticheta MAVIS/\*.**

Mai mult (măsurat 2026-10-23): **510 mesaje în inbox în 7 zile** (azi 12, 24h 99)
⇒ filtrele nici măcar nu arhivează mailul nou.

**Cauza probabilă:** etichetarea se făcea de un script **local**
(`mavis-tools/email-sort-full.js`, rulează pe calculatorul lui Alex), iar
filtrele din Gmail doar arhivează. Scriptul local nu mai rulează de 12 zile.

## Cauza 2 — nu pot repara filtrele fără re-consimțământ

`filters.list` merge cu scope-ul `gmail.modify`, dar `filters PATCH` →
**HTTP 403 insufficient authentication scopes**: lipsește `gmail.settings.basic`.

Repararea cere **re-consimțământ cu scope-ul adăugat**. Scriptul e gata:
`mavis-tools/fix-mavis-filters.js`, cu rollback în
`filters-state-before-repair.json`.

## Capcana de diagnostic

```
label:"MAVIS/Joburi" after:2026/10/22   → 0
label:"MAVIS/Joburi" newer_than:30d     → 474
label:"MAVIS/Joburi" newer_than:7d      → 0
```

Zero-ul **NU** însemna „eticheta e goală" — însemna „eticheta nu mai primește
nimic de 7 zile". **Verifică mereu cu două ferestre de timp, nu cu una.**

## Ce se cere ca să se repare

1. Re-consimțământ Google cu scope `gmail.settings.basic` adăugat
   (→ vezi topicul `google-cloud-access` pentru fluxul OAuth și regula „7 zile").
2. Rularea lui `mavis-tools/fix-mavis-filters.js` (are rollback).
3. Restartarea scriptului local `mavis-tools/email-sort-full.js` pe calculatorul
   lui Alex — altfel etichetarea nu se face deloc.
4. Verificare: `label:"MAVIS/Joburi" newer_than:7d` > 0 **și**
   `label:"MAVIS/Joburi" newer_than:30d` ≈ similar.

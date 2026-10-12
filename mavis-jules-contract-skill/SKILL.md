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
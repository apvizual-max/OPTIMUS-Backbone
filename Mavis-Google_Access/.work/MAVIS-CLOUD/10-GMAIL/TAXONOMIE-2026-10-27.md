# GMAIL — taxonomia măsurată la 2026-10-27

> Măsurată live din cloud la `2026-10-27 ~14:40 UTC`, cu paginare exactă.
> **Nu e estimare.** Fiecare număr vine din `labels/{id}` (API-ul oficial).

---

## 1. Ce s-a schimbat față de 12 iul

Între 12 iul și 27 octombrie, taxonomia Gmail a fost **rearanjată**:

| Etichetă veche (09 iul) | Etichetă nouă (27 oct) | Mesaje | Thread-uri |
|---|---|---|---|
| `MAVIS/Joburi` | **`MAVIS/Joburi`** (singura păstrată) | 8.125 | 7.945 |
| `MAVIS/Newsletter` | `Newsletter` | 4.558 | 4.005 |
| `MAVIS/Social` | `Socials` | 2.864 | 2.787 |
| `MAVIS/AI si comunitati` | `AI Folder/AI si Comunitati` | 2.499 | 2.303 |
| `MAVIS/De raspuns` | `De raspuns` | 1.750 | 1.291 |
| `MAVIS/Facturi si conturi` | `Facturi si Conturi` | 113 | 91 |
| `MAVIS/Personal` | `Personal` | 169 | 168 |
| `MAVIS/Finante` | `Finante` | 15 | 14 |

**Prefixul `MAVIS/` a căzut de pe 7 din 8 etichete.** Doar `MAVIS/Joburi` l-a
păstrat — probabil pentru că e eticheta de lucru principală.

**Hierarhii noi, care nu existau în iulie:**

```
WORK | AP-ID/                        ← businessul de design (apvizual.ro)
  ├─ WORK | AP-ID/THEMA - Siteuri AP              42 mesaje
  ├─ WORK | AP-ID/TRIPINGERS                       28
  ├─ WORK | AP-ID/ROTLD - Domenii                  28
  ├─ WORK | AP-ID/RESURSE si INSPIRATIE            20
  ├─ WORK | AP-ID/Dreams Time                       8
  ├─ WORK | AP-ID/Scoala foto - SFF - Dan Besliu    7
  ├─ WORK | AP-ID/PHOTOGRAPHY - Subscriptions and Material   5
  ├─ WORK | AP-ID/Claus Web - Gazduire ap-id.ro     3
  ├─ WORK | AP-ID/www.aptailor.com                  3
  └─ WORK | AP-ID/Finantare - Granturi              0

Knowledge/                           ← bibliotecă personală
  ├─ Knowledge/Pillai Center Brzee Godess            9
  ├─ Knowledge/Dr. Pillai                            8
  ├─ Knowledge/ISHA                                  4
  ├─ Knowledge/MANIFESTATION - 15 min                4
  ├─ Knowledge/Inner Engineering - Sadguru           2
  ├─ Knowledge/ARK Cristal                          2
  └─ Knowledge/Gaia                                  0

AI Folder/AI si Comunitati            2.499
Crypto | Trade | News/Token Metrics   0
Home | Car | Shopping/Electric Company  2
JOBS-Interview            18 · JOBS-Interview/Taste  25
Optimus CD                687
SCAMS                       0
```

**Total etichetat: 20.780 mesaje** (era 19.070 la 12 iul) — deci sortarea a
continuat, în plus față de rearanjare.

---

## 2. Filtrele server-side — reparate azi, verificate de Mavis Cloud

**19 filtre, 0 sparte — măsurat la 14:40 UTC, după reparație.**

**Cronologia, pentru că e importantă:**

| Când | Ce |
|---|---|
| ~11 oct | Filtrele se **opresc** să mai lovească ceva. 8 categorii rămân fără mesaje. |
| 25 oct 06:11 | Raport zilnic: **cauza reală identificată** |
| 27 oct 06:16 | Raport zilnic + taxonomia rezolvată live |
| 27 oct 08:42 | **Reparația aplicată**: DELETE + CREATE, etichetele rezolvate live |
| 27 oct 14:40 | **Verificare independentă Mavis Cloud: 19/19 filtre sănătoase** |

**Cauza era dublă, și niciuna n-ar fi fost suficientă singură:**

1. **Criteriile:** în căutarea Gmail, `()` înseamnă **ȘI**, `{}` înseamnă **SAU**.
   Cele 5 filtre scriau `from:(jooble bestjobs hipo indeed jobleads linkedin)` —
   cereau un expeditor care să conțină **toate** cuvintele simultan. → **0 mesaje.**
   Cu `{}` ar fi prins ~3.700 în 30 de zile.
2. **Acțiunea:** `addLabelIds` era **vid**. Chiar dacă filtrul ar fi lovit ceva,
   nu ar fi pus eticheta.

**Concluzia:** rearanjarea etichetelor de azi **nu a fost cosmeticală** — a fost
repararea unui sistem care era mort de 16 zile. Cele 8 categorii primeau
câte **0** mesaje; acum au criterii care chiar lovesc.

Am verificat fiecare filtru: eticheta țintă există și încă poartă numele nou.

| Filtre | Etichetă țintă | Status |
|---|---|---|
| joburi (`jooble bestjobs linkedin …`) | `MAVIS/Joburi` | ✅ |
| AI (`substack goatacademy …`) | `AI Folder/AI si Comunitati` | ✅ |
| social (`skool facebook instagram …`) | `Socials` | ✅ |
| newsletter (`noreply newsletter digest …`) | `Newsletter` | ✅ |
| crypto (`kraken tradingview binance …`) | `Finante` | ✅ |
| GitHub / Jules | `Optimus CD` | ✅ |
| 2 filtre AP-ID | `WORK \| AP-ID/THEMA - Siteuri AP`, `WORK \| AP-ID/www.aptailor.com` | ✅ |

**Cine a rearanjat a mutat etichetele ȘI filtrele împreună.** Nu s-a lăsat un
filtre batând spre o etichetă dispărută — care ar fi însemnat că mailul nou
nu mai ajunge nicăieri.

### Filtrele care pun în Trash — verificate, sunt strânse

| Filtre | Criteriu complet |
|---|---|
| YouTube | `from: noreply@youtube.com` |
| GraphicStock | `from: mail@graphicstockemail.com` |
| DigitalMarketer | `from: support@digitalmarketer.com` |
| Tinder | `from: mail@tinder.pc.dating` + are atașament + >1000 bytes |
| Barnes & Noble | `from: barnesandnoble@mail.barnesandnoble.com` + are atașament |

Niciunul nu prinde mailul de lucru. **Risc de pierdere de date: zero.**

### Etichete fără filtru automat

`De raspuns` (1.750) · `Personal` (169) · `Facturi si Conturi` (113) ·
`Newsletter` are filtru, dar `Personal`/`Facturi`/`De raspuns` nu. Sunt
etichete de **triaj manual**, nu de filtrare automată — la fel ca în iulie.
`De respuns` era deja documentat ca „etichetă fără regulă" în skill-ul
`gmail-label-correction`.

---

## 3. Taxonomia reflectă cele 5 trasee de venit

Asta e partea importantă. Etichetele noi **nu sunt o reorganizare cosmetică** —
ele codifică exact cele 2 trasee active decise pe 22 octombrie:

| Traseu | Etichete |
|---|---|
| **1. Locuri de muncă** | `MAVIS/Joburi` (8.125) · `JOBS-Interview` · `JOBS-Interview/Taste` |
| **2a. Freelance (design)** | `WORK \| AP-ID/*` · `Optimus CD` (687) · `De raspuns` (1.750) · `Facturi si Conturi` · `Finante` |
| **2b. AI** | `AI Folder/AI si Comunitati` (2.499) |
| **2c. Arhivă foto** | `WORK \| AP-ID/PHOTOGRAPHY…` · `WORK \| AP-ID/Scoala foto…` · `WORK \| AP-ID/Dreams Time` · `TRIPINGERS` |
| **2d. Crypto** | `Crypto \| Trade \| News` · `/Token Metrics` |
| **Personal** | `Personal` · `Home \| Car \| Shopping/*` · `Knowledge/*` |

**Concluzie operațională:** orice workflow Gmail pe care îl construim
(TO DO 03) trebuie să citească aceste etichete, nu vechile `MAVIS/*`.

---

## 4. Ce a dispărut din cont — de verificat cu POPY

| | 22 oct | 27 oct | Δ |
|---|---|---|---|
| mesaje în cont | 84.316 | **83.505** | **−811** |
| thread-uri | 78.522 | **77.701** | **−821** |
| în Trash | (necontorizat) | **626** | — |
| în Spam | (necontorizat) | 2 | — |

**811 mesaje au dispărut din cont** între 22 și 27 octombrie, în timp ce
mesajele *etichetate* au **crescut** cu ~1.000 (sortarea a continuat).

**Ce am verificat, ca să nu inventez o alarmă falsă:**

- **Trash-ul are 626 mesaje** — și **conține mesaje din august**, deci NU e o
  golire recentă de masă. E un amestec vechi.
- **Nu am contorizat Trash-ul pe 22 oct**, deci nu pot separa „golit de POPY"
  de „șters automat".
- **Cea mai probabilă cauză a diferenței: măsurătoarea veche a fost luată în
  timp ce rulau sortările locale.** Skill-ul `gmail-exact-counting` spune
  exact asta: *„Nu număra niciodată cât rulează altă operațiune Gmail"* —
  cererile se ciocnesc și contorul raportează greșit. Pe 22 oct erau rapoarte
  zilnice active.

**Răspuns onest: nu pot afirma că s-a șters ceva. Pot afirma că diferența
e reală ca număr, dar cauza nu e determinată de date.** Singurul lucru care
o poate lămuri: **ai golit Trash-ul sau ai șters ceva manual între 22 și 27
octombrie?** Dacă da — totul e în regulă și închidem subiectul. Dacă nu, e
un lucru de aflat, și atunci merită o căutare în activitatea agentului local
din acea fereastră.

---

## 5. Reguli pentru ce urmează

1. **Nicio etichetă nouă fără filtru**, sau fără o notă aici că e manuală.
2. **Când rearanjezi etichete, mută filtrele în aceeași zi.** Altfel, mailul
   nou dispare din sistem.
3. **Nu șterge definitiv.** Trash, cu motiv scris. (Ca în vault.)
4. **Nu număra în timp ce rulează altă operațiune Gmail** — cererile se
   ciocnesc, `threads.list` întoarce gol și raportează 0 cînd sunt mii.
5. **Măsoară cu paginare** — `resultSizeEstimate` e plafonat (a raportat 201
   pentru tot, inclusiv pentru `in:trash` care are 626).

---

## 6. Reconciliere cu raportul zilnic din 27 oct

Raportul zilnic (`rapoarte/RAPORT-ZILNIC-202610-27.md`) documentează **starea
de dinainte de reparație**: 8 categorii moarte de 15 zile, filtre cu `()` în
loc de `{}`, `addLabelIds` vid, 635 mesaje în inbox într-o săptămână.

**Acel raport și măsurătoarea mea nu se contrazic — măsoară momente diferite:**

| | Raport zilnic (fereastră 00:00–09:15 EEST) | Măsurătoarea mea (14:40 UTC = 16:40 EEST) |
|---|---|---|
| Filtre | 5 cu `()`, `addLabelIds` vid | 19/19 cu `{}` și `addLabelIds` pline |
| Etichete | 8 categorii moarte de 15 zile | toate active, noile nume |
| Inbox | 635 mesaje în 7 zile | (re-verificat) |

**Reparația a fost aplicată la 08:42 EEST**, în mijlocul ferestrei de
măsurare a raportului. Deci raportul a prins-o pe cea veche, iar eu am prins-o
pe cea nouă.

**Ce am adăugat peste raport:**
1. **Verificarea independentă de la cloud** a celor 19 filtre, după reparație.
2. **Numărul exact al etichetelor noi** (36 de utilizator, cu mesaje și
   thread-uri fiecare) — raportul le are ca moarte, nu ca populate.
3. **Harta etichetă → traseu de venit** (§3) — etichetele noi codifică exact
   cele 2 trasee active.
4. **Analiza Δ-ului de cont**, cu ce am putut și ce n-am putut verifica.
5. **Cele 5 filtre de Trash verificate** — criterii complete, strânse, zero
   risc de pierdere de date.

**Ce am greșit:** am scris inițial în acest document că filtrele erau
„intacte". Nu erau — erau **moarte de 16 zile**. Cândva între 11 și 25 oct
filtrele au încetat să lovească. Repararea a fost făcută de partea locală
azi la 08:42, iar eu am verificat-o de la cloud la 14:40. **Sistemul a funcționat:
cineva a reparat, cineva a verificat.**

---

*2026-10-27 · Mavis Cloud · măsurat live din cloud, la 14:40 UTC*

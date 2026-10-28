# CONTRACTUL COADEI CLOUD — măsurat pe disc

> **Sursa de adevăr e discul lui Cloud, nu acest document.**
> Acesta e o **copie de lucru**, verificată de `scripts\queue-contract-check.ps1`
> împotriva sursei live, la fiecare rulare. Dacă Cloud își schimbă
> contractul, poarta raportează `CONTRACT_DRIFT=YES` — și atunci *acest*
> document e cel care e depășit, nu poarta.

## Proveniență (măsurată 2026-10-27)

| Sursă | Ce stabilește |
|---|---|
| `cloud-ingest/MAVIS-CLOUD/.skills/mavis-cloud-to-local-reporting/SKILL.md` | cine citește, ce execută, unde livrează |
| `cloud-ingest/MAVIS-CLOUD/QUEUE/TASKS-FOR-CLOUD.md` | formatul exact al unei tichete |
| `cloud-ingest/MAVIS-CLOUD/AGENTS.md` | cine e Cloud și cum împinge |

## Cine consumă

Cloud, la `git pull --rebase origin main`, în **repo-ul propriu**:

```
1. git pull --rebase origin main — mereu primul. TASK-urile vin de aici.
2. Citește QUEUE/TASKS-FOR-CLOUD.md
3. Execută tichetele cu scope: cloud
4. Scrie rezultatul în QUEUE/DONE/<id>.md
5. Marchează [x] în coadă
6. Nu șterge nimic — mută în docs/arhiva/handoffs-vechi/ cu git mv
```

> **SKILL.md, linia 59:** „`QUEUE/TASKS-FOR-CLOUD.md` — singura cale de intrare sigură."

## Format

```
### [id] titlu
cerut de: local | data: YYYY-MM-DD
scope: cloud | local | ambele
ce trebuie: ...
livrare: unde trebuie să ajungă rezultatul
```

## Cele cinci câmpuri obligatorii

| Câmp | Valoare | De ce contează |
|---|---|---|
| `cerut de` | `local` | cine a cerut ticheta |
| `data` | `YYYY-MM-DD` | când, pentru ordine |
| `scope` | `cloud` · `local` · `ambele` | **singurul câmp care decide dacă Cloud execută ticheta** |
| `ce trebuie` | textul cererii | ce are de făcut |
| `livrare` | calea de livrare | unde trebuie să ajungă rezultatul |

**Ticheta fără `scope: cloud` nu e executată.** Nu e „executată mai târziu" —
nu e executată deloc. O coadă plină de tichete fără `scope` e o coadă goală.

## Două reguli pe care le-am măsurat pe noi înșine

1. **O tichetă trunchiată e o instrucțiune trunchiată.** Măsurat 2026-10-27:
   ultima tichetă din coada CI se termina în `Nu intai` — mijloc de
   propoziție — în **ambele** canale, pentru că publisherul a primit un corp
   trunchiat și l-a scris așa, raportând succes. Deci: valoarea lui
   `ce trebuie` trebuie să se termine cu punct, exclam, interrogativ sau
   închidere de paranteză. Altfel e trunchiată.
2. **Ținta de livrare trebuie să existe.** Cloud scrie în `QUEUE/DONE/<id>.md`.
   În repo-ul CI, `QUEUE/DONE/` nu exista — măsurat 2026-10-27.

## Formatul copiei **secundare** (canalul GitHub)

Copia secundară din `QUEUE/TASKS-FOR-CLOUD.md` respectă exact contractul de
mai sus, cu două diferențe oneste, declarate:

- `livrare:` indică `QUEUE/DONE/<id>.md` — ținta din **repo**, nu din Drive.
  În canalul primar (Drive), ținta e `BRIDGE-DRIVE/INTRARI-CLOUD/`.
- `detalii:` păstrează corpul original al tichetei, pentru ca nimic să nu
  se piardă la conversie. Nu e un câmp al contractului; e o notă, citită
  după cele cinci.

Ambele copii poartă **același `TASK_ID`** — asta e regula „același TASK_ID,
două canale", verificată de poartă, nu afirmată într-un document.

## Poarta

```
powershell -NoProfile -File "scripts\queue-contract-check.ps1"
```

| Cod | Sens |
|---|---|
| `0` | măsurat, totul adevărat: tichetele conforme, contractul fără drift |
| `1` | cel puțin o tichetă încalcă contractul, sau contractul a derivat |
| `2` | măsurătoarea e incompletă (contractul live nu e lizibil) — **nu e succes** |

> Codul `2` există pentru un motiv: o poartă care nu poate măsura nu are
> dreptul să spună „e bine". Necunoscutul se raportează, nu se presupune.

---

## Livrarea: unde stă de fapt coada (aditiv, 2026-10-27)

> **Aditiv.** Contractul de mai sus nu se rescrie.

Contractul spune *ce* citește Cloud-ul. Nu spune *de unde* îl ia. Iar
această diferență este chiar defectul:

| | |
|---|---|
| **Formatul** cozii | contractul de mai sus (`## Format`, cele cinci câmpuri) |
| **Locația** cozii | `QUEUE/TASKS-FOR-CLOUD.md` **din repo-ul `MAVIS-CLOUD`** — acolo trage Cloud-ul cu `git pull --rebase origin main` |

Coada din repo-ul **CI** (`MAVIS-OPTIMUS-CI`) este o copie locală de
înregistrare, nu canalul. Măsurat 2026-10-27: 2 tichete în coada locală,
**0** în coada pe care Cloud-ul o citește.

### Cum se livrează

`scripts/queue-deliver.ps1` scrie tichetele în repo-ul Cloud-ului și le
publică. Ordinea: sync → scriere → scanare de secrete → commit → push →
verificare la remote. Detalii: `docs/BRIDGE-LOCAL-CLOUD.md` §11.

### Cum se verifică

`scripts/queue-contract-check.ps1`, proba `DELIVERY`: fiecare `TASK_ID`
local trebuie să fie în coada repo-ului Cloud-ului, citită la vârful
ramurii remote. Fără această probă, poarta raporta sănătate pentru o coadă
pe care nimeni nu o citește — exact ce s-a întâmplat.

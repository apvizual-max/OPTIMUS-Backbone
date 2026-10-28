# REGULILE VAULTULUI — cum lucrez cu PKM-ul din cloud

**Sursa:** `AGENTS.md` și `COTOR.md` din vaultul live
(`GDrive-Second_Brain_PKMS`), citite de Mavis Cloud pe 2026-10-22.
**De ce contează:** din cloud am acces la Drive acum. Orice scriu acolo intră în
sistemul tău real, cu 51.157 de fișiere și oglindă sincronizată.

---

## Cele 8 reguli care nu se încalcă

1. **Nu se șterge nimic.** `rm` și `Remove-Item` sunt blocate. Neclarul ajunge
   în `_QUARANTINE`, cu motiv scris în indexul lui.
2. **Nu se atinge arhiva externă** (`H:\CLAUDE_Archive` și
   `H:\Alex_Knowlege_Vault_BKUP_10-19-2026`). Se citește doar la nevoie.
   **Ea nu mai e reperul** — reperul e oglinda Google Drive Cloud, verificată
   per fișier local↔cloud.
3. **Nu se scrie o cale cu un folder numerotat în mână.** Numerotarea este
   poziție, nu etichetă, și se oprește la al treilea nivel în adâncime.
4. **`00_INDEX.md` nu se editează manual** — se regenerează. Singura excepție:
   rândul `**De ce e aici:**`, scris de om.
5. **Rădăcinile care încep cu `_`** (`_SYSTEM`, `_ARCHIVE`, `_QUARANTINE`) nu
   primesc cod numeric: sublinierea spune deja „sunt sistem, nu conținut".
6. **Zero ștergeri și zero mutări fără R0.** Mutarea conținutului e decizia
   suverană a lui POPY.
7. **Ramura Knights Templar** (cele două directoare identice de 14,09 GB din
   `01_Projects`) rămâne neatinsă până la organizarea manuală de POPY.
8. **Nu se scrie nicio cale de reper în mână, nicăieri.** Calea reală e
   `E:\Google\GDrive\GDrive-Second_Brain_PKMS` și se **descoperă** dinamic
   (`paths.ps1` → `Get-PkmsVault` / `Get-PkmsDriveFsMount`).

## Vocabular — folosit corect

| Cuvânt | Ce înseamnă | Nu e |
|---|---|---|
| **vault** | singurul loc unde se lucrează | — |
| **backup** | arhiva de pe `H:`, **imutabilă**, nu e reperul | nu e raft, nu e reper |
| **oglindă** | perechea local↔cloud a aceluiași fișier | nu e copie locală |
| **bază** | nivelul `00`–`09` (10 baze), neatins | nu e locul de lucru |
| **proiect** | `01_Projects` — singurul nivel în care intri | nu e o bază |
| **raft** | un folder din `01_Projects`, pe un subiect de muncă | — |
| **cotor** | documentația sistemului, tot pe un fir | — |
| **index** | `00_INDEX.md`: ce conține, în cuvinte | — |
| **carantină** | `_QUARANTINE` — nimic nu se șterge | nu e coș de gunoi |

## Ordinea de citit: patru citiri, zero scanări

1. `COTOR.md` — sistemul: ce e, ce nu se atinge, cine scrie ce
2. `MANUAL DE NAVIGARE - cotor.md` — cum cauți
3. `02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_guide\START AICI.md` — harta rafturilor, cifrele de azi
4. `00_INDEX.md` din folderul în care lucrezi

## Scara de căutare

| Situație | Faci | De ce |
|---|---|---|
| Știi calea | deschizi folderul | nu cauți nimic |
| Știi subiectul | cauți în `00_INDEX.md` | sub o secundă |
| Nu știi nici subiectul | `INDEX CENTRAL.md` | tot vaultul, pe un ecran |
| Ai nevoie de cifre vii | `health-check.ps1` | cifrele din rapoartele vechi sunt istorice |

**Interdicție:** nu scanezi niciodată tot arborele ca să găsești un fișier.
Cotorul răspunde în sub o secundă.

## Cum se aplică din cloud

Unelta: `mavis-tools/drive-vault.js` — **read-only**, cu o singură excepție:
`quarantine`, care **mută** (nu șterge) și cere `--confirm` + motiv scris.

```bash
node mavis-tools/drive-vault.js root                    # structura de la rădăcină
node mavis-tools/drive-vault.js ls "01_Projects"        # conținutul unui folder
node mavis-tools/drive-vault.js read "COTOR.md"         # citește un fișier
node mavis-tools/drive-vault.js find "termen"           # caută în 00_INDEX.md
node mavis-tools/drive-vault.js quarantine "<cale>" "<motiv>" --confirm
```

Zonele protejate (refuză automat): `Knights Templar`, `_SYSTEM`, `.obsidian`,
`.trash`, `.vault-intelligence`, `.claudian`, `.neural_memory`, `.wwebjs_cache`.

## Ce NU fac din cloud

- **Nu șterg.** Nimic, niciodată. Nici Trash.
- **Nu mut.** Fără R0 și fără decizia lui POPY.
- **Nu editez `00_INDEX.md`** — se regenerează.
- **Nu ating `.obsidian` / `.trash` / `.vault-intelligence`** și nici ramura
  Knights Templar.
- **Nu scriu căi de reper în mână** — le descoper, ca `drive-vault.js`.
- **Nu ating `H:`** — inaccesibil din cloud prin design.

---

*2026-10-22 · Mavis Cloud · copiat din contractul live al vaultului*

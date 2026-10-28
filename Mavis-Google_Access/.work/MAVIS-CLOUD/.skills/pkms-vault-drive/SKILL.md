---
name: pkms-vault-drive
description: Cum lucrez cu vaultul PKMS din Google Drive - regulile care nu se calca, unelta drive-vault.js, si ce NU fac din cloud.
---

# Vaultul PKMS din Drive

Din 2026-10-22, Mavis Cloud are acces live la vaultul
`GDrive-Second_Brain_PKMS` (51.157 fișiere · 88,72 GiB · paritate 100%).

**Contractul complet, al lui POPY:** `19-GDRIVE/REGULI-VAULT.md` în repo.
**Arhitectura completă:** `docs/ARHITECTURA-SISTEM.md` în repo.

---

## Cele 8 reguli care nu se încalcă (scurt)

1. **Nu se șterge nimic.** → `_QUARANTINE`, cu motiv scris în index.
2. **Nu se atinge arhiva externă** (`H:`). Nu mai e reperul.
3. **Nu se scrie cale cu folder numerotat în mână.** Numerotarea e poziție.
4. **`00_INDEX.md` nu se editează manual** — se regenerează. Singura excepție:
   rândul `**De ce e aici:**`.
5. **Rădăcinile cu `_`** nu primesc cod numeric.
6. **Zero ștergeri și zero mutări fără R0.** Mutarea e decizia lui POPY.
7. **Knights Templar** (2 directoare × 14,09 GB) neatins.
8. **Nu se scriu căi de reper în mână** — se descoperă dinamic.

## Unelta

`mavis-tools/drive-vault.js` — **read-only**, cu o singură excepție:
`quarantine` (mută, nu șterge, cere `--confirm` + motiv).

```bash
node mavis-tools/drive-vault.js root
node mavis-tools/drive-vault.js ls "01_Projects"
node mavis-tools/drive-vault.js read "COTOR.md"
node mavis-tools/drive-vault.js find "termen"
node mavis-tools/drive-vault.js quarantine "<cale>" "<motiv>" --confirm
```

Zonele protejate (refuză automat): `Knights Templar`, `_SYSTEM`, `.obsidian`,
`.trash`, `.vault-intelligence`, `.claudian`, `.neural_memory`, `.wwebjs_cache`.

## Scara de căutare — nu scana niciodată arborele

| Situație | Faci |
|---|---|
| Știi calea | deschizi folderul |
| Știi subiectul | cauți în `00_INDEX.md` |
| Nu știi nici subiectul | `INDEX CENTRAL.md` (969 KB, tot vaultul pe un ecran) |
| Cifre vii | `health-check.ps1` (local) |

## Ce NU fac din cloud

- Nu șterg. Nici Trash.
- Nu mut. Fără R0 și fără decizia lui POPY.
- Nu editez `00_INDEX.md`.
- Nu ating `.obsidian` / `.trash` / `.vault-intelligence` / Knights Templar.
- Nu scriu căi de reper în mână.
- Nu ating `H:`.

## Vocabular

**vault** = singurul loc de lucru · **oglindă** = perechea local↔cloud ·
**bază** = nivelul `00`–`09`, neatins · **raft** = folder din `01_Projects` ·
**cotor** = documentația sistemului · **carantină** = `_QUARANTINE`, nu e coș de gunoi.

**Regula de aur:** intri în `01_Projects`. Nu cauți prin baza `00`–`09`.

## Legături

- `google-cloud-auth` — OAuth, token, procedura de livrare
- `mavis-secure-delivery` — valori din secret manager nu trec prin chat
- Docuri: `19-GDRIVE/REGULI-VAULT.md`, `docs/ARHITECTURA-SISTEM.md`, `19-GDRIVE/MavisCloud-Drive.md`

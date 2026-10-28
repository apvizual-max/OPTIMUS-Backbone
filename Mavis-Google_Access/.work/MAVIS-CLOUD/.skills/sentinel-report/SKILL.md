---
name: sentinel-report
description: Raport de stare complet al proiectului Mavis. Se genereaza la cerere, se arhiveaza cu data, nu se modifica dupa.
---

# Sentinel — raport de stare

Un singur document care cuprinde **tot**: ce e gata, ce nu e, ce e blocat, ce urmează.
Se generează **la cerere**, se salvează cu dată, și **nu se modifică niciodată după**.

## Comanda care îl generează

```bash
python3 mavis-tools/sentinel.py
```

Scrie în `docs/SENTINEL/YYYY-MM-DD-sentinel.md` și pune în `docs/SENTINEL/INDEX.md`
o linie nouă, la început.

## Regi

1. **Fiecare raport e o fotografie, nu o actualizare.** Nu editezi un raport vechi.
   Dacă ceva s-a schimbat, scrii alt raport.
2. **Numerele se numără, nu se estimează.** `resultSizeEstimate` din Gmail nu e
   numărătoare. Dacă nu ai numărat, scrii „necontorizat".
3. **Tot ce e blocat apare pe listă.** Nimic nu rămâne în capul meu.
4. **Dacă ceva nu merge, se spune.** Nu se scoate din raport pentru că deranjează.
5. **Arhivare la 6 luni.** Rapoartele mai vechi de 6 luni se mută în
   `docs/SENTINEL/ARHIVA/`. Un an e și el acceptabil.

## Ce cuprinde obligatoriu

```
1. Stare în 5 rânduri          — unde suntem azi
2. Numerele contorizate        — Gmail, Drive, repo, skill-uri
3. Gata, cu dovezi             — nu doar "funcționează", ci ce l-am verificat
4. Ne făcut, în ordine         — ce urmează, cu urgență
5. BLOCAT explicit             — și de ce
6. Decizii luate, cu motiv      — să nu se re-discute în gol
7. Erori comise și reparate     — ca să nu se repete
8. Ce așteaptă răspuns de la POPY
```

## De ce există

POPY a cerut: „dacă deschid o sesiune zero, cu zero context, zero memorie, absolut
nimic, trebuie să-i dau o singură comandă: du-te la repo și instalează tot."

Raportul e **punctul de pornire**. `SENTINEL-LATEST.md` e un symlink/copie către
cel mai nou, ca un agent nou să știe de unde începe fără să caute prin istoric.

## Legătura cu celelalte documente

| Document | Rol |
|---|---|
| `SENTINEL-LATEST.md` | de aici pornești |
| `docs/SENTINEL/` | istoricul, cu dată |
| `docs/REGISTRUL-EXTERN.md` | ce e luat de pe GitHub/GitLab |
| `docs/PROCES-COMPLET.md` | cum funcționează, nu unde suntem |
| `docs/HANDOFF.md` | A2A și A2U |
| `PROGRES.md` | lista de taskuri din interfață |
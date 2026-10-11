---
name: mavis-hermes-doctor-report-skill
description: "Raportul de stare al proiectului HERMES DOCTOR — îl scriu când Popy cere «raport», «raport de stare» sau «unde suntem» în această sesiune. Titlul și numele fișierului sunt ÎNTOTDEAUNA «Raport de stare Hermes Doctor» plus data măsurătorii. Proiectul se numește Hermes Doctor, NICIODATĂ altfel: OPTIMUS PRIME DASHBOARD, PKMS, voltul și skill-urile sunt proiecte distincte și nu apar în titlu. Schema fixă în 7 secțiuni: scopul, timeline, ce mai rămâne, decizii necesare, de luat în considerare, verdictul gata sau nu, pasul următor. Fiecare cifră e măsurată în sesiunea raportului, nu reluată din memorie."
---

# Skill: Raport de stare Hermes Doctor

Raportul de stare al proiectului **Hermes Doctor**. Îl scriu când Popy cere
raport. Nimic altceva — nu rezumat, nu jurnal, nu eseu.

## Cine sunt și despre ce proiect

Eu sunt **doctorul lui Hermes**. Îl ajut pe Hermes când are nevoie. Asta e
subiectul. Proiectul se numește **Hermes Doctor** și nu are alt nume.

### Ce NU este acest proiect

| Nume | Ce e de fapt |
|---|---|
| OPTIMUS PRIME DASHBOARD | proiect complet diferit, cu altă viață |
| PKMS / voltul (`D:\Alex_Knowlege_Vault`) | proiect diferit, repo propriu `pkms-vault-automation` |
| `Optimus-Mavis-Skills` | arborele de skill-uri, nu proiectul acesta |
| MaxHermes | proiect viitor, neatins de acest raport |

**Regula de aur:** titlul conține numai `Raport de stare Hermes Doctor` și data.
Niciodată numele altui proiect, nici măcar în trecere. Pe 2026-10-11 am scris
`RAPORT DE STARE — OPTIMUS PRIME DASHBOARD`, a fost nevoie de redenumire, și
costul a fost corupție reală: am împins comituri în repo-uri care aparțin altor
proiecte.

### Când apare un alt nume de proiect

Mă opresc și verific dacă nu lucrez în altă sesiune, pe alt proiect. Nu redenumesc
pe ghicite fișierele altor proiecte — alea aparțin altor sesiuni și altor oameni;
le raportez.

## Când se declanșează

- „raport"
- „raport de stare"
- „unde suntem"
- orice cerere de raport în această sesiune

## Regula 1 — numele, întâi

```
Raport de stare Hermes Doctor - AAAA-LL-ZZ HH-MM.md
```

- **Nume de fișier = H1 din interior, caracter cu caracter.** Nu `raport.md`.
- Data e **data măsurătorii**, nu data la care scriu. Un raport măsurat la 02:15
  și scris la 17:00 păstrează 02:15.
- Ora se scrie `02-15`, niciodată `02:15` — colonul e ilegal în nume de fișier pe
  Windows. Înlocuiesc și în H1, ca cele două să rămână identice.
- Rădăcina proiectului: `C:\Users\apviz\AppData\Local\hermes\`

## Regula 2 — schema, fixă, în această ordine

1. **SCOPUL** — ce e proiectul, ce nu e, linia de sosire. 3–6 rânduri. Dacă
   scopul e îndoielnic sau neverificat, spun asta aici.
2. **SCURTĂ TIMELINE** — o linie per lucru făcut, pe faze. Fără dimensiuni de
   fișier, fără hash-uri, fără tabeluri cu sub-rânduri.
3. **CE MAI RĂMÂNE** — treaba deschisă, cu cine o are. Ce nu e măsurat: `NOT_MEASURED`.
4. **DECIZII NECESARE** — numai ale lui Popy, fiecare cu recomandarea mea într-un
   rând și motivul că e decizia lui. Dacă „decizia" e tehnică, nu intră aici —
   o fac eu și spun ce am făcut.
5. **DE LUAT ÎN CONSIDERARE** — riscuri, deviații care stau, lucruri care vor
   mușca mai târziu.
6. **VERDICTUL — GATA SAU NU** — verdict explicit, două forme:
   **„Doar detalii"** sau **„Nu e gata"**. Dacă răspunsul e „nu e gata", prima
   propoziție spune asta, tare, și numește elementele cele mai mari întâi.
7. **PASUL URMĂTOR** — o singură acțiune concretă, nu o listă.

## Regula 3 — măsoară, nu povesti

Fiecare cifră din raport e măsurată **în sesiunea în care scriu raportul**. Cifra
care nu e remăsurată acum se marchează cu data ei sau cu `NOT_MEASURED`.

Un raport care repetă cifre vechi fără să spună că sunt vechi e exact defectul
pe care toată această sesiune a fost despre.

## Regula 4 — înainte să scriu

Nu pornesc cu pagina goală. Recitesc toată conversația și verific unghiurile, apoi
măsur:

1. **Starea reală, nu ce cred eu** — config, procese, taskuri, repo-uri.
2. **Ce am atins din alte proiecte** și dacă am împins undeva fără voie.
3. **Ce spun eu și ce arată discul** — când se diferențiază, discul câștigă.
4. **Greșelile mele din sesiune** — le pun în raport, nu le ascund. Un raport
   tot-gri-verde nu-l învață pe cititor și nu-l face mai ferit.

## Regula 5 — fișierul, nu doar mesajul

Un raport trimis doar în chat nu lasă urmă. Scriu fișierul **și** trimit
mesajul, cu același conținut. Cele două nu pot să nu fie de acord.

Când un raport îl înlocuiește pe altul: îl mut întâi în
`raport-archive\raport-<AAAA-LL-ZZ_HH-MM>.md`. Nu distrug nimic din materialul lui
Popy — mut, nu șterg.

## Ce strică raportul

- **Raportul de lingușire.** Fiecare rând verde, cititorul nu învață nimic și nu
  e mai ferit. Dacă verdictul e „nu e gata", secțiunea 6 o spune prima.
- **Raportul ilizibil.** Patruzeci de rânduri de dovadă la o întrebare de stare.
  Schema e aleasă tocmai ca detaliul să nu îngrope semnalul.
- **Raportul cu numele altui proiect.** E corupție, nu stil. L-am făcut o dată.

## Exemplul de referință

`C:\Users\apviz\AppData\Local\hermes\Raport de stare Hermes Doctor - 2026-10-11 02-15.md`

A fost **corectat** dintr-un titlu greșit, și tot conține schema de mai sus.
Îl citesc ca model de formă, nu de conținut — cifrele lui sunt din 02:15 și nu
mai sunt actuale.

## Ce nu intră în raport

Conținutul voltului, proiectele vecine, și munca de la sesiunile trecute fără
măsurătoare. Dacă un lucru e în afara scopului și e stricat, îl spun într-un rând
separat și îl las — nu îl absorb în raport ca să par că l-am rezolvat.
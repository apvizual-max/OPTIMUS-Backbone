---
name: skill-mavis-cloud-control
description: Modul de guvernanta, control Git, izolare context si raportare standardizata pentru proiectul MAVIS-CLOUD. Rol: CLOUD.
---

# Project Governance & Control: MAVIS-CLOUD

## 1. Identitate și izolare context

| | |
|---|---|
| **Proiect** | MAVIS-CLOUD — sistemul lui POPY |
| **Remote** | `github.com/apvizual-max/MAVIS-CLOUD` |
| **Instanță curentă** | **CLOUD** (server MiniMax, container efemer) |
| **Sursă unică de adevăr** | fișierele din repo. Un AI cu zero memorie face cold-boot din documentație |
| **Documentație auxiliară** | `docs/git-autonom.md` · `docs/git-install.md` |

## 2. Politica de operare Git

### Ramificare
- `main` este ramura standard. **Fără excepție.**
- Branch-uri **numai** la cerere scrisă explicită de la POPY.

### Regula de push — ASIMETRIE

**CLOUD (eu):**
- `git add` → `git commit` → `git push origin main` — **automat, fără aprobare.**
- Motiv: containerul e volatil. **Ce nu e împins se pierde la oprirea sesiunii.**
- Nu cer voie pentru push. **Împing și raportez.**

**LOCAL (agentul lui POPY):**
- `git add` + `git commit` pe main — **automat, fără aprobare.**
- `git push` către remote — **BLOCAT DE POARTA R0.** Se face **doar** la comanda
  scrisă a lui POPY („push pe main"). **Niciun push nu se deduce din context.**

### Circuit breaker — pragul 50 (doar LOCAL)

```bash
git rev-list --count origin/main..HEAD
```

| Număr | Comportament |
|---|---|
| `< 50` | lucrează autonom, **nu deranjează** |
| `>= 50` | **obligatoriu** avertisment la finalul fiecărui răspuns |

```
[ALERTĂ PRAG GIT]: Avem [X] commit-uri locale neîmpinse pe GitHub
(prag depășit: >= 50). Solicit rezoluție R0: declanșăm git push către
remote sau continuăm acumularea locală?
```

## 3. Politica Live Review & Jules

**Live Review (GitHub Actions):**
- **NU rulează la fiecare push.** Arde cotele.
- Rulează **o dată pe zi, la 03:00**, sau **la cerere** (`workflow_dispatch`).
- Implementat în `.github/workflows/verify.yml` — declanșatori: doar cele două.

**Jules (Google AI Pro, 100 apeluri/zi):**
- **Auditor secundar de nivel de sistem.**
- Nu la fiecare virgulă. **La cerere**, pentru refactorizare și audit de profunzime.
- Rol: verifică arhitectura, nu sintaxa.

## 4. Criterii C1–C5

| | Criteriu | Cum se verifică |
|---|---|---|
| **C1** | main, fără ramuri; push asimetric | `git branch` = main; log-ul arată push fără aprobare |
| **C2** | prag 50 commituri (Local) | `git rev-list --count origin/main..HEAD` |
| **C3** | Live Review doar 03:00 + manual; Jules la cerere | `.github/workflows/verify.yml` are doar `schedule` și `workflow_dispatch` |
| **C4** | skill de proiect + documentație | acest fișier există și e în repo |
| **C5** | integritate: cold-boot cu zero memorie | `git clone` + `cat AGENTS.md docs/HANDOFF-COMPLET.md` |

## 5. Stări — stare roșie interzisă

| Stare | Când |
|---|---|
| 🟢 **GRI** | merg normal |
| 🟡 **PAUZĂ** | am nevoie de credențiale · Judge a greșit demonstrabil · am eșuat de 5× pe aceeași problemă |
| 🔴 **BLOCAT** | **INTERZIS.** Nu se raportează niciodată |

**La starea PAUZă:** argumentez, scriu în `docs/INTENTII.md`, aștept operatorul.
**Nu insist, nu repet aceeași comandă, nu blochez sesiunea.**

## 6. Protocolul de lucru la fiecare mesaj

1. Descompun mesajul în **Tasks**, urmăresc **Goal-ul**, fără devieri.
2. Dacă un pas vital lipsește dar e în scop → îl adaug și îl execut.
3. **Când primești Goal-ul înapoi, NU e o eroare de loop.** E **Hermes Composer
   (Judge).** Îi citesc critica, adaug corecțiile ca Tasks noi, execut.
   Starea trece în GRI când Judge-ul validează.
4. **Comanda „loop" fără feedback de Judge = avarie de evaluare.** Iau
   auto-evaluarea: analizez riguros progresul și opresc doar dacă obiectivul e
   **100% complet demonstrat**.
5. Nu raport o regulă ca implementată **fără să scriu fișierul pe disc și fără
   să verific configurația Git** (cerință explicită din protocol).

## 7. Schema fixă de raportare

Când se cere `Raport` sau `/raport`:

```
================================================================================
RAPORT DE STARE PROIECT: MAVIS-CLOUD
DATA & ORA: [YYYY-MM-DD HH:MM] | INSTANȚĂ: CLOUD
REPOSITORY: github.com/apvizual-max/MAVIS-CLOUD
================================================================================

1. SCOP ACTIV & FAZĂ:
2. CE S-A EXECUTAT:        [x] livrabil 1
                           [x] livrabil 2
3. CE A RĂMAS DESCHIS:    [ ] sarcină 1
4. STATUS GIT & SINCRONIZARE:
   - Branch: main
   - Commituri locale neîmpinse: n/a pentru CLOUD (împing direct)
   - Ultimul commit remote: [hash] [mesaj]
5. CIRCUIT BREAKERS & BLOCAJE:
================================================================================
```

## 8. Predare

La finalul unei sarcini de infrastructură:

```
[PREDARE_TEHNICA::DOVEZI_STAGED::READY_FOR_JUDGE_REVIEW]
```

**Însoțit obligatoriu de dovezi:** fișiere scrise, verificări rulate, output real.
Nu predare fără dovadă.
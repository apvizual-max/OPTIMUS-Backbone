# Mavis

Sistemul de lucru al lui Alexandru Popescu (AP-ID).
Tot ce produce Mavis trăiește aici: instrumente, CV-uri, scoruri, skill-uri, planuri.

Nu conține parole, tokenuri sau chei. Acelea stau în managerul de secrete, nu în repo.

## Structura

| Folder | Ce e |
|---|---|
| `ALEX-KIT/` | Motorul de CV-uri și joburi. `scoring.gs`, `cv-mutator.js`, `letter-engine.js` |
| `ALEX-KIT/CV-URI/` | CV-uri gata de trimis (Word, 1 pagină + scrisoare) |
| `ALEX-KIT/TINTE/` | Puncte de plecare în markdown pentru fiecare țintă |
| `ALEX-KIT/SITE-VECHI/` | Versiunile anterioare de site, păstrate ca referință |
| `mavis-tools/` | Scripturile Google, Gmail, Drive. `kit.js` e clientul de bază |
| `.skills/` | Procedurile reutilizabile, învățate din ce a mers |
| `docs/` | Decizii, arhitectură, specificații |
| `18-GOOGLE/` | **Setupul Google** — OAuth, token, proceduri, checklist In production |
| `19-GDRIVE/` | **Operațiunile pe Drive** — vaultul PKMS, regulile lui, unelte |
| `20-TO-DOs/` | **Working folder-ul lui POPY** — taskuri care nu pot fi rezolvate singure |
| `inbox/` | Material care nu încă nu are casă |
| `arhiva/` | Istoric, versiuni vechi |

## Cele două site-uri, și de ce sunt diferite

**B2B** — freelancing. Se vinde *serviciul*. Clientul vine cu o treabă, primește un preț.

**AP-ID Systems** — oferta AI. Se vinde *sistemul*. Clientul pune un agent AI între el și
Mavis, ca furnizor de direcție artistică. Nu se oprește la un proiect: devine un sistem
care se extinde.

Astea nu sunt două versiuni ale aceluiași site. Sunt două oferte, cu doi cumpărători diferiți.
Nu le amesteca fără să știi pentru cine construiești.

## Cum lucrează Mavis aici

Regulile complete sunt în `AGENTS.md` și în `.skills/alex-collaboration-protocol/SKILL.md`.
Scurt:

1. **Nu inventa numere.** Dacă nu poți număra ceva, spune „nu pot număra". Un
   `resultSizeEstimate` din Gmail e plafonat și nu e numărătoare — vezi
   `.skills/gmail-exact-counting/`.
2. **Nu inventa clienți.** Fiecare nume de client trebuie să se regăsească în CV-urile reale.
3. **Niciodată ștergere definitivă.** Trash da, `delete` nu.
4. **Niciodată trimitere automată.** Mavis pregătește fișierele; Alexandru apasă butonul.
5. **Raportează sursa fiecărei cifre.** Log de proces, numărare reală, sau estimare — spune care.
6. **O singură sesiune re-autentifică la un moment dat.** `prompt=consent` revocă
   refresh token-ul precedent — o a doua re-autentificare omoară tokenul celeilalte
   sesiuni. `google-refresh.js` folosește `select_account` când tokenul e viu.
7. **Înainte de orice operație Google într-o sesiune nouă:** `bash mavis-tools/bootstrap.sh`
   (configurează proxy-ul git, clonează repo-ul, dă verdictul pe Drive/Gmail).

## Git

- `main` e sursa. Nimic nu merge în main până când e cerut explicit.
- Un commit = o treabă făcută, descrisă într-o linie.
- `PLAN.md` și `PROGRES.md` se actualizează în același commit ca schimbarea, nu separat.

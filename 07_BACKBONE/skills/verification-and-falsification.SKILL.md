---
name: verification-and-falsification
description: "Disciplina de masurare si de falsificare: cum dovedesti ca un control chiar verifica ceva, cum masuri ca un test chiar poate esua, si de ce o cifra scrisa in memoria ta e o afirmatie, nu o dovada. Se incarca oricand scrii un raport cu cifre, oricand adaugi un test de regresie, oricand schimbi o poarta de securitate, si oricand afirmi ca un sistem este verde. Contine retete reproductibile pentru controale de sensibilitate, probe care nu executa nimic, si corectii care se adauga, nu se sterg."
parent: mavis-autonomous-operator-skill
source_of_truth: SENTINEL_PRIME/07_BACKBONE/skills/
---

# Masurare si falsificare

## 0. Regula care le acopera pe toate

**O cifra pe care ai citit-o din memorie este o afirmatie. O cifra pe care ai
masurat-o este o dovada.** Daca raportul zice "506/0" si tu nu ai rulat suita in
sesiunea asta, atunci raportul e fals, oricat de corect a fost numarul cand l-ai
scris prima data.

Asta nu e teorie. In sesiunea din 2026-10-11 am raportat `506/0/0` in timp ce
suita era **504/2, exit 1**. Verificatorul independent a gasit acelasi lucru, pe
alt drum. Cauza nu era un defect de cod: un singur artefact imbatranit, la 26 de
ore peste o limita de 24. Remedierea era scrisa chiar in campul `evidence` al
verificarii: "re-run mcp_handshake.py".

**Cine are dreptate cand o cifra e scrisa in fisier si nu e masurata acum?** Nici
una. Fisierele mentin, ca sa nu se piarda faptul, dar nu au voie sa se
inlocuiasca masurarea.

## 1. Un control care nu poate esua nu e control

Orice poarta de securitate sau orice verificare de stare trebuie sa aiba un
**control de sensibilitate**: acelasi lucru, cu o singura variabila schimbata,
unde **trebuie** sa esueze.

### Cele trei forme de control, si de ce primele doua nu merg

| Forma | Ce inseamna | De ce nu e suficient |
|---|---|---|
| v1: scrii un fisier modificat | scrii o copie cu poarta stricata | **Fisierul nu e executat.** Nimic nu dovedeste ca calea modificata e cea care ruleaza |
| v2: pornesti o a doua instanta pe alt port | serverul neutru | functioneaza uneori, dar procesul **nu leaga portul** si fiecare probe primeste "no connection" — controlezi un port mort |
| v3: **invariant static, neutralizat in memorie** | preiei starea reala din cod, rulezi acelasi predicat peste ea, si peste aceeasi stare cu poarta neutralizata | **functioneaza** |

Forma v3 e cea care s-a folosit si a rezistat. Pentru poarta de pe ruta statica:

```
gate_is_literal: fiecare Join-Path sub $ROOT primeste $key (literal din tabel)
control_discriminates: acelasi predicat, dar cu Join-Path-ul primind $rel — trebuie SA ESUEZE
```

### Reguli practice

- **Controlul trebuie sa fie atasat la ceea ce atacă.** Un control care nu poate
  bloca nu masoara nimic; cere ca numarul de blocari sa **scada**, nu sa ramana
  egal.
- **Inversarea sensului conteaza.** Daca poarta blocheaza ceea ce **nu** e in
  tabel, atunci neutralizarea prin golirea tabelului o face sa blocheze **mai
  mult**. Neutralizarea corecta e **largirea** tabelului, ca sa admita tot.
  (Am construit controlul gresit prima data, in sensul invers.)
- **Un control care raporteaza FAIL cand nu are voie este corect.** Daca
  controlul tau esueaza, inseamna ca starea reala s-a schimbat sub picioarele
  tale. Asta e informatie, nu un accident.
- **Testul trebuie sa poata distinge.** Un test care trece pentru ca
  verificarea nu s-a executat niciodata e un test care nu verifica nimic.

## 2. Probe care nu executa nimic

Cand vrei sa dovedesti ca o poarta blocheaza, **nu folosi o actiune reala ca
sonda**. Probe-ul trebuie sa aiba doua iesiri distincte, ca sa poti spune
*unde* a fost blocat:

| Raspuns | Ce insemna |
|---|---|
| **403** | poarta a interceptat — nimic nu a fost executat |
| **400** | cererea a ajuns in stratul de actiuni si a fost refuzata acolo |

Sonda: un id de actiune care **nu exista**. 403 = poarta a functionat, 400 = a
trecut de poarta. Probe-ul nu are efect lateral, deci il poti repeta oricand.

La fel: pentru un traseu de fisiere, afirma pe **continut**, nu pe status.
HttpListener raspunde 400 sau 403 la unele forme *inainte* de ca ruta sa fie
atinsa, deci statusul nu dovedeste nimic despre poarta.

## 3. O poarta se probeaza cu o singura variabila schimbata

Doua probe care difera doar prin valoarea `Origin` — unul primeste 400, celalalt
403 — demonstreaza ca poarta e cea care decide. Daca difera si culoarea, si
endpointul, si corpul, nu ai demonstrat nimic.

La fel, **nu schimba doua lucruri intre o observatie care esueaza si una care
merge.** Daca ai schimbat calea octetilor *si* formatul fisierului, nu poti
atribui castigul. Am facut exact asta: am schimbat corectia de octeti si am
trecut de la WOFF2 la TTF, si am atribuit victoria ultimei schimbari. Al treilea
candidat, pe care nu l-am testat niciodata, era un `Cache-Control: immutable` de
un an pus pe un corp corupt — browserul tinea in cache un font corupt.

**Atribuirea e posibila doar cu o variabila.**

## 4. Corectiile se adauga, nu se sterg

Cand o afirmatie scrisa de tine se dovedeste falsa, **textul fals ramane
vizibil deasupra corectiei, marcat ca fals**. Nu il editezi in loc: cine citeste
mainut inainte si nu stie ca s-a corectat primeste o citire complet gresita.

Formatul care s-a folosit:

```
# CORRECTED <data> de un verificator independent.
# Textul de mai jos a fost al meu si era fals. Se pastreaza, nu se sterge:
#   "<textul fals>"
# Masurat pe aceasta masina:
#   <masurarea>
```

Adauga si in raportul de stare, si in fisierul de istoric al proiectului
(`EVOLUTION.md`), si in motivul de carantina. Un loc nu e suficient: cititorii
vin din locuri diferite.

## 5. Sabotajul care nu produce eroare nu dovedeste lipsa erorii

Un test care strica ceva si totusi nu arunca nicio eroare **nu iti spune ca
nu exista erori**. Spune ca testul tau nu cauta in locul potrivit.

Conditiile pentru un test de falsificare valid:

1. numara **dupa marker semantic**, nu dupa un substring (regexul meu s-a
   potrivit pe `if (!` cu spatiu, codul scria `if(!tBox || ...)` — si am raportat
   "0 garzii" cand erau **24**);
2. apeleaza **calea de randare reala** a aplicatiei, nu o functie izolata;
3. are **trei conditii**: sabotajul produce un simptom masurabil, testul il
   detecta, iar un control confirma ca testul **poate** esua.

## 6. Falsificarile de memorie si de tipar

- `ContainsKey` pe un hashtable PowerShell: **case-insensibil**. Probe-ul meu
  dadea `False` din cauza slash-ului de la inceput — o variabila pe care nu am
  variat-o niciodata. Verifica masurand, nu citind un tabel mental despre
  PowerShell.
- `[uri]` normalizeaza segmentele `..` **inainte** de ca ruta sa le vada. Un
  `switch` in PowerShell e case-insensibil. Un `Get-Content -Raw` mangledeaza
  liniile cu em-dash. `[regex]::ReadAllText` nu exista — e `[IO.File]::ReadAllText`.
- Git scrie progresul pe **stderr** si arunca o eroare rosie chiar la push
  reusit. Verificarea de push e `git ls-remote`, nu exit code-ul.
- **Un pipeline gol masurat cu `Measure-Object -Line` numara 1, nu 0.** Cand
  comanda nu returneaza nimic, PowerShell ii pasa un sir gol, iar
  `Measure-Object -Line` raporteaza o linie. Un arbore curat se masura astfel
  "dirty=1". Filtreaza sirurile goale inainte de numarat si verifica **ce
  inseamna** numarul inainte sa-l folosesti intr-o afirmatie.

## 7. Ce scrie Popy cand cere "raport"

Formatul fix e in skill-ul `popy-project-status-report`. Acolo se cere si
**starea Git/GitHub** — nu era in raport si a fost o lipsa reala.

## 8. O limita fara scriitor in spatele ei: masurati cine scrie, inainte sa schimbati limita

Cand o verificare de stare cade in rosu, exista doua interpretari posibile, si
ele cer **actiuni opuse**:

| Interpretare | Actiunea corecta |
|---|---|
| artefactul e stricat | repara scriitorul |
| **nu exista scriitor** (nimic nu scrie artefactul) | **adauga scriitorul** pe bucla de refresh |

A treia interpretare, cea care trage inspre "hai sa largim limita", **ascunde
defectul** in loc sa-l rezolve. E alegerea prin care un sistem de sanatate
invata sa minta.

**Cum masuri cine scrie** - trei pasi, fiecare cu un semne distinct:

1. **Fereastra de scriere.** Compara mtime-urile artefactelor: un scriitor cu
   ceas lasa o fereastra regulata; un scriitor la cerere lasa o fereastra
   stransa, coincidenta cu evenimentul care l-a declansat.
2. **Re-masurare peste mai multe cicluri.** Masoara din nou peste cel putin un
   ciclu complet al refresh-ului. Daca varsta creste in ritm constant, nimeni
   nu scrie.
3. **Codul.** Gaseste scrierile reale si verifica daca sunt apelate din bucla
   de refresh.

**Succes masurat, 2026-10-28.** `mcp_handshake.json` avea o limita de 24 de ore
si **nu era scris de nimic** intre doua rulari de suita: era un termen pe care
doar un om il putea onora. Scriitorul a fost mutat pe bucla de refresh, cu
cadenta **calculata** din perioada de refresh (nu codificata), si o data la
pornirea worker-ului. Limita a ramas neatinsa. Verificat end-to-end: logul
worker-ului spune cadenta, mtime-ul artefactului e mai nou decat ciclul, iar
verificarea live raporteaza OK cu varsta in evidenta.

**Cazul opus, masurat in aceeasi sesiune.** Familia `log_*` si
`workflow_state_fresh` sunt scrise **la cerere** (de suita de test si de
actiunile operatorului), nu de o bucla cu ceas. Aici **limita se pastreaza**:
un STALE inseamna "nu s-a cerut nimic de el", nu "e stricat". Largirea limitei
ar face antetul verde, adica ar ascunde exact lucrul pe care sistemul trebuie
sa-l spuna. Inainte de a schimba o limita, **cauta in documentele proiectului**
daca verificarea e deja ratificata: in SENTINEL_PRIME, `14_HANDOFF/02_GAPS.md`
si `11_PLANS/POST_R0_EXECUTION_RECORD.md` spuneau explicit ca STALE pe un
artefact scris la cerere e comportament corect ("the check working, not a
fault"). Le-am citit **inainte** de a schimba ceva, si decizia s-a intors.

**Greseli de repetat.**
- Nu largesti o limita ca sa repari un semnal de staleness. Mai intai masura cine
  scrie.
- Nu confunda "nimeni nu scrie" cu "e stricat": primul cere un scriitor nou,
  al doilea cere scriitorul reparat.
- Nu schimba semantica unei verificari fara sa cauti in documentele proiectului
  daca e deja ratificata.

## 9. Legaturi

- `sentinel-cd-pipeline-sync.SKILL.md` — sincronizarea cu pipeline-ul
- `command-center.SKILL.md` — sistemul in care se aplica toate astea
- `mavis-autonomous-operator-skill` — modul general de lucru

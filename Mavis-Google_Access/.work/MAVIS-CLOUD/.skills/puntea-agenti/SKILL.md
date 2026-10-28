---
name: puntea-agenti
description: Cum comunica Mavis din cloud cu agentul local al lui POPY, prin repo. Puntea e repo-ul, nu o conversatie.
---

# Puntea între agenți · Mavis Cloud ↔ Mavis Local

Mavis (cloud) și agentul local al lui POPY nu pot conversa direct.
**Repo-ul e puntea.** Tot ce unul scrie, celălalt îl citește.

## Cum funcționează

```
Mavis (cloud)                    Agentul local (POPY)
     ↓                                    ↓
  scrie în repo  ──────────────→  git pull → citește → lucrează
     ↑                                    ↓
  git pull    ←──────────────   scrie → commit → push
```

## Comanda unică de pornire

Oricine, oricând, cu zero memorie:

```
Du-te la repo-ul apvizual-max/Mavis, citește docs/SENTINEL-LATEST.md,
apoi AGENTS.md, apoi docs/HANDOFF.md. Instalează ce ai nevoie și continuă de acolo.
```

**Trei fișiere, în ordine: unde suntem → cum lucrez → predarea.**

## Cine scrie unde

| Fișier | Scris de | Citit de |
|---|---|---|
| `docs/SENTINEL-LATEST.md` | Mavis | agentul local, la pornire |
| `docs/SENTINEL/` | Mavis, cu dată | oricine, istoric |
| `PROGRES.md` | Mavis | ambii |
| `docs/REGISTRUL-EXTERN.md` | Mavis | ambii |
| `docs/HANDOFF.md` | Mavis | agentul local |
| `docs/INTENTII.md` | agentul local → Mavis | Mavis |

## `docs/INTENTII.md` — canalul de la om spre cloud

Fișierul prin care POPY îi spune agentului local ce vrea de la cloud.
Stă în repo, agentul local îl citește, face ce poate, și notează ce a făcut.

```markdown
## [data] cerință
- ce vreau
- ce a răspuns Mavis
```

## Regula de conflict

**Un singur agent scrie în același fișier, la un moment dat.**
Dacă ambii modifică `PROGRES.md`, se pierd editările.

Soluția: agentul local lucrează pe **ramură**, face PR, Mavis face merge.
Nu se editează `main` direct din două locuri.

## Regula de aur

**Nicio componentă nouă nu se consideră făcută până nu apare în Registrul extern
și într-un Sentinel.** Altfel rămâne în capul unui singur agent și se pierde.

## Cum face agentul local să tragă automat

**Nu poate singur.** Un agent nu rulează în buclă fără un programator care îl pornească
o dată. Necesită **un singur fișier** pe calculatorul lui, pornit o dată.

```
mavis-local.sh          # scriptul de pornire
├── git pull            # ia ce a scris Mavis Cloud
├── citește docs/INTENTII.md
├── face ce poate
└── git push             # scrie înapoi
```

Lansat cu `nohup` sau într-un terminal dedicat, merge singur. **Asta e tot.**
POPY nu are nevoie să știe git — doar să aibă scriptul și să-l pornească o dată.

## Cine construiește ce

| Mavis Cloud | Mavis Local |
|---|---|
| site-uri, CV-uri, scoring | deployment local |
| sortarea Gmail | YouTube |
| log, panou, documentație | fișiere care nu ies de pe mașina lui |

**Nu construiesc puntea.** Construiesc partea de cloud și las schema pe hârtie
clara, ca el să nu depindă de o decizie a mea.

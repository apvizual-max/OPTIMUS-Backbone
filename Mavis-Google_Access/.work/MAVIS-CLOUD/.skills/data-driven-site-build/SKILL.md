---
name: data-driven-site-build
description: Cum se construieste un site de CV cu un singur template si multe variante. Date separate de UI, generate la build.
---

# Site cu strat de date

## Ideea

Un singur `schelet.css`, un singur `build.py`, **multe fișiere JSON**. Fiecare rol e un
JSON. UI-ul nu se atinge niciodată.

```
SITE/
├── date/graphic-designer.json   ← singurul lucru pe care îl schimbi
├── date/art-director.json       ← când ajungi la nivelul 2
├── css/schelet.css              ← nu se atinge
├── build.py                     ← JSON intră, HTML iese
└── dist/                        ← generat, nu se versionează
```

## Comanda

```bash
python3 SITE/build.py graphic-designer
```

## Ce se câștigă

Adăugarea unui rol nou **nu înseamnă scriere de HTML**. Înseamnă un JSON. Asta face
posibil să ai 9 site-uri pentru 9 CV-uri fără să întreții vreodată 9 layout-uri.

## De ce asta și nu WordPress / generator static

- **Zero dependențe** — un fișier HTML, un fișier CSS, embedded
- **Deploy instant** — se urcă oriunde, funcționează și cu `file://`
- **Fără build step la deschidere** — nu trebuie Node, Python, sau server
- **Dif-abil** — două JSON-uri diferite, același HTML, comparație imediată

## Ce a funcționat vizual, verificat pe ecran

- fundal cu textură (`feTurbulence` la 3.5% opacitate) — adâncime fără zgomot vizual
- **două aure colorate** care plutesc în fundal (`drift` 26s) — viața fără conținut
- **gradație pe titlu** (`linear-gradient` + `background-clip:text`) — nu culoare plată
- **lumina urmărește cursorul** pe carduri, viazualizator CSS `--x/--y`
- tab-uri cu `backdrop-filter: blur(14px)` — bară vie, nu plată
- `prefers-reduced-motion` respectat **în toate cele trei** locuri care animă

## Reguli care nu se negociază

1. `prefers-reduced-motion` — cine are vertij nu trebuie să suporte drift
2. Fără tabele — se rup pe mobil
3. Contrast minim 4.5:1 pentru text mic
4. Text alternativ real pe fiecare imagine
5. `overflow-x: hidden` pe body — altfel aura iese din viewport și apare scroll orizontal
6. `100vh` pe mobil — problema cunoscută, vezi skill-ul `mobile-native` din vendor

## Ce urmează după

- nivelul 2: B2B / freelancing, cu rate
- nivelul 3: AP-ID Systems — agent AI între client și POPY
- site de agenție care le cuprinde pe primele două

Toate trei se construiesc **din același schelet**, cu JSON-uri diferite.

## Verificare înainte de commit

```bash
python3 SITE/build.py graphic-designer
node --check ALEX-KIT/cv-mutator.js
```

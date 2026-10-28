#!/usr/bin/env python3
"""Genereaza un Priming KIT in fiecare folder de capitol.

    python3 mavis-tools/priming-kit.py

Un agent nou, cu 0 memorie si 0 context, primeste folderul si stie tot.
"""
import os, datetime, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AZI  = datetime.date.today().isoformat()

# folder -> (titlu, subiect, notebook_name)
CAPITOLE = {
 '10-GMAIL':       ('Gmail',        'Email, sortare, etichete, spam, cote',            None),
 '11-JULES':       ('Jules',        'Agent de audit de la Google, pe GitHub',          'MavisCloud-Jules'),
 '12-LIVEREVIEW':  ('Live Review',  'Code review automat pe GitHub',                  None),
 '13-NOTEBOOKLM':  ('NotebookLM',   'Cercetare cu citari, pe documente reale',         'MavisCloud-NotebookLM'),
 '14-LINKEDIN':    ('LinkedIn',     'Profil, reputatie, prezenta profesionala',         None),
 '07-SITEURI-NIVEL1': ('Site-uri Nivel 1', 'Site de prezentare, unul per rol de CV',   'MavisCloud-SitePrezentare'),
 '15-SITE-B2B':    ('B2B / freelancing', 'Serviciu cu rata si pe ora',               'MavisCloud-B2B'),
 '16-SITE-SYSTEMS':('AP-ID Systems','Agent AI intre client si POPY',                   'MavisCloud-APIDSystems'),
 '17-SKILLS':      ('Skills',       'Dezvoltare si management de skill-uri',           None),
 '18-GOOGLE':      ('Google Workspace', 'Drive, Sheets, Docs, Calendar',               None),
 'ALEX-KIT':       ('ALEX-KIT',     'Motorul de CV-uri, scoring, sabloane',            None),
}

def git_state():
    def sh(args):
        return subprocess.run(args, shell=False, cwd=REPO, capture_output=True,
                              text=True, timeout=20).stdout.strip()
    return sh(['git', 'rev-list', '--count', 'HEAD']), sh(['git', 'log', '--oneline', '-1']), sh(['git', 'remote', 'get-url', 'origin'])

def _write_readme(d, titlu, subiect, notebook, commits, last, remote, AZI):
    open(os.path.join(d, 'README.md'), 'w', encoding='utf-8').write(f"""# {titlu} — Priming KIT

**Creat:** {AZI} · **Repo:** `{remote}` · **{commits} commituri**
**Ultimul commit:** `{last}`

## Ce e capitolul

{subiect}

## Ce conține

| Fișier | Ce dă |
|---|---|
| `SKILL.md` | skill-ul de control al capitolului |
| `HANDOFF.md` | predare completă, pentru agent cu zero memorie |
| `PROMPT-START.txt` | textul de trimis la începutul sesiunii noi |
| `STATUS.md` | starea curentă, pe scurt |

## Regula

> **Niciun agent nu începe acest capitol cu memorie goală și fără context.**
> Se citește acest folder, apoi se lucrează.

{'**Notebook:** `' + notebook + '`' if notebook else '**Fără notebook** — capitol fără componentă NotebookLM.'}
""")

def _write_skill(d, folder, titlu, subiect):
    open(os.path.join(d, 'SKILL.md'), 'w', encoding='utf-8').write(f"""---
name: {folder.lower()}-priming-kit
description: Priming KIT pentru capitolul {titlu}. Îl citești primul, înainte de orice lucru la acest subiect.
---

# {titlu} — Priming KIT

**Subiect:** {subiect}

## Ordine de citire

1. `README.md` — ce e, unde sunt datele
2. `STATUS.md` — unde a rămas
3. `HANDOFF.md` — predarea completă
4. restul fișierelor din folderul părinte

## Reguli care nu se încalcă

- **Nu inventa.** Dacă nu e în surse, spune că nu e. Lasă gol, nu umple cu memorie.
- **Nu șterge definitiv.** Trash da, `delete` nu.
- **Nu trimite nimic** în numele lui POPY.
- **Nu cere ce poți verifica singur.** Verifici și raportezi.
- **`main`, fără ramuri**, dacă POPY nu cere altfel.
- **Totul în repo**, automat.
""")

def _write_handoff(d, folder, titlu, subiect, remote):
    open(os.path.join(d, 'HANDOFF.md'), 'w', encoding='utf-8').write(f"""# HANDOFF — {titlu}

## 1. Cine ești

**Mavis Cloud** — server MiniMax, container izolat.
Fără acces la discul lui POPY. Fără browser. Rulezi taskuri lungi.

## 2. Subiectul tău acum

{subiect}

## 3. Ce e deja

Vezi `STATUS.md` din acest folder și folderul părinte
`{folder}/`.

## 4. Datele lui POPY

```
Nume:    Alexandru Popescu (POPY)
Email:   apvizual@gmail.com      ← verificat în 17 surse
Telefon: +40722121752
Oraș:    București, România
Site:    ap-id.ro
Design:  20+ ani · Art direction 15 · AI 4 · foto/video/UX câte 5
```

## 5. Ce nu poți face

- nu editezi fișiere de pe calculatorul lui
- nu apeși butoane într-o interfață care nu există
- nu faci deploy fără cerere (creează site nou de fiecare dată)

## 6. Ce faci

- culegi, compari, sintetizezi
- pregătești date, documente, conținut
- împingi pe `main` fără aprobare
- tot ce iese ajunge în repo

## 7. Prima sarcină la începutul sesiunii

```
git clone {remote}
cd MAVIS-CLOUD
cat AGENTS.md
ls {folder}/
cat {folder}/*Priming*/README.md {folder}/*Priming*/STATUS.md {folder}/*Priming*/HANDOFF.md
```

**Apoi întreabă ce nu e clar.** Nu presupune.
""")

def _write_prompt_start(d, folder, titlu, last, remote):
    open(os.path.join(d, 'PROMPT-START.txt'), 'w', encoding='utf-8').write(
f"""PROMPT DE START — trimite asta într-o sesiție nouă, pe capitolul {titlu}:

────────────────────────────────────────────────────────────
Continui proiectul MAVIS-CLOUD, capitolul {titlu}.

Repo: {remote}
Ultimul commit cunoscut: {last}

Fă asta, în ordine:
1. git clone {remote} && cd MAVIS-CLOUD
2. Citește AGENTS.md
3. Citește folderul {folder}/ și tot {folder}/*Priming*/
4. Rezumă în 5 rânduri: unde suntem, ce e gata, ce lipsește, ce e blocat
5. Așteaptă instrucțiunea mea. NU construiește nimic înainte să știi
   exact ce vreau, și NU inventa date care nu sunt în repo.

Reguli care nu se încalcă:
- nu inventa, lasă gol dacă nu știi
- nu șterge definitiv
- nu trimite nimic în numele meu
- main, fără ramuri, dacă nu cer altfel
────────────────────────────────────────────────────────────

Voi completa după ce îmi spui ce vreau.
""")

def _write_status(d, folder, titlu, notebook, commits, remote, AZI):
    open(os.path.join(d, 'STATUS.md'), 'w', encoding='utf-8').write(f"""# STATUS — {titlu}

**Creat:** {AZI} · **Repo:** `{remote}` · **{commits} commituri**

## Stare

| Ce | Stare |
|---|---|
| Capitol documentat | ✅ |
| Priming KIT creat | ✅ |
| Skill de control | ✅ `.skills/{folder.lower()}/` |
| Predare completă | ✅ `HANDOFF.md` în acest folder |
| Prompt de start | ✅ `PROMPT-START.txt` |

## Ce urmează

Citit în `../` folderul părinte — acolo e documentația completă a
capitolului: ce am discutat, ce am stabilit, ce am implementat.

## Regula de naming

{'Notebook: `' + notebook + '`' if notebook else 'Fără notebook pentru acest capitol.'}
Notebook-urile create de Mavis Cloud se numesc obligatoriu
`MavisCloud-(subiect)`.
""")

def scrie(folder, titlu, subiect, notebook, commits, last, remote):
    d = os.path.join(REPO, folder, folder.split('-')[-1] + ' Priming KIT'
                     if False else folder.split('-', 1)[-1].replace('SITEURI-', '').title() + ' Priming KIT')
    os.makedirs(d, exist_ok=True)

    _write_readme(d, titlu, subiect, notebook, commits, last, remote, AZI)
    _write_skill(d, folder, titlu, subiect)
    _write_handoff(d, folder, titlu, subiect, remote)
    _write_prompt_start(d, folder, titlu, last, remote)
    _write_status(d, folder, titlu, notebook, commits, remote, AZI)

    return d

if __name__ == '__main__':
    commits, last, remote = git_state()
    n = 0
    for folder, (titlu, subiect, notebook) in CAPITOLE.items():
        if not os.path.isdir(os.path.join(REPO, folder)):
            os.makedirs(os.path.join(REPO, folder), exist_ok=True)
        d = scrie(folder, titlu, subiect, notebook, commits, last, remote)
        print('  %-20s → %s' % (folder, os.path.relpath(d, REPO)))
        n += 1
    print('\n%d Priming KIT-uri create' % n)

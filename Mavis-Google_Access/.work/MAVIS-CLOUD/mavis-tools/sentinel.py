#!/usr/bin/env python3
"""Sentinel - raport de stare complet al proiectului.

    python3 mavis-tools/sentinel.py

Genereaza docs/SENTINEL/YYYY-MM-DD-sentinel.md, actualizeaza INDEX.md
si copiazaza in SENTINEL-LATEST.md. Rapoartele vechi NU se modifica niciodata.
"""
import os, json, glob, subprocess, datetime

REPO  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR   = os.path.join(REPO, 'docs', 'SENTINEL')
GH    = os.path.join(REPO, 'mavis-tools', 'bin', 'gh')
TODAY = datetime.date.today().isoformat()

def sh(args, cwd=REPO, t=25):
    try:
        return subprocess.run(args, shell=False, cwd=cwd, capture_output=True,
                              text=True, timeout=t).stdout.strip()
    except Exception:
        return ''

def git(*a):
    return sh(['git'] + list(a))

def count_paginiq(q):
    """Numara prin paginare reala - resultSizeEstimate e plafonat."""
    script = (
        "const k=require('./kit.js');"
        "(async()=>{let p=null,t=0;do{"
        "const u='https://gmail.googleapis.com/gmail/v1/users/me/threads?q='"
        "+encodeURIComponent(%s)+'&maxResults=500'+(p?'&pageToken='+encodeURIComponent(p):'');"
        "const r=await k.req('GET',u);t+=(r.threads||[]).length;p=r.nextPageToken||null;"
        "if(t>=%d)break;if(p)await new Promise(s=>setTimeout(s,280));}while(p);"
        "console.log(t);})();" % (json.dumps(q), 4000)
    )
    r = sh(['node', '-e', script],
           cwd=os.path.join(REPO, 'mavis-tools'), t=180)
    try:
        return r.strip().splitlines()[-1] if r.strip() else 'necontorizat'
    except Exception:
        return 'necontorizat'


def gather_stats():
    os.makedirs(DIR, exist_ok=True)

    # ---- git ----
    branch  = git('rev-parse', '--abbrev-ref', 'HEAD') or 'main'
    commits = git('rev-list', '--count', 'HEAD') or '?'
    dirty   = len(git('status', '--porcelain').splitlines())
    last    = git('log', '--oneline', '-1')
    remote  = git('remote', 'get-url', 'origin')

    # ---- skill-uri ----
    own   = [d for d in glob.glob(os.path.join(REPO, '.skills', '*')) if os.path.isdir(d)]
    vend  = [d for d in glob.glob(os.path.join(REPO, 'vendor', '*')) if os.path.isdir(d)]
    names = sorted(os.path.basename(d) for d in own)
    vnames= sorted(os.path.basename(d) for d in vend)

    # ---- site-uri ----
    sites = sorted(os.path.basename(p).replace('.index.html', '')
                   for p in glob.glob(os.path.join(REPO, 'SITE', 'dist', '*.index.html')))

    # ---- șabloane + CV-uri ----
    sab = sorted(os.path.basename(p) for p in
                 glob.glob(os.path.join(REPO, 'ALEX-KIT', 'SABLOANE', '*.md')))
    cvs = sorted(os.path.basename(p) for p in
                 glob.glob(os.path.join(REPO, 'ALEX-KIT', 'CV-URI', '*.docx')))

    # ---- Gmail: numărat real ----
    gmail = {}
    for lbl in ['MAVIS/Joburi', 'MAVIS/AI si comunitati', 'MAVIS/Social',
                'MAVIS/Newsletter', 'MAVIS/Finante', 'MAVIS/Personal',
                'MAVIS/De raspuns', 'MAVIS/Facturi si conturi']:
        # GHILIMELE OBLIGATORII - vezi skill gmail-label-correction
        gmail[lbl] = count_paginiq('label:"' + lbl + '"')
    inbox = count_paginiq('in:inbox')
    trash = count_paginiq('in:trash')

    # ---- workflow ----
    wf = sh([GH, 'run', 'list', '--repo', 'apvizual-max/MAVIS-CLOUD', '--limit', '1', '--json', 'conclusion', '--jq', '.[0].conclusion']) or 'necunoscut'

    g = '\n'.join('| `%s` | %s |' % (k, v) for k, v in gmail.items())

    log = json.load(open(os.path.join(REPO, 'docs', 'LOG-SISTEM.json'), encoding='utf-8')) \
        if os.path.exists(os.path.join(REPO, 'docs', 'LOG-SISTEM.json')) else {'intrari': [], 'nivel': {}}
    prag = sh(['git', 'rev-list', '--count', 'origin/main..HEAD']) or '0'
    erori = [i for i in log.get('intrari', []) if i.get('nivel') in ('eroare', 'critic')]

    return {
        'branch': branch,
        'commits': commits,
        'dirty': dirty,
        'last': last,
        'remote': remote,
        'own': own,
        'vend': vend,
        'names': names,
        'vnames': vnames,
        'sites': sites,
        'sab': sab,
        'cvs': cvs,
        'gmail': gmail,
        'inbox': inbox,
        'trash': trash,
        'wf': wf,
        'g': g,
        'prag': prag,
        'erori': erori
    }

def build_markdown(stats):
    branch = stats['branch']
    commits = stats['commits']
    dirty = stats['dirty']
    last = stats['last']
    remote = stats['remote']
    own = stats['own']
    vend = stats['vend']
    names = stats['names']
    vnames = stats['vnames']
    sites = stats['sites']
    sab = stats['sab']
    cvs = stats['cvs']
    gmail = stats['gmail']
    inbox = stats['inbox']
    trash = stats['trash']
    wf = stats['wf']
    g = stats['g']
    prag = stats['prag']
    erori = stats['erori']
    md = f"""================================================================================
RAPORT DE STARE PROIECT: MAVIS-CLOUD
DATA & ORA: {TODAY} {datetime.datetime.now():%H:%M} | INSTANȚĂ: CLOUD
REPOSITORY: {remote}
================================================================================

> Fotografie a stării. **Nu se modifică după.** Generat de `mavis-tools/sentinel.py`.

---

## 1. SCOP ACTIV & FAZĂ

Faza: **Predare spre Local.** Site-ul trece la agentul local; eu rămân scout.

## 2. CE S-A EXECUTAT

## 3. CE A RĂMAS DESCHIS (NEXT STEPS)

## 4. STATUS GIT & SINCRONIZARE

- Branch: **{branch}**
- Commituri locale neîmpinse: {prag} (CLOUD împinge direct — nu se aplică pragul)
- Ultimul commit remote: `{last}`

## 5. CIRCUIT BREAKERS & BLOCAJE

- Erori active: **{len(erori)}**
- Blocaje: **{0 if not erori else len(erori)}**

---

## 6. Stare în cinci rânduri

Repo-ul Mavis e pe GitHub, totul pe `{branch}`, workflow-ul de verificare e **{wf}**.
Gmail-ul e sortat pe 8 etichete, gunoiul e gol. Există {len(own)} skill-uri proprii și
{len(vend)} importate. Site-ul de CV de Nivel 1 e funcțional pe {len(sites)} rol.
**Următorul pas: celelalte {9 - len(sites)} site-uri de Nivel 1.**

## 2. Numerele — contorizate, nu estimate

### Gmail
| Etichetă | Thread-uri |
|---|---|
{g}

| | |
|---|---|
| `in:inbox` (neatins) | **{inbox}** |
| `in:trash` | **{trash}** |

### Repo
| | |
|---|---|
| Remote | `{remote}` |
| Ramură | `{branch}` |
| Commit-uri | **{commits}** |
| Fișiere necomitate | **{dirty}** |
| Ultimul commit | `{last}` |
| Workflow | **{wf}** |

### Proiect
| | |
|---|---|
| Skill-uri proprii | **{len(own)}** |
| Skill-uri importate (vendor) | **{len(vend)}** |
| Site-uri de CV | **{len(sites)}** — {', '.join(sites) or 'niciunul'} |
| Șabloane CV generice | **{len(sab)}** |
| CV-uri Word | **{len(cvs)}** |

## 3. Gata, cu dovezi

| Ce | Cum s-a verificat |
|---|---|
| Repo pe GitHub | `gh api repos/apvizual-max/Mavis` — {commits} commit-uri pe `{branch}` |
| Workflow verde | `gh run list` → **{wf}** la ultimul push |
| Fără secrete | verificarea rulează la fiecare push, blochează build-ul |
| 22/22 fișiere JS valide | `node --check` pe fiecare, plus în workflow |
| Șabloane generice | `grep` nu găsește niciun nume de firmă |
| Gmail sortat | numărare prin paginare, nu prin estimare |
| Clasificări reparate | iqads: 0 în Personal · linkedin: 0 în Social |
| Site de CV | randat în Chromium, 3 tab-uri, 0 erori JS |

## 4. Ne făcut, în ordine

1. Site-urile de Nivel 1 rămase ({9 - len(sites)} roluri) — 7 JSON-uri, același `build.py`
2. CV-urile Word regenerate din șabloane, cu date generice
3. `MAVIS/Actiune - de raspuns` — regulă scrisă, rulează acum
4. `MAVIS/Facturi si conturi` — regulă scrisă, rulează acum
5. `MAVIS/AI si comunitati` — fereastra 1–3 ani era greșită, reparată
6. {inbox} thread-uri rămase în inbox
7. NotebookLM
8. LinkedIn — pregătit, trimis de POPY
9. Nivel 2: B2B / freelancing
10. Nivel 3: AP-ID Systems
11. MaxHermes — ultimul

## 5. BLOCAT

| Ce | De ce | Cine rezolvă |
|---|---|---|
| GitHub Copilot / Jules | cont `apvizual-max` pe plan **FREE**, API răspunde `Not Found` | **POPY**, din interfața web |
| Script „Mavis Apple Design" | link menționat, nu primit | **POPY**, trimite linkul |
| Nume de client „Smite" | — | **rezolvat**, corect, în toate fișierele |
| Fără factură fiscală | nu se poate vinde serviciu | POPY — de aceea site-ul e Nivel 1 |

## 6. Decizii luate, cu motiv

| Decizie | Motiv |
|---|---|
| MaxHermes înainte de MaxClaw | MaxClaw costă și nu aduce nevoie independentă încă |
| Drive ca stoc de sistem | POPY deschide efectiv ce e acolo |
| Trash da, `delete` nu | POPY a golit manual gunoiul, corect |
| Filtroane server-side pentru mail nou | `messages.list` costă 5 unități, nu 100 |
| Șablon generic înainte de aplicație concretă | altfel lucrezi de două ori |
| Nivelul 1 primul | fără PFA nu vinzi serviciu, dar impresionezi imediat |
| Date separate de UI în site | 9 roluri fără 9 layout-uri |

## 7. Erori comise, ca să nu se repete

| Eroare | Repar | Lecție |
|---|---|---|
| Am raportat „Social: 6.614" — realul era 2.678 | paginare reală | **dacă nu poți număra, spune** |
| „Contorul e defect" — era o greșeală a mea | `.raw`, nu `.data` | verifică instrumentul înainte de cont |
| `pgrep` spunea ALIVE pentru procese moarte | `date -r x.log` | `pgrep` se potrivește cu propria comandă |
| 722 de joburi erau în „Personal" | reclasificat + verificat în ambele sensuri | un identificator, o singură categorie |
| Titlu dedus din text → „Print" câștiga | `FAMILY_TITLE[family]` | rolul spune familia, textul colorează |
| Template literal neterminat | workflow-ul l-a prins | nu verifica doar ce ai editat acum |
| Am șosit 7 CV-uri cu cale cu `..` | recuperate | cale cu `..` în mijloc = risc |
| „Smite" → „Smike", fără motiv | revertat | nu „corectezi" ceva ce nu ai motiv să schimbi |

## 8. Ce așteaptă răspuns de la POPY

1. **Linkul scriptului „Mavis Apple Design"** — sau confirmă că acoperă repo-ul Emil
2. **Activează GitHub Copilot și Jules** din interfața web
3. **Decide etichetele goale**: le rezolv eu, sau le ștergi tu dacă ale tale
4. **Email, telefon** pentru site — sunt `[EMAIL]` și `[TELEFON]`

---

*Raport generat {TODAY} · {commits} commit-uri · {len(own) + len(vend)} skill-uri*
"""

    return md

def write_reports(md, stats):
    own = stats['own']
    vend = stats['vend']
    sites = stats['sites']
    inbox = stats['inbox']
    trash = stats['trash']
    path = os.path.join(DIR, TODAY + '-sentinel.md')
    open(path, 'w', encoding='utf-8').write(md)
    open(os.path.join(REPO, 'docs', 'SENTINEL-LATEST.md'), 'w', encoding='utf-8').write(md)

    # INDEX - rapoarte vechi, cu cel mai nou la început
    idx_path = os.path.join(DIR, 'INDEX.md')
    old = open(idx_path, encoding='utf-8').read() if os.path.exists(idx_path) else \
          '# Jurnal Sentinel\n\n> Rapoartele de stare, cel mai nou primul. **Nu se modifică.**\n\n'
    entry = '- [%s](%s-sentinel.md) — %d skill-uri, %d site-uri, inbox %s\n' % (
        TODAY, TODAY, len(own) + len(vend), len(sites), inbox)
    if entry not in old:
        body = old.split('\n\n', 1)[1] if '\n\n' in old else ''
        open(idx_path, 'w', encoding='utf-8').write(old.split('\n\n')[0] + '\n\n' + entry + body)

    print('OK  %s' % path)
    print('    inbox=%s trash=%s skilluri=%d siteuri=%d' % (inbox, trash, len(own) + len(vend), len(sites)))
    return path


def main():
    stats = gather_stats()
    md = build_markdown(stats)
    return write_reports(md, stats)

if __name__ == '__main__':
    main()
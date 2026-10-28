#!/usr/bin/env python3
"""MAVIS CLOUD - panoul de comanda, un singur site, cu tab-uri.

    python3 SITE/build-hub.py     ->  SITE/dist/index.html

Tab-uri: PANO · SITE CV · PUNTE · JULES/GIT/GITHUB · PROMPT
Actiunile se salveaza local si se exporta ca fisier, pe care POPY il trimite.
Site-ul e static: nu poate scrie in repo. Asta e limita lui, spusa deschis.
"""
import os, json, glob, datetime, subprocess, shutil, shlex

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
DIST = os.path.join(BASE, 'dist')

# Unde stau LOCAL cele 4 repo-uri. repos.json tine date despre ele
# (nume/rol/ramura/remote), dar NU tine cale pe disc - pentru ca aceleasi
# repo-uri au alte cai in cloud si pe masina lui Popy. Comanda ruleaza pe
# masina lui Popy, deci maparea de aici e cea valida.
CALE_REPO = {
    'MAVIS-CLOUD':           REPO,
    'MAVIS-OPTIMUS-CI':      os.path.dirname(REPO),
    'pkms-vault-automation': r'D:\Alex_Knowlege_Vault',
    'Optimus-Mavis-Skills':  r'C:\Users\apviz\.minimax\agents\mavis\skills',
}

def sh(c, cwd=REPO, t=25):
    try:
        args = shlex.split(c, posix=(os.name == 'posix'))
        return subprocess.run(args, shell=False, cwd=cwd, capture_output=True,
                              text=True, timeout=t).stdout.strip()
    except Exception:
        return ''

def stare_repo(name, branch):
    """Masura starea REALA a unui repo: HEAD, ramura, MATCH, murdare, fisiere.

    Interogam RAMURA DIN CONFIGURATIE, nu 'main'Blind. pkms-vault-automation
    e pe 'master', iar 'git ls-remote origin main' intoarce VID cu exit 0 -
    un verificator scris prost citeste asta ca dezincronizare cand e ok."""
    cale = CALE_REPO.get(name)
    d = {'nume': name, 'ramura': branch, 'cale': cale or 'necunoscuta',
         'head': '-', 'remote': '-', 'match': None, 'murdare': '-',
         'fisiere': '-', 'exista': bool(cale and os.path.isdir(cale))}
    if not d['exista']:
        return d
    d['head']    = sh('git rev-parse HEAD', cwd=cale)[:12] or '-'
    d['murdare'] = len(sh('git status --porcelain', cwd=cale, t=40).splitlines())
    n = sh('git ls-files', cwd=cale, t=60)
    d['fisiere'] = len(n.splitlines()) if n else 0
    d['remote']  = sh(f'git ls-remote origin refs/heads/{branch}', cwd=cale, t=40)[:12] or 'ref absent'
    # Ref absent inseamna "nu stiu", NU "dezincronizat". Se pastreaza ca atare.
    d['match'] = (d['head'] == d['remote']) if d['remote'] not in ('ref absent', '-') else None
    return d

def citeste_repo():
    """Citeste repos.json si masoara fiecare repo de pe disc."""
    p = os.path.join(BASE, 'date', 'repos.json')
    if not os.path.exists(p):
        return []
    try:
        cfg = json.load(open(p, encoding='utf-8'))
    except Exception:
        return []
    out = []
    for r in cfg:
        d = stare_repo(r.get('name', '?'), r.get('branch', 'main'))
        d['rol'] = r.get('role', '')
        d['remote_url'] = r.get('remote', '')
        out.append(d)
    return out

def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))

ICON = {'debug': '·', 'info': '›', 'atentie': '!', 'eroare': '✕', 'critic': '■'}
CUL  = {'debug': '#64748b', 'info': '#14b8a6', 'atentie': '#fbbf24',
        'eroare': '#f87171', 'critic': '#ef4444'}

# Actiuni pe butoane. Fiecare genereaza un prompt pe care POPY il trimite.
ACTIUNI = [
 ('Stare Sentinel',        'Genereaza raportul de stare complet, cu numere contorizate.'),
 ('Rezolva erorile',       'Citeeste logul, repara fiecare eroare, verifica, noteaza in log.'),
 ('Construieste site nou',  'Construieste urmatorul site de CV din sabloanele generice.'),
 ('Scaneaza joburi',       'Cauta joburi reale, aplica scoring, scrie pe Drive.'),
 ('Sorteaza Gmail',        'Ruleaza sortarea pe etichete, cu skip si ghilimele.'),
 ('Verifica tot',          'Ruleaza toate verificarile si raporteaza ce nu merge.'),
 ('Reconstruieste panoul',  'Regenereaza toate site-urile si panoul, apoi verifica.'),
 ('Foloseste Jules',       'Apeleaza Jules pentru review si aplica ce propune.'),
]

def copiaza_docs():
    """Documentele trebuie sa existe LANGA site, nu doar in repo.
    Link catre ../docs/ da 404 daca serverul nu are folderul."""
    src = os.path.join(REPO, 'docs')
    dst = os.path.join(DIST, 'docs')
    os.makedirs(dst, exist_ok=True)
    n = 0
    for f in glob.glob(os.path.join(src, '*.md')):
        with open(f, encoding='utf-8') as a, \
             open(os.path.join(dst, os.path.basename(f)), 'w', encoding='utf-8') as b:
            b.write(a.read())
        n += 1
    # vizualizatorul ramane langa documente
    # vizualizatorul e creat o data si pastrat in repo, nu se suprascrie

    # CSS-ul vizualizatorului trebuie SAU LANGa el, nu doar in repo.
    # Deployul trimite doar dist/, deci ../css/ din docs/ dava 404.
    css_src = os.path.join(BASE, 'css', 'doc.css')
    css_dst = os.path.join(DIST, 'css')
    os.makedirs(css_dst, exist_ok=True)
    if os.path.exists(css_src):
        shutil.copyfile(css_src, os.path.join(css_dst, 'doc.css'))
        n += 1
    return n

def badge(m):
    if m is True:
        return '<span class="tag ok">MATCH</span>'
    if m is False:
        return '<span class="tag" style="background:rgba(248,113,113,.12);color:#f87171;border-color:rgba(248,113,113,.3)">NESINCRON</span>'
    return '<span class="tag" style="color:#64748b">NECUNOSCUT</span>'

def main():
    os.makedirs(DIST, exist_ok=True)
    ndocs = copiaza_docs()
    todo = {'sarcini': []}
    tp = os.path.join(REPO, 'docs', 'TODO.json')
    if os.path.exists(tp):
        try: todo = json.load(open(tp, encoding='utf-8'))
        except Exception: pass
    azi = datetime.date.today().isoformat()

    repos = citeste_repo()
    n_ok = sum(1 for r in repos if r['match'] is True)
    n_r = len(repos)

    repo_rows = ''.join(
        '<tr><td class="mono"><b>%s</b><div style="color:#64748b;font-size:11.5px">%s</div></td>'
        '<td>%s</td><td class="mono">%s</td><td class="mono">%s</td><td>%s</td>'
        '<td style="text-align:right">%s</td><td style="text-align:right">%s</td></tr>' % (
            esc(r['nume']), esc(r['rol']),
            '<span class="tag">%s</span>' % esc(r['ramura']),
            esc(r['head']), esc(r['remote']), badge(r['match']),
            esc(r['murdare']), esc(r['fisiere']))
        for r in repos) or (
        '<tr><td colspan="7" style="color:#64748b;padding:14px 12px">'
        'repos.json lipseste sau nu poate fi citit.</td></tr>')

    branch  = sh('git rev-parse --abbrev-ref HEAD') or 'main'
    commits = sh('git rev-list --count HEAD') or '0'
    dirty   = len(sh('git status --porcelain').splitlines())
    last    = sh('git log --oneline -1')
    remote  = sh('git remote get-url origin')
    neimp = sh('git log origin/main..HEAD --oneline') or ''

    log = {'intrari': [], 'nivel': {}}
    lp = os.path.join(REPO, 'docs', 'LOG-SISTEM.json')
    if os.path.exists(lp):
        try: log = json.load(open(lp, encoding='utf-8'))
        except Exception: pass
    intr   = log.get('intrari', [])[:150]
    erori  = [i for i in intr if i['nivel'] in ('eroare', 'critic')]
    log_rows = ''.join(
        '<tr><td class="mono" style="white-space:nowrap;color:#64748b">%s</td>'
        '<td><span class="lv" style="color:%s;background:%s18;border:1px solid %s33">%s %s</span></td>'
        '<td>%s</td><td style="color:#94a3b8">%s</td></tr>' % (
            esc(i['t']), CUL.get(i['nivel'], '#94a3b8'), CUL.get(i['nivel'], '#94a3b8'),
            CUL.get(i['nivel'], '#94a3b8'), ICON.get(i['nivel'], '›'), esc(i['nivel']),
            esc(i['msg']), esc(i.get('rol', '-')))
        for i in intr)

    err_rows = ''.join(
        '<tr><td class="mono" style="color:#64748b;white-space:nowrap">%s</td>'
        '<td><span class="lv" style="color:#f87171;background:#f8717118;border:1px solid #f8717133">%s</span></td>'
        '<td><b>%s</b><div style="color:#94a3b8;font-size:12.5px;margin-top:3px">%s</div></td></tr>'
        % (esc(e['t']), esc(e['nivel']), esc(e['msg']), esc(e.get('detaliu', '')))
        for e in erori) or '<tr><td colspan="3" style="color:#64748b;padding:14px 12px">Nicio eroare.</td></tr>'

    own  = sorted(d for d in glob.glob(os.path.join(REPO, '.skills', '*')) if os.path.isdir(d))
    vend = sorted(d for d in glob.glob(os.path.join(REPO, 'vendor', '*')) if os.path.isdir(d))
    vn   = [os.path.basename(v) for v in vend]
    srows = ''
    desc_map = {}
    for s_path in own + vend:
        f = os.path.join(s_path, 'SKILL.md')
        if os.path.exists(f):
            with open(f, encoding='utf-8') as file:
                for ln in file:
                    if ln.startswith('description:'):
                        desc_map[os.path.basename(s_path)] = ln.split(':', 1)[1].strip()[:100]
                        break

    for s in sorted(own):
        n = os.path.basename(s)
        desc = desc_map.get(n, '')
        srows += '<tr><td class="mono">%s</td><td>%s</td><td><span class="tag %s">%s</span></td></tr>' % (
            n, esc(desc), 'v' if n in vn else '', 'vendor' if n in vn else 'propriu')

    sites = sorted(os.path.basename(p).replace('.index.html', '')
                   for p in glob.glob(os.path.join(DIST, '*.index.html')))
    sab = sorted(os.path.basename(p) for p in glob.glob(os.path.join(REPO, 'ALEX-KIT', 'SABLOANE', '*.md')))
    docs = sorted(os.path.basename(p) for p in glob.glob(os.path.join(REPO, 'docs', '*.md')))
    nskill = len(own) + len(vend)

    BAND = {'GATA': '#14b8a6', 'URMĂTORUL': '#fbbf24', 'DE FACUT': '#94a3b8', 'AMÂNAT': '#64748b'}
    todo_rows = ''.join(
        '<tr><td><b>%s</b><div style="color:#64748b;font-size:11.5px;margin-top:2px">%s</div></td>'
        '<td style="color:#94a3b8">%s</td>'
        '<td><span class="lv" style="color:%s;background:%s18;border:1px solid %s33">%s</span></td>'
        '<td style="color:#94a3b8;font-size:13px">%s</td>'
        '<td style="color:#cbd5e1;font-size:13px">%s</td></tr>' % (
            esc(x['titlu']), esc(x.get('id','')), esc(x.get('cine','-')),
            BAND.get(x.get('status',''), '#94a3b8'), BAND.get(x.get('status',''), '#94a3b8'),
            BAND.get(x.get('status',''), '#94a3b8'), esc(x.get('status','')),
            esc(x.get('rezultat','-')), esc(x.get('ramase','') or '<span style="color:#14b8a6">nimic</span>'))
        for x in todo.get('sarcini', []))

    act_btns = ''.join(
        '<button class="act" data-t="%s" data-c="%s">%s</button>' % (
            esc(t), esc(c), esc(t)) for t, c in ACTIUNI)

    doc_rows = ''.join('<tr><td><a href="docs/?doc=%s">%s</a></td></tr>' % (esc(d), esc(d)) for d in docs)
    sab_rows = ''.join('<li class="mono">%s</li>' % esc(s) for s in sab)

    html = f"""<!DOCTYPE html><html lang="ro"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mavis Cloud · tot ce există</title>
<meta http-equiv="refresh" content="180">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0b0f19;color:#f8fafc;font-family:'Inter',sans-serif;line-height:1.6;padding-bottom:90px}}
.wrap{{max-width:1200px;margin:0 auto;padding:0 24px}}
header{{padding:44px 0 0}}
h1{{font-size:clamp(1.7rem,4.5vw,2.6rem);font-weight:800;letter-spacing:-.03em;line-height:1.1}}
h1 span{{background:linear-gradient(120deg,#14b8a6,#67e8f9);-webkit-background-clip:text;background-clip:text;color:transparent}}
.sub{{color:#94a3b8;margin:10px 0 22px;font-size:.95rem}}
.mono{{font-family:'JetBrains Mono',monospace;font-size:12.5px}}
a{{color:#14b8a6;text-decoration:none}} a:hover{{text-decoration:underline}}
nav{{position:sticky;top:0;z-index:40;background:rgba(11,15,25,.94);
    backdrop-filter:blur(14px);border-bottom:1px solid #1e293b;margin-bottom:30px}}
nav .wrap{{display:flex;gap:4px;padding:9px 24px;overflow-x:auto}}
.tab{{appearance:none;background:none;border:0;cursor:pointer;color:#94a3b8;
     font:inherit;font-size:13.5px;font-weight:700;padding:9px 15px;border-radius:9px;
     transition:.2s;white-space:nowrap}}
.tab:hover{{color:#f8fafc;background:rgba(255,255,255,.05)}}
.tab[aria-selected="true"]{{color:#04211e;background:#14b8a6}}
.pane{{display:none;animation:r .4s cubic-bezier(.22,1,.36,1) both}}
.pane.on{{display:block}}
@keyframes r{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
h2{{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;font-weight:800;
   margin:34px 0 14px;padding-bottom:8px;border-bottom:1px solid #1e293b;
   display:flex;align-items:center;gap:10px}}
h2 .ct{{margin-left:auto;font-weight:600;letter-spacing:0;text-transform:none;
        font-size:11.5px;color:#64748b}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:11px}}
.card{{background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:16px}}
.card .n{{font-size:1.7rem;font-weight:800;color:#14b8a6;line-height:1}}
.card.bad .n{{color:#f87171}} .card.warn .n{{color:#fbbf24}}
.card .l{{font-size:10.5px;color:#64748b;margin-top:5px;text-transform:uppercase;letter-spacing:.07em;font-weight:700}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
th{{text-align:left;font-size:10.5px;letter-spacing:.11em;text-transform:uppercase;color:#64748b;
   padding:9px 12px;border-bottom:1px solid #1e293b;font-weight:800}}
td{{padding:9px 12px;border-bottom:1px solid #131c2e;vertical-align:top}}
tr:hover td{{background:rgba(20,184,166,.035)}}
.tag{{font-size:10px;font-weight:800;padding:3px 8px;border-radius:5px;background:rgba(148,163,184,.1);
     color:#94a3b8;border:1px solid #1e293b;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}}
.tag.ok{{background:rgba(20,184,166,.12);color:#14b8a6;border-color:rgba(20,184,166,.3)}}
.tag.v{{background:rgba(99,102,241,.1);color:#818cf8;border-color:rgba(99,102,241,.25)}}
.lv{{font-size:10.5px;font-weight:800;padding:2px 8px;border-radius:5px;white-space:nowrap}}
ul{{list-style:none;display:grid;gap:5px}}
li{{padding:8px 12px;background:#0f172a;border:1px solid #1e293b;border-radius:8px}}
.note{{padding:13px 16px;border-radius:10px;border:1px solid rgba(20,184,166,.22);
      background:rgba(20,184,166,.05);color:#94a3b8;font-size:13.5px;margin-top:14px}}
.note b{{color:#14b8a6}}
.warn{{border-color:rgba(251,191,36,.25);background:rgba(251,191,36,.05)}} .warn b{{color:#fbbf24}}
.bad{{border-color:rgba(248,113,113,.25);background:rgba(248,113,113,.05)}} .bad b{{color:#f87171}}
pre{{background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:15px;
    font-family:'JetBrains Mono',monospace;font-size:12.5px;color:#cbd5e1;
    white-space:pre-wrap;word-break:break-word;max-height:360px;overflow:auto}}
.act{{appearance:none;cursor:pointer;background:#0f172a;border:1px solid #1e293b;color:#cbd5e1;
     font:inherit;font-size:13.5px;font-weight:700;padding:11px 16px;border-radius:10px;
     margin:6px 8px 0 0;transition:.2s;text-align:left}}
.act:hover{{border-color:#14b8a6;color:#f8fafc;background:#111c33;transform:translateY(-1px)}}
.act.prim{{background:#14b8a6;border-color:#14b8a6;color:#04211e}}
.act.prim:hover{{background:#0d9488}}
.inp{{width:100%;background:#0f172a;border:1px solid #1e293b;border-radius:10px;color:#f8fafc;
     font:inherit;font-size:14px;padding:12px 14px;margin-top:8px;resize:vertical}}
.inp:focus{{outline:none;border-color:#14b8a6}}
.tab:focus-visible, .act:focus-visible, .qitem button:focus-visible, a:focus-visible {{ outline: 2px solid #14b8a6; outline-offset: 2px; border-radius: 4px; }}
.lbl{{font-size:10.5px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;
     color:#64748b;margin-top:16px;display:block}}
.row{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:16px}}
.box{{background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:18px}}
.box h3{{font-size:15px;font-weight:800;margin-bottom:8px}}
.box p{{color:#94a3b8;font-size:13.5px}}
.queue{{margin-top:14px}}
.qitem{{background:#0f172a;border:1px solid #1e293b;border-left:3px solid #14b8a6;
        border-radius:8px;padding:11px 14px;margin-bottom:7px;font-size:13.5px;
        display:flex;justify-content:space-between;gap:12px;align-items:center}}
.qitem button{{background:none;border:0;color:#64748b;cursor:pointer;font-size:17px;line-height:1}}
.qitem button:hover{{color:#f87171}}
.kv{{display:grid;grid-template-columns:auto 1fr;gap:7px 16px;font-size:13.5px;color:#94a3b8}}
.kv b{{color:#f8fafc}}
iframe{{width:100%;height:640px;border:1px solid #1e293b;border-radius:12px;background:#0b0f19}}
</style></head><body>

<div class="wrap"><header>
  <h1>Mavis <span>Cloud</span> · tot ce există</h1>
  <p class="sub">{azi} · <a href="https://github.com/apvizual-max/MAVIS-CLOUD">apvizual-max/MAVIS-CLOUD</a> ·
  ramura <code class="mono">{esc(branch)}</code> · {commits} commit-uri · {dirty} necomitate</p>
</header></div>

<nav><div class="wrap" role="tablist">
  <button class="tab" role="tab" aria-selected="true"  data-p="pano">Pano</button>
  <button class="tab" role="tab" aria-selected="false" data-p="cv">Site CV</button>
  <button class="tab" role="tab" aria-selected="false" data-p="punte">Punte · Bridge</button>
  <button class="tab" role="tab" aria-selected="false" data-p="jules">Jules · Git · GitHub</button>
  <button class="tab" role="tab" aria-selected="false" data-p="prompt">Prompt · Acțiuni</button>
  <button class="tab" role="tab" aria-selected="false" data-p="todo">TO DO</button>
</div></nav>

<div class="wrap">

<!-- ============ PANO ============ -->
<section class="pane on" role="tabpanel" id="pano">
  <div class="grid">
    <div class="card"><div class="n">{nskill}</div><div class="l">skill-uri</div></div>
    <div class="card {'bad' if (n_r and n_ok < n_r) else ''}"><div class="n">{n_ok}/{n_r}</div><div class="l">repo-uri MATCH</div></div>
    <div class="card"><div class="n">{len(sites)}</div><div class="l">site-uri CV</div></div>
    <div class="card"><div class="n">{len(sab)}</div><div class="l">șabloane</div></div>
    <div class="card {'bad' if erori else ''}"><div class="n">{len(erori)}</div><div class="l">erori</div></div>
    <div class="card"><div class="n">{len(intr)}</div><div class="l">în log</div></div>
  </div>

  <h2>Repo-uri <span class="ct">{n_ok} din {n_r} sincronizate · măsurat pe disc, nu declarat</span></h2>
  <table><thead><tr><th>Repo · rol</th><th>Ramură</th><th>HEAD local</th><th>HEAD remote</th>
  <th>Stare</th><th style="text-align:right">Modif.</th><th style="text-align:right">Fișiere</th></tr></thead>
  <tbody>{repo_rows}</tbody></table>
  <div class="note"><b>Se interogează ramura configurată, nu orbește pe <code class="mono">main</code>.</b>
  <code class="mono">pkms-vault-automation</code> e pe <code class="mono">master</code>; interogarea lui pe
  <code class="mono">main</code> întoarce <b>vid cu exit 0</b>, iar un verificator scris prost citește
  asta ca dezincronizare. „Ref absent" e starea <b>NECUNOSCUT</b>, nu starea <b>NESINCRON</b>.</div>

  <h2>Erori <span class="ct">{len(erori)} de rezolvat</span></h2>
  <table><thead><tr><th>Timp</th><th>Nivel</th><th>Ce</th></tr></thead><tbody>{err_rows}</tbody></table>

  <h2>Log live <span class="ct">ultimele {len(intr)} de 150 · cel mai nou primul</span></h2>
  <table><thead><tr><th>Timp</th><th>Nivel</th><th>Mesaj</th><th>Rol</th></tr></thead>
  <tbody>{log_rows or '<tr><td colspan="4" style="color:#64748b;padding:14px 12px">Log gol.</td></tr>'}</tbody></table>
  <div class="note"><b>Plafon 150, rotație FIFO.</b> Intrarea 151 șterge intrarea 1.
  Se scrie automat la orice schimbare.</div>

  <h2>Skill-uri <span class="ct">{len(own)} proprii + {len(vend)} vendor</span></h2>
  <table><thead><tr><th>Nume</th><th>Ce face</th><th>Origine</th></tr></thead><tbody>{srows}</tbody></table>

  <h2>Documentație <span class="ct">{len(docs)} fișiere, deschise din panou</span></h2>
  <table><tbody>{doc_rows}</tbody></table>
  <div class="note"><b>Se deschid aici, nu te trimit în altă parte.</b> Fiecare document
  e copiat lângă panou, ca linkul să funcționeze și offline.</div>

  <h2>Ultimul commit</h2>
  <p class="mono" style="color:#94a3b8">{esc(last)}</p>
</section>

<!-- ============ SITE CV ============ -->
<section class="pane" role="tabpanel" id="cv">
  <h2>Site de CV <span class="ct">{len(sites)} roluri, se construiește din date</span></h2>
  <div class="note"><b>Nu e o pagină goală.</b> Fiecare rol e un fișier JSON;
  interfața e aceeași pentru toate. Adăugarea unui rol nou nu înseamnă scriere de HTML.</div>
  <div style="margin:16px 0">
    {' · '.join('<a href="%s.index.html" style="margin-right:14px">%s</a>' % (s, s) for s in sites) or 'niciunul'}
    <a href="/">← Panoul</a>
  </div>
  <iframe src="graphic-designer.index.html" title="Site CV"></iframe>
</section>

<!-- ============ PUNTE ============ -->
<section class="pane" role="tabpanel" id="punte">
  <h2>Punte · Bridge <span class="ct">cloud ↔ local, prin repo</span></h2>
  <div class="row">
    <div class="box">
      <h3>Ce construiește Mavis Cloud</h3>
      <p>Site-urile, CV-urile, scorul, sortarea Gmail, logul, panoul, documentația.
      Rulează automat. Nu te întreabă dacă poate.</p>
    </div>
    <div class="box">
      <h3>Ce construiește Mavis Local</h3>
      <p>Deployment local, YouTube, fișiere pe calculatorul lui POPY,
      lucruri care nu au voie să iasă din mașina lui.</p>
    </div>
  </div>

  <h2>Cum circulă informația</h2>
  <pre>Mavis Cloud (aici)                Mavis Local (la POPY)
     |                                  |
     |  scrie in repo  ──────────────►  git pull → citește → lucrează
     |                                  |
     |  git pull      ◄──────────────  scrie → commit → push
     |                                  |
   PANOUL (live)  ◄──── se actualizeaza la 3 minute</pre>

  <h2>Cum face agentul local să tragă automat</h2>
  <div class="note"><b>Răspunsul scurt: nu poate singur, fără un programator care îl pornească o dată.</b>
  Trebuie <b>un singur fișier</b> pe calculatorul lui, care face <code class="mono">git pull</code>,
  citește cerințele, face ce poate, și face <code class="mono">git push</code>. Îl pornește o dată,
  apoi merge singur. E scris în <code class="mono">docs/INTENTII.md</code> și
  <code class="mono">.skills/puntea-agenti/SKILL.md</code>.</div>
  <div class="row" style="margin-top:14px">
    <div class="box"><h3>Fișierul 1 — cerințe</h3><p><code class="mono">docs/INTENTII.md</code><br>
      POPY scrie, agentul local citește și răspunde tot acolo.</p></div>
    <div class="box"><h3>Fișierul 2 — pornire</h3><p><code class="mono">.skills/puntea-agenti/SKILL.md</code><br>
      Comanda unică, pentru agent fără memorie.</p></div>
  </div>
  <h2>Stare</h2>
  <div class="kv">
    <b>Repo</b><span>{esc(remote)}</span>
    <b>Ramură</b><span>{esc(branch)}</span>
    <b>Commit-uri</b><span>{commits}</span>
    <b>Nepushate</b><span>{len(neimp.splitlines()) if neimp else '0 — sincronizat'}</span>
    <b>Fișiere necomitate</b><span>{dirty}</span>
  </div>
</section>

<!-- ============ JULES · GIT · GITHUB ============ -->
<section class="pane" role="tabpanel" id="jules">
  <h2>Git <span class="ct">stare internă</span></h2>
  <div class="kv">
    <b>Remote</b><span>{esc(remote)}</span>
    <b>Ramură</b><span>{esc(branch)}</span>
    <b>Commit-uri</b><span>{commits}</span>
    <b>Necomitate</b><span>{dirty}</span>
    <b>Ultimul</b><span class="mono">{esc(last)}</span>
  </div>

  <h2>GitHub <span class="ct">hosting, workflow, review</span></h2>
  <div class="row">
    <div class="box"><h3>Workflow de verificare</h3>
      <p>Rulează la fiecare push: secrete, JSON, sintaxă JS, build site, șabloane ne-generice.</p></div>
    <div class="box"><h3>Live Review</h3>
      <p>hexmos.com — plan free. Reactionează la <b>pull request</b>, nu la push direct.
      De aceea îți cer să faci PR când vrei review.</p></div>
  </div>

  <h2>Jules <span class="ct">agentul de review de la Google</span></h2>
  <div class="note"><b>Deja conectat la MAVIS-CLOUD.</b> În captura ta, Jules arată deja sugestii
  reale pe codul tău — de exemplu <code class="mono">Missing Escaping/Sanitization for Process
  Argument in cv-mutator.js</code> și teste lipsă pentru funcțiile din
  <code class="mono">cv-mutator.js</code> / <code class="mono">letter-engine.js</code>.
  <b>Astea sunt adevărate și merită luate.</b></div>
  <div class="row" style="margin-top:14px">
    <div class="box"><h3>Cum îl folosești</h3>
      <p>Intri în Jules, alegi <code class="mono">apvizual-max/MAVIS-CLOUD</code>,
      vezi Suggestions, apeși Start. El face ramura și PR-ul.</p></div>
    <div class="box"><h3>Cum îl folosesc eu</h3>
      <p>Prin API cu cheia din managerul de secrete, și prin panou:
      butonul <b>„Foloseste Jules"</b> din tab-ul Prompt.</p></div>
  </div>
  <h2>Documentația de instrumentare</h2>
  <div class="note">Am scris <code class="mono">docs/JULES-INSTRUMENTARE.md</code> cu ce ai văzut
  în capturi și ce trebuie configurat. <a href="docs/?doc=JULES-INSTRUMENTARE.md">Vezi aici</a></div>

  <h2>Live Review — panoul lui</h2>
  <div class="note">Funcționează. În captura ta scrie „No review pipeline data yet" — asta înseamnă
  <b>că nu a existat încă un pull request</b> ca el să-l analizeze. Prima rulare are loc la primul PR.</div>
</section>

<!-- ============ PROMPT · ACTIUNI ============ -->
<section class="pane" role="tabpanel" id="prompt">
  <h2>Acțiuni rapide <span class="ct">un clic → prompt gata de trimis</span></h2>
  <p style="color:#94a3b8;font-size:13.5px;margin-bottom:6px">
    Fiecare buton pune o cerință în coadă și îți dă prompt-ul. Trimite-mi promptul și lucrez.</p>
  {act_btns}
  <div class="qbar">
    <button class="act prim" id="copiaza">Copiază toate acțiunile</button>
    <button class="act" id="descarca">Descarcă coada ca fișier</button>
    <button class="act" id="golește">Golește coada</button>
  </div>
  <div class="queue" id="coada"></div>

  <h2>Generator de prompt <span class="ct">obiectiv · sarcină · criterii</span></h2>
  <div class="note"><b>Scrie problema în cuvintele tale.</b> Generatorul o transformă în prompt
  structurat pe care îl trimiți aici. Nu trebuie să știi să scrii prompturi.</div>

  <label class="lbl" for="dureri">Ce vrei — în cuvintele tale</label>
  <textarea class="inp" id="dureri" rows="4"
    placeholder="Ex: nu mai văd emailurile vechi, vreau să fie ordonate, și vreau să știu care cer răspuns"></textarea>

  <label class="lbl" for="criterii">Criterii — cum știi că e rezolvat</label>
  <textarea class="inp" id="criterii" rows="2"
    placeholder="Ex: vreau să văd un raport, și să nu se piardă nimic"></textarea>

  <label class="lbl" for="restrictii">Ce NU ai voie să faci</label>
  <textarea class="inp" id="restrictii" rows="2"
    placeholder="Ex: nu șterge nimic definitiv, nu trimite nimic în numele meu"></textarea>

  <button class="act prim" id="genereaza" style="margin-top:16px">Generează promptul</button>
  <div id="rezultat" style="margin-top:14px"></div>

  <h2>Limită onestă</h2>
  <div class="note warn"><b>Asta e un site static.</b> Butoanele nu pot scrie direct în repo-ul meu —
  un site fără server nu are cum. De aceea funcționează pe <b>coadă + copiere</b>: apeși, îți iese
  promptul, îl trimiți aici. Singura cale sigură prin care cerința ta ajunge la mine.</div>
</section>

<!-- ============ TO DO ============ -->
<section class="pane" role="tabpanel" id="todo">
  <h2>TO DO <span class="ct">{len(todo.get('sarcini', []))} sarcini</span></h2>
  <table><thead><tr><th>Sarcină</th><th>Cine</th><th>Status</th><th>Stare acum</th><th>Mai rămâne</th></tr></thead>
  <tbody>{todo_rows}</tbody></table>
  <div class="note"><b>Lista se actualizează singură.</b> Vine din
  <code class="mono">docs/TODO.json</code>, pe care îl modific la fiecare schimbare
  reală de stare. Nu e text tastat de mână în interfață.</div>
</section>

</div>

<script>
(function(){{
  var tabs = [].slice.call(document.querySelectorAll('.tab'));
  var panes = {{}};
  tabs.forEach(function(t){{ panes[t.dataset.p] = document.getElementById(t.dataset.p); }});
  function show(id){{
    tabs.forEach(function(t){{ t.setAttribute('aria-selected', t.dataset.p===id?'true':'false'); }});
    Object.keys(panes).forEach(function(k){{ panes[k].classList.toggle('on', k===id); }});
    try{{ history.replaceState(null,'','#'+id); }}catch(e){{}}
  }}
  tabs.forEach(function(t){{ t.addEventListener('click', function(){{ show(t.dataset.p); }}); }});
  if (location.hash) {{ var h = location.hash.slice(1); if (panes[h]) show(h); }}

  var CHEIE = 'mavis-cloud-coada';
  function coada(){{ return JSON.parse(localStorage.getItem(CHEIE) || '[]'); }}
  function salveaza(c){{ localStorage.setItem(CHEIE, JSON.stringify(c)); rand(); }}

  function rand(){{
    function escHtml(s){{ return (s||'').replace(/[&<>]/g, function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c];}}); }};
    var c = coada(), box = document.getElementById('coada');
    if (!c.length) {{ box.innerHTML = '<p style="color:#64748b;font-size:13.5px;margin-top:12px">Coada e goală. Apasă un buton de mai sus.</p>'; return; }}
    box.innerHTML = c.map(function(x,i){{
      return '<div class="qitem"><span>'+ (i+1) +'. '+ escHtml(x.titlu) +'</span>'+
             '<button title="șterge" aria-label="Șterge acțiunea" onclick="stergeAcțiune('+i+')">&times;</button></div>';
    }}).join('');
  }}
  window.stergeAcțiune = function(i){{ var c = coada(); c.splice(i,1); salveaza(c); }};

  document.querySelectorAll('.act[data-t]').forEach(function(b){{
    b.addEventListener('click', function(){{
      var c = coada();
      c.push({{ titlu: b.dataset.t, cerinta: b.dataset.c,
                t: new Date().toLocaleString('ro-RO') }});
      salveaza(c);
    }});
  }});

  document.getElementById('golește').addEventListener('click', function(){{ localStorage.removeItem(CHEIE); rand(); }});

  document.getElementById('copiaza').addEventListener('click', function(){{
    var c = coada(); if (!c.length) return;
    var txt = c.map(function(x,i){{ return (i+1)+'. '+x.cerinta; }}).join('\\n');
    navigator.clipboard.writeText(txt).then(function(){{
      var b = document.getElementById('copiaza'); b.textContent = 'Copiat ✓';
      setTimeout(function(){{ b.textContent = 'Copiază toate acțiunile'; }}, 1800);
    }});
  }});

  document.getElementById('descarca').addEventListener('click', function(){{
    var c = coada(); if (!c.length) return;
    var blob = new Blob([JSON.stringify({{ repo:'apvizual-max/MAVIS-CLOUD', actiuni:c }}, null, 2)],
                        {{ type:'application/json' }});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'mavis-cloud-coada.json'; a.click();
  }});

  document.getElementById('genereaza').addEventListener('click', function(){{
    var d = document.getElementById('dureri').value.trim();
    var c = document.getElementById('criterii').value.trim();
    var r = document.getElementById('restrictii').value.trim();
    if (!d) {{ alert('Scrie măcar problema.'); return; }}
    var p = '## OBIECTIV\\n' + d + '\\n\\n' +
            '## SARCINA\\n' +
            'Repo: apvizual-max/MAVIS-CLOUD. Citește docs/SENTINEL-LATEST.md, apoi AGENTS.md, ' +
            'apoi docs/HANDOFF.md, apoi docs/LOG-SISTEM.json. Lucrează pe main, comitează și împinge.\\n\\n' +
            '## CRITERII DE ACCEPTARE\\n' + (c || '- execută și verifică\\n- scrie în log\\n- actualizează PROGRES.md') + '\\n\\n' +
            '## RESTRICȚII\\n' + (r || '- nu șterge nimic definitiv\\n- nu trimite nimic în numele lui POPY\\n- nu inventa numere sau nume\\n- nu rescrie motorul, doar amendă') + '\\n\\n' +
            '## VERIFICARE\\n' +
            '- rulează comanda și arată rezultatul\\n- dacă ceva nu merge, scrie în log ca eroare și raportează\\n';
    document.getElementById('rezultat').innerHTML =
      '<pre>'+p.replace(/[&<>]/g, function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c];}})+'</pre>' +
      '<button class="act prim" id="copiazaP" style="margin-top:10px">Copiază promptul</button>';
    document.getElementById('copiazaP').addEventListener('click', function(ev){{
      navigator.clipboard.writeText(p);
      ev.target.textContent = 'Copiat ✓';
      setTimeout(function(){{ ev.target.textContent = 'Copiază promptul'; }}, 1800);
    }});
  }});

  rand();
}})();
</script>
</body></html>"""

    out = os.path.join(DIST, 'index.html')
    open(out, 'w', encoding='utf-8').write(html)
    return out, len(sites), nskill, len(erori), len(intr)

if __name__ == '__main__':
    p, s, n, e, l = main()
    print('OK  %s' % p)
    print('    %d roluri · %d skill-uri · %d erori · %d intrari log' % (s, n, e, l))
    print('    docs/ copiate langa panou')
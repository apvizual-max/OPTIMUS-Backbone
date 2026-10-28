# DEPRECAT 2026-12 — defect F4
#
# Acest script si SITE/build-hub.py scriau AMBII in dist/index.html.
# Al doilea suprascria panoul complet al primului (25.016 B, 0 repo-uri
# peste 60.958 B, 4 repo-uri).
#
# SITE/build-hub.py este SINGURUL script autorizat sa scrie dist/index.html.
#
# Daca ai nevoie de vechea versiune: python3 SITE/build-dashboard-legacy.py
#   -> scrie dist/dashboard-legacy.html

#!/usr/bin/env python3
"""Panou de bord MAVIS CLOUD - tot ce exista, live, cu log si erori.

    python3 SITE/build-dashboard.py
    deschide SITE/dist/dashboard-legacy.html

Populat din date reale: git, log, erori, skill-uri, site-uri, Gmail.
"""
import os, json, glob, datetime, subprocess, shlex

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
DIST = os.path.join(BASE, 'dist')

def sh(cmd_args, cwd=REPO, t=25):
    try:
        return subprocess.run(cmd_args, shell=False, cwd=cwd, capture_output=True,
                              text=True, timeout=t).stdout.strip()
    except Exception:
        return ''

def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

ICON = {'debug': '·', 'info': '›', 'atentie': '!', 'eroare': '✕', 'critic': '■'}
CUL  = {'debug': '#64748b', 'info': '#14b8a6', 'atentie': '#fbbf24',
        'eroare': '#f87171', 'critic': '#ef4444'}

def main():
    os.makedirs(DIST, exist_ok=True)
    azi = datetime.date.today().isoformat()

    # ---- git ----
    branch  = sh(['git', 'rev-parse', '--abbrev-ref', 'HEAD']) or 'main'
    commits = sh(['git', 'rev-list', '--count', 'HEAD']) or '0'
    dirty   = len(sh(['git', 'status', '--porcelain']).splitlines())
    last    = sh(['git', 'log', '--oneline', '-1'])
    remote  = sh(['git', 'remote', 'get-url', 'origin'])
    neimpush = sh(['git', 'log', 'origin/main..HEAD', '--oneline']) if remote else ''

    # ---- log ----
    log = {'intrari': [], 'nivel': {}}
    lp = os.path.join(REPO, 'docs', 'LOG-SISTEM.json')
    if os.path.exists(lp):
        try:
            log = json.load(open(lp, encoding='utf-8'))
        except Exception:
            pass
    intr = log.get('intrari', [])[:150]
    erori = [i for i in intr if i['nivel'] in ('eroare', 'critic')]
    atn   = [i for i in intr if i['nivel'] == 'atentie']

    log_rows = ''
    for i in intr:
        c = CUL.get(i['nivel'], '#94a3b8')
        log_rows += (
        '<tr><td class="mono" style="white-space:nowrap;color:#64748b">%s</td>'
        '<td><span class="lv" style="color:%s;background:%s18;border:1px solid %s33">%s %s</span></td>'
        '<td>%s</td><td style="color:#94a3b8">%s</td></tr>' % (
            esc(i['t']), c, c, c, ICON.get(i['nivel'], '›'), esc(i['nivel']),
            esc(i['msg']), esc(i.get('rol', '-'))))

    # ---- erori ----
    if erori:
        err_rows = ''.join(
            '<tr><td class="mono" style="color:#64748b;white-space:nowrap">%s</td>'
            '<td><span class="lv" style="color:#f87171;background:#f8717118;border:1px solid #f8717133">%s</span></td>'
            '<td><b>%s</b><div style="color:#94a3b8;font-size:12.5px;margin-top:3px">%s</div></td></tr>'
            % (esc(e['t']), esc(e['nivel']), esc(e['msg']), esc(e.get('detaliu', '')))
            for e in erori)
        prompt = ('Repo apvizual-max/MAVIS-CLOUD. Citeste docs/LOG-SISTEM.json, filtreaza '
                'nivel=eroare sau critic, repara fiecare, verifica, apoi scrie in log.')
    else:
        err_rows = '<tr><td colspan="3" style="color:#64748b;padding:14px 12px">Nicio eroare.</td></tr>'
        prompt = 'Nicio eroare de rezolvat.'

    # ---- skill-uri ----
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
                        desc_map[os.path.basename(s_path)] = ln.split(':', 1)[1].strip()[:110]
                        break

    for s in sorted(own):
        n = os.path.basename(s)
        desc = desc_map.get(n, '')
        src = 'vendor' if n in vn else 'propriu'
        srows += '<tr><td class="mono">%s</td><td>%s</td><td><span class="tag %s">%s</span></td></tr>' % (
            n, esc(desc), 'v' if src == 'vendor' else '', src)

    # ---- site-uri ----
    sites = sorted(os.path.basename(p).replace('.index.html', '')
                for p in glob.glob(os.path.join(DIST, '*.index.html')))
    site_rows = ''.join(
        '<tr><td><a href="%s.index.html">%s</a></td>'
        '<td><span class="tag ok">gata</span></td><td>deschide</td></tr>' % (s, s) for s in sites)

    # ---- documente ----
    docs = sorted(os.path.basename(p) for p in glob.glob(os.path.join(REPO, 'docs', '*.md')))
    doc_rows = ''.join('<tr><td><a href="../docs/%s">%s</a></td></tr>' % (esc(d), esc(d)) for d in docs)

    sab = sorted(os.path.basename(p) for p in glob.glob(os.path.join(REPO, 'ALEX-KIT', 'SABLOANE', '*.md')))
    cvs = sorted(os.path.basename(p) for p in glob.glob(os.path.join(REPO, 'ALEX-KIT', 'CV-URI', '*.docx')))
    sab_rows = ''.join('<li class="mono">%s</li>' % esc(s) for s in sab)
    cv_rows  = ''.join('<li class="mono">%s</li>' % esc(c) for c in cvs)

    n = len(own) + len(vend)
    niveluri = ' · '.join('%s %d' % (k, v) for k, v in log.get('nivel', {}).items()) or 'gol'

    html = f"""<!DOCTYPE html><html lang="ro"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mavis Cloud · Tot ce există</title>
<meta http-equiv="refresh" content="120">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0b0f19;color:#f8fafc;font-family:'Inter',sans-serif;line-height:1.6;padding-bottom:80px}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 24px}}
header{{padding:60px 0 30px;border-bottom:1px solid #1e293b;margin-bottom:32px}}
h1{{font-size:clamp(1.9rem,5vw,3.1rem);font-weight:800;letter-spacing:-.03em;line-height:1.06}}
h1 span{{background:linear-gradient(120deg,#14b8a6,#67e8f9);-webkit-background-clip:text;background-clip:text;color:transparent}}
.sub{{color:#94a3b8;margin-top:12px;font-size:1rem}}
.mono{{font-family:'JetBrains Mono',monospace;font-size:12.5px}}
a{{color:#14b8a6;text-decoration:none}} a:hover{{text-decoration:underline}}
h2{{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;font-weight:800;
    margin:42px 0 15px;padding-bottom:9px;border-bottom:1px solid #1e293b;
    display:flex;align-items:center;gap:10px}}
h2 .ct{{margin-left:auto;font-weight:600;letter-spacing:0;text-transform:none;
        font-size:11.5px;color:#64748b}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:11px}}
.card{{background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:17px}}
.card .n{{font-size:1.85rem;font-weight:800;color:#14b8a6;line-height:1}}
.card.bad .n{{color:#f87171}} .card.warn .n{{color:#fbbf24}}
.card .l{{font-size:11px;color:#64748b;margin-top:6px;text-transform:uppercase;letter-spacing:.07em;font-weight:700}}
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
.btn{{display:inline-block;padding:12px 22px;background:#14b8a6;color:#04211e;border-radius:10px;
    font-weight:800;font-size:14px;margin:6px 8px 0 0;transition:.2s}}
.btn:hover{{background:#0d9488;text-decoration:none;color:#04211e}}
.btn.g{{background:transparent;color:#14b8a6;border:1px solid rgba(20,184,166,.4)}}
.note{{padding:13px 16px;border-radius:10px;border:1px solid rgba(20,184,166,.22);
    background:rgba(20,184,166,.05);color:#94a3b8;font-size:13.5px;margin-top:14px}}
.note b{{color:#14b8a6}}
.warn{{border-color:rgba(251,191,36,.25);background:rgba(251,191,36,.05)}} .warn b{{color:#fbbf24}}
.bad{{border-color:rgba(248,113,113,.25);background:rgba(248,113,113,.05)}} .bad b{{color:#f87171}}
pre{{background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:15px;
    font-family:'JetBrains Mono',monospace;font-size:12.5px;color:#94a3b8;
    white-space:pre-wrap;word-break:break-word;max-height:320px;overflow:auto}}
.top{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:14px}}
</style></head><body><div class="wrap">

<header>
    <h1>Mavis <span>Cloud</span> · Tot ce există</h1>
    <p class="sub">{azi} · <a href="https://github.com/apvizual-max/MAVIS-CLOUD">apvizual-max/MAVIS-CLOUD</a> ·
    ramura <code class="mono">{esc(branch)}</code> · {commits} commit-uri ·
    {dirty} necomitate</p>
    <div class="top">
    <span class="tag {'ok' if dirty==0 else ''}">{'totul comitat' if dirty=='0' else str(dirty)+' necomitat'}</span>
    <span class="tag ok">log: {len(intr)}/150</span>
    <span class="tag {'' if not erori else 'bad'}">erori: {len(erori)}</span>
    </div>
</header>

<h2>Deschide <span class="ct">două site-uri, subiecte separate</span></h2>
<a class="btn" href="graphic-designer.index.html">Site de CV — Graphic Designer</a>
<a class="btn g" href="#log">Panoul acesta</a>
<div class="note"><b>Site-ul de CV</b> e documentul tău de prezentare.
<b>Panoul acesta</b> e partea operațională: log, erori, stare.</div>

<h2>Sumar <span class="ct">{niveluri}</span></h2>
<div class="grid">
    <div class="card"><div class="n">{n}</div><div class="l">skill-uri</div></div>
    <div class="card"><div class="n">{len(sites)}</div><div class="l">site-uri CV</div></div>
    <div class="card"><div class="n">{len(sab)}</div><div class="l">șabloane CV</div></div>
    <div class="card"><div class="n">{len(cvs)}</div><div class="l">CV-uri Word</div></div>
    <div class="card {'bad' if erori else ''}"><div class="n">{len(erori)}</div><div class="l">erori</div></div>
    <div class="card"><div class="n">{len(intr)}</div><div class="l">în log</div></div>
</div>

<h2 id="erori">Erori <span class="ct">{len(erori)} de rezolvat, {len(atn)} atenționări</span></h2>
<table><thead><tr><th>Timp</th><th>Nivel</th><th>Ce</th></tr></thead><tbody>
{err_rows}
</tbody></table>
<pre>## Prompt de apel — trimite-l și vine promptul de reparare

{prompt}</pre>

<h2 id="log">Log live <span class="ct">ultimele {len(intr)} de 150 · cel mai nou primul</span></h2>
<table><thead><tr><th>Timp</th><th>Nivel</th><th>Mesaj</th><th>Rol</th></tr></thead><tbody>
{log_rows or '<tr><td colspan="4" style="color:#64748b;padding:14px 12px">Log gol.</td></tr>'}
</tbody></table>
<div class="note"><b>Plafon 150, rotație FIFO.</b> Intrarea 151 șterge intrarea 1.
Nu se umple niciodată, nu ocupă memorie, și nu ai niciodată de citit prin
mii de intrări ca să găsești ce contează. Se scrie automat la orice schimbare.</div>

<h2>Site-uri de CV <span class="ct">{len(sites)}</span></h2>
<table><thead><tr><th>Rol</th><th>Stare</th><th>Cum îl deschizi</th></tr></thead><tbody>
{site_rows or '<tr><td colspan="3">niciunul</td></tr>'}
</tbody></table>

<h2>Șabloane CV <span class="ct">generice, zero nume de firmă</span></h2>
<ul>{sab_rows}</ul>

<h2>CV-uri Word</h2>
<ul>{cv_rows}</ul>

<h2>Skill-uri <span class="ct">{len(own)} proprii + {len(vend)} importate</span></h2>
<table><thead><tr><th>Nume</th><th>Ce face</th><th>Origine</th></tr></thead><tbody>
{srows}
</tbody></table>

<h2>Documentație</h2>
<table><tbody>{doc_rows}</tbody></table>

<h2>Ultimul commit</h2>
<p class="mono" style="color:#94a3b8">{esc(last)}</p>
<div class="note"><b>Se reîmprospătează singur la 2 minute.</b>
Generat de <code class="mono">SITE/build-dashboard.py</code> din date reale —
git, log, erori, skill-uri, site-uri. Nicio cifră tastată manual.</div>

</div></body></html>"""

    out = os.path.join(DIST, 'dashboard-legacy.html')  # F4: nu suprascrie panoul
    open(out, 'w', encoding='utf-8').write(html)
    return out, len(sites), n, len(erori), len(intr)

if __name__ == '__main__':
    p, s, n, e, l = main()
    print('OK  %s' % p)
    print('    %d site-uri · %d skill-uri · %d erori · %d intrari log' % (s, n, e, l))
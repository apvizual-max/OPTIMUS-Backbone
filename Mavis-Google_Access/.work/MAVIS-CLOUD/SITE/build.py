#!/usr/bin/env python3
"""Construieste site-ul de CV din fisierul de date.

    python3 build.py graphic-designer

Citeste SITE/date/<rol>.json, emite SITE/dist/<rol>.index.html
Structura ramane aceeasi. Schimbi datele, nu UI-ul.
"""
import json, os, sys, html

BASE = os.path.dirname(os.path.abspath(__file__))
DATE = os.path.join(BASE, 'date')
DIST = os.path.join(BASE, 'dist')
CSS  = os.path.join(BASE, 'css', 'schelet.css')

def esc(s):
    return html.escape(str(s), quote=True)

def initials(name):
    parts = [p for p in str(name or '').split() if p]
    return ''.join(p[0] for p in parts[:2]).upper() or '—'

def load_data(slug):
    src = os.path.join(DATE, slug + '.json')
    return json.load(open(src, encoding='utf-8'))

def render_cv(cv):
    skills = '\n'.join(
        '        <li class="skill"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<polyline points="20 6 9 17 4 12"/></svg>%s</li>' % esc(s)
        for s in cv['competente'])

    ach = '\n'.join(
        '        <article class="ach-item"><h3 class="ach-t">%s</h3><p class="ach-d">%s</p></article>'
        % (esc(a['titlu']), esc(a['text'])) for a in cv['realizari'])

    tl = '\n'.join(
        '        <div class="tl-item"><div class="tl-when">%s</div>'
        '<div class="tl-role">%s</div><div class="tl-detail">%s</div></div>'
        % (esc(e['perioada']), esc(e['rol']), esc(e['detaliu'])) for e in cv['experienta'])

    edu = '\n'.join('        <li class="skill"><span aria-hidden="true">—</span>%s</li>' % esc(e)
                    for e in cv.get('educatie', []))

    return skills, ach, tl, edu

def render_portfolio(port):
    return '\n'.join(
        '      <article class="pf" data-tilt>\n'
        '        <div class="pf-top"><div class="pf-ico" aria-hidden="true">%s</div>'
        '<div><div class="pf-client">%s</div><div class="pf-cat">%s</div></div></div>\n'
        '        <div><h3 class="pf-title">%s</h3><p class="pf-note">%s</p></div>\n'
        '        <span class="pf-status" data-s="%s">%s</span>\n'
        '      </article>' % (esc(initials(p['client'])), esc(p['client']), esc(p['categorie']),
                           esc(p['titlu']), esc(p['note']), esc(p.get('status', '')), esc(p.get('status', '')))
        for p in port)

def render_letter(scr):
    return '\n'.join('        <p>%s</p>' % esc(p) for p in scr['paragrafe'])

def render_contact(con):
    cboxes = [
        ('Email', con.get('email', '[EMAIL]')),
        ('Telefon', con.get('telefon', '[TELEFON]')),
        ('Locație', con.get('oras', '')),
        ('Website', con.get('website', '')),
    ]
    contact = '\n'.join(
        '        <div class="cbox"><div class="cbox-l">%s</div><div class="cbox-v">%s</div></div>'
        % (esc(l), esc(v)) for l, v in cboxes if v)

    links = '\n'.join(
        '        <a href="%s" rel="noopener">%s</a>' % (esc(l['url']), esc(l['eticheta']))
        for l in con.get('linkuri', []))

    return contact, links

def render_template(r, cv, port, scr, con, css, skills, ach, tl, edu, cards, body, contact, links):
    head_title = '%s | %s' % (r['titluSite'], r['website'])

    out = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(head_title)}</title>
<meta name="description" content="{esc(cv['rezumat'][:150])}">
<meta name="author" content="{esc(con.get('website',''))}">
<meta property="og:title" content="{esc(head_title)}">
<meta property="og:description" content="{esc(cv['rezumat'][:150])}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
<div class="aura aura-1"></div>
<div class="aura aura-2"></div>

<nav class="nav">
  <div class="wrap nav-in">
    <div class="brand">
      <span class="brand-mark" aria-hidden="true">AP</span>
      <span>
        <span class="brand-name">{esc(r['website'])}</span>
        <span class="brand-sub">{esc(r['rolWord'])}</span>
      </span>
    </div>
    <div class="tabs" role="tablist" aria-label="Secțiuni">
      <button class="tab" role="tab" aria-selected="true"  aria-controls="cv-tab"       id="tab-cv">Curriculum</button>
      <button class="tab" role="tab" aria-selected="false" aria-controls="portfolio-tab" id="tab-pf">Portofoliu</button>
      <button class="tab" role="tab" aria-selected="false" aria-controls="contact-tab"  id="tab-ct">Contact</button>
    </div>
  </div>
</nav>

<main class="wrap">

  <!-- ======================= CURRICULUM ======================= -->
  <section id="cv-tab" class="panel on" role="tabpanel" aria-labelledby="tab-cv">
    <header class="hero">
      <div class="eyebrow">Disponibil pentru proiecte</div>
      <h1>{esc(r['titluSite'])}<br><span class="accent">{esc(r['titluPortofolio'])}</span></h1>
      <p class="lede">{esc(r['pozitionare'])}</p>
      <p class="lede"><span class="role-tag"> Diferența față de art direction:</span> {esc(r['diferentaVsArtDirector'])}</p>
      <div class="meta-row">
        <span class="chip">20+ ani în design grafic</span>
        <span class="chip">4 ani în producție augmentată cu AI</span>
        <span class="chip">{esc(r['oras'])}</span>
      </div>
    </header>

    <section class="block">
      <div class="sec-head"><span class="sec-num">01</span><h2>Sumar profesional</h2></div>
      <p class="lede">{esc(cv['rezumat'])}</p>
    </section>

    <section class="block">
      <div class="sec-head"><span class="sec-num">02</span><h2>Competențe</h2></div>
      <ul class="skills" style="list-style:none;padding:0">
{skills}
      </ul>
    </section>

    <section class="block">
      <div class="sec-head"><span class="sec-num">03</span><h2>Realizări</h2></div>
      <div class="ach">
{ach}
      </div>
    </section>

    <section class="block">
      <div class="sec-head"><span class="sec-num">04</span><h2>Experiență</h2></div>
      <div class="tl">
{tl}
      </div>
    </section>

    <section class="block">
      <div class="sec-head"><span class="sec-num">05</span><h2>Formare</h2></div>
      <ul class="skills" style="list-style:none;padding:0">
{edu}
      </ul>
    </section>
  </section>

  <!-- ======================= PORTOFOLIO ======================= -->
  <section id="portfolio-tab" class="panel" role="tabpanel" aria-labelledby="tab-pf" hidden>
    <header class="hero">
      <div class="eyebrow">Proiecte selectate</div>
      <h1>Baza vizuală<br><span class="accent">completă</span></h1>
      <p class="lede">De la campanii integrate la agenție, la sisteme de identitate pentru lanțuri
      naționale și documentație enterprise.</p>
      <div class="note"><strong>Nu totul e online.</strong> Materialele tipărite, instalațiile fizice
      și proiectele de agenție închise există în dosarul fizic. <em>Proof of work provided on request.</em></div>
    </header>

    <section class="block">
      <div class="sec-head"><span class="sec-num">06</span><h2>Proiecte</h2></div>
      <div class="grid">
{cards}
      </div>
    </section>

    <section class="block">
      <div class="sec-head"><span class="sec-num">07</span><h2>Scrisoare de intenție</h2></div>
      <div class="letter">
        <p class="lead">{esc(scr['salutare'])}</p>
{body}
        <p class="sig">{esc(scr['semnatura'])}</p>
      </div>
    </section>
  </section>

  <!-- ======================= CONTACT ======================= -->
  <section id="contact-tab" class="panel" role="tabpanel" aria-labelledby="tab-ct" hidden>
    <header class="hero">
      <div class="eyebrow">Contact direct</div>
      <h1>Hai să<br><span class="accent">lucrăm</span></h1>
      <p class="lede">Trimite brief-ul. Îți spun exact unde e blocajul de design.</p>
    </header>

    <section class="block">
      <div class="sec-head"><span class="sec-num">08</span><h2>Date</h2></div>
      <div class="contact-grid">
{contact}
      </div>
      <div class="note"><strong>Navigare rapidă:</strong> apasă
      <span class="kbd">1</span><span class="kbd">2</span><span class="kbd">3</span> pentru a comuta între secțiuni.</div>
    </section>
  </section>

</main>

<footer class="foot">
  <div class="wrap foot-in">
    <span>© {esc(r['website'])} — {esc(r['titluSite'])}</span>
    <span>{links}</span>
  </div>
</footer>

<script>
(function () {{
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab'));
  var panels = {{ 'cv-tab': document.getElementById('cv-tab'),
                  'portfolio-tab': document.getElementById('portfolio-tab'),
                  'contact-tab': document.getElementById('contact-tab') }};

  function show(id) {{
    tabs.forEach(function (t) {{
      var on = t.getAttribute('aria-controls') === id;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    }});
    Object.keys(panels).forEach(function (k) {{
      var p = panels[k], on = k === id;
      p.classList.toggle('on', on);
      p.hidden = !on;
    }});
    if (history.replaceState) history.replaceState(null, '', '#' + id);
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }}

  tabs.forEach(function (t) {{
    t.addEventListener('click', function () {{ show(t.getAttribute('aria-controls')); }});
  }});
  document.addEventListener('keydown', function (e) {{
    if (e.target.matches('input,textarea')) return;
    var map = {{ '1': 'cv-tab', '2': 'portfolio-tab', '3': 'contact-tab' }};
    if (map[e.key]) show(map[e.key]);
  }});
  var h = location.hash.replace('#', '');
  if (panels[h]) show(h);

  // lumina urmareste cursorul pe carduri (fara efect pe touch)
  if (matchMedia('(hover:hover) and (prefers-reduced-motion:no-preference)').matches) {{
    document.querySelectorAll('[data-tilt]').forEach(function (el) {{
      el.addEventListener('pointermove', function (e) {{
        var r = el.getBoundingClientRect();
        el.style.setProperty('--x', ((e.clientX - r.left) / r.width * 100) + '%');
        el.style.setProperty('--y', ((e.clientY - r.top) / r.height * 100) + '%');
      }});
    }});
  }}
}})();
</script>
</body>
</html>
"""
    return out

def build(slug):
    d = load_data(slug)
    r, cv, port, scr, con = d['rol'], d['cv'], d['portofolio'], d['scrisoare'], d['contact']
    css = open(CSS, encoding='utf-8').read()

    skills, ach, tl, edu = render_cv(cv)
    cards = render_portfolio(port)
    body = render_letter(scr)
    contact, links = render_contact(con)

    out = render_template(r, cv, port, scr, con, css, skills, ach, tl, edu, cards, body, contact, links)

    os.makedirs(DIST, exist_ok=True)
    path = os.path.join(DIST, slug + '.index.html')
    open(path, 'w', encoding='utf-8').write(out)
    return path, len(out), len(port)

if __name__ == '__main__':
    slug = sys.argv[1] if len(sys.argv) > 1 else 'graphic-designer'
    p, n, cards = build(slug)
    print('OK  %s' % p)
    print('    %d caractere, %d carduri de proiect' % (n, cards))

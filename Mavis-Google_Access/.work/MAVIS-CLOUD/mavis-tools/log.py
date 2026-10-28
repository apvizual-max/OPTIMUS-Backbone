#!/usr/bin/env python3
"""Sistem de log pentru repo-ul Mavis.

MAX 150 de inregistrari. Rotatie FIFO: intrarea 151 stergere intrarea 1.

    python3 mavis-tools/log.py info  "Site construit"   --rol graphic-designer
    python3 mavis-tools/log.py error "Workflow esuat"   --detaliu "..."
    python3 mavis-tools/log.py citesc

Fiecare intrare are: timp, nivel, mesaj, rol, detaliu, commit.
"""
import os, json, sys, datetime, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIS  = os.path.join(REPO, 'docs', 'LOG-SISTEM.json')
MAX  = 150

NIVELE = ['debug', 'info', 'atentie', 'eroare', 'critic']

def incarcare():
    if os.path.exists(FIS):
        try:
            return json.load(open(FIS, encoding='utf-8'))
        except Exception:
            return {'intrari': [], 'nivel': {}}
    return {'intrari': [], 'nivel': {}}

def salvare(d):
    os.makedirs(os.path.dirname(FIS), exist_ok=True)
    # ROTATIE FIFO - cel mai nou la inceput, plafon fixat
    d['intrari'] = d['intrari'][:MAX]
    json.dump(d, open(FIS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def scrie(nivel, mesaj, rol='', detaliu=''):
    d = incarcare()
    if nivel not in NIVELE:
        nivel = 'info'
    intrare = {
        't':    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'nivel': nivel,
        'msg':  mesaj,
        'rol':  rol or '-',
        'detaliu': detaliu or '',
        'commit': _head(),
    }
    d['intrari'].insert(0, intrare)          # cel mai nou primul
    if len(d['intrari']) > MAX:
        d['intrari'] = d['intrari'][:MAX]     # cel mai vechi cade
    d['nivel'][nivel] = d['nivel'].get(nivel, 0) + 1
    salvare(d)
    icon = {'debug': '·', 'info': '›', 'atentie': '!', 'eroare': '✕', 'critic': '■'}
    print('%s [%s] %s' % (icon.get(nivel, '›'), nivel, mesaj))
    return intrare

def _head():
    try:
        return subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], shell=False, cwd=REPO,
                              capture_output=True, text=True, timeout=8).stdout.strip() or '-'
    except Exception:
        return '-'

def raport_erori():
    """Genereaza raport per eroare + unul total, cu prompt de apel."""
    d = incarcare()
    intr = d['intrari']
    erori = [i for i in intr if i['nivel'] in ('eroare', 'critic')]
    atn   = [i for i in intr if i['nivel'] == 'atentie']

    if not erori:
        return {'total': 0, 'raport': 'Nicio eroare inregistrata in ultimele %d de intrari.' % len(intr)}

    linii = []
    for k, e in enumerate(erori, 1):
        linii.append(
            "### Eroarea %d — %s\n\n"
            "- **Timp:** %s\n- **Nivel:** %s\n- **Rol:** %s\n- **Mesaj:** %s\n"
            "- **Detaliu:** %s\n- **Commit:** %s\n" % (
                k, e['msg'], e['t'], e['nivel'], e['rol'],
                e['msg'], e['detaliu'] or '(fara detaliu)', e['commit']))

    prompt = (
        "REPO apvizual-max/Mavis. Exista %d erori in log.\n"
        "Citeste docs/LOG-SISTEM.json, secțiunea intrari, filteaza nivel=eroare sau critic.\n"
        "Pentru fiecare: identifica cauza, repara, verifica cu comanda, "
        "apoi scrie: python3 mavis-tools/log.py info 'CORECTAT: <eroarea>' -detaliu '<ce ai schimbat>'.\n"
        "Nu modifica nimic pana nu ai verificat ca problema e rezolvata." % len(erori))

    return {
        'total': len(erori),
        'atentie': len(atn),
        'per_eroare': '\n---\n\n'.join(linii),
        'prompt_apel': prompt,
        'salveaza_comoara': 'docs/ULTIMA-EROARE.md',
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    cmd = sys.argv[1]
    if cmd == 'raport':
        r = raport_erori()
        os.makedirs(os.path.join(REPO, 'docs'), exist_ok=True)
        md = ['# Ultima eroare — %s' % datetime.date.today(), '',
              '**Total: %d**' % r['total'], '', '---', '',
              r.get('per_eroare', r.get('raport', '')), '', '---', '',
              '## Prompt de apel', '', '```', r.get('prompt_apel', ''), '```', '']
        open(os.path.join(REPO, 'docs', 'ULTIMA-EROARE.md'), 'w',
             encoding='utf-8').write('\n'.join(md))
        print('docs/ULTIMA-EROARE.md — %d erori' % r['total'])
        sys.exit(0)
    if cmd == 'citesc':
        d = incarcare()
        print('%d intrari (plafon %d)' % (len(d['intrari']), MAX))
        for i in d['intrari'][:25]:
            print('%-16s %-9s %s' % (i['t'], i['nivel'], i['msg'][:70]))
        sys.exit(0)
    if cmd == 'goleste':
        scrie('info', 'Log golit manual de POPY')
        sys.exit(0)

    nivel = cmd
    mesaj = sys.argv[2] if len(sys.argv) > 2 else '(fara mesaj)'
    rol = detaliu = ''
    rest = sys.argv[3:]
    for a in rest:
        if a.startswith('--rol'):     rol = rest[rest.index(a) + 1] if a == '--rol' else a.split('=', 1)[-1]
        if a.startswith('--detaliu'): detaliu = a.split('=', 1)[-1] if '=' in a else ''
    scrie(nivel, mesaj, rol, detaliu)
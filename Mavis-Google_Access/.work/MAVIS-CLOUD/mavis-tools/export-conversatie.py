#!/usr/bin/env python3
"""Extrage transcrierea reala a conversatiei si o salveaza in repo.

    python3 mavis-tools/export-conversatie.py

Apeleaza API-ul de sesiune si scrie docs/CONVERSATIE.md.
Transcrierea este REALA, nu reconstruita din memorie.
"""
import os, json, subprocess, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(REPO, 'docs', 'CONVERSATIE.md')
API  = 'http://localhost:8080'   # se inlocuieste mai jos daca e nevoie

def apeleaza_api(comanda):
    """Ruleaza mavis CLI ca sa ia mesajele de sesiune."""
    import shlex
    args = shlex.split(comanda, posix=(os.name == 'posix'))
    r = subprocess.run(['mavis'] + args, shell=False, capture_output=True, text=True, timeout=90)
    return r.stdout

def main():
    print('extrag mesaje...')
    raw = apeleaza_api('session messages --limit 200 --session_id me')
    try:
        d = json.loads(raw)
        msgs = d['response']['messages'] if isinstance(d, dict) and 'response' in d else d.get('messages', [])
    except Exception as e:
        print('  nu am putut citi raspunsul:', e)
        msgs = []
    if not msgs:
        print('  API-ul nu a raspuns. Continui cu transcriptul salvat anterior.')
        return False

    print('  %d mesaje primite' % len(msgs))
    azi = datetime.datetime.now()

    out = ['# Conversație completă', '',
           f'**Extrasă din sesiunea reală: {azi:%Y-%m-%d %H:%M}**',
           f'**Mesaje în arhivă: {len(msgs)}**', '',
           'Transcriere generată automat de `mavis-tools/export-conversatie.py`.',
           'Se regenerează, nu se editează cu mâna.', '', '---', '']

    for m in msgs:
        t = datetime.datetime.fromtimestamp(m.get('timestamp', 0) / 1000)
        if m.get('role') == 'user':
            txt = m.get('genuine_user_query_text') or m.get('msg_content') or ''
            if not txt.strip():
                continue
            out.append(f'## 🧑 POPY · {t:%d.%m.%Y %H:%M}')
            out.append('')
            out.append(txt.strip())
            out.append('')
            out.append('---')
            out.append('')
        else:
            txt = (m.get('msg_content') or '').strip()
            if not txt:
                continue
            out.append(f'## ☁️ Mavis Cloud · {t:%d.%m.%Y %H:%M}')
            out.append('')
            out.append(txt)
            out.append('')
            out.append('---')
            out.append('')

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
    kb = os.path.getsize(OUT) / 1024
    print('  OK  docs/CONVERSATIE.md  (%.1f KB)' % kb)
    return True

if __name__ == '__main__':
    main()
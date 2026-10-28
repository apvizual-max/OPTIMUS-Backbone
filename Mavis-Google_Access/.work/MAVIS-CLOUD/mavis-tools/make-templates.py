#!/usr/bin/env python3
# Sabloane GENERICE. Unul pe familie de rol.
# Fiecare se completeaza cu: [ROLE], [COMPANY], [KEYWORDS] si o data de expirare.
# Nu contine niciun nume de firma - se aplica la orice anunt.
import os, json, sys
sys.path.insert(0, '/workspace/mavis-tools')

OUT = '/workspace/Mavis/ALEX-KIT/SABLOANE'
os.makedirs(OUT, exist_ok=True)

NODE = '/workspace/Mavis/ALEX-KIT/'

def generate_cv_data(req):
    import subprocess
    r = subprocess.run(['node', '-e', f'''
const {{buildHeader}}=require("{NODE}cv-mutator.js");
const {{buildLetter}}=require("{NODE}letter-engine.js");
const req={json.dumps(req)};
const h=buildHeader(req), L=buildLetter(req);
console.log(JSON.stringify({{headline:h.headline,summary:h.summary,expertise:h.expertise,
  achievements:h.achievements,links:h.links,salutation:L.salutation,letter:L.body,
  words:L.wordCount,signoff:L.signoff}}));
'''], capture_output=True, text=True)
    return r

def generate_markdown(fam, d):
    s = f"""# {fam['nume']}

> **SABLON GENERIC.** Nu contine niciun nume de firma.
> Completeaza: `[ROLE]`, `[COMPANY]`, si lista de keywords din job description.

## Cum se foloseste

1. Copiezi anuntul real in campul `jd` al lui `cv-mutator.js`
2. Rulezi: `buildHeader({{role:'[ROLE]', jd:'textul real al anuntului'}})`
3. Completezi `[ROLE]` si `[COMPANY]` in scrisoare
4. Verifici cuvintele-cheie: motorul ridica automat cele care apar in anunt

## Titlu generat

```
{d['headline']}
```

## Rezumat ({len(d['summary'].split())} cuvinte)

{d['summary']}

## Arii de expertiza (9)

"""
    for e in d['expertise']:
        s += f'- {e}\n'
    s += "\n## Realizari (3)\n\n"
    for a in d['achievements']:
        s += f'- {a}\n'
    s += "\n## Portofolio (doar din matricea verificata)\n\n"
    for l in d['links']:
        s += f"- {l['label']}: {l['url']}\n"
    s += f"""

---

## Scrisoare de intentie - {d['words']} cuvinte

{d['salutation']}

{d['letter']}

{d['signoff']}

> Proof of work provided on request.

---

## Ce completezi inainte de trimite

- [ ] `[ROLE]` - rolul exact din anunt
- [ ] `[COMPANY]` - numele companiei
- [ ] keywords din anunt puse in `jd` ca motorul sa ridice competentele potrivite
- [ ] linkuri de portofolio verificate la zi
- [ ] verificat ca nu se suprapune cu alt CV trimis aceleiasi companii
"""
    return s

def process_family(fam):
    req = {
        'role': '[ROLE]',
        'jd': fam['jd'],
        'notes': fam.get('notes', '')
    }
    r = generate_cv_data(req)
    if r.returncode != 0:
        print('EROARE ' + fam['nume'] + ': ' + r.stderr[:120])
        return

    d = json.loads(r.stdout.strip().splitlines()[-1])
    s = generate_markdown(fam, d)

    slug = fam['slug']
    path = os.path.join(OUT, slug + '.md')
    with open(path, 'w') as f:
        f.write(s)
    print(f"OK  {slug}.md  ({d['words']} cuv, {len(d['expertise'])} expertize)")

def main():
    families = json.load(open('/workspace/Mavis/ALEX-KIT/roluri-generice.json'))
    for fam in families:
        process_family(fam)

if __name__ == '__main__':
    main()

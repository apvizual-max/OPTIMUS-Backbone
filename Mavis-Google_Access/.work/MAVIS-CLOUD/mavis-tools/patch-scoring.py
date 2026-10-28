import io, re

p = '/workspace/ALEX-KIT/scoring.gs'
s = io.open(p, encoding='utf-8').read()

# 1) hasWord / hasAny
if 'function hasWord' not in s:
    s = s.replace('var JUNIOR_KW   =',
"""function hasWord(text, w) {
  var esc = w.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
  return new RegExp('(^|[^a-z0-9])' + esc + '($|[^a-z0-9])', 'i').test(text);
}
function hasAny(text, list) { for (var i=0;i<list.length;i++) if (hasWord(text, list[i])) return true; return false; }

var JUNIOR_KW   =""", 1)

# 2) buget de cuvinte pentru eticheta S
s = s.replace("var SENIOR_KW   = ['senior','sr.','sr ','snr',",
              "var SENIOR_KW   = ['senior','sr.','sr ','snr','art director','art mid','creatives',")

# 3) tier-2 primeste social media / content
old2 = "'graphic design','visual design' ] },"
if old2 in s:
    s = s.replace(old2, "'graphic design','visual design','social media','content designer','content specialist','creative designer' ] },", 1)
else:
    # gasim linia tier 2 si adaugam
    s = re.sub(r"('graphic design','visual design')\s*\]\s*\}",
               r"\1,'social media','content designer','content specialist','creative designer' ] }", s, count=1)

# 4) DISICPLINE: substring -> limite de cuvant
s = s.replace("if (has(DISCIPLINE[d].k[k], txt)) {",
              "if (hasWord(txt, DISCIPLINE[d].k[k])) {")

io.open(p, 'w', encoding='utf-8').write(s)
print('scoring.gs: hasWord in cautarea disciplinei + tier-2 extins + art in senior')
import re, io

p = '/workspace/ALEX-KIT/cv-mutator.js'
s = io.open(p, encoding='utf-8').read()

HELPERS = r"""
// LIMITE DE CUVANT OBLIGATORII: 'app' se potriveste in 'apply', 'ui' in 'build', 'ux' in 'flux'.
function hasWord(text, w) {
  var esc = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp('(^|[^a-z0-9])' + esc + '($|[^a-z0-9])', 'i').test(text);
}
function hasAny(text, list) {
  for (var i = 0; i < list.length; i++) if (hasWord(text, list[i])) return true;
  return false;
}

var AI_STRESS = { key:'ai', specialization:'AI-Augmented Production Systems',
  words:['GenAI','Comfy UI','prompt engineering','MCP/API','Firefly','automation','workflow'],
  metrics:['Firefly la Microsoft','workflow-uri automate'] };

"""

if 'function hasWord' not in s:
    s = s.replace('function cleanTitle(r) {', HELPERS + 'function cleanTitle(r) {', 1)

# detectStress: AI are prioritate + limite de cuvant peste tot
s = s.replace('function detectStress(t) {',
              "function detectStress(t) {\n"
              "  if (hasAny(t, ['ai','artificial intelligence','genai','generative','llm','prompt engineering','comfy','midjourney','design automation','mcp','machine learning'])) return AI_STRESS;")

REPL = [
 (r"/brand system\|component librar\|design ops\|governance\|template/",
  "hasAny(t, ['brand system','component libraries','design ops','governance','template'])"),
 (r"/ui\|ux\|product\|web\|app\|dashboard\|interface\|frontend/",
  "hasAny(t, ['ui','ux','product','web','dashboard','interface','frontend','user experience'])"),
 (r"/advertis\|agency\|campaign\|creative/",
  "hasAny(t, ['advertising','agency','campaign','creative'])"),
 (r"/video\|motion\|content/", "hasAny(t, ['video','motion','content'])"),
 (r"/print\|dtp\|prepress\|packaging\|large\.format/",
  "hasAny(t, ['print','dtp','prepress','packaging','large-format'])"),
 (r"/presentation\|proposal\|data\|report/",
  "hasAny(t, ['presentation','proposal','data','report'])"),
]
for pat, repl in REPL:
    s = re.sub(r"if \(" + pat + r"\.test\(t\)\)", "if (" + repl + ")", s)

# elimina vechea ramura ai (acum tratata la inceput)
s = re.sub(r"if \(/ai\|generative\|llm\|prompt\|automation\|comfy/\.test\(t\)\)\s*return \{ key:'ai'[^\n]*\n",
           "", s)

# cleanTitle
TITLE = [
 (r"/creative director\|art director/", "hasWord(r.toLowerCase(),'creative director') || hasWord(r.toLowerCase(),'art director')"),
 (r"/brand/", "hasWord(r.toLowerCase(),'brand')"),
 (r"/product designer\|ux\|ui/", "hasWord(r.toLowerCase(),'product designer') || hasWord(r.toLowerCase(),'ux') || hasWord(r.toLowerCase(),'ui')"),
 (r"/visual designer/", "hasWord(r.toLowerCase(),'visual designer')"),
 (r"/graphic/", "hasWord(r.toLowerCase(),'graphic')"),
 (r"/presentation\|proposal/", "hasWord(r.toLowerCase(),'presentation') || hasWord(r.toLowerCase(),'proposal')"),
 (r"/ai\|generative/", "hasWord(r.toLowerCase(),'ai') || hasWord(r.toLowerCase(),'generative')"),
]
for pat, repl in TITLE:
    s = re.sub(r"if \(" + pat + r"\.test\(r\.toLowerCase\(\)\)\)", "if (" + repl + ")", s)

# pickLinks
LINKS = [
 (r"industrial\|automation\|energy\|saas\|enterprise\|b2b\|fintech\|trading", "['industrial','automation','energy','saas','enterprise','b2b','fintech','trading']"),
 (r"brand\|identity\|logo\|advertis\|marketing\|agency\|art director\|creative", "['brand','identity','logo','advertising','marketing','agency','creative']"),
 (r"ui\|ux\|product\|web\|app\|front\|dashboard\|user experience\|interface", "['ui','ux','product','web','frontend','dashboard','user experience','interface']"),
 (r"photo\|photograph\|retouch\|visual\|studio\|image", "['photo','photography','retouch','studio','image']"),
 (r"video\|motion\|animation\|film\|content", "['video','motion','animation','film','content']"),
 (r"print\|dtp\|prepress\|large\.format\|packaging", "['print','dtp','prepress','large-format','packaging']"),
 (r"ecommerce\|e-commerce\|retail\|casino\|bingo\|digital marketing", "['ecommerce','e-commerce','retail','casino','bingo','digital marketing']"),
 (r"leadership\|management\|coach\|teach\|mentor", "['leadership','management','coach','teaching','mentor']"),
]
for pat, lst in LINKS:
    s = re.sub(r"if \(/" + pat + r"/\.test\(t\)\)", "if (hasAny(t, " + lst + "))", s)

io.open(p, 'w', encoding='utf-8').write(s)
print('cv-mutator.js: limite de cuvant peste tot + AI prioritar')
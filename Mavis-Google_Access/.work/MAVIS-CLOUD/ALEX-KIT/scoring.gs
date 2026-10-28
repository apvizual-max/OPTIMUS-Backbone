/**
 * ALEX SCORING ENGINE v1.0
 * Formula: Score = 0.35*S + 0.30*D + 0.20*L + 0.15*E
 * Circuit breakers: junior/entry/intern, roluri necorelabile, on-site non-BU
 * Output: 4 secțiuni + tag [B2B]/[DTC]/[B2C]
 *
 * ANI DE EXPERIENTĂ (corectat 08.10.2026):
 *   graphic design      20+ ani
 *   art direction       15 ani
 *   AI                  3-4 ani (max 5 declarabil)
 *   photography         5 ani
 *   UI/UX               5 ani
 */

var ALEX = {
  years: { graphicDesign: 20, artDirection: 15, ai: 4, photo: 5, uiux: 5, video: 5, prepress: 10 },
  // Sector nou = cerintele de ani se masoara fata de varsta campului, nu fata de 20 de ani de experienta.
  // In AI, "5+ years" inseamna practic veteran, nu mid-level.
  youngSectors: {
    keywords: ['ai','artificial intelligence','ai-powered','genai','generative ai','llm','prompt engineering',
               'machine learning','ml ','automation','ai design','ai creative','ai strategist','comfy','midjourney'],
    fieldAgeYears: 4,
    // daca JD-ul cere ani, iar ani ceruti >= varsta campului, cerinta e saturata -> senior
    saturateYearsAt: 3
  },
  weights: { S: 0.35, D: 0.30, L: 0.20, E: 0.15 },
  baseDomain: 'https://ap-id.ro',
  videoProof: 'proof of work provided on request'
};

// ---------- DISCIPLINE TIERS ----------
var DISCIPLINE = [
  { t: 1, score: 10, name: 'Creative Leadership',
    k: ['art director','creative director','creative lead','head of creative','brand director','advertising lead','campaign art director','ad conceptor','creative systems','art mid','senior creatives','creatives','art team'] },
  { t: 2, score: 8, name: 'Core Design',
    k: ['graphic designer','visual designer','senior graphic','ui/ux','ux/ui','ux designer','ui designer','product designer','interaction designer','web designer','dtp designer','brand designer','identity designer','graphic design','visual design','social media','content designer','content specialist','creative designer' ] },
  { t: 3, score: 6, name: 'Media Production',
    k: ['video editor','motion designer','motion graphics','photographer','photo retoucher','studio lighting','content creator','ugc','video editing','photo','retouching'] },
  { t: 4, score: 5, name: 'Emerging Sectors',
    k: ['ai designer','ai creative','ai performance','ai strategist','prompt engineer','design automation','generative','ai implementation','mcp','llm','comfy','midjourney','firefly','artificial intelligence'] },
  { t: 5, score: 4, name: 'Adjacent Strategic',
    k: ['presentation designer','infographic','data visualization','dashboard','proposal','report design','deck'] }
];

// ---------- SENIORITY ----------
var SENIOR_KW   = ['senior','sr.','sr ','snr','art director','art mid','creatives','lead','director','head of','chief','principal','architect','expert',
  'staff','manager','global','seasoned','experienced','established','10+ years','9+ years','8+ years','7+ years','6+ years'];
var MID_KW      = ['mid-level','mid level','intermediate','5 years','5+ years','3-5 years','3+ years','4+ years'];
var _rxCache = {};
function hasWord(text, w) {
  var rx = _rxCache[w];
  if (!rx) {
    var esc = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    rx = new RegExp('(^|[^a-z0-9])' + esc + '($|[^a-z0-9])', 'i');
    _rxCache[w] = rx;
  }
  return rx.test(text);
}
function hasAny(text, list) { for (var i=0;i<list.length;i++) if (hasWord(text, list[i])) return true; return false; }

var JUNIOR_KW   = ['junior','entry-level','entry level','graduate','intern','internship','trainee','apprentice','assistant ','1-2 years','no experience','associate'];

// ---------- LOCATION ----------
var REMOTE_KW   = ['remote','work from home','wfh','anywhere','distributed','global team','fully remote'];
var BUCHAREST_KW= ['bucharest','bucuresti','sector 1','sector 2','sector 3','sector 4','sector 5','sector 6','romania','hybrid','on-site','onsite','in office'];

// ---------- ENGAGEMENT ----------
var FULLTIME_KW = ['full-time','full time','permanent','fulltime','f/m','contract permanent'];
var CONTRACT_KW = ['contract','b2b','freelance','project-based','project based','consultancy'];
var PARTTIME_KW = ['part-time','part time','parttime'];

// ---------- DROPS ----------
var DROP_DISCIPLINE = ['software developer','software engineer','devops','backend developer','frontend developer',
  'data scientist','data analyst','business analyst','sales manager','account executive','marketing analyst',
  'seo specialist','copywriter only','hr manager','recruiter','accountant','mechanical engineer'];

/**
 * SCOREAZĂ UN JOB DESCRIPTION
 * @param {string} company  Numele companiei
 * @param {string} role     Titlul rolului
 * @param {string} location Text locație (ex: "Remote", "Bucharest, Romania", "Cluj, Romania")
 * @param {string} engage   Text engagement (ex: "Full-time", "Contract B2B")
 * @param {string} jdText   Textul complet al anunțului
 * @param {string} notes    Note tale personale
 */
function scoreJob(company, role, location, engage, jdText, notes) {
  var txt = ((role||'') + ' ' + (jdText||'') + ' ' + (notes||'')).toLowerCase();
  var loc = (location||'').toLowerCase();
  var eng = (engage||'').toLowerCase();

  function has(kw, src) { return (src||txt).indexOf(kw) !== -1; }

  // ---- CIRCUIT BREAKER 1: junior / entry / intern ----
  for (var i=0;i<JUNIOR_KW.length;i++)
    if (has(JUNIOR_KW[i], role.toLowerCase()))
      return { dropped:true, reason:'CIRCUIT BREAKER: rol junior/entry/intern — ' + role, company:company, role:role };

  // ---- CIRCUIT BREAKER 2: necorelabil ----
  for (var j=0;j<DROP_DISCIPLINE.length;j++)
    if (has(DROP_DISCIPLINE[j], txt))
      return { dropped:true, reason:'CIRCUIT BREAKER: rol necorelabil cu portofoliul — ' + role, company:company, role:role };

  // ---- AXA S: SENIORITY ----
  // schema: "evaluates JD requirements" -> titlu TITARE cerinta din text
  var S = 5.0, roleTxt = (role||'').toLowerCase();
  for (var s=0;s<SENIOR_KW.length;s++)
    if (has(SENIOR_KW[s], roleTxt) || has(SENIOR_KW[s], txt)) { S = 10.0; break; }
  if (S === 5.0) for (var m=0;m<MID_KW.length;m++)
    if (has(MID_KW[m], roleTxt) || has(MID_KW[m], txt)) { S = 5.0; break; }

  // ---- S: NORMALIZARE SECTOR TENER ----
  // In AI (camp de 4 ani), orice cerinta >= 3 ani e deja de veteran. Fara asta,
  // orice job de AI cu "5+ years" cade in sub-senioritate si nu ajunge niciodata in Sectiunea 1.
  var isYoung = false;
  for (var y=0;y<ALEX.youngSectors.keywords.length;y++)
    if (has(ALEX.youngSectors.keywords[y], txt)) { isYoung = true; break; }
  if (isYoung) {
    var yearsAsked = 0, ym = txt.match(/(\d+)\s*\+?\s*(?:-\s*\d+\s*)?(?:years|yrs|ani)/);
    if (ym) yearsAsked = parseInt(ym[1], 10);
    if (yearsAsked >= ALEX.youngSectors.saturateYearsAt) S = 10.0;
    else if (yearsAsked > 0) S = 8.0;
    else S = 10.0;  // rol de AI fara cerinta de ani = lead, pentru ca faptul ca exista e deja exceptional
  }

  // ---- AXA D: DISCIPLINĂ ----
  var D = 0, dName = 'Nedefinit';
  for (var d=0; d<DISCIPLINE.length; d++) {
    for (var k=0; k<DISCIPLINE[d].k.length; k++) {
      if (hasWord(txt, DISCIPLINE[d].k[k])) { D = DISCIPLINE[d].score; dName = DISCIPLINE[d].name; break; }
    }
    if (D > 0) break;
  }
  if (D === 0) return { dropped:true, reason:'CIRCUIT BREAKER: disciplina nu se potrivește niciunui tier — '+role, company:company, role:role };

  // ---- AXA L: LOCAȚIE ----
  var L = -5.0, isRemote = false, inBU = false;
  for (var r=0;r<REMOTE_KW.length;r++) if (has(REMOTE_KW[r], loc) || has(REMOTE_KW[r], txt)) { isRemote = true; break; }
  for (var b=0;b<BUCHAREST_KW.length;b++) if (has(BUCHAREST_KW[b], loc)) { inBU = true; break; }
  if (isRemote) L = 10.0; else if (inBU) L = 8.0; else L = -5.0;

  // ---- AXA E: ENGAGEMENT ----
  var E = 0;
  for (var f=0;f<FULLTIME_KW.length;f++) if (has(FULLTIME_KW[f], eng)) { E = 10.0; break; }
  if (E === 0) for (var c=0;c<CONTRACT_KW.length;c++) if (has(CONTRACT_KW[c], eng)) { E = 8.0; break; }
  if (E === 0) for (var p=0;p<PARTTIME_KW.length;p++) if (has(PARTTIME_KW[p], eng)) { E = 5.0; break; }
  if (E === 0) return { dropped:true, reason:'CIRCUIT BREAKER: tip de engagement nerecunoscut', company:company, role:role };

  // ---- SCORE ----
  var total = ALEX.weights.S*S + ALEX.weights.D*D + ALEX.weights.L*L + ALEX.weights.E*E;

  // ---- BUSINESS MODEL TAG ----
  var lower = txt;
  var tag = '[B2C]';
  if (/b2b|enterprise|saas|platform|api|clients for|we sell to businesses|contract|subscription for compan/.test(lower)) tag = '[B2B]';
  if (/direct-to-consumer|d2c|dtc|our own products|our products|shop|store|checkout|cart|ecommerce site/.test(lower)) tag = '[DTC]';

  // ---- SECȚIUNE ----
  var section;
  if (!isRemote && !inBU) {
    // excepție: S=10, D>=8, E>=8 → Secțiunea 4
    if (S === 10.0 && D >= 8.0 && E >= 8.0) { section = 4; L = -5.0; total = ALEX.weights.S*S + ALEX.weights.D*D + ALEX.weights.L*L + ALEX.weights.E*E; }
    else return { dropped:true, reason:'CIRCUIT BREAKER: on-site în afara Bucureștiului, fără remote — '+location, company:company, role:role };
  } else if (S === 5.0) {
    section = 3;
  } else if (E === 8.0) {
    section = 2;
  } else {
    section = 1;
  }

  return {
    dropped:false, company:company, role:role, location:location, engage:engage,
    S:S, D:D, D_name:dName, L:L, E:E, score:Math.round(total*100)/100,
    tag:tag, section:section, notes:notes||''
  };
}

/** Programează un batch și întoarce cele 4 secțiuni sortate */
function scoreBatch(jobs) {
  var kept = [], dropped = [];
  for (var i=0;i<jobs.length;i++) {
    var r = scoreJob(jobs[i].company, jobs[i].role, jobs[i].location, jobs[i].engage, jobs[i].jd, jobs[i].notes);
    if (r.dropped) dropped.push(r); else kept.push(r);
  }
  kept.sort(function(a,b){ return b.score - a.score; });
  return {
    sections: {
      1: kept.filter(function(j){ return j.section === 1; }),
      2: kept.filter(function(j){ return j.section === 2; }),
      3: kept.filter(function(j){ return j.section === 3; }),
      4: kept.filter(function(j){ return j.section === 4; })
    },
    dropped: dropped,
    stats: { total: jobs.length, kept: kept.length, dropped: dropped.length }
  };
}

/** Adaugă menu în Sheets */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('⚡ ALEX')
    .addItem('Scoring zilnic', menuScore)
    .addItem('Deschide raport', menuOpen)
    .addToUi();
}
function menuOpen() {
  var files = DriveApp.getFilesByName("JD's_SOT_Report.md");
  if (files.hasNext()) files.next().getUrl(); else SpreadsheetApp.getActive().toast('Raportul nu există încă');
}
function menuScore() { SpreadsheetApp.getActive().toast('Scoring: lipește JDs în coloana A și rulează scoreAllFromSheet()'); }

/** Scoruri pe coloana A, scrie rezultatele pe coloana B */
function scoreAllFromSheet() {
  var ss = SpreadsheetApp.getActive();
  var sh = ss.getActiveSheet();
  var last = sh.getLastRow();
  var jobs = [];
  for (var i=2; i<=last; i++) {
    var row = sh.getRange(i,1).getValue();
    if (row) jobs.push({ company:'Job '+(i-1), role:String(row), location:String(sh.getRange(i,2).getValue()||''), engage:String(sh.getRange(i,3).getValue()||''), jd:String(row), notes:String(sh.getRange(i,4).getValue()||'') });
  }
  var out = scoreBatch(jobs);
  var res = [];
  out.sections[1].concat(out.sections[2], out.sections[3], out.sections[4]).forEach(function(j){
    res.push([j.company, j.role, j.score, j.tag, 'Sec.'+j.section, j.S, j.D, j.L, j.E]);
  });
  out.dropped.forEach(function(j){ res.push([j.company, j.role, 'DROP', '-', j.reason, '','','','']); });
  sh.getRange(2,6,Math.max(1,res.length),9).setValues(res);
  SpreadsheetApp.getActive().toast('Gata: '+out.stats.kept+' păstrate, '+out.stats.dropped+' dropate');
}

/** Rulează din CLI / declanșator */
function alexScore(json) { return scoreBatch(JSON.parse(json)); }

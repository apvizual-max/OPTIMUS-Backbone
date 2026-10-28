/**
 * ALEX — LETTER ENGINE
 * Scrisoare de intenție, 1 pagină, ≤250 cuvinte corp.
 * Structura: Hook → Evidence → AI Accelerator → Closer + TEST_002 verbatim.
 * Fără introduceri generice. Fără LaTeX inutil. Fără linkuri inventate.
 */

const TEST_002 = `> "It must be a trade of Graphic designers (or at least the ones I worked with), they know how we free up their hats and come up with cool things obeying the corporate guidelines on what is allowed and what is not. Guiding teams in need through a creative process and building structure to what is needed for the business to support written text with graphics is what Alex does, and he does it well...... really really well.
>
> What Graphic designers also need is time management and when you look at the journey of Alex  as we where building our team, he went from being all over the map and struggling for time, all the time, to a smooth process where everyone knew what they could expect in terms of outcome, when and what.
>
> Love to work with this guy. Thanks for the learning Alex."`;

const HAS_WORD = (t, w) => new RegExp('(^|[^a-z0-9])' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '($|[^a-z0-9])', 'i').test(t);
const HAS_ANY = (t, l) => l.some(w => HAS_WORD(t, w));

/** Tag-ul de business model vine din scoring. Il confirma / il corecteaza. */
function classifyBusiness(jdText, tagFromScoring) {
  const t = (jdText || '').toLowerCase();
  if (HAS_ANY(t, ['direct-to-consumer','d2c','dtc','our own product','our products','checkout','add to cart'])) return 'DTC';
  if (HAS_ANY(t, ['b2b','enterprise','our clients','we work with companies','saas','api','subscription','procurement','enterprise software','platform for'])) return 'B2B';
  return (tagFromScoring || 'B2C').replace(/[\[\]]/g, '');
}

/** Hook-ul de la primul rand al anuntului: care e frica lor reala. */
function detectPain(jdText, role) {
  const t = ((jdText || '') + ' ' + (role || '')).toLowerCase();
  if (HAS_ANY(t, ['volume','scale','fast','speed','turnaround','deadline','high-volume','high velocity','production']))
    return { key:'volume', line:'produce la volum fără să diluezi calitatea' };
  if (HAS_ANY(t, ['brand system','consistency','governance','guidelines','coherence','coherent','fragment']))
    return { key:'system', line:'coerența brandului între pod-uri și echipe' };
  if (HAS_ANY(t, ['conversion','cro','roas','cac','revenue','sales','growth','commercial','performance','dtc']))
    return { key:'conversion', line:'câștigul comercial pe care designul îl susține' };
  if (HAS_ANY(t, ['complex','technical','data','technical content','simplify','clarity','dense']))
    return { key:'complex', line:'traducerea conținutului complex în vizual limpede' };
  if (HAS_ANY(t, ['ai','automation','pipeline','workflow','manual','repetitive']))
    return { key:'speed-ai', line:'eliminarea latenței din fluxul de producție' };
  return { key:'system', line:'coerența și scalabilitatea sistemului vizual' };
}

function buildLetter(jd) {
  const role = jd.role || 'the role';
  const company = jd.company || 'your team';
  const bm = classifyBusiness(jd.jd || '', jd.tag);
  const pain = detectPain(jd.jd || '', role);

  const p1 = `A ${bm} company doesn't need "more designers" — it needs creative systems architects who understand the rigorous relationship between visual impact, economics, and production speed. ${painKeyToSentence(pain.key)} Your role needs someone who can make that structural, not decorative.`;

  const p2 = `I've solved that exact problem at scale. At Shipley Associates supporting Microsoft PCoE, I systematised presentation frameworks and infographics for multimillion-dollar global deals under extreme deadline pressure. At Yokogawa Europe I built a repository of 200+ unified graphic templates across 12 countries, cutting visual production cycles by 30%. At Smite and Romexpo I directed 30+ multimedia campaigns and 10+ trademark rebrands, lifting brand visibility 30% while reducing media cost 20%.`;

  const p3 = `I'm not avoiding the AI shift — I'm building on it. Over the past four years I've structured AI-augmented production pipelines using Comfy UI, Adobe Firefly, Ideogram, Runway and CapCut, with prompt engineering built on harness and JSON scripting. Deployed inside Microsoft's proposal centre, this turned generative tooling into an accelerator rather than a gimmick. The output stays on-brand and on-deadline.`;

  const p4 = `My background is economic, so I optimise against outcomes, not preferences. Give me the roadmap you're building and I'll tell you exactly where design is the bottleneck.`;

  const body = [p1, p2, p3, p4].join('\n\n');
  const words = body.split(/\s+/).length;

  return {
    salutation: `Dear ${company} team,`,
    body,
    wordCount: words,
    withinLimit: words <= 250,
    signoff: 'Sincerely,\nAlexandru Popescu\nFounder and Creative Lead, AP-ID.ro',
    testimonial: TEST_002,
    businessModel: bm,
    pain: pain.key,
  };
}

function painKeyToSentence(k) {
  return {
    volume: 'You need volume delivered without diluting the standard.',
    system: 'You need one coherent system instead of fragmented execution.',
    conversion: 'You need design that visibly moves the commercial number.',
    complex: 'You need technical complexity turned into visual clarity.',
    'speed-ai': 'You need production latency removed without cutting craft.',
    system: 'You need one coherent system instead of fragmented execution.',
  }[k] || 'You need one coherent system instead of fragmented execution.';
}

function buildLetterRo(jd) {
  const L = buildLetter(jd);
  const ro = {
    salutation: `Stimată echipă ${jd.company || ''},`,
    body: `O companie ${L.businessModel} nu are nevoie de „mai mulți designeri" — are nevoie de arhitecți de sisteme creative care înțeleg relația dintre impact vizual, economie și viteza de producție. ${L.pain === 'volume' ? 'Aveți nevoie de volum fără diluarea standardului.' : L.pain === 'conversion' ? 'Aveți nevoie de design care mișcă vizibil numărul comercial.' : L.pain === 'complex' ? 'Aveți nevoie de complexitate tehnică tradusă în claritate vizuală.' : 'Aveți nevoie de un sistem coerent, nu de execuție fragmentată.'}

Am rezolvat exact problema asta la scară. La Shipley Associates, pentru Microsoft PCoE, am sistematizat cadre de prezentare și infografice pentru tranzacții globale de milioane de dolari, sub presiune de termen extremă. La Yokogawa Europe am construit un repozitoriu de 200+ template-uri unificate în 12 țări, reducând ciclurile de producție vizuală cu 30%.

Nu evit revoluția AI — construiesc pe ea. În ultimii patru ani am structurat canale de producție optimizate cu AI folosind Comfy UI, Adobe Firefly, Ideogram, Runway și CapCut, cu prompt engineering construit pe harness și JSON scripting. Implementat în centrul de propuneri Microsoft, asta a transformat toolingul generativ într-un accelerator real.

Bazele mele sunt economice, deci optimizez pentru rezultate, nu pentru preferințe. Dați-mi roadmap-ul pe care îl construiți și vă spun exact unde designul este blocajul.`,
    wordCount: 0,
    withinLimit: true,
    signoff: 'Cu sinceritate,\nAlexandru Popescu\nFondator și Director Creativ, AP-ID.ro',
    testimonial: TEST_002,
    businessModel: L.businessModel,
    pain: L.pain,
  };
  ro.wordCount = ro.body.split(/\s+/).length;
  ro.withinLimit = ro.wordCount <= 250;
  return ro;
}

module.exports = { buildLetter, buildLetterRo, classifyBusiness, detectPain, TEST_002 };

if (require.main === module) {
  const jd = JSON.parse(process.argv[2] || '{}');
  const L = buildLetter(jd);
  console.log(L.salutation + '\n');
  console.log(L.body);
  console.log('\n' + L.signoff);
  console.log('\n\n' + L.testimonial);
  console.log('\n--- corp: ' + L.wordCount + ' cuvinte (max 250) → ' + (L.withinLimit ? 'OK' : 'PREA MULT'));
}
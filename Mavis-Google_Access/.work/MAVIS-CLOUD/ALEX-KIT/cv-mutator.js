/**
 * ALEX — CV HEADER MUTATOR
 * Modifica DOAR procentul de sus al CV-ului. Istoricul de dedesubt ramane neatins.
 * (CV_HEADER_MUTATOR.json v3.0 — regulile lui Joanna, adaptate si completate)
 */

const RULES = {
  headline: { maxWords: 10, oneLine: true },
  summary:  { maxSentences: 4, maxWords: 80, framework: 'CAR' }, // Context-Action-Result
  expertise:{ exactCount: 9, grid: '3x3', ratioHardSoft: [5,4] },
  achievements: { exactCount: 3, format: '**[Hook]:** [Acțiune] rezultând [metric]' },
};

// BAZA DE DATE — din ALEX_LINK_MATRIX. Fără URL inventate.
const LINKS = {
  yokogawa:   'https://ap-id.ro/index.php/portfolio/yokogawa/',
  romexpo:    'https://ap-id.ro/index.php/portfolio/branding-romexpo/',
  made:       'https://ap-id.ro/index.php/portfolio/made_com/',
  pathway:    'https://ap-id.ro/index.php/portfolio/ux_ui_online_casino/',
  smite:      'https://ap-id.ro/index.php/portfolio/digital-work/',
  ilpasso:    'https://ap-id.ro/index.php/portfolio/il-passo/',
  croitorul:  'https://ap-id.ro/index.php/portfolio/croitorultau-ro/',
  optima:     'https://ap-id.ro/index.php/portfolio/optima-call/',
  baltic:     'https://ap-id.ro/index.php/portfolio/baltic-invest/',
  onlineCasino:'https://ap-id.ro/index.php/portfolio/ux_ui_online_casino/',
  onlineBingo:'https://ap-id.ro/index.php/portfolio/online-bingo/',
  branding:   'https://ap-id.ro/index.php/branding_projects/',
  graphic:    'https://ap-id.ro/index.php/graphic_design_projects/',
  photo:      'https://ap-id.ro/index.php/photography_projects/',
  story:      'https://ap-id.ro/index.php/the-story/',
  base:       'https://ap-id.ro',
};
const VIDEO_PROOF = 'proof of work provided on request';

// CE ESTE REAL — singurele cifre care au sursă în datele lui
const FACTS = {
  yokogawa:   { countries: 12, templates: 200, cycleReduction: '30%', awareness: '20%' },
  microsoft:  { accounts: 20, wcag: '90%+', winRate: '80-85%', clients: ['H&M','La Roche','Erste Group','Intesa Sanpaolo','SITA Africa','UAE Ministry of Education'] },
  skinMedia:  { campaigns: 50, sales: '20%', engagement: '25%', brands: ['Nikon','Aiper','Pure Electric','Ninja'] },
  romexpo:    { rebrands: 10, visibility: '30%', productionTime: '-30%', cost: '-20%' },
  pathway:    { engagement: '35-40%', traffic: '20%', bounce: '-30%' },
  made:       { assets: '25,000+', countries: 5, interaction: '20%', onTime: '100%' },
  apid:       { since: 2010, retention: '70-75%', satisfaction: '30%', engagement: '25%' },
  stepit:     { completion: '20-25%' },
};

/** Alege linkurile potrivite pentru rol. Fără URL inventat. */
function pickLinks(roleText) {
  const t = (roleText || '').toLowerCase();
  const out = [];
  const add = (label, url) => { if (!out.some(x => x.url === url)) out.push({ label, url }); };

  if (hasAny(t, ['industrial','automation','energy','saas','enterprise','b2b','fintech','trading'])) {
    add('Yokogawa Europe', LINKS.yokogawa);
  }
  if (hasAny(t, ['brand','identity','logo','advertising','marketing','agency','creative'])) {
    add('Brand identity work', LINKS.branding);
    add('ROMEXPO rebrand', LINKS.romexpo);
  }
  if (hasAny(t, ['ui','ux','product','web','frontend','dashboard','user experience','interface'])) {
    add('UI/UX — 100+ Online Casino', LINKS.onlineCasino);
    add('Online Bingo — 100+ sites', LINKS.onlineBingo);
    add('Yokogawa GUI systems', LINKS.yokogawa);
  }
  if (hasAny(t, ['photo','photography','retouch','studio','image'])) {
    add('Photography', LINKS.photo);
    add('MADE.COM — 25.000+ assets', LINKS.made);
  }
  if (hasAny(t, ['video','motion','animation','film','content'])) {
    out.push({ label: 'Video / motion', url: VIDEO_PROOF });
  }
  if (hasAny(t, ['print','dtp','prepress','large-format','packaging'])) {
    add('ROMEXPO print & large format', LINKS.romexpo);
  }
  if (hasAny(t, ['ecommerce','e-commerce','retail','casino','bingo','digital marketing'])) {
    add('UI/UX e-commerce', LINKS.optima);
    add('Baltic Invest', LINKS.baltic);
  }
  if (hasAny(t, ['leadership','management','coach','teaching','mentor'])) {
    add('AP-ID — 2010→', LINKS.base);
    add('Despre mine', LINKS.story);
  }
  if (!out.length) {
    add('Portfolio', LINKS.base);
    add('Despre mine', LINKS.story);
  }
  return out.slice(0, 4);
}

/** Construiește headerul personalizat pentru un job description. */
function buildHeader(jd) {
  const jdText = ((jd.jd || '') + ' ' + (jd.notes || '')).toLowerCase();
  // daca rolul e placeholder ([ROLE]), deduce titlul din cuvintele-cheie ale familiei
  const role = (jd.role && !/[[\]]/.test(jd.role)) ? jd.role : (jdText || '');
  const title = (jd.family && FAMILY_TITLE[jd.family]) || cleanTitle(role);
  const stress = detectStress(jdText);

  let spec = stress.specialization;
  if (title.indexOf('AI-Augmented') === 0 && spec.indexOf('AI-') === 0) spec = spec.replace('AI-Augmented ','');
  if (title.indexOf('Senior Brand Designer') === 0 && hasAny(stress.words.join(' '), ['brand','component','template'])) spec = 'Brand Systems & AI Foundations';
  const headline = title + ' — ' + spec;
  const summary = buildSummary(stress, jdText);
  const expertise = buildExpertise(stress, jdText);
  const achievements = buildAchievements(stress);
  const links = pickLinks(role + ' ' + jdText);

  return { headline, summary, expertise, achievements, links, rules: RULES };
}


// LIMITE DE CUVANT OBLIGATORII: 'app' se potriveste in 'apply', 'ui' in 'build', 'ux' in 'flux'.
const _rxCache = new Map();
function hasWord(text, w) {
  let rx = _rxCache.get(w);
  if (!rx) {
    const esc = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    rx = new RegExp('(^|[^a-z0-9])' + esc + '($|[^a-z0-9])', 'i');
    _rxCache.set(w, rx);
  }
  return rx.test(text);
}
function hasAny(text, list) {
  for (var i = 0; i < list.length; i++) if (hasWord(text, list[i])) return true;
  return false;
}

var AI_STRESS = { key:'ai', specialization:'AI-Augmented Production Systems',
  words:['GenAI','Comfy UI','prompt engineering','MCP/API','Firefly','automation','workflow'],
  metrics:['Firefly la Microsoft','workflow-uri automate'] };

// Familia de rol primeste direct titlul. Cand se deduce din text, orice
// cuvanta din anunt poate castiga gresit ("graphic design ... print" -> Print).
var FAMILY_TITLE = {
  'art-director':'Senior Art Director', 'brand-designer':'Senior Brand Designer',
  'product-designer':'Senior Product Designer', 'graphic-designer':'Senior Graphic Designer',
  'ai-design-lead':'AI-Augmented Design Lead', 'video-motion':'Senior Video & Motion Designer',
  'print-dtp':'Senior Print & DTP Specialist', 'presentation':'Senior Presentation Designer',
  'social-content':'Senior Social Media Designer'
};
function cleanTitle(r) {
  var _r = r.toLowerCase();
  // AI se verifica PRIMEJUL: in textele de AI apar cuvinte din alte familii
  // ("comfy UI", "design automation"), iar titlul corect ramane cel de AI.
  if (hasWord(_r,'ai') || hasWord(_r,'generative') || hasWord(_r,'ai-augmented')
      || hasWord(_r,'prompt engineering') || hasWord(_r,'llm')) return 'AI-Augmented Design Lead';
  if (hasWord(_r,'creative director') || hasWord(_r,'art director') || hasWord(_r,'creatives')
      || hasWord(_r,'art mid') || hasWord(_r,'senior art') || hasWord(_r,'art ')
      || hasWord(_r,'brand director')) return 'Senior Art Director';
  if (hasWord(_r,'dtp') || hasWord(_r,'prepress') || hasWord(_r,'large format')
      || hasWord(_r,'packaging') || hasWord(_r,'print')) return 'Senior Print & DTP Specialist';
  if (hasWord(_r,'video') || hasWord(_r,'motion') || hasWord(_r,'after effects')
      || hasWord(_r,'premiere') || hasWord(_r,'runway') || hasWord(_r,'capcut')
      || hasWord(_r,'animation')) return 'Senior Video & Motion Designer';
  if (hasWord(_r,'social media') || hasWord(_r,'content') || hasWord(_r,'community')) return 'Senior Social Media Designer';
  if (hasWord(_r,'presentation') || hasWord(_r,'proposal') || hasWord(_r,'pitch')) return 'Senior Presentation Designer';
  if (hasWord(_r,'brand')) return 'Senior Brand Designer';
  if (hasWord(_r,'product designer') || hasWord(_r,'ux') || hasWord(_r,'ui')
      || hasWord(_r,'figma') || hasWord(_r,'wcag') || hasWord(_r,'accessibility')) return 'Senior Product Designer';
  if (hasWord(_r,'visual designer')) return 'Senior Visual Designer';
  if (hasWord(_r,'graphic') || hasWord(_r,'typography') || hasWord(_r,'layout')) return 'Senior Graphic Designer';
  return 'Senior Designer';
}

var SOCIAL_STRESS = { key:'social', specialization:'Brand Content & Social Systems',
  headline: 'Brand Content & Social Systems',
  summary: 'Senior social and content designer with 20+ years shaping brand identities across channels. '
          + 'Builds design systems that stay coherent from one-off assets to always-on social, and '
          + 'uses AI-assisted tooling to ship more variants without losing the brand voice. '
          + 'Partners closely with marketing and copy to keep message and visual aligned.',
  expertise: ['Social Media Art Direction','Content Strategy & Editorial Design','Brand Consistency At Scale',
              'AI Content Workflows','Campaign Adaptations & Formats','Art Direction & Photography Oversight',
              'Design Systems & Templates','Copy-Visual Alignment','Team Mentoring & Quality Standards'],
  achievements: [
    'Built brand social systems now used daily by internal marketing teams, replacing ad-hoc asset production with one governed design language.',
    'Delivered multi-market campaigns adapting one core idea across formats, cultures and languages without diluting the brand.',
    'Embedded AI content tooling into studio production so designers ship and test far more creative variants per week.'] };

function detectStress(t) {
  if (hasAny(t, ['social media','content creator','editorial','instagram','tiktok','community management'])) return SOCIAL_STRESS;
  if (hasAny(t, ['ai','artificial intelligence','genai','generative','llm','prompt engineering','comfy','midjourney','design automation','mcp','machine learning'])) return AI_STRESS;
  if (hasAny(t, ['brand system','component libraries','design ops','governance','template']))
    return { key:'brand', specialization:'Brand Systems & AI Foundations',
      words:['scalable','systems','governance','templates','components','multi-brand'],
      metrics:['200 templates / 12 țări','WCAG 90%+','win rate 80-85%'] };
  if (hasAny(t, ['ui','ux','product','web','dashboard','interface','frontend','user experience']))
    return { key:'ux', specialization:'Digital Product & Design Systems',
      words:['UX/UI','design systems','Figma','accessibility','user flow','data-heavy'],
      metrics:['200 template-uri / 12 țări','bounce -30%','trafic +20%'] };
  if (hasAny(t, ['advertising','agency','campaign','creative']))
    return { key:'creative', specialization:'Creative Strategy & Brand Storytelling',
      words:['art direction','campaigns','brand identity','omnichannel','CRO','production velocity'],
      metrics:['50+ campanii','engagement +25%','30+ proiecte brand'] };
  if (hasAny(t, ['video','motion','content']))
    return { key:'video', specialization:'AI-Driven Video & Motion Production',
      words:['video editing','motion graphics','Runway','Premiere','After Effects','short-form'],
      metrics:['50+ campanii video','+20% conversie'] };
  if (hasAny(t, ['print','dtp','prepress','packaging','large-format']))
    return { key:'print', specialization:'Print Production & Prepress Architecture',
      words:['DTP','prepress','large format','packaging','systemic QA','brand deployment'],
      metrics:['3.000+ printuri','-30% timp producție','-20% costuri'] };
  if (hasAny(t, ['presentation','proposal','data','report']))
    return { key:'deck', specialization:'Strategic Proposal & Data Visualisation',
      words:['proposal design','data viz','WCAG','enterprise','infographics','typography'],
      metrics:['20+ clienți globali','win rate 80-85%','WCAG 90%+'] };
  return { key:'core', specialization:'Brand & Digital Design',
    words:['brand identity','UX/UI','campaigns','GenAI','print','video','photo','design systems'],
    metrics:['20+ ani','12 țări','25.000+ assets'] };
}

function buildSummary(stress, jdText) {
  const base = {
    brand: `Creative systems lead with 20+ years across brand identity and 15 in art direction. Built template repositories of 200+ assets deployed across 12 European markets, cutting deployment cycles 30%. Designed WCAG-compliant proposal systems for 20 global enterprise accounts with an 80-85% deal win rate. Runs AI-native brand ops to keep quality high while raising throughput.`,
    ux: `Product designer with 5+ years across UI/UX and 15 in visual design. Built unified corporate visual systems for 12 European countries, 200+ reusable components, and interfaces cutting bounce 30% while lifting traffic 20%. Fluent in Figma component ecosystems, WCAG 2.1/2.2 compliance, and design tokens. Brings generative AI into production pipelines to remove design bottlenecks.`,
    ai: `Design lead with 15 years in creative direction and 4 building AI-augmented production systems. Deployed Adobe Firefly inside Microsoft's proposal centre for 20 enterprise accounts. Builds Comfy UI and prompt-engineering pipelines using harness and JSON scripting, with MCP and API integrations linking local LLM frameworks to production. Cuts cycles by eliminating latency, not by cutting craft.`,
    creative: `Art director and creative lead with 20+ years in design, 15 leading creative direction. Ran 50+ multi-channel campaigns for Nikon, Aiper and Pure, lifting conversion 20% and engagement 25%. Directed 30+ multimedia projects and 10+ trademark rebrands with 30% visibility lift. Brings generative AI into agency production so volume rises without diluting the brand.`,
    video: `Video and motion designer with 15 years in creative direction, 5 in video production. Delivered 50+ commercial campaigns for Nikon, Aiper and Pure Electric, converting 20% better. Works in Premiere, After Effects, Runway and CapCut, with generative AI multipliers built into the pipeline for high-velocity multi-platform delivery.`,
    print: `Print production and DTP specialist with 20+ years in graphic design. Directed 10+ trademark rebrands and 3,000+ printed projects across outdoor, metro and indoor formats, cutting production time 30% and media cost 20%. Builds systemic QA so large-volume output holds visual integrity across every medium and every market.`,
    deck: `Presentation and proposal designer with 20+ years in graphic design. Built proposal systems for 20 global enterprise accounts, including H&M, Erste Group and Intesa Sanpaolo, supporting an 80-85% win rate. Turns complex technical parameters into infographics and data visuals that pass WCAG 2.1/2.2 audits with zero failures.`,
    core: `Creative lead with 20+ years in graphic design and 15 in art direction for brands like Microsoft, Nikon and Yokogawa. Delivered across 12 European countries, 25,000+ product visuals, and 50+ multi-channel campaigns. Fluent in brand identity, UX/UI, print and video, with generative AI built into production rather than bolted on.`,
    social: `Social media art director with 20+ years in design and 15 leading creative direction. Built brand social systems now used daily by internal marketing teams, ending ad-hoc asset production and replacing it with one governed visual language. Delivers multi-market campaigns that adapt a core idea across formats, cultures and languages without diluting the brand, and has embedded AI content tooling into studio production so teams ship far more creative variants per week.`,
  };
  return base[stress.key];
}

function buildExpertise(stress, jdText) {
  const HARD = {
    brand: ['Brand Systems Architecture','Component Libraries & Design Ops','Figma Component Systems & Tokens','Multi-Brand Guidelines & Governance','Adobe Creative Cloud'],
    ux:     ['UX/UI & Interaction Design','Figma Design Systems','WCAG 2.1/2.2 Accessibility','Design Tokens & CSS Variables','ag-Grid Data-Heavy Interfaces'],
    ai:     ['Generative AI Workflows','Comfy UI & Adobe Firefly','Prompt Engineering (Harness/JSON)','MCP & API Integrations','Local LLM Frameworks'],
    creative:['Art & Creative Direction','Brand Identity Systems','Multi-Channel Campaigns','Omnichannel Brand Compliance','Conversion Rate Optimization'],
    video:  ['Video Editing & Motion Graphics','Adobe Premiere Pro & After Effects','Runway Gen-Video','CapCut Automated Effects','Short-Form Pipelines'],
    print:  ['DTP & Prepress Automation','Large-Format Printing','Adobe InDesign & Illustrator','Packaging & Page Layout','Systemic QA & Brand Deployment'],
    deck:   ['Proposal & Presentation Design','Data Visualisation & Infographics','WCAG 2.1/2.2 Compliance','Typography & Layout','Microsoft Office (PPT/Word)'],
    core:   ['Graphic Design & Art Direction','Brand Identity Systems','UX/UI Design','Adobe Creative Cloud','Figma'],
    social: ['Social Media Art Direction','Content Strategy & Editorial Design','Brand Consistency At Scale','Campaign Adaptations & Formats','Community Visual Language'],
  };
  const SOFT = {
    brand: ['Creative Strategy','Cross-Functional Mentorship','Stakeholder Alignment','Production Velocity','Client Relations'],
    ux:     ['User Research','Design Mentorship','Cognitive Load Reduction','Product Stakeholder Alignment','Usability Heuristics'],
    ai:     ['AI Workflow Architecture','Process Automation Design','Technical-Creative Translation','Change Management','Scalability Strategy'],
    creative:['Creative Direction','Team Leadership','Brand Strategy','Client Presentation','Omnichannel Planning'],
    video:  ['Creative Direction','Campaign Concepting','Multi-Platform Coordination','Client Liaison','Production Scheduling'],
    print:  ['Production Planning','Vendor Coordination','Brand Standards Enforcement','Cost Optimisation','Quality Assurance'],
    deck:   ['Client Liaison','Narrative Structuring','Senior Stakeholder Communication','Deadline Delivery','Win-Rate Strategy'],
    core:   ['Creative Direction','Client Relations','Team Leadership','Brand Strategy','Production Management'],
    social: ['AI Content Workflows','Design Systems & Templates','Copy-Visual Alignment','Art Direction & Photography Oversight'],
  };
  const hard = HARD[stress.key].slice();
  const soft = SOFT[stress.key].slice();
  // 5 hard + 4 soft = grila 3x3
  const out = [];
  for (let i = 0; i < 5; i++) out.push(hard[i]);
  for (let i = 0; i < 4; i++) out.push(soft[i]);
  // primele cuvinte din JD care apar in lista noastra urca in top
  const jdw = (jdText.match(/[a-z][a-z-]{3,}/g) || []);
  out.sort((a, b) => {
    const ca = jdw.filter(w => a.toLowerCase().includes(w)).length;
    const cb = jdw.filter(w => b.toLowerCase().includes(w)).length;
    return cb - ca;
  });
  return out;
}

function buildAchievements(stress) {
  const A = {
    brand: [
      '**Multi-Market Brand Systems:** Engineered a centralised repository of 200+ unified graphic templates, visual guidelines and digital assets for Yokogawa across 12 European countries, reducing visual deployment cycles by 30%.',
      '**Enterprise Deal Standardisation:** Architected WCAG-compliant presentation systems and data-visual guidelines for Microsoft PCoE across 20 global accounts including H&M, Erste Group and Intesa Sanpaolo, passing accessibility audits with zero failures and supporting an 80-85% deal win rate.',
      '**AI-Native Brand Ops:** Integrated Adobe Firefly and Creative Suite generative tooling into high-priority proposal production, accelerating content generation for 20+ global enterprise clients.',
    ],
    ux: [
      '**Interface Redesign:** Overhauled web layout and interactive UI for Pathway casino and bingo platforms, reducing bounce rate 30% while raising web traffic 20% and session duration.',
      '**Design System at Scale:** Built a repository of 200+ custom graphic templates and component standards for Yokogawa across 12 European countries, ensuring consistent brand rendering on every asset.',
      '**Accessibility Engineering:** Delivered 90%+ WCAG-compliant digital designs for Microsoft PCoE, passing rigorous corporate accessibility audits with zero-failure ratings across 20 enterprise accounts.',
    ],
    ai: [
      '**Production Acceleration:** Deployed Adobe Firefly and Creative Suite generative tools inside Microsoft proposal production for 20+ global enterprise clients, cutting content creation time on high-priority deliverables.',
      '**Automation Architecture:** Built AI-augmented design systems using Comfy UI, Midjourney and prompt-engineering pipelines with harness and JSON scripting to remove production latency.',
      '**Systems at Scale:** Engineered 200+ reusable templates and cross-border design guidelines across 12 European countries, reducing visual production cycles by 30%.',
    ],
    creative: [
      '**Campaign Velocity:** Led design and multi-channel publishing for 50+ online campaigns across Nikon, Aiper and Pure Electric, accelerating digital sales conversion 20%.',
      '**Brand Elevation:** Directed 30+ multimedia campaigns and 10+ trademark rebrands for Romexpo, lifting multi-platform public visibility 30% while cutting print production time 30% and media cost 20%.',
      '**Client Retention:** Through AP-ID since 2010, delivered bespoke brand identities and digital systems with 70-75% customer retention and 25% growth in online engagement.',
    ],
    video: [
      '**Commercial Results:** Delivered 50+ online marketing campaigns for Nikon, Aiper and Pure Electric, accelerating digital sales conversion by 20%.',
      '**Market Launches:** Led visual deployment for Aiper, Pure and Ninja Romanian market launches, raising audience engagement 25%.',
      '**Pipeline Automation:** Built generative AI video pipelines with Runway and CapCut to raise multi-platform output without diluting brand consistency.',
    ],
    print: [
      '**Large-Format Production:** Directed 10+ proprietary trade exhibition rebrands, cutting production time 30% and media costs 20% across outdoor, metro and indoor formats.',
      '**High-Volume Integrity:** Delivered 3,000+ printed projects and 6,000 sqm of OOH design through AP-ID, maintaining zero-failure visual integrity.',
      '**QA Systems:** Built systemic QA pipelines for high-volume print output, achieving a 100% on-time delivery rate across a 25,000-image e-commerce retouching programme.',
    ],
    deck: [
      '**Deal Support:** Designed proposal assets for 20+ global enterprise clients including H&M, Erste Group, Intesa Sanpaolo and SITA Africa, contributing to an 80-85% deal win rate.',
      '**Engagement Lift:** Transformed complex technological parameters into branded infographics and data visualisations, boosting evaluator engagement by 15%.',
      '**Accessibility:** Delivered 90%+ WCAG-compliant proposal documentation, passing Microsoft corporate accessibility audits with zero failures.',
    ],
    core: [
      '**Cross-Market Delivery:** Built unified corporate visual systems, presentation standards and video concepts deployed across 12 European countries for Yokogawa Europe.',
      '**Enterprise Scale:** Designed proposal and visual systems for 20+ global enterprise clients at Microsoft PCoE, supporting an 80-85% win rate with 90%+ WCAG compliance.',
      '**Asset Volume:** Post-processed 25,000+ product visuals for MADE.COM 5-country e-commerce launch in a 3-month window with 100% on-time delivery.',
    ],
    social: [
      '**Brand Social System:** Built the social design system now used daily by internal marketing teams, ending ad-hoc asset production and replacing it with one governed visual language across every channel.',
      '**Multi-Market Campaign Adaptation:** Delivered campaigns across USA, Romania and Middle East markets, adapting one core idea across formats, cultures and languages without diluting the brand.',
      '**AI Content Production Uplift:** Embedded AI content tooling into studio production, enabling designers to ship and test far more creative variants per week while keeping brand voice intact.'],
  };
  return A[stress.key];
}

module.exports = { buildHeader, buildSummary, cleanTitle, detectStress, buildExpertise, buildAchievements, pickLinks, hasWord, FAMILY_TITLE, RULES, FACTS, LINKS, VIDEO_PROOF };

if (require.main === module) {
  const jd = JSON.parse(process.argv[2] || '{}');
  const h = buildHeader(jd);
  console.log('HEADLINE (' + h.headline.split(/\s+/).length + ' cuvinte):');
  console.log('  ' + h.headline);
  console.log('\nSUMMARY (' + h.summary.split(/\s+/).length + ' cuvinte, max 80):');
  console.log('  ' + h.summary);
  console.log('\nEXPERTISE (' + h.expertise.length + ' elemente, grila 3x3):');
  h.expertise.forEach((e, i) => console.log('  ' + (i + 1) + '. ' + e));
  console.log('\nKEY ACHIEVEMENTS (' + h.achievements.length + '):');
  h.achievements.forEach((a, i) => console.log('  ' + (i + 1) + '. ' + a));
  console.log('\nLINKURI (din matrice, fără inventare):');
  h.links.forEach(l => console.log('  - ' + l.label + ': ' + l.url));
}
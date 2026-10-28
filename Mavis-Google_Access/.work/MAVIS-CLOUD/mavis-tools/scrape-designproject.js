#!/usr/bin/env node
/**
 * DESIGNPROJECT.IO SCRAPER — listările de joburi din România + textul integral.
 *
 * Măsurat 2026-10-23: site-ul e REACHABLE din cloud (HTTP 200, ~490-500 KB).
 * Structura e Next.js: carduri <a class="... job-card" href="/jobs/SLUG">.
 *
 * PAGINAREA: ?page=1 servește PAGINA 0 (confirmat: bytes identici, aceleași carduri).
 * Sunt disponibile paginile 0, 2, 3. Deci iau 0, 2, 3 și compar — nu mă bazez pe 1.
 * Două listări: /jobs/location/romania și /jobs/city/bucharest/category/all
 *
 * Cardul conține: titlu (h2), companie, tip job, salariu, locație, dată publicare.
 */
const fs = require('fs');
const https = require('https');

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
const BASE = 'https://designproject.io';
const OUT = process.argv[2] || '/workspace/Mavis/mavis-tools/jobs-designproject-2026-10-23.json';

function get(url) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const req = https.request({
      hostname: u.hostname, path: u.pathname + u.search, method: 'GET',
      headers: { 'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9' },
      rejectUnauthorized: false,
    }, r => {
      let d = '';
      r.on('data', c => d += c);
      r.on('end', () => resolve({ status: r.statusCode, body: d }));
    });
    req.on('error', reject);
    req.setTimeout(25000, () => req.destroy(new Error('timeout ' + url)));
    req.end();
  });
}

const strip = s => s.replace(/&amp;/g, '&').replace(/&nbsp;/g, ' ').replace(/&quot;/g, '"')
  .replace(/&#39;|&#x27;/g, "'").replace(/&rsquo;/g, "'").replace(/&ldquo;|&rdquo;/g, '"')
  .replace(/&ndash;/g, '-').replace(/&mdash;/g, '-').replace(/&#(\d+);/g, (m, d) => String.fromCharCode(d))
  .replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();

function parseCards(html) {
  const out = [];
  const re = /<a class="block p-4[^"]*job-card" href="(\/jobs\/[^"]+)"[^>]*>([\s\S]*?)<\/a>/g;
  for (const m of html.matchAll(re)) {
    const b = m[2];
    const title = strip((b.match(/<h2[^>]*>([\s\S]*?)<\/h2>/) || [])[1] || '');
    const company = strip((b.match(/<div class="text-sm text-neutral-600">([\s\S]*?)<\/div>/) || [])[1] || '');
    const spans = [...b.matchAll(/<span[^>]*>([\s\S]*?)<\/span>/g)].map(s => strip(s[1])).filter(Boolean);
    const dateM = b.match(/([A-Z][a-z]{2} \d{1,2}, 20\d\d)/);
    out.push({
      url: BASE + m[1], slug: m[1].replace('/jobs/', ''), title, company, spans,
      date: dateM ? dateM[1] : null,
    });
  }
  return out;
}

function parseDetail(html, card) {
  // Sursa: JSON-LD schema.org JobPosting, ascuns in payload-ul RSC (Next.js).
  // IMPORTANT: chunkurile se concateneaza FARA separator — cu '\n' se rupe
  // obiectul JSON-LD, care e taiat la mijloc de granita dintre doua chunkuri.
  const re = /self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)/g;
  let rsc = '', m;
  while ((m = re.exec(html))) { try { rsc += JSON.parse(m[1]); } catch (e) {} }

  const key = '{"@context":"https://schema.org","@type":"JobPosting"';
  const i = rsc.indexOf(key);
  let ld = null;
  if (i >= 0) {
    let depth = 0, end = -1, inStr = false, esc = false;
    for (let j = i; j < rsc.length; j++) {
      const c = rsc[j];
      if (inStr) { if (esc) esc = false; else if (c === '\\') esc = true; else if (c === '"') inStr = false; continue; }
      if (c === '"') { inStr = true; continue; }
      if (c === '{') depth++;
      else if (c === '}') { depth--; if (depth === 0) { end = j + 1; break; } }
    }
    if (end > 0) { try { ld = JSON.parse(rsc.slice(i, end)); } catch (e) { ld = null; } }
  }
  if (!ld) return { jd: '', ld: null };

  const jd = (ld.description || '').replace(/<\/(p|li|h[1-6]|div|tr|blockquote)>/gi, '\n').replace(/<br\s*\/?>/gi, '\n')
    .replace(/<[^>]+>/g, ' ').split(/\n+/).map(t => strip(t)).filter(t => t.length > 1).join('\n');

  const addr = (ld.jobLocation && ld.jobLocation.address) || {};
  const locParts = [];
  if (addr.addressLocality) locParts.push(addr.addressLocality);
  if (addr.addressRegion && addr.addressRegion !== addr.addressLocality) locParts.push(addr.addressRegion);
  if (addr.addressCountry) locParts.push(addr.addressCountry);
  let loc = locParts.join(', ');
  const rs = (jd.match(/Remote Status:\s*([^\n]+)/i) || [])[1];
  if (rs) loc = (loc ? loc + ', ' : '') + rs.trim();
  const et = (ld.employmentType || '').replace(/_/g, ' ').toUpperCase();
  const ENG = { 'FULL TIME': 'Full Time', 'PART TIME': 'Part Time', 'CONTRACTOR': 'Contract', 'TEMPORARY': 'Contract', 'INTERN': 'Intern', 'VOLUNTARY': 'Part Time' };
  const eng = ENG[et] || et;

  return {
    jd,
    ld: {
      title: ld.title, company: (ld.hiringOrganization && ld.hiringOrganization.name) || card.company,
      datePosted: ld.datePosted, validThrough: ld.validThrough, employmentType: ld.employmentType,
      jobLocation: ld.jobLocation, baseSalary: ld.baseSalary, experienceRequirements: ld.experienceRequirements,
      skills: ld.skills, url: ld.url,
    },
    loc, eng,
  };
}

(async () => {
  const listBase = [BASE + '/jobs/location/romania', BASE + '/jobs/city/bucharest/category/all'];
  const cards = new Map();
  for (const lb of listBase) {
    for (const p of [0, 2, 3]) {
      let r;
      try { r = await get(lb + '?page=' + p); } catch (e) { console.log('! ' + lb + ' p' + p + ' ' + e.message); continue; }
      if (r.status !== 200) { console.log('! ' + lb + ' p' + p + ' HTTP ' + r.status); continue; }
      const cs = parseCards(r.body);
      let added = 0;
      for (const c of cs) if (!cards.has(c.slug)) { cards.set(c.slug, { ...c, listed: [] }); added++; }
      for (const c of cs) { const e = cards.get(c.slug); if (!e.listed.includes(lb.replace(BASE, ''))) e.listed.push(lb.replace(BASE, '')); }
      console.log(`  ${lb.replace(BASE, '')} p${p} -> ${cs.length} carduri (+${added}, total ${cards.size})`);
    }
  }

  const jobs = [];
  for (const c of cards.values()) {
    let d;
    try { d = await get(c.url); } catch (e) { console.log('! ' + c.slug + ' ' + e.message); continue; }
    if (d.status !== 200) { console.log('! ' + c.slug + ' HTTP ' + d.status); continue; }
    const p = parseDetail(d.body, c);
    const jd = p.jd;
    if (!jd || jd.length < 100) { console.log('~ ' + c.slug + ' fara descriere utila (' + (jd || '').length + 'c)'); continue; }
    jobs.push({ src: 'designproject.io', ...c, jd, loc: p.loc, eng: p.eng, ld: p.ld });
    console.log(`  ${c.date} | ${c.company} | ${c.title} | loc=${p.loc} | eng=${p.eng} | jd ${jd.length}c`);
    await new Promise(res => setTimeout(res, 350));
  }
  fs.writeFileSync(OUT, JSON.stringify({ _meta: { scraped: '2026-10-23', source: 'designproject.io', count: jobs.length }, jobs }, null, 2));
  console.log('\nscrapat: ' + jobs.length + ' -> ' + OUT);
})();

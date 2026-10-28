#!/usr/bin/env node
/**
 * IQADS SCRAPER — extrage setul complet de joburi din AdJob + textul integral.
 *
 * Măsurat 2026-10-23: https://www.iqads.ro/p/adjob e REACHABLE din cloud (HTTP 200,
 * ~73 KB) și conține toate joburile. PAGINAREA NU FUNC�IONEAZĂ: ?page=2 și ?page=3
 * servesc exact același set ca pagina 0 (verificat: aceleași 47 linkuri).
 * ⇒ nu iterez pagini, iau catalogul complet de pe pagina 0.
 *
 * Parser: headerul e mereu
 *   <p class="muted">Anunt valabil pana la data de <span>DATE</span><br/>
 *   Companie: <a>X</a><br/>Specializare: <a>..</a>, <a>..</a><br/>
 *   Tip job: <a>..</a>, <a>..</a><br/>Nivel: <a>..</a></p>
 * urmat de paragrafele descrierii.
 *
 * Ieșire: jobs-iqads-<data>.json
 */
const fs = require('fs');
const https = require('https');

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
const BASE = 'https://www.iqads.ro';
const OUT = process.argv[2] || '/workspace/Mavis/mavis-tools/jobs-iqads-2026-10-23.json';

function get(url) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const req = https.request({
      hostname: u.hostname, path: u.pathname + u.search, method: 'GET',
      headers: { 'User-Agent': UA, 'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.8' },
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

const strip = s => s.replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&')
  .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&rsquo;/g, "'").replace(/&ldquo;|&rdquo;/g, '"')
  .replace(/&middot;/g, '·').replace(/&euro;/g, 'EUR').replace(/&#(\d+);/g, (m, d) => String.fromCharCode(d))
  .replace(/\s+/g, ' ').trim();

function parseJob(html) {
  const out = { expiry: null, company: null, specialization: [], jobType: [], level: null, jd: '', title: null };
  const h = html.match(/<p class="muted">([\s\S]*?)<\/p>/);
  if (h) {
    const hdr = h[1];
    const ex = hdr.match(/Anunt valabil pana la data de\s*<span>([^<]+)<\/span>/);
    if (ex) out.expiry = ex[1].trim();
    const co = hdr.match(/Companie:\s*<a[^>]*>([^<]+)<\/a>/);
    if (co) out.company = co[1].trim();
    const sp = hdr.match(/Specializare:\s*([\s\S]*?)<br\/>/);
    if (sp) out.specialization = [...sp[1].matchAll(/<a[^>]*>([^<]+)<\/a>/g)].map(m => m[1].trim());
    const jt = hdr.match(/Tip job:\s*([\s\S]*?)<br\/>/);
    if (jt) out.jobType = [...jt[1].matchAll(/<a[^>]*>([^<]+)<\/a>/g)].map(m => m[1].trim());
    const lv = hdr.match(/Nivel:\s*<a[^>]*>([^<]+)<\/a>/);
    if (lv) out.level = lv[1].trim();
  }
  // corpul: de la primul <p> DUPA header pana la sectiunea de aplicare
  const start = h ? html.indexOf('</p>', h.index) + 4 : 0;
  let body = html.slice(start);
  body = body.replace(/<script[\s\S]*?<\/script>/gi, ' ').replace(/<style[\s\S]*?<\/style>/gi, ' ');
  const cut = body.search(/Aplica la|Aplicați la|Trimite CV|post-solicit|\/aplica"|class="btn/i);
  if (cut > 200) body = body.slice(0, cut);
  // IMPORTANT: IQads pune cerintele in <ul><li>, nu in <p>. Daca citesc doar <p>,
  // tai jumatate din anunt. Deci transform blocurile in newline si apoi curat etichetele.
  body = body.replace(/<\/(p|li|h[1-6]|div|ul|ol|tr|blockquote)>/gi, '\n')
             .replace(/<br\s*\/?>/gi, '\n')
             .replace(/<[^>]+>/g, ' ');
  const paras = body.split(/\n+/)
    .map(t => strip(t))
    .filter(t => t.length > 2);
  out.jd = paras.join('\n');
  const t = html.match(/<title>([^<]*?)\s*@\s*([^<]*)<\/title>/);
  if (t) { out.title = t[1].trim(); }
  return out;
}

(async () => {
  // Doua surse: catalogul AdJob + paginile de tag /relevant/<rol> (joburi deschise)
  const sources = [BASE + '/p/adjob'];
  for (const t of ['art-director', 'creative-director', 'graphic-designer', 'art', 'digital', 'marketing', 'pozitii'])
    sources.push(BASE + '/relevant/' + t);

  const seen = new Map();
  for (const src of sources) {
    let cat;
    try { cat = await get(src); } catch (e) { console.log('  ! sursa ' + src + ' ' + e.message); continue; }
    if (cat.status !== 200) { console.log('  ! sursa ' + src + ' HTTP ' + cat.status); continue; }
    const links = [...cat.body.matchAll(/href="(?:https?:\/\/(?:www\.)?iqads\.ro)?\/?(adjob\/(\d+)\/[a-z0-9-]+)"/g)];
    let added = 0;
    for (const m of links) if (!seen.has(m[2])) { seen.set(m[2], m[1]); added++; }
    console.log('  sursa ' + src.replace(BASE, '') + ' -> +' + added + ' (total ' + seen.size + ')');
  }
  console.log('joburi unice: ' + seen.size);

  const jobs = [];
  const ids = [...seen.keys()].sort((a, b) => b - a);
  for (let i = 0; i < ids.length; i++) {
    const id = ids[i], path = seen.get(id);
    let r;
    try { r = await get(BASE + '/' + path); } catch (e) { console.log('  ! ' + id + ' ' + e.message); continue; }
    if (r.status !== 200) { console.log('  ! ' + id + ' HTTP ' + r.status); continue; }
    const p = parseJob(r.body);
    if (!p.jd || p.jd.length < 80) { console.log('  ~ ' + id + ' fara descriere utila'); continue; }
    const slug = path.split('/').pop();
    jobs.push({ src: 'IQads', id, url: BASE + '/' + path, slug, ...p });
    process.stdout.write(`  ${id} ${p.company || '?'} | ${p.title || slug} | exp ${p.expiry} | tip ${p.jobType.join('/')} | niv ${p.level} | jd ${p.jd.length}c\n`);
    await new Promise(res => setTimeout(res, 450));
  }
  fs.writeFileSync(OUT, JSON.stringify({ _meta: { scraped: '2026-10-23', source: BASE + '/p/adjob', count: jobs.length }, jobs }, null, 2));
  console.log('\nscrapat: ' + jobs.length + ' -> ' + OUT);
})();

#!/usr/bin/env node
/**
 * RAPORT ZILNIC — SONDA DE SURSE.
 *
 * Măsură comportamentul celor două surse de joburi în ziua curentă, ca
 * secțiunea "Ce n-a mers, măsurat" din raport să nu repete cifrele de ieri.
 *
 * Zero cereri Google (doar cereri web către iqads.ro / designproject.io).
 *
 * Ieșire: report-source-probe.json
 */
const fs = require('fs');
const path = require('path');
const https = require('https');

const DIR = __dirname;
const DATE = process.argv[2] || new Date().toISOString().slice(0, 10);
const OUT = path.join(DIR, 'report-source-probe.json');

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

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

const linkSet = body => [...new Set([...body.matchAll(/adjob\/(\d+)\//g)].map(m => m[1]))].sort();
const cardCount = body => (body.match(/job-card/g) || []).length;

(async () => {
  const out = { date: DATE };

  // ---------- designproject.io: ce spun datele de azi ----------
  try {
    const dp = JSON.parse(fs.readFileSync(path.join(DIR, `jobs-designproject-${DATE}.json`), 'utf8'));
    const jobs = dp.jobs || [];
    const lens = jobs.map(j => (j.jd || '').length).sort((a, b) => a - b);
    const et = {};
    let withJobType = 0, badgeFullTime = 0;
    for (const j of jobs) {
      const e = (j.ld && j.ld.employmentType) || '(null)';
      et[e] = (et[e] || 0) + 1;
      if (/Job Type:\s*/i.test(j.jd || '')) withJobType++;
      if ((j.spans || []).some(s => /full-?time/i.test(s))) badgeFullTime++;
    }
    // validThrough = datePosted + 30 zile? (relatia s-a masurat pe 24.10)
    const MON = { Jan:0,Feb:1,Mar:2,Apr:3,May:4,Jun:5,Jul:6,Aug:7,Sep:8,Oct:9,Nov:10,Dec:11 };
    let checked = 0, exact = 0, offByOne = 0, other = 0;
    for (const j of jobs) {
      const posted = (j.ld && j.ld.datePosted) || null;
      const valid = (j.ld && j.ld.validThrough) || null;
      if (!posted || !valid) continue;
      const p = new Date(posted), v = new Date(valid);
      if (isNaN(p) || isNaN(v)) continue;
      checked++;
      const days = Math.round((v - p) / 86400000);
      if (days === 30) exact++;
      else if (days === 29 || days === 31) offByOne++;
      else other++;
    }
    out.designproject = {
      count: jobs.length,
      jdLenMin: lens[0] || 0,
      jdLenMax: lens[lens.length - 1] || 0,
      employmentType: et,
      jsonLdAllFullTime: Object.keys(et).length === 1 && !!et.FULL_TIME,
      badgeFullTime,
      withJobTypeLine: withJobType,
      newestPostDate: jobs.map(j => j.date).filter(Boolean).sort().slice(-1)[0] || null,
      validThrough: { checked, exact, offByOne, other, rule: 'datePosted + 30 zile' },
    };
  } catch (e) { out.designproject = { error: e.message }; }

  // ---------- designproject.io: paginatia ----------
  try {
    const base = 'https://designproject.io/jobs/location/romania';
    const [p0, p1] = await Promise.all([get(base + '?page=0'), get(base + '?page=1')]);
    out.designproject.pagination = {
      page0Cards: cardCount(p0.body),
      page1Cards: cardCount(p1.body),
      sameBytes: p0.body.length === p1.body.length,
      // paginatia nu avanseaza => catalogul complet e pe page=0
      page1EqualsPage0: p0.body.length === p1.body.length && cardCount(p0.body) === cardCount(p1.body),
    };
  } catch (e) { out.designproject = out.designproject || {}; out.designproject.pagination = { error: e.message }; }

  // ---------- IQads: paginatia ----------
  try {
    const pages = [];
    for (const p of [0, 2, 3]) {
      const r = await get('https://www.iqads.ro/p/adjob?page=' + p);
      pages.push({ p, status: r.status, links: linkSet(r.body) });
    }
    const base = pages[0].links.join(',');
    out.iqads = {
      catalogueLinks: pages[0].links.length,
      pagesTested: pages.map(x => x.p),
      allPagesIdentical: pages.every(x => x.links.join(',') === base),
      status: pages.map(x => x.p + ':' + x.status),
    };
  } catch (e) { out.iqads = { error: e.message }; }

  fs.writeFileSync(OUT, JSON.stringify(out, null, 2));
  console.log(JSON.stringify(out, null, 2));
  console.log('\n-> ' + OUT);
  console.log('cereri Google: 0');
})();

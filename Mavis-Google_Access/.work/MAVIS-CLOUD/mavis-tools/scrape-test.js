const https = require('https');
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36';

function get(url, depth = 0) {
  return new Promise((res) => {
    const t = Date.now();
    const r = https.get(url, { headers: { 'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml' }, timeout: 20000 }, (resp) => {
      let d = '';
      resp.on('data', c => { if (d.length < 400000) d += c; });
      resp.on('end', () => res({ ok: true, code: resp.statusCode, ms: Date.now() - t, len: d.length, body: d, url }));
    });
    r.on('error', e => res({ ok: false, err: e.code || e.message.slice(0, 40), ms: Date.now() - t, url }));
    r.on('timeout', () => { r.destroy(); res({ ok: false, err: 'TIMEOUT', ms: Date.now() - t, url }); });
  });
}

const TARGETS = [
  ['JOBS RO',        'https://www.jobinsider.ro/'],
  ['JOBS RO',        'https://www.bestjobs.eu/'],
  ['JOBS RO',        'https://www.hipo.ro/'],
  ['JOBS RO',        'https://www.hipo.ro/jobs/'],
  ['JOBS BU',        'https://www.jobboard.ro/jobs/'],
  ['JOBS EU',        'https://weworkremotely.com/'],
  ['JOBS EU',        'https://remoteok.com/remote-design-jobs'],
  ['JOBS EU',        'https://remotive.com/remote-jobs'],
  ['JOBS INTL',      'https://www.linkedin.com/jobs/search?keywords=designer'],
  ['JOBS INTL',      'https://wellfound.com/jobs'],
  ['JOBS INTL',      'https://www.indeed.com/'],
  ['JOBS INTL',      'https://glassdoor.com/'],
  ['AI JOBS',        'https://aijobs.net/'],
  ['AI JOBS',        'https://www.aiautomationsociety.ai/'],
  ['AI JOBS',        'https://huggingface.co/jobs'],
  ['WIRESTOCK',      'https://wirestock.com/'],
  ['PAYS.AI',        'https://pays.ai/'],
  ['FREELANCE',      'https://www.upwork.com/'],
  ['FREELANCE',      'https://www.fiverr.com/'],
  ['FREELANCE',      'https://www.malt.com/'],
  ['CREATIVE',       'https://www.behance.net/'],
  ['CREATIVE',       'https://dribbble.com/'],
  ['DESIGN JOBS',    'https://www.designjobs.com/'],
  ['DESIGN JOBS',    'https://coroflot.com/'],
];

(async () => {
  for (const [cat, url] of TARGETS) {
    const r = await get(url);
    let jobs = 0, blocked = false, hasLogin = false;
    if (r.ok) {
      const b = r.body || '';
      jobs = (b.match(/class="[^"]*job[^"]*"/gi) || []).length + (b.match(/<article/gi) || []).length;
      blocked = /captcha|unusual traffic|are you a robot|cloudflare|access denied|just a moment/i.test(b);
      hasLogin = /type="password"|sign in|log in/i.test(b.slice(0, 20000));
      console.log(`${String(r.code).padEnd(4)} ${String(r.ms + 'ms').padEnd(8)} ${cat.padEnd(13)} ${url.replace('https://', '').padEnd(42)} ${jobs ? 'joburi~' + jobs : 'fara marker'} ${blocked ? '🚫 BLOCAT' : '✅ citibil'}${hasLogin ? ' 🔐 login' : ''}`);
    } else {
      console.log(`${'ERR'.padEnd(4)} ${String(r.ms + 'ms').padEnd(8)} ${cat.padEnd(13)} ${url.replace('https://', '').padEnd(42)} ❌ ${r.err}`);
    }
  }
})();

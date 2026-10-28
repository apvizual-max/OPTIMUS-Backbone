#!/usr/bin/env node
/**
 * Inspecteaza un job designproject.io: extrage JSON-LD JobPosting si afiseaza
 * campurile din "Job Overview" (Job Type, Location, Remote Status, Experience Level).
 * Uzaj: node mavis-tools/dp-inspect.js <slug> [<slug> ...]
 */
const fs = require('fs');

function ldOf(file) {
  const html = fs.readFileSync(file, 'utf8');
  const re = /self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)/g;
  let rsc = '', m;
  while ((m = re.exec(html))) { try { rsc += JSON.parse(m[1]); } catch (e) {} }
  const key = '{"@context":"https://schema.org","@type":"JobPosting"';
  const i = rsc.indexOf(key);
  if (i < 0) return null;
  let depth = 0, end = -1, inStr = false, esc = false;
  for (let j = i; j < rsc.length; j++) {
    const c = rsc[j];
    if (inStr) { if (esc) esc = false; else if (c === '\\') esc = true; else if (c === '"') inStr = false; continue; }
    if (c === '"') { inStr = true; continue; }
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) { end = j + 1; break; } }
  }
  return end > 0 ? JSON.parse(rsc.slice(i, end)) : null;
}

for (const f of process.argv.slice(2)) {
  const ld = ldOf(f);
  if (!ld) { console.log(f + ' -> fara JSON-LD'); continue; }
  const txt = (ld.description || '').replace(/<[^>]+>/g, '\n');
  const grab = k => { const m = txt.match(new RegExp(k + ':\\s*([^\\n]+)')); return m ? m[1].trim() : 'n/a'; };
  console.log('=== ' + f.replace(/^.*dpx-|\.html$/g, ''));
  console.log('   title      : ' + ld.title);
  console.log('   Job Type   : ' + grab('Job Type'));
  console.log('   Location   : ' + grab('Location'));
  console.log('   RemoteStat : ' + grab('Remote Status'));
  console.log('   Experience : ' + grab('Experience Level'));
  console.log('   DatePosted : ' + grab('Date Posted'));
  console.log('   JSONLD eng : ' + ld.employmentType + ' | jobLocation: ' + JSON.stringify(ld.jobLocation));
  console.log('   intro      : ' + (ld.description || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').slice(0, 240));
}

// Audit: which script-scope bindings shadow a real window member?
// Walks the source tracking brace/paren/bracket depth so that only depth-0
// `let`/`const`/`var` statements count, then splits each declarator list at
// depth 0. A single-name pattern misses `let a=1, b=2, history=[]`.
import { readFileSync } from 'node:fs';

const HTML = process.argv[2] || 'C:/Users/apviz/.minimax-agent/projects/Mavis-Optimus-Dashboard/90_CONTROL_CENTER/index.html';
const html = readFileSync(HTML, 'utf8');
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)];
if (!blocks.length) { console.log('no inline script found'); process.exit(1); }
const js = blocks.map(b => b[1]).join('\n');

// real window members worth colliding with: function-valued or hot-path objects
const DANGER = new Set([
  'history','name','top','parent','self','status','length','origin','close','focus','blur',
  'open','event','screen','frames','opener','console','alert','prompt','confirm','fetch',
  'navigator','location','localStorage','sessionStorage','crypto','performance',
  'getComputedStyle','requestAnimationFrame','cancelAnimationFrame','setTimeout',
  'setInterval','clearTimeout','clearInterval','queueMicrotask','structuredClone','URL',
  'URLSearchParams','Blob','File','FileReader','FormData','Headers','Request','Response',
  'AbortController','TextEncoder','TextDecoder','atob','btoa','escape','unescape','isNaN',
  'isFinite','parseInt','parseFloat','encodeURIComponent','decodeURIComponent','encodeURI',
  'decodeURI','eval','Function','Array','Object','String','Number','Boolean','Symbol','Math',
  'JSON','Date','RegExp','Error','Map','Set','Promise','Proxy','Reflect','Intl','print',
  'find','matchMedia','scroll','scrollTo','scrollBy','innerWidth','innerHeight','outerWidth',
  'outerHeight','devicePixelRatio','screenX','screenY','device','screenLeft','screenTop',
  'onload','onerror','onresize','onclick','addEventListener','removeEventListener',
  'dispatchEvent','postMessage','requestIdleCallback','Text','Image','Option','Audio'
]);

// scan char by char, tracking depth; collect depth-0 declaration statements
let depth = 0, i = 0, decls = [];
const OPEN = { '(': 1, '[': 1, '{': 1 }, CLOSE = { ')': 1, ']': 1, '}': 1 };
let str = null, lineComment = false, blockComment = false;
const isDeclStart = (idx) => {
  // only at a statement boundary (start of line, after indent) at depth 0
  if (depth !== 0) return false;
  const before = js.slice(Math.max(0, idx - 3), idx);
  if (/[^\s;{}()=+\-*/%&|^<>!~,?:[.\]]/.test(before.slice(-1)) && before.length) return false;
  return /^(let|const|var)\b/.test(js.slice(idx, idx + 6));
};
let stmtStart = -1, stmtKw = '';
while (i < js.length) {
  const c = js[i], n = js[i + 1];
  if (lineComment) { if (c === '\n') lineComment = false; i++; continue; }
  if (blockComment) { if (c === '*' && n === '/') { blockComment = false; i += 2; } else i++; continue; }
  if (str) { if (c === '\\') { i += 2; continue; } if (c === str) str = null; i++; continue; }
  if (c === '/' && n === '/') { lineComment = true; i += 2; continue; }
  if (c === '/' && n === '*') { blockComment = true; i += 2; continue; }
  if (c === '"' || c === "'" || c === '`') { str = c; i++; continue; }
  if (stmtStart < 0 && isDeclStart(i)) { stmtStart = i; stmtKw = js.slice(i, i + js.slice(i).match(/^(let|const|var)/)[0].length); }
  if (stmtStart >= 0) {
    // end the statement at depth-0 ';' or at a depth-0 newline that leaves braces balanced
    const atLineStart = c === '\n';
    if (c === ';' && depth === 0) { decls.push({ kw: stmtKw, text: js.slice(stmtStart, i) }); stmtStart = -1; i++; continue; }
    if (atLineStart && depth === 0) {
      const seg = js.slice(stmtStart, i);
      if (!/[,=({[]$/.test(seg.trimEnd()) ) { decls.push({ kw: stmtKw, text: seg }); stmtStart = -1; }
    }
  }
  if (OPEN[c]) depth++;
  else if (CLOSE[c]) depth--;
  i++;
}

const names = new Map();
for (const d of decls) {
  const body = d.text.replace(/^(let|const|var)\s+/, '');
  // split declarators at depth 0 commas
  let dd = 0, cur = '';
  const parts = [];
  for (const ch of body) {
    if (OPEN[ch]) dd++; else if (CLOSE[ch]) dd--;
    if (ch === ',' && dd === 0) { parts.push(cur); cur = ''; } else cur += ch;
  }
  parts.push(cur);
  for (const p of parts) {
    const m = p.trim().match(/^([A-Za-z_$][\w$]*)/);
    if (m) { if (!names.has(m[1])) names.set(m[1], d.kw); }
  }
}

console.log('script-scope bindings found:', names.size);
console.log('');
const hits = [...names.keys()].filter(n => DANGER.has(n)).sort();
console.log('=== SHADOWED WINDOW MEMBERS ===');
if (!hits.length) console.log('  (none)');
for (const h of hits) {
  const bare = (js.match(new RegExp('(?<![\\w$.])' + h + '\\s*[.(]', 'g')) || []).length;
  const winq = (js.match(new RegExp('window\\.' + h + '\\b', 'g')) || []).length;
  const d = [...decls].find(x => new RegExp('(^|[,\\s])' + h + '(\\s*[=,;]|\\s*$)').test(x.text));
  console.log(`  >> ${names.get(h)} ${h}   (shadows window.${h})`);
  console.log(`     line: ${(d?.text || '').trim().slice(0, 110)}`);
  console.log(`     bare uses routed to the shadow: ${bare}    window-qualified: ${winq}`);
}
console.log('');
console.log('=== all script-scope bindings ===');
console.log('  ' + [...names.keys()].sort().join(', '));

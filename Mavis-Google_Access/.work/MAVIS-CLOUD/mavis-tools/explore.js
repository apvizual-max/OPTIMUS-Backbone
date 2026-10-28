const k = require('./kit.js');

async function children(id) {
  const r = await k.drive.list(`'${id}' in parents and trashed=false`, 100);
  return r.files;
}
async function walk(id, depth, prefix, maxD) {
  if (depth > maxD) return;
  const cs = await children(id);
  for (const c of cs) {
    const isF = c.mimeType === 'application/vnd.google-apps.folder';
    console.log(prefix + (isF ? '📁 ' : '📄 ') + c.name + (isF ? '' : '  [' + (c.mimeType || '').split('.').pop() + ']'));
    if (isF) await walk(c.id, depth + 1, prefix + '   ', maxD);
  }
}
(async () => {
  const r = await k.drive.list('trashed=false', 200);
  const want = process.argv.slice(2);
  for (const target of want) {
    const f = r.files.find(x => x.name.toLowerCase().includes(target.toLowerCase()));
    if (!f) { console.log('nu am gasit:', target); continue; }
    console.log('\n=== ' + f.name + ' ===');
    await walk(f.id, 0, '  ', 3);
  }
})();

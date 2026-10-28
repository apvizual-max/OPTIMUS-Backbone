#!/usr/bin/env node
/**
 * RAPORT ZILNIC — descoperirea destinației pe Drive + starea filtrelor MAVIS/*.
 *
 * 1) Găsește folderul "Alex Work" și subfolderul "00-INTRARE" din Drive.
 * 2) Citește filtrele Gmail și arată dacă mai adaugă etichetele MAVIS/*.
 *
 * READ-ONLY: nu creează, nu mută, nu șterge nimic. Doar citire.
 */
const k = require('./kit.js');

(async () => {
  console.log('=== ROOT DRIVE ===');
  const root = await k.drive.list("mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed=false", 100);
  root.files.forEach(f => console.log('  ' + f.id + '  ' + f.name + '  (' + f.mimeType + ')'));

  // cauta "Alex Work" oriunde sub root (1 nivel)
  const aw = await k.drive.list("name = 'Alex Work' and mimeType='application/vnd.google-apps.folder' and trashed=false", 20);
  console.log('\n=== "Alex Work" ===');
  if (!aw.files.length) { console.log('  NU EXISTA un folder "Alex Work" in Drive'); }
  else {
    for (const f of aw.files) {
      console.log('  FOUND ' + f.id + ' | ' + f.name);
      const kids = await k.drive.list("'" + f.id + "' in parents and trashed=false", 100);
      console.log('  copii:');
      kids.files.forEach(x => console.log('    ' + x.id + '  ' + x.name + '  (' + (x.mimeType || '').slice(0, 40) + ')'));
    }
  }

  // subfolder 00-INTRARE oriunde
  const intr = await k.drive.list("name = '00-INTRARE' and mimeType='application/vnd.google-apps.folder' and trashed=false", 20);
  console.log('\n=== "00-INTRARE" (cautare globala) ===');
  if (!intr.files.length) console.log('  NU EXISTA');
  else intr.files.forEach(f => console.log('  ' + f.id + ' | ' + f.name + ' | parent: ' + (f.parents || []).join(',')));

  console.log('\n=== FILTRE GMAIL ===');
  const fl = await k.req('GET', 'https://gmail.googleapis.com/gmail/v1/users/me/settings/filters');
  const filters = (fl.filter || []);
  // filtrele refera etichetele prin ID, nu prin nume -> rezolvam ID->nume
  const labs = await k.gmail.labels();
  const id2name = {};
  (labs.labels || []).forEach(l => { id2name[l.id] = l.name; });
  const nm = id => (id2name[id] || id);
  console.log('  total filtre: ' + filters.length);
  filters.forEach(f => {
    const c = f.criteria || {}, a = f.action || {};
    const add = (a.addLabelIds || []).map(nm), rem = (a.removeLabelIds || []).map(nm);
    const _TAX = require('./taxonomy.js');
    const _r = _TAX.resolve(labs.labels || []);
    const _mavisNames = new Set(_r.resolved.map(x => x.name));
    const touched = add.concat(rem).filter(x => _mavisNames.has(x));
    const mark = touched.length ? '  <<< TAXONOMIE' : '';
    console.log(`  id=${f.id} | from=${c.from || '-'} | query="${c.query || '-'}" | add=[${add.join(',')}] | remove=[${rem.join(',')}]${mark}`);
  });

  console.log('\ncereri Google folosite: ' + k.CALL_STATE.calls);
})();

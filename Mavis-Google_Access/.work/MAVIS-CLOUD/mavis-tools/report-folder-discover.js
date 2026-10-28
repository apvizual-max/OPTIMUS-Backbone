#!/usr/bin/env node
/**
 * RAPORT ZILNIC — descoperirea folderului de livrare pe Drive + starea de mai devreme.
 *
 * Fiișierul de raport poate ajunge în mai multe locații (folderul "de lucru"
 * și folderul din vault). Scriptul găsește ID-urile pe cALE, în ordine, fără
 * să invente niciun id.
 *
 * READ-ONLY: nu creează, nu mută, nu șterge nimic. Doar citire.
 *
 * Utilizare: node report-folder-discover.js <nume-folder-1> <nume-folder-2> ...
 *   ex: node report-folder-discover.js GDrive-Second_Brain_PKMS/00_Inbox/00-2-Daily_Raw_Notes
 */
const k = require('./kit.js');

/** Imparte "A/B/C" in [A, B, C]. */
function splitPath(p) {
  return String(p || '').split('/').map(s => s.trim()).filter(Boolean);
}

(async () => {
  const target = splitPath(process.argv[2]);
  if (!target.length) {
    console.log('folosire: node report-folder-discover.js A/B/C');
    process.exit(1);
  }

  // pornim de la root: cautam primul segment oriunde in Drive
  let current = null;
  const first = target[0];
  const found = await k.drive.list(
    `name = '${first.replace(/'/g, "\\'")}' and mimeType='application/vnd.google-apps.folder' and trashed=false`,
    20);
  if (!found.files.length) {
    console.log('NU EXISTA folderul "' + first + '" in Drive');
    console.log('cereri Google folosite: ' + k.CALL_STATE.calls);
    process.exit(2);
  }
  current = found.files[0];
  console.log('1) ' + current.name + '  ->  ' + current.id);

  for (let i = 1; i < target.length; i++) {
    const seg = target[i];
    const kids = await k.drive.list(
      `'${current.id}' in parents and name = '${seg.replace(/'/g, "\\'")}' and mimeType='application/vnd.google-apps.folder' and trashed=false`,
      20);
    if (!kids.files.length) {
      console.log('NU EXISTA subfolderul "' + seg + '" in "' + current.name + '"');
      console.log('cereri Google folosite: ' + k.CALL_STATE.calls);
      process.exit(3);
    }
    current = kids.files[0];
    console.log((i + 1) + ') ' + current.name + '  ->  ' + current.id);
  }

  console.log('\nFOLDER_ID=' + current.id);

  // cate fisiere markdown exista deja acolo (nu facem nimic, doar vedem)
  const md = await k.drive.list(
    `'${current.id}' in parents and trashed=false and mimeType='text/markdown'`,
    50);
  console.log('\nrapoarte .md in folder: ' + (md.files || []).length);
  for (const f of (md.files || []).slice(0, 10)) {
    console.log('  ' + f.id + '  ' + f.name + '  (' + f.modifiedTime + ')');
  }

  console.log('\ncereri Google folosite: ' + k.CALL_STATE.calls);
})();

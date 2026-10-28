// TEST COMPLET CAPACITATI DRIVE
const k = require('./kit.js');
const fs = require('fs');

const ok = (n) => console.log('  ✅ ' + n);
const fail = (n, e) => console.log('  ❌ ' + n + ' -> ' + String(e).slice(0, 80));

(async () => {
  let rootId, docId, subId;
  try {
    // 1. creeaza folder ROOT de test
    const r1 = await k.drive.list("name='MAVIS Test' and mimeType='application/vnd.google-apps.folder' and trashed=false");
    if (r1.files.length) { rootId = r1.files[0].id; console.log('  ♻️  folder MAVIS Test exista, il reutilizez'); }
    else { rootId = (await k.drive.mkdir('MAVIS Test')).id; ok('1. creez folder ROOT: MAVIS Test'); }

    // 2. creeaza subfolder
    subId = (await k.drive.mkdir('Subfolder Test', rootId)).id;
    ok('2. creez subfolder in el');

    // 3. creeaza document cu continut
    const CONT = 'Test Mavis ' + new Date().toISOString() + '\nVerificare functionalitati Drive.';
    docId = (await k.drive.upload('document test.txt', CONT, 'text/plain', subId)).id;
    ok('3. creez document cu continut');

    // 4. CITESTE continutul (download)
    const meta = await k.req('GET', `https://www.googleapis.com/drive/v3/files/${docId}?alt=media`);
    ok('4. descarc/ citesc continutul: ' + JSON.stringify(String(meta).slice(0, 40)));

    // 5. REDENUMESC
    await k.drive.rename(docId, 'document RENUMAT.txt');
    const g1 = await k.drive.get(docId);
    ok('5. redenumesc -> ' + g1.name);

    // 6. MUT documentul in root
    await k.drive.move(docId, rootId, subId);
    const g2 = await k.drive.get(docId);
    ok('6. mut documentul -> ' + (g2.parents || []).slice(0, 1) + ' in root');

    // 7. MUT folderul (subfolder in alt loc)
    const dest = (await k.drive.mkdir('Dest Test', rootId)).id;
    await k.drive.move(subId, dest, rootId);
    ok('7. mut folderul');

    // 8. TRASH document
    await k.drive.trashed(docId, true);
    const g3 = await k.drive.get(docId);
    ok('8. mut in Trash -> trashed=' + g3.trashed);

    // 9. RESTORE din trash
    await k.drive.trashed(docId, false);
    const g4 = await k.drive.get(docId);
    ok('9. RESTAURAT din trash -> trashed=' + g4.trashed);

    // 10. COPY
    const cp = await k.drive.copy(docId, 'COPIA document.txt', rootId);
    ok('10. creez copie: ' + cp.name);

    // 11. cauta
    const s = await k.drive.list("name contains 'MAVIS Test'");
    ok('11. caut -> ' + s.files.length + ' obiecte sub MAVIS Test');

    // 12. vezi toate fisierele mele
    const all = await k.drive.list('trashed=false', 20);
    ok('12. acces la root: ' + all.files.length + ' obiecte (primele 20)');

    console.log('\n  ID-uri pentru curatare:');
    console.log('   root=' + rootId + ' dest=' + dest + ' doc=' + docId + ' copy=' + cp.id);
    fs.writeFileSync('/workspace/mavis-tools/test_ids.json', JSON.stringify({ rootId, dest, docId, copyId: cp.id }, null, 1));
  } catch (e) { fail('TEST', e.message); }
})();

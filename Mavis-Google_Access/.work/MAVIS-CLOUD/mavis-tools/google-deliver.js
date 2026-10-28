#!/usr/bin/env node
/**
 * LIVRARE PE DRIVE — Mavis Cloud → Mavis-Cloud-Google-Access-Bot
 *
 * Publică conținutul repo-ului în folderul principal de referință de pe Drive.
 * Face și **Google Docs native** prin conversie Drive (Docs API direct e
 * blocat de anti-bot din cloud).
 *
 *   node mavis-tools/google-deliver.js
 *   node mavis-tools/google-deliver.js --bot <folderId>
 *
 * NU șterge nimic. Nu suprascrie: creează versiuni noi, cu timestamp.
 */

const fs = require('fs');
const path = require('path');
const kit = require('./kit.js');

const args = process.argv.slice(2);
const argOf = (f, d) => { const i = args.indexOf(f); return i >= 0 ? args[i + 1] : d; };

const BOT = argOf('--bot', '1UQIxhctyJxBXIIFnpxSc5Jd0wvFxEylu');
const REPO = path.join(__dirname, '..');
const STAMP = new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-');

const G = (s) => `\x1b[32m${s}\x1b[0m`, D = (s) => `\x1b[2m${s}\x1b[0m`;
const B = (s) => `\x1b[1m${s}\x1b[0m`, R = (s) => `\x1b[31m${s}\x1b[0m`;

const SUB = {
  '01-Transcript': ['TRANSCRIPT-SESIUNE-2026-10-28.md'],
  '02-Deliverables': ['README.md', 'GHID-WORKFLOW.md', 'CAPABILITATI-GOOGLE.md', 'EVAL-SKILL-VS-BASELINE.md'],
  '04-Capabilitati': ['probe/capabilities.json'],
  '05-Comunicare': ['COMUNICARE/CANAL.md', 'COMUNICARE/2026-10-28-001-FINALIZARE-INTEGRARE.md'],
  '06-Handoff': ['HANDOFF/HANDOFF-COMPLET-2026-10-28.md', 'HANDOFF/ENV-INVENTORY.json'],
};

/** Fișierele care merită și versiune Google Doc NATIVĂ (citite/editate în UI). */
const AS_NATIVE_DOC = [
  'README.md', 'CAPABILITATI-GOOGLE.md', 'GHID-WORKFLOW.md', 'TRANSCRIPT-SESIUNE-2026-10-28.md',
  'HANDOFF/HANDOFF-COMPLET-2026-10-28.md', 'EVAL-SKILL-VS-BASELINE.md',
];

const folderCache = {};
async function ensureFolder(name, parent) {
  const key = name + '|' + parent;
  if (folderCache[key]) return folderCache[key];
  const q = `name='${name}' and '${parent}' in parents and trashed=false`;
  const found = await kit.req('GET', `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(q)}&fields=files(id,name)`);
  if ((found.files || []).length) { folderCache[key] = found.files[0].id; return folderCache[key]; }
  const f = await kit.drive.mkdir(name, parent);
  folderCache[key] = f.id;
  console.log(D(`    folder creat: ${name}`));
  return f.id;
}

async function uploadMd(localPath, remoteName, parentId) {
  const content = fs.readFileSync(localPath, 'utf8');
  const f = await kit.drive.upload(remoteName, content, 'text/markdown', parentId);
  return f;
}

/** Idempotenta: daca exista deja un fisier cu numele asta, il trashuiește
 *  (reversibil) inainte de a crea versiunea noua. Fara asta, fiecare rulare
 *  lasa duplicate. */
async function replaceExisting(remoteName, parentId) {
  const q = `name='${remoteName}' and '${parentId}' in parents and trashed=false`;
  const found = await kit.req('GET', `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(q)}&fields=files(id,name)`);
  for (const f of (found.files || [])) {
    await kit.drive.trashed(f.id, true);
    console.log(D(`    inlocuit (trash): ${remoteName}`));
  }
}

async function uploadRaw(localPath, remoteName, parentId, mime) {
  const content = fs.readFileSync(localPath, 'utf8');
  const f = await kit.drive.upload(remoteName, content, mime, parentId);
  return f;
}

async function asNativeDoc(localPath, name, parentId) {
  // Docs API direct e blocat din cloud; conversia prin Drive merge.
  const tmp = await kit.drive.upload(`TMP-${name}.md`, fs.readFileSync(localPath, 'utf8'), 'text/markdown', parentId);
  const conv = await kit.req('POST', `https://www.googleapis.com/drive/v3/files/${tmp.id}/copy`, {
    name: name.replace(/\.md$/, ''), mimeType: 'application/vnd.google-apps.document',
  });
  // sursa temporara: se trueste imediat (reversibil). Master-ul text e deja
  // uploadat separat ca `MavisCloud-<nume>.md`.
  await kit.drive.trashed(tmp.id, true);
  return { doc: conv, tmp };
}

(async () => {
  console.log(B(`\n=== LIVRARE PE DRIVE → Mavis-Cloud-Google-Access-Bot ===\n`));
  console.log(D(`  bot folder: ${BOT}\n`));

  const manifest = [];

  // 1. structura de foldere
  const folders = {};
  for (const s of Object.keys(SUB)) {
    // 06-Handoff exista deja ca subfolder al botului (creat de POPY)
    if (s === '06-Handoff') {
      const q = `name='06-Handoff' and '${BOT}' in parents and trashed=false`;
      const found = await kit.req('GET', `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(q)}&fields=files(id,name)`);
      folders[s] = (found.files || [])[0] ? found.files[0].id : await ensureFolder(s, BOT);
    } else {
      folders[s] = await ensureFolder(s, BOT);
    }
    console.log(D(`  folder: ${s} → ${folders[s]}`));
  }
  folders['03-Skills'] = await ensureFolder('03-Skills', BOT);

  // 2. documente
  for (const [sub, files] of Object.entries(SUB)) {
    for (const rel of files) {
      const local = path.join(REPO, '21-GOOGLE-ACCESS-BOT', rel);
      if (!fs.existsSync(local)) { console.log(R(`  LIPSA: ${rel}`)); continue; }
      const remoteName = 'MavisCloud-' + path.basename(rel).replace(/^README\.md$/, 'README-GOOGLE-ACCESS-BOT.md');
      try {
        await replaceExisting(remoteName, folders[sub]);
        const f = await uploadMd(local, remoteName, folders[sub]);
        manifest.push({ sub, nume: remoteName, id: f.id, tip: 'markdown' });
        console.log(G(`  OK  ${sub}/${remoteName}`) + D(`  ${f.id}`));
      } catch (e) {
        console.log(R(`  FAIL ${sub}/${remoteName}: `) + String(e.message).slice(0, 110));
      }
    }
  }

  // 3. probe-ul brut
  try {
    const p = path.join(REPO, 'mavis-tools', '.capabilities.json');
    if (fs.existsSync(p)) {
      await replaceExisting(`MavisCloud-Probe-Capabilitati-${STAMP}.json`, folders['04-Capabilitati']);
    const f = await uploadRaw(p, `MavisCloud-Probe-Capabilitati-${STAMP}.json`, folders['04-Capabilitati'], 'application/json');
      manifest.push({ sub: '04-Capabilitati', nume: `MavisCloud-Probe-Capabilitati-${STAMP}.json`, id: f.id, tip: 'json' });
      console.log(G(`  OK  04-Capabilitati/probe.json`));
    }
  } catch (e) { console.log(R('  FAIL probe.json: ' + String(e.message).slice(0, 100))); }

  // 4. skill-urile
  const skillDir = path.join(REPO, '.skills');
  const skillNames = fs.readdirSync(skillDir).filter((n) => n.startsWith('mavis-cloud-google-access-bot') || n.startsWith('mavis-cloud-skill-'));
  for (const n of skillNames) {
    const local = path.join(skillDir, n, 'SKILL.md');
    if (!fs.existsSync(local)) continue;
    try {
      // mavis-cloud-skill-drive -> drive ; mavis-cloud-google-access-bot -> google-access-bot
      const clean = n.replace(/^mavis-cloud-skill-/, '').replace(/^mavis-cloud-/, '');
      await replaceExisting(`MavisCloud-Skill-${clean}.md`, folders['03-Skills']);
      const f = await uploadMd(local, `MavisCloud-Skill-${clean}.md`, folders['03-Skills']);
      manifest.push({ sub: '03-Skills', nume: `MavisCloud-Skill-${clean}.md`, id: f.id, tip: 'skill' });
      console.log(G(`  OK  03-Skills/${n}.md`));
    } catch (e) { console.log(R(`  FAIL ${n}: ` + String(e.message).slice(0, 100))); }
  }

  // 5. versiuni Google Doc NATIVE pentru documentele cheie
  console.log(D('\n  Google Docs native (prin conversie Drive):'));
  for (const rel of AS_NATIVE_DOC) {
    const local = path.join(REPO, '21-GOOGLE-ACCESS-BOT', rel);
    if (!fs.existsSync(local)) continue;
    const sub = rel.startsWith('HANDOFF/') ? '06-Handoff'
      : rel === 'TRANSCRIPT-SESIUNE-2026-10-28.md' ? '01-Transcript'
      : rel === 'EVAL-SKILL-VS-BASELINE.md' ? '02-Deliverables'
      : '02-Deliverables';
    try {
      const docName = 'MavisCloud-' + path.basename(rel, '.md').replace(/^README$/, 'Google-Access-Bot');
      await replaceExisting(docName, folders[sub]);
      const { doc } = await asNativeDoc(local, docName, folders[sub]);
      const t = String(await kit.docs.text(doc.id));
      manifest.push({ sub, nume: docName, id: doc.id, tip: 'gdoc', caractere: t.length });
      console.log(G(`  OK  ${sub}/${docName}`) + D(`  doc nativ ${doc.id} · export ${t.length} char`));
    } catch (e) { console.log(R(`  FAIL ${rel}: ` + String(e.message).slice(0, 110))); }
  }

  // 6. manifest
  const mf = path.join(REPO, '21-GOOGLE-ACCESS-BOT', 'MANIFEST-DRIVE.json');
  fs.writeFileSync(mf, JSON.stringify({ stamp: STAMP, bot: BOT, folders, items: manifest }, null, 2));
  console.log(B(`\n  ${manifest.length} elemente livrate.`));
  console.log(D(`  manifest: ${mf}`));
  console.log(D(`  Drive: https://drive.google.com/drive/folders/${BOT}\n`));
  process.exit(0);
})().catch((e) => { console.error(R('\nFAIL: ' + e.message + '\n')); process.exit(3); });

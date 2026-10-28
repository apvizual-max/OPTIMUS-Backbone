#!/usr/bin/env node
/**
 * DRIVE VAULT — acces la vault-ul PKMS din Google Drive, respectând regulile lui.
 *
 *   node mavis-tools/drive-vault.js root                 # structura de la rădăcină
 *   node mavis-tools/drive-vault.js ls "<cale>"           # conținutul unui folder
 *   node mavis-tools/drive-vault.js read "<cale>"         # citește un fișier (.md)
 *   node mavis-tools/drive-vault.js find "<termen>"       # caută în 00_INDEX.md
 *   node mavis-tools/drive-vault.js index                # citește 00_INDEX.md din rădăcină
 *
 * REGULILE VAULTULUI (din AGENTS.md / COTOR.md, 21-10-2026) — respectate aici:
 *   1. Nu se șterge nimic. Nimic. Funcția `quarantine` mută, nu șterge.
 *   2. Nu se atinge arhiva externă (H:) — inaccesibilă din cloud, prin design.
 *   3. Nu se scrie o cale cu folder numerotat „din mână" — căile se descoperă.
 *   4. 00_INDEX.md nu se editează manual — se regenerează.
 *   5. Rădăcinile cu "_" nu primesc cod numeric.
 *   6. Zero ștergeri și zero mutări fără R0.
 *   7. Ramura Knights Templar rămâne neatinsă.
 *   8. Nu se scriu căi de reper în mână — se descoperă dinamic.
 *
 * PRIN ROST: READ-ONLY, cu o singură excepție — `quarantine`, care mută în
 * _QUARANTINE cu motiv scris. Și asta cere --confirm explicit.
 */
const path = require('path');
const k = require('./kit.js');

const C = {
  b: s => `\x1b[1m${s}\x1b[0m`, g: s => `\x1b[32m${s}\x1b[0m`,
  y: s => `\x1b[33m${s}\x1b[0m`, r: s => `\x1b[31m${s}\x1b[0m`, d: s => `\x1b[2m${s}\x1b[0m`,
};

const VAULT_NAME = 'GDrive-Second_Brain_PKMS';
const QUARANTINE = '_QUARANTINE';
const PROTECTED = [
  // reguli care nu se ating, nici cu quarantine
  'Knights Templar',
  '_SYSTEM',
  '.obsidian', '.trash', '.vault-intelligence', '.claudian', '.neural_memory', '.wwebjs_cache',
];

/** Rădăcina vaultului, descoperită dinamic (regula 8 — nu scriem căi de reper). */
async function findVaultRoot() {
  const r = await k.drive.list("mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed=false", 50);
  const v = r.files.find(f => f.name === VAULT_NAME);
  if (!v) {
    const names = r.files.map(f => f.name).join(', ');
    throw new Error(`Vaultul "${VAULT_NAME}" nu e la rădăcina Drive. Root are: ${names || '(gol)'}`);
  }
  return v;
}

/** Rezolvă o cale relativă din rădăcina vaultului -> id de folder. */
async function resolvePath(rel) {
  const root = await findVaultRoot();
  const parts = String(rel || '').split('/').map(s => s.trim()).filter(Boolean);
  if (!parts.length) return { root, folder: root, parts: [] };
  let cur = root;
  for (const part of parts) {
    const q = `name='${part.replace(/'/g, "\\'")}' and mimeType='application/vnd.google-apps.folder' and trashed=false`;
    const r = await k.drive.list(q, 20);
    if (!r.files.length) throw new Error(`Nu am gasit folderul "${part}" in calea "${rel}".`);
    cur = r.files[0];
  }
  return { root, folder: cur, parts };
}

async function listFolder(rel) {
  const { folder, parts } = await resolvePath(rel);
  const r = await k.drive.list(`'${folder.id}' in parents and trashed=false`, 200);
  const label = parts.length ? parts.join('/') : '(rădăcină)';
  console.log(C.b(`\n  ${label}`) + C.d(`  [${r.files.length} elemente]\n`));
  const folders = r.files.filter(f => f.mimeType === 'application/vnd.google-apps.folder');
  const files = r.files.filter(f => f.mimeType !== 'application/vnd.google-apps.folder');
  for (const f of folders) {
    const prot = PROTECTED.some(p => f.name.includes(p)) ? C.y('  [PROTECTAT — nu se atinge]') : '';
    console.log(`  ${C.b('[ ]')} ${f.name}${prot}`);
  }
  if (folders.length) console.log('');
  for (const f of files) {
    const kind = f.mimeType.replace('application/vnd.google-apps.', '').replace('text/', '');
    const size = f.size ? ` · ${(f.size / 1024).toFixed(0)} KB` : '';
    console.log(`  ${C.d('•')} ${f.name} ${C.d('(' + kind + size + ')')}`);
  }
  console.log('');
  return r.files;
}

/** Citește un fișier .md din vault. Fișierele obișnuite se citesc cu alt=media. */
async function readFile(rel) {
  const { folder, parts } = await resolvePath(path.dirname(rel) === '.' ? '' : path.dirname(rel));
  const name = path.basename(rel);
  const r = await k.drive.list(`'${folder.id}' in parents and name='${name.replace(/'/g, "\\'")}' and trashed=false`, 5);
  if (!r.files.length) throw new Error(`Nu am gasit fisierul "${name}" in "${parts.join('/')}".`);
  const f = r.files[0];
  if (f.mimeType === 'application/vnd.google-apps.document') {
    const t = await k.docs.text(f.id);
    console.log(t);
    return t;
  }
  const d = await k.req('GET', `https://www.googleapis.com/drive/v3/files/${f.id}?alt=media`);
  const txt = String(d.raw || d.data || '');
  console.log(txt);
  return txt;
}

/**
 * Scara de căutare a vaultului: NU scanăm arborele.
 * 1. știi calea -> deschizi folderul
 * 2. știi subiectul -> cauți în 00_INDEX.md
 * 3. nu știi nimic -> INDEX CENTRAL.md
 */
async function find(term, limit = 40) {
  const { root } = await findVaultRoot();
  const hits = [];
  // cautam in 00_INDEX.md din toate folderele urmarite de repo
  const q = `mimeType='text/markdown' and name='00_INDEX.md' and trashed=false`;
  let page = await k.drive.list(q, 1000);
  const all = page.files || [];
  for (const f of all) {
    if (!f.name) continue;
    const d = await k.req('GET', `https://www.googleapis.com/drive/v3/files/${f.id}?alt=media`);
    const txt = String(d.raw || d.data || '');
    if (txt.toLowerCase().includes(term.toLowerCase())) {
      // gasim folderul parinte prin lista de fisiere
      hits.push({ id: f.id, name: f.name });
    }
  }
  console.log(C.b(`\n  "${term}" — ${hits.length} indexuri contin termenul\n`));
  for (const h of hits.slice(0, limit)) console.log(`  ${C.g('•')} ${h.name}`);
  console.log(C.d(`\n  Sursa: indexurile 00_INDEX.md (nu continutul). ` +
    `Pentru "nu stiu nici subiectul" -> INDEX CENTRAL.md\n`));
  return hits;
}

async function quarantine(rel, reason) {
  if (!reason) throw new Error('Motivul e obligatoriu: nimic nu se muta fara motiv scris in index.');
  if (!process.argv.includes('--confirm')) {
    console.log(C.y('\n  QUARANTINE cere --confirm.'));
    console.log(C.d(`  node mavis-tools/drive-vault.js quarantine "${rel}" "<motiv>" --confirm\n`));
    return;
  }
  const { folder, parts } = await resolvePath(path.dirname(rel) === '.' ? '' : path.dirname(rel));
  const name = path.basename(rel);
  if (PROTECTED.some(p => (parts.join('/') + '/' + name).includes(p))) {
    throw new Error(`REFUZAT: "${rel}" e in zona protejata. Regula 1-2-7.`);
  }
  const r = await k.drive.list(`'${folder.id}' in parents and name='${name.replace(/'/g, "\\'")}' and trashed=false`, 5);
  if (!r.files.length) throw new Error(`Nu am gasit "${name}" in "${parts.join('/')}".`);
  const f = r.files[0];
  const qf = await k.drive.list(`name='${QUARANTINE}' and mimeType='application/vnd.google-apps.folder' and trashed=false`, 5);
  if (!qf.files.length) throw new Error(`Folderul ${QUARANTINE} nu exista.`);
  await k.drive.move(f.id, qf.files[0].id, folder.id);
  console.log(C.g(`  Mutat in ${QUARANTINE}: ${name}`));
  console.log(C.d(`  Motiv: ${reason}`));
  console.log(C.y('  Nu s-a sters nimic. Motivul trebuie scris si in 00_INDEX.md al folderului.'));
}

(async () => {
  const [cmd, ...rest] = process.argv.slice(2);
  try {
    if (cmd === 'root') {
      const v = await findVaultRoot();
      const r = await k.drive.list(`'${v.id}' in parents and trashed=false`, 200);
      console.log(C.b(`\n  ${v.name}`) + C.d(`  [${r.files.length} elemente la rădăcină]\n`));
      for (const f of r.files) {
        if (f.mimeType === 'application/vnd.google-apps.folder') console.log(`  ${C.b('[ ]')} ${f.name}`);
        else console.log(`  ${C.d('•')} ${f.name}`);
      }
      console.log('');
    } else if (cmd === 'ls') {
      await listFolder(rest.join(' '));
    } else if (cmd === 'read') {
      await readFile(rest.join(' '));
    } else if (cmd === 'find') {
      await find(rest.join(' '));
    } else if (cmd === 'quarantine') {
      await quarantine(rest[0], rest[1]);
    } else {
      console.log(C.b('\n  DRIVE VAULT — comenzi:\n'));
      console.log('    node mavis-tools/drive-vault.js root');
      console.log('    node mavis-tools/drive-vault.js ls "<subfolder>"');
      console.log('    node mavis-tools/drive-vault.js read "<nume.md>"');
      console.log('    node mavis-tools/drive-vault.js find "<termen>"');
      console.log('    node mavis-tools/drive-vault.js quarantine "<cale>" "<motiv>" --confirm\n');
      console.log(C.d('  READ-ONLY, cu o singură excepție: quarantine mută, nu șterge.\n'));
    }
  } catch (e) {
    console.log(C.r('\n  Eroare: ' + e.message + '\n'));
    process.exit(1);
  }
})();

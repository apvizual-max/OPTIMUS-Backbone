#!/usr/bin/env node
/**
 * ARBOREA DRIVE — afișează structura unui folder (recursiv, 2 niveluri).
 *
 *   node mavis-tools/drive-tree.js [folderId] [--depth 2]
 *
 * Implicit: folderul principal al botului.
 */

const path = require('path');
const kit = require('./kit.js');

const args = process.argv.slice(2);
const depth = args.includes('--depth') ? Number(args[args.indexOf('--depth') + 1]) : 2;
const ROOT = args.find((a) => a && !a.startsWith('--') && a !== String(depth)) || '1UQIxhctyJxBXIIFnpxSc5Jd0wvFxEylu';

const D = (s) => `\x1b[2m${s}\x1b[0m`, B = (s) => `\x1b[1m${s}\x1b[0m`;
const G = (s) => `\x1b[32m${s}\x1b[0m`;

const q = (parent) => `'${parent}' in parents and trashed=false`;

async function walk(parent, level) {
  const r = await kit.req('GET',
    `https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(q(parent))}` +
    `&fields=files(id,name,mimeType,size,modifiedTime,webViewLink)&pageSize=200&orderBy=name`);
  const files = r.files || [];
  for (const f of files) {
    const isFolder = f.mimeType === 'application/vnd.google-apps.folder';
    const isDoc = f.mimeType === 'application/vnd.google-apps.document';
    const tag = isFolder ? B('[FOLDER]') : isDoc ? G('[GDOC] ') : D('[FILE] ');
    const size = f.size ? D(` ${f.size}B`) : '';
    console.log(`  ${'  '.repeat(level)}${tag} ${f.name}${size}`);
    if (isFolder && level < depth) await walk(f.id, level + 1);
  }
  if (!files.length && level > 0) console.log(`  ${'  '.repeat(level)}${D('(gol)')}`);
}

(async () => {
  console.log(B(`\n=== ARBORE DRIVE: ${ROOT} ===\n`));
  const meta = await kit.req('GET', `https://www.googleapis.com/drive/v3/files/${ROOT}?fields=id,name,mimeType,webViewLink`);
  console.log(D(`  ${meta.name}`));
  console.log(D(`  ${meta.webViewLink}\n`));
  await walk(ROOT, 0);
  console.log();
})().catch((e) => { console.error('FAIL: ' + e.message); process.exit(1); });

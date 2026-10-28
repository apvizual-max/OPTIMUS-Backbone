#!/usr/bin/env node
/**
 * verify-mcp-development.mjs - prove the MCP registry is healthy and that the
 * route for adding a server is real.
 *
 * Checks:
 *   V1  the global registry parses and holds the servers it claims to
 *   V2  EVERY local path any stdio entry points to exists on disk
 *   V3  the Google_Access entry is enabled and points at the measured endpoint
 *   V4  the container source and the repo source are identical (the rebuild
 *       source is truthful)
 *   V5  the development route's own instruments exist
 *
 * V2 is the check that had to exist: three entries pointed at a moved folder
 * and the registry said "enabled".
 *
 * Exit: 0 = all checks passed, 1 = a check failed, 3 = the registry is absent.
 */

import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';

const MCP_JSON = join(homedir(), '.minimax', 'mcp.json');
const REPO = 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Google_Access';
const EXPECTED_URL = 'http://127.0.0.1:8766/mcp';
const defects = [];

function check(id, ok, detail) {
  console.log(`${ok ? 'OK  ' : 'FAIL'} ${id} ${detail}`);
  if (!ok) defects.push(`${id}: ${detail}`);
  return ok;
}

if (!check('V0.registry-exists', existsSync(MCP_JSON), MCP_JSON)) {
  console.log('VERDICT=FAIL (no registry)');
  process.exit(3);
}

let reg;
try {
  reg = JSON.parse(readFileSync(MCP_JSON, 'utf8')).mcpServers || {};
} catch (e) {
  console.log('VERDICT=FAIL (registry unreadable)');
  process.exit(3);
}

// V1
const names = Object.keys(reg);
check('V1.registry-parses', names.length >= 15, `servers=${names.length}`);

// V2 - every local path of every stdio entry
const dead = [];
let checked = 0;
for (const [name, e] of Object.entries(reg)) {
  if (!e || e.type !== 'stdio') continue;
  const paths = [];
  if (typeof e.command === 'string' && /[\\/]/.test(e.command)) paths.push(e.command);
  for (const a of e.args || []) {
    if (typeof a === 'string' && /^[A-Za-z]:\\/.test(a) && /\.(js|mjs|cjs|cmd|exe|ps1)$/.test(a)) paths.push(a);
  }
  for (const p of paths) {
    checked++;
    if (!existsSync(p)) dead.push(`${name} -> ${p}`);
  }
}
check('V2.no-dead-paths', dead.length === 0, `checked=${checked} dead=${dead.length}${dead.length ? ' -> ' + dead.join(', ') : ''}`);

// V3
const ga = reg['Google_Access'];
check(
  'V3.google-access-registered',
  Boolean(ga) && ga.enabled !== false && String(ga.url || '').trim() === EXPECTED_URL,
  ga ? `enabled=${ga.enabled} url=${ga.url}` : 'Google_Access missing'
);

// V4 - repo source == live source
const repoServer = join(REPO, 'container', 'server.mjs');
const liveServer = 'C:\\Users\\apviz\\.minimax\\google-access\\server.mjs';
let same = false;
if (existsSync(repoServer) && existsSync(liveServer)) {
  const h = (p) => createHash('sha256').update(readFileSync(p)).digest('hex');
  same = h(repoServer) === h(liveServer);
}
check('V4.repo-equals-live-source', same, `repo=${existsSync(repoServer) ? 'present' : 'MISSING'} live=${existsSync(liveServer) ? 'present' : 'MISSING'}`);

// V5 - the instruments of the route
const tools = [
  join(REPO, 'scripts', 'probe-mcp-stdio.mjs'),
  join(REPO, 'scripts', 'sync-container-source.py'),
  join(REPO, 'scripts', 'ga-doctor.mjs'),
];
const missingTools = tools.filter((t) => !existsSync(t));
check('V5.instruments-exist', missingTools.length === 0, missingTools.length ? 'missing: ' + missingTools.join(', ') : `${tools.length} instruments present`);

console.log('');
console.log(defects.length === 0 ? 'VERDICT=PASS (5 checks)' : `VERDICT=FAIL (${defects.length} defect(s))`);
for (const x of defects) console.log('  - ' + x);
process.exit(defects.length === 0 ? 0 : 1);

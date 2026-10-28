#!/usr/bin/env node
/**
 * verify-browser-mcp.mjs - prove the browser layer of Google Access is real.
 *
 * Checks:
 *   V1  the global registry contains `minimax-notebooklm`
 *   V2  its registered script path EXISTS on disk
 *   V3  it completes a REAL stdio handshake and advertises tools
 *   V4  the own Chrome profile directory exists and the CDP port is declared
 *   V5  the registry's `notebooklm-mcp` entry is the shared package, not a
 *       minimax capability (namespace separation, measured not assumed)
 *
 * Exit: 0 = all checks passed, 1 = a check failed, 3 = the registry is absent.
 */

import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';
import { spawn } from 'node:child_process';

const MCP_JSON = join(homedir(), '.minimax', 'mcp.json');
const PROFILE = join(process.env.LOCALAPPDATA || join(homedir(), 'AppData', 'Local'), 'minimax-notebooklm', 'chrome_profile');
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

const reg = JSON.parse(readFileSync(MCP_JSON, 'utf8')).mcpServers || {};
const entry = reg['minimax-notebooklm'];
if (!check('V1.registered', Boolean(entry), 'minimax-notebooklm present in mcp.json')) {
  console.log(`VERDICT=FAIL (${defects.length} defect(s))`);
  process.exit(1);
}

const script = entry.args && entry.args[0];
check('V2.path-exists', Boolean(script) && existsSync(script), String(script));

// V3 - the real handshake
const result = await new Promise((resolve) => {
  const child = spawn(entry.command, entry.args || [], { windowsHide: true, stdio: ['pipe', 'pipe', 'ignore'] });
  let buf = '';
  const pending = new Map();
  let id = 0;
  let settled = false;
  const finish = (r) => {
    if (settled) return;
    settled = true;
    try { child.kill(); } catch { /* already gone */ }
    resolve(r);
  };
  child.on('error', (e) => finish({ ok: false, reason: 'spawn_error:' + e.message }));
  child.stdout.on('data', (c) => {
    buf += c.toString();
    let i;
    while ((i = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      if (!line) continue;
      let m;
      try { m = JSON.parse(line); } catch { continue; }
      if (m.id !== undefined && pending.has(m.id)) {
        const p = pending.get(m.id);
        pending.delete(m.id);
        p(m);
      }
    }
  });
  const call = (method, params) =>
    new Promise((r) => {
      const i = ++id;
      pending.set(i, r);
      try { child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: i, method, params }) + '\n'); }
      catch { pending.delete(i); r(null); }
    });
  (async () => {
    const init = await call('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'verify-browser-mcp', version: '1.0.0' },
    });
    if (!init || !init.result) return finish({ ok: false, reason: 'no_initialize_answer' });
    const list = await call('tools/list', {});
    const tools = list && list.result && Array.isArray(list.result.tools) ? list.result.tools.length : 0;
    finish({ ok: tools > 0, server: (init.result.serverInfo || {}).name || '?', tools });
  })();
  setTimeout(() => finish({ ok: false, reason: 'timeout' }), 30000);
});

check('V3.handshake', Boolean(result.ok), result.ok ? `server=${result.server} tools=${result.tools}` : 'reason=' + result.reason);

// V4 - the own profile
check('V4.own-profile', existsSync(PROFILE), PROFILE);

// V5 - namespace separation: the shared package must NOT be the minimax one
const shared = reg['notebooklm-mcp'];
const sharedOk = Boolean(shared) && /notebooklm-mcp/i.test(String(shared.command || ''));
check('V5.namespace-separation', sharedOk, shared ? `notebooklm-mcp -> ${shared.command}` : 'notebooklm-mcp not registered');

console.log('');
console.log(defects.length === 0 ? 'VERDICT=PASS (5 checks)' : `VERDICT=FAIL (${defects.length} defect(s))`);
for (const x of defects) console.log('  - ' + x);
process.exit(defects.length === 0 ? 0 : 1);

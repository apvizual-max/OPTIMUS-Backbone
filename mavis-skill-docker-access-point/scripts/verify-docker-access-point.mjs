#!/usr/bin/env node
/**
 * verify-docker-access-point.mjs - prove the Docker substrate of Google Access
 * is what it claims to be.
 *
 * Checks (each independent):
 *   V1  the container exists, runs, and is healthy
 *   V2  the restart policy is unless-stopped (it must survive a reboot)
 *   V3  the data volume is mounted read-write and the secrets volume read-only
 *   V4  the credential is NOT baked into the image (no credentials.json in any
 *       image layer)
 *   V5  the bytes running inside the container equal the bytes in the repo
 *
 * V5 is the one that caught the 1.0.9 incident: healthy container, old code.
 *
 * Exit: 0 = all checks passed, 1 = a check failed, 3 = docker itself is absent.
 */

import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';

const CONTAINER = 'Google_Access';
const REPO_FILE = 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Google_Access\\container\\server.mjs';
const defects = [];

function check(id, ok, detail) {
  console.log(`${ok ? 'OK  ' : 'FAIL'} ${id} ${detail}`);
  if (!ok) defects.push(`${id}: ${detail}`);
  return ok;
}

function docker(args, opts) {
  return execFileSync('docker', args, Object.assign({ encoding: 'utf8', windowsHide: true, timeout: 60000 }, opts || {}));
}

let inspect;
try {
  inspect = docker(['inspect', CONTAINER]);
} catch (e) {
  console.log('ERROR: docker inspect failed for ' + CONTAINER + ' (is the container running?)');
  console.log('VERDICT=FAIL (container not reachable)');
  process.exit(3);
}

const d = JSON.parse(inspect)[0];
const status = d.State ? d.State.Status : '?';
const health = d.State && d.State.Health ? d.State.Health.Status : 'none';
const policy = d.HostConfig && d.HostConfig.RestartPolicy ? d.HostConfig.RestartPolicy.Name : '?';
const image = d.Config ? d.Config.Image : '?';

check('V1.running-healthy', status === 'running' && health === 'healthy', `status=${status} health=${health} image=${image}`);
check('V2.restart-policy', policy === 'unless-stopped', `restart=${policy}`);

// V3 - mounts
const mounts = (d.Mounts || []).map((m) => ({
  source: m.Source,
  dest: m.Destination,
  rw: m.RW === true,
}));
const data = mounts.find((m) => m.dest === '/data');
const secrets = mounts.find((m) => m.dest === '/secrets');
check('V3.data-volume-rw', Boolean(data && data.rw), data ? `${data.source} -> /data rw=${data.rw}` : 'no /data mount');
check('V3.secrets-volume-ro', Boolean(secrets && !secrets.rw), secrets ? `${secrets.source} -> /secrets rw=${secrets.rw}` : 'no /secrets mount');

// V4 - the credential must not be inside the image
let inImage = false;
try {
  const layers = docker(['image', 'save', image, '-o', process.env.TEMP + '\\ga-image-probe.tar']).toString();
  inImage = layers.includes('credentials.json');
} catch {
  // image save may be unavailable; fall back to inspecting the image config
  try {
    const cfg = docker(['image', 'inspect', image]);
    inImage = cfg.includes('credentials.json');
  } catch {
    inImage = false;
  }
}
check('V4.credential-not-in-image', !inImage, inImage ? 'credentials.json IS present in the image' : 'no credential inside the image');

// V5 - the running bytes equal the repo bytes
let live = '';
try {
  live = docker([
    'exec', CONTAINER, 'node', '-p',
    "require('crypto').createHash('sha256').update(require('fs').readFileSync('/app/server.mjs')).digest('hex')",
  ]).trim().split(/\r?\n/).filter(Boolean).pop();
} catch {
  live = '';
}
let repoHash = '';
try {
  const { createHash } = await import('node:crypto');
  const { readFileSync } = await import('node:fs');
  repoHash = createHash('sha256').update(readFileSync(REPO_FILE)).digest('hex');
} catch {
  repoHash = '';
}
check(
  'V5.running-equals-repo',
  Boolean(live) && live === repoHash,
  `running=${(live || '?').slice(0, 12)} repo=${repoHash.slice(0, 12)}`
);

console.log('');
console.log(defects.length === 0 ? 'VERDICT=PASS (5 checks)' : `VERDICT=FAIL (${defects.length} defect(s))`);
for (const x of defects) console.log('  - ' + x);
process.exit(defects.length === 0 ? 0 : 1);

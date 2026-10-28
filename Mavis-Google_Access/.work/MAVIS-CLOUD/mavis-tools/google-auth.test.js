const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const { readJson } = require('./google-auth.js');

/**
 * RULEA (masurat 2026-10-27): client_id + client_secret trebuie sa vina din
 * ACEEASI sursa cu refresh_token. Altfel Google raspunde invalid_grant /
 * unauthorized_client — pentru ca refresh-tokenul apartine altui client.
 *
 * Cazul masurat in cloud: tokenul era al clientului ...u773, iar
 * credentials.json tinea clientul ...5b7h17gt1c5hc4. Implementarea veche
 * amesteca cele doua -> 403/401 la fiecare apel.
 */
function withFakeHome(files, fn) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'google-auth-home-'));
  const prevHome = process.env.HOME;
  const prevEnv = {};
  for (const k of ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REFRESH_TOKEN',
    'GOOGLE_CLIENT_ID_MAVIS_CLOUD', 'GOOGLE_CLIENT_SECRET_MAVIS_CLOUD',
    'GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD']) {
    prevEnv[k] = process.env[k];
    delete process.env[k];
  }
  try {
    fs.mkdirSync(path.join(tempDir, '.google-mcp', 'tokens'), { recursive: true });
    for (const [rel, content] of Object.entries(files)) {
      const p = path.join(tempDir, rel);
      fs.mkdirSync(path.dirname(p), { recursive: true });
      fs.writeFileSync(p, typeof content === 'string' ? content : JSON.stringify(content));
    }
    process.env.HOME = tempDir;
    const modPath = require.resolve('./google-auth.js');
    delete require.cache[modPath];
    const mod = require(modPath);
    return fn(mod);
  } finally {
    delete require.cache[require.resolve('./google-auth.js')];
    if (prevHome === undefined) delete process.env.HOME; else process.env.HOME = prevHome;
    for (const [k, v] of Object.entries(prevEnv)) {
      if (v === undefined) delete process.env[k]; else process.env[k] = v;
    }
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
}

test('fromFiles: token file with its own client wins over credentials.json', () => {
  withFakeHome({
    '.google-mcp/credentials.json': { installed: { client_id: 'CLIENT-FROM-CREDS', client_secret: 'SECRET-FROM-CREDS' } },
    '.google-mcp/tokens/mavis.json': { refresh_token: 'RT-FROM-TOKEN', client_id: 'CLIENT-FROM-TOKEN', client_secret: 'SECRET-FROM-TOKEN' },
  }, (mod) => {
    const r = mod.fromFiles();
    assert.ok(r, 'credentialele trebuie sa se rezolve');
    assert.equal(r.client_id, 'CLIENT-FROM-TOKEN');
    assert.equal(r.client_secret, 'SECRET-FROM-TOKEN');
    assert.equal(r.refresh_token, 'RT-FROM-TOKEN');
    assert.equal(r.client_source, 'token-file');
    assert.equal(r.mixed_sources, false);
  });
});

test('fromFiles: falls back to credentials.json when the token file carries no client', () => {
  withFakeHome({
    '.google-mcp/credentials.json': { installed: { client_id: 'CLIENT-FROM-CREDS', client_secret: 'SECRET-FROM-CREDS' } },
    '.google-mcp/tokens/mavis.json': { refresh_token: 'RT-FROM-TOKEN' },
  }, (mod) => {
    const r = mod.fromFiles();
    assert.ok(r);
    assert.equal(r.client_id, 'CLIENT-FROM-CREDS');
    assert.equal(r.client_source, 'credentials-file');
  });
});

test('fromFiles: never mixes the client of one source with the token of another', () => {
  withFakeHome({
    '.google-mcp/credentials.json': { installed: { client_id: 'CLIENT-FROM-CREDS', client_secret: 'SECRET-FROM-CREDS' } },
    '.google-mcp/tokens/mavis.json': { refresh_token: 'RT-FROM-TOKEN', client_id: 'CLIENT-FROM-TOKEN' },
  }, (mod) => {
    // Tokenul are client_id dar NU are client_secret: perechea completa nu
    // poate fi asamblata din surse diferite. Rezultatul corect este null.
    const r = mod.fromFiles();
    assert.equal(r, null);
  });
});

test('describe: reports different-clients instead of hiding the mismatch', () => {
  withFakeHome({
    '.google-mcp/credentials.json': { installed: { client_id: 'CLIENT-FROM-CREDS', client_secret: 'SECRET-FROM-CREDS' } },
    '.google-mcp/tokens/mavis.json': { refresh_token: 'RT-FROM-TOKEN', client_id: 'CLIENT-FROM-TOKEN', client_secret: 'SECRET-FROM-TOKEN' },
  }, (mod) => {
    const d = mod.describe();
    assert.equal(d.client_pairing, 'different-clients');
    assert.equal(d.client_source, 'token-file');
    assert.equal(d.mixed_sources, false);
  });
});

test('fromEnv: prefers the _MAVIS_CLOUD triple as one unit, never mixed with unsuffixed vars', () => {
  withFakeHome({}, (mod) => {
    process.env.GOOGLE_CLIENT_ID = 'CLIENT-UNSUFFIXED';
    process.env.GOOGLE_CLIENT_SECRET = 'SECRET-UNSUFFIXED';
    process.env.GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD = 'RT-CLOUD';
    try {
      const r = mod.fromEnv();
      // Doar refresh_token-ul _MAVIS_CLOUD exista: perechea nu e completa,
      // deci NU se amesteca cu clientul nesufixit.
      assert.equal(r, null);
      // Iar diagnosticul arata exact amestecul, ca remedierea sa fie un pas.
      const d = mod.describe();
      assert.ok(Array.isArray(d.mixed_env), 'mixed_env trebuie raportat');
      assert.equal(d.mixed_env.length, 3);
      assert.equal(d.resolved, false);
      process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD = 'CLIENT-CLOUD';
      process.env.GOOGLE_CLIENT_SECRET_MAVIS_CLOUD = 'SECRET-CLOUD';
      const r2 = mod.fromEnv();
      assert.ok(r2);
      assert.equal(r2.client_id, 'CLIENT-CLOUD');
      assert.equal(r2.client_secret, 'SECRET-CLOUD');
      assert.equal(r2.refresh_token, 'RT-CLOUD');
      assert.equal(r2.mixed_sources, false);
    } finally {
      delete process.env.GOOGLE_CLIENT_ID;
      delete process.env.GOOGLE_CLIENT_SECRET;
      delete process.env.GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD;
      delete process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD;
      delete process.env.GOOGLE_CLIENT_SECRET_MAVIS_CLOUD;
    }
  });
});

test('readJson handles non-existent file', () => {
  const result = readJson(path.join(os.tmpdir(), 'this-file-will-never-exist-' + Date.now() + '.json'));
  assert.equal(result, null);
});

test('readJson successfully reads valid JSON', () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'google-auth-test-'));
  const tempPath = path.join(tempDir, 'test-valid.json');
  fs.writeFileSync(tempPath, JSON.stringify({ key: 'value' }));

  try {
    const result = readJson(tempPath);
    assert.deepEqual(result, { key: 'value' });
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test('readJson handles invalid JSON', () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'google-auth-test-'));
  const tempPath = path.join(tempDir, 'test-invalid.json');
  fs.writeFileSync(tempPath, '{ key: value'); // Invalid JSON

  try {
    const result = readJson(tempPath);
    assert.equal(result, null);
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

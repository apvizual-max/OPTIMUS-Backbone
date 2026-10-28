const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const child_process = require('child_process');

const { readClientConfig, git, hasLiveToken } = require('./google-refresh.js');

test('readClientConfig should return null on fs.readFileSync error', (t) => {
  // mock fs.readFileSync to throw an error
  t.mock.method(fs, 'readFileSync', () => {
    throw new Error('Mock error');
  });

  const config = readClientConfig();
  assert.strictEqual(config, null);
});

test('readClientConfig should return parsed JSON on success', (t) => {
  const mockConfig = { client_id: 'test_client_id' };
  t.mock.method(fs, 'readFileSync', () => {
    return JSON.stringify(mockConfig);
  });

  const config = readClientConfig();
  assert.deepStrictEqual(config, mockConfig);
});

test('git should return null on execFileSync error', (t) => {
  t.mock.method(child_process, 'execFileSync', () => {
    throw new Error('Mock error');
  });

  const result = git(['status']);
  assert.strictEqual(result, null);
});

test('hasLiveToken should correctly evaluate tokens in process.env', (t) => {
  // Cache original env values to ensure test isolation
  const originalEnv = { ...process.env };

  t.after(() => {
    // Restore original env
    process.env = originalEnv;
  });

  // Test 1: Missing both tokens
  delete process.env.GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD;
  delete process.env.GOOGLE_REFRESH_TOKEN;
  assert.strictEqual(hasLiveToken(), false);

  // Test 2: MAVIS token present but too short
  process.env.GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD = 'short';
  assert.strictEqual(hasLiveToken(), false);

  // Test 3: MAVIS token present and long enough
  process.env.GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD = 'a'.repeat(41);
  assert.strictEqual(hasLiveToken(), true);

  // Test 4: MAVIS token absent, fallback token present and long enough
  delete process.env.GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD;
  process.env.GOOGLE_REFRESH_TOKEN = 'b'.repeat(41);
  assert.strictEqual(hasLiveToken(), true);

  // Test 5: Only fallback token present, but too short
  process.env.GOOGLE_REFRESH_TOKEN = 'short';
  assert.strictEqual(hasLiveToken(), false);
});

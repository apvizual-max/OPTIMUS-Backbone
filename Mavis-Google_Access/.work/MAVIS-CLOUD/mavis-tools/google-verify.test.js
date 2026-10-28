const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const { execSync } = require('child_process');
const fs = require('fs');

test('google-verify exits correctly when tokeninfo fails', (t) => {
  const mockScriptPath = path.join(__dirname, 'google-verify-mock-runner.js');

  const runnerCode = `
    const path = require('path');
    const authPath = require.resolve('./google-auth.js');
    require.cache[authPath] = {
      id: authPath,
      filename: authPath,
      loaded: true,
      exports: {
        describe: () => ({ resolved: true, source: 'mock', missing: [] })
      }
    };

    const kitPath = require.resolve('./kit.js');
    require.cache[kitPath] = {
      id: kitPath,
      filename: kitPath,
      loaded: true,
      exports: {
        tokeninfo: async () => { throw new Error('Mock invalid_grant error'); }
      }
    };

    require('./google-verify.js');
  `;

  fs.writeFileSync(mockScriptPath, runnerCode);

  try {
    execSync(`node ${mockScriptPath} --json`, { encoding: 'utf-8', stdio: 'pipe' });
    assert.fail('Should have thrown due to exit 1');
  } catch (error) {
    assert.equal(error.status, 1, 'process.exit should be called with 1');
    const jsonOutput = error.stdout;
    const parsed = JSON.parse(jsonOutput.trim());

    // In google-verify.js: if (JSON_OUT) console.log(JSON.stringify(results, null, 2));
    // It prints an array `results` in this branch, not `{ results: [...] }`
    // However, looking at the code around line 57:
    // if (JSON_OUT) console.log(JSON.stringify(results, null, 2));
    const tokenResult = Array.isArray(parsed)
      ? parsed.find(r => r.service === 'token')
      : (parsed.results ? parsed.results.find(r => r.service === 'token') : null);

    assert.ok(tokenResult, 'Should output JSON with token failure');
    assert.equal(tokenResult.status, 'FAIL');
    assert.equal(tokenResult.detail, 'Mock invalid_grant error');
  } finally {
    fs.unlinkSync(mockScriptPath);
  }
});

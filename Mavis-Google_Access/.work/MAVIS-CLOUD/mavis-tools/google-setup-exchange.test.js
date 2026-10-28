const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn } = require('child_process');
const http = require('http');

test('exchange error handling in google-setup.js', async () => {
  const tempHome = fs.mkdtempSync(path.join(os.tmpdir(), 'mavis-test-'));
  const mcpDir = path.join(tempHome, '.google-mcp');
  fs.mkdirSync(mcpDir, { recursive: true });
  fs.writeFileSync(path.join(mcpDir, 'credentials.json'), JSON.stringify({
    installed: { client_id: 'test_client_id', client_secret: 'test_client_secret' }
  }));

  const interceptorPath = path.join(tempHome, 'mock-fetch.js');
  fs.writeFileSync(interceptorPath, `
    const originalFetch = global.fetch;
    global.fetch = async (url, opts) => {
        if (url === 'https://oauth2.googleapis.com/token') {
            const body = new URLSearchParams(opts.body);
            if (body.get('grant_type') === 'refresh_token' && body.get('refresh_token') === 'PREFLIGHT_PROBE_INVALID') {
                return { json: async () => ({ error: 'invalid_grant' }) };
            }
            if (body.get('code') === 'TEST_CODE') {
                return {
                    json: async () => ({
                        error: 'invalid_grant',
                        error_description: 'Bad verification code.'
                    })
                };
            }
        }
        return originalFetch(url, opts);
    };

    const originalExit = process.exit;
    process.exit = (code) => {
        console.log("PROCESS_EXIT_CODE:" + code);
        originalExit(code);
    };

    const originalExec = require('child_process').exec;
    require('child_process').exec = (cmd, cb) => {
        if (cmd.startsWith('open') || cmd.startsWith('start') || cmd.startsWith('xdg-open')) {
            if (cb) cb();
        } else {
            originalExec(cmd, cb);
        }
    };
  `);

  const p = spawn(process.execPath, ['--require', interceptorPath, path.join(__dirname, 'google-setup.js')], {
    env: { ...process.env, HOME: tempHome }
  });

  let output = '';
  let port = null;

  p.stdout.on('data', (data) => {
    const str = data.toString();
    output += str;
    if (!port) {
      const match1 = str.match(/http%3A%2F%2F127\.0\.0\.1%3A(\d+)/);
      const match2 = str.match(/http:\/\/127\.0\.0\.1:(\d+)/);
      if (match1) port = match1[1];
      else if (match2) port = match2[1];
    }
  });

  p.stderr.on('data', (data) => {
    output += data.toString();
  });

  for (let i = 0; i < 50; i++) {
    if (port) break;
    await new Promise(r => setTimeout(r, 100));
  }

  if (port) {
    await new Promise((resolve, reject) => {
      http.get("http://127.0.0.1:" + port + "/callback?code=TEST_CODE", (res) => {
        res.resume();
        res.on('end', resolve);
      }).on('error', reject);
    });
  } else {
    p.kill();
    throw new Error('Port not found in output');
  }

  const exitCode = await new Promise(resolve => {
    const timeout = setTimeout(() => {
        p.kill();
        resolve(-1);
    }, 5000);
    p.on('close', (code) => {
        clearTimeout(timeout);
        resolve(code);
    });
  });

  fs.rmSync(tempHome, { recursive: true, force: true });

  assert.equal(exitCode, 1, 'Process should exit with code 1 when exchange fails');
  assert.ok(output.includes('Schimbul codului a esuat'), 'Should log the error message');
  assert.ok(output.includes('invalid_grant'), 'Should log the error code');
  assert.ok(output.includes('Bad verification code.'), 'Should log the error description');
});

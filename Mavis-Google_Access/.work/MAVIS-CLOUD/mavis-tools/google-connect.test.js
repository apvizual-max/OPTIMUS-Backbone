const test = require('node:test');
const assert = require('node:assert');

const { extractCode } = require('./google-connect.js');

test('extractCode should return null for falsy/empty inputs', () => {
  assert.strictEqual(extractCode(null), null);
  assert.strictEqual(extractCode(undefined), null);
  assert.strictEqual(extractCode(''), null);
  assert.strictEqual(extractCode('   '), null);
});

test('extractCode should extract code from query parameter', () => {
  assert.strictEqual(extractCode('http://127.0.0.1:8976/callback?code=abc_123'), 'abc_123');
  assert.strictEqual(extractCode('https://example.com/?some=val&code=4/0AeaYSH...'), '4/0AeaYSH...');
});

test('extractCode should decode URL-encoded query parameter', () => {
  assert.strictEqual(extractCode('http://127.0.0.1:8976/callback?code=a%2Fb%3Dc'), 'a/b=c');
});

test('extractCode should return the raw string if it matches the valid character set', () => {
  assert.strictEqual(extractCode('4/0AeaYSH-abc_def'), '4/0AeaYSH-abc_def');
  assert.strictEqual(extractCode('valid_code-123.456'), 'valid_code-123.456');
});

test('extractCode should return null for invalid strings without code parameter', () => {
  assert.strictEqual(extractCode('some random text!'), null);
  assert.strictEqual(extractCode('http://127.0.0.1:8976/callback?notcode=abc'), null);
  assert.strictEqual(extractCode('invalid code with spaces'), null);
});

test('extractCode should return null for empty code parameter', () => {
  assert.strictEqual(extractCode('http://127.0.0.1:8976/callback?code='), null);
});

test('extractCode should gracefully handle non-string inputs', () => {
  assert.strictEqual(extractCode({ code: '123' }), null);
  assert.strictEqual(extractCode(['123']), '123'); // Array gets converted to '123'
});

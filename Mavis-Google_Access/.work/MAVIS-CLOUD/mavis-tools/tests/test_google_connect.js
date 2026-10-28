const assert = require('node:assert/strict');
const test = require('node:test');
const { extractCode } = require('../google-connect.js');

test('extractCode', async (t) => {
  await t.test('returns null for empty input', () => {
    assert.equal(extractCode(''), null);
    assert.equal(extractCode(null), null);
    assert.equal(extractCode(undefined), null);
    assert.equal(extractCode('   '), null);
  });

  await t.test('extracts code from full URL', () => {
    assert.equal(extractCode('http://127.0.0.1:8976/callback?code=4/0AfJohXl_xyz123'), '4/0AfJohXl_xyz123');
    assert.equal(extractCode('http://localhost/?code=some-code-here&state=123'), 'some-code-here');
  });

  await t.test('decodes URI encoded components', () => {
    assert.equal(extractCode('http://127.0.0.1:8976/?code=4%2F0AfJohXl_xyz123'), '4/0AfJohXl_xyz123');
  });

  await t.test('returns raw code if it matches regex', () => {
    assert.equal(extractCode('some-code-here'), 'some-code-here');
    assert.equal(extractCode('123abcXYZ._-'), '123abcXYZ._-');
  });

  await t.test('returns null for invalid strings without code param', () => {
    assert.equal(extractCode('http://127.0.0.1:8976/callback'), null);
    assert.equal(extractCode('just some random text'), null);
    assert.equal(extractCode('http://localhost/?state=123'), null);
  });

  await t.test('returns null for empty code param value', () => {
    assert.equal(extractCode('http://127.0.0.1:8976/callback?code='), null);
    assert.equal(extractCode('?code='), null);
    assert.equal(extractCode('&code='), null);
    assert.equal(extractCode('http://localhost/?code=&state=123'), null);
  });

});

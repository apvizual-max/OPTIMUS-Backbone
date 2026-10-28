const { test, describe, mock } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');

const { readJsonTolerant } = require('./google-local.js');

describe('google-local.js', () => {
  describe('readJsonTolerant', () => {
    test('returns null if file does not exist (throws ENOENT)', () => {
      mock.method(fs, 'readFileSync', () => {
        throw new Error('ENOENT');
      });
      const result = readJsonTolerant('dummy.json');
      assert.equal(result, null);
      mock.restoreAll();
    });

    test('parses pure valid JSON', () => {
      mock.method(fs, 'readFileSync', () => '{ "key": "value", "num": 123 }');
      const result = readJsonTolerant('dummy.json');
      assert.deepEqual(result, { key: 'value', num: 123 });
      mock.restoreAll();
    });

    test('returns null if string contains no open brace', () => {
      mock.method(fs, 'readFileSync', () => 'this is just text without braces');
      const result = readJsonTolerant('dummy.json');
      assert.equal(result, null);
      mock.restoreAll();
    });

    test('parses JSON hidden within junk characters', () => {
      mock.method(fs, 'readFileSync', () => 'junk text { "hidden": "json" } more junk');
      const result = readJsonTolerant('dummy.json');
      assert.deepEqual(result, { hidden: 'json' });
      mock.restoreAll();
    });

    test('parses nested JSON containing stringified braces', () => {
      const complexJson = '{ "test": "{ braces inside string }", "nested": { "a": 1 } }';
      mock.method(fs, 'readFileSync', () => 'junk ' + complexJson + ' junk');
      const result = readJsonTolerant('dummy.json');
      assert.deepEqual(result, { test: '{ braces inside string }', nested: { a: 1 } });
      mock.restoreAll();
    });

    test('handles escaped quotes within strings', () => {
      const complexJson = '{ "test": "has \\"quotes\\" and { braces } inside" }';
      mock.method(fs, 'readFileSync', () => 'junk ' + complexJson + ' junk');
      const result = readJsonTolerant('dummy.json');
      assert.deepEqual(result, { test: 'has "quotes" and { braces } inside' });
      mock.restoreAll();
    });

    test('returns null if JSON is incomplete', () => {
      mock.method(fs, 'readFileSync', () => 'junk { "incomplete": "json" junk');
      const result = readJsonTolerant('dummy.json');
      assert.equal(result, null);
      mock.restoreAll();
    });

    test('returns null if extracted substring is invalid JSON', () => {
      mock.method(fs, 'readFileSync', () => 'junk { "badly": formed, "json" } junk');
      const result = readJsonTolerant('dummy.json');
      assert.equal(result, null);
      mock.restoreAll();
    });
  });
});

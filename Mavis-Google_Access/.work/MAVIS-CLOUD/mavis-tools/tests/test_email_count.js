const assert = require('node:assert/strict');
const test = require('node:test');
const { pad } = require('../email-count.js');

test('pad', async (t) => {
  await t.test('pads string to specified length', () => {
    assert.equal(pad('foo', 5), 'foo  ');
    assert.equal(pad('hello', 10), 'hello     ');
  });

  await t.test('does not pad if string is already at or beyond specified length', () => {
    assert.equal(pad('foo', 3), 'foo');
    assert.equal(pad('hello', 2), 'hello');
  });

  await t.test('pads empty string correctly', () => {
    assert.equal(pad('', 4), '    ');
    assert.equal(pad('', 0), '');
  });
});

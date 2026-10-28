const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const { pad } = require('./email-count-exact.js');

describe('email-count-exact pad function', () => {
  test('pads string to specified length', () => {
    assert.equal(pad('hello', 10), 'hello     ');
  });

  test('does not pad if string is already equal to or longer than specified length', () => {
    assert.equal(pad('hello', 5), 'hello');
    assert.equal(pad('hello', 3), 'hello');
  });

  test('handles empty string', () => {
    assert.equal(pad('', 5), '     ');
  });

  test('handles edge case when length is 0 or negative', () => {
    assert.equal(pad('hello', 0), 'hello');
    assert.equal(pad('hello', -5), 'hello');
  });
});

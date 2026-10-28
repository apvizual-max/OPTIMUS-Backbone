const { test } = require('node:test');
const assert = require('node:assert/strict');
const { pad } = require('./email-count.js');

test('pad function correctly pads shorter strings', () => {
  assert.equal(pad('test', 10), 'test      ');
  assert.equal(pad('123', 5), '123  ');
});

test('pad function does not pad strings that are already the desired length or longer', () => {
  assert.equal(pad('exactly10!', 10), 'exactly10!');
  assert.equal(pad('longer_than_10', 10), 'longer_than_10');
});

test('pad function correctly pads empty strings', () => {
  assert.equal(pad('', 5), '     ');
  assert.equal(pad('', 0), '');
});

test('pad function handles negative padding length gracefully (should not change string)', () => {
  assert.equal(pad('test', -5), 'test');
});

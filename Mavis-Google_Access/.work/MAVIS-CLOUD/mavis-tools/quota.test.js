const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const { costOf } = require('./quota.js');

describe('mavis-tools/quota unit tests', () => {

  test('costOf returns the specific cost for known methods', () => {
    assert.equal(costOf('messages.get'), 20);
    assert.equal(costOf('messages.list'), 5);
    assert.equal(costOf('messages.send'), 100);
    assert.equal(costOf('history.list'), 2);
  });

  test('costOf returns the default cost (10) for unknown methods', () => {
    assert.equal(costOf('unknown.method'), 10);
    assert.equal(costOf('something.else'), 10);
  });

  test('costOf returns the default cost (10) for invalid inputs', () => {
    assert.equal(costOf(null), 10);
    assert.equal(costOf(undefined), 10);
    assert.equal(costOf(''), 10);
    assert.equal(costOf(123), 10);
  });
});

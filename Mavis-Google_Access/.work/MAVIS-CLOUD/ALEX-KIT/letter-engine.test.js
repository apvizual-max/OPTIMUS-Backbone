const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const { classifyBusiness } = require('./letter-engine.js');

describe('classifyBusiness', () => {
  test('returns DTC when jdText contains DTC keywords', () => {
    assert.equal(classifyBusiness('We are a direct-to-consumer brand'), 'DTC');
    assert.equal(classifyBusiness('Looking for someone to help with d2c marketing'), 'DTC');
    assert.equal(classifyBusiness('Our focus is on DTC sales'), 'DTC');
    assert.equal(classifyBusiness('Improving the checkout experience'), 'DTC');
    assert.equal(classifyBusiness('Developing our own product line'), 'DTC');
    assert.equal(classifyBusiness('Optimizing the add to cart flow'), 'DTC');
  });

  test('returns B2B when jdText contains B2B keywords', () => {
    assert.equal(classifyBusiness('We provide b2b solutions'), 'B2B');
    assert.equal(classifyBusiness('Selling to enterprise customers'), 'B2B');
    assert.equal(classifyBusiness('Helping our clients succeed'), 'B2B');
    assert.equal(classifyBusiness('We work with companies worldwide'), 'B2B');
    assert.equal(classifyBusiness('Building a new saas product'), 'B2B');
    assert.equal(classifyBusiness('Integrating with our API'), 'B2B');
    assert.equal(classifyBusiness('Managing subscription services'), 'B2B');
    assert.equal(classifyBusiness('Streamlining procurement processes'), 'B2B');
    assert.equal(classifyBusiness('Developing enterprise software'), 'B2B');
    assert.equal(classifyBusiness('A platform for developers'), 'B2B');
  });

  test('returns tagFromScoring without brackets if no keywords matched', () => {
    assert.equal(classifyBusiness('A generic job description', '[B2C]'), 'B2C');
    assert.equal(classifyBusiness('Another job ad', '[B2B]'), 'B2B');
    assert.equal(classifyBusiness('Nothing specific', 'DTC'), 'DTC');
  });

  test('defaults to B2C if no keywords matched and no tagFromScoring provided', () => {
    assert.equal(classifyBusiness('Just some text'), 'B2C');
    assert.equal(classifyBusiness(null), 'B2C');
    assert.equal(classifyBusiness(''), 'B2C');
    assert.equal(classifyBusiness(), 'B2C');
  });

  test('handles null or undefined jdText gracefully', () => {
    assert.equal(classifyBusiness(null, '[B2B]'), 'B2B');
    assert.equal(classifyBusiness(undefined, '[DTC]'), 'DTC');
  });

  test('DTC keywords take precedence over B2B if both are present', () => {
    assert.equal(classifyBusiness('We do both b2b and direct-to-consumer'), 'DTC');
  });
});

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { redact, validateOrigin } from './privacy.mjs';

test('redacts identifiers and account information but preserves model output', () => {
  const input = 'Probability 0.165468722464; request 12345678-abcd-4321-abcd-123456789012; user@example.test';
  const result = redact(input);
  assert.match(result, /0.165468722464/);
  assert.doesNotMatch(result, /12345678|user@example/);
});
test('rejects credential-bearing origins and unapproved destinations', () => {
  assert.throws(() => validateOrigin('https://user:password@example.test'));
  assert.throws(() => validateOrigin('https://example.test'));
  assert.throws(() => validateOrigin('http://frontend.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io'));
});
test('only the approved public origin is accepted', () => {
  assert.equal(validateOrigin('https://frontend.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io/'), 'https://frontend.whiteflower-9d03c62c.southeastasia.azurecontainerapps.io');
});
test('token and private-key text never survives caption sanitization', () => {
  const token = ['eyJ' + 'a'.repeat(24), 'b'.repeat(24), 'c'.repeat(24)].join('.');
  assert.doesNotMatch(redact(token), /eyJ/);
  assert.doesNotMatch(redact('-----BEGIN PRIVATE KEY-----'), /BEGIN/);
});

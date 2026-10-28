const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { readFromDir, readFromStdin, writeSnapshot, verify, list } = require('./memory-snapshot.js');

function tmp() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'memsnap-'));
}

test('writeSnapshot scrie MEMORY.md, topics/ si MANIFEST.md', () => {
  const out = tmp();
  const res = writeSnapshot({
    memory: '# MEMORY\n\n- ceva\n',
    topics: { 'topic-a.md': '# A\n', 'topic-b.md': '# B\n' },
    label: 'test-snapshot',
    source: 'test',
    outRoot: out,
  });
  assert.ok(fs.existsSync(path.join(res.dir, 'MEMORY.md')));
  assert.ok(fs.existsSync(path.join(res.dir, 'topics', 'topic-a.md')));
  assert.ok(fs.existsSync(path.join(res.dir, 'topics', 'topic-b.md')));
  const manifest = fs.readFileSync(path.join(res.dir, 'MANIFEST.md'), 'utf8');
  assert.match(manifest, /test-snapshot/);
  assert.match(manifest, /MEMORY\.md/);
  assert.match(manifest, /topics\/topic-a\.md/);
});

test('arhiva e append-only: a doua scriere cu aceeasi eticheta arunca', () => {
  const out = tmp();
  const args = { memory: 'x', topics: {}, label: 'dublu', source: 'test', outRoot: out };
  writeSnapshot(args);
  assert.throws(() => writeSnapshot(args), /EXISTĂ deja/);
});

test('verify intoarce ok doar daca exista MEMORY.md si MANIFEST.md', () => {
  const out = tmp();
  assert.equal(verify('nimic', out).ok, false);
  writeSnapshot({ memory: 'x', topics: {}, label: 'ok-label', source: 't', outRoot: out });
  assert.equal(verify('ok-label', out).ok, true);
  // arhiva incompleta (fara MANIFEST) => nu ok
  const dirs = fs.readdirSync(out);
  fs.rmSync(path.join(out, dirs[0], 'MANIFEST.md'));
  assert.equal(verify('ok-label', out).ok, false);
});

test('readFromDir citeste MEMORY.md si topicurile', () => {
  const src = tmp();
  fs.writeFileSync(path.join(src, 'MEMORY.md'), 'memorie', 'utf8');
  fs.mkdirSync(path.join(src, 'topics'));
  fs.writeFileSync(path.join(src, 'topics', 'x.md'), 'topic', 'utf8');
  const r = readFromDir(src);
  assert.equal(r.memory, 'memorie');
  assert.equal(r.topics['x.md'], 'topic');
});

test('readFromDir arunca daca lipseste MEMORY.md', () => {
  const src = tmp();
  assert.throws(() => readFromDir(src), /LIPSA/);
});

test('readFromStdin accepta { MEMORY.md, topics }', () => {
  const r = readFromStdin(JSON.stringify({ 'MEMORY.md': 'mem', topics: { 't.md': 'x' } }));
  assert.equal(r.memory, 'mem');
  assert.equal(r.topics['t.md'], 'x');
});

test('readFromStdin arunca pe JSON invalid sau fara MEMORY.md', () => {
  assert.throws(() => readFromStdin('nu json'), /nu e JSON valid/);
  assert.throws(() => readFromStdin(JSON.stringify({ topics: {} })), /nu conține/);
});

test('list intoarce directoarele de arhiva', () => {
  const out = tmp();
  writeSnapshot({ memory: 'x', topics: {}, label: 'a', source: 't', outRoot: out });
  writeSnapshot({ memory: 'y', topics: {}, label: 'b', source: 't', outRoot: out });
  assert.equal(list(out).length, 2);
});

test('nume de topic cu path traversal sunt blocate', () => {
  const out = tmp();
  const res = writeSnapshot({
    memory: 'x', topics: { '../../evitat.md': 'malicious' },
    label: 'traversal', source: 't', outRoot: out,
  });
  assert.ok(fs.existsSync(path.join(res.dir, 'topics', 'evitat.md')));
  assert.ok(!fs.existsSync(path.join(out, 'evitat.md')));
});

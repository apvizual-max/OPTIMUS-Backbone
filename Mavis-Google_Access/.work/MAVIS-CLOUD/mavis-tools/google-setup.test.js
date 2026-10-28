const assert = require('node:assert/strict');
const { describe, it, mock } = require('node:test');

// We need to mock AUTH before requiring google-setup.js
const AUTH = require('./google-auth.js');
const { credsFromDisk } = require('./google-setup.js');

describe('credsFromDisk', () => {
    it('returns null if AUTH.readJson returns null', () => {
        mock.method(AUTH, 'readJson', () => null);
        const result = credsFromDisk();
        assert.equal(result, null);
    });

    it('returns installed (desktop) credentials', () => {
        mock.method(AUTH, 'readJson', () => ({
            installed: { client_id: 'id1', client_secret: 'sec1' }
        }));
        const result = credsFromDisk();
        assert.deepEqual(result, {
            client_id: 'id1',
            client_secret: 'sec1',
            kind: 'installed (desktop)'
        });
    });

    it('returns web credentials', () => {
        mock.method(AUTH, 'readJson', () => ({
            web: { client_id: 'id2', client_secret: 'sec2' }
        }));
        const result = credsFromDisk();
        assert.deepEqual(result, {
            client_id: 'id2',
            client_secret: 'sec2',
            kind: 'web'
        });
    });

    it('returns raw credentials', () => {
        mock.method(AUTH, 'readJson', () => ({
            client_id: 'id3', client_secret: 'sec3'
        }));
        const result = credsFromDisk();
        assert.deepEqual(result, {
            client_id: 'id3',
            client_secret: 'sec3',
            kind: 'raw'
        });
    });

    it('returns null if client_id is missing', () => {
        mock.method(AUTH, 'readJson', () => ({
            client_secret: 'sec'
        }));
        const result = credsFromDisk();
        assert.equal(result, null);
    });

    it('returns null if client_secret is missing', () => {
        mock.method(AUTH, 'readJson', () => ({
            client_id: 'id'
        }));
        const result = credsFromDisk();
        assert.equal(result, null);
    });
});

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const html = read('index.html');
const i18nPipelineReadme = read(path.join('tools', 'README.i18n-content.md'));

function apiBaseUrlFor(hostname) {
    const bootstrap = html.match(
        /function getApiBaseUrl\([\s\S]*?const API_BASE_URL = getApiBaseUrl\(\);/,
    );
    assert.ok(bootstrap, 'Missing API base URL bootstrap');
    const context = vm.createContext({ window: { location: { hostname } } });
    vm.runInContext(bootstrap[0], context);
    return vm.runInContext('API_BASE_URL', context);
}

test('frontend selects the matching API while preserving legacy fallbacks', () => {
    assert.equal(apiBaseUrlFor('192.168.0.103'), '/api');
    assert.equal(apiBaseUrlFor('enplay.aoke.ltd'), 'https://api-enplay.aoke.ltd');
    assert.equal(apiBaseUrlFor('enplay.ningboaoke.com'), 'https://api-enplay.ningboaoke.com');
    assert.equal(apiBaseUrlFor('cet4-words-study.pages.dev'), 'https://api-enplay.ningboaoke.com');
});

test('CSP permits both API domains for data and recorded audio', () => {
    const headers = read('_headers');
    for (const directive of ['connect-src', 'media-src']) {
        assert.match(
            headers,
            new RegExp(`${directive}[^;]*https://api-enplay\\.aoke\\.ltd[^;]*https://api-enplay\\.ningboaoke\\.com`),
        );
    }
});

test('backend defaults and compose deployment accept both domain generations', () => {
    const compose = read('docker-compose.yml');
    const api = read(path.join('api', 'app', 'main.py'));

    for (const origin of ['https://enplay.aoke.ltd', 'https://enplay.ningboaoke.com']) {
        assert.ok(compose.includes(origin), `Compose is missing origin ${origin}`);
        assert.ok(api.includes(origin), `API defaults are missing origin ${origin}`);
    }
    for (const host of ['api-enplay.aoke.ltd', 'api-enplay.ningboaoke.com']) {
        assert.ok(compose.includes(host), `Compose is missing host ${host}`);
        assert.ok(api.includes(host), `API defaults are missing host ${host}`);
    }
});

test('i18n publishing documentation targets the production API host', () => {
    assert.ok(i18nPipelineReadme.includes('--api-base https://api-enplay.aoke.ltd'));
    assert.ok(!i18nPipelineReadme.includes('--api-base https://enplay.aoke.ltd/api'));
    assert.ok(
        i18nPipelineReadme.includes(
            '--api-base http://192.168.0.103/api --allow-http',
        ),
    );
});

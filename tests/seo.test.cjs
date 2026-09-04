const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const root = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');

test('production page exposes canonical search and social metadata', () => {
    const html = read('index.html');
    assert.match(html, /<link rel="canonical" href="https:\/\/enplay\.aoke\.ltd\/">/);
    assert.match(html, /<meta name="description" content="[^"]+">/);
    assert.match(html, /<meta property="og:title" content="[^"]+">/);
    assert.match(html, /<meta name="twitter:card" content="summary">/);
    assert.match(html, /"@type": \["WebApplication", "LearningResource"\]/);
    assert.match(html, /"@type": "FAQPage"/);
});

test('crawler and answer-engine discovery files target the production domain', () => {
    assert.match(read('robots.txt'), /Sitemap: https:\/\/enplay\.aoke\.ltd\/sitemap\.xml/);
    assert.match(read('sitemap.xml'), /<loc>https:\/\/enplay\.aoke\.ltd\/<\/loc>/);
    assert.match(read('llms.txt'), /# Enplay/);
    const manifest = JSON.parse(read('site.webmanifest'));
    assert.equal(manifest.name, 'Enplay Language Study');
    assert.equal(manifest.start_url, '/#words');
});

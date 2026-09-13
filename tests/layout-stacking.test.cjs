const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

function zIndex(selector) {
    const escaped = selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const match = html.match(new RegExp(`${escaped}\\s*\\{[^}]*?z-index:\\s*(\\d+)`, 's'));
    assert.ok(match, `Missing z-index for ${selector}`);
    return Number(match[1]);
}

test('the language menu stacking context stays above the floating notebook', () => {
    assert.ok(zIndex('.app-header') > zIndex('.vocabulary-notebook-widget'));
    assert.ok(zIndex('.modal') > zIndex('.app-header'));
});

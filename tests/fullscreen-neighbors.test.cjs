const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
function source(name) {
    const start = html.indexOf(`        function ${name}(`);
    assert.ok(start >= 0, `Missing function ${name}`);
    return html.slice(start, html.indexOf('\n        }', start) + 10);
}
function fixture(overrides = {}) {
    const context = vm.createContext({
        notebookDisplayedEntry: null, notebookPlaybackQueue: [], notebookPlaybackIndex: 0,
        cet4Words: [{ word: 'alpha' }, { word: 'beta' }, { word: 'gamma' }],
        order: [2, 0, 1], orderPosition: 1, isNewWordsOnly: false,
        phraseList: [{ text: 'First', scene: 'a', idx: 0 }, { text: 'Second', scene: 'a', idx: 1 }, { text: 'Third', scene: 'a', idx: 2 }],
        phraseIndex: 1,
        getTodayLearnedSet: () => new Set([1]),
        getAllLearnedPhraseSet: () => new Set(['a:2']),
        getPhraseKey: (scene, idx) => `${scene}:${idx}`,
        ...overrides,
    });
    ['findPreviousPosition', 'findNextPosition', 'findPrevPhraseIndex', 'findNextPhraseIndex', 'getFullscreenNeighbors', 'updateFullscreenNeighbors']
        .forEach(name => vm.runInContext(source(name), context));
    return context;
}
const names = (context, type) => Array.from(context.getFullscreenNeighbors(type), item => item?.word || item?.text || null);

test('all inline JavaScript parses and UTF-8 has no replacement characters', () => {
    assert.ok(!html.includes('\uFFFD'));
    for (const match of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)) {
        new vm.Script(match[1]);
    }
});
test('word previews follow shuffled playback order and learned filter', () => {
    assert.deepEqual(names(fixture(), 'word'), ['gamma', 'beta']);
    assert.deepEqual(names(fixture({ isNewWordsOnly: true }), 'word'), ['gamma', null]);
});
test('review order and list boundaries do not leak original dictionary entries', () => {
    assert.deepEqual(names(fixture({ order: [2, 0], orderPosition: 0 }), 'word'), [null, 'alpha']);
    assert.deepEqual(names(fixture({ order: [2], orderPosition: 0 }), 'word'), [null, null]);
});
test('sentence previews follow the same learned filter as navigation', () => {
    assert.deepEqual(names(fixture(), 'sentence'), ['First', 'Third']);
    assert.deepEqual(names(fixture({ isNewWordsOnly: true }), 'sentence'), ['First', null]);
    assert.deepEqual(names(fixture({ phraseList: [], phraseIndex: 0 }), 'sentence'), [null, null]);
});
test('notebook previews stay inside their saved queue even when paused', () => {
    for (const type of ['word', 'sentence']) {
        const queue = [{ word: 'Saved A', text: 'Saved A' }, { word: 'Saved B', text: 'Saved B' }];
        const context = fixture({ notebookDisplayedEntry: { type }, notebookPlaybackQueue: queue, notebookPlaybackIndex: 0 });
        assert.deepEqual(names(context, type), [null, 'Saved B']);
        context.notebookPlaybackIndex = 1;
        assert.deepEqual(names(context, type), ['Saved A', null]);
    }
});
test('preview renderer disables boundaries and inserts untrusted content as text', () => {
    const elements = {};
    const document = { getElementById(id) {
        return elements[id] ||= { parts: {}, attributes: {}, querySelector(selector) { return this.parts[selector] ||= {}; }, setAttribute(key, value) { this.attributes[key] = value; } };
    } };
    const context = fixture({ document, order: [0, 1], orderPosition: 0, cet4Words: [{ word: 'first' }, { word: '<img src=x onerror=alert(1)>' }] });
    context.updateFullscreenNeighbors('word');
    assert.equal(elements.wordPreviousPreview.disabled, true);
    assert.equal(elements.wordPreviousPreview.parts['.neighbor-label'].textContent, '已到开头');
    assert.equal(elements.wordNextPreview.parts['.neighbor-text'].textContent, '<img src=x onerror=alert(1)>');
    assert.equal(elements.wordNextPreview.innerHTML, undefined);
});

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { webcrypto } = require('node:crypto');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
function source(name) {
    const functionMarker = `        function ${name}(`;
    const asyncFunctionMarker = `        async function ${name}(`;
    const start = Math.max(html.indexOf(functionMarker), html.indexOf(asyncFunctionMarker));
    assert.ok(start >= 0, `Missing function ${name}`);
    return html.slice(start, html.indexOf('\n        }', start) + 10);
}
function fixture(overrides = {}) {
    const translations = {
        'fullscreen.previousWord': '上一個單詞',
        'fullscreen.nextWord': '下一個單詞',
        'fullscreen.previousSentence': '上一句',
        'fullscreen.nextSentence': '下一句',
        'fullscreen.start': '已到開頭',
        'fullscreen.end': '已到末尾',
    };
    const context = vm.createContext({
        notebookDisplayedEntry: null, notebookPlaybackQueue: [], notebookPlaybackIndex: 0,
        cet4Words: [{ word: 'alpha' }, { word: 'beta' }, { word: 'gamma' }],
        order: [2, 0, 1], orderPosition: 1, isNewWordsOnly: false,
        phraseList: [{ text: 'First', scene: 'a', idx: 0 }, { text: 'Second', scene: 'a', idx: 1 }, { text: 'Third', scene: 'a', idx: 2 }],
        phraseIndex: 1,
        getTodayLearnedSet: () => new Set([1]),
        getAllLearnedPhraseSet: () => new Set(['a:2']),
        getPhraseKey: (scene, idx) => `${scene}:${idx}`,
        t: key => translations[key] || key,
        ...overrides,
    });
    ['findPreviousPosition', 'findNextPosition', 'findPrevPhraseIndex', 'findNextPhraseIndex', 'getFullscreenNeighbors', 'updateFullscreenNeighbors']
        .forEach(name => vm.runInContext(source(name), context));
    return context;
}
const names = (context, type) => Array.from(context.getFullscreenNeighbors(type), item => item?.word || item?.text || null);

test('all inline JavaScript parses and UTF-8 has no replacement characters', () => {
    assert.ok(!html.includes('\uFFFD'));
    for (const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
        const type = match[1].match(/\btype=["']([^"']+)["']/i)?.[1];
        if (type && !['text/javascript', 'application/javascript', 'module'].includes(type)) continue;
        new vm.Script(match[2]);
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
    assert.equal(elements.wordPreviousPreview.parts['.neighbor-label'].textContent, '已到開頭');
    assert.equal(elements.wordNextPreview.parts['.neighbor-text'].textContent, '<img src=x onerror=alert(1)>');
    assert.equal(elements.wordNextPreview.innerHTML, undefined);
});

test('recorded sentence URLs are warmed per voice before playback', async () => {
    const context = vm.createContext({
        API_BASE_URL: 'https://audio.example.test',
        AUDIO_LIBRARY_VERSION: 'test-version',
        TextEncoder,
        crypto: webcrypto,
        recordedAudioHashCache: new Map(),
        recordedAudioUrlCache: new Map(),
    });
    ['getRecordedAudioCacheKey', 'getCachedRecordedAudioUrl', 'warmRecordedAudioUrl', 'getRecordedAudioUrl']
        .forEach(name => vm.runInContext(source(name), context));

    const text = 'A sentence ready to play.';
    context.warmRecordedAudioUrl(text, 'af_heart');
    await context.getRecordedAudioUrl(text, 'af_heart');

    const femaleUrl = context.getCachedRecordedAudioUrl(text, 'af_heart');
    assert.match(femaleUrl, /\/audio\/v1\/af_heart\//);
    assert.equal(context.getCachedRecordedAudioUrl(text, 'am_michael'), '');

    await context.getRecordedAudioUrl(text, 'am_michael');
    assert.match(context.getCachedRecordedAudioUrl(text, 'am_michael'), /\/audio\/v1\/am_michael\//);
});

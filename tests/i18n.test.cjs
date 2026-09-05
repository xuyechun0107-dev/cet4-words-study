const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const source = fs.readFileSync(path.join(root, 'i18n.js'), 'utf8');

function createContext(storedLocale = null, storedInterfaceLanguage = null) {
    const storage = new Map();
    if (storedLocale) storage.set('enplay_locale_v1', storedLocale);
    if (storedInterfaceLanguage) storage.set('enplay_interface_language_v1', storedInterfaceLanguage);
    const events = [];
    const document = {
        documentElement: { lang: '', dir: '' },
        readyState: 'complete',
        querySelectorAll: () => [],
    };
    const window = {
        localStorage: {
            getItem: key => storage.get(key) ?? null,
            setItem: (key, value) => storage.set(key, String(value)),
        },
        dispatchEvent: event => events.push(event),
    };
    class CustomEvent {
        constructor(type, init = {}) {
            this.type = type;
            this.detail = init.detail;
        }
    }
    const context = vm.createContext({ window, document, CustomEvent, Intl, Date, console });
    vm.runInContext(source, context, { filename: 'i18n.js' });
    return { api: window.EnplayI18n, document, storage, events };
}

function collectUsedKeys() {
    const keys = new Set();
    for (const match of html.matchAll(/data-i18n(?:-[a-z-]+)?="([A-Za-z0-9_.-]+)"/g)) keys.add(match[1]);
    for (const match of html.matchAll(/\bt\('([A-Za-z0-9_.-]+)'/g)) keys.add(match[1]);
    for (const match of html.matchAll(/setLabel\([^,]+,\s*'([A-Za-z0-9_.-]+)'\)/g)) keys.add(match[1]);
    for (const match of html.matchAll(/['"]((?:language|interface|common|nav|online|player|content|articleEmpty|article|shelf|notebook|history|import|fullscreen|errors|categories|document)\.[A-Za-z0-9_.-]+)['"]/g)) keys.add(match[1]);
    return [...keys].sort();
}

test('translation bundle exposes all requested locales with identical key coverage', () => {
    const { api } = createContext();
    const expectedLocales = ['zh-Hant', 'ja', 'ko', 'fr', 'es', 'pt', 'ru', 'th', 'ar'];
    assert.deepEqual(Object.keys(api.locales), expectedLocales);

    const baseline = Object.keys(api.locales['zh-Hant'].messages).sort();
    assert.ok(baseline.length >= 200);
    for (const locale of expectedLocales) {
        assert.deepEqual(Object.keys(api.locales[locale].messages).sort(), baseline, `${locale} key coverage differs`);
        assert.ok(!Object.values(api.locales[locale].messages).some(value => String(value).includes('\uFFFD')));
    }
});

test('all directly referenced interface keys resolve in every locale', () => {
    const { api } = createContext();
    const usedKeys = collectUsedKeys();
    assert.ok(usedKeys.length >= 120);

    for (const locale of Object.keys(api.locales)) {
        api.setLocale(locale, { persist: false });
        for (const key of usedKeys) {
            assert.notEqual(api.t(key), key, `${locale} is missing ${key}`);
        }
    }

    api.setInterfaceLanguage('en', { persist: false });
    for (const key of usedKeys) {
        const value = api.t(key);
        assert.notEqual(value, key, `English interface is missing ${key}`);
        assert.doesNotMatch(value, /[\u3400-\u9fff\u3040-\u30ff\uac00-\ud7af]/u, `English interface falls back for ${key}`);
    }
});

test('locale preference persists and Arabic alone enables RTL', () => {
    const state = createContext();
    assert.equal(state.api.getLocale(), 'zh-Hant');
    assert.equal(state.document.documentElement.lang, 'zh-Hant');
    assert.equal(state.document.documentElement.dir, 'ltr');

    state.api.setLocale('ar');
    assert.equal(state.storage.get('enplay_locale_v1'), 'ar');
    assert.equal(state.document.documentElement.lang, 'ar');
    assert.equal(state.document.documentElement.dir, 'rtl');
    assert.equal(state.events.at(-1).type, 'enplay:localechange');

    state.api.setLocale('ja');
    assert.equal(state.document.documentElement.dir, 'ltr');
});

test('invalid stored locales safely fall back to Traditional Chinese', () => {
    const { api, document } = createContext('unsupported-locale');
    assert.equal(api.getLocale(), 'zh-Hant');
    assert.equal(document.documentElement.lang, 'zh-Hant');
});

test('English interface mode is independent from the selected content locale', () => {
    const state = createContext('ja');
    assert.equal(state.api.getLocale(), 'ja');
    assert.equal(state.api.getInterfaceLanguage(), 'localized');

    state.api.setInterfaceLanguage('en');
    assert.equal(state.api.getLocale(), 'ja');
    assert.equal(state.api.getInterfaceLanguage(), 'en');
    assert.equal(state.api.t('nav.words'), 'Words');
    assert.equal(state.storage.get('enplay_interface_language_v1'), 'en');
    assert.equal(state.storage.get('enplay_locale_v1'), 'ja');
    assert.equal(state.document.documentElement.lang, 'en');
    assert.equal(state.document.documentElement.dir, 'ltr');
    assert.equal(state.events.at(-1).type, 'enplay:interfacechange');

    state.api.setLocale('ar', { persist: false });
    assert.equal(state.api.getLocale(), 'ar');
    assert.equal(state.api.t('nav.words'), 'Words');
    assert.equal(state.document.documentElement.dir, 'ltr');
});

test('English interface preference restores without becoming a content locale', () => {
    const state = createContext('fr', 'en');
    assert.equal(state.api.getLocale(), 'fr');
    assert.equal(state.api.getInterfaceLanguage(), 'en');
    assert.equal(state.api.t('shelf.localeEmpty'), 'No content is available for the selected content language yet.');
    assert.deepEqual(Object.keys(state.api.locales), ['zh-Hant', 'ja', 'ko', 'fr', 'es', 'pt', 'ru', 'th', 'ar']);
});

test('header places the English interface checkbox directly after the content language selector', () => {
    assert.match(html, /<div class="language-switcher">[\s\S]*?<\/div>\s*<label class="interface-language-toggle"[\s\S]*?id="englishInterfaceToggle"/);
    assert.doesNotMatch(html, /<nav class="workspace-nav"[\s\S]*id="englishInterfaceToggle"[\s\S]*<\/nav>/);
    assert.doesNotMatch(html, /id="englishInterfaceToggle"[^>]*data-locale/);
    assert.match(html, /enplay:interfacechange[\s\S]*refreshLocalizedInterface\(true\)/);
    assert.match(html, /if \(skipContentSynchronization !== true\) void synchronizeLocaleLibraries\(getContentLocale\(\)\)/);
});

test('runtime listens for locale changes on window and treats locales as a keyed object', () => {
    assert.match(html, /window\.addEventListener\('enplay:localechange', refreshLocalizedInterface\)/);
    assert.doesNotMatch(html, /i18n\.locales\.find\(/);
});

test('translations avoid known count and terminology traps', () => {
    const { api } = createContext();
    assert.equal(api.locales.fr.messages['shelf.count'], 'Total : {count}');
    assert.equal(api.locales.es.messages['import.success'], 'Elementos importados: {count}');
    assert.equal(api.locales.pt.messages['import.jsonError'], 'A raiz do JSON deve ser um array ou conter um array "items"');
    assert.match(api.locales.th.messages['history.confirmWords'], /วันที่เลือก/);
    assert.equal(api.locales.ar.messages['import.success'], 'العناصر المستوردة: {count}');
});

test('definition and attribution labels stay language-neutral in every locale', () => {
    const { api } = createContext();
    const forbiddenChineseLanguageLabels = /中文|中國語|中国語|중국어|chinois|chinoise|china|chinês|китай|ภาษาจีน|الصيني/u;
    for (const locale of Object.keys(api.locales)) {
        const messages = api.locales[locale].messages;
        for (const key of ['player.readChinese', 'content.chineseDefinition', 'content.noChinese']) {
            assert.ok(messages[key], `${locale} is missing ${key}`);
            assert.doesNotMatch(messages[key].toLocaleLowerCase(), forbiddenChineseLanguageLabels, `${locale} ${key} is not neutral`);
        }
        assert.ok(messages['shelf.sourceLabel'], `${locale} is missing the visible source label`);
        assert.ok(messages['shelf.licenseLabel'], `${locale} is missing the visible license label`);
    }
});

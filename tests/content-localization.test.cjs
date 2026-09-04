const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

function functionSource(name) {
    const markers = [`function ${name}(`, `async function ${name}(`];
    const starts = markers.map(marker => html.indexOf(marker)).filter(index => index >= 0);
    const start = Math.min(...starts);
    assert.ok(start >= 0, `Missing function ${name}`);
    const brace = html.indexOf('{', start);
    let depth = 0;
    let quote = '';
    let escaped = false;
    let lineComment = false;
    let blockComment = false;
    for (let index = brace; index < html.length; index++) {
        const char = html[index];
        const next = html[index + 1];
        if (lineComment) {
            if (char === '\n') lineComment = false;
            continue;
        }
        if (blockComment) {
            if (char === '*' && next === '/') {
                blockComment = false;
                index++;
            }
            continue;
        }
        if (quote) {
            if (escaped) escaped = false;
            else if (char === '\\') escaped = true;
            else if (char === quote) quote = '';
            continue;
        }
        if (char === '/' && next === '/') {
            lineComment = true;
            index++;
            continue;
        }
        if (char === '/' && next === '*') {
            blockComment = true;
            index++;
            continue;
        }
        if (char === '"' || char === "'" || char === '`') {
            quote = char;
            continue;
        }
        if (char === '{') depth++;
        if (char === '}' && --depth === 0) return html.slice(start, index + 1);
    }
    throw new Error(`Unterminated function ${name}`);
}

function runFunctions(context, names) {
    const sandbox = vm.createContext(context);
    for (const name of names) vm.runInContext(functionSource(name), sandbox);
    return sandbox;
}

test('stable datasets and item keys cover every built-in content family', () => {
    const context = runFunctions({}, [
        'normalizeContentLookupKey',
        'getLibraryContentDataset',
        'getContentDatasetFromSourceId',
        'getContentItemKey',
    ]);
    assert.equal(context.getLibraryContentDataset('words', { id: 'builtin-words' }), 'words-cet4');
    assert.equal(context.getLibraryContentDataset('words', { id: 'remote-ecdict-cet6', slug: 'ecdict-cet6' }), 'wordbook-ecdict-cet6');
    assert.equal(context.getLibraryContentDataset('sentences', { id: 'builtin-sentences' }), 'sentences-daily');
    assert.equal(context.getLibraryContentDataset('sentences', { id: 'builtin-sentences-tatoeba-basic' }), 'sentences-tatoeba-basic');
    assert.equal(context.getLibraryContentDataset('sentences', { id: 'builtin-sentences-tatoeba-intermediate' }), 'sentences-tatoeba-intermediate');
    const articleDatasets = {
        'builtin-articles': 'articles-graded',
        'builtin-articles-junior-basic': 'articles-graded-junior-basic',
        'builtin-articles-junior-advanced': 'articles-graded-junior-advanced',
        'builtin-articles-senior-basic': 'articles-graded-senior-basic',
        'builtin-articles-senior-advanced': 'articles-graded-senior-advanced',
    };
    for (const [sourceLibraryId, dataset] of Object.entries(articleDatasets)) {
        assert.equal(context.getLibraryContentDataset('articles', { id: sourceLibraryId }), dataset);
        assert.equal(context.getContentDatasetFromSourceId('articles', sourceLibraryId), dataset);
    }
    assert.equal(context.getContentItemKey('words', { word: '  Abandon  ' }), 'abandon');
    assert.equal(context.getContentItemKey('sentences', { text: '  How   are you? ' }), 'how are you?');
    assert.equal(context.getContentItemKey('sentences', { text: 'ignored', sourceIds: [3101536, 2] }), '3101536');
    assert.equal(context.getContentItemKey('articles', { id: 'junior-basic-library-card' }), 'junior-basic-library-card');
});

test('five localized article shelves resolve their own catalog library and bundle', () => {
    const articleDatasets = {
        'builtin-articles': 'articles-graded',
        'builtin-articles-junior-basic': 'articles-graded-junior-basic',
        'builtin-articles-junior-advanced': 'articles-graded-junior-advanced',
        'builtin-articles-senior-basic': 'articles-graded-senior-basic',
        'builtin-articles-senior-advanced': 'articles-graded-senior-advanced',
    };
    const libraries = Object.entries(articleDatasets).map(([sourceLibraryId, dataset]) => ({
        id: `fr:${dataset}`,
        type: 'articles',
        dataset,
        sourceLibraryId,
        contentVersion: `version-${dataset}`,
        localized: true,
    }));
    const contentBundleCache = new Map();
    for (const library of libraries) {
        const itemKey = `${library.dataset}-item`;
        contentBundleCache.set(`${library.dataset}::fr::${library.contentVersion}`, {
            contentVersion: library.contentVersion,
            items: {},
            content: [{
                libraryId: library.id,
                itemKey,
                position: 0,
                payload: { id: itemKey, titleLocalized: library.dataset },
            }],
        });
    }
    const context = runFunctions({
        CONTENT_FALLBACK_LOCALE: 'zh-Hans',
        localizedCatalogCache: new Map([['fr', libraries]]),
        contentBundleCache,
        getContentLocale: () => 'fr',
    }, [
        'getContentDatasetFromSourceId',
        'getCatalogLibraryForContent',
        'getContentBundleCacheKey',
        'getContentItemKey',
        'getContentBundleItem',
    ]);

    for (const [sourceLibraryId, dataset] of Object.entries(articleDatasets)) {
        const library = context.getCatalogLibraryForContent(
            dataset,
            'articles',
            'fr',
            sourceLibraryId,
        );
        assert.equal(library.sourceLibraryId, sourceLibraryId);
        assert.equal(context.getContentDatasetFromSourceId('articles', sourceLibraryId), dataset);
        const itemKey = `${dataset}-item`;
        assert.equal(
            context.getContentBundleItem(dataset, itemKey, 'fr', library).titleLocalized,
            dataset,
        );
    }
});

test('materialized records retain the stable itemKey supplied by the bundle wrapper', () => {
    const context = runFunctions({}, ['getLocalizedBundleRecords']);
    const records = context.getLocalizedBundleRecords({
        content: [{
            libraryId: 'fr:sentences-daily',
            itemKey: 'daily:dining:42',
            position: 42,
            payload: { text: 'This tastes delicious!', translationLocalized: 'C’est délicieux !' },
        }],
    }, {
        id: 'fr:sentences-daily',
        sourceLibraryId: 'builtin-sentences',
    });
    assert.equal(records[0].contentKey, 'daily:dining:42');
});

test('bundle loader requests and caches the exact catalog content version', async () => {
    const calls = [];
    const context = runFunctions({
        CONTENT_FALLBACK_LOCALE: 'zh-Hans',
        CONTENT_BUNDLE_SCHEMA_VERSION: 1,
        API_BASE_URL: 'https://api.example.test',
        contentBundleCache: new Map(),
        contentBundleRequests: new Map(),
        getContentLocale: () => 'ja',
        presenceFetch: async url => {
            calls.push(url);
            const version = new URL(url).searchParams.get('v');
            return {
                ok: true,
                status: 200,
                json: async () => ({
                    schemaVersion: 1,
                    dataset: 'words-cet4',
                    locale: 'ja',
                    contentVersion: version,
                    content: [{ libraryId: 'ja:words-cet4', position: 0, payload: { word: 'abandon' } }],
                }),
            };
        },
        console: { warn() {} },
    }, ['getContentBundleCacheKey', 'normalizeContentBundle', 'loadContentBundle']);

    const first = await context.loadContentBundle('words-cet4', 'ja', '2026.09.04-1');
    const second = await context.loadContentBundle('words-cet4', 'ja', '2026.09.04-1');
    const nextVersion = await context.loadContentBundle('words-cet4', 'ja', '2026.09.04-2');
    assert.equal(calls.length, 2);
    assert.equal(calls[0], 'https://api.example.test/v1/i18n/bundles/words-cet4/ja?v=2026.09.04-1');
    assert.equal(calls[1], 'https://api.example.test/v1/i18n/bundles/words-cet4/ja?v=2026.09.04-2');
    assert.equal(first.content.length, 1);
    assert.equal(second, first);
    assert.notEqual(nextVersion, first);
    assert.equal(nextVersion.contentVersion, '2026.09.04-2');
});

test('bundle loader and materializer reject missing or stale content versions', async () => {
    const cache = new Map();
    const catalogCache = new Map([['fr', [{ id: 'fr:words-cet4', locale: 'fr' }]]]);
    const context = runFunctions({
        CONTENT_FALLBACK_LOCALE: 'zh-Hans',
        CONTENT_BUNDLE_SCHEMA_VERSION: 1,
        API_BASE_URL: 'https://api.example.test',
        contentBundleCache: cache,
        contentBundleRequests: new Map(),
        localizedCatalogCache: catalogCache,
        localizedCatalogFetchedAt: new Map([['fr', 1]]),
        localizedLibraryCache: new Map([['fr:another::old-version', { locale: 'fr' }]]),
        getContentLocale: () => 'fr',
        presenceFetch: async () => ({
            ok: true,
            status: 200,
            json: async () => ({
                schemaVersion: 1,
                dataset: 'words-cet4',
                locale: 'fr',
                contentVersion: 'old-version',
                content: [{ payload: { word: 'abandon' } }],
            }),
        }),
        console: { warn() {} },
    }, ['getContentBundleCacheKey', 'normalizeContentBundle', 'invalidateLocaleCatalog', 'loadContentBundle']);

    const stale = await context.loadContentBundle('words-cet4', 'fr', 'new-version');
    assert.equal(stale.notFound, true);
    assert.equal(stale.versionMismatch, true);
    assert.equal(stale.requestedContentVersion, 'new-version');
    assert.equal(cache.size, 0);
    assert.equal(catalogCache.has('fr'), false);
    const materializer = functionSource('materializeLocalizedLibrary');
    assert.ok(
        materializer.indexOf('if (!library.contentVersion) throw')
            < materializer.indexOf('localizedLibraryCache.has(cacheKey)'),
        'the catalog version must be required before reading the materialized cache',
    );
    assert.match(materializer, /loadContentBundle\(library\.dataset, library\.locale, library\.contentVersion\)/);
    assert.match(materializer, /bundle\.contentVersion !== library\.contentVersion/);
});

test('a stale catalog version is force-refreshed and materialized exactly once after bundle 404', async () => {
    const calls = [];
    const oldLibrary = {
        id: 'fr:words-cet4',
        type: 'words',
        dataset: 'words-cet4',
        sourceLibraryId: 'builtin-words',
        name: 'Français CET-4',
        locale: 'fr',
        localized: true,
        contentVersion: 'v1',
    };
    const localizedLibraryCache = new Map([
        ['fr:sentences::v1', { id: 'fr:sentences', locale: 'fr', contentVersion: 'v1' }],
    ]);
    const context = runFunctions({
        CONTENT_FALLBACK_LOCALE: 'zh-Hans',
        CONTENT_BUNDLE_SCHEMA_VERSION: 1,
        API_BASE_URL: 'https://api.example.test',
        LOCALE_CATALOG_TTL_MS: 300000,
        contentBundleCache: new Map(),
        contentBundleRequests: new Map(),
        localizedCatalogCache: new Map([['fr', [oldLibrary]]]),
        localizedCatalogRequests: new Map(),
        localizedCatalogFetchedAt: new Map([['fr', Date.now()]]),
        localizedLibraryCache,
        getContentLocale: () => 'fr',
        getLocalizedBundleRecords: bundle => bundle.content.map(entry => entry.payload),
        normalizeLocalizedLibraryItems: (records, type, locale) => records.map(item => ({ ...item, contentLocale: locale })),
        presenceFetch: async (url, options) => {
            calls.push({ url, options });
            if (url.includes('/bundles/') && url.includes('v=v1')) {
                return { ok: false, status: 404, json: async () => ({}) };
            }
            if (url.includes('/catalog/')) {
                return {
                    ok: true,
                    status: 200,
                    json: async () => ({
                        locale: 'fr',
                        libraries: [{
                            ...oldLibrary,
                            contentVersion: 'v2',
                        }],
                    }),
                };
            }
            return {
                ok: true,
                status: 200,
                json: async () => ({
                    schemaVersion: 1,
                    dataset: 'words-cet4',
                    locale: 'fr',
                    contentVersion: 'v2',
                    content: [{
                        libraryId: 'fr:words-cet4',
                        itemKey: 'abandon',
                        position: 0,
                        payload: { word: 'abandon', definitionLocalized: 'abandonner' },
                    }],
                }),
            };
        },
        console: { warn() {} },
    }, [
        'getContentBundleCacheKey',
        'normalizeContentBundle',
        'normalizeLocaleCatalog',
        'isLocaleCatalogFresh',
        'invalidateLocaleCatalog',
        'loadContentBundle',
        'loadLocaleCatalog',
        'materializeLocalizedLibrary',
    ]);

    const materialized = await context.materializeLocalizedLibrary(oldLibrary);
    assert.equal(materialized.contentVersion, 'v2');
    assert.equal(materialized.items[0].definitionLocalized, 'abandonner');
    assert.deepEqual(
        calls.filter(call => call.url.includes('/bundles/')).map(call => new URL(call.url).searchParams.get('v')),
        ['v1', 'v2'],
    );
    const catalogCall = calls.find(call => call.url.includes('/catalog/'));
    assert.ok(catalogCall.url.includes('?refresh='));
    assert.equal(catalogCall.options.cache, 'no-store');
    assert.equal(localizedLibraryCache.has('fr:sentences::v1'), false);
});

test('locale catalog is independent and never falls back to the Chinese shelf', async () => {
    const calls = [];
    const context = runFunctions({
        CONTENT_FALLBACK_LOCALE: 'zh-Hans',
        API_BASE_URL: 'https://api.example.test',
        localizedCatalogCache: new Map(),
        localizedCatalogRequests: new Map(),
        localizedCatalogFetchedAt: new Map(),
        localizedLibraryCache: new Map(),
        LOCALE_CATALOG_TTL_MS: 300000,
        getContentLocale: () => 'ja',
        getBuiltInLibraries: () => [{ id: 'builtin-words', type: 'words' }],
        remoteWordbooks: [{ id: 'remote-ecdict-cet6', type: 'words' }],
        customLibraries: [{ id: 'local-words', type: 'words' }],
        presenceFetch: async url => {
            calls.push(url);
            return {
                ok: true,
                status: 200,
                json: async () => ({
                    locale: 'ja',
                    libraries: [{
                        id: 'ja:words-cet4', type: 'words', dataset: 'words-cet4',
                        sourceLibraryId: 'builtin-words', name: '日本語 CET-4', itemCount: 4123,
                        contentVersion: '2026.09.04-1',
                    }],
                }),
            };
        },
        console: { warn() {} },
    }, ['normalizeLocaleCatalog', 'isLocaleCatalogFresh', 'invalidateLocaleCatalog', 'loadLocaleCatalog', 'getAvailableLibraries']);

    assert.deepEqual(Array.from(context.getAvailableLibraries('words', 'ja')), []);
    await context.loadLocaleCatalog('ja');
    assert.deepEqual(Array.from(context.getAvailableLibraries('words', 'ja'), item => item.id), ['ja:words-cet4']);
    assert.equal(calls[0], 'https://api.example.test/v1/i18n/catalog/ja');
    assert.deepEqual(
        Array.from(context.getAvailableLibraries('words', 'zh-Hant'), item => item.id),
        ['builtin-words', 'remote-ecdict-cet6', 'local-words'],
    );
});

test('Traditional Chinese prefers a complete localized catalog and falls back only when it is empty', async () => {
    let libraries = [];
    const catalogCache = new Map();
    const bundleCache = new Map();
    const context = runFunctions({
        CONTENT_FALLBACK_LOCALE: 'zh-Hans',
        API_BASE_URL: 'https://api.example.test',
        LOCALE_CATALOG_TTL_MS: 300000,
        localizedCatalogCache: catalogCache,
        localizedCatalogRequests: new Map(),
        localizedCatalogFetchedAt: new Map(),
        localizedLibraryCache: new Map(),
        contentBundleCache: bundleCache,
        getContentLocale: () => 'zh-Hant',
        getBuiltInLibraries: () => [{ id: 'builtin-words', type: 'words' }],
        remoteWordbooks: [{ id: 'remote-ecdict-cet6', type: 'words' }],
        customLibraries: [{ id: 'local-words', type: 'words' }],
        getContentItemKey: () => '',
        presenceFetch: async () => ({
            ok: true,
            status: 200,
            json: async () => ({ locale: 'zh-Hant', libraries }),
        }),
        console: { warn() {} },
    }, [
        'getContentBundleCacheKey',
        'normalizeLocaleCatalog',
        'isLocaleCatalogFresh',
        'invalidateLocaleCatalog',
        'loadLocaleCatalog',
        'getAvailableLibraries',
        'getContentBundleItem',
    ]);

    await context.loadLocaleCatalog('zh-Hant');
    assert.deepEqual(
        Array.from(context.getAvailableLibraries('words', 'zh-Hant'), item => item.id),
        ['builtin-words', 'remote-ecdict-cet6', 'local-words'],
    );

    libraries = [{
        id: 'zh-Hant:words-cet4',
        type: 'words',
        dataset: 'words-cet4',
        sourceLibraryId: 'builtin-words',
        name: 'CET-4 核心詞庫',
        contentVersion: 'v-traditional-1',
    }];
    const [localizedLibrary] = await context.loadLocaleCatalog('zh-Hant');
    assert.deepEqual(
        Array.from(context.getAvailableLibraries('words', 'zh-Hant'), item => item.id),
        ['zh-Hant:words-cet4'],
    );
    bundleCache.set('words-cet4::zh-Hant::v-traditional-1', {
        contentVersion: 'v-traditional-1',
        items: { abandon: { definition: '放弃' } },
        content: [{
            libraryId: 'zh-Hant:words-cet4',
            itemKey: 'abandon',
            position: 0,
            payload: { word: 'abandon', definitionLocalized: '放棄' },
        }],
    });
    assert.equal(
        context.getContentBundleItem('words-cet4', 'abandon', 'zh-Hant', localizedLibrary, 0).definitionLocalized,
        '放棄',
    );
});

test('empty locale catalogs are not session-cached and populated catalogs expire by TTL', async () => {
    let now = 1000;
    let requestCount = 0;
    let libraries = [];
    const catalogCache = new Map();
    const context = runFunctions({
        CONTENT_FALLBACK_LOCALE: 'zh-Hans',
        API_BASE_URL: 'https://api.example.test',
        LOCALE_CATALOG_TTL_MS: 1000,
        localizedCatalogCache: catalogCache,
        localizedCatalogRequests: new Map(),
        localizedCatalogFetchedAt: new Map(),
        localizedLibraryCache: new Map(),
        getContentLocale: () => 'fr',
        Date: { now: () => now },
        presenceFetch: async () => {
            requestCount++;
            return {
                ok: true,
                status: 200,
                json: async () => ({ locale: 'fr', libraries }),
            };
        },
        console: { warn() {} },
    }, ['normalizeLocaleCatalog', 'isLocaleCatalogFresh', 'invalidateLocaleCatalog', 'loadLocaleCatalog']);

    assert.deepEqual(Array.from(await context.loadLocaleCatalog('fr')), []);
    assert.equal(catalogCache.has('fr'), false);
    libraries = [{
        id: 'fr:words-cet4', type: 'words', dataset: 'words-cet4',
        sourceLibraryId: 'builtin-words', name: 'Français', contentVersion: 'v1',
    }];
    await context.loadLocaleCatalog('fr');
    await context.loadLocaleCatalog('fr');
    assert.equal(requestCount, 2, 'the populated catalog should be reused inside its TTL');
    now += 1001;
    await context.loadLocaleCatalog('fr');
    assert.equal(requestCount, 3, 'the catalog should be revalidated after its TTL');
});

test('foreign article metadata comes only from localized payload fields', () => {
    const labels = {
        'article.defaultLevel': 'Niveau indisponible',
        'article.defaultTopic': 'Sujet indisponible',
        'article.listening': 'Écoute',
        'article.readingComprehension': 'Lecture',
    };
    const context = runFunctions({
        t: key => labels[key] || key,
        splitArticleText: () => [],
    }, ['resolveArticleMetadata', 'getArticleGenreMeta']);
    const normalizeStart = html.indexOf('function normalizeLibraryItems(');
    const normalizeEnd = html.indexOf('function splitArticleText(', normalizeStart);
    assert.ok(normalizeStart >= 0 && normalizeEnd > normalizeStart);
    vm.runInContext(html.slice(normalizeStart, normalizeEnd), context);
    const [article] = context.normalizeLibraryItems([{
        id: 'article-1',
        title: 'Canonical title',
        level: 'Junior high foundation',
        levelLocalized: 'Collège · Fondamentaux',
        cefr: 'A2',
        genre: 'reading',
        genreLocalized: 'Compréhension écrite',
        topic: 'People and society',
        topicLocalized: 'Individus et société',
        sentences: [{ en: 'A sentence.', translationLocalized: 'Une phrase.' }],
    }], 'articles');
    article.contentLocale = 'fr';
    article.sentences[0].contentLocale = 'fr';

    assert.equal(article.levelLocalized, 'Collège · Fondamentaux');
    assert.equal(article.genreLocalized, 'Compréhension écrite');
    assert.equal(article.topicLocalized, 'Individus et société');
    const [roundTrippedArticle] = context.normalizeLibraryItems([article], 'articles');
    assert.equal(roundTrippedArticle.contentLocale, 'fr');
    assert.equal(roundTrippedArticle.sentences[0].contentLocale, 'fr');
    assert.deepEqual(
        JSON.parse(JSON.stringify(
        context.resolveArticleMetadata(article, { localized: true }, 'fr'),
        )),
        {
            level: 'Collège · Fondamentaux',
            genre: 'Compréhension écrite',
            topic: 'Individus et société',
        },
    );

    const missing = context.resolveArticleMetadata({
        ...article,
        levelLocalized: '',
        genreLocalized: '',
        topicLocalized: '',
    }, { localized: true }, 'fr');
    assert.deepEqual(JSON.parse(JSON.stringify(missing)), {
        level: 'Niveau indisponible',
        genre: 'Lecture',
        topic: 'Sujet indisponible',
    });
    assert.ok(!Object.values(missing).includes('Junior high foundation'));
    assert.ok(!Object.values(missing).includes('People and society'));

    assert.deepEqual(
        JSON.parse(JSON.stringify(
        context.resolveArticleMetadata(article, { localized: false }, 'zh-Hant'),
        )),
        { level: 'Junior high foundation', genre: 'Lecture', topic: 'People and society' },
    );
    const traditionalArticle = {
        ...article,
        contentLocale: 'zh-Hant',
        levelLocalized: '中學基礎',
        genreLocalized: '閱讀理解',
        topicLocalized: '人物與社會',
    };
    assert.deepEqual(
        JSON.parse(JSON.stringify(
            context.resolveArticleMetadata(traditionalArticle, { localized: true }, 'zh-Hant'),
        )),
        { level: '中學基礎', genre: '閱讀理解', topic: '人物與社會' },
    );
    for (const genre of [
        'Short Listening Passage',
        'Listening Interview',
        'Listening Story',
        '聽力短文',
        '听力短文',
    ]) {
        assert.equal(context.getArticleGenreMeta(genre).icon, 'fa-headphones');
    }
    assert.match(functionSource('updateArticleCard'), /updateArticleMetadata\(article, articleLibrary\)/);
    assert.match(functionSource('refreshCurrentContentTranslations'), /updateArticleMetadata\(article, library\)/);
    assert.match(functionSource('refreshLocalizedInterface'), /updateArticleMetadata\(article, getContentLibrary\('articles'\)\)/);
});

test('selected foreign library attribution is visible and external links are hardened', () => {
    const exactNotice = 'This product is created by the adaptation of LEXiTRON developed by NECTEC (http://www.nectec.or.th/).';
    const createNode = tagName => ({
        tagName: tagName.toUpperCase(),
        children: [],
        append(...children) { this.children.push(...children); },
        appendChild(child) { this.children.push(child); },
    });
    const context = runFunctions({
        URL,
        YAITRON_ATTRIBUTION_NOTICE: exactNotice,
        document: { createElement: createNode },
        t: key => ({ 'shelf.sourceLabel': 'Source', 'shelf.licenseLabel': 'Licence' })[key] || key,
    }, [
        'getSafeAttributionUrl',
        'getLibraryAttributionNotices',
        'getLibraryAttributionNotice',
        'createLibraryAttributionValue',
        'createLibraryAttribution',
    ]);

    const attribution = context.createLibraryAttribution({
        id: 'th:yaitron',
        sourceName: 'Yaitron',
        sourceUrl: 'https://github.com/veer66/Yaitron',
        licenseName: 'LEXiTRON Terms of Use',
        licenseUrl: 'https://github.com/veer66/Yaitron/blob/master/LICENSE-LEXITRON',
    });
    assert.equal(attribution.children.length, 3);
    assert.equal(attribution.children[0].children[0].textContent, 'Source:');
    assert.equal(attribution.children[0].children[1].target, '_blank');
    assert.equal(attribution.children[0].children[1].rel, 'noopener noreferrer');
    assert.equal(attribution.children[2].textContent, exactNotice);
    assert.equal(context.createLibraryAttributionValue('Unsafe', 'javascript:alert(1)').tagName, 'SPAN');
    assert.equal(context.createLibraryAttributionValue('Safe', 'https://example.com/source').tagName, 'A');
    const notices = context.createLibraryAttribution({
        sourceNotice: 'Source notice.',
        licenseNotice: 'License notice.',
    });
    assert.deepEqual(
        notices.children.map(child => child.textContent),
        ['Source notice.', 'License notice.'],
    );
    assert.match(functionSource('renderLibraryShelf'), /isActive && library\.localized/);
    assert.match(functionSource('renderLibraryShelf'), /libraryListEl\.appendChild\(attribution\)/);
});

test('foreign notebook translation uses the current versioned full bundle and fails closed', () => {
    const library = {
        id: 'fr:words-cet4',
        type: 'words',
        dataset: 'wordbook-common',
        sourceLibraryId: 'builtin-words',
        contentVersion: 'v2',
        localized: true,
    };
    const cache = new Map([
        ['wordbook-common::fr::v2', {
            contentVersion: 'v2',
            items: {},
            content: [{
                libraryId: 'fr:words-cet4',
                itemKey: 'abandon',
                position: 0,
                payload: { word: 'abandon', definitionLocalized: 'abandonner' },
            }],
        }],
        ['words-cet4::fr::unversioned', {
            contentVersion: '',
            items: { abandon: { definition: '放弃' } },
            content: [],
        }],
    ]);
    const context = runFunctions({
        CONTENT_FALLBACK_LOCALE: 'zh-Hans',
        localizedCatalogCache: new Map([['fr', [library]]]),
        contentBundleCache: cache,
        getContentLocale: () => 'fr',
        getContentDatasetFromSourceId: () => '',
        getContentItemKey: () => '',
    }, [
        'getContentBundleCacheKey',
        'getCatalogLibraryForContent',
        'getContentBundleItem',
        'getInlineLocalizedItem',
        'resolvedContent',
        'getNotebookContentDataset',
        'getNotebookContentKey',
        'getNotebookEntryContentLocale',
        'getNotebookCatalogLibrary',
        'getNotebookBundleDataset',
        'getLocalizedPayloadField',
        'getNotebookLocalizedField',
        'resolveNotebookTranslation',
    ]);
    const savedChineseEntry = {
        type: 'word',
        sourceId: 'builtin-words',
        dataset: 'words-cet4',
        contentKey: 'abandon',
        contentPosition: 0,
        contentLocale: 'zh-Hant',
        definitionZh: '放弃',
    };

    assert.deepEqual(JSON.parse(JSON.stringify(context.resolveNotebookTranslation(savedChineseEntry, 'fr'))), {
        text: 'abandonner',
        locale: 'fr',
    });
    cache.set('wordbook-common::fr::v2', { contentVersion: 'v2', items: {}, content: [] });
    assert.deepEqual(JSON.parse(JSON.stringify(context.resolveNotebookTranslation(savedChineseEntry, 'fr'))), {
        text: '',
        locale: 'fr',
    });
    assert.deepEqual(JSON.parse(JSON.stringify(context.resolveNotebookTranslation(savedChineseEntry, 'zh-Hant'))), {
        text: '放弃',
        locale: 'zh-Hant',
    });
    const savedFrenchEntry = {
        ...savedChineseEntry,
        contentLocale: 'fr',
        definitionZh: 'abandonner',
    };
    assert.deepEqual(JSON.parse(JSON.stringify(context.resolveNotebookTranslation(savedFrenchEntry, 'fr'))), {
        text: 'abandonner',
        locale: 'fr',
    });
    assert.deepEqual(JSON.parse(JSON.stringify(context.resolveNotebookTranslation(savedFrenchEntry, 'ja'))), {
        text: '',
        locale: 'ja',
    });
    assert.match(functionSource('getCurrentNotebookEntry'), /library\.localized \? '' : definitions\.chinese/);
    assert.doesNotMatch(functionSource('loadWordsFromJsFiles'), /localizedDefinition\.text \|\| wordData\.definition/);
});

test('notebook bundle requests follow the current catalog output dataset', async () => {
    const calls = [];
    const libraries = {
        word: { id: 'fr:words-common', type: 'words', dataset: 'wordbook-common', contentVersion: 'words-v3' },
        sentence: { id: 'fr:sentences-common', type: 'sentences', dataset: 'sentences-common', contentVersion: 'sentences-v4' },
    };
    const context = runFunctions({
        vocabularyNotebook: [
            { type: 'word', dataset: 'words-cet4', contentKey: 'abandon' },
            { type: 'sentence', dataset: 'sentences-tatoeba-basic', contentKey: '387554' },
        ],
        vocabularyNotebookModal: null,
        notebookDisplayedEntry: null,
        getContentLocale: () => 'fr',
        getNotebookCatalogLibrary: entry => libraries[entry.type],
        getNotebookContentDataset: entry => entry.dataset,
        getContentBundleCacheKey: (dataset, locale, version) => `${dataset}::${locale}::${version}`,
        loadContentBundle: async (...args) => {
            calls.push(args);
            return { contentVersion: args[2], content: [] };
        },
        renderVocabularyNotebook() {},
        refreshCurrentContentTranslations() {},
    }, ['getNotebookBundleDataset', 'requestNotebookContentBundles']);

    await context.requestNotebookContentBundles();
    assert.deepEqual(JSON.parse(JSON.stringify(calls)), [
        ['wordbook-common', 'fr', 'words-v3'],
        ['sentences-common', 'fr', 'sentences-v4'],
    ]);
});

test('legacy notebook ids migrate to locale-independent content identities and duplicate entries collapse', () => {
    const storage = new Map();
    storage.set('notebook', JSON.stringify([
        {
            id: 'fr:words-cet4::abandon',
            type: 'word',
            word: 'abandon',
            sourceId: 'fr:words-cet4',
            dataset: 'words-cet4',
            contentKey: 'abandon',
            contentLocale: 'fr',
            definitionZh: 'abandonner',
        },
        {
            id: 'builtin-words::abandon',
            word: 'abandon',
            sourceId: 'builtin-words',
            definitionZh: '放弃',
        },
        {
            id: 'sentence::builtin-sentences::how are you?',
            text: 'How are you?',
            sourceId: 'builtin-sentences',
            translation: '你好嗎？',
            contentLocale: 'zh-Hans',
        },
    ]));
    const context = runFunctions({
        CONTENT_FALLBACK_LOCALE: 'zh-Hans',
        VOCABULARY_NOTEBOOK_KEY: 'notebook',
        localStorage: {
            getItem: key => storage.get(key) ?? null,
            setItem: (key, value) => storage.set(key, String(value)),
        },
        console: { warn() {} },
    }, [
        'normalizeContentLookupKey',
        'getLibraryContentDataset',
        'getContentItemKey',
        'getContentDatasetFromSourceId',
        'getNotebookContentDataset',
        'getNotebookContentKey',
        'getNotebookSourceLibraryId',
        'getNotebookSourceDataset',
        'getNotebookIdentityDataset',
        'getStableNotebookEntryId',
        'getNotebookEntryContentLocale',
        'normalizeVocabularyNotebookEntry',
        'loadVocabularyNotebook',
    ]);

    const entries = context.loadVocabularyNotebook();
    assert.equal(entries.length, 2, 'the same dataset item saved from two UI locales should not duplicate');
    assert.equal(entries[0].id, 'word::words-cet4::abandon');
    assert.equal(entries[0].contentLocale, 'fr');
    assert.equal(entries[1].id, 'sentence::sentences-daily::how are you?');
    assert.equal(entries[1].contentLocale, 'zh-Hant');
    assert.deepEqual(
        JSON.parse(storage.get('notebook')).map(entry => entry.id),
        ['word::words-cet4::abandon', 'sentence::sentences-daily::how are you?'],
    );
    const foreignWordLibrary = {
        id: 'fr:words-common',
        type: 'words',
        dataset: 'wordbook-common',
        sourceLibraryId: 'builtin-words',
    };
    const foreignSentenceLibrary = {
        id: 'fr:sentences-common',
        type: 'sentences',
        dataset: 'sentences-common',
        sourceLibraryId: 'builtin-sentences-tatoeba-basic',
    };
    assert.equal(context.getNotebookSourceDataset('words', foreignWordLibrary), 'words-cet4');
    assert.equal(context.getNotebookSourceDataset('sentences', foreignSentenceLibrary), 'sentences-tatoeba-basic');
    assert.equal(
        context.getStableNotebookEntryId({ type: 'word', dataset: context.getNotebookSourceDataset('words', foreignWordLibrary), contentKey: 'abandon' }),
        'word::words-cet4::abandon',
    );
    assert.match(functionSource('getCurrentNotebookEntry'), /getNotebookSourceDataset\('words', library\)/);
    assert.match(functionSource('getCurrentPhraseNotebookEntry'), /getNotebookSourceDataset\('sentences', library\)/);
});

test('active library preferences are isolated by locale while retaining the Chinese legacy key', () => {
    const storage = new Map([
        ['enplay_active_libraries', JSON.stringify({ words: 'remote-ecdict-cet6' })],
        ['enplay_active_libraries_by_locale_v2', JSON.stringify({ ja: { words: 'ja:words-cet4' } })],
    ]);
    const context = runFunctions({
        localStorage: {
            getItem: key => storage.get(key) ?? null,
            setItem: (key, value) => storage.set(key, String(value)),
        },
        getContentLocale: () => 'ja',
        activeLibraryIds: { words: 'ja:words-cet6', sentences: 'ja:sentences', articles: 'ja:articles' },
        console: { warn() {} },
        getAvailableLibraries: () => [],
    }, ['getDefaultActiveLibraryIds', 'loadActiveLibraryIds', 'saveActiveLibraryIds']);

    assert.equal(context.loadActiveLibraryIds('ja').words, 'ja:words-cet4');
    assert.equal(context.loadActiveLibraryIds('zh-Hant').words, 'remote-ecdict-cet6');
    context.saveActiveLibraryIds('ja');
    const scoped = JSON.parse(storage.get('enplay_active_libraries_by_locale_v2'));
    assert.equal(scoped.ja.words, 'ja:words-cet6');
    assert.equal(JSON.parse(storage.get('enplay_active_libraries')).words, 'remote-ecdict-cet6');
});

test('Traditional Chinese catalog aliases preserve the legacy active library and progress storage scope', () => {
    const storage = new Map([
        ['enplay_active_libraries', JSON.stringify({
            words: 'remote-ecdict-cet6',
            sentences: 'builtin-sentences-tatoeba-basic',
            articles: 'builtin-articles-senior-basic',
        })],
        ['enplay_active_libraries_by_locale_v2', JSON.stringify({
            'zh-Hant': {
                words: 'remote-ecdict-cet6',
                sentences: 'builtin-sentences-tatoeba-basic',
                articles: 'builtin-articles-senior-basic',
            },
        })],
    ]);
    const libraries = {
        words: [{
            id: 'zh-Hant:wordbook-cet6',
            type: 'words',
            sourceLibraryId: 'remote-ecdict-cet6',
            locale: 'zh-Hant',
            localized: true,
        }],
        sentences: [{
            id: 'zh-Hant:sentences-basic',
            type: 'sentences',
            sourceLibraryId: 'builtin-sentences-tatoeba-basic',
            locale: 'zh-Hant',
            localized: true,
        }],
        articles: [{
            id: 'zh-Hant:articles-graded',
            type: 'articles',
            sourceLibraryId: 'builtin-articles-senior-basic',
            locale: 'zh-Hant',
            localized: true,
        }],
    };
    const context = runFunctions({
        localStorage: {
            getItem: key => storage.get(key) ?? null,
            setItem: (key, value) => storage.set(key, String(value)),
        },
        getContentLocale: () => 'zh-Hant',
        getAvailableLibraries: type => libraries[type],
        activeLibraryIds: {
            words: 'zh-Hant:wordbook-cet6',
            sentences: 'zh-Hant:sentences-basic',
            articles: 'zh-Hant:articles-graded',
        },
        CURRENT_INDEX_KEY: '',
        ORDER_KEY: '',
        ORDER_POSITION_KEY: '',
        LEARNED_WORDS_KEY: '',
        LEARNED_PHRASES_KEY: '',
        console: { warn() {} },
    }, [
        'getDefaultActiveLibraryIds',
        'getLegacyActiveLibraryIds',
        'loadActiveLibraryIds',
        'resolveAvailableLibraryId',
        'saveActiveLibraryIds',
        'setLibraryStorageScope',
        'getLibraryStorageScopeId',
    ]);

    const loaded = context.loadActiveLibraryIds('zh-Hant');
    assert.equal(
        context.resolveAvailableLibraryId('words', loaded.words, libraries.words, 'zh-Hant'),
        'zh-Hant:wordbook-cet6',
    );
    const scopeId = context.getLibraryStorageScopeId(libraries.words[0]);
    assert.equal(scopeId, 'remote-ecdict-cet6');
    context.setLibraryStorageScope('words', scopeId);
    assert.equal(context.CURRENT_INDEX_KEY, 'cet4_current_index:remote-ecdict-cet6');
    assert.equal(context.ORDER_KEY, 'cet4_word_order:remote-ecdict-cet6');
    assert.equal(context.LEARNED_WORDS_KEY, 'cet4_learned_words:remote-ecdict-cet6');

    context.saveActiveLibraryIds('zh-Hant');
    assert.deepEqual(
        JSON.parse(storage.get('enplay_active_libraries')),
        {
            words: 'remote-ecdict-cet6',
            sentences: 'builtin-sentences-tatoeba-basic',
            articles: 'builtin-articles-senior-basic',
        },
    );
});

test('locale changes wait for a playback boundary and translated TTS receives an explicit locale', () => {
    const refresh = functionSource('refreshLocalizedInterface');
    assert.doesNotMatch(refresh, /stopPlayback|stopPhrasePlayback|stopArticlePlayback/);
    assert.match(functionSource('finishCurrentWordPlayback'), /completePendingLocaleSwitchAtBoundary\('words'\)/);
    assert.match(functionSource('playCurrentPhrase'), /completePendingLocaleSwitchAtBoundary\('sentences'\)/);
    assert.match(functionSource('finishArticlePlayback'), /completePendingLocaleSwitchAtBoundary\('articles'\)/);
    assert.match(html, /utterance\.lang = options\.lang \|\|/);
    assert.match(functionSource('playChineseDefinitionIfEnabled'), /getContentSpeechLanguage/);
});

test('idle locale changes and uncached foreign views clear stale cards before awaiting content', async () => {
    let releaseCatalog;
    const catalogPending = new Promise(resolve => { releaseCatalog = resolve; });
    const cleared = [];
    const synchronized = runFunctions({
        currentWorkspaceView: 'words',
        pendingLocaleLibrarySwitch: null,
        activeLibraryIds: { words: 'builtin-words', sentences: 'builtin-sentences', articles: 'builtin-articles' },
        appliedLibraryLocales: { words: 'zh-Hant', sentences: 'zh-Hant', articles: 'zh-Hant' },
        vocabularyNotebook: [],
        clearPendingLocaleLibrarySwitch() {},
        captureLocalePlaybackResumeContext: () => ({ resumeAfterSwitch: false, playbackKind: 'words' }),
        isViewPlaybackActive: () => false,
        showLocaleContentEmpty: view => cleared.push(view),
        loadActiveLibraryIds: () => ({
            words: 'fr:words-common',
            sentences: 'fr:sentences-common',
            articles: 'fr:articles-graded',
        }),
        loadLocaleCatalog: () => catalogPending,
        getContentLocale: () => 'fr',
        getAvailableLibraries: type => [{ id: `fr:${type}-common`, type }],
        resolveAvailableLibraryId: (type, requestedId, libraries) => (
            libraries.some(library => library.id === requestedId)
                ? requestedId
                : libraries[0] && libraries[0].id || ''
        ),
        saveActiveLibraryIds() {},
        renderLibraryShelf() {},
        flushPendingLocaleLibrarySwitch() {},
    }, ['synchronizeLocaleLibraries']);

    const synchronization = synchronized.synchronizeLocaleLibraries('fr');
    assert.deepEqual(cleared, ['words'], 'the previous locale must be hidden before the catalog request settles');
    releaseCatalog([]);
    await synchronization;

    const scheduleClears = [];
    let viewPlaying = false;
    const scheduled = runFunctions({
        pendingLocaleLibrarySwitch: null,
        appliedLibraryLocales: { sentences: 'zh-Hant' },
        appliedLibraryIds: { sentences: 'builtin-sentences' },
        appliedLibraryVersions: { sentences: '' },
        getContentLocale: () => 'fr',
        getAvailableLibraries: () => [{
            id: 'fr:sentences-common',
            type: 'sentences',
            localized: true,
            contentVersion: 'v2',
        }],
        clearPendingLocaleLibrarySwitch() {},
        isViewPlaybackActive: () => viewPlaying,
        showLocaleContentEmpty: view => scheduleClears.push(view),
        captureLocalePlaybackResumeContext: () => ({
            resumeAfterSwitch: false,
            playbackKind: 'sentences',
            notebookType: '',
            notebookIndex: -1,
        }),
        flushPendingLocaleLibrarySwitch() {},
    }, ['scheduleLocaleLibrarySwitch']);

    scheduled.scheduleLocaleLibrarySwitch('fr', 'sentences', 'fr:sentences-common');
    assert.deepEqual(scheduleClears, ['sentences']);
    scheduleClears.length = 0;
    viewPlaying = true;
    scheduled.scheduleLocaleLibrarySwitch('fr', 'sentences', 'fr:sentences-common');
    assert.deepEqual(scheduleClears, [], 'active playback keeps the current card until its boundary');
});

test('restarting article playback restores locale-boundary continuation', () => {
    const context = runFunctions({
        articleList: [{ sentences: [{ en: 'Hello.' }] }],
        articleIndex: 0,
        articleSentenceIndex: 0,
        articlePassCount: 2,
        articlePlaybackMode: 'article',
        articlePlaybackCompleted: false,
        continueAutoPlay: false,
        isArticlePlaying: false,
        isPlaying: false,
        isPhrasePlaying: false,
        isNotebookPlaying: false,
        isAutoPlaying: true,
        notebookPlaybackType: '',
        notebookPlaybackIndex: -1,
        stopPlayback() {},
        stopPhrasePlayback() {},
        stopVocabularyNotebookPlayback() {},
        cancelSpeechSession() {},
        articlePlayIcon: { classList: { replace() {} } },
        articleStatusKey: '',
        updateTransportButtonLabels() {},
        playCurrentArticleSentence() {},
        Math,
    }, ['isViewPlaybackActive', 'captureLocalePlaybackResumeContext', 'startArticlePlayback']);

    context.startArticlePlayback(0, 'article', { resetPass: false });
    assert.equal(context.continueAutoPlay, true);
    assert.equal(context.isArticlePlaying, true);
    assert.equal(context.captureLocalePlaybackResumeContext('articles').resumeAfterSwitch, true);
});

test('notebook item looping yields to a pending locale switch at the configured entry boundary', () => {
    const events = [];
    const context = runFunctions({
        isNotebookPlaying: true,
        notebookEntryPlayCount: 2,
        playRepeatCount: 3,
        isWordLooping: true,
        pendingLocaleLibrarySwitch: { view: 'words' },
        notebookPlaybackIndex: 0,
        notebookPlaybackQueue: [{ word: 'one' }],
        isAutoPlaying: true,
        notebookRepeatTimer: null,
        schedulePlaybackStep: () => {
            events.push('repeat');
            return 1;
        },
        stopVocabularyNotebookPlayback: () => events.push('stop'),
        completePendingLocaleSwitchAtBoundary: view => {
            events.push(`switch:${view}`);
            return true;
        },
    }, ['finishCurrentNotebookEntryPlayback']);

    context.finishCurrentNotebookEntryPlayback();
    assert.deepEqual(events, ['stop', 'switch:words']);
    assert.equal(context.notebookEntryPlayCount, 0);

    events.length = 0;
    context.pendingLocaleLibrarySwitch = null;
    context.isNotebookPlaying = true;
    context.notebookEntryPlayCount = 2;
    context.finishCurrentNotebookEntryPlayback();
    assert.deepEqual(events, ['repeat'], 'item looping continues only when no locale switch is pending');
});

test('manual pause cancels a pending locale resume and notebook playback keeps its queue semantics', () => {
    const resumed = [];
    const context = runFunctions({
        pendingLocaleLibrarySwitch: { view: 'words', resumeAfterSwitch: true },
        currentWorkspaceView: 'words',
        isAutoPlaying: true,
        continueAutoPlay: true,
        notebookPlaybackQueue: [{ word: 'one' }, { word: 'two' }, { word: 'three' }],
        notebookPlaybackType: 'word',
        notebookPlaybackIndex: 0,
        notebookEntryPlayCount: 2,
        resumeVocabularyNotebookPlayback: () => resumed.push('notebook'),
        startPlayback: () => resumed.push('words'),
        startPhrasePlayback: () => resumed.push('sentences'),
        startArticlePlayback: () => resumed.push('articles'),
        Math,
        Number,
    }, ['cancelPendingLocalePlaybackResume', 'resumePendingLocalePlayback']);

    context.cancelPendingLocalePlaybackResume('words');
    assert.equal(context.pendingLocaleLibrarySwitch.resumeAfterSwitch, false);
    assert.equal(context.resumePendingLocalePlayback(context.pendingLocaleLibrarySwitch), false);
    assert.deepEqual(resumed, []);

    context.continueAutoPlay = true;
    const notebookPending = {
        view: 'sentences',
        resumeAfterSwitch: true,
        playbackKind: 'notebook',
        notebookType: 'sentence',
        notebookIndex: 2,
    };
    assert.equal(context.resumePendingLocalePlayback(notebookPending), true);
    assert.deepEqual(resumed, ['notebook']);
    assert.equal(context.notebookPlaybackType, 'sentence');
    assert.equal(context.notebookPlaybackIndex, 2);
    assert.equal(context.notebookEntryPlayCount, 0);
});

# Enplay API

## Independent localized libraries

The public multilingual bookshelf is backed by complete, locale-scoped
libraries rather than runtime translation overlays:

- `content_libraries` stores a library's locale, type, dataset, attribution,
  active content version, item count, order, and publication status.
- `content_library_items` stores the complete localized word, sentence, or
  article payload for an immutable content version and position.
- `content_segments` and `content_translations` retain field-level source
  provenance and support the existing `zh-Hant` compatibility path. They are
  not the source of foreign-language bookshelves.

`ja`, `ko`, `fr`, `es`, `pt`, `ru`, `th`, and `ar` never fall back to a
Chinese library or a partial translation map. If a foreign catalog or complete
bundle is unavailable, the API returns an empty catalog or `404` and the client
must show that the language has no available content. `zh-Hant` continues to
use the existing application libraries; its field-level bundle path is kept
only for compatibility and auditability.

`Base.metadata.create_all()` creates these four additive tables on startup. It
does not alter the existing word, sentence, article, or wordbook tables. Take a
database backup and inspect the DDL on development before the first production
rollout. Later column or index changes require a versioned migration rather
than relying on `create_all()`.

Supported locales are `zh-Hant`, `ja`, `ko`, `fr`, `es`, `pt`, `ru`, `th`, and
`ar`. Supported datasets are `words-cet4`, `wordbook-{slug}`,
`sentences-daily`, `sentences-tatoeba-basic`,
`sentences-tatoeba-intermediate`, the aggregated `sentences-common`, and
the fixed article datasets `articles-graded`,
`articles-graded-junior-basic`, `articles-graded-junior-advanced`,
`articles-graded-senior-basic`, and `articles-graded-senior-advanced`. A locale
can publish only one library for a dataset. The five article datasets preserve
the existing all-articles shelf plus its four level shelves without weakening
that uniqueness rule.

Stable item keys are lowercase, whitespace-collapsed words for word datasets;
lowercase, whitespace-collapsed English text for `sentences-daily` (later
duplicates receive a deterministic `#duplicate-N` suffix); positive Tatoeba
source IDs for `sentences-common` and both Tatoeba datasets (the first unused
ID in `sourceIds` is preferred, with a deterministic positive record key only
when every real ID is already used); and lowercase article IDs scoped within
each fixed `articles-graded*` dataset.

## Public catalog API

Public catalog and bundle reads participate in the same 200-user admission
gate as the existing word, sentence, article, and wordbook APIs. Browser
clients send the signed live lease as `X-Presence-Token` (the `presence` query
parameter remains available for compatibility). A missing, invalid, or expired
lease returns `401`; the health, presence join/status, and authenticated admin
routes retain their existing behavior.

```text
GET /v1/i18n/catalog/{locale}
```

The catalog lists only `ready` or `reviewed` libraries for the requested
locale. An allowed locale with no published libraries returns an empty list.
Catalog responses use ETags for explicit conditional requests but are marked
`private, no-store`; neither a CDN nor a browser may retain them past the
request that passed the presence gate.

```json
{
  "schemaVersion": 1,
  "locale": "ja",
  "libraries": [
    {
      "id": "ja:words-cet4",
      "type": "words",
      "dataset": "words-cet4",
      "sourceLibraryId": "builtin-words",
      "name": "英日 CET-4 語彙",
      "description": "...",
      "format": "WikDict · 日本語",
      "itemCount": 4123,
      "source": {"name": "WikDict", "url": "https://example.invalid/source", "notice": null},
      "license": {"name": "CC BY-SA 4.0", "url": "https://creativecommons.org/licenses/by-sa/4.0/", "notice": null},
      "contentVersion": "ja-cet4-2026.09.04"
    }
  ]
}
```

## Public bundle API

```text
GET /v1/i18n/bundles/{dataset}/{locale}?v={catalog.contentVersion}
```

A foreign-language response materializes complete records in deterministic
display order. `items` is reserved for the `zh-Hant` compatibility map;
foreign clients consume `content`.

```json
{
  "schemaVersion": 1,
  "dataset": "words-cet4",
  "locale": "ja",
  "contentVersion": "ja-cet4-2026.09.04",
  "items": {},
  "content": [
    {
      "libraryId": "ja:words-cet4",
      "itemKey": "abandon",
      "position": 0,
      "payload": {
        "word": "abandon",
        "phonetic": "/əˈbændən/",
        "definitionLocalized": "捨てる、断念する",
        "definitionEn": "to leave or give up completely",
        "example": "They had to abandon the plan.",
        "contentKey": "abandon",
        "sourceLibraryId": "builtin-words"
      }
    }
  ]
}
```

Complete payload shapes are:

| Type | Required payload |
| --- | --- |
| Word | `word`, `definitionLocalized`, `definitionEn`, `contentKey`, `sourceLibraryId`; optional `phonetic`, `example` |
| Sentence | `text`, `translationLocalized`, `sourceIds`, `contentKey`, `sourceLibraryId`; optional `scene` |
| Article | `id`, `title`, `titleLocalized`, `summaryLocalized`, canonical English `level`/`genre`/`topic`, `levelLocalized`/`genreLocalized`/`topicLocalized`, `cefr`, `estimatedWords`, non-empty `sentences[{en,translationLocalized}]`, `contentKey`, `sourceLibraryId` |

The item importer accepts the earlier unambiguous aliases `definition`,
`translation`, `titleTranslation`, `summaryTranslation`, and nested
`translation`, but stores and returns the explicit `*Localized` field names.
Conflicting aliases are rejected.

Unsupported, unpublished, and incomplete foreign bundles return `404` rather
than exposing a Chinese fallback. Ambiguous locale/dataset resolution returns
`409`. Responses include a deterministic ETag and `Content-Language`, use
`Cache-Control: private, no-store` so a shared CDN cache cannot bypass the
presence admission gate, and support conditional `If-None-Match` requests.
The API does not retain full bundles in a Python process-wide memory cache.

Foreign clients pass the catalog's `contentVersion` as `v` and must verify that
the bundle response has the same `contentVersion`. The query parameter binds
the read to the catalog version and makes a stale client fail closed instead of
materializing mismatched content. Omitting `v` remains supported for
compatibility; supplying a version other than the active one returns `404`.

A client may still hold an older catalog in its own short-lived memory cache at
the instant a new version is promoted. When a versioned bundle request returns
`404`, discard that locale's in-memory catalog/materialized cache, revalidate
the catalog, and retry once with the newly advertised version. If that retry
also fails, show the locale as temporarily unavailable; never substitute a
Chinese library. The API intentionally does not expose arbitrary non-active
item versions because uploaded staging rows have not necessarily been
published or reviewed.

## Offline import APIs

All admin routes require `X-Admin-Token`. They only validate and persist
already-generated data; they never call a translation provider.

### 1. Create a draft catalog library

```text
POST /v1/admin/i18n/catalog
```

```json
{
  "schemaVersion": 1,
  "locale": "ja",
  "contentVersion": "ja-cet4-2026.09.04",
  "libraries": [
    {
      "id": "ja:words-cet4",
      "type": "words",
      "dataset": "words-cet4",
      "sourceLibraryId": "builtin-words",
      "name": "英日 CET-4 語彙",
      "description": "...",
      "format": "WikDict · 日本語",
      "itemCount": 4123,
      "source": {"name": "WikDict", "url": "https://example.invalid/source", "notice": null},
      "license": {"name": "CC BY-SA 4.0", "url": "https://creativecommons.org/licenses/by-sa/4.0/", "notice": null},
      "status": "draft",
      "displayOrder": 100
    }
  ]
}
```

Library IDs must be locale-scoped, such as `ja:words-cet4`. Identity fields
`type`, `dataset`, and `sourceLibraryId` cannot be changed after creation.
Missing attribution URLs may be `null` or an empty string; non-empty URLs must
use HTTP or HTTPS. `source.notice` and `license.notice` preserve any exact
redistribution acknowledgement or disclaimer that the frontend must display;
notices are stored verbatim apart from surrounding whitespace.

### 2. Import complete versioned records

```text
POST /v1/admin/i18n/library-items
```

```json
{
  "schemaVersion": 1,
  "locale": "ja",
  "libraryId": "ja:words-cet4",
  "contentVersion": "ja-cet4-2026.09.04",
  "items": [
    {
      "itemKey": "abandon",
      "position": 0,
      "payload": {
        "word": "abandon",
        "phonetic": "/əˈbændən/",
        "definitionLocalized": "捨てる、断念する",
        "definitionEn": "to leave or give up completely",
        "example": "They had to abandon the plan.",
        "contentKey": "abandon",
        "sourceLibraryId": "builtin-words"
      },
      "sourceHash": "<lowercase SHA-256 source fingerprint>",
      "status": "ready"
    }
  ]
}
```

Each request accepts at most 100 records and each canonical JSON payload is
limited to 250,000 UTF-8 bytes. The API verifies the item key and catalog
identity, computes its own payload hash, and upserts idempotently within the
specified content version. Once a versioned item row exists it is immutable,
even after another version becomes active; an exact replay is accepted, while
any payload, source hash, position, or status change must use a new
`contentVersion`. This preserves version integrity and known-good rollback
versions.

### 3. Publish the complete version

Post the same catalog metadata again with `status` set to `ready` or
`reviewed`. Promotion succeeds only when the number of ready/reviewed records
in that exact content version equals the declared `itemCount`. The metadata
update then changes the active version atomically.

For the first release, post the generated `*.draft.json`, all matching item
batches, and finally `*.ready.json`. To replace an already-published library,
leave its current catalog row untouched while staging item batches under the
new version, then post the new `*.ready.json`. For safety, a draft request for
an already-ready library is treated as a staging no-op and returns a
`librariesStaged` count; it never hides or changes the active version. Retain
the old version rows for rollback, which is a catalog metadata switch rather
than a bulk rewrite.

There is intentionally no automatic old-version deletion in the request path.
Keep at least the active and previous known-good versions. Review row counts
and database backups during maintenance, then prune only versions that are not
referenced by `content_libraries.content_version`; do not run pruning alongside
an import or audio build.

### Field-level provenance compatibility

```text
POST /v1/admin/i18n/translations
```

This endpoint accepts at most 500 stable field translations per request and
verifies an optional SHA-256 of the exact source text. It exists for `zh-Hant`
compatibility and translation provenance/auditing; it does not create a
foreign-language bookshelf and foreign bundle reads never use these rows.
Article audit fields include `title`, `summary`, `level`, `genre`, `topic`, and
`sentences.N`.

Generate and validate translations outside the public request path. Import in
small resumable batches, verify counts and sample output on the development
database, and promote only deterministic manifests and localized tables; do
not replace the full production database.

## Tests

Install the development requirements and run the focused API and content
pipeline tests from the repository root:

```text
python -m pip install -r api/requirements-dev.txt
python -m pytest -p no:cacheprovider tests/test_i18n_api.py tests/test_i18n_content_pipeline.py
```

# Enplay multilingual content builder

`i18n_content_pipeline.py` builds reviewable, deterministic locale libraries. It
does not change `words.js`, the sentence sources, the article source, the API, or
the web page. Run translation work on the development host and publish only the
reviewed JSON artifacts.

## Output contract

Every target locale has at most one ready library for each dataset:

- `wordbook-common`: a standalone English–target-language word library.
- `sentences-common`: a standalone English–target-language sentence library.
- `articles-graded`: the 12-article aggregate shelf.
- `articles-graded-junior-basic`, `articles-graded-junior-advanced`,
  `articles-graded-senior-basic`, and `articles-graded-senior-advanced`: the
  four three-article level shelves. Their `sourceLibraryId` values remain the
  exact existing `builtin-articles-*` IDs.

`bundles/<dataset>/<locale>.json` contains both the field map used by the
existing bundle reader and ordered, fully materialised content:

```json
{
  "schemaVersion": 1,
  "kind": "enplay.localized-content-bundle",
  "dataset": "sentences-common",
  "locale": "ja",
  "contentVersion": "<sha256>",
  "items": {"3101536": {"translation": "…"}},
  "content": [
    {
      "libraryId": "ja:sentences-common",
      "itemKey": "3101536",
      "position": 0,
      "payload": {
        "scene": "greetingsSocial",
        "text": "Can you please give me something to do?",
        "translationLocalized": "…",
        "sourceIds": [3101536, 123456],
        "contentKey": "3101536",
        "sourceLibraryId": "builtin-sentences-tatoeba-basic"
      }
    }
  ]
}
```

Additional artifacts are:

- `catalog/<locale>.json`: locale catalog manifest for inspection.
- `admin/catalog/<locale>/<library>.draft.json`: create/update the catalog row
  as draft before importing items.
- `admin/library-items/<locale>/<library>/NNNN.json`: complete content imports,
  at most 100 items per request.
- `admin/catalog/<locale>/<library>.ready.json`: atomically expose the library
  after every item batch succeeds.
- `upserts/<dataset>/<locale>/NNNN.json`: field-level provenance/audit imports,
  at most 500 translations per request.
- `reports/`: coverage and missing keys; `provenance/`: source and license data.
- `.checkpoints/`: source fingerprints and completed-stage markers. Re-running
  the same command is a no-op unless `--force` is supplied.

The complete content payload never includes Chinese as a runtime fallback for
`ja`, `ko`, `fr`, `es`, `pt`, `ru`, `th`, or `ar`. English remains canonical.
Localized payload fields are explicit: words use `definitionLocalized`,
sentences use `translationLocalized`, and articles use `titleLocalized`,
`summaryLocalized`, `levelLocalized`, `genreLocalized`, `topicLocalized`, plus
`sentences[].translationLocalized`. Foreign article payloads retain canonical
English `level`, `genre`, and `topic` alongside those localized fields; they
never copy the original Chinese metadata into the independent library.

## 1. Export canonical project content

```powershell
python tools/i18n_content_pipeline.py export `
  --project-root . `
  --output build/i18n/source-manifest.json
```

Five API wordbooks can be added using one `--wordbook-json` argument per saved
JSON response or HTTPS API URL. For a protected API URL, pass
`--presence-token`; do not put a token in a committed command file. Every
exported word must include a non-empty `definition_en` or `definitionEn` value;
the export fails closed instead of creating a library that the API would reject
or filling the English definition from Chinese.

```powershell
python tools/i18n_content_pipeline.py export `
  --project-root . `
  --wordbook-json build/input/cet6.json `
  --wordbook-json build/input/kaoyan.json `
  --wordbook-json build/input/ielts.json `
  --wordbook-json build/input/toefl.json `
  --wordbook-json build/input/gre.json `
  --output build/i18n/source-manifest.json
```

The current built-in source export is expected to contain 4,123 CET-4 words,
429 daily sentences, two 1,000-item Tatoeba libraries, and five article
datasets: one 12-article aggregate plus four three-article level shelves. The
aggregate has 167 translatable text fields plus 36 localized metadata fields
(203 total). Repeated articles are intentionally scoped by dataset, so their
stable item keys do not collide across shelves.

## 2. Generate complete Traditional Chinese maps with OpenCC

Install the pinned offline converter into a dedicated `.i18n-python`
environment on the development host only (do not add it to the API runtime):

```powershell
python -m venv .i18n-python
& .\.i18n-python\Scripts\python.exe -m pip install -r tools/requirements-i18n.txt
```

On the Linux development host, the equivalent interpreter is
`.i18n-python/bin/python` after `python3 -m venv .i18n-python`.

Run `opencc-hant` once for every dataset in the exported manifest. It always
uses OpenCC's `s2t` profile and reads only each field's explicit `zh-Hans`
source; it never translates from English or fills gaps from another language.

```powershell
& .\.i18n-python\Scripts\python.exe tools/i18n_content_pipeline.py opencc-hant `
  --manifest build/i18n/source-manifest.json `
  --source-dataset words-cet4 `
  --output build/reviewed/words-cet4-zh-Hant.json `
  --checkpoint-dir build/i18n/.translation-state `
  --batch-size 100
```

The final reviewed-map is atomically written only after every item and field
has a non-empty, hash-matched Simplified Chinese source and every conversion
succeeds. Partial progress stays in an atomic checkpoint, so rerunning resumes
without making incomplete content publishable. Daily-sentence duplicate text
gets a deterministic `#duplicate-N` content key. Tatoeba collisions prefer the
next unused real ID in `sourceIds`; only an exact repeated source pair receives
a deterministic positive record key, while its original IDs remain in the
payload for attribution.

Materialise each complete map through the existing reviewed stage, preserving
that source library's actual attribution and license metadata:

```powershell
& .\.i18n-python\Scripts\python.exe tools/i18n_content_pipeline.py reviewed `
  --manifest build/i18n/source-manifest.json `
  --source-dataset words-cet4 `
  --output-dataset words-cet4 `
  --locale zh-Hant `
  --output-dir build/i18n `
  --library-id zh-Hant:words-cet4 `
  --name "CET-4 繁體詞庫" `
  --description "CET-4 English vocabulary with Traditional Chinese meanings" `
  --translations build/reviewed/words-cet4-zh-Hant.json `
  --provider OpenCC `
  --model s2t `
  --source-url "SOURCE_LIBRARY_URL" `
  --license-name "SOURCE_LIBRARY_LICENSE" `
  --license-url "SOURCE_LIBRARY_LICENSE_URL"
```

The reviewed stage validates the map's locale, source dataset, and exact source
content version. For `zh-Hant` it also refuses to emit artifacts if even one
source item or localized field is missing. Repeat these two commands for the
five exported wordbooks, three sentence datasets, and all five article
datasets, using a unique locale-scoped library ID for each dataset. Inspect the
complete artifacts before using the normal publisher; do not install OpenCC on
the production request host. For articles, convert the 12-article aggregate
once, derive the four level reviewed-maps with `subset-reviewed-map` as shown
below, then run `reviewed` for all five `articles-graded*` datasets so the
aggregate and four level shelves remain separately selectable.

## 3. Build a WikDict word library

Use WikDict's language-pair database in the English-to-target direction. The
adapter reads the database in immutable read-only mode and selects the sense
closest to the project's English definition.

```powershell
python tools/i18n_content_pipeline.py wikdict `
  --manifest build/i18n/source-manifest.json `
  --source-dataset words-cet4 `
  --output-dataset wordbook-common `
  --locale ja `
  --output-dir build/i18n `
  --library-id ja:words-common `
  --name "英日常用詞典" `
  --description "CET-4 English headwords with Japanese meanings" `
  --sqlite build/sources/en-ja.sqlite3 `
  --source-url https://download.wikdict.com/dictionaries/sqlite/2_2026-06/en-ja.sqlite3
```

WikDict currently supplies `en-ja`, `en-fr`, `en-es`, `en-pt`, and `en-ru`.
Its download page describes the data as CC BY-SA. Keep the generated
attribution/provenance files with the release.

For Korean, the preferred downloaded source is Open English-Korean Dictionary.
The adapter detects its `dict/words.json` and `dict/word_dictionary.sqlite`
formats automatically:

```powershell
python tools/i18n_content_pipeline.py korean-dict `
  --manifest build/i18n/source-manifest.json `
  --source-dataset words-cet4 `
  --output-dataset wordbook-common `
  --locale ko `
  --output-dir build/i18n `
  --library-id ko:words-common `
  --name "영한 상용 사전" `
  --description "CET-4 English headwords with Korean meanings" `
  --source build/sources/open-english-korean-dict/dict/words.json
```

Use the SQLite file in the same `--source` argument if preferred. The combined
dictionary is CC BY-SA 4.0; preserve the generated source URL and attribution,
and apply its ShareAlike requirement to redistributed adaptations.

For Thai, the preferred downloaded source is Yaitron. Both the actual NDJSON
and TEI distributions are supported:

```powershell
python tools/i18n_content_pipeline.py yaitron `
  --manifest build/i18n/source-manifest.json `
  --source-dataset words-cet4 `
  --output-dataset wordbook-common `
  --locale th `
  --output-dir build/i18n `
  --library-id th:words-common `
  --name "พจนานุกรมอังกฤษ-ไทย" `
  --description "CET-4 English headwords with Thai meanings" `
  --source build/sources/Yaitron/data/yaitron.ndjson
```

Replace the source with `data/yaitron.tei` to use TEI. Only entries whose
headword language is English and translation language is Thai are imported.
Yaitron inherits the custom LEXiTRON terms; its full license/disclaimer must be
retained and every redistributed derived product must show this exact notice:

> This product is created by the adaptation of LEXiTRON developed by NECTEC
> (http://www.nectec.or.th/).

Do not name the derived library LEXiTRON. The notice is also copied into each
generated provenance record.

Kaikki/Wiktionary remains an optional Korean/Thai fallback adapter:

```powershell
python tools/i18n_content_pipeline.py kaikki `
  --manifest build/i18n/source-manifest.json `
  --source-dataset words-cet4 `
  --output-dataset wordbook-common `
  --locale ko `
  --output-dir build/i18n `
  --library-id ko:words-common `
  --name "영한 상용 사전" `
  --jsonl build/sources/kowiktionary-English.jsonl.gz `
  --source-url https://kaikki.org/kowiktionary/
```

Kaikki output inherits the selected Wiktionary edition's CC BY-SA 4.0/GFDL
terms; it must not be labelled with the separate WikDict license.

The `freedict` command accepts an extracted TEI file. Supply that individual
dictionary's exact license name and URL: FreeDict intentionally stores license
information per dictionary in the TEI header, so a blanket FreeDict license
must not be assumed.

## 4. Build a Tatoeba sentence library

For a new independent language shelf, use `tatoeba-direct`. It does not read a
manifest or consult any Chinese sentence library. It deterministically selects
exactly 1,000 direct English–target-language pairs from the three official
exports by default, keeps the lowest valid target ID for each English ID,
normalizes and deduplicates both sides, filters malformed/unsafe study text,
and fails without writing a publishable bundle when fewer than the requested
number remain.

```powershell
python tools/i18n_content_pipeline.py tatoeba-direct `
  --output-dataset sentences-common `
  --locale ja `
  --output-dir build/i18n `
  --library-id ja:sentences-common `
  --source-library-id tatoeba-eng-jpn `
  --name "英日例文集" `
  --description "Direct English–Japanese sentence pairs from Tatoeba" `
  --english-sentences build/sources/eng_sentences.tsv.bz2 `
  --links build/sources/eng-jpn_links.tsv.bz2 `
  --target-sentences build/sources/jpn_sentences.tsv.bz2 `
  --target-count 1000
```

Every output uses the real positive English sentence ID as `itemKey` and keeps
`sourceIds: [englishId, targetId]`. Provenance records all three SHA-256 input
fingerprints and both sentence-page URLs per item. Catalog attribution names
Tatoeba contributors and carries the CC BY 2.0 FR notice. This license applies
to text exports, not to independently licensed Tatoeba audio.

The older `tatoeba` command remains for the narrower compatibility workflow of
finding target translations for sentences already present in a project
manifest:

The builder chooses the lowest target sentence ID when an English sentence has
multiple direct translations. That rule is simple, deterministic, and auditable;
the result still needs language-quality review before publishing.

```powershell
python tools/i18n_content_pipeline.py tatoeba `
  --manifest build/i18n/source-manifest.json `
  --source-dataset sentences-tatoeba-basic `
  --output-dataset sentences-common `
  --locale ja `
  --output-dir build/i18n `
  --library-id ja:sentences-common `
  --name "英日例文集" `
  --links build/sources/eng-jpn_links.tsv.bz2 `
  --target-sentences build/sources/jpn_sentences.tsv.bz2 `
  --description "Direct English–Japanese sentence pairs from Tatoeba"
```

Official pair files are under
`https://downloads.tatoeba.org/exports/per_language/eng/` and target sentence
tables under `https://downloads.tatoeba.org/exports/per_language/<code>/`.
Codes are `jpn`, `kor`, `fra`, `spa`, `por`, `rus`, `tha`, and `ara`.
Tatoeba text/link exports use CC BY 2.0 FR unless a specifically marked CC0
export is selected; retain both sentence IDs for attribution.

If a project sentence lacks `sourceIds`, add the official
`eng_sentences.tsv.bz2` with `--english-sentences`; the adapter then performs an
exact normalised English-text match before joining the pair file.

## 5. Pre-generate article translations with Argos

The optional `argos-translate` stage loads an already installed direct
English-to-target Argos package on the development host. Run it once for the
12-article aggregate. It translates titles, summaries, level labels, genres,
topics, and sentences to a reviewed-map file that the next stage consumes
directly. It never downloads or publishes a model package.

```powershell
python tools/i18n_content_pipeline.py argos-translate `
  --manifest build/i18n/source-manifest.json `
  --source-dataset articles-graded `
  --locale ja `
  --output build/reviewed/articles-ja.json `
  --checkpoint-dir build/i18n/.translation-state `
  --batch-size 16
```

Derive each smaller article shelf without translating repeated articles again:

```powershell
python tools/i18n_content_pipeline.py subset-reviewed-map `
  --manifest build/i18n/source-manifest.json `
  --source-dataset articles-graded `
  --target-dataset articles-graded-junior-basic `
  --source-reviewed-map build/reviewed/articles-ja.json `
  --output build/reviewed/articles-junior-basic-ja.json
```

Repeat only the derivation for `articles-graded-junior-advanced`,
`articles-graded-senior-basic`, and `articles-graded-senior-advanced`.
The command accepts only a non-empty strict article subset. Before writing, it
requires the aggregate reviewed-map to have exact full-field coverage and
verifies every target item key, field, source language, source text hash and
source content version against the aggregate manifest entry. The derived map
uses the target dataset's own content version and is therefore accepted by the
existing fail-closed `reviewed` stage. The same derivation works for an
aggregate `zh-Hant` OpenCC map, using its exact `zh-Hans` source hashes.

The final output is written atomically only after every field succeeds. Batch
checkpoints contain the source hashes and completed translations, so the same
command resumes after interruption. The output records the installed Argos
application and language-package versions. Because the current article source
has no authored English summaries, export transparently marks the first English
sentence as an extractive `summaryEn` source; review or replace those summaries
before release.

Model licensing is separate from the Argos application license. Keep models on
the development host and verify the individual package license before using
its generated content commercially.

## 6. Materialise reviewed article or fallback translations

The `reviewed` command consumes a JSON map with the same shape as the public
bundle `items` object. It refuses to materialise a partially translated item,
so a foreign-language library cannot silently display Chinese for missing
fields.

```json
{
  "items": {
    "junior-basic-library-card": {
      "title": "…",
      "summary": "…",
      "level": "…",
      "genre": "…",
      "topic": "…",
      "sentences": {"0": "…", "1": "…"}
    }
  }
}
```

```powershell
python tools/i18n_content_pipeline.py reviewed `
  --manifest build/i18n/source-manifest.json `
  --source-dataset articles-graded `
  --output-dataset articles-graded `
  --locale ja `
  --output-dir build/i18n `
  --library-id ja:articles-graded `
  --name "レベル別英語リーディング" `
  --description "12 graded English articles with sentence translations" `
  --translations build/reviewed/articles-ja.json `
  --provider offline-reviewed `
  --model <pinned-model-name>
```

For Argos fallback, record the exact model/version in `--model`. Do not
redistribute an `.argosmodel` merely because the Argos application code is
MIT/CC0: several language packages still lack an explicit model license. Run
those packages only on the development host until their individual license is
confirmed. Repeat the reviewed command with the matching stable
`articles-graded*` source/output dataset, its aggregate or derived reviewed-map,
and locale-scoped library ID; the five commands merge into one locale catalog
while retaining five distinct books.

## 7. Validate and publish one library

First validate the exact production plan without credentials or network
writes:

```powershell
python tools/i18n_content_pipeline.py publish `
  --output-dir build/i18n `
  --locale ja `
  --library-id ja:articles-graded `
  --api-base https://api-enplay.aoke.ltd `
  --dry-run
```

Then place the token in an environment variable and run the same target:

```powershell
$env:ENPLAY_ADMIN_TOKEN = "<admin token>"
python tools/i18n_content_pipeline.py publish `
  --output-dir build/i18n `
  --locale ja `
  --library-id ja:articles-graded `
  --api-base https://api-enplay.aoke.ltd
```

For the private 103 development host, use
`--api-base http://192.168.0.103/api --allow-http`; never copy that HTTP target
into the Singapore production command.

The builder validates every target library and all counts, keys, positions and
payload limits before writing a replacement bundle. A zero-item or inconsistent
rebuild fails closed and invalidates that library's previous draft, ready, item
batch, build-checkpoint and publish-checkpoint artifacts, so an old successful
plan cannot be mistaken for the failed rebuild.

The publisher then binds the admin artifacts to the current complete build
checkpoint and verifies the bundle fingerprint, item payloads, positions,
locale, library and content version before sending anything. It POSTs the draft
catalog, every 100-item batch, then the ready catalog. A publish checkpoint is
saved after each successful request; retrying resumes at the first unfinished
step. If the API returns `429`, the publisher honors `Retry-After` and retries
that exact request without advancing the checkpoint. By default it permits
five rate-limit retries for one step and at most 600 seconds of cumulative
waiting per run; `--rate-limit-retries` and `--rate-limit-wait-limit` can lower
or raise those bounds for a deliberately throttled endpoint. Other failures
stop the run. Tokens are never included in output or checkpoints. Plain HTTP
is rejected except for loopback; use `--allow-http` only for a trusted private
development endpoint. Use `--restart` only when intentionally replaying the
whole idempotent sequence.

## Verification

```powershell
python -m py_compile tools/i18n_content_pipeline.py
python -m unittest tests.test_i18n_content_pipeline -v
```

Before a production import, inspect every coverage report, retain the source
checksums and license files, review a stratified sample in each language, then
POST the generated admin files in this order: catalog draft, all library-item
batches, optional field-audit batches, catalog ready.

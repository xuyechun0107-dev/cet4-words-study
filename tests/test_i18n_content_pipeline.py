import bz2
import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "tools" / "i18n_content_pipeline.py"
SPEC = importlib.util.spec_from_file_location("i18n_content_pipeline", MODULE_PATH)
pipeline = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = pipeline
SPEC.loader.exec_module(pipeline)


class SourceManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = pipeline.build_source_manifest(PROJECT_ROOT)

    def test_extracts_every_builtin_content_type(self):
        datasets = {item["dataset"]: item for item in self.manifest["datasets"]}
        self.assertEqual(datasets["words-cet4"]["itemCount"], 4123)
        self.assertEqual(datasets["sentences-daily"]["itemCount"], 429)
        self.assertEqual(datasets["sentences-tatoeba-basic"]["itemCount"], 1000)
        self.assertEqual(datasets["sentences-tatoeba-intermediate"]["itemCount"], 1000)
        self.assertEqual(datasets["articles-graded"]["itemCount"], 12)
        self.assertEqual(datasets["articles-graded"]["segmentCount"], 203)
        article_dataset_ids = set(pipeline.ARTICLE_SOURCE_DATASETS.values())
        self.assertTrue(article_dataset_ids.issubset(datasets))
        self.assertEqual(
            {
                dataset_id: datasets[dataset_id]["itemCount"]
                for dataset_id in article_dataset_ids
            },
            {
                "articles-graded": 12,
                "articles-graded-junior-basic": 3,
                "articles-graded-junior-advanced": 3,
                "articles-graded-senior-basic": 3,
                "articles-graded-senior-advanced": 3,
            },
        )
        article_libraries = {
            library["id"]: library
            for library in self.manifest["libraries"]
            if library["type"] == "articles"
        }
        self.assertEqual(set(article_libraries), set(pipeline.ARTICLE_SOURCE_DATASETS))
        for source_library_id, dataset_id in pipeline.ARTICLE_SOURCE_DATASETS.items():
            self.assertEqual(article_libraries[source_library_id]["dataset"], dataset_id)
            self.assertEqual(datasets[dataset_id]["sourceLibraryId"], source_library_id)
            keys = [item["itemKey"] for item in datasets[dataset_id]["items"]]
            self.assertEqual(len(keys), len(set(keys)))
        aggregate_keys = {
            item["itemKey"] for item in datasets["articles-graded"]["items"]
        }
        tier_keys = {
            item["itemKey"]
            for dataset_id in article_dataset_ids - {"articles-graded"}
            for item in datasets[dataset_id]["items"]
        }
        self.assertEqual(aggregate_keys, tier_keys)
        daily_keys = [
            item["itemKey"] for item in datasets["sentences-daily"]["items"]
        ]
        self.assertEqual(len(daily_keys), len(set(daily_keys)))
        self.assertIn("this tastes delicious!", daily_keys)
        self.assertIn("this tastes delicious!#duplicate-2", daily_keys)
        for dataset_id in (
            "sentences-tatoeba-basic",
            "sentences-tatoeba-intermediate",
        ):
            source_keys = [item["itemKey"] for item in datasets[dataset_id]["items"]]
            self.assertEqual(len(source_keys), len(set(source_keys)))
            self.assertTrue(all(key.isdigit() and int(key) > 0 for key in source_keys))

    def test_manifest_is_deterministic_and_preserves_source_languages(self):
        rebuilt = pipeline.build_source_manifest(PROJECT_ROOT)
        self.assertEqual(self.manifest, rebuilt)
        words = pipeline.get_dataset(self.manifest, "words-cet4")
        sources = words["items"][0]["fields"]["definition"]["sources"]
        self.assertEqual(set(sources), {"en", "zh-Hans"})
        for source in sources.values():
            self.assertEqual(source["sourceHash"], pipeline.sha256_text(source["text"]))
        articles = pipeline.get_dataset(self.manifest, "articles-graded")
        summary_sources = articles["items"][0]["fields"]["summary"]["sources"]
        self.assertIn("en", summary_sources)
        self.assertEqual(
            summary_sources["en"]["sourceField"],
            "sentences.en[0] (extractive summary)",
        )
        article = articles["items"][0]
        self.assertEqual(article["payload"]["levelEn"], "Lower Secondary Foundation · A2")
        self.assertEqual(article["payload"]["genreEn"], "Short Listening Passage")
        self.assertEqual(article["payload"]["topicEn"], "People and Society")
        for field in ("level", "genre", "topic"):
            self.assertIn("en", article["fields"][field]["sources"])
            self.assertIn("zh-Hans", article["fields"][field]["sources"])

    def test_remote_wordbook_json_is_supported(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            wordbook = Path(temporary_directory) / "cet6.json"
            wordbook.write_text(
                json.dumps(
                    {
                        "slug": "cet6",
                        "name": "CET-6",
                        "source_name": "fixture",
                        "source_url": "https://example.invalid/source",
                        "license_name": "CC0",
                        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                        "items": [
                            {
                                "word": "example",
                                "phonetic": "/ɪɡˈzɑːmpəl/",
                                "definition": "例子",
                                "definition_en": "something used to explain an idea",
                                "example": "This is an example.",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            manifest = pipeline.build_source_manifest(PROJECT_ROOT, [str(wordbook)])
            dataset = pipeline.get_dataset(manifest, "wordbook-cet6")
            self.assertEqual(dataset["sourceLibraryId"], "remote-cet6")
            self.assertEqual(dataset["items"][0]["itemKey"], "example")

    def test_remote_wordbook_without_english_definition_fails_before_generation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            wordbook = Path(temporary_directory) / "invalid.json"
            wordbook.write_text(
                json.dumps(
                    {
                        "slug": "invalid",
                        "items": [{"word": "example", "definition": "例子"}],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                pipeline.PipelineError,
                "needs a non-empty definition_en/definitionEn",
            ):
                pipeline.build_source_manifest(PROJECT_ROOT, [str(wordbook)])


class AdapterTests(unittest.TestCase):
    def test_wikdict_selects_the_closest_sense_and_builds_complete_payload(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            database = temporary / "en-ja.sqlite3"
            connection = sqlite3.connect(database)
            connection.execute(
                "CREATE TABLE translation (lexentry, sense_num, sense, written_rep TEXT, "
                "trans_list, score, is_good, importance)"
            )
            connection.execute(
                "CREATE TABLE simple_translation "
                "(written_rep TEXT, trans_list, max_score, rel_importance)"
            )
            connection.executemany(
                "INSERT INTO translation VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (None, 1, "river edge", "bank", "岸", 100, 1, 1),
                    (None, 2, "financial institution", "bank", "銀行", 100, 1, 1),
                ],
            )
            connection.commit()
            connection.close()

            source = pipeline.make_source("a financial institution", "en", "definition")
            manifest = {
                "datasets": [
                    {
                        "dataset": "words-cet4",
                        "type": "words",
                        "sourceLibraryId": "builtin-words",
                        "contentVersion": "source-v1",
                        "items": [
                            {
                                "itemKey": "bank",
                                "position": 0,
                                "payload": {
                                    "word": "bank",
                                    "phonetic": "/bæŋk/",
                                    "definitionEn": "a financial institution",
                                    "example": "I went to the bank.",
                                },
                                "fields": {
                                    "definition": pipeline.make_field_sources(source)
                                },
                            }
                        ],
                    }
                ]
            }
            output = temporary / "out"
            with pipeline.WikDictSQLiteAdapter(database) as adapter:
                report = pipeline.build_lexical_library(
                    manifest,
                    source_dataset_id="words-cet4",
                    output_dataset_id="wordbook-common",
                    locale="ja",
                    adapter=adapter,
                    output_dir=output,
                    library_id="ja:words-common",
                    name="英日常用詞典",
                    description="fixture",
                    source_url="https://example.invalid/en-ja.sqlite3",
                    license_info=pipeline.WIKDICT_LICENSE,
                )
            self.assertEqual(report["translated"], 1)
            bundle = json.loads(
                (output / "bundles" / "wordbook-common" / "ja.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(bundle["items"]["bank"]["definition"], "銀行")
            payload = bundle["content"][0]["payload"]
            self.assertEqual(payload["definitionLocalized"], "銀行")
            self.assertEqual(payload["definitionEn"], "a financial institution")
            self.assertNotIn("definitionZh", payload)
            self.assertNotIn("definition", payload)
            draft = json.loads(
                (
                    output
                    / "admin"
                    / "catalog"
                    / "ja"
                    / "ja-words-common.draft.json"
                ).read_text(encoding="utf-8")
            )
            ready = json.loads(
                (
                    output
                    / "admin"
                    / "catalog"
                    / "ja"
                    / "ja-words-common.ready.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(draft["libraries"][0]["status"], "draft")
            self.assertEqual(ready["libraries"][0]["status"], "ready")
            self.assertEqual(draft["contentVersion"], ready["contentVersion"])
            item_batch = json.loads(
                (
                    output
                    / "admin"
                    / "library-items"
                    / "ja"
                    / "ja-words-common"
                    / "0001.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(item_batch["libraryId"], "ja:words-common")
            self.assertRegex(item_batch["items"][0]["sourceHash"], r"^[0-9a-f]{64}$")

    def test_changed_library_identity_cannot_reuse_or_publish_old_checkpoint(self):
        class FixtureAdapter(pipeline.LexicalAdapter):
            provider = "fixture"
            source_name = "Fixture dictionary"

            def fingerprint(self):
                return {"provider": self.provider, "version": "stable"}

            def lookup(self, headword, english_definition=""):
                return pipeline.LookupResult(
                    text="livre",
                    provider=self.provider,
                    model="fixture-v1",
                    source_ref=f"fixture:{headword}",
                )

        source = pipeline.make_source("a written work", "en", "definition")
        manifest = {
            "datasets": [
                {
                    "dataset": "words-cet4",
                    "type": "words",
                    "sourceLibraryId": "builtin-words",
                    "contentVersion": "source-v1",
                    "items": [
                        {
                            "itemKey": "book",
                            "position": 0,
                            "payload": {
                                "word": "book",
                                "definitionEn": "a written work",
                            },
                            "fields": {
                                "definition": pipeline.make_field_sources(source)
                            },
                        }
                    ],
                }
            ]
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)
            common = {
                "manifest": manifest,
                "source_dataset_id": "words-cet4",
                "output_dataset_id": "wordbook-common",
                "locale": "fr",
                "adapter": FixtureAdapter(),
                "output_dir": output,
                "description": "fixture",
                "source_url": "https://example.invalid/dictionary",
                "license_info": pipeline.PROJECT_LICENSE,
            }
            first = pipeline.build_lexical_library(
                **common,
                library_id="fr:old-library",
                name="Old name",
            )
            self.assertEqual(first["translated"], 1)
            second = pipeline.build_lexical_library(
                **common,
                library_id="fr:new-library",
                name="New name",
            )
            self.assertEqual(second["translated"], 1)
            self.assertNotIn("skipped", second)
            self.assertFalse(
                (
                    output
                    / "admin"
                    / "catalog"
                    / "fr"
                    / "fr-old-library.ready.json"
                ).exists()
            )
            self.assertTrue(
                (
                    output
                    / "admin"
                    / "catalog"
                    / "fr"
                    / "fr-new-library.ready.json"
                ).is_file()
            )
            catalog = json.loads(
                (output / "catalog" / "fr.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                [item["id"] for item in catalog["libraries"]],
                ["fr:new-library"],
            )
            with self.assertRaisesRegex(
                pipeline.PipelineError,
                "Missing draft catalog artifact",
            ):
                pipeline.publish_library_artifacts(
                    output_dir=output,
                    locale="fr",
                    library_id="fr:old-library",
                    api_base="https://api.example.invalid",
                    dry_run=True,
                )
            new_plan = pipeline.publish_library_artifacts(
                output_dir=output,
                locale="fr",
                library_id="fr:new-library",
                api_base="https://api.example.invalid",
                dry_run=True,
            )
            self.assertEqual(new_plan["items"], 1)

    def test_kaikki_and_freedict_adapters_reserve_korean_thai_paths(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            kaikki = temporary / "ko.jsonl"
            kaikki.write_text(
                json.dumps(
                    {"word": "book", "senses": [{"glosses": ["책", "서적"]}]},
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            result = pipeline.KaikkiJsonlAdapter(kaikki, ["book"]).lookup("book")
            self.assertIsNotNone(result)
            self.assertIn("책", result.text)

            tei = temporary / "eng-tha.tei"
            tei.write_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
                <entry><form><orth>book</orth></form><sense>
                <cit type="trans"><quote>หนังสือ</quote></cit></sense></entry>
                </body></text></TEI>""",
                encoding="utf-8",
            )
            result = pipeline.FreeDictTeiAdapter(tei, ["book"]).lookup("book")
            self.assertIsNotNone(result)
            self.assertEqual(result.text, "หนังสือ")

    def test_open_english_korean_adapter_reads_json_and_sqlite(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            json_path = temporary / "words.json"
            json_path.write_text(
                json.dumps(
                    {
                        "book": {
                            "meaning_ko": "책, 서적",
                            "meaning_en": "a written work",
                            "ipa": "/bʊk/",
                            "pos": "noun",
                            "cefr": "A1",
                            "freq_rank": 101,
                        },
                        "words": {
                            "meaning_ko": "단어들",
                            "meaning_en": "more than one word",
                        },
                        "unused": {"meaning_ko": "사용하지 않음"},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with pipeline.OpenEnglishKoreanAdapter(json_path, ["book", "words"]) as adapter:
                result = adapter.lookup("BOOK")
                self.assertIsNotNone(result)
                self.assertEqual(result.text, "책, 서적")
                self.assertEqual(result.provider, "open-english-korean-dict")
                self.assertEqual(result.details["cefr"], "A1")
                self.assertEqual(adapter.lookup("words").text, "단어들")
                self.assertIsNone(adapter.lookup("unused"))

            database = temporary / "word_dictionary.sqlite"
            connection = sqlite3.connect(database)
            connection.execute(
                "CREATE TABLE words (word TEXT PRIMARY KEY, meaning_ko TEXT NOT NULL, "
                "meaning_ja TEXT, meaning_zh TEXT, meaning_en TEXT, "
                "meaning_secondary TEXT, ipa TEXT, pos TEXT, cefr TEXT, freq_rank INTEGER)"
            )
            connection.execute(
                "INSERT INTO words VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    "book",
                    "책, 서적",
                    None,
                    None,
                    "a written work",
                    None,
                    "/bʊk/",
                    "noun",
                    "A1",
                    101,
                ),
            )
            connection.commit()
            connection.close()
            with pipeline.OpenEnglishKoreanAdapter(database, ["book"]) as adapter:
                result = adapter.lookup("Book")
                self.assertIsNotNone(result)
                self.assertEqual(result.text, "책, 서적")
                self.assertEqual(adapter.fingerprint()["format"], "sqlite")

    def test_yaitron_adapter_reads_ndjson_and_tei_english_thai_entries(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            ndjson = temporary / "yaitron.ndjson"
            rows = [
                {
                    "entry_id": 1,
                    "lang": "th",
                    "headword": "หนังสือ",
                    "translation": {"lang": "en", "text": "book"},
                },
                {
                    "entry_id": 40851,
                    "lang": "en",
                    "headword": "book",
                    "pos": "n",
                    "translation": {"lang": "th", "text": "หนังสือ"},
                    "similar_translations": [
                        {"lang": "th", "text": "ตำรา"}
                    ],
                },
                {
                    "entry_id": 40852,
                    "lang": "en",
                    "headword": "book",
                    "pos": "v",
                    "translation": {"lang": "th", "text": "จอง"},
                },
            ]
            ndjson.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                encoding="utf-8",
            )
            result = pipeline.YaitronAdapter(ndjson, ["book"]).lookup("BOOK")
            self.assertIsNotNone(result)
            self.assertEqual(result.text, "หนังสือ；ตำรา；จอง")
            self.assertEqual(result.details["acknowledgement"], pipeline.YAITRON_ACKNOWLEDGEMENT)

            tei = temporary / "yaitron.tei"
            tei.write_text(
                """<?xml version="1.0" encoding="UTF-8"?>
                <TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
                <entry xml:lang="th"><form><orth>หนังสือ</orth></form>
                <cit type="translation" xml:lang="en"><quote>book</quote></cit></entry>
                <entry xml:lang="en"><form><orth>book</orth></form><gramGrp><pos>n</pos></gramGrp>
                <cit type="translation" xml:lang="th"><quote>หนังสือ</quote></cit>
                <cit type="translation" subtype="similar" xml:lang="th"><quote>ตำรา</quote></cit>
                </entry></body></text></TEI>""",
                encoding="utf-8",
            )
            result = pipeline.YaitronAdapter(tei, ["book"]).lookup("book")
            self.assertIsNotNone(result)
            self.assertEqual(result.text, "หนังสือ；ตำรา")
            self.assertEqual(result.details["partsOfSpeech"], ["n"])

    def test_tatoeba_direct_pair_is_deterministic_and_resumable(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            links = temporary / "eng-fra_links.tsv.bz2"
            targets = temporary / "fra_sentences.tsv.bz2"
            with bz2.open(links, "wt", encoding="utf-8") as handle:
                handle.write("10\t200\n10\t100\n20\t300\n")
            with bz2.open(targets, "wt", encoding="utf-8") as handle:
                handle.write("100\tfra\tBonjour.\n200\tfra\tSalut.\n300\tfra\tMerci.\n")

            manifest = {
                "datasets": [
                    {
                        "dataset": "sentences-tatoeba-basic",
                        "type": "sentences",
                        "sourceLibraryId": "builtin-sentences-tatoeba-basic",
                        "contentVersion": "source-v1",
                        "items": [
                            {
                                "itemKey": "10",
                                "position": 0,
                                "payload": {"scene": "greetings", "text": "Hello."},
                                "fields": {
                                    "translation": pipeline.make_field_sources(
                                        pipeline.make_source("Hello.", "en", "text")
                                    )
                                },
                            },
                            {
                                "itemKey": "20",
                                "position": 1,
                                "payload": {"scene": "greetings", "text": "Thanks."},
                                "fields": {
                                    "translation": pipeline.make_field_sources(
                                        pipeline.make_source("Thanks.", "en", "text")
                                    )
                                },
                            },
                        ],
                    }
                ]
            }
            output = temporary / "out"
            arguments = dict(
                source_dataset_id="sentences-tatoeba-basic",
                output_dataset_id="sentences-common",
                locale="fr",
                links_path=links,
                target_sentences_path=targets,
                output_dir=output,
                library_id="fr:sentences-common",
                name="Phrases anglaises–françaises",
                description="fixture",
            )
            first = pipeline.build_tatoeba_library(manifest, **arguments)
            bundle_path = output / "bundles" / "sentences-common" / "fr.json"
            first_bytes = bundle_path.read_bytes()
            second = pipeline.build_tatoeba_library(manifest, **arguments)
            self.assertEqual(first["translated"], 2)
            self.assertTrue(second["skipped"])
            self.assertEqual(first_bytes, bundle_path.read_bytes())
            bundle = json.loads(first_bytes)
            self.assertEqual(bundle["items"]["10"]["translation"], "Bonjour.")
            self.assertEqual(
                bundle["content"][0]["payload"]["translationLocalized"], "Bonjour."
            )
            self.assertEqual(bundle["content"][0]["payload"]["sourceIds"], [10, 100])


class TatoebaDirectTests(unittest.TestCase):
    @staticmethod
    def _write_rows(path, rows):
        with bz2.open(path, "wt", encoding="utf-8") as handle:
            for row in rows:
                handle.write("\t".join(str(value) for value in row) + "\n")

    def test_direct_selection_is_order_independent_deduplicated_and_filtered(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            english = temporary / "eng.tsv.bz2"
            targets = temporary / "fra.tsv.bz2"
            links_a = temporary / "links-a.tsv.bz2"
            links_b = temporary / "links-b.tsv.bz2"
            self._write_rows(
                english,
                [
                    (60, "eng", "Another useful sentence."),
                    (30, "eng", "Hello there."),
                    (20, "eng", "Please sit down."),
                    (10, "eng", "Hello there."),
                    (50, "eng", "This is valid."),
                    (40, "eng", "Visit https://example.com now."),
                ],
            )
            self._write_rows(
                targets,
                [
                    (600, "fra", "Encore une phrase utile."),
                    (500, "fra", "这是中文。"),
                    (400, "fra", "Bonjour à vous."),
                    (300, "fra", "Veuillez vous asseoir."),
                    (200, "fra", "Salut à tous."),
                    (100, "fra", "Bonjour à vous."),
                ],
            )
            links = [
                (60, 600),
                (10, 200),
                (50, 100),
                (20, 300),
                (30, 400),
                (10, 100),
                (40, 200),
                (60, 500),
                (10, 100),
            ]
            self._write_rows(links_a, links)
            self._write_rows(links_b, reversed(links))

            first, first_report = pipeline.select_tatoeba_direct_pairs(
                english,
                links_a,
                targets,
                locale="fr",
                target_count=3,
            )
            second, second_report = pipeline.select_tatoeba_direct_pairs(
                english,
                links_b,
                targets,
                locale="fr",
                target_count=3,
            )

            self.assertEqual(first, second)
            self.assertEqual(
                [(item["englishId"], item["targetId"]) for item in first],
                [(10, 100), (20, 300), (60, 600)],
            )
            self.assertEqual(first_report["duplicateLinks"], 1)
            self.assertEqual(first_report, second_report)
            self.assertGreaterEqual(first_report["filteredPairs"], 1)
            with self.assertRaisesRegex(pipeline.PipelineError, "4 are required"):
                pipeline.select_tatoeba_direct_pairs(
                    english,
                    links_a,
                    targets,
                    locale="fr",
                    target_count=4,
                )

    def test_direct_builder_defaults_to_exactly_1000_publishable_pairs(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            english = temporary / "eng.tsv.bz2"
            targets = temporary / "fra.tsv.bz2"
            links = temporary / "links.tsv.bz2"
            total = 1005
            self._write_rows(
                english,
                [
                    (index, "eng", f"This is useful sentence number {index}.")
                    for index in range(1, total + 1)
                ],
            )
            self._write_rows(
                targets,
                [
                    (10000 + index, "fra", f"Ceci est la phrase utile numéro {index}.")
                    for index in range(1, total + 1)
                ],
            )
            self._write_rows(
                links,
                [
                    (index, 10000 + index)
                    for index in range(total, 0, -1)
                ],
            )
            output = temporary / "out"
            arguments = {
                "output_dataset_id": "sentences-common",
                "locale": "fr",
                "english_sentences_path": english,
                "links_path": links,
                "target_sentences_path": targets,
                "output_dir": output,
                "library_id": "fr:sentences-common",
                "name": "Phrases anglaises–françaises",
                "description": "fixture",
            }

            first = pipeline.build_tatoeba_direct_library(**arguments)
            bundle_path = output / "bundles" / "sentences-common" / "fr.json"
            first_bytes = bundle_path.read_bytes()
            second = pipeline.build_tatoeba_direct_library(**arguments)

            self.assertEqual(first["materializedItems"], 1000)
            self.assertTrue(second["skipped"])
            self.assertEqual(first_bytes, bundle_path.read_bytes())
            bundle = json.loads(first_bytes)
            self.assertEqual(len(bundle["content"]), 1000)
            self.assertEqual(bundle["content"][0]["itemKey"], "1")
            self.assertEqual(bundle["content"][-1]["itemKey"], "1000")
            self.assertTrue(
                all(
                    item["payload"]["sourceIds"]
                    == [int(item["itemKey"]), 10000 + int(item["itemKey"])]
                    for item in bundle["content"]
                )
            )
            self.assertNotRegex(
                json.dumps(bundle["content"], ensure_ascii=False),
                r"[\u3400-\u9fff]",
            )
            batches = sorted(
                (
                    output
                    / "admin"
                    / "library-items"
                    / "fr"
                    / "fr-sentences-common"
                ).glob("*.json")
            )
            self.assertEqual(len(batches), 10)
            self.assertTrue(
                all(
                    len(json.loads(path.read_text(encoding="utf-8"))["items"]) == 100
                    for path in batches
                )
            )
            catalog = json.loads(
                (
                    output
                    / "admin"
                    / "catalog"
                    / "fr"
                    / "fr-sentences-common.ready.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(
                catalog["libraries"][0]["sourceLibraryId"],
                "tatoeba-eng-fra",
            )
            self.assertIn("Tatoeba", catalog["libraries"][0]["license"]["notice"])
            provenance = json.loads(
                (
                    output
                    / "provenance"
                    / "sentences-common"
                    / "fr.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(
                provenance["policyVersion"], pipeline.TATOEBA_DIRECT_POLICY_VERSION
            )
            self.assertEqual(len(provenance["items"]), 1000)
            self.assertTrue(provenance["items"][0]["englishUrl"].endswith("/1"))
            for input_name in ("englishSentences", "links", "targetSentences"):
                self.assertEqual(len(provenance["inputs"][input_name]["sha256"]), 64)

            parsed = pipeline.build_parser().parse_args(
                [
                    "tatoeba-direct",
                    "--locale",
                    "fr",
                    "--output-dir",
                    str(output),
                    "--library-id",
                    "fr:sentences-common",
                    "--name",
                    "fixture",
                    "--english-sentences",
                    str(english),
                    "--links",
                    str(links),
                    "--target-sentences",
                    str(targets),
                ]
            )
            self.assertEqual(parsed.target_count, 1000)
            self.assertFalse(hasattr(parsed, "manifest"))


class ReviewedArticleTests(unittest.TestCase):
    def test_all_five_article_shelves_materialize_as_independent_datasets(self):
        manifest = pipeline.build_source_manifest(PROJECT_ROOT)
        output_datasets = set(pipeline.ARTICLE_SOURCE_DATASETS.values())
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            output = temporary / "out"
            expected_counts = {}
            for source_library_id, dataset_id in pipeline.ARTICLE_SOURCE_DATASETS.items():
                dataset = pipeline.get_dataset(manifest, dataset_id)
                expected_counts[dataset_id] = dataset["itemCount"]
                localized_items = {}
                for item in dataset["items"]:
                    localized = {"sentences": {}}
                    for field_name in item["fields"]:
                        value = f"localized {dataset_id} {item['itemKey']} {field_name}"
                        if field_name.startswith("sentences."):
                            localized["sentences"][field_name.split(".", 1)[1]] = value
                        else:
                            localized[field_name] = value
                    localized_items[item["itemKey"]] = localized
                translations = temporary / f"{dataset_id}.json"
                translations.write_text(
                    json.dumps({"items": localized_items}, ensure_ascii=False),
                    encoding="utf-8",
                )
                report = pipeline.build_reviewed_translation_libraries(
                    manifest,
                    source_dataset_id=dataset_id,
                    output_dataset_id=dataset_id,
                    locale="fr",
                    translations_path=translations,
                    output_dir=output,
                    library_id=f"fr:{dataset_id}",
                    name=f"Localized {dataset_id}",
                    description="fixture",
                    provider="reviewed-offline",
                    model="fixture",
                    source_url="",
                    license_info=pipeline.PROJECT_LICENSE,
                )
                self.assertEqual(report["materializedItems"], dataset["itemCount"])

            catalog = json.loads(
                (output / "catalog" / "fr.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(catalog["libraries"]), 5)
            self.assertEqual(
                {library["dataset"] for library in catalog["libraries"]},
                output_datasets,
            )
            self.assertEqual(
                {library["sourceLibraryId"] for library in catalog["libraries"]},
                set(pipeline.ARTICLE_SOURCE_DATASETS),
            )
            self.assertEqual(
                [library["sourceLibraryId"] for library in catalog["libraries"]],
                list(pipeline.ARTICLE_SOURCE_DATASETS),
            )
            self.assertEqual(
                [library["displayOrder"] for library in catalog["libraries"]],
                [300, 301, 302, 303, 304],
            )
            for source_library_id, dataset_id in pipeline.ARTICLE_SOURCE_DATASETS.items():
                bundle = json.loads(
                    (output / "bundles" / dataset_id / "fr.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(len(bundle["content"]), expected_counts[dataset_id])
                self.assertTrue(
                    all(
                        item["payload"]["sourceLibraryId"] == source_library_id
                        for item in bundle["content"]
                    )
                )
                self.assertNotRegex(
                    json.dumps(bundle["content"], ensure_ascii=False),
                    r"[\u3400-\u9fff]",
                )

    def test_articles_are_one_locale_library_with_no_chinese_runtime_fallback(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            title_source = pipeline.make_source("A Test", "en", "title")
            summary_source_en = pipeline.make_source("A summary.", "en", "summaryEn")
            summary_source_zh = pipeline.make_source("测试摘要", "zh-Hans", "summary")
            sentence_source = pipeline.make_source("A sentence.", "en", "sentences.en")
            level_source = pipeline.make_source(
                "Lower Secondary Foundation · A2", "en", "levelCanonicalEn"
            )
            genre_source = pipeline.make_source(
                "Narrative", "en", "genreCanonicalEn"
            )
            topic_source = pipeline.make_source(
                "People and Society", "en", "topicCanonicalEn"
            )
            manifest = {
                "libraries": [
                    {"id": "builtin-articles-a2", "type": "articles", "name": "A2"}
                ],
                "datasets": [
                    {
                        "dataset": "articles-graded",
                        "type": "articles",
                        "sourceLibraryId": "builtin-articles",
                        "contentVersion": "source-v1",
                        "items": [
                            {
                                "itemKey": "a-test",
                                "position": 0,
                                "sourceLibraryId": "builtin-articles-a2",
                                "payload": {
                                    "id": "a-test",
                                    "title": "A Test",
                                    "titleZh": "一个测试",
                                    "summaryZh": "测试摘要",
                                    "level": "中考基础 · A2",
                                    "levelEn": "Lower Secondary Foundation · A2",
                                    "genre": "记叙文",
                                    "genreEn": "Narrative",
                                    "topic": "人与社会",
                                    "topicEn": "People and Society",
                                    "sentences": [{"en": "A sentence.", "zh": "一个句子。"}],
                                },
                                "fields": {
                                    "title": pipeline.make_field_sources(title_source),
                                    "summary": pipeline.make_field_sources(
                                        summary_source_en, summary_source_zh
                                    ),
                                    "level": pipeline.make_field_sources(level_source),
                                    "genre": pipeline.make_field_sources(genre_source),
                                    "topic": pipeline.make_field_sources(topic_source),
                                    "sentences.0": pipeline.make_field_sources(sentence_source),
                                },
                            }
                        ],
                    }
                ],
            }
            translations = temporary / "fr.json"
            translations.write_text(
                json.dumps(
                    {
                        "items": {
                            "a-test": {
                                "title": "Un test",
                                "summary": "Résumé du test",
                                "level": "Secondaire inférieur · A2",
                                "genre": "Récit",
                                "topic": "Personnes et société",
                                "sentences": {"0": "Une phrase."},
                            }
                        }
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            output = temporary / "out"
            report = pipeline.build_reviewed_translation_libraries(
                manifest,
                source_dataset_id="articles-graded",
                output_dataset_id="articles-graded",
                locale="fr",
                translations_path=translations,
                output_dir=output,
                library_id="fr:articles-graded",
                name="Lectures graduées",
                description="fixture",
                provider="reviewed-offline",
                model="fixture",
                source_url="",
                license_info=pipeline.PROJECT_LICENSE,
            )
            self.assertEqual(report["materializedItems"], 1)
            catalog = json.loads(
                (output / "catalog" / "fr.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(catalog["libraries"]), 1)
            bundle = json.loads(
                (output / "bundles" / "articles-graded" / "fr.json").read_text(
                    encoding="utf-8"
                )
            )
            payload = bundle["content"][0]["payload"]
            self.assertEqual(payload["title"], "A Test")
            self.assertEqual(payload["titleLocalized"], "Un test")
            self.assertEqual(payload["summaryLocalized"], "Résumé du test")
            self.assertEqual(payload["level"], "Lower Secondary Foundation · A2")
            self.assertEqual(payload["levelLocalized"], "Secondaire inférieur · A2")
            self.assertEqual(payload["genre"], "Narrative")
            self.assertEqual(payload["genreLocalized"], "Récit")
            self.assertEqual(payload["topic"], "People and Society")
            self.assertEqual(payload["topicLocalized"], "Personnes et société")
            self.assertEqual(
                payload["sentences"][0]["translationLocalized"], "Une phrase."
            )
            self.assertEqual(payload["sourceLibraryId"], "builtin-articles")
            self.assertEqual(
                payload["provenanceSourceLibraryId"], "builtin-articles-a2"
            )
            serialized = json.dumps(payload, ensure_ascii=False)
            self.assertNotIn("一个测试", serialized)
            self.assertNotIn("一个句子", serialized)
            self.assertNotRegex(serialized, r"[\u3400-\u9fff]")

    def test_all_eight_foreign_article_payloads_exclude_chinese_metadata(self):
        manifest = pipeline.build_source_manifest(PROJECT_ROOT)
        dataset = pipeline.get_dataset(manifest, "articles-graded")
        source_item = dataset["items"][0]
        item_key = source_item["itemKey"]
        localized_item = {"sentences": {}}
        for field_name in source_item["fields"]:
            translated = f"localized-{field_name}"
            if field_name.startswith("sentences."):
                localized_item["sentences"][field_name.split(".", 1)[1]] = translated
            else:
                localized_item[field_name] = translated

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            translations = temporary / "articles.json"
            translations.write_text(
                json.dumps({"items": {item_key: localized_item}}, ensure_ascii=False),
                encoding="utf-8",
            )
            for locale in ("ja", "ko", "fr", "es", "pt", "ru", "th", "ar"):
                output = temporary / locale
                report = pipeline.build_reviewed_translation_libraries(
                    manifest,
                    source_dataset_id="articles-graded",
                    output_dataset_id="articles-graded",
                    locale=locale,
                    translations_path=translations,
                    output_dir=output,
                    library_id=f"{locale}:articles-graded",
                    name=f"{locale} graded articles",
                    description="fixture",
                    provider="reviewed-offline",
                    model="fixture",
                    source_url="",
                    license_info=pipeline.PROJECT_LICENSE,
                )
                self.assertEqual(report["materializedItems"], 1)
                bundle = json.loads(
                    (output / "bundles" / "articles-graded" / f"{locale}.json").read_text(
                        encoding="utf-8"
                    )
                )
                payload = bundle["content"][0]["payload"]
                self.assertEqual(payload["level"], "Lower Secondary Foundation · A2")
                self.assertEqual(payload["genre"], "Short Listening Passage")
                self.assertEqual(payload["topic"], "People and Society")
                for field_name in (
                    "levelLocalized",
                    "genreLocalized",
                    "topicLocalized",
                ):
                    self.assertTrue(payload[field_name])
                self.assertNotRegex(
                    json.dumps(payload, ensure_ascii=False), r"[\u3400-\u9fff]"
                )


class ArgosArticleTests(unittest.TestCase):
    @staticmethod
    def _manifest():
        return {
            "datasets": [
                {
                    "dataset": "articles-graded",
                    "type": "articles",
                    "sourceLibraryId": "builtin-articles",
                    "contentVersion": "source-v1",
                    "items": [
                        {
                            "itemKey": "article-one",
                            "position": 0,
                            "payload": {"title": "A title", "sentences": []},
                            "fields": {
                                "title": pipeline.make_field_sources(
                                    pipeline.make_source("A title", "en", "title")
                                ),
                                "summary": pipeline.make_field_sources(
                                    pipeline.make_source("A summary.", "en", "summaryEn")
                                ),
                                "level": pipeline.make_field_sources(
                                    pipeline.make_source(
                                        "Lower Secondary Foundation · A2",
                                        "en",
                                        "levelCanonicalEn",
                                    )
                                ),
                                "genre": pipeline.make_field_sources(
                                    pipeline.make_source(
                                        "Narrative", "en", "genreCanonicalEn"
                                    )
                                ),
                                "topic": pipeline.make_field_sources(
                                    pipeline.make_source(
                                        "People and Society", "en", "topicCanonicalEn"
                                    )
                                ),
                                "sentences.0": pipeline.make_field_sources(
                                    pipeline.make_source(
                                        "A sentence.", "en", "sentences.en"
                                    )
                                ),
                            },
                        }
                    ],
                }
            ]
        }

    def test_argos_stage_resumes_batches_and_never_writes_partial_final_map(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            output = temporary / "articles-ja.json"
            translator_info = {
                "provider": "argos-translate",
                "applicationVersion": "1.2.3",
                "packageVersion": "4.5.6",
                "model": "fixture-en-ja",
            }
            failed_calls = []

            def failing_translator(text):
                failed_calls.append(text)
                if text == "A summary.":
                    raise RuntimeError("fixture interruption")
                return f"JA:{text}"

            with self.assertRaises(pipeline.PipelineError):
                pipeline.generate_argos_article_translations(
                    self._manifest(),
                    source_dataset_id="articles-graded",
                    locale="ja",
                    output_path=output,
                    checkpoint_dir=temporary / "state",
                    batch_size=1,
                    translator=failing_translator,
                    translator_info=translator_info,
                )
            self.assertFalse(output.exists())
            self.assertEqual(failed_calls, ["A title", "A summary."])

            resumed_calls = []

            def working_translator(text):
                resumed_calls.append(text)
                return f"JA:{text}"

            report = pipeline.generate_argos_article_translations(
                self._manifest(),
                source_dataset_id="articles-graded",
                locale="ja",
                output_path=output,
                checkpoint_dir=temporary / "state",
                batch_size=1,
                translator=working_translator,
                translator_info=translator_info,
            )
            self.assertEqual(
                resumed_calls,
                [
                    "A summary.",
                    "Lower Secondary Foundation · A2",
                    "Narrative",
                    "People and Society",
                    "A sentence.",
                ],
            )
            self.assertEqual(report["translatedThisRun"], 5)
            translated = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(translated["generator"]["model"], "fixture-en-ja")
            self.assertEqual(translated["items"]["article-one"]["title"], "JA:A title")
            self.assertEqual(
                translated["items"]["article-one"]["level"],
                "JA:Lower Secondary Foundation · A2",
            )
            self.assertEqual(
                translated["items"]["article-one"]["genre"], "JA:Narrative"
            )
            self.assertEqual(
                translated["items"]["article-one"]["topic"],
                "JA:People and Society",
            )
            self.assertEqual(
                translated["items"]["article-one"]["sentences"]["0"],
                "JA:A sentence.",
            )
            skipped = pipeline.generate_argos_article_translations(
                self._manifest(),
                source_dataset_id="articles-graded",
                locale="ja",
                output_path=output,
                checkpoint_dir=temporary / "state",
                batch_size=1,
                translator=working_translator,
                translator_info=translator_info,
            )
            self.assertTrue(skipped["skipped"])


class ReviewedSubsetMapTests(unittest.TestCase):
    @staticmethod
    def _write_aggregate_map(manifest, path, locale="fr"):
        dataset = pipeline.get_dataset(manifest, "articles-graded")
        items = {}
        for item in dataset["items"]:
            localized = {}
            for field_name, field_value in item["fields"].items():
                source = field_value["sources"]["en"]
                translated = f"FR:{source['text']}"
                if field_name.startswith("sentences."):
                    localized.setdefault("sentences", {})[
                        field_name.split(".", 1)[1]
                    ] = translated
                else:
                    localized[field_name] = translated
            items[item["itemKey"]] = localized
        payload = {
            "schemaVersion": pipeline.SCHEMA_VERSION,
            "kind": pipeline.REVIEWED_MAP_KIND,
            "locale": locale,
            "sourceDataset": "articles-graded",
            "sourceContentVersion": dataset["contentVersion"],
            "generator": {"provider": "fixture-translator", "model": "fixture-v1"},
            "items": items,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return payload

    def test_derives_complete_deterministic_shelf_map_without_retranslation(self):
        manifest = pipeline.build_source_manifest(PROJECT_ROOT)
        target_dataset_id = "articles-graded-junior-basic"
        target_dataset = pipeline.get_dataset(manifest, target_dataset_id)
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            aggregate_map = temporary / "articles-graded-fr.json"
            self._write_aggregate_map(manifest, aggregate_map)
            output = temporary / "junior-basic-fr.json"

            report = pipeline.derive_subset_reviewed_map(
                manifest,
                source_dataset_id="articles-graded",
                target_dataset_id=target_dataset_id,
                source_reviewed_map_path=aggregate_map,
                output_path=output,
            )
            self.assertEqual(report["items"], 3)
            self.assertEqual(report["translatedFields"], target_dataset["segmentCount"])
            derived = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(derived["sourceDataset"], target_dataset_id)
            self.assertEqual(
                derived["sourceContentVersion"], target_dataset["contentVersion"]
            )
            self.assertEqual(
                set(derived["items"]),
                {item["itemKey"] for item in target_dataset["items"]},
            )
            self.assertEqual(
                derived["generator"]["sourceReviewedMapSha256"],
                pipeline.sha256_file(aggregate_map),
            )
            tier_dataset_ids = set(pipeline.ARTICLE_SOURCE_DATASETS.values()) - {
                "articles-graded"
            }
            self.assertEqual(len(tier_dataset_ids), 4)
            for other_target_id in sorted(tier_dataset_ids - {target_dataset_id}):
                other_target = pipeline.get_dataset(manifest, other_target_id)
                other_report = pipeline.derive_subset_reviewed_map(
                    manifest,
                    source_dataset_id="articles-graded",
                    target_dataset_id=other_target_id,
                    source_reviewed_map_path=aggregate_map,
                    output_path=temporary / f"{other_target_id}-fr.json",
                )
                self.assertEqual(other_report["items"], other_target["itemCount"])
                self.assertEqual(
                    other_report["translatedFields"], other_target["segmentCount"]
                )

            repeated = pipeline.derive_subset_reviewed_map(
                manifest,
                source_dataset_id="articles-graded",
                target_dataset_id=target_dataset_id,
                source_reviewed_map_path=aggregate_map,
                output_path=output,
            )
            self.assertFalse(repeated["changed"])

            materialized = pipeline.build_reviewed_translation_libraries(
                manifest,
                source_dataset_id=target_dataset_id,
                output_dataset_id=target_dataset_id,
                locale="fr",
                translations_path=output,
                output_dir=temporary / "materialized",
                library_id="fr:articles-junior-basic",
                name="Articles collège · fondamentaux",
                description="fixture",
                provider="subset-reviewed-map",
                model="fixture-v1",
                source_url="https://example.invalid/articles",
                license_info=pipeline.PROJECT_LICENSE,
            )
            self.assertEqual(materialized["materializedItems"], 3)
            self.assertEqual(materialized["itemsWithMissingFields"], 0)

            parsed = pipeline.build_parser().parse_args(
                [
                    "subset-reviewed-map",
                    "--manifest",
                    "source.json",
                    "--target-dataset",
                    target_dataset_id,
                    "--source-reviewed-map",
                    "aggregate.json",
                    "--output",
                    "subset.json",
                ]
            )
            self.assertEqual(parsed.source_dataset, "articles-graded")
            self.assertEqual(parsed.target_dataset, target_dataset_id)

    def test_rejects_incomplete_map_and_changed_target_source_hash(self):
        manifest = pipeline.build_source_manifest(PROJECT_ROOT)
        target_dataset_id = "articles-graded-junior-basic"
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            aggregate_map = temporary / "articles-graded-fr.json"
            payload = self._write_aggregate_map(manifest, aggregate_map)
            first_item = next(iter(payload["items"].values()))
            first_item.pop("title")
            aggregate_map.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
            incomplete_output = temporary / "incomplete.json"
            with self.assertRaisesRegex(
                pipeline.PipelineError,
                "exactly cover the aggregate source fields",
            ):
                pipeline.derive_subset_reviewed_map(
                    manifest,
                    source_dataset_id="articles-graded",
                    target_dataset_id=target_dataset_id,
                    source_reviewed_map_path=aggregate_map,
                    output_path=incomplete_output,
                )
            self.assertFalse(incomplete_output.exists())

            self._write_aggregate_map(manifest, aggregate_map)
            changed_manifest = json.loads(json.dumps(manifest, ensure_ascii=False))
            target_dataset = pipeline.get_dataset(changed_manifest, target_dataset_id)
            target_source = target_dataset["items"][0]["fields"]["title"]["sources"]["en"]
            target_source["text"] = "A changed source title"
            target_source["sourceHash"] = pipeline.sha256_text(target_source["text"])
            changed_output = temporary / "changed.json"
            with self.assertRaisesRegex(
                pipeline.PipelineError,
                "sourceHash differs from aggregate source",
            ):
                pipeline.derive_subset_reviewed_map(
                    changed_manifest,
                    source_dataset_id="articles-graded",
                    target_dataset_id=target_dataset_id,
                    source_reviewed_map_path=aggregate_map,
                    output_path=changed_output,
                )
            self.assertFalse(changed_output.exists())


class OpenCCHantTests(unittest.TestCase):
    @staticmethod
    def _manifest():
        return {
            "datasets": [
                {
                    "dataset": "words-cet4",
                    "type": "words",
                    "sourceLibraryId": "builtin-words",
                    "contentVersion": "source-v1",
                    "items": [
                        {
                            "itemKey": "hanzi",
                            "position": 0,
                            "payload": {
                                "word": "hanzi",
                                "definitionEn": "Chinese characters",
                                "example": "These are Chinese characters.",
                            },
                            "fields": {
                                "definition": pipeline.make_field_sources(
                                    pipeline.make_source(
                                        "汉字", "zh-Hans", "definitionZh"
                                    )
                                )
                            },
                        },
                        {
                            "itemKey": "longma",
                            "position": 1,
                            "payload": {
                                "word": "longma",
                                "definitionEn": "dragon horse",
                                "example": "A dragon horse appears in the story.",
                            },
                            "fields": {
                                "definition": pipeline.make_field_sources(
                                    pipeline.make_source(
                                        "龙马", "zh-Hans", "definitionZh"
                                    )
                                )
                            },
                        },
                    ],
                }
            ]
        }

    def test_every_builtin_dataset_has_complete_zh_hans_sources(self):
        manifest = pipeline.build_source_manifest(PROJECT_ROOT)
        for dataset in manifest["datasets"]:
            with self.subTest(dataset=dataset["dataset"]):
                segments = pipeline._zh_hans_segments(dataset)
                self.assertEqual(len(segments), dataset["segmentCount"])

    def test_opencc_stage_resumes_and_materializes_a_complete_library(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            output = temporary / "words-zh-Hant.json"
            converter_info = {
                "provider": "OpenCC",
                "packageName": "fixture-opencc",
                "packageVersion": "1.0",
                "model": "s2t",
            }
            failed_calls = []

            def failing_converter(text):
                failed_calls.append(text)
                if text == "龙马":
                    raise RuntimeError("fixture interruption")
                return text.translate(str.maketrans("汉龙马", "漢龍馬"))

            with self.assertRaises(pipeline.PipelineError):
                pipeline.generate_opencc_hant_translations(
                    self._manifest(),
                    source_dataset_id="words-cet4",
                    output_path=output,
                    checkpoint_dir=temporary / "state",
                    batch_size=1,
                    converter=failing_converter,
                    converter_info=converter_info,
                )
            self.assertFalse(output.exists())
            self.assertEqual(failed_calls, ["汉字", "龙马"])

            resumed_calls = []

            def working_converter(text):
                resumed_calls.append(text)
                return text.translate(str.maketrans("汉龙马", "漢龍馬"))

            report = pipeline.generate_opencc_hant_translations(
                self._manifest(),
                source_dataset_id="words-cet4",
                output_path=output,
                checkpoint_dir=temporary / "state",
                batch_size=1,
                converter=working_converter,
                converter_info=converter_info,
            )
            self.assertEqual(resumed_calls, ["龙马"])
            self.assertEqual(report["translatedFields"], 2)
            self.assertEqual(report["convertedThisRun"], 1)
            translated = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(translated["kind"], pipeline.REVIEWED_MAP_KIND)
            self.assertEqual(translated["locale"], "zh-Hant")
            self.assertEqual(translated["items"]["hanzi"]["definition"], "漢字")
            self.assertEqual(translated["items"]["longma"]["definition"], "龍馬")

            materialized = temporary / "materialized"
            coverage = pipeline.build_reviewed_translation_libraries(
                self._manifest(),
                source_dataset_id="words-cet4",
                output_dataset_id="words-cet4",
                locale="zh-Hant",
                translations_path=output,
                output_dir=materialized,
                library_id="zh-Hant:words-cet4",
                name="CET-4 繁體詞庫",
                description="fixture",
                provider="OpenCC",
                model="s2t",
                source_url="https://github.com/BYVoid/OpenCC",
                license_info={"name": "Apache-2.0", "url": ""},
            )
            self.assertEqual(coverage["requestedItems"], 2)
            self.assertEqual(coverage["materializedItems"], 2)
            self.assertEqual(coverage["itemsWithMissingFields"], 0)
            bundle = json.loads(
                (
                    materialized / "bundles" / "words-cet4" / "zh-Hant.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(
                [item["payload"]["definitionLocalized"] for item in bundle["content"]],
                ["漢字", "龍馬"],
            )

            skipped = pipeline.generate_opencc_hant_translations(
                self._manifest(),
                source_dataset_id="words-cet4",
                output_path=output,
                checkpoint_dir=temporary / "state",
                batch_size=1,
                converter=working_converter,
                converter_info=converter_info,
            )
            self.assertTrue(skipped["skipped"])

    def test_opencc_and_reviewed_stages_fail_closed(self):
        manifest = self._manifest()
        definition = manifest["datasets"][0]["items"][1]["fields"]["definition"]
        definition["sources"].pop("zh-Hans")
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            output = temporary / "words-zh-Hant.json"
            with self.assertRaisesRegex(
                pipeline.PipelineError, "lacks valid zh-Hans source text"
            ):
                pipeline.generate_opencc_hant_translations(
                    manifest,
                    source_dataset_id="words-cet4",
                    output_path=output,
                    converter=lambda text: text,
                    converter_info={"provider": "OpenCC", "model": "s2t"},
                )
            self.assertFalse(output.exists())

            stale_map = temporary / "stale.json"
            stale_map.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "kind": pipeline.REVIEWED_MAP_KIND,
                        "locale": "zh-Hant",
                        "sourceDataset": "words-cet4",
                        "sourceContentVersion": "stale-source",
                        "items": {},
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                pipeline.PipelineError, "does not match the requested source"
            ):
                pipeline.build_reviewed_translation_libraries(
                    self._manifest(),
                    source_dataset_id="words-cet4",
                    output_dataset_id="words-cet4",
                    locale="zh-Hant",
                    translations_path=stale_map,
                    output_dir=temporary / "must-not-publish",
                    library_id="zh-Hant:words-cet4",
                    name="CET-4 繁體詞庫",
                    description="fixture",
                    provider="OpenCC",
                    model="s2t",
                    source_url="https://github.com/BYVoid/OpenCC",
                    license_info={"name": "Apache-2.0", "url": ""},
                )
            self.assertFalse((temporary / "must-not-publish").exists())


class PublishTests(unittest.TestCase):
    def test_publish_is_ordered_dry_runnable_and_resumes_after_failure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)
            version = "a" * 64
            source = pipeline.make_source("book definition", "en", "definition")
            field_item = pipeline.make_upsert_item(
                "book",
                "definition",
                source,
                "livre",
                provider="fixture",
                model="fixture",
            )
            library = pipeline.localized_library_metadata(
                locale="fr",
                library_id="fr:words-common",
                content_type="words",
                dataset="wordbook-common",
                source_library_id="builtin-words",
                name="Dictionnaire anglais-français",
                description="fixture",
                format_name="fixture",
                item_count=1,
                source={"name": "fixture", "url": "https://example.invalid/source"},
                license_info=pipeline.PROJECT_LICENSE,
                version=version,
            )
            pipeline.write_bundle_artifacts(
                output,
                dataset="wordbook-common",
                locale="fr",
                version=version,
                field_items=[field_item],
                content_items=[
                    {
                        "libraryId": "fr:words-common",
                        "itemKey": "book",
                        "position": 0,
                        "payload": {
                            "word": "book",
                            "definitionLocalized": "livre",
                            "definitionEn": "book definition",
                            "contentKey": "book",
                            "sourceLibraryId": "builtin-words",
                        },
                    }
                ],
                libraries=[library],
                provenance={},
                coverage={},
                checkpoint_key="fixture",
            )

            dry_run = pipeline.publish_library_artifacts(
                output_dir=output,
                locale="fr",
                library_id="fr:words-common",
                api_base="https://api.example.invalid",
                dry_run=True,
            )
            self.assertEqual(
                dry_run["steps"],
                ["catalog:draft", "items:0001", "catalog:ready"],
            )
            self.assertFalse((output / ".publish-checkpoints").exists())

            first_calls = []

            def failing_sender(url, payload, token, timeout):
                first_calls.append((url, payload, token, timeout))
                if len(first_calls) == 2:
                    raise pipeline.PipelineError("fixture failure")
                return {"status": 200}

            with self.assertRaises(pipeline.PipelineError):
                pipeline.publish_library_artifacts(
                    output_dir=output,
                    locale="fr",
                    library_id="fr:words-common",
                    api_base="https://api.example.invalid",
                    token="secret-do-not-print",
                    post_json=failing_sender,
                )
            self.assertEqual(first_calls[0][1]["libraries"][0]["status"], "draft")

            resumed_calls = []

            def working_sender(url, payload, token, timeout):
                resumed_calls.append((url, payload, token, timeout))
                return {"status": 201}

            report = pipeline.publish_library_artifacts(
                output_dir=output,
                locale="fr",
                library_id="fr:words-common",
                api_base="https://api.example.invalid",
                token="secret-do-not-print",
                post_json=working_sender,
            )
            self.assertEqual(report["posted"], 2)
            self.assertEqual(resumed_calls[0][1]["libraryId"], "fr:words-common")
            self.assertEqual(resumed_calls[1][1]["libraries"][0]["status"], "ready")
            self.assertNotIn("secret-do-not-print", json.dumps(report))

    def test_failed_empty_or_mismatched_rebuild_invalidates_old_publish_artifacts(self):
        for declared_count, replacement_items, expected_message in (
            (0, [], "has no materialized items"),
            (2, ["book"], "declares 2 items but materializes 1"),
        ):
            with self.subTest(declared_count=declared_count):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    output = Path(temporary_directory)
                    old_version = "c" * 64
                    replacement_version = "d" * 64

                    def library(version, item_count):
                        return pipeline.localized_library_metadata(
                            locale="fr",
                            library_id="fr:words-common",
                            content_type="words",
                            dataset="wordbook-common",
                            source_library_id="builtin-words",
                            name="Dictionnaire anglais-français",
                            description="fixture",
                            format_name="fixture",
                            item_count=item_count,
                            source={"name": "fixture", "url": "https://example.invalid"},
                            license_info=pipeline.PROJECT_LICENSE,
                            version=version,
                        )

                    def content(item_key):
                        return {
                            "libraryId": "fr:words-common",
                            "itemKey": item_key,
                            "position": 0,
                            "payload": {
                                "word": item_key,
                                "definitionLocalized": "livre",
                                "definitionEn": "book definition",
                                "contentKey": item_key,
                                "sourceLibraryId": "builtin-words",
                            },
                        }

                    pipeline.write_bundle_artifacts(
                        output,
                        dataset="wordbook-common",
                        locale="fr",
                        version=old_version,
                        field_items=[],
                        content_items=[content("book")],
                        libraries=[library(old_version, 1)],
                        provenance={},
                        coverage={},
                        checkpoint_key="old-success",
                    )
                    published = pipeline.publish_library_artifacts(
                        output_dir=output,
                        locale="fr",
                        library_id="fr:words-common",
                        api_base="https://api.example.invalid",
                        token="fixture-token",
                        post_json=lambda *_: {"status": 200},
                    )
                    self.assertTrue(published["complete"])
                    self.assertTrue(Path(published["checkpoint"]).is_file())

                    with self.assertRaisesRegex(pipeline.PipelineError, expected_message):
                        pipeline.write_bundle_artifacts(
                            output,
                            dataset="wordbook-common",
                            locale="fr",
                            version=replacement_version,
                            field_items=[],
                            content_items=[content(key) for key in replacement_items],
                            libraries=[library(replacement_version, declared_count)],
                            provenance={},
                            coverage={},
                            checkpoint_key="forced-rebuild",
                        )

                    artifact_name = "fr-words-common"
                    self.assertFalse(
                        (
                            output
                            / "admin"
                            / "catalog"
                            / "fr"
                            / f"{artifact_name}.draft.json"
                        ).exists()
                    )
                    self.assertFalse(
                        (
                            output
                            / "admin"
                            / "catalog"
                            / "fr"
                            / f"{artifact_name}.ready.json"
                        ).exists()
                    )
                    self.assertEqual(
                        list(
                            (
                                output
                                / "admin"
                                / "library-items"
                                / "fr"
                                / artifact_name
                            ).glob("*.json")
                        ),
                        [],
                    )
                    self.assertFalse(
                        (
                            output
                            / ".checkpoints"
                            / "wordbook-common"
                            / "fr.json"
                        ).exists()
                    )
                    self.assertFalse(Path(published["checkpoint"]).exists())
                    with self.assertRaisesRegex(
                        pipeline.PipelineError,
                        "Missing draft catalog artifact",
                    ):
                        pipeline.publish_library_artifacts(
                            output_dir=output,
                            locale="fr",
                            library_id="fr:words-common",
                            api_base="https://api.example.invalid",
                            dry_run=True,
                        )

    def test_large_publish_retries_rate_limited_batch_without_advancing_checkpoint(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)
            version = "b" * 64
            item_count = 2_001
            library = pipeline.localized_library_metadata(
                locale="fr",
                library_id="fr:words-common",
                content_type="words",
                dataset="wordbook-common",
                source_library_id="builtin-words",
                name="Dictionnaire anglais-français",
                description="large fixture",
                format_name="fixture",
                item_count=item_count,
                source={"name": "fixture", "url": "https://example.invalid/source"},
                license_info=pipeline.PROJECT_LICENSE,
                version=version,
            )
            content_items = []
            for position in range(item_count):
                item_key = f"word-{position:04d}"
                content_items.append(
                    {
                        "libraryId": "fr:words-common",
                        "itemKey": item_key,
                        "position": position,
                        "payload": {
                            "word": item_key,
                            "definitionLocalized": f"sens {position}",
                            "definitionEn": f"definition {position}",
                            "contentKey": item_key,
                            "sourceLibraryId": "builtin-words",
                        },
                    }
                )
            pipeline.write_bundle_artifacts(
                output,
                dataset="wordbook-common",
                locale="fr",
                version=version,
                field_items=[],
                content_items=content_items,
                libraries=[library],
                provenance={},
                coverage={},
                checkpoint_key="large-fixture",
            )

            calls = []
            waits = []

            def rate_limited_sender(url, payload, token, timeout):
                calls.append((url, payload, token, timeout))
                if len(calls) == 21:
                    return {"status": 429, "retryAfter": "2"}
                return {"status": 200}

            report = pipeline.publish_library_artifacts(
                output_dir=output,
                locale="fr",
                library_id="fr:words-common",
                api_base="https://api.example.invalid",
                token="secret-do-not-print",
                post_json=rate_limited_sender,
                sleep_fn=waits.append,
            )

            self.assertTrue(report["complete"])
            self.assertEqual(report["posted"], 23)
            self.assertEqual(report["rateLimitRetries"], 1)
            self.assertEqual(report["rateLimitWaitSeconds"], 2.0)
            self.assertEqual(waits, [2.0])
            self.assertEqual(len(calls), 24)
            self.assertEqual(calls[20][0:2], calls[21][0:2])
            checkpoint = json.loads(Path(report["checkpoint"]).read_text(encoding="utf-8"))
            self.assertTrue(checkpoint["complete"])
            self.assertEqual(len(checkpoint["completedSteps"]), 23)
            self.assertEqual(checkpoint["completedSteps"][0], "catalog:draft")
            self.assertEqual(checkpoint["completedSteps"][-1], "catalog:ready")


if __name__ == "__main__":
    unittest.main()

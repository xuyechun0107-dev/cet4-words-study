import bz2
import hashlib
import importlib
import json
import sys
import time

import pytest
from fastapi.testclient import TestClient
from tools import i18n_content_pipeline as pipeline


ADMIN_TOKEN = "test-admin-token"


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    database_path = (tmp_path / "i18n-api.sqlite3").as_posix()
    audio_root = tmp_path / "audio"
    audio_root.mkdir()
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{database_path}")
    monkeypatch.setenv("ADMIN_TOKEN", ADMIN_TOKEN)
    monkeypatch.setenv("ALLOWED_HOSTS", "testserver,localhost,127.0.0.1")
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://testserver")
    monkeypatch.setenv("AUDIO_ROOT", str(audio_root))

    for module_name in ("api.app.main", "api.app.models", "api.app.database"):
        sys.modules.pop(module_name, None)
    main = importlib.import_module("api.app.main")

    class FakePresenceRedis:
        async def zscore(self, key, device_id):
            return time.time() + 3_600

        async def zremrangebyscore(self, key, minimum, maximum):
            return 0

        async def zcard(self, key):
            return 1

        async def aclose(self):
            return None

    main.redis_client = FakePresenceRedis()
    presence_token = main.sign_device("0" * 32)
    with TestClient(
        main.app,
        headers={"X-Presence-Token": presence_token},
    ) as client:
        yield client


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def admin_headers() -> dict[str, str]:
    return {"X-Admin-Token": ADMIN_TOKEN}


def translation_item(
    item_key: str,
    field: str,
    source_text: str,
    translated_text: str,
    *,
    source_lang: str = "en",
    source_field: str = "text",
    status: str = "ready",
) -> dict[str, str]:
    return {
        "itemKey": item_key,
        "field": field,
        "sourceLang": source_lang,
        "sourceField": source_field,
        "sourceText": source_text,
        "sourceHash": source_hash(source_text),
        "translatedText": translated_text,
        "provider": "offline-test",
        "model": "fixture-v1",
        "status": status,
    }


def batch(dataset: str, locale: str, items: list[dict[str, str]]) -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "dataset": dataset,
        "locale": locale,
        "contentVersion": "fixture-2026.09.04",
        "items": items,
    }


def test_admin_upsert_requires_token(api_client):
    payload = batch(
        "words-cet4",
        "ja",
        [translation_item("ability", "definition", "capacity to do something", "能力")],
    )

    response = api_client.post("/v1/admin/i18n/translations", json=payload)

    assert response.status_code == 401


def test_i18n_public_reads_require_a_live_presence_lease(api_client):
    missing_catalog_lease = api_client.get(
        "/v1/i18n/catalog/ja",
        headers={"X-Presence-Token": ""},
    )
    missing_bundle_lease = api_client.get(
        "/v1/i18n/bundles/words-cet4/ja",
        headers={"X-Presence-Token": ""},
    )

    assert missing_catalog_lease.status_code == 401
    assert missing_bundle_lease.status_code == 401
    assert missing_catalog_lease.json()["detail"] == "An active visitor session is required."

    admitted_catalog = api_client.get("/v1/i18n/catalog/ja")
    assert admitted_catalog.status_code == 200
    assert admitted_catalog.json()["libraries"] == []
    assert api_client.get("/health", headers={"X-Presence-Token": ""}).status_code == 200
    assert (
        api_client.get(
            "/v1/presence/status",
            headers={"X-Presence-Token": ""},
        ).status_code
        == 200
    )
    admin_without_lease = api_client.post(
        "/v1/admin/i18n/translations",
        json=batch(
            "words-cet4",
            "ja",
            [translation_item("ability", "definition", "capacity", "能力")],
        ),
        headers={"X-Admin-Token": ADMIN_TOKEN, "X-Presence-Token": ""},
    )
    assert admin_without_lease.status_code == 200


def test_article_shelf_datasets_are_an_explicit_fixed_whitelist(api_client):
    api_main = sys.modules["api.app.main"]
    expected = {
        "articles-graded",
        "articles-graded-junior-basic",
        "articles-graded-junior-advanced",
        "articles-graded-senior-basic",
        "articles-graded-senior-advanced",
    }

    assert api_main.I18N_ARTICLE_DATASETS == expected
    for dataset in expected:
        assert api_main.supported_i18n_dataset(dataset)
        assert api_main.normalize_i18n_item_key(dataset, "article-one") == "article-one"
        assert api_main.valid_i18n_field(dataset, "sentences.0")
        assert api_main.i18n_dataset_matches_type(dataset, "articles")
    assert not api_main.supported_i18n_dataset("articles-graded-arbitrary")


def test_article_bundle_shape_etag_and_conditional_get(api_client):
    library = {
        "id": "ja:articles-graded",
        "type": "articles",
        "dataset": "articles-graded",
        "sourceLibraryId": "builtin-articles",
        "name": "段階別英語リーディング",
        "description": "段階別の記事ライブラリ",
        "format": "Original · Graded",
        "itemCount": 1,
        "source": {"name": "Enplay", "url": "https://enplay.aoke.ltd/"},
        "license": {"name": "Enplay original", "url": None},
        "status": "draft",
        "displayOrder": 0,
    }
    catalog_payload = {
        "schemaVersion": 1,
        "locale": "ja",
        "contentVersion": "articles-ja-v1",
        "libraries": [library],
    }
    catalog_created = api_client.post(
        "/v1/admin/i18n/catalog",
        json=catalog_payload,
        headers=admin_headers(),
    )
    assert catalog_created.status_code == 200
    assert catalog_created.json()["librariesCreated"] == 1
    assert api_client.get("/v1/i18n/catalog/ja").json()["libraries"] == []

    article_payload = {
        "id": "junior-basic-library-card",
        "title": "My First Library Card",
        "titleTranslation": "初めての図書館カード",
        "summaryTranslation": "生徒が図書館カードを作ります。",
        "level": "Junior foundation · A2",
        "levelLocalized": "中学基礎 · A2",
        "cefr": "A2",
        "genre": "Listening",
        "genreLocalized": "リスニング",
        "topic": "People and society",
        "topicLocalized": "人と社会",
        "estimatedWords": 12,
        "sentences": [
            {
                "en": "On Saturday morning, my father took me to the library.",
                "translation": "土曜日の朝、父は私を図書館へ連れて行きました。",
            }
        ],
        "contentKey": "junior-basic-library-card",
        "sourceLibraryId": "builtin-articles",
    }
    items_imported = api_client.post(
        "/v1/admin/i18n/library-items",
        json={
            "schemaVersion": 1,
            "locale": "ja",
            "libraryId": "ja:articles-graded",
            "contentVersion": "articles-ja-v1",
            "items": [
                {
                    "itemKey": "junior-basic-library-card",
                    "position": 0,
                    "payload": article_payload,
                    "sourceHash": source_hash("article source fixture"),
                    "status": "ready",
                }
            ],
        },
        headers=admin_headers(),
    )
    assert items_imported.status_code == 200
    assert items_imported.json()["itemsCreated"] == 1

    library["status"] = "ready"
    catalog_promoted = api_client.post(
        "/v1/admin/i18n/catalog",
        json=catalog_payload,
        headers=admin_headers(),
    )
    assert catalog_promoted.status_code == 200
    assert catalog_promoted.json()["librariesUpdated"] == 1

    catalog = api_client.get("/v1/i18n/catalog/ja")
    assert catalog.status_code == 200
    assert catalog.headers["cache-control"] == "private, no-store"
    assert catalog.json()["libraries"][0]["itemCount"] == 1
    assert catalog.json()["libraries"][0]["source"] == {
        "name": "Enplay",
        "url": "https://enplay.aoke.ltd/",
        "notice": None,
    }

    response = api_client.get(
        "/v1/i18n/bundles/articles-graded/ja",
        params={"v": "articles-ja-v1"},
    )
    assert response.status_code == 200
    normalized_article_payload = {
        key: value
        for key, value in article_payload.items()
        if key not in {"titleTranslation", "summaryTranslation", "sentences"}
    }
    normalized_article_payload.update(
        {
            "titleLocalized": article_payload["titleTranslation"],
            "summaryLocalized": article_payload["summaryTranslation"],
            "sentences": [
                {
                    "en": article_payload["sentences"][0]["en"],
                    "translationLocalized": article_payload["sentences"][0][
                        "translation"
                    ],
                }
            ],
        }
    )
    assert response.json() == {
        "schemaVersion": 1,
        "dataset": "articles-graded",
        "locale": "ja",
        "contentVersion": "articles-ja-v1",
        "items": {},
        "content": [
            {
                "libraryId": "ja:articles-graded",
                "itemKey": "junior-basic-library-card",
                "position": 0,
                "payload": normalized_article_payload,
            }
        ],
    }
    assert response.headers["content-language"] == "ja"
    assert response.headers["cache-control"] == "private, no-store"
    etag = response.headers["etag"]

    not_modified = api_client.get(
        "/v1/i18n/bundles/articles-graded/ja",
        params={"v": "articles-ja-v1"},
        headers={"If-None-Match": etag},
    )
    assert not_modified.status_code == 304
    assert not_modified.content == b""
    assert not_modified.headers["etag"] == etag
    assert (
        api_client.get(
            "/v1/i18n/bundles/articles-graded/ja",
            params={"v": "articles-ja-v0"},
        ).status_code
        == 404
    )


def test_word_key_normalization_and_idempotent_update(api_client):
    api_main = sys.modules["api.app.main"]
    assert api_main.normalize_i18n_item_key("wordbook-common", " ＳＴＲＡＳＳＥ ") == "strasse"

    first_payload = batch(
        "words-cet4",
        "zh-Hant",
        [
            translation_item(
                "  Abandon  ",
                "definition",
                "vt. 放弃, 抛弃",
                "vt. 放棄, 拋棄",
                source_lang="zh-Hans",
                source_field="definitionZh",
            )
        ],
    )
    first = api_client.post(
        "/v1/admin/i18n/translations",
        json=first_payload,
        headers=admin_headers(),
    )
    assert first.status_code == 200
    assert first.json()["segmentsCreated"] == 1
    assert first.json()["translationsCreated"] == 1

    unchanged = api_client.post(
        "/v1/admin/i18n/translations",
        json=first_payload,
        headers=admin_headers(),
    )
    assert unchanged.status_code == 200
    assert unchanged.json()["segmentsCreated"] == 0
    assert unchanged.json()["translationsUnchanged"] == 1

    bundle_response = api_client.get("/v1/i18n/bundles/words-cet4/zh-Hant")
    assert bundle_response.status_code == 200
    assert bundle_response.json()["items"] == {
        "abandon": {"definition": "vt. 放棄, 拋棄"}
    }

    first_payload["items"][0]["translatedText"] = "vt. 放棄、遺棄"
    updated = api_client.post(
        "/v1/admin/i18n/translations",
        json=first_payload,
        headers=admin_headers(),
    )
    assert updated.status_code == 200
    assert updated.json()["translationsUpdated"] == 1
    assert api_client.get("/v1/i18n/bundles/words-cet4/zh-Hant").json()["items"] == {
        "abandon": {"definition": "vt. 放棄、遺棄"}
    }


def test_hash_mismatch_and_invalid_field_are_rejected_atomically(api_client):
    good_item = translation_item(
        "42",
        "translation",
        "How are you?",
        "お元気ですか。",
    )
    bad_hash_item = translation_item(
        "43",
        "translation",
        "Where are you?",
        "どこにいますか。",
    )
    bad_hash_item["sourceHash"] = "0" * 64
    payload = batch(
        "sentences-tatoeba-basic",
        "ja",
        [good_item, bad_hash_item],
    )

    rejected = api_client.post(
        "/v1/admin/i18n/translations",
        json=payload,
        headers=admin_headers(),
    )
    assert rejected.status_code == 422
    assert api_client.get("/v1/i18n/bundles/sentences-tatoeba-basic/ja").status_code == 404

    wrong_field = batch(
        "words-cet4",
        "ja",
        [translation_item("ability", "translation", "ability", "能力")],
    )
    rejected_field = api_client.post(
        "/v1/admin/i18n/translations",
        json=wrong_field,
        headers=admin_headers(),
    )
    assert rejected_field.status_code == 422


def test_draft_rows_and_unsupported_bundles_are_not_public(api_client):
    payload = batch(
        "sentences-daily",
        "fr",
        [
            translation_item(
                "  Could   you help me? ",
                "translation",
                "Could you help me?",
                "Pourriez-vous m'aider ?",
                status="draft",
            )
        ],
    )
    imported = api_client.post(
        "/v1/admin/i18n/translations",
        json=payload,
        headers=admin_headers(),
    )
    assert imported.status_code == 200
    assert api_client.get("/v1/i18n/bundles/sentences-daily/fr").status_code == 404
    assert api_client.get("/v1/i18n/bundles/not-a-dataset/fr").status_code == 404
    assert api_client.get("/v1/i18n/bundles/sentences-daily/en").status_code == 404


def test_foreign_bundle_never_falls_back_to_legacy_overlay(api_client):
    payload = batch(
        "words-cet4",
        "ja",
        [
            translation_item(
                "ability",
                "definition",
                "the capacity to do something",
                "何かをする能力",
                source_field="definition",
            )
        ],
    )
    imported = api_client.post(
        "/v1/admin/i18n/translations",
        json=payload,
        headers=admin_headers(),
    )
    assert imported.status_code == 200

    response = api_client.get("/v1/i18n/bundles/words-cet4/ja")

    assert response.status_code == 404
    assert api_client.get("/v1/i18n/catalog/ja").json()["libraries"] == []


def test_article_metadata_audit_fields_are_accepted_without_publishing(api_client):
    payload = batch(
        "articles-graded",
        "fr",
        [
            translation_item(
                "junior-basic-library-card",
                field,
                source_text,
                translated_text,
                source_field=field,
            )
            for field, source_text, translated_text in (
                ("level", "Junior foundation · A2", "Collège débutant · A2"),
                ("genre", "Listening", "Compréhension orale"),
                ("topic", "People and society", "Personnes et société"),
            )
        ],
    )

    imported = api_client.post(
        "/v1/admin/i18n/translations",
        json=payload,
        headers=admin_headers(),
    )

    assert imported.status_code == 200
    assert imported.json()["translationsCreated"] == 3
    assert api_client.get("/v1/i18n/bundles/articles-graded/fr").status_code == 404


def test_catalog_promotion_requires_complete_version_and_unique_dataset(api_client):
    library = {
        "id": "ko:words-cet4",
        "type": "words",
        "dataset": "words-cet4",
        "sourceLibraryId": "builtin-words",
        "name": "CET-4 어휘",
        "description": None,
        "format": "Localized",
        "itemCount": 1,
        "source": {"name": "Enplay", "url": None},
        "license": {"name": "Source licenses", "url": None},
        "status": "ready",
        "displayOrder": 0,
    }
    payload = {
        "schemaVersion": 1,
        "locale": "ko",
        "contentVersion": "words-ko-v1",
        "libraries": [library],
    }

    incomplete = api_client.post(
        "/v1/admin/i18n/catalog",
        json=payload,
        headers=admin_headers(),
    )

    assert incomplete.status_code == 409
    assert api_client.get("/v1/i18n/catalog/ko").json()["libraries"] == []

    library["status"] = "draft"
    duplicate = dict(library)
    duplicate["id"] = "ko:words-cet4-copy"
    duplicate_payload = dict(payload)
    duplicate_payload["libraries"] = [library, duplicate]
    duplicate_response = api_client.post(
        "/v1/admin/i18n/catalog",
        json=duplicate_payload,
        headers=admin_headers(),
    )
    assert duplicate_response.status_code == 422


def test_library_item_payload_must_match_catalog_identity(api_client):
    catalog_payload = {
        "schemaVersion": 1,
        "locale": "es",
        "contentVersion": "words-es-v1",
        "libraries": [
            {
                "id": "es:words-cet4",
                "type": "words",
                "dataset": "words-cet4",
                "sourceLibraryId": "builtin-words",
                "name": "Vocabulario CET-4",
                "description": None,
                "format": "Localized",
                "itemCount": 1,
                "source": {"name": "Enplay", "url": ""},
                "license": {
                    "name": "LEXiTRON Terms of Use " + ("extended " * 10),
                    "url": "",
                    "notice": (
                        "This product is created by the adaptation of LEXiTRON "
                        "developed by NECTEC (http://www.nectec.or.th/)."
                    ),
                },
                "status": "draft",
                "displayOrder": 0,
            }
        ],
    }
    assert (
        api_client.post(
            "/v1/admin/i18n/catalog",
            json=catalog_payload,
            headers=admin_headers(),
        ).status_code
        == 200
    )
    invalid_item = {
        "word": "ability",
        "phonetic": "/əˈbɪləti/",
        "definition": "capacidad para hacer algo",
        "definitionEn": "the capacity to do something",
        "example": "She has the ability to explain it.",
        "contentKey": "ability",
        "sourceLibraryId": "wrong-library",
    }

    rejected = api_client.post(
        "/v1/admin/i18n/library-items",
        json={
            "schemaVersion": 1,
            "locale": "es",
            "libraryId": "es:words-cet4",
            "contentVersion": "words-es-v1",
            "items": [
                {
                    "itemKey": "ability",
                    "position": 0,
                    "payload": invalid_item,
                    "sourceHash": source_hash("ability source"),
                    "status": "ready",
                }
            ],
        },
        headers=admin_headers(),
    )

    assert rejected.status_code == 422
    assert api_client.get("/v1/i18n/bundles/words-cet4/es").status_code == 404

    valid_item = dict(invalid_item)
    valid_item["sourceLibraryId"] = "builtin-words"
    valid_item["definitionLocalized"] = valid_item.pop("definition")
    imported = api_client.post(
        "/v1/admin/i18n/library-items",
        json={
            "schemaVersion": 1,
            "locale": "es",
            "libraryId": "es:words-cet4",
            "contentVersion": "words-es-v1",
            "items": [
                {
                    "itemKey": "ability",
                    "position": 0,
                    "payload": valid_item,
                    "sourceHash": source_hash("ability source"),
                    "status": "ready",
                }
            ],
        },
        headers=admin_headers(),
    )
    assert imported.status_code == 200

    catalog_payload["libraries"][0]["status"] = "ready"
    promoted = api_client.post(
        "/v1/admin/i18n/catalog",
        json=catalog_payload,
        headers=admin_headers(),
    )
    assert promoted.status_code == 200
    catalog = api_client.get("/v1/i18n/catalog/es").json()["libraries"][0]
    assert (
        sys.modules["api.app.models"].ContentLibrary.__table__.c.license_name.type.length
        == 160
    )
    assert catalog["source"]["url"] is None
    assert catalog["license"]["url"] is None
    assert len(catalog["license"]["name"]) > 80
    assert catalog["license"]["notice"] == (
        "This product is created by the adaptation of LEXiTRON developed by "
        "NECTEC (http://www.nectec.or.th/)."
    )
    stored_payload = api_client.get(
        "/v1/i18n/bundles/words-cet4/es"
    ).json()["content"][0]["payload"]
    assert stored_payload["definitionLocalized"] == "capacidad para hacer algo"
    assert "definition" not in stored_payload


def test_pipeline_generated_common_sentence_batches_are_accepted(api_client, tmp_path):
    links = tmp_path / "eng-fra_links.tsv.bz2"
    targets = tmp_path / "fra_sentences.tsv.bz2"
    with bz2.open(links, "wt", encoding="utf-8") as handle:
        handle.write("10\t100\n")
    with bz2.open(targets, "wt", encoding="utf-8") as handle:
        handle.write("100\tfra\tBonjour.\n")

    source = pipeline.make_source("Hello.", "en", "text")
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
                            "translation": pipeline.make_field_sources(source)
                        },
                    }
                ],
            }
        ]
    }
    output = tmp_path / "generated"
    report = pipeline.build_tatoeba_library(
        manifest,
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
    assert report["translated"] == 1

    catalog_dir = output / "admin" / "catalog" / "fr"
    draft = json.loads(
        (catalog_dir / "fr-sentences-common.draft.json").read_text(encoding="utf-8")
    )
    ready = json.loads(
        (catalog_dir / "fr-sentences-common.ready.json").read_text(encoding="utf-8")
    )
    assert (
        api_client.post(
            "/v1/admin/i18n/catalog",
            json=draft,
            headers=admin_headers(),
        ).status_code
        == 200
    )
    for batch_path in sorted(
        (output / "admin" / "library-items" / "fr" / "fr-sentences-common").glob(
            "*.json"
        )
    ):
        item_batch = json.loads(batch_path.read_text(encoding="utf-8"))
        assert (
            api_client.post(
                "/v1/admin/i18n/library-items",
                json=item_batch,
                headers=admin_headers(),
            ).status_code
            == 200
        )
    assert (
        api_client.post(
            "/v1/admin/i18n/catalog",
            json=ready,
            headers=admin_headers(),
        ).status_code
        == 200
    )

    bundle = api_client.get("/v1/i18n/bundles/sentences-common/fr")
    assert bundle.status_code == 200
    assert bundle.json()["content"][0]["payload"] == {
        "scene": "greetings",
        "text": "Hello.",
        "translationLocalized": "Bonjour.",
        "sourceIds": [10, 100],
        "contentKey": "10",
        "sourceLibraryId": "builtin-sentences-tatoeba-basic",
    }


def test_pipeline_generated_tatoeba_direct_artifacts_round_trip(api_client, tmp_path):
    english = tmp_path / "eng_sentences.tsv.bz2"
    links = tmp_path / "eng-fra_links.tsv.bz2"
    targets = tmp_path / "fra_sentences.tsv.bz2"
    with bz2.open(english, "wt", encoding="utf-8") as handle:
        handle.write("10\teng\tHello there!\n")
        handle.write("20\teng\tWhere are you going?\n")
        handle.write("30\teng\tThis meal tastes wonderful.\n")
    with bz2.open(links, "wt", encoding="utf-8") as handle:
        handle.write("30\t300\n")
        handle.write("10\t100\n")
        handle.write("20\t200\n")
    with bz2.open(targets, "wt", encoding="utf-8") as handle:
        handle.write("100\tfra\tBonjour à tous !\n")
        handle.write("200\tfra\tOù allez-vous ?\n")
        handle.write("300\tfra\tCe repas est délicieux.\n")

    output = tmp_path / "generated-direct"
    report = pipeline.build_tatoeba_direct_library(
        output_dataset_id="sentences-common",
        locale="fr",
        english_sentences_path=english,
        links_path=links,
        target_sentences_path=targets,
        output_dir=output,
        library_id="fr:sentences-direct",
        name="Phrases anglaises–françaises",
        description="fixture",
        target_count=3,
    )
    assert report["materializedItems"] == 3

    catalog_dir = output / "admin" / "catalog" / "fr"
    draft_path, = tuple(catalog_dir.glob("*.draft.json"))
    ready_path, = tuple(catalog_dir.glob("*.ready.json"))
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    ready = json.loads(ready_path.read_text(encoding="utf-8"))
    assert api_client.post(
        "/v1/admin/i18n/catalog",
        json=draft,
        headers=admin_headers(),
    ).status_code == 200

    item_paths = sorted(
        (
            output
            / "admin"
            / "library-items"
            / "fr"
            / "fr-sentences-direct"
        ).glob("*.json")
    )
    assert len(item_paths) == 1
    for item_path in item_paths:
        item_batch = json.loads(item_path.read_text(encoding="utf-8"))
        response = api_client.post(
            "/v1/admin/i18n/library-items",
            json=item_batch,
            headers=admin_headers(),
        )
        assert response.status_code == 200, response.text

    assert api_client.post(
        "/v1/admin/i18n/catalog",
        json=ready,
        headers=admin_headers(),
    ).status_code == 200

    content_version = ready["contentVersion"]
    bundle = api_client.get(
        "/v1/i18n/bundles/sentences-common/fr",
        params={"v": content_version},
    )
    assert bundle.status_code == 200
    assert bundle.json()["contentVersion"] == content_version
    assert [entry["itemKey"] for entry in bundle.json()["content"]] == [
        "10",
        "20",
        "30",
    ]
    assert bundle.json()["content"][0]["payload"] == {
        "scene": "generalConversation",
        "text": "Hello there!",
        "translationLocalized": "Bonjour à tous !",
        "sourceIds": [10, 100],
        "contentKey": "10",
        "sourceLibraryId": "tatoeba-eng-fra",
    }
    catalog_library = api_client.get("/v1/i18n/catalog/fr").json()["libraries"][0]
    assert catalog_library["source"]["notice"]
    assert catalog_library["license"]["name"] == "CC BY 2.0 FR"


def test_existing_library_stays_live_during_interrupted_version_staging(api_client):
    library = {
        "id": "fr:words-cet4",
        "type": "words",
        "dataset": "words-cet4",
        "sourceLibraryId": "builtin-words",
        "name": "Vocabulaire CET-4",
        "description": "fixture",
        "format": "fixture",
        "itemCount": 1,
        "source": {"name": "fixture", "url": ""},
        "license": {"name": "fixture", "url": ""},
        "status": "draft",
        "displayOrder": 0,
    }

    def catalog_payload(version: str, publish_status: str) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "locale": "fr",
            "contentVersion": version,
            "libraries": [{**library, "status": publish_status}],
        }

    def item_payload(version: str, definition: str) -> dict[str, object]:
        return {
            "schemaVersion": 1,
            "locale": "fr",
            "libraryId": "fr:words-cet4",
            "contentVersion": version,
            "items": [
                {
                    "itemKey": "ability",
                    "position": 0,
                    "payload": {
                        "word": "ability",
                        "phonetic": "/əˈbɪləti/",
                        "definitionLocalized": definition,
                        "definitionEn": "the capacity to do something",
                        "example": "She has the ability to explain it.",
                        "contentKey": "ability",
                        "sourceLibraryId": "builtin-words",
                    },
                    "sourceHash": source_hash(f"ability-{version}"),
                    "status": "ready",
                }
            ],
        }

    assert (
        api_client.post(
            "/v1/admin/i18n/catalog",
            json=catalog_payload("words-fr-v1", "draft"),
            headers=admin_headers(),
        ).status_code
        == 200
    )
    assert (
        api_client.post(
            "/v1/admin/i18n/library-items",
            json=item_payload("words-fr-v1", "capacité v1"),
            headers=admin_headers(),
        ).status_code
        == 200
    )
    assert (
        api_client.post(
            "/v1/admin/i18n/catalog",
            json=catalog_payload("words-fr-v1", "ready"),
            headers=admin_headers(),
        ).status_code
        == 200
    )

    staged = api_client.post(
        "/v1/admin/i18n/catalog",
        json=catalog_payload("words-fr-v2", "draft"),
        headers=admin_headers(),
    )
    assert staged.status_code == 200
    assert staged.json()["librariesStaged"] == 1

    incomplete_promotion = api_client.post(
        "/v1/admin/i18n/catalog",
        json=catalog_payload("words-fr-v2", "ready"),
        headers=admin_headers(),
    )
    assert incomplete_promotion.status_code == 409
    catalog = api_client.get("/v1/i18n/catalog/fr").json()["libraries"][0]
    assert catalog["contentVersion"] == "words-fr-v1"
    bundle = api_client.get("/v1/i18n/bundles/words-cet4/fr").json()
    assert bundle["content"][0]["payload"]["definitionLocalized"] == "capacité v1"

    assert (
        api_client.post(
            "/v1/admin/i18n/library-items",
            json=item_payload("words-fr-v2", "capacité v2"),
            headers=admin_headers(),
        ).status_code
        == 200
    )
    promoted = api_client.post(
        "/v1/admin/i18n/catalog",
        json=catalog_payload("words-fr-v2", "ready"),
        headers=admin_headers(),
    )
    assert promoted.status_code == 200
    assert api_client.get("/v1/i18n/catalog/fr").json()["libraries"][0][
        "contentVersion"
    ] == "words-fr-v2"
    assert api_client.get("/v1/i18n/bundles/words-cet4/fr").json()["content"][0][
        "payload"
    ]["definitionLocalized"] == "capacité v2"

    active_mutation = api_client.post(
        "/v1/admin/i18n/library-items",
        json=item_payload("words-fr-v2", "mutation partielle interdite"),
        headers=admin_headers(),
    )
    assert active_mutation.status_code == 409
    assert api_client.get("/v1/i18n/bundles/words-cet4/fr").json()["content"][0][
        "payload"
    ]["definitionLocalized"] == "capacité v2"

    active_replay = api_client.post(
        "/v1/admin/i18n/library-items",
        json=item_payload("words-fr-v2", "capacité v2"),
        headers=admin_headers(),
    )
    assert active_replay.status_code == 200
    assert active_replay.json()["itemsUnchanged"] == 1

    active_append_payload = item_payload("words-fr-v2", "capacité v2")
    active_append_payload["items"].append(
        {
            "itemKey": "access",
            "position": 1,
            "payload": {
                "word": "access",
                "definitionLocalized": "accès",
                "definitionEn": "the ability or right to enter or use something",
                "contentKey": "access",
                "sourceLibraryId": "builtin-words",
            },
            "sourceHash": source_hash("access-words-fr-v2"),
            "status": "ready",
        }
    )
    active_append = api_client.post(
        "/v1/admin/i18n/library-items",
        json=active_append_payload,
        headers=admin_headers(),
    )
    assert active_append.status_code == 409
    after_append_bundle = api_client.get("/v1/i18n/bundles/words-cet4/fr").json()
    assert len(after_append_bundle["content"]) == 1
    assert after_append_bundle["content"][0]["itemKey"] == "ability"
    assert api_client.get("/v1/i18n/catalog/fr").json()["libraries"][0][
        "itemCount"
    ] == 1

    old_version_mutation = api_client.post(
        "/v1/admin/i18n/library-items",
        json=item_payload("words-fr-v1", "ancienne version altérée"),
        headers=admin_headers(),
    )
    assert old_version_mutation.status_code == 409
    old_version_replay = api_client.post(
        "/v1/admin/i18n/library-items",
        json=item_payload("words-fr-v1", "capacité v1"),
        headers=admin_headers(),
    )
    assert old_version_replay.status_code == 200
    assert old_version_replay.json()["itemsUnchanged"] == 1

    rollback = api_client.post(
        "/v1/admin/i18n/catalog",
        json=catalog_payload("words-fr-v1", "ready"),
        headers=admin_headers(),
    )
    assert rollback.status_code == 200
    assert api_client.get("/v1/i18n/bundles/words-cet4/fr").json()["content"][0][
        "payload"
    ]["definitionLocalized"] == "capacité v1"

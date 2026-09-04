#!/usr/bin/env python3
"""Build deterministic multilingual content artifacts for Enplay.

The core tool deliberately uses only the Python standard library.  It turns
the project's JavaScript data files (and optional API/JSON wordbooks) into a
stable source manifest, then materialises locale-scoped libraries from reviewed
data sources such as WikDict and Tatoeba.  Optional offline conversion stages
load their own development-host dependency only when invoked.

Generated files are written atomically and only when their bytes changed.  A
stage checkpoint makes completed jobs cheap to resume.  This module never
modifies the application source data.
"""

from __future__ import annotations

import argparse
import bz2
import datetime
import email.utils
import gzip
import hashlib
import importlib.metadata
import json
import lzma
import math
import os
import re
import sqlite3
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


SCHEMA_VERSION = 1
MANIFEST_KIND = "enplay.i18n-source-manifest"
BUNDLE_KIND = "enplay.localized-content-bundle"
CATALOG_KIND = "enplay.localized-library-catalog"
REVIEWED_MAP_KIND = "enplay.reviewed-translation-map"
MAX_LIBRARY_ITEM_PAYLOAD_BYTES = 250_000
SUPPORTED_LOCALES = ("zh-Hant", "ja", "ko", "fr", "es", "pt", "ru", "th", "ar")
TATOEBA_CODES = {
    "ja": "jpn",
    "ko": "kor",
    "fr": "fra",
    "es": "spa",
    "pt": "por",
    "ru": "rus",
    "th": "tha",
    "ar": "ara",
}
LOCALE_LABELS = {
    "zh-Hant": "繁體中文",
    "ja": "日本語",
    "ko": "한국어",
    "fr": "Français",
    "es": "Español",
    "pt": "Português",
    "ru": "Русский",
    "th": "ไทย",
    "ar": "العربية",
}
ARTICLE_METADATA_EN = {
    "level": {
        "中考基础 · A2": "Lower Secondary Foundation · A2",
        "中考提高 · A2+–B1": "Lower Secondary Advanced · A2+–B1",
        "高考基础 · B1": "Upper Secondary Foundation · B1",
        "高考提高 · B1+–B2": "Upper Secondary Advanced · B1+–B2",
    },
    "genre": {
        "记叙文": "Narrative",
        "经验分享": "Personal Experience",
        "科普阅读": "Popular Science Reading",
        "说明文": "Expository Text",
        "听力短文": "Short Listening Passage",
        "听力访谈": "Listening Interview",
        "听力故事": "Listening Story",
        "议论文": "Argumentative Essay",
        "阅读理解": "Reading Comprehension",
    },
    "topic": {
        "人与社会": "People and Society",
        "人与自然": "People and Nature",
        "人与自我": "Self and Personal Development",
    },
}
WIKDICT_LICENSE = {
    "name": "CC BY-SA",
    "url": "https://www.wikdict.com/page/download",
}
KAIKKI_WIKTIONARY_LICENSE = {
    "name": "Wiktionary CC BY-SA 4.0 / GFDL",
    "url": "https://kaikki.org/dictionary/rawdata.html",
}
TATOEBA_LICENSE = {
    "name": "CC BY 2.0 FR",
    "url": "https://creativecommons.org/licenses/by/2.0/fr/",
    "notice": (
        "Sentence pairs are derived from contributions to Tatoeba "
        "(https://tatoeba.org/). Original sentence IDs are retained for "
        "attribution and verification."
    ),
}
ARTICLE_SOURCE_DATASETS = {
    "builtin-articles": "articles-graded",
    "builtin-articles-junior-basic": "articles-graded-junior-basic",
    "builtin-articles-junior-advanced": "articles-graded-junior-advanced",
    "builtin-articles-senior-basic": "articles-graded-senior-basic",
    "builtin-articles-senior-advanced": "articles-graded-senior-advanced",
}
ARTICLE_SOURCE_DISPLAY_ORDER = {
    source_library_id: 300 + index
    for index, source_library_id in enumerate(ARTICLE_SOURCE_DATASETS)
}
TATOEBA_DIRECT_POLICY_VERSION = "tatoeba-direct-v1"
TATOEBA_ENGLISH_SHAPE = re.compile(r"^[A-Za-z][A-Za-z0-9 '\",.!?;:()\-]+[.!?]$")
TATOEBA_ENGLISH_WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
TATOEBA_UNSAFE_TEXT = re.compile(
    r"(?:https?://|www\.|\b[^\s@]+@[^\s@]+\b|[<>]|"
    r"\b(?:kill|killed|murder|suicide|rape|porn|naked|bomb|terrorist)\b)",
    re.IGNORECASE,
)
TATOEBA_TARGET_SCRIPT = {
    "ja": re.compile(r"[\u3040-\u30ff]"),
    "ko": re.compile(r"[\uac00-\ud7af]"),
    "fr": re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-ž]"),
    "es": re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-ž]"),
    "pt": re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-ž]"),
    "ru": re.compile(r"[\u0400-\u052f]"),
    "th": re.compile(r"[\u0e00-\u0e7f]"),
    "ar": re.compile(r"[\u0600-\u06ff]"),
}
PROJECT_LICENSE = {
    "name": "Project content (license not declared)",
    "url": "",
}
OPEN_ENGLISH_KOREAN_LICENSE = {
    "name": "CC BY-SA 4.0",
    "url": "https://creativecommons.org/licenses/by-sa/4.0/",
}
YAITRON_ACKNOWLEDGEMENT = (
    "This product is created by the adaptation of LEXiTRON developed by "
    "NECTEC (http://www.nectec.or.th/)."
)
YAITRON_LICENSE = {
    "name": "LEXiTRON Terms of Use",
    "url": "https://github.com/veer66/Yaitron/blob/master/LICENSE-LEXITRON",
    "notice": YAITRON_ACKNOWLEDGEMENT,
}


class PipelineError(RuntimeError):
    """Raised for user-actionable input or adapter failures."""


def canonical_article_metadata(field_name: str, value: Any) -> str:
    """Map current curriculum metadata to a stable canonical English value."""

    text = " ".join(str(value or "").strip().split())
    if not text:
        return ""
    mapped = ARTICLE_METADATA_EN.get(field_name, {}).get(text)
    if mapped:
        return mapped
    if not re.search(r"[\u3400-\u9fff]", text):
        return text
    raise PipelineError(
        f"No canonical English mapping for article {field_name} value {text!r}"
    )


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8") + b"\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def content_version(value: Any) -> str:
    """Return an API-compatible stable 64-character content version."""

    return sha256_bytes(canonical_json_bytes(value))


def normalize_key(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    return " ".join(text.strip().split()).casefold()


def disambiguate_duplicate_key(
    base_key: str,
    occurrence: int,
    used_keys: set[str],
    *,
    max_length: int = 512,
) -> str:
    """Keep the first natural key and suffix later source-order duplicates."""

    if occurrence == 1 and base_key not in used_keys:
        candidate = base_key
    else:
        suffix_number = max(2, occurrence)
        while True:
            suffix = f"#duplicate-{suffix_number}"
            candidate = f"{base_key[: max_length - len(suffix)]}{suffix}"
            if candidate not in used_keys:
                break
            suffix_number += 1
    used_keys.add(candidate)
    return candidate


def select_unique_positive_source_key(
    source_ids: Sequence[int],
    used_keys: set[str],
    *,
    identity: Mapping[str, Any],
) -> str:
    """Prefer a real source ID, then derive a stable JS-safe positive key."""

    for source_id in source_ids:
        candidate = str(source_id)
        if source_id > 0 and candidate not in used_keys:
            used_keys.add(candidate)
            return candidate

    # Exact source pairs can themselves repeat.  Preserve the record and its
    # real IDs in payload.sourceIds while deriving a stable positive key from
    # the full source identity.  Keep it within JavaScript's safe integer range
    # even though the public API transports it as a string.
    maximum = (2**53) - 1
    candidate_number = (int(content_version(identity)[:13], 16) % maximum) + 1
    while str(candidate_number) in used_keys:
        candidate_number = (candidate_number % maximum) + 1
    candidate = str(candidate_number)
    used_keys.add(candidate)
    return candidate


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
    return cleaned or "artifact"


def write_json_if_changed(path: Path, payload: Any) -> bool:
    """Atomically write canonical UTF-8 JSON, returning whether bytes changed."""

    encoded = canonical_json_bytes(payload)
    if path.exists() and path.read_bytes() == encoded:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
    return True


def _extract_balanced_literal(source: str, variable: str) -> str:
    match = re.search(rf"\b(?:const|let|var)\s+{re.escape(variable)}\s*=\s*", source)
    if not match:
        raise PipelineError(f"Cannot find JavaScript variable {variable!r}")
    start = match.end()
    while start < len(source) and source[start].isspace():
        start += 1
    if start >= len(source) or source[start] not in "[{":
        raise PipelineError(f"Variable {variable!r} is not an array/object literal")

    pairs = {"[": "]", "{": "}"}
    stack = [pairs[source[start]]]
    quote: str | None = None
    escaped = False
    index = start + 1
    while index < len(source):
        character = source[index]
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            index += 1
            continue
        if character in "\"'`":
            quote = character
        elif character in pairs:
            stack.append(pairs[character])
        elif stack and character == stack[-1]:
            stack.pop()
            if not stack:
                return source[start : index + 1]
        index += 1
    raise PipelineError(f"Unterminated JavaScript literal for {variable!r}")


def read_js_literal(path: Path, variable: str, *, relaxed: bool = False) -> Any:
    source = path.read_text(encoding="utf-8")
    literal = _extract_balanced_literal(source, variable)
    if relaxed:
        # articles_graded.js is JSON-shaped JavaScript: unquoted identifier keys
        # and trailing commas are the only syntax differences we accept.
        literal = re.sub(
            r"(?m)(^|[{,]\s*)([A-Za-z_$][A-Za-z0-9_$]*)(\s*:)",
            r'\1"\2"\3',
            literal,
        )
        literal = re.sub(r",\s*([}\]])", r"\1", literal)
    try:
        return json.loads(literal)
    except json.JSONDecodeError as error:
        raise PipelineError(
            f"Unable to parse {variable!r} in {path}: {error.msg} at line {error.lineno}"
        ) from error


def load_json_locator(locator: str, *, bearer_token: str | None = None) -> tuple[Any, dict[str, Any]]:
    headers = {"Accept": "application/json", "User-Agent": "Enplay-i18n-builder/1"}
    if bearer_token:
        headers["X-Presence-Token"] = bearer_token
    if re.match(r"^https?://", locator, re.IGNORECASE):
        request = urllib.request.Request(locator, headers=headers)
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
        origin = locator
    else:
        path = Path(locator).resolve()
        raw = path.read_bytes()
        origin = str(path)
    try:
        return json.loads(raw.decode("utf-8-sig")), {
            "locator": origin,
            "sha256": sha256_bytes(raw),
            "bytes": len(raw),
        }
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PipelineError(f"Invalid UTF-8 JSON wordbook at {locator}: {error}") from error


def make_source(text: Any, language: str, source_field: str) -> dict[str, str] | None:
    value = str(text or "").strip()
    if not value:
        return None
    return {
        "lang": language,
        "sourceField": source_field,
        "text": value,
        "sourceHash": sha256_text(value),
    }


def make_field_sources(*sources: dict[str, str] | None) -> dict[str, Any]:
    return {"sources": {source["lang"]: source for source in sources if source}}


def _dataset(
    dataset_id: str,
    content_type: str,
    source_library_id: str,
    items: list[dict[str, Any]],
    source: dict[str, Any],
) -> dict[str, Any]:
    items.sort(key=lambda item: (int(item.get("position", 0)), str(item["itemKey"])))
    core = {
        "dataset": dataset_id,
        "type": content_type,
        "sourceLibraryId": source_library_id,
        "source": source,
        "itemCount": len(items),
        "segmentCount": sum(len(item.get("fields", {})) for item in items),
        "items": items,
    }
    core["contentVersion"] = content_version(core)
    return core


def _file_source(project_root: Path, path: Path) -> dict[str, Any]:
    try:
        display = str(path.relative_to(project_root)).replace("\\", "/")
    except ValueError:
        display = str(path)
    return {"name": display, "url": display, "sha256": sha256_file(path)}


def _tatoeba_dataset_id(library: Mapping[str, Any]) -> str:
    library_id = str(library.get("id") or "")
    prefix = "builtin-sentences-tatoeba-"
    suffix = library_id[len(prefix) :] if library_id.startswith(prefix) else safe_filename(library_id)
    return f"sentences-tatoeba-{suffix or 'basic'}"


def _article_dataset_id(source_library_id: str) -> str:
    try:
        return ARTICLE_SOURCE_DATASETS[source_library_id]
    except KeyError as error:
        raise PipelineError(
            f"Unsupported built-in article library id {source_library_id!r}"
        ) from error


def build_source_manifest(
    project_root: Path,
    remote_wordbooks: Sequence[str] = (),
    *,
    presence_token: str | None = None,
) -> dict[str, Any]:
    """Extract every canonical source into a deterministic intermediate manifest."""

    project_root = project_root.resolve()
    words_path = project_root / "words.js"
    phrases_path = project_root / "phrases_normalized.js"
    tatoeba_path = project_root / "sentences_tatoeba.js"
    articles_path = project_root / "articles_graded.js"
    for path in (words_path, phrases_path, tatoeba_path, articles_path):
        if not path.is_file():
            raise PipelineError(f"Required source file is missing: {path}")

    datasets: list[dict[str, Any]] = []
    libraries: list[dict[str, Any]] = []

    words = read_js_literal(words_path, "cet4Words")
    word_items: list[dict[str, Any]] = []
    for position, raw in enumerate(words):
        word = str(raw.get("word") or "").strip()
        if not word:
            continue
        definition_en = raw.get("definition")
        definition_zh = raw.get("definitionZh")
        word_items.append(
            {
                "itemKey": normalize_key(word),
                "position": position,
                "payload": {
                    "word": word,
                    "phonetic": raw.get("phonetic") or "",
                    "definitionEn": definition_en or "",
                    "definitionZh": definition_zh or "",
                    "example": raw.get("example") or "",
                },
                "fields": {
                    "definition": make_field_sources(
                        make_source(definition_en, "en", "definition"),
                        make_source(definition_zh, "zh-Hans", "definitionZh"),
                    )
                },
            }
        )
    datasets.append(
        _dataset(
            "words-cet4",
            "words",
            "builtin-words",
            word_items,
            _file_source(project_root, words_path),
        )
    )
    libraries.append(
        {
            "id": "builtin-words",
            "type": "words",
            "dataset": "words-cet4",
            "name": "CET-4",
            "description": "Built-in CET-4 vocabulary source",
        }
    )

    phrases = read_js_literal(phrases_path, "phrases")
    phrase_items: list[dict[str, Any]] = []
    phrase_key_occurrences: defaultdict[str, int] = defaultdict(int)
    phrase_item_keys: set[str] = set()
    for position, raw in enumerate(phrases):
        sentence = str(raw.get("sentence") or "").strip()
        if not sentence:
            continue
        base_item_key = normalize_key(sentence)
        phrase_key_occurrences[base_item_key] += 1
        item_key = disambiguate_duplicate_key(
            base_item_key,
            phrase_key_occurrences[base_item_key],
            phrase_item_keys,
        )
        note = raw.get("note")
        phrase_items.append(
            {
                "itemKey": item_key,
                "position": position,
                "payload": {
                    "scene": raw.get("scene") or "generalConversation",
                    "text": sentence,
                    "translationZh": note or "",
                },
                "fields": {
                    "translation": make_field_sources(
                        make_source(sentence, "en", "sentence"),
                        make_source(note, "zh-Hans", "note"),
                    )
                },
            }
        )
    datasets.append(
        _dataset(
            "sentences-daily",
            "sentences",
            "builtin-sentences",
            phrase_items,
            _file_source(project_root, phrases_path),
        )
    )
    libraries.append(
        {
            "id": "builtin-sentences",
            "type": "sentences",
            "dataset": "sentences-daily",
            "name": "Daily English",
            "description": "Built-in daily English sentence source",
        }
    )

    tatoeba_libraries = read_js_literal(tatoeba_path, "libraries")
    for library in tatoeba_libraries:
        dataset_id = _tatoeba_dataset_id(library)
        sentence_items: list[dict[str, Any]] = []
        sentence_item_keys: set[str] = set()
        for position, raw in enumerate(library.get("items") or []):
            sentence = str(raw.get("text") or "").strip()
            if not sentence:
                continue
            source_ids = [int(value) for value in raw.get("sourceIds") or [] if str(value).isdigit()]
            item_key = select_unique_positive_source_key(
                source_ids,
                sentence_item_keys,
                identity={
                    "dataset": dataset_id,
                    "position": position,
                    "scene": raw.get("scene") or "generalConversation",
                    "text": sentence,
                    "translationZh": raw.get("note") or "",
                    "sourceIds": source_ids,
                },
            )
            sentence_items.append(
                {
                    "itemKey": item_key,
                    "position": position,
                    "payload": {
                        "scene": raw.get("scene") or "generalConversation",
                        "text": sentence,
                        "translationZh": raw.get("note") or "",
                        "sourceIds": source_ids,
                    },
                    "fields": {
                        "translation": make_field_sources(
                            make_source(sentence, "en", "text"),
                            make_source(raw.get("note"), "zh-Hans", "note"),
                        )
                    },
                }
            )
        source = {
            **_file_source(project_root, tatoeba_path),
            "upstream": library.get("sourceUrl") or "https://tatoeba.org/",
            "license": {
                "name": library.get("format") or TATOEBA_LICENSE["name"],
                "url": library.get("licenseUrl") or TATOEBA_LICENSE["url"],
            },
        }
        datasets.append(
            _dataset(
                dataset_id,
                "sentences",
                str(library.get("id") or dataset_id),
                sentence_items,
                source,
            )
        )
        libraries.append(
            {
                "id": str(library.get("id") or dataset_id),
                "type": "sentences",
                "dataset": dataset_id,
                "name": library.get("name") or "Tatoeba sentences",
                "description": library.get("description") or "",
            }
        )

    article_libraries = read_js_literal(articles_path, "gradedArticleLibraries", relaxed=True)
    article_source = _file_source(project_root, articles_path)
    article_items: list[dict[str, Any]] = []
    libraries.append(
        {
            "id": "builtin-articles",
            "type": "articles",
            "dataset": "articles-graded",
            "name": "All graded articles",
            "description": "All built-in graded article sources",
            "level": "",
            "cefr": "",
        }
    )
    for library in article_libraries:
        source_library_id = str(library.get("id") or "").strip()
        if not source_library_id:
            raise PipelineError("Every graded article library needs a stable id")
        library_dataset_id = _article_dataset_id(source_library_id)
        library_items: list[dict[str, Any]] = []
        libraries.append(
            {
                "id": source_library_id,
                "type": "articles",
                "dataset": library_dataset_id,
                "name": library.get("name") or "Graded articles",
                "description": library.get("description") or "",
                "level": library.get("level") or "",
                "cefr": library.get("cefr") or "",
            }
        )
        for raw in library.get("items") or []:
            article_id = str(raw.get("id") or "").strip()
            if not article_id:
                continue
            raw_sentences = list(raw.get("sentences") or [])
            # The original article collection currently has a Chinese editorial
            # summary but no authored English equivalent.  Keep the source
            # lineage honest by using an explicitly labelled extractive summary
            # (the first English sentence) until summaryEn is supplied.
            summary_en = str(raw.get("summaryEn") or "").strip()
            summary_source_field = "summaryEn"
            if not summary_en:
                summary_en = next(
                    (
                        str(sentence.get("en") or "").strip()
                        for sentence in raw_sentences
                        if str(sentence.get("en") or "").strip()
                    ),
                    "",
                )
                summary_source_field = "sentences.en[0] (extractive summary)"
            level_zh = raw.get("level") or library.get("level") or ""
            genre_zh = raw.get("genre") or ""
            topic_zh = raw.get("topic") or ""
            level_en = canonical_article_metadata("level", level_zh)
            genre_en = canonical_article_metadata("genre", genre_zh)
            topic_en = canonical_article_metadata("topic", topic_zh)
            fields: dict[str, Any] = {
                "title": make_field_sources(
                    make_source(raw.get("title"), "en", "title"),
                    make_source(raw.get("titleZh"), "zh-Hans", "titleZh"),
                ),
                "summary": make_field_sources(
                    make_source(summary_en, "en", summary_source_field),
                    make_source(raw.get("summary"), "zh-Hans", "summary"),
                ),
                "level": make_field_sources(
                    make_source(level_en, "en", "levelCanonicalEn"),
                    make_source(level_zh, "zh-Hans", "level"),
                ),
                "genre": make_field_sources(
                    make_source(genre_en, "en", "genreCanonicalEn"),
                    make_source(genre_zh, "zh-Hans", "genre"),
                ),
                "topic": make_field_sources(
                    make_source(topic_en, "en", "topicCanonicalEn"),
                    make_source(topic_zh, "zh-Hans", "topic"),
                ),
            }
            sentences: list[dict[str, Any]] = []
            for sentence_index, sentence in enumerate(raw_sentences):
                fields[f"sentences.{sentence_index}"] = make_field_sources(
                    make_source(sentence.get("en"), "en", "sentences.en"),
                    make_source(sentence.get("zh"), "zh-Hans", "sentences.zh"),
                )
                sentences.append(
                    {"en": sentence.get("en") or "", "zh": sentence.get("zh") or ""}
                )
            article_entry = {
                "itemKey": article_id,
                "position": len(article_items),
                "sourceLibraryId": source_library_id,
                "payload": {
                    "id": article_id,
                    "title": raw.get("title") or "",
                    "titleZh": raw.get("titleZh") or "",
                    "summaryEn": summary_en,
                    "summaryZh": raw.get("summary") or "",
                    "level": level_zh,
                    "levelEn": level_en,
                    "cefr": raw.get("cefr") or library.get("cefr") or "",
                    "genre": genre_zh,
                    "genreEn": genre_en,
                    "topic": topic_zh,
                    "topicEn": topic_en,
                    "estimatedWords": raw.get("estimatedWords") or 0,
                    "sentences": sentences,
                },
                "fields": fields,
            }
            article_items.append(article_entry)
            library_items.append({**article_entry, "position": len(library_items)})
        datasets.append(
            _dataset(
                library_dataset_id,
                "articles",
                source_library_id,
                library_items,
                article_source,
            )
        )
    datasets.append(
        _dataset(
            "articles-graded",
            "articles",
            "builtin-articles",
            article_items,
            article_source,
        )
    )

    for locator in remote_wordbooks:
        payload, locator_source = load_json_locator(locator, bearer_token=presence_token)
        if not isinstance(payload, Mapping) or not isinstance(payload.get("items"), list):
            raise PipelineError(f"Remote wordbook {locator} must be an object with an items array")
        slug = safe_filename(str(payload.get("slug") or Path(locator).stem)).lower()
        dataset_id = f"wordbook-{slug}"
        library_id = f"remote-{slug}"
        remote_items: list[dict[str, Any]] = []
        for position, raw in enumerate(payload["items"]):
            word = str(raw.get("word") or raw.get("text") or "").strip()
            if not word:
                continue
            definition_en = raw.get("definition_en") or raw.get("definitionEn")
            definition_local = raw.get("definition")
            if not str(definition_en or "").strip():
                raise PipelineError(
                    f"Remote wordbook {locator} item {word!r} needs a non-empty "
                    "definition_en/definitionEn field"
                )
            remote_items.append(
                {
                    "itemKey": normalize_key(word),
                    "position": position,
                    "payload": {
                        "word": word,
                        "phonetic": raw.get("phonetic") or "",
                        "definitionEn": definition_en or "",
                        "definitionZh": definition_local or "",
                        "example": raw.get("example") or "",
                    },
                    "fields": {
                        "definition": make_field_sources(
                            make_source(definition_en, "en", "definition_en"),
                            make_source(definition_local, "zh-Hans", "definition"),
                        )
                    },
                }
            )
        source = {
            "name": payload.get("source_name") or payload.get("sourceName") or "API wordbook",
            "url": payload.get("source_url") or payload.get("sourceUrl") or locator_source["locator"],
            "license": {
                "name": payload.get("license_name") or payload.get("licenseName") or "Unknown",
                "url": payload.get("license_url") or payload.get("licenseUrl") or "",
            },
            "input": locator_source,
        }
        datasets.append(_dataset(dataset_id, "words", library_id, remote_items, source))
        libraries.append(
            {
                "id": library_id,
                "type": "words",
                "dataset": dataset_id,
                "name": payload.get("name") or slug,
                "description": payload.get("description") or "",
            }
        )

    datasets.sort(key=lambda value: value["dataset"])
    libraries.sort(key=lambda value: value["id"])
    manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": MANIFEST_KIND,
        "project": "enplay",
        "libraries": libraries,
        "datasets": datasets,
    }
    manifest["manifestVersion"] = content_version(manifest)
    return manifest


def get_dataset(manifest: Mapping[str, Any], dataset_id: str) -> Mapping[str, Any]:
    for dataset in manifest.get("datasets") or []:
        if dataset.get("dataset") == dataset_id:
            return dataset
    raise PipelineError(f"Dataset {dataset_id!r} does not exist in the source manifest")


@dataclass(frozen=True)
class LookupResult:
    text: str
    provider: str
    model: str
    source_ref: str
    score: float = 0.0
    details: Mapping[str, Any] = field(default_factory=dict)


class LexicalAdapter:
    """Small interface shared by WikDict, FreeDict and Kaikki adapters."""

    provider = "unknown"

    def lookup(self, headword: str, english_definition: str = "") -> LookupResult | None:
        raise NotImplementedError

    def fingerprint(self) -> Mapping[str, Any]:
        raise NotImplementedError


def _definition_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z][a-z'-]{1,}", text.casefold())
        if token not in {"the", "and", "that", "with", "from", "into", "for", "are", "you"}
    }


class WikDictSQLiteAdapter(LexicalAdapter):
    provider = "wikdict"

    def __init__(self, path: Path):
        self.path = path.resolve()
        if not self.path.is_file():
            raise PipelineError(f"WikDict SQLite file does not exist: {self.path}")
        uri = f"file:{self.path.as_posix()}?mode=ro&immutable=1"
        self.connection = sqlite3.connect(uri, uri=True)
        self.connection.row_factory = sqlite3.Row
        tables = {
            row[0]
            for row in self.connection.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
        }
        if "translation" not in tables and "simple_translation" not in tables:
            self.connection.close()
            raise PipelineError(
                "Unsupported WikDict schema: expected translation or simple_translation table"
            )
        self.tables = tables

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "WikDictSQLiteAdapter":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def fingerprint(self) -> Mapping[str, Any]:
        return {
            "provider": self.provider,
            "path": str(self.path),
            "sha256": sha256_file(self.path),
            "bytes": self.path.stat().st_size,
        }

    def lookup(self, headword: str, english_definition: str = "") -> LookupResult | None:
        candidates: list[sqlite3.Row] = []
        if "translation" in self.tables:
            candidates = list(
                self.connection.execute(
                    """
                    SELECT written_rep, trans_list, COALESCE(sense, '') AS sense,
                           CAST(COALESCE(score, 0) AS REAL) AS score,
                           CAST(COALESCE(importance, 0) AS REAL) AS importance
                    FROM translation
                    WHERE written_rep = ? COLLATE NOCASE AND trim(COALESCE(trans_list, '')) <> ''
                    """,
                    (headword.strip(),),
                )
            )
        if candidates:
            wanted = _definition_tokens(english_definition)

            def rank(row: sqlite3.Row) -> tuple[float, float, float, str]:
                sense_tokens = _definition_tokens(str(row["sense"]))
                overlap = len(wanted & sense_tokens) / max(1, len(wanted | sense_tokens))
                return (
                    overlap,
                    float(row["score"]),
                    float(row["importance"]),
                    str(row["trans_list"]),
                )

            selected = max(candidates, key=rank)
            translation = " · ".join(
                dict.fromkeys(
                    part.strip()
                    for part in str(selected["trans_list"]).split("|")
                    if part.strip()
                )
            )
            if translation:
                return LookupResult(
                    text=translation,
                    provider=self.provider,
                    model=self.path.name,
                    source_ref=f"sqlite:{self.path.name}:translation:{headword}",
                    score=rank(selected)[0],
                    details={
                        "sense": str(selected["sense"]),
                        "wikdictScore": float(selected["score"]),
                        "importance": float(selected["importance"]),
                    },
                )
        if "simple_translation" in self.tables:
            row = self.connection.execute(
                """
                SELECT written_rep, trans_list,
                       CAST(COALESCE(max_score, 0) AS REAL) AS score,
                       CAST(COALESCE(rel_importance, 0) AS REAL) AS importance
                FROM simple_translation
                WHERE written_rep = ? COLLATE NOCASE AND trim(COALESCE(trans_list, '')) <> ''
                ORDER BY score DESC, importance DESC
                LIMIT 1
                """,
                (headword.strip(),),
            ).fetchone()
            if row:
                translation = " · ".join(
                    dict.fromkeys(
                        part.strip()
                        for part in str(row["trans_list"]).split("|")
                        if part.strip()
                    )
                )
                if translation:
                    return LookupResult(
                        text=translation,
                        provider=self.provider,
                        model=self.path.name,
                        source_ref=f"sqlite:{self.path.name}:simple_translation:{headword}",
                        details={"wikdictScore": float(row["score"])},
                    )
        return None


def _open_text_auto(path: Path) -> Any:
    suffix = path.suffix.casefold()
    if suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8")
    if suffix == ".bz2":
        return bz2.open(path, "rt", encoding="utf-8")
    if suffix in {".xz", ".lzma"}:
        return lzma.open(path, "rt", encoding="utf-8")
    return path.open("rt", encoding="utf-8")


class OpenEnglishKoreanAdapter(LexicalAdapter):
    """Read the Open English-Korean Dictionary JSON export or SQLite DB."""

    provider = "open-english-korean-dict"
    source_name = "Open English-Korean Dictionary"

    def __init__(self, path: Path, wanted_headwords: Iterable[str] | None = None):
        self.path = path.resolve()
        if not self.path.is_file():
            raise PipelineError(f"Korean dictionary file does not exist: {self.path}")
        self.wanted = {normalize_key(word) for word in wanted_headwords or []}
        self.entries: dict[str, LookupResult] = {}
        self.connection: sqlite3.Connection | None = None
        with self.path.open("rb") as handle:
            sqlite_header = handle.read(16) == b"SQLite format 3\x00"
        self.format = "sqlite" if sqlite_header else "json"
        if self.format == "sqlite":
            self._open_sqlite()
        else:
            self._load_json()

    def _open_sqlite(self) -> None:
        uri = f"file:{self.path.as_posix()}?mode=ro&immutable=1"
        self.connection = sqlite3.connect(uri, uri=True)
        self.connection.row_factory = sqlite3.Row
        table = self.connection.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name = 'words'"
        ).fetchone()
        if not table:
            self.close()
            raise PipelineError("Unsupported Korean dictionary schema: expected words table")
        columns = {
            str(row[1]) for row in self.connection.execute("PRAGMA table_info(words)")
        }
        required = {"word", "meaning_ko"}
        if not required.issubset(columns):
            self.close()
            raise PipelineError(
                "Unsupported Korean dictionary schema: words needs word and meaning_ko"
            )
        self.columns = columns

    @staticmethod
    def _make_result(
        word: str,
        raw: Mapping[str, Any],
        *,
        model: str,
        source_ref: str,
    ) -> LookupResult | None:
        meaning = str(raw.get("meaning_ko") or "").strip()
        if not meaning:
            return None
        details = {
            key: raw.get(key)
            for key in (
                "meaning_en",
                "meaning_secondary",
                "ipa",
                "pos",
                "cefr",
                "freq_rank",
            )
            if raw.get(key) is not None and raw.get(key) != ""
        }
        return LookupResult(
            text=meaning,
            provider="open-english-korean-dict",
            model=model,
            source_ref=source_ref,
            details={"headword": word, **details},
        )

    def _load_json(self) -> None:
        raw_payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw_payload, Mapping):
            raise PipelineError("Korean words.json must be an object keyed by English word")
        nested_words = raw_payload.get("words")
        raw_entries = (
            nested_words
            if isinstance(nested_words, Mapping)
            and any(
                isinstance(value, Mapping) and "meaning_ko" in value
                for value in nested_words.values()
            )
            else raw_payload
        )
        if not isinstance(raw_entries, Mapping):
            raise PipelineError("Korean words.json 'words' value must be an object")
        for raw_word, raw in raw_entries.items():
            if not isinstance(raw, Mapping):
                continue
            word = str(raw_word).strip()
            key = normalize_key(word)
            if not key or (self.wanted and key not in self.wanted):
                continue
            result = self._make_result(
                word,
                raw,
                model=self.path.name,
                source_ref=f"json:{self.path.name}:{word}",
            )
            if result:
                self.entries[key] = result

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def __enter__(self) -> "OpenEnglishKoreanAdapter":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def lookup(self, headword: str, english_definition: str = "") -> LookupResult | None:
        del english_definition
        key = normalize_key(headword)
        if self.format == "json":
            return self.entries.get(key)
        if self.connection is None:
            raise PipelineError("Korean SQLite adapter is closed")
        selected_columns = [
            column
            for column in (
                "word",
                "meaning_ko",
                "meaning_en",
                "meaning_secondary",
                "ipa",
                "pos",
                "cefr",
                "freq_rank",
            )
            if column in self.columns
        ]
        row = self.connection.execute(
            f"SELECT {', '.join(selected_columns)} FROM words "
            "WHERE word = ? COLLATE NOCASE LIMIT 1",
            (headword.strip(),),
        ).fetchone()
        if not row:
            return None
        raw = dict(row)
        return self._make_result(
            str(raw.get("word") or headword),
            raw,
            model=self.path.name,
            source_ref=f"sqlite:{self.path.name}:words:{raw.get('word') or headword}",
        )

    def fingerprint(self) -> Mapping[str, Any]:
        return {
            "provider": self.provider,
            "format": self.format,
            "path": str(self.path),
            "sha256": sha256_file(self.path),
            "bytes": self.path.stat().st_size,
        }


class YaitronAdapter(LexicalAdapter):
    """Read Yaitron English-to-Thai entries from NDJSON or TEI."""

    provider = "yaitron"
    source_name = "Yaitron"
    _XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

    def __init__(self, path: Path, wanted_headwords: Iterable[str] | None = None):
        self.path = path.resolve()
        if not self.path.is_file():
            raise PipelineError(f"Yaitron source file does not exist: {self.path}")
        wanted = {normalize_key(word) for word in wanted_headwords or []}
        self.format = "tei" if self.path.suffix.casefold() in {".tei", ".xml"} else "ndjson"
        collected: dict[str, dict[str, Any]] = {}
        if self.format == "tei":
            self._load_tei(wanted, collected)
        else:
            self._load_ndjson(wanted, collected)
        self.entries: dict[str, LookupResult] = {}
        for key, entry in collected.items():
            translations = list(dict.fromkeys(entry["translations"]))[:12]
            if not translations:
                continue
            references = list(dict.fromkeys(entry["references"]))
            self.entries[key] = LookupResult(
                text="；".join(translations),
                provider=self.provider,
                model=self.path.name,
                source_ref=(
                    f"{self.format}:{self.path.name}:" + ",".join(references[:12])
                ),
                details={
                    "entryReferences": references,
                    "partsOfSpeech": list(dict.fromkeys(entry["partsOfSpeech"])),
                    "translationCount": len(translations),
                    "acknowledgement": YAITRON_ACKNOWLEDGEMENT,
                },
            )

    @staticmethod
    def _collect(
        collected: dict[str, dict[str, Any]],
        wanted: set[str],
        word: str,
        translations: Iterable[str],
        reference: str,
        part_of_speech: str = "",
    ) -> None:
        key = normalize_key(word)
        if not key or (wanted and key not in wanted):
            return
        values = [str(value).strip() for value in translations if str(value).strip()]
        if not values:
            return
        entry = collected.setdefault(
            key, {"translations": [], "references": [], "partsOfSpeech": []}
        )
        entry["translations"].extend(values)
        entry["references"].append(reference)
        if part_of_speech:
            entry["partsOfSpeech"].append(part_of_speech)

    def _load_ndjson(
        self, wanted: set[str], collected: dict[str, dict[str, Any]]
    ) -> None:
        with _open_text_auto(self.path) as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError as error:
                    raise PipelineError(
                        f"Malformed Yaitron NDJSON at {self.path}:{line_number}: {error.msg}"
                    ) from error
                if not isinstance(raw, Mapping):
                    continue
                translation = raw.get("translation") or {}
                if not isinstance(translation, Mapping):
                    continue
                if raw.get("lang") != "en" or translation.get("lang") != "th":
                    continue
                values = [translation.get("text") or ""]
                for similar in raw.get("similar_translations") or []:
                    if isinstance(similar, Mapping) and similar.get("lang") == "th":
                        values.append(similar.get("text") or "")
                self._collect(
                    collected,
                    wanted,
                    str(raw.get("headword") or ""),
                    values,
                    str(raw.get("entry_id") or line_number),
                    str(raw.get("pos") or ""),
                )

    def _load_tei(
        self, wanted: set[str], collected: dict[str, dict[str, Any]]
    ) -> None:
        entry_number = 0
        for _, element in ET.iterparse(self.path, events=("end",)):
            if element.tag.rsplit("}", 1)[-1] != "entry":
                continue
            entry_number += 1
            if element.attrib.get(self._XML_LANG) != "en":
                element.clear()
                continue
            headword = next(
                (
                    " ".join(node.itertext()).strip()
                    for node in element.iter()
                    if node.tag.rsplit("}", 1)[-1] == "orth"
                    and " ".join(node.itertext()).strip()
                ),
                "",
            )
            part_of_speech = next(
                (
                    " ".join(node.itertext()).strip()
                    for node in element.iter()
                    if node.tag.rsplit("}", 1)[-1] == "pos"
                ),
                "",
            )
            translations: list[str] = []
            for citation in element.iter():
                if citation.tag.rsplit("}", 1)[-1] != "cit":
                    continue
                if citation.attrib.get("type") not in {"translation", "trans"}:
                    continue
                if citation.attrib.get(self._XML_LANG) not in {None, "th"}:
                    continue
                translations.extend(
                    " ".join(node.itertext()).strip()
                    for node in citation.iter()
                    if node.tag.rsplit("}", 1)[-1] == "quote"
                )
            self._collect(
                collected,
                wanted,
                headword,
                translations,
                str(entry_number),
                part_of_speech,
            )
            element.clear()

    def lookup(self, headword: str, english_definition: str = "") -> LookupResult | None:
        del english_definition
        return self.entries.get(normalize_key(headword))

    def fingerprint(self) -> Mapping[str, Any]:
        return {
            "provider": self.provider,
            "format": self.format,
            "path": str(self.path),
            "sha256": sha256_file(self.path),
            "bytes": self.path.stat().st_size,
        }


class KaikkiJsonlAdapter(LexicalAdapter):
    """Adapter for a target-language Kaikki Wiktionary JSONL extract.

    Korean and Thai are intentionally handled here rather than by FreeDict,
    which currently publishes no eng-kor or eng-tha dataset.
    """

    provider = "kaikki-wiktionary"

    def __init__(self, path: Path, wanted_headwords: Iterable[str] | None = None):
        self.path = path.resolve()
        wanted = {normalize_key(word) for word in wanted_headwords or []}
        self.entries: dict[str, LookupResult] = {}
        with _open_text_auto(self.path) as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                raw = json.loads(line)
                word = str(raw.get("word") or "").strip()
                key = normalize_key(word)
                if not key or (wanted and key not in wanted) or key in self.entries:
                    continue
                glosses: list[str] = []
                for sense in raw.get("senses") or []:
                    glosses.extend(str(value).strip() for value in sense.get("glosses") or [])
                glosses = list(dict.fromkeys(value for value in glosses if value))
                if glosses:
                    self.entries[key] = LookupResult(
                        text="；".join(glosses[:8]),
                        provider=self.provider,
                        model=self.path.name,
                        source_ref=f"jsonl:{self.path.name}:{line_number}",
                        details={"glossCount": len(glosses)},
                    )

    def lookup(self, headword: str, english_definition: str = "") -> LookupResult | None:
        del english_definition
        return self.entries.get(normalize_key(headword))

    def fingerprint(self) -> Mapping[str, Any]:
        return {
            "provider": self.provider,
            "path": str(self.path),
            "sha256": sha256_file(self.path),
            "bytes": self.path.stat().st_size,
        }


class FreeDictTeiAdapter(LexicalAdapter):
    """Minimal namespace-agnostic adapter for an extracted FreeDict TEI file."""

    provider = "freedict"

    def __init__(self, path: Path, wanted_headwords: Iterable[str] | None = None):
        self.path = path.resolve()
        wanted = {normalize_key(word) for word in wanted_headwords or []}
        self.entries: dict[str, LookupResult] = {}
        for _, element in ET.iterparse(self.path, events=("end",)):
            if element.tag.rsplit("}", 1)[-1] != "entry":
                continue
            orthographies = [
                " ".join(node.itertext()).strip()
                for node in element.iter()
                if node.tag.rsplit("}", 1)[-1] == "orth"
            ]
            headword = next((value for value in orthographies if value), "")
            key = normalize_key(headword)
            if key and (not wanted or key in wanted) and key not in self.entries:
                translations: list[str] = []
                for citation in element.iter():
                    if citation.tag.rsplit("}", 1)[-1] != "cit":
                        continue
                    if citation.attrib.get("type") not in {None, "trans"}:
                        continue
                    for node in citation.iter():
                        if node.tag.rsplit("}", 1)[-1] in {"quote", "orth"}:
                            value = " ".join(node.itertext()).strip()
                            if value and normalize_key(value) != key:
                                translations.append(value)
                translations = list(dict.fromkeys(translations))
                if translations:
                    self.entries[key] = LookupResult(
                        text=" · ".join(translations[:12]),
                        provider=self.provider,
                        model=self.path.name,
                        source_ref=f"tei:{self.path.name}:{headword}",
                        details={"translationCount": len(translations)},
                    )
            element.clear()

    def lookup(self, headword: str, english_definition: str = "") -> LookupResult | None:
        del english_definition
        return self.entries.get(normalize_key(headword))

    def fingerprint(self) -> Mapping[str, Any]:
        return {
            "provider": self.provider,
            "path": str(self.path),
            "sha256": sha256_file(self.path),
            "bytes": self.path.stat().st_size,
        }


def select_source(field_value: Mapping[str, Any], locale: str) -> Mapping[str, str] | None:
    sources = field_value.get("sources") or {}
    source_language = "zh-Hans" if locale == "zh-Hant" else "en"
    source = sources.get(source_language)
    if source and source.get("text"):
        return source
    return None


def make_upsert_item(
    item_key: str,
    output_field: str,
    source: Mapping[str, str],
    translated_text: str,
    result: LookupResult | None = None,
    *,
    provider: str | None = None,
    model: str | None = None,
    status: str = "ready",
) -> dict[str, Any]:
    return {
        "itemKey": item_key,
        "field": output_field,
        "sourceLang": source["lang"],
        "sourceField": source["sourceField"],
        "sourceText": source["text"],
        "sourceHash": source["sourceHash"],
        "translatedText": translated_text.strip(),
        "provider": result.provider if result else provider,
        "model": result.model if result else model,
        "status": status,
    }


def localized_library_metadata(
    *,
    locale: str,
    library_id: str,
    content_type: str,
    dataset: str,
    source_library_id: str,
    name: str,
    description: str,
    format_name: str,
    item_count: int,
    source: Mapping[str, str],
    license_info: Mapping[str, str],
    version: str,
    status: str = "ready",
    display_order: int = 100,
) -> dict[str, Any]:
    return {
        "id": library_id,
        "locale": locale,
        "type": content_type,
        "dataset": dataset,
        "sourceLibraryId": source_library_id,
        "name": name,
        "description": description,
        "format": format_name,
        "itemCount": item_count,
        "source": {
            "name": source.get("name", ""),
            "url": source.get("url", ""),
            "notice": source.get("notice", ""),
        },
        "license": {
            "name": license_info.get("name", ""),
            "url": license_info.get("url", ""),
            "notice": license_info.get("notice", ""),
        },
        "contentVersion": version,
        "status": status,
        "displayOrder": display_order,
    }


def _catalog_path(output_dir: Path, locale: str) -> Path:
    return output_dir / "catalog" / f"{safe_filename(locale)}.json"


def update_catalog(output_dir: Path, locale: str, libraries: Sequence[Mapping[str, Any]]) -> None:
    path = _catalog_path(output_dir, locale)
    existing: dict[str, Any] = {}
    if path.exists():
        existing_payload = json.loads(path.read_text(encoding="utf-8"))
        existing = {item["id"]: item for item in existing_payload.get("libraries") or []}
    for library in libraries:
        existing[str(library["id"])] = dict(library)
    ordered = sorted(existing.values(), key=lambda item: (item.get("displayOrder", 0), item["id"]))
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": CATALOG_KIND,
        "locale": locale,
        "libraries": ordered,
    }
    payload["catalogVersion"] = content_version(payload)
    write_json_if_changed(path, payload)


def _invalidate_bundle_artifacts(
    output_dir: Path,
    *,
    dataset: str,
    locale: str,
    library_ids: Sequence[str],
) -> None:
    """Make a failed rebuild impossible to publish from stale generated files."""

    build_checkpoint_path = (
        output_dir
        / ".checkpoints"
        / safe_filename(dataset)
        / f"{safe_filename(locale)}.json"
    )
    invalidated_library_ids = {
        str(value) for value in library_ids if str(value).strip()
    }
    if build_checkpoint_path.is_file():
        try:
            previous_checkpoint = json.loads(
                build_checkpoint_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            previous_checkpoint = {}
        invalidated_library_ids.update(
            str(value)
            for value in (previous_checkpoint.get("libraryIds") or [])
            if str(value).strip()
        )
    direct_files = (
        output_dir / "bundles" / safe_filename(dataset) / f"{safe_filename(locale)}.json",
        output_dir / "provenance" / safe_filename(dataset) / f"{safe_filename(locale)}.json",
        output_dir / "reports" / safe_filename(dataset) / f"{safe_filename(locale)}.json",
        build_checkpoint_path,
    )
    for path in direct_files:
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    upsert_dir = output_dir / "upserts" / safe_filename(dataset) / safe_filename(locale)
    if upsert_dir.is_dir():
        for path in upsert_dir.glob("*.json"):
            path.unlink()

    catalog_dir = output_dir / "admin" / "catalog" / safe_filename(locale)
    for library_id in sorted(invalidated_library_ids):
        artifact_name = safe_filename(library_id)
        for suffix in ("draft", "ready"):
            try:
                (catalog_dir / f"{artifact_name}.{suffix}.json").unlink()
            except FileNotFoundError:
                pass
        item_dir = (
            output_dir
            / "admin"
            / "library-items"
            / safe_filename(locale)
            / artifact_name
        )
        if item_dir.is_dir():
            for path in item_dir.glob("*.json"):
                path.unlink()
        try:
            (
                output_dir
                / ".publish-checkpoints"
                / safe_filename(locale)
                / f"{artifact_name}.json"
            ).unlink()
        except FileNotFoundError:
            pass

    catalog_path = _catalog_path(output_dir, locale)
    if catalog_path.is_file() and invalidated_library_ids:
        try:
            catalog_payload = json.loads(catalog_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            catalog_payload = None
        if isinstance(catalog_payload, Mapping):
            retained_libraries = [
                item
                for item in (catalog_payload.get("libraries") or [])
                if isinstance(item, Mapping)
                and str(item.get("id") or "") not in invalidated_library_ids
            ]
            if retained_libraries:
                replacement = {
                    **catalog_payload,
                    "libraries": retained_libraries,
                }
                replacement.pop("catalogVersion", None)
                replacement["catalogVersion"] = content_version(replacement)
                write_json_if_changed(catalog_path, replacement)
            else:
                catalog_path.unlink()


def _prepare_bundle_artifact_inputs(
    *,
    dataset: str,
    locale: str,
    version: str,
    field_items: Sequence[Mapping[str, Any]],
    content_items: Sequence[Mapping[str, Any]],
    libraries: Sequence[Mapping[str, Any]],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, Mapping[str, Any]],
    dict[str, list[dict[str, Any]]],
]:
    """Validate the complete artifact graph before any new file is written."""

    if not libraries:
        raise PipelineError("At least one localized target library is required")
    libraries_by_id: dict[str, Mapping[str, Any]] = {}
    expected_counts: dict[str, int] = {}
    for index, library in enumerate(libraries):
        if not isinstance(library, Mapping):
            raise PipelineError(f"libraries[{index}] must be an object")
        library_id = str(library.get("id") or "").strip()
        if not library_id:
            raise PipelineError(f"libraries[{index}] needs a non-empty id")
        if library_id in libraries_by_id:
            raise PipelineError(f"Duplicate localized library id {library_id!r}")
        if library.get("locale") != locale:
            raise PipelineError(f"Library {library_id!r} locale does not match {locale!r}")
        if library.get("dataset") != dataset:
            raise PipelineError(f"Library {library_id!r} dataset does not match {dataset!r}")
        if library.get("contentVersion") != version:
            raise PipelineError(f"Library {library_id!r} contentVersion does not match bundle")
        if not str(library.get("sourceLibraryId") or "").strip():
            raise PipelineError(f"Library {library_id!r} needs a sourceLibraryId")
        try:
            item_count = int(library.get("itemCount"))
        except (TypeError, ValueError) as error:
            raise PipelineError(f"Library {library_id!r} itemCount must be an integer") from error
        if item_count <= 0:
            raise PipelineError(
                f"Library {library_id!r} has no materialized items; refusing to retain "
                "or publish stale artifacts"
            )
        libraries_by_id[library_id] = library
        expected_counts[library_id] = item_count

    field_map: dict[str, dict[str, Any]] = defaultdict(dict)
    source_hashes_by_item: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen_fields: set[tuple[str, str]] = set()
    for index, item in enumerate(field_items):
        if not isinstance(item, Mapping):
            raise PipelineError(f"field_items[{index}] must be an object")
        key = str(item.get("itemKey") or "").strip()
        output_field = str(item.get("field") or "").strip()
        if not key or not output_field:
            raise PipelineError(f"field_items[{index}] needs itemKey and field")
        translated_text = item.get("translatedText")
        if not isinstance(translated_text, str) or not translated_text.strip():
            raise PipelineError(f"field_items[{index}] needs non-empty translatedText")
        source_hash = str(item.get("sourceHash") or "")
        if not re.fullmatch(r"[0-9a-f]{64}", source_hash):
            raise PipelineError(f"field_items[{index}] needs a valid sourceHash")
        field_identity = (key, output_field)
        if field_identity in seen_fields:
            raise PipelineError(f"Duplicate translated field {key!r}/{output_field!r}")
        seen_fields.add(field_identity)
        if output_field.startswith("sentences."):
            field_map[key].setdefault("sentences", {})[output_field.split(".", 1)[1]] = item[
                "translatedText"
            ]
        else:
            field_map[key][output_field] = item["translatedText"]
        source_hashes_by_item[key].append(
            {"field": output_field, "sourceHash": source_hash}
        )

    content_by_library: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_keys: dict[str, set[str]] = defaultdict(set)
    seen_positions: dict[str, set[int]] = defaultdict(set)
    for index, item in enumerate(content_items):
        if not isinstance(item, Mapping):
            raise PipelineError(f"content_items[{index}] must be an object")
        library_id = str(item.get("libraryId") or "").strip()
        item_key = str(item.get("itemKey") or "").strip()
        if library_id not in libraries_by_id:
            raise PipelineError(f"Content references unknown localized library {library_id!r}")
        if not item_key or item_key in seen_keys[library_id]:
            raise PipelineError(
                f"Content has a missing or duplicate itemKey {item_key!r} in {library_id!r}"
            )
        try:
            position = int(item.get("position"))
        except (TypeError, ValueError) as error:
            raise PipelineError(
                f"Content item {library_id!r}/{item_key!r} has an invalid position"
            ) from error
        if position < 0 or position in seen_positions[library_id]:
            raise PipelineError(
                f"Content item {library_id!r}/{item_key!r} has a duplicate or negative position"
            )
        payload = item.get("payload")
        if not isinstance(payload, Mapping):
            raise PipelineError(f"Payload for {library_id!r}/{item_key!r} must be an object")
        library = libraries_by_id[library_id]
        if str(payload.get("contentKey")) != item_key:
            raise PipelineError(f"Payload contentKey does not match itemKey {item_key!r}")
        if str(payload.get("sourceLibraryId")) != str(library["sourceLibraryId"]):
            raise PipelineError(
                f"Payload sourceLibraryId does not match catalog for {library_id!r}"
            )
        payload_size = len(canonical_json_bytes(payload))
        if payload_size > MAX_LIBRARY_ITEM_PAYLOAD_BYTES:
            raise PipelineError(
                f"Payload for {library_id!r}/{item_key!r} exceeds the "
                f"{MAX_LIBRARY_ITEM_PAYLOAD_BYTES}-byte API limit"
            )
        source_parts = sorted(
            source_hashes_by_item.get(item_key, []),
            key=lambda value: (value["field"], value["sourceHash"]),
        )
        content_by_library[library_id].append(
            {
                "itemKey": item_key,
                "position": position,
                "payload": dict(payload),
                "sourceHash": content_version(source_parts or {"itemKey": item_key}),
                "status": "ready",
            }
        )
        seen_keys[library_id].add(item_key)
        seen_positions[library_id].add(position)

    for library_id, expected_count in expected_counts.items():
        actual_count = len(content_by_library.get(library_id, ()))
        if actual_count != expected_count:
            raise PipelineError(
                f"Library {library_id!r} declares {expected_count} items but "
                f"materializes {actual_count}"
            )
        if seen_positions[library_id] != set(range(expected_count)):
            raise PipelineError(
                f"Library {library_id!r} positions must be contiguous from zero"
            )

    return dict(field_map), libraries_by_id, dict(content_by_library)


def write_bundle_artifacts(
    output_dir: Path,
    *,
    dataset: str,
    locale: str,
    version: str,
    field_items: Sequence[Mapping[str, Any]],
    content_items: Sequence[Mapping[str, Any]],
    libraries: Sequence[Mapping[str, Any]],
    provenance: Mapping[str, Any],
    coverage: Mapping[str, Any],
    checkpoint_key: str,
    batch_size: int = 500,
) -> None:
    target_library_ids = [
        str(library.get("id") or "").strip()
        for library in libraries
        if isinstance(library, Mapping)
    ]
    try:
        if not 1 <= batch_size <= 500:
            raise PipelineError("batch_size must be between 1 and the API limit of 500")
        if not re.fullmatch(r"[0-9a-f]{64}", version):
            raise PipelineError("contentVersion must be a 64-character lowercase hash")
        if not str(checkpoint_key).strip():
            raise PipelineError("checkpoint_key must not be empty")
        field_map, libraries_by_id, content_by_library = _prepare_bundle_artifact_inputs(
            dataset=dataset,
            locale=locale,
            version=version,
            field_items=field_items,
            content_items=content_items,
            libraries=libraries,
        )
    except Exception:
        _invalidate_bundle_artifacts(
            output_dir,
            dataset=dataset,
            locale=locale,
            library_ids=target_library_ids,
        )
        raise

    bundle = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": BUNDLE_KIND,
        "dataset": dataset,
        "locale": locale,
        "contentVersion": version,
        "items": dict(sorted(field_map.items())),
        "content": list(content_items),
    }
    bundle_path = output_dir / "bundles" / safe_filename(dataset) / f"{safe_filename(locale)}.json"
    # Validation succeeded. Remove the previous publication plan and success
    # marker before creating any replacement files, so an interrupted write is
    # fail-closed rather than silently publishable as the previous build.
    _invalidate_bundle_artifacts(
        output_dir,
        dataset=dataset,
        locale=locale,
        library_ids=target_library_ids,
    )
    write_json_if_changed(bundle_path, bundle)

    upsert_dir = output_dir / "upserts" / safe_filename(dataset) / safe_filename(locale)
    expected_names: set[str] = set()
    for start in range(0, len(field_items), batch_size):
        name = f"{start // batch_size + 1:04d}.json"
        expected_names.add(name)
        batch = {
            "schemaVersion": SCHEMA_VERSION,
            "dataset": dataset,
            "locale": locale,
            "contentVersion": version,
            "items": list(field_items[start : start + batch_size]),
        }
        write_json_if_changed(upsert_dir / name, batch)
    # Stale generated batches would otherwise be accidentally posted after a
    # smaller rebuild.  Only this narrow generated directory is cleaned.
    if upsert_dir.exists():
        for path in upsert_dir.glob("*.json"):
            if path.name not in expected_names:
                path.unlink()

    for library_id, materialized_items in sorted(content_by_library.items()):
        library = libraries_by_id[library_id]
        catalog_library = {
            key: value
            for key, value in library.items()
            if key not in {"locale", "contentVersion"}
        }
        catalog_base = {
            "schemaVersion": SCHEMA_VERSION,
            "locale": locale,
            "contentVersion": version,
        }
        draft_library = {**catalog_library, "status": "draft"}
        ready_library = {**catalog_library, "status": library.get("status", "ready")}
        catalog_admin_dir = output_dir / "admin" / "catalog" / safe_filename(locale)
        name = safe_filename(library_id)
        write_json_if_changed(
            catalog_admin_dir / f"{name}.draft.json",
            {**catalog_base, "libraries": [draft_library]},
        )
        write_json_if_changed(
            catalog_admin_dir / f"{name}.ready.json",
            {**catalog_base, "libraries": [ready_library]},
        )

        item_admin_dir = (
            output_dir
            / "admin"
            / "library-items"
            / safe_filename(locale)
            / safe_filename(library_id)
        )
        expected_item_batches: set[str] = set()
        for start in range(0, len(materialized_items), 100):
            batch_name = f"{start // 100 + 1:04d}.json"
            expected_item_batches.add(batch_name)
            write_json_if_changed(
                item_admin_dir / batch_name,
                {
                    "schemaVersion": SCHEMA_VERSION,
                    "locale": locale,
                    "libraryId": library_id,
                    "contentVersion": version,
                    "items": materialized_items[start : start + 100],
                },
            )
        if item_admin_dir.exists():
            for path in item_admin_dir.glob("*.json"):
                if path.name not in expected_item_batches:
                    path.unlink()

    write_json_if_changed(
        output_dir / "provenance" / safe_filename(dataset) / f"{safe_filename(locale)}.json",
        provenance,
    )
    write_json_if_changed(
        output_dir / "reports" / safe_filename(dataset) / f"{safe_filename(locale)}.json",
        coverage,
    )
    update_catalog(output_dir, locale, libraries)
    write_json_if_changed(
        output_dir / ".checkpoints" / safe_filename(dataset) / f"{safe_filename(locale)}.json",
        {
            "schemaVersion": SCHEMA_VERSION,
            "checkpointKey": checkpoint_key,
            "dataset": dataset,
            "locale": locale,
            "bundle": str(bundle_path.relative_to(output_dir)).replace("\\", "/"),
            "bundleSha256": sha256_file(bundle_path),
            "contentVersion": version,
            "libraryIds": sorted(libraries_by_id),
            "complete": True,
        },
    )


def _job_is_complete(
    output_dir: Path,
    dataset: str,
    locale: str,
    checkpoint_key: str,
    library_id: str,
) -> bool:
    checkpoint = output_dir / ".checkpoints" / safe_filename(dataset) / f"{safe_filename(locale)}.json"
    bundle = output_dir / "bundles" / safe_filename(dataset) / f"{safe_filename(locale)}.json"
    if not checkpoint.is_file() or not bundle.is_file():
        return False
    try:
        payload = json.loads(checkpoint.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    expected_bundle_sha256 = str(payload.get("bundleSha256") or "")
    completed_library_ids = {
        str(value) for value in (payload.get("libraryIds") or [])
    }
    return (
        payload.get("complete") is True
        and payload.get("checkpointKey") == checkpoint_key
        and payload.get("dataset") == dataset
        and payload.get("locale") == locale
        and library_id in completed_library_ids
        and re.fullmatch(r"[0-9a-f]{64}", expected_bundle_sha256) is not None
        and sha256_file(bundle) == expected_bundle_sha256
    )


def build_lexical_library(
    manifest: Mapping[str, Any],
    *,
    source_dataset_id: str,
    output_dataset_id: str,
    locale: str,
    adapter: LexicalAdapter,
    output_dir: Path,
    library_id: str,
    name: str,
    description: str,
    source_url: str,
    license_info: Mapping[str, str],
    force: bool = False,
) -> Mapping[str, Any]:
    dataset = get_dataset(manifest, source_dataset_id)
    adapter_fingerprint = adapter.fingerprint()
    checkpoint_key = content_version(
        {
            "stage": "lexical",
            "sourceContentVersion": dataset["contentVersion"],
            "outputDataset": output_dataset_id,
            "locale": locale,
            "adapter": adapter_fingerprint,
            "target": {
                "libraryId": library_id,
                "sourceLibraryId": dataset["sourceLibraryId"],
                "name": name,
                "description": description,
                "sourceName": str(getattr(adapter, "source_name", adapter.provider)),
                "sourceUrl": source_url,
                "license": dict(license_info),
            },
        }
    )
    if not force and _job_is_complete(
        output_dir,
        output_dataset_id,
        locale,
        checkpoint_key,
        library_id,
    ):
        return {"skipped": True, "checkpointKey": checkpoint_key}
    _invalidate_bundle_artifacts(
        output_dir,
        dataset=output_dataset_id,
        locale=locale,
        library_ids=[library_id],
    )

    field_items: list[dict[str, Any]] = []
    content_items: list[dict[str, Any]] = []
    provenance_items: list[dict[str, Any]] = []
    missing: list[str] = []
    for item in dataset.get("items") or []:
        source = select_source(item["fields"]["definition"], locale)
        base = item.get("payload") or {}
        definition_en = str(base.get("definitionEn") or "").strip()
        if not source or not definition_en:
            missing.append(str(item["itemKey"]))
            continue
        word = str(base.get("word") or item["itemKey"])
        result = adapter.lookup(word, definition_en)
        if not result or not result.text.strip():
            missing.append(str(item["itemKey"]))
            continue
        field_items.append(make_upsert_item(str(item["itemKey"]), "definition", source, result.text, result))
        content_items.append(
            {
                "libraryId": library_id,
                "itemKey": str(item["itemKey"]),
                "position": len(content_items),
                "payload": {
                    "word": word,
                    "phonetic": base.get("phonetic") or "",
                    "definitionLocalized": result.text,
                    "definitionEn": definition_en,
                    "example": base.get("example") or "",
                    "contentKey": str(item["itemKey"]),
                    "sourceLibraryId": dataset["sourceLibraryId"],
                },
            }
        )
        provenance_items.append(
            {
                "itemKey": str(item["itemKey"]),
                "sourceRef": result.source_ref,
                "score": result.score,
                "details": dict(result.details),
            }
        )

    version = content_version(
        {
            "dataset": output_dataset_id,
            "locale": locale,
            "sourceContentVersion": dataset["contentVersion"],
            "adapter": adapter_fingerprint,
            "items": field_items,
        }
    )
    coverage = {
        "schemaVersion": SCHEMA_VERSION,
        "dataset": output_dataset_id,
        "locale": locale,
        "requested": len(dataset.get("items") or []),
        "translated": len(field_items),
        "missing": len(missing),
        "coverage": round(len(field_items) / max(1, len(dataset.get("items") or [])), 6),
        "missingItemKeys": missing,
    }
    catalog_library = localized_library_metadata(
        locale=locale,
        library_id=library_id,
        content_type="words",
        dataset=output_dataset_id,
        source_library_id=str(dataset["sourceLibraryId"]),
        name=name,
        description=description,
        format_name=f"{adapter.provider} · {LOCALE_LABELS.get(locale, locale)}",
        item_count=len(content_items),
        source={
            "name": str(getattr(adapter, "source_name", adapter.provider)),
            "url": source_url,
        },
        license_info=license_info,
        version=version,
    )
    provenance = {
        "schemaVersion": SCHEMA_VERSION,
        "dataset": output_dataset_id,
        "locale": locale,
        "sourceDataset": source_dataset_id,
        "sourceContentVersion": dataset["contentVersion"],
        "adapter": adapter_fingerprint,
        "source": {"url": source_url, "license": dict(license_info)},
        "items": provenance_items,
    }
    write_bundle_artifacts(
        output_dir,
        dataset=output_dataset_id,
        locale=locale,
        version=version,
        field_items=field_items,
        content_items=content_items,
        libraries=[catalog_library],
        provenance=provenance,
        coverage=coverage,
        checkpoint_key=checkpoint_key,
    )
    return coverage


def iter_tsv_bz2(path: Path) -> Iterator[list[str]]:
    with bz2.open(path, "rt", encoding="utf-8", newline="") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.rstrip("\r\n")
            if not line:
                continue
            columns = line.split("\t")
            if len(columns) < 2:
                raise PipelineError(f"Malformed TSV row at {path}:{line_number}")
            yield columns


def _normalized_tatoeba_text(value: Any) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(value or "")).strip().split())


def _read_tatoeba_sentence_subset(
    path: Path,
    wanted_ids: set[int],
    expected_language: str,
) -> dict[int, str]:
    sentences: dict[int, str] = {}
    for columns in iter_tsv_bz2(path):
        if len(columns) < 3:
            raise PipelineError(f"Tatoeba sentence rows need id, language and text: {path}")
        try:
            sentence_id = int(columns[0])
        except ValueError as error:
            raise PipelineError(f"Invalid Tatoeba sentence id {columns[0]!r} in {path}") from error
        if sentence_id <= 0:
            raise PipelineError(f"Tatoeba sentence ids must be positive in {path}")
        language = columns[1].strip()
        if language != expected_language:
            raise PipelineError(
                f"Expected Tatoeba language {expected_language!r}, got {language!r} in {path}"
            )
        if sentence_id not in wanted_ids:
            continue
        text = _normalized_tatoeba_text(columns[2])
        if not text:
            continue
        previous = sentences.get(sentence_id)
        if previous is not None and previous != text:
            raise PipelineError(
                f"Tatoeba sentence id {sentence_id} has conflicting text in {path}"
            )
        sentences[sentence_id] = text
    return sentences


def _tatoeba_direct_pair_is_suitable(
    english: str,
    target: str,
    *,
    locale: str,
    min_words: int,
    max_words: int,
    max_english_chars: int,
    max_target_chars: int,
) -> bool:
    if not TATOEBA_ENGLISH_SHAPE.fullmatch(english):
        return False
    words = TATOEBA_ENGLISH_WORD.findall(english)
    if not min_words <= len(words) <= max_words:
        return False
    if not 8 <= len(english) <= max_english_chars:
        return False
    if max(map(len, words), default=0) > 20:
        return False
    if not target or len(target) > max_target_chars:
        return False
    if TATOEBA_UNSAFE_TEXT.search(english) or TATOEBA_UNSAFE_TEXT.search(target):
        return False
    if any(unicodedata.category(character) in {"Cc", "Cs"} for character in english + target):
        return False
    target_script = TATOEBA_TARGET_SCRIPT.get(locale)
    if target_script is None or not target_script.search(target):
        return False
    return normalize_key(english) != normalize_key(target)


def select_tatoeba_direct_pairs(
    english_sentences_path: Path,
    links_path: Path,
    target_sentences_path: Path,
    *,
    locale: str,
    target_count: int = 1000,
    min_words: int = 2,
    max_words: int = 16,
    max_english_chars: int = 115,
    max_target_chars: int = 240,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Select direct official Tatoeba pairs without consulting Chinese content."""

    if locale not in TATOEBA_CODES:
        raise PipelineError(f"Tatoeba direct builder needs one of: {', '.join(TATOEBA_CODES)}")
    if not 1 <= target_count <= 10_000:
        raise PipelineError("target_count must be between 1 and 10000")
    if not 1 <= min_words <= max_words <= 100:
        raise PipelineError("word limits must satisfy 1 <= min_words <= max_words <= 100")
    if not 8 <= max_english_chars <= 20_000:
        raise PipelineError("max_english_chars must be between 8 and 20000")
    if not 1 <= max_target_chars <= 20_000:
        raise PipelineError("max_target_chars must be between 1 and 20000")

    link_rows = 0
    invalid_link_rows = 0
    links: set[tuple[int, int]] = set()
    for columns in iter_tsv_bz2(links_path):
        link_rows += 1
        try:
            english_id, target_id = int(columns[0]), int(columns[1])
        except ValueError as error:
            raise PipelineError(f"Invalid Tatoeba link ids in {links_path}") from error
        if english_id <= 0 or target_id <= 0:
            invalid_link_rows += 1
            continue
        links.add((english_id, target_id))

    english_ids = {english_id for english_id, _ in links}
    target_ids = {target_id for _, target_id in links}
    target_code = TATOEBA_CODES[locale]
    english_sentences = _read_tatoeba_sentence_subset(
        english_sentences_path,
        english_ids,
        "eng",
    )
    target_sentences = _read_tatoeba_sentence_subset(
        target_sentences_path,
        target_ids,
        target_code,
    )

    target_ids_by_english: defaultdict[int, list[int]] = defaultdict(list)
    for english_id, target_id in sorted(links):
        target_ids_by_english[english_id].append(target_id)

    selected: list[dict[str, Any]] = []
    seen_english_text: set[str] = set()
    seen_target_text: set[str] = set()
    missing_english = 0
    missing_target = 0
    filtered_pairs = 0
    duplicate_english = 0
    duplicate_target = 0
    for english_id in sorted(target_ids_by_english):
        english_text = english_sentences.get(english_id)
        if not english_text:
            missing_english += 1
            continue
        normalized_english = normalize_key(english_text)
        if normalized_english in seen_english_text:
            duplicate_english += 1
            continue
        chosen: tuple[int, str, str] | None = None
        for target_id in target_ids_by_english[english_id]:
            target_text = target_sentences.get(target_id)
            if not target_text:
                missing_target += 1
                continue
            if not _tatoeba_direct_pair_is_suitable(
                english_text,
                target_text,
                locale=locale,
                min_words=min_words,
                max_words=max_words,
                max_english_chars=max_english_chars,
                max_target_chars=max_target_chars,
            ):
                filtered_pairs += 1
                continue
            normalized_target = normalize_key(target_text)
            if normalized_target in seen_target_text:
                duplicate_target += 1
                continue
            chosen = (target_id, target_text, normalized_target)
            break
        if chosen is None:
            continue
        target_id, target_text, normalized_target = chosen
        selected.append(
            {
                "itemKey": str(english_id),
                "englishId": english_id,
                "targetId": target_id,
                "english": english_text,
                "target": target_text,
            }
        )
        seen_english_text.add(normalized_english)
        seen_target_text.add(normalized_target)
        if len(selected) == target_count:
            break

    report = {
        "policyVersion": TATOEBA_DIRECT_POLICY_VERSION,
        "targetCount": target_count,
        "selected": len(selected),
        "linkRows": link_rows,
        "uniqueLinks": len(links),
        "duplicateLinks": link_rows - invalid_link_rows - len(links),
        "invalidLinkRows": invalid_link_rows,
        "missingEnglish": missing_english,
        "missingTarget": missing_target,
        "filteredPairs": filtered_pairs,
        "duplicateEnglish": duplicate_english,
        "duplicateTarget": duplicate_target,
        "filters": {
            "minWords": min_words,
            "maxWords": max_words,
            "maxEnglishChars": max_english_chars,
            "maxTargetChars": max_target_chars,
        },
    }
    if len(selected) < target_count:
        raise PipelineError(
            f"Tatoeba direct selection found {len(selected)} suitable unique pairs; "
            f"{target_count} are required"
        )
    return selected, report


def match_tatoeba_translations(
    source_items: Sequence[Mapping[str, Any]],
    links_path: Path,
    target_sentences_path: Path,
    *,
    english_sentences_path: Path | None = None,
    stage_cache_path: Path | None = None,
) -> tuple[dict[str, tuple[int, int, str]], dict[str, Any]]:
    """Match local source items to one deterministic direct target sentence."""

    by_key = {str(item["itemKey"]): item for item in source_items}
    english_ids: dict[int, str] = {}
    unresolved_texts: dict[str, str] = {}
    for key, item in by_key.items():
        source_ids = (item.get("payload") or {}).get("sourceIds") or []
        source_english_id = next(
            (
                int(value)
                for value in source_ids[:1]
                if str(value).isdigit() and int(value) > 0
            ),
            None,
        )
        if source_english_id is not None:
            english_ids[source_english_id] = key
            continue
        try:
            numeric_key = int(key)
        except ValueError:
            text = normalize_key((item.get("payload") or {}).get("text"))
            if text:
                unresolved_texts[text] = key
        else:
            if numeric_key > 0:
                english_ids[numeric_key] = key

    if unresolved_texts:
        if not english_sentences_path:
            raise PipelineError(
                "Source items without numeric Tatoeba IDs require --english-sentences"
            )
        for columns in iter_tsv_bz2(english_sentences_path):
            sentence_id = int(columns[0])
            text = normalize_key(columns[2] if len(columns) >= 3 else columns[-1])
            key = unresolved_texts.get(text)
            if key:
                english_ids[sentence_id] = key

    stage_key = content_version(
        {
            "sourceKeys": sorted(english_ids.items()),
            "linksSha256": sha256_file(links_path),
            "targetSha256": sha256_file(target_sentences_path),
        }
    )
    if stage_cache_path and stage_cache_path.is_file():
        cached = json.loads(stage_cache_path.read_text(encoding="utf-8"))
        if cached.get("stageKey") == stage_key:
            return {
                key: (
                    int(value["englishId"]),
                    int(value["targetId"]),
                    str(value["text"]),
                )
                for key, value in (cached.get("matches") or {}).items()
            }, {"stageKey": stage_key, "cacheHit": True}

    wanted_ids = set(english_ids)
    candidates: dict[int, int] = {}
    link_rows = 0
    for columns in iter_tsv_bz2(links_path):
        link_rows += 1
        left, right = int(columns[0]), int(columns[1])
        if left in wanted_ids:
            candidates[left] = min(right, candidates.get(left, right))
    wanted_target_ids = set(candidates.values())
    target_texts: dict[int, str] = {}
    target_rows = 0
    for columns in iter_tsv_bz2(target_sentences_path):
        target_rows += 1
        sentence_id = int(columns[0])
        if sentence_id in wanted_target_ids:
            target_texts[sentence_id] = columns[2] if len(columns) >= 3 else columns[-1]

    matches: dict[str, tuple[int, int, str]] = {}
    for english_id, target_id in candidates.items():
        text = target_texts.get(target_id, "").strip()
        if text:
            matches[english_ids[english_id]] = (english_id, target_id, text)
    if stage_cache_path:
        write_json_if_changed(
            stage_cache_path,
            {
                "schemaVersion": SCHEMA_VERSION,
                "stageKey": stage_key,
                "matches": {
                    key: {
                        "englishId": value[0],
                        "targetId": value[1],
                        "text": value[2],
                    }
                    for key, value in sorted(matches.items())
                },
            },
        )
    return matches, {
        "stageKey": stage_key,
        "cacheHit": False,
        "linkRows": link_rows,
        "targetRows": target_rows,
    }


def build_tatoeba_library(
    manifest: Mapping[str, Any],
    *,
    source_dataset_id: str,
    output_dataset_id: str,
    locale: str,
    links_path: Path,
    target_sentences_path: Path,
    output_dir: Path,
    library_id: str,
    name: str,
    description: str,
    english_sentences_path: Path | None = None,
    force: bool = False,
) -> Mapping[str, Any]:
    if locale not in TATOEBA_CODES:
        raise PipelineError(f"Tatoeba builder needs one of: {', '.join(TATOEBA_CODES)}")
    dataset = get_dataset(manifest, source_dataset_id)
    target_code = TATOEBA_CODES[locale]
    source_url = (
        "https://downloads.tatoeba.org/exports/per_language/eng/"
        f"eng-{target_code}_links.tsv.bz2"
    )
    checkpoint_key = content_version(
        {
            "stage": "tatoeba",
            "sourceContentVersion": dataset["contentVersion"],
            "outputDataset": output_dataset_id,
            "locale": locale,
            "linksSha256": sha256_file(links_path),
            "targetSha256": sha256_file(target_sentences_path),
            "englishSha256": (
                sha256_file(english_sentences_path)
                if english_sentences_path is not None
                else None
            ),
            "target": {
                "libraryId": library_id,
                "sourceLibraryId": dataset["sourceLibraryId"],
                "name": name,
                "description": description,
                "sourceUrl": source_url,
                "license": dict(TATOEBA_LICENSE),
            },
        }
    )
    if not force and _job_is_complete(
        output_dir,
        output_dataset_id,
        locale,
        checkpoint_key,
        library_id,
    ):
        return {"skipped": True, "checkpointKey": checkpoint_key}
    _invalidate_bundle_artifacts(
        output_dir,
        dataset=output_dataset_id,
        locale=locale,
        library_ids=[library_id],
    )

    stage_cache = (
        output_dir
        / ".checkpoints"
        / "tatoeba-stage"
        / f"{safe_filename(source_dataset_id)}-{safe_filename(locale)}.json"
    )
    matches, stage_report = match_tatoeba_translations(
        dataset.get("items") or [],
        links_path,
        target_sentences_path,
        english_sentences_path=english_sentences_path,
        stage_cache_path=stage_cache,
    )
    field_items: list[dict[str, Any]] = []
    content_items: list[dict[str, Any]] = []
    provenance_items: list[dict[str, Any]] = []
    missing: list[str] = []
    for item in dataset.get("items") or []:
        item_key = str(item["itemKey"])
        match = matches.get(item_key)
        source = select_source(item["fields"]["translation"], locale)
        if not match or not source:
            missing.append(item_key)
            continue
        english_id, target_id, translated_text = match
        result = LookupResult(
            text=translated_text,
            provider="tatoeba",
            model=f"eng-{target_code}",
            source_ref=f"tatoeba:{item_key}:{target_id}",
            details={"englishSentenceId": english_id, "targetSentenceId": target_id},
        )
        field_items.append(
            make_upsert_item(item_key, "translation", source, translated_text, result)
        )
        base = item.get("payload") or {}
        content_items.append(
            {
                "libraryId": library_id,
                "itemKey": item_key,
                "position": len(content_items),
                "payload": {
                    "scene": base.get("scene") or "generalConversation",
                    "text": base.get("text") or source["text"],
                    "translationLocalized": translated_text,
                    "sourceIds": [english_id, target_id],
                    "contentKey": item_key,
                    "sourceLibraryId": dataset["sourceLibraryId"],
                },
            }
        )
        provenance_items.append({"itemKey": item_key, **dict(result.details)})

    version = content_version(
        {
            "dataset": output_dataset_id,
            "locale": locale,
            "sourceContentVersion": dataset["contentVersion"],
            "stageKey": stage_report["stageKey"],
            "items": field_items,
        }
    )
    coverage = {
        "schemaVersion": SCHEMA_VERSION,
        "dataset": output_dataset_id,
        "locale": locale,
        "requested": len(dataset.get("items") or []),
        "translated": len(field_items),
        "missing": len(missing),
        "coverage": round(len(field_items) / max(1, len(dataset.get("items") or [])), 6),
        "missingItemKeys": missing,
        "scan": stage_report,
    }
    catalog_library = localized_library_metadata(
        locale=locale,
        library_id=library_id,
        content_type="sentences",
        dataset=output_dataset_id,
        source_library_id=str(dataset["sourceLibraryId"]),
        name=name,
        description=description,
        format_name=f"Tatoeba · English/{target_code}",
        item_count=len(content_items),
        source={"name": "Tatoeba", "url": source_url},
        license_info=TATOEBA_LICENSE,
        version=version,
        display_order=200,
    )
    provenance = {
        "schemaVersion": SCHEMA_VERSION,
        "dataset": output_dataset_id,
        "locale": locale,
        "sourceDataset": source_dataset_id,
        "sourceContentVersion": dataset["contentVersion"],
        "source": {"name": "Tatoeba", "url": source_url, "license": TATOEBA_LICENSE},
        "inputs": {
            "links": {"path": str(links_path), "sha256": sha256_file(links_path)},
            "targetSentences": {
                "path": str(target_sentences_path),
                "sha256": sha256_file(target_sentences_path),
            },
            "englishSentences": (
                {
                    "path": str(english_sentences_path),
                    "sha256": sha256_file(english_sentences_path),
                }
                if english_sentences_path is not None
                else None
            ),
        },
        "items": provenance_items,
    }
    write_bundle_artifacts(
        output_dir,
        dataset=output_dataset_id,
        locale=locale,
        version=version,
        field_items=field_items,
        content_items=content_items,
        libraries=[catalog_library],
        provenance=provenance,
        coverage=coverage,
        checkpoint_key=checkpoint_key,
    )
    return coverage


def build_tatoeba_direct_library(
    *,
    output_dataset_id: str,
    locale: str,
    english_sentences_path: Path,
    links_path: Path,
    target_sentences_path: Path,
    output_dir: Path,
    library_id: str,
    name: str,
    description: str,
    source_library_id: str | None = None,
    target_count: int = 1000,
    min_words: int = 2,
    max_words: int = 16,
    max_english_chars: int = 115,
    max_target_chars: int = 240,
    force: bool = False,
) -> Mapping[str, Any]:
    """Build a standalone locale library from official direct Tatoeba links."""

    if locale not in TATOEBA_CODES:
        raise PipelineError(f"Tatoeba direct builder needs one of: {', '.join(TATOEBA_CODES)}")
    if output_dataset_id != "sentences-common":
        raise PipelineError(
            "Tatoeba direct libraries must use the API-whitelisted "
            "sentences-common dataset"
        )
    target_code = TATOEBA_CODES[locale]
    resolved_source_library_id = (
        str(source_library_id).strip()
        if source_library_id and str(source_library_id).strip()
        else f"tatoeba-eng-{target_code}"
    )
    input_fingerprints = {
        "englishSentences": sha256_file(english_sentences_path),
        "links": sha256_file(links_path),
        "targetSentences": sha256_file(target_sentences_path),
    }
    selection_parameters = {
        "targetCount": target_count,
        "minWords": min_words,
        "maxWords": max_words,
        "maxEnglishChars": max_english_chars,
        "maxTargetChars": max_target_chars,
    }
    checkpoint_key = content_version(
        {
            "stage": TATOEBA_DIRECT_POLICY_VERSION,
            "dataset": output_dataset_id,
            "locale": locale,
            "libraryId": library_id,
            "sourceLibraryId": resolved_source_library_id,
            "name": name,
            "description": description,
            "inputs": input_fingerprints,
            "selection": selection_parameters,
        }
    )
    if not force and _job_is_complete(
        output_dir,
        output_dataset_id,
        locale,
        checkpoint_key,
        library_id,
    ):
        return {"skipped": True, "checkpointKey": checkpoint_key}
    _invalidate_bundle_artifacts(
        output_dir,
        dataset=output_dataset_id,
        locale=locale,
        library_ids=[library_id],
    )

    pairs, selection_report = select_tatoeba_direct_pairs(
        english_sentences_path,
        links_path,
        target_sentences_path,
        locale=locale,
        target_count=target_count,
        min_words=min_words,
        max_words=max_words,
        max_english_chars=max_english_chars,
        max_target_chars=max_target_chars,
    )
    field_items: list[dict[str, Any]] = []
    content_items: list[dict[str, Any]] = []
    provenance_items: list[dict[str, Any]] = []
    for position, pair in enumerate(pairs):
        item_key = str(pair["itemKey"])
        english_id = int(pair["englishId"])
        target_id = int(pair["targetId"])
        english_text = str(pair["english"])
        target_text = str(pair["target"])
        source = make_source(english_text, "en", "Tatoeba sentence text")
        if source is None:
            raise PipelineError(f"Tatoeba English sentence {english_id} is empty")
        result = LookupResult(
            text=target_text,
            provider="tatoeba",
            model=f"direct-eng-{target_code}",
            source_ref=f"tatoeba:eng:{english_id}:{target_code}:{target_id}",
            details={
                "englishSentenceId": english_id,
                "targetSentenceId": target_id,
            },
        )
        field_items.append(
            make_upsert_item(
                item_key,
                "translation",
                source,
                target_text,
                result,
            )
        )
        content_items.append(
            {
                "libraryId": library_id,
                "itemKey": item_key,
                "position": position,
                "payload": {
                    "scene": "generalConversation",
                    "text": english_text,
                    "translationLocalized": target_text,
                    "sourceIds": [english_id, target_id],
                    "contentKey": item_key,
                    "sourceLibraryId": resolved_source_library_id,
                },
            }
        )
        provenance_items.append(
            {
                "itemKey": item_key,
                "englishSentenceId": english_id,
                "targetSentenceId": target_id,
                "englishSourceHash": sha256_text(english_text),
                "targetSourceHash": sha256_text(target_text),
                "englishUrl": f"https://tatoeba.org/en/sentences/show/{english_id}",
                "targetUrl": f"https://tatoeba.org/en/sentences/show/{target_id}",
            }
        )

    version = content_version(
        {
            "dataset": output_dataset_id,
            "locale": locale,
            "policyVersion": TATOEBA_DIRECT_POLICY_VERSION,
            "sourceLibraryId": resolved_source_library_id,
            "inputs": input_fingerprints,
            "selection": selection_parameters,
            "items": field_items,
        }
    )
    source_url = (
        "https://downloads.tatoeba.org/exports/per_language/eng/"
        f"eng-{target_code}_links.tsv.bz2"
    )
    catalog_library = localized_library_metadata(
        locale=locale,
        library_id=library_id,
        content_type="sentences",
        dataset=output_dataset_id,
        source_library_id=resolved_source_library_id,
        name=name,
        description=description,
        format_name=f"Tatoeba · English/{target_code} · direct",
        item_count=len(content_items),
        source={
            "name": "Tatoeba contributors",
            "url": "https://tatoeba.org/",
            "notice": TATOEBA_LICENSE["notice"],
        },
        license_info=TATOEBA_LICENSE,
        version=version,
        display_order=200,
    )
    coverage = {
        "schemaVersion": SCHEMA_VERSION,
        "dataset": output_dataset_id,
        "locale": locale,
        "requested": target_count,
        "materializedItems": len(content_items),
        "selection": selection_report,
    }
    provenance = {
        "schemaVersion": SCHEMA_VERSION,
        "dataset": output_dataset_id,
        "locale": locale,
        "policyVersion": TATOEBA_DIRECT_POLICY_VERSION,
        "checkpointKey": checkpoint_key,
        "contentVersion": version,
        "source": {
            "name": "Tatoeba contributors",
            "url": "https://tatoeba.org/",
            "license": dict(TATOEBA_LICENSE),
        },
        "inputs": {
            "englishSentences": {
                "path": str(english_sentences_path.resolve()),
                "url": (
                    "https://downloads.tatoeba.org/exports/per_language/eng/"
                    "eng_sentences.tsv.bz2"
                ),
                "sha256": input_fingerprints["englishSentences"],
            },
            "links": {
                "path": str(links_path.resolve()),
                "url": source_url,
                "sha256": input_fingerprints["links"],
            },
            "targetSentences": {
                "path": str(target_sentences_path.resolve()),
                "url": (
                    "https://downloads.tatoeba.org/exports/per_language/"
                    f"{target_code}/{target_code}_sentences.tsv.bz2"
                ),
                "sha256": input_fingerprints["targetSentences"],
            },
        },
        "selection": selection_report,
        "items": provenance_items,
    }
    write_bundle_artifacts(
        output_dir,
        dataset=output_dataset_id,
        locale=locale,
        version=version,
        field_items=field_items,
        content_items=content_items,
        libraries=[catalog_library],
        provenance=provenance,
        coverage=coverage,
        checkpoint_key=checkpoint_key,
    )
    return coverage


def _flatten_translation_map(payload: Mapping[str, Any]) -> dict[tuple[str, str], str]:
    raw_items = payload.get("items") if isinstance(payload.get("items"), Mapping) else payload
    flattened: dict[tuple[str, str], str] = {}
    for raw_key, raw_value in raw_items.items():
        item_key = str(raw_key)
        if isinstance(raw_value, str):
            flattened[(item_key, "translation")] = raw_value
            continue
        if not isinstance(raw_value, Mapping):
            continue
        fields = raw_value.get("fields") if isinstance(raw_value.get("fields"), Mapping) else raw_value
        for output_field, value in fields.items():
            if output_field == "sentences" and isinstance(value, Mapping):
                for sentence_index, sentence_value in value.items():
                    flattened[(item_key, f"sentences.{sentence_index}")] = str(sentence_value)
            elif isinstance(value, str):
                flattened[(item_key, str(output_field))] = value
    return flattened


def build_reviewed_translation_libraries(
    manifest: Mapping[str, Any],
    *,
    source_dataset_id: str,
    output_dataset_id: str,
    locale: str,
    translations_path: Path,
    output_dir: Path,
    library_id: str,
    name: str,
    description: str,
    provider: str,
    model: str,
    source_url: str,
    license_info: Mapping[str, str],
    force: bool = False,
) -> Mapping[str, Any]:
    """Materialise reviewed/offline-MT translations for any manifest dataset."""

    dataset = get_dataset(manifest, source_dataset_id)
    raw = json.loads(translations_path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise PipelineError("Reviewed translations must be a JSON object")
    if raw.get("kind") is not None and raw.get("kind") != REVIEWED_MAP_KIND:
        raise PipelineError(f"Unsupported reviewed translation map: {translations_path}")
    if raw.get("kind") == REVIEWED_MAP_KIND:
        expected_metadata = {
            "schemaVersion": SCHEMA_VERSION,
            "locale": locale,
            "sourceDataset": source_dataset_id,
            "sourceContentVersion": dataset["contentVersion"],
        }
        mismatches = [
            field_name
            for field_name, expected_value in expected_metadata.items()
            if raw.get(field_name) != expected_value
        ]
        if mismatches:
            raise PipelineError(
                "Reviewed translation map does not match the requested source: "
                + ", ".join(mismatches)
            )
    translated = _flatten_translation_map(raw)
    checkpoint_key = content_version(
        {
            "stage": "reviewed-translations",
            "sourceContentVersion": dataset["contentVersion"],
            "translationSha256": sha256_file(translations_path),
            "outputDataset": output_dataset_id,
            "locale": locale,
            "provider": provider,
            "model": model,
            "target": {
                "libraryId": library_id,
                "sourceLibraryId": dataset["sourceLibraryId"],
                "name": name,
                "description": description,
                "sourceUrl": source_url,
                "license": dict(license_info),
            },
        }
    )
    if not force and _job_is_complete(
        output_dir,
        output_dataset_id,
        locale,
        checkpoint_key,
        library_id,
    ):
        return {"skipped": True, "checkpointKey": checkpoint_key}
    _invalidate_bundle_artifacts(
        output_dir,
        dataset=output_dataset_id,
        locale=locale,
        library_ids=[library_id],
    )

    field_items: list[dict[str, Any]] = []
    content_items: list[dict[str, Any]] = []
    missing: list[str] = []
    provenance_items: list[dict[str, str]] = []
    content_type = str(dataset["type"])
    for item in dataset.get("items") or []:
        item_key = str(item["itemKey"])
        base = dict(item.get("payload") or {})
        if content_type == "words" and not str(base.get("definitionEn") or "").strip():
            missing.append(item_key)
            continue
        values: dict[str, str] = {}
        item_missing = False
        for output_field, field_value in item.get("fields", {}).items():
            value = str(translated.get((item_key, output_field), "")).strip()
            source = select_source(field_value, locale)
            if not value or not source:
                item_missing = True
                continue
            values[output_field] = value
            field_items.append(
                make_upsert_item(
                    item_key,
                    output_field,
                    source,
                    value,
                    provider=provider,
                    model=model,
                    status="reviewed",
                )
            )
        if not values:
            missing.append(item_key)
            continue
        if item_missing:
            missing.append(item_key)
            # A locale library is standalone and must never expose a partly
            # translated item whose empty fields could fall back to Chinese.
            continue
        provenance_source_library_id = str(
            item.get("sourceLibraryId") or dataset["sourceLibraryId"]
        )
        source_library_id = str(dataset["sourceLibraryId"])
        if content_type == "words":
            payload = {
                "word": base.get("word") or item_key,
                "phonetic": base.get("phonetic") or "",
                "definitionLocalized": values.get("definition", ""),
                "definitionEn": str(base.get("definitionEn") or "").strip(),
                "example": base.get("example") or "",
                "contentKey": item_key,
                "sourceLibraryId": source_library_id,
            }
        elif content_type == "sentences":
            payload = {
                "scene": base.get("scene") or "generalConversation",
                "text": base.get("text") or "",
                "translationLocalized": values.get("translation", ""),
                "sourceIds": base.get("sourceIds") or [],
                "contentKey": item_key,
                "sourceLibraryId": source_library_id,
            }
        elif content_type == "articles":
            def canonical_metadata(field_name: str) -> str:
                field_sources = (
                    ((item.get("fields") or {}).get(field_name) or {}).get("sources")
                    or {}
                )
                english_source = field_sources.get("en") or {}
                english_text = str(english_source.get("text") or "").strip()
                if english_text:
                    return english_text
                explicit = str(base.get(f"{field_name}En") or "").strip()
                if explicit:
                    return explicit
                return canonical_article_metadata(field_name, base.get(field_name))

            localized_sentences = []
            for index, sentence in enumerate(base.get("sentences") or []):
                localized_sentences.append(
                    {
                        "en": sentence.get("en") or "",
                        "translationLocalized": values.get(f"sentences.{index}", ""),
                    }
                )
            payload = {
                "id": base.get("id") or item_key,
                "title": base.get("title") or "",
                "titleLocalized": values.get("title", ""),
                "summaryLocalized": values.get("summary", ""),
                "level": canonical_metadata("level"),
                "levelLocalized": values.get("level", ""),
                "cefr": base.get("cefr") or "",
                "genre": canonical_metadata("genre"),
                "genreLocalized": values.get("genre", ""),
                "topic": canonical_metadata("topic"),
                "topicLocalized": values.get("topic", ""),
                "estimatedWords": base.get("estimatedWords") or 0,
                "sentences": localized_sentences,
                "contentKey": item_key,
                "sourceLibraryId": source_library_id,
                "provenanceSourceLibraryId": provenance_source_library_id,
            }
        else:
            raise PipelineError(f"Unsupported content type: {content_type}")
        entry = {
            "libraryId": library_id,
            "itemKey": item_key,
            "position": len(content_items),
            "payload": payload,
        }
        content_items.append(entry)
        provenance_items.append(
            {
                "itemKey": item_key,
                "sourceLibraryId": provenance_source_library_id,
            }
        )

    if locale == "zh-Hant" and missing:
        unique_missing = sorted(set(missing))
        preview = ", ".join(unique_missing[:5])
        raise PipelineError(
            "A Traditional Chinese library requires complete zh-Hans coverage; "
            f"{len(unique_missing)} items have missing fields ({preview})"
        )

    version = content_version(
        {
            "dataset": output_dataset_id,
            "locale": locale,
            "sourceContentVersion": dataset["contentVersion"],
            "translations": field_items,
        }
    )
    # A locale may expose only one ready library for a dataset.  Each graded
    # article shelf therefore has its own stable dataset, while the aggregate
    # shelf remains separately selectable and repeated article IDs stay scoped
    # to their dataset.
    catalog_libraries = [
        localized_library_metadata(
            locale=locale,
            library_id=library_id,
            content_type=content_type,
            dataset=output_dataset_id,
            source_library_id=str(dataset["sourceLibraryId"]),
            name=name,
            description=description,
            format_name=f"{provider} · reviewed",
            item_count=len(content_items),
            source={"name": provider, "url": source_url},
            license_info=license_info,
            version=version,
            display_order=(
                ARTICLE_SOURCE_DISPLAY_ORDER.get(str(dataset["sourceLibraryId"]), 300)
                if content_type == "articles"
                else 100
            ),
        )
    ]
    coverage = {
        "schemaVersion": SCHEMA_VERSION,
        "dataset": output_dataset_id,
        "locale": locale,
        "requestedItems": len(dataset.get("items") or []),
        "materializedItems": len(content_items),
        "translatedFields": len(field_items),
        "itemsWithMissingFields": len(set(missing)),
        "missingItemKeys": sorted(set(missing)),
    }
    provenance = {
        "schemaVersion": SCHEMA_VERSION,
        "dataset": output_dataset_id,
        "locale": locale,
        "sourceDataset": source_dataset_id,
        "sourceContentVersion": dataset["contentVersion"],
        "translationInput": {
            "path": str(translations_path.resolve()),
            "sha256": sha256_file(translations_path),
        },
        "provider": provider,
        "model": model,
        "source": {"url": source_url, "license": dict(license_info)},
        "items": provenance_items,
    }
    write_bundle_artifacts(
        output_dir,
        dataset=output_dataset_id,
        locale=locale,
        version=version,
        field_items=field_items,
        content_items=content_items,
        libraries=catalog_libraries,
        provenance=provenance,
        coverage=coverage,
        checkpoint_key=checkpoint_key,
    )
    return coverage


def _load_opencc_hant_converter() -> tuple[Any, Mapping[str, Any]]:
    """Load the optional OpenCC s2t converter from the development environment."""

    try:
        from opencc import OpenCC
    except ImportError as error:
        raise PipelineError(
            "opencc-hant requires opencc-python-reimplemented on the development "
            "host; install tools/requirements-i18n.txt"
        ) from error

    try:
        converter = OpenCC("s2t")
    except Exception as error:
        raise PipelineError("OpenCC could not load the s2t conversion profile") from error

    package_name = "opencc-python-reimplemented"
    try:
        package_version = importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        package_name = "OpenCC"
        try:
            package_version = importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            package_version = "unknown"
    return converter, {
        "provider": "OpenCC",
        "packageName": package_name,
        "packageVersion": package_version,
        "model": "s2t",
    }


def _zh_hans_segments(dataset: Mapping[str, Any]) -> list[dict[str, str]]:
    """Collect every exact zh-Hans field source or fail before conversion starts."""

    segments: list[dict[str, str]] = []
    missing: list[str] = []
    seen: set[str] = set()
    for item in dataset.get("items") or []:
        item_key = str(item.get("itemKey") or "")
        fields = item.get("fields") or {}
        if not item_key or "\x00" in item_key or not isinstance(fields, Mapping) or not fields:
            missing.append(f"{item_key or '<empty>'}:*")
            continue
        for output_field, field_value in fields.items():
            field_name = str(output_field)
            segment_key = f"{item_key}\x00{field_name}"
            if "\x00" in field_name or segment_key in seen:
                raise PipelineError(
                    f"Duplicate or invalid source segment {item_key}:{field_name}"
                )
            seen.add(segment_key)
            if not isinstance(field_value, Mapping):
                missing.append(f"{item_key}:{field_name}")
                continue
            sources = field_value.get("sources") or {}
            source = sources.get("zh-Hans") if isinstance(sources, Mapping) else None
            if not isinstance(source, Mapping):
                missing.append(f"{item_key}:{field_name}")
                continue
            source_text = str(source.get("text") or "")
            source_hash = str(source.get("sourceHash") or "")
            if (
                source.get("lang") != "zh-Hans"
                or not source_text.strip()
                or "\x00" in source_text
                or source_hash != sha256_text(source_text)
            ):
                missing.append(f"{item_key}:{field_name}")
                continue
            segments.append(
                {
                    "segmentKey": segment_key,
                    "itemKey": item_key,
                    "field": field_name,
                    "sourceText": source_text,
                    "sourceHash": source_hash,
                    "sourceField": str(source.get("sourceField") or ""),
                }
            )
    if missing:
        preview = ", ".join(missing[:5])
        raise PipelineError(
            f"Dataset {dataset.get('dataset')!r} lacks valid zh-Hans source text for "
            f"{len(missing)} fields ({preview})"
        )
    return segments


def generate_opencc_hant_translations(
    manifest: Mapping[str, Any],
    *,
    source_dataset_id: str,
    output_path: Path,
    checkpoint_dir: Path | None = None,
    batch_size: int = 100,
    converter: Any | None = None,
    converter_info: Mapping[str, Any] | None = None,
    force: bool = False,
) -> Mapping[str, Any]:
    """Generate a complete, resumable zh-Hant reviewed-map using OpenCC s2t.

    Only the final all-fields map is written to ``output_path``.  Partial work
    is confined to an atomic checkpoint and can never be consumed by the
    existing ``reviewed``/``publish`` path as a finished translation map.
    """

    if not 1 <= batch_size <= 1_000:
        raise PipelineError("OpenCC checkpoint batch size must be between 1 and 1000")
    dataset = get_dataset(manifest, source_dataset_id)
    if dataset.get("type") not in {"words", "sentences", "articles"}:
        raise PipelineError("opencc-hant requires a word, sentence, or article dataset")
    segments = _zh_hans_segments(dataset)
    if not segments:
        raise PipelineError(f"Dataset {source_dataset_id!r} has no translatable fields")

    if converter is None:
        converter, detected_info = _load_opencc_hant_converter()
        converter_info = detected_info
    else:
        converter_info = dict(
            converter_info
            or {
                "provider": "OpenCC",
                "packageName": "test-or-injected",
                "packageVersion": "test-or-injected",
                "model": "s2t",
            }
        )
    convert_text = getattr(converter, "convert", None)
    if not callable(convert_text):
        if callable(converter):
            convert_text = converter
        else:
            raise PipelineError("OpenCC converter must be callable or expose convert(text)")

    info = dict(converter_info or {})
    if str(info.get("model") or "") != "s2t":
        raise PipelineError("opencc-hant requires the OpenCC s2t conversion profile")
    stage_key = content_version(
        {
            "stage": "opencc-hant",
            "sourceDataset": source_dataset_id,
            "sourceContentVersion": dataset["contentVersion"],
            "locale": "zh-Hant",
            "converter": info,
            "segments": [
                {
                    "segmentKey": segment["segmentKey"],
                    "sourceHash": segment["sourceHash"],
                }
                for segment in segments
            ],
        }
    )
    resolved_checkpoint_dir = (
        checkpoint_dir.resolve()
        if checkpoint_dir is not None
        else output_path.resolve().parent / ".checkpoints"
    )
    checkpoint_path = (
        resolved_checkpoint_dir
        / "opencc-hant"
        / f"{safe_filename(source_dataset_id)}-zh-Hant.json"
    )
    completed: dict[str, dict[str, str]] = {}
    if not force and checkpoint_path.is_file():
        try:
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            checkpoint = {}
        if checkpoint.get("stageKey") == stage_key:
            for segment_key, value in (checkpoint.get("translations") or {}).items():
                if isinstance(value, Mapping):
                    completed[str(segment_key)] = {
                        "sourceHash": str(value.get("sourceHash") or ""),
                        "text": str(value.get("text") or ""),
                    }
            if (
                checkpoint.get("complete") is True
                and output_path.is_file()
                and checkpoint.get("outputSha256") == sha256_file(output_path)
            ):
                return {
                    "skipped": True,
                    "stageKey": stage_key,
                    "output": str(output_path),
                }

    def write_checkpoint(*, complete: bool, output_sha256: str | None = None) -> None:
        payload: dict[str, Any] = {
            "schemaVersion": SCHEMA_VERSION,
            "stageKey": stage_key,
            "sourceDataset": source_dataset_id,
            "sourceContentVersion": dataset["contentVersion"],
            "locale": "zh-Hant",
            "converter": info,
            "converted": len(completed),
            "total": len(segments),
            "complete": complete,
            "translations": completed,
        }
        if complete:
            payload["output"] = str(output_path.resolve())
            payload["outputSha256"] = output_sha256
        write_json_if_changed(checkpoint_path, payload)

    converted_this_run = 0
    pending_batch = 0
    for segment in segments:
        previous = completed.get(segment["segmentKey"])
        if (
            previous
            and previous.get("sourceHash") == segment["sourceHash"]
            and previous.get("text", "").strip()
        ):
            continue
        try:
            converted_text = str(convert_text(segment["sourceText"])).strip()
        except Exception as error:
            if pending_batch:
                write_checkpoint(complete=False)
            raise PipelineError(
                f"OpenCC conversion failed at {segment['itemKey']}:{segment['field']}: "
                f"{error}"
            ) from error
        if not converted_text or "\x00" in converted_text:
            if pending_batch:
                write_checkpoint(complete=False)
            raise PipelineError(
                f"OpenCC returned invalid text for {segment['itemKey']}:{segment['field']}"
            )
        completed[segment["segmentKey"]] = {
            "sourceHash": segment["sourceHash"],
            "text": converted_text,
        }
        converted_this_run += 1
        pending_batch += 1
        if pending_batch >= batch_size:
            write_checkpoint(complete=False)
            pending_batch = 0

    expected_keys = {segment["segmentKey"] for segment in segments}
    completed_keys = {
        segment_key
        for segment_key, value in completed.items()
        if segment_key in expected_keys and str(value.get("text") or "").strip()
    }
    if completed_keys != expected_keys:
        raise PipelineError("OpenCC checkpoint is incomplete; refusing to write a final map")

    items: dict[str, dict[str, Any]] = {}
    for segment in segments:
        converted_text = completed[segment["segmentKey"]]["text"]
        item = items.setdefault(segment["itemKey"], {})
        if segment["field"].startswith("sentences."):
            sentence_index = segment["field"].split(".", 1)[1]
            sentences = item.setdefault("sentences", {})
            sentences[sentence_index] = converted_text
        else:
            item[segment["field"]] = converted_text

    output = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": REVIEWED_MAP_KIND,
        "locale": "zh-Hant",
        "sourceDataset": source_dataset_id,
        "sourceContentVersion": dataset["contentVersion"],
        "generator": info,
        "items": items,
    }
    changed = write_json_if_changed(output_path, output)
    output_sha256 = sha256_file(output_path)
    write_checkpoint(complete=True, output_sha256=output_sha256)
    return {
        "output": str(output_path),
        "changed": changed,
        "stageKey": stage_key,
        "translatedFields": len(segments),
        "convertedThisRun": converted_this_run,
        "items": len(items),
        "converter": info,
    }


def _load_installed_argos_translator(locale: str) -> tuple[Any, Mapping[str, Any]]:
    """Return an installed direct English-to-locale Argos translator and metadata."""

    try:
        import argostranslate.package as argos_package
        import argostranslate.translate as argos_translate
    except ImportError as error:
        raise PipelineError(
            "argostranslate is not installed; install and review the target model on the "
            "development host before running argos-translate"
        ) from error

    installed_languages = argos_translate.get_installed_languages()
    source_language = next(
        (language for language in installed_languages if language.code == "en"), None
    )
    target_language = next(
        (language for language in installed_languages if language.code == locale), None
    )
    if source_language is None or target_language is None:
        raise PipelineError(f"No installed Argos English-to-{locale} language pair")
    try:
        translator = source_language.get_translation(target_language)
    except Exception as error:
        raise PipelineError(f"No installed direct Argos English-to-{locale} model") from error

    package_details: dict[str, Any] = {}
    get_packages = getattr(argos_package, "get_installed_packages", None)
    if callable(get_packages):
        for package in get_packages():
            if getattr(package, "from_code", None) != "en":
                continue
            if getattr(package, "to_code", None) != locale:
                continue
            package_details = {
                key: value
                for key, value in {
                    "packageName": getattr(package, "package_name", None),
                    "packageVersion": getattr(package, "package_version", None),
                }.items()
                if value not in {None, ""}
            }
            break
    try:
        application_version = importlib.metadata.version("argostranslate")
    except importlib.metadata.PackageNotFoundError:
        application_version = "unknown"
    package_version = str(package_details.get("packageVersion") or "unknown")
    return translator, {
        "provider": "argos-translate",
        "applicationVersion": application_version,
        "packageVersion": package_version,
        "model": f"argos-en-{locale}-{package_version}",
        **package_details,
    }


def generate_argos_article_translations(
    manifest: Mapping[str, Any],
    *,
    source_dataset_id: str,
    locale: str,
    output_path: Path,
    checkpoint_dir: Path | None = None,
    batch_size: int = 16,
    translator: Any | None = None,
    translator_info: Mapping[str, Any] | None = None,
    force: bool = False,
) -> Mapping[str, Any]:
    """Generate a reviewed-map input from an installed offline Argos model.

    Only the final complete map is written to ``output_path``.  Atomic batch
    checkpoints live outside that path and make a failed/interrupted run
    resumable without presenting partial translations as publishable content.
    """

    if locale == "zh-Hant" or locale not in SUPPORTED_LOCALES:
        raise PipelineError("argos-translate requires one of the eight foreign locales")
    if not 1 <= batch_size <= 100:
        raise PipelineError("Argos checkpoint batch size must be between 1 and 100")
    dataset = get_dataset(manifest, source_dataset_id)
    if dataset.get("type") != "articles":
        raise PipelineError("argos-translate currently accepts an articles dataset")

    if translator is None:
        translator, detected_info = _load_installed_argos_translator(locale)
        translator_info = detected_info
    else:
        translator_info = dict(
            translator_info
            or {
                "provider": "argos-translate",
                "applicationVersion": "test-or-injected",
                "packageVersion": "test-or-injected",
                "model": f"argos-en-{locale}-injected",
            }
        )
    if not callable(translator) and not callable(getattr(translator, "translate", None)):
        raise PipelineError("Argos translator must be callable or expose translate(text)")
    translate_text = translator if callable(translator) else translator.translate

    segments: list[dict[str, str]] = []
    missing_english_sources: list[str] = []
    for item in dataset.get("items") or []:
        item_key = str(item["itemKey"])
        for output_field, field_value in (item.get("fields") or {}).items():
            source = (field_value.get("sources") or {}).get("en")
            if not source or not str(source.get("text") or "").strip():
                missing_english_sources.append(f"{item_key}:{output_field}")
                continue
            segments.append(
                {
                    "segmentKey": f"{item_key}\u0000{output_field}",
                    "itemKey": item_key,
                    "field": str(output_field),
                    "sourceText": str(source["text"]),
                    "sourceHash": str(source["sourceHash"]),
                    "sourceField": str(source["sourceField"]),
                }
            )
    if missing_english_sources:
        preview = ", ".join(missing_english_sources[:5])
        raise PipelineError(
            f"Article manifest lacks English source text for {len(missing_english_sources)} "
            f"fields ({preview})"
        )

    info = dict(translator_info or {})
    stage_key = content_version(
        {
            "stage": "argos-translate-articles",
            "sourceDataset": source_dataset_id,
            "sourceContentVersion": dataset["contentVersion"],
            "locale": locale,
            "translator": info,
            "segments": [
                {
                    "segmentKey": value["segmentKey"],
                    "sourceHash": value["sourceHash"],
                }
                for value in segments
            ],
        }
    )
    resolved_checkpoint_dir = (
        checkpoint_dir.resolve()
        if checkpoint_dir is not None
        else output_path.resolve().parent / ".checkpoints"
    )
    checkpoint_path = (
        resolved_checkpoint_dir
        / "argos-translate"
        / f"{safe_filename(source_dataset_id)}-{safe_filename(locale)}.json"
    )
    completed: dict[str, dict[str, str]] = {}
    if not force and checkpoint_path.is_file():
        try:
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            checkpoint = {}
        if checkpoint.get("stageKey") == stage_key:
            for segment_key, value in (checkpoint.get("translations") or {}).items():
                if isinstance(value, Mapping):
                    completed[str(segment_key)] = {
                        "sourceHash": str(value.get("sourceHash") or ""),
                        "text": str(value.get("text") or ""),
                    }
            if (
                checkpoint.get("complete") is True
                and output_path.is_file()
                and checkpoint.get("outputSha256") == sha256_file(output_path)
            ):
                return {
                    "skipped": True,
                    "stageKey": stage_key,
                    "output": str(output_path),
                }

    translated_this_run = 0
    pending_batch = 0
    for segment in segments:
        previous = completed.get(segment["segmentKey"])
        if (
            previous
            and previous.get("sourceHash") == segment["sourceHash"]
            and previous.get("text", "").strip()
        ):
            continue
        try:
            translated_text = str(translate_text(segment["sourceText"])).strip()
        except Exception as error:
            raise PipelineError(
                f"Argos translation failed at {segment['itemKey']}:{segment['field']}: {error}"
            ) from error
        if not translated_text:
            raise PipelineError(
                f"Argos returned an empty translation for "
                f"{segment['itemKey']}:{segment['field']}"
            )
        completed[segment["segmentKey"]] = {
            "sourceHash": segment["sourceHash"],
            "text": translated_text,
        }
        translated_this_run += 1
        pending_batch += 1
        if pending_batch >= batch_size:
            write_json_if_changed(
                checkpoint_path,
                {
                    "schemaVersion": SCHEMA_VERSION,
                    "stageKey": stage_key,
                    "sourceDataset": source_dataset_id,
                    "sourceContentVersion": dataset["contentVersion"],
                    "locale": locale,
                    "translator": info,
                    "translated": len(completed),
                    "total": len(segments),
                    "complete": False,
                    "translations": completed,
                },
            )
            pending_batch = 0

    items: dict[str, dict[str, Any]] = {}
    for segment in segments:
        translated_text = completed[segment["segmentKey"]]["text"]
        item = items.setdefault(
            segment["itemKey"], {"title": "", "summary": "", "sentences": {}}
        )
        if segment["field"].startswith("sentences."):
            index = segment["field"].split(".", 1)[1]
            item["sentences"][index] = translated_text
        else:
            item[segment["field"]] = translated_text

    output = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": "enplay.reviewed-translation-map",
        "locale": locale,
        "sourceDataset": source_dataset_id,
        "sourceContentVersion": dataset["contentVersion"],
        "generator": info,
        "items": items,
    }
    changed = write_json_if_changed(output_path, output)
    write_json_if_changed(
        checkpoint_path,
        {
            "schemaVersion": SCHEMA_VERSION,
            "stageKey": stage_key,
            "sourceDataset": source_dataset_id,
            "sourceContentVersion": dataset["contentVersion"],
            "locale": locale,
            "translator": info,
            "translated": len(completed),
            "total": len(segments),
            "complete": True,
            "output": str(output_path.resolve()),
            "outputSha256": sha256_file(output_path),
            "translations": completed,
        },
    )
    return {
        "output": str(output_path),
        "changed": changed,
        "stageKey": stage_key,
        "translatedFields": len(segments),
        "translatedThisRun": translated_this_run,
        "articles": len(items),
        "translator": info,
    }


def _reviewed_source_segments(
    dataset: Mapping[str, Any],
    *,
    source_lang: str,
) -> dict[tuple[str, str], Mapping[str, Any]]:
    """Return validated source identities for every field in one dataset."""

    segments: dict[tuple[str, str], Mapping[str, Any]] = {}
    missing: list[str] = []
    for item in dataset.get("items") or []:
        item_key = str(item.get("itemKey") or "")
        fields = item.get("fields")
        if not item_key or not isinstance(fields, Mapping) or not fields:
            missing.append(f"{item_key or '<empty>'}:*")
            continue
        for raw_field, field_value in fields.items():
            field_name = str(raw_field)
            identity = (item_key, field_name)
            if identity in segments:
                raise PipelineError(
                    f"Duplicate reviewed-map source segment {item_key}:{field_name}"
                )
            sources = field_value.get("sources") if isinstance(field_value, Mapping) else None
            source = sources.get(source_lang) if isinstance(sources, Mapping) else None
            if not isinstance(source, Mapping):
                missing.append(f"{item_key}:{field_name}")
                continue
            source_text = str(source.get("text") or "")
            source_hash = str(source.get("sourceHash") or "")
            if (
                source.get("lang") != source_lang
                or not source_text.strip()
                or source_hash != sha256_text(source_text)
            ):
                missing.append(f"{item_key}:{field_name}")
                continue
            segments[identity] = source
    if missing:
        preview = ", ".join(missing[:5])
        raise PipelineError(
            f"Dataset {dataset.get('dataset')!r} lacks valid {source_lang} sources for "
            f"{len(missing)} fields ({preview})"
        )
    return segments


def derive_subset_reviewed_map(
    manifest: Mapping[str, Any],
    *,
    source_dataset_id: str,
    target_dataset_id: str,
    source_reviewed_map_path: Path,
    output_path: Path,
) -> Mapping[str, Any]:
    """Derive a complete article reviewed-map from a strict source subset."""

    aggregate_dataset_id = ARTICLE_SOURCE_DATASETS["builtin-articles"]
    tier_dataset_ids = set(ARTICLE_SOURCE_DATASETS.values()) - {aggregate_dataset_id}
    if source_dataset_id != aggregate_dataset_id:
        raise PipelineError(
            f"subset-reviewed-map source must be {aggregate_dataset_id!r}"
        )
    if target_dataset_id not in tier_dataset_ids:
        raise PipelineError("subset-reviewed-map target must be one of the four article shelves")
    source_dataset = get_dataset(manifest, source_dataset_id)
    target_dataset = get_dataset(manifest, target_dataset_id)
    if source_dataset.get("type") != "articles" or target_dataset.get("type") != "articles":
        raise PipelineError("subset-reviewed-map requires article source and target datasets")
    if source_dataset_id == target_dataset_id:
        raise PipelineError("subset-reviewed-map target must be a strict subset dataset")

    reviewed_map = _read_json_object(source_reviewed_map_path, "source reviewed-map")
    if (
        reviewed_map.get("schemaVersion") != SCHEMA_VERSION
        or reviewed_map.get("kind") != REVIEWED_MAP_KIND
    ):
        raise PipelineError("Source reviewed-map has an unsupported schema or kind")
    if reviewed_map.get("sourceDataset") != source_dataset_id:
        raise PipelineError("Source reviewed-map dataset does not match --source-dataset")
    if reviewed_map.get("sourceContentVersion") != source_dataset.get("contentVersion"):
        raise PipelineError("Source reviewed-map content version is stale")
    locale = str(reviewed_map.get("locale") or "")
    if locale not in SUPPORTED_LOCALES:
        raise PipelineError("Source reviewed-map locale is unsupported")
    source_lang = "zh-Hans" if locale == "zh-Hant" else "en"

    source_segments = _reviewed_source_segments(
        source_dataset,
        source_lang=source_lang,
    )
    target_segments = _reviewed_source_segments(
        target_dataset,
        source_lang=source_lang,
    )
    source_item_keys = {item_key for item_key, _ in source_segments}
    target_item_keys = {item_key for item_key, _ in target_segments}
    if not target_item_keys or not target_item_keys < source_item_keys:
        raise PipelineError(
            "Target article item keys must be a non-empty strict subset of the source dataset"
        )
    if not set(target_segments) < set(source_segments):
        raise PipelineError(
            "Target article fields must be a strict subset of the source dataset"
        )
    for identity, target_source in target_segments.items():
        source = source_segments.get(identity)
        if source is None or source.get("sourceHash") != target_source.get("sourceHash"):
            raise PipelineError(
                "Target sourceHash differs from aggregate source for "
                f"{identity[0]}:{identity[1]}"
            )

    translated = _flatten_translation_map(reviewed_map)
    source_identities = set(source_segments)
    translated_identities = set(translated)
    if translated_identities != source_identities:
        missing = sorted(source_identities - translated_identities)
        extra = sorted(translated_identities - source_identities)
        raise PipelineError(
            "Source reviewed-map must exactly cover the aggregate source fields "
            f"(missing={len(missing)}, extra={len(extra)})"
        )
    empty = [
        identity for identity, value in translated.items() if not str(value).strip()
    ]
    if empty:
        raise PipelineError(
            f"Source reviewed-map contains {len(empty)} empty translated fields"
        )

    target_items: dict[str, dict[str, Any]] = {}
    for item in target_dataset.get("items") or []:
        item_key = str(item["itemKey"])
        localized: dict[str, Any] = {}
        for field_name in (item.get("fields") or {}):
            field = str(field_name)
            value = str(translated[(item_key, field)]).strip()
            if field.startswith("sentences."):
                localized.setdefault("sentences", {})[field.split(".", 1)[1]] = value
            else:
                localized[field] = value
        target_items[item_key] = localized

    source_map_sha256 = sha256_file(source_reviewed_map_path)
    output = {
        "schemaVersion": SCHEMA_VERSION,
        "kind": REVIEWED_MAP_KIND,
        "locale": locale,
        "sourceDataset": target_dataset_id,
        "sourceContentVersion": target_dataset["contentVersion"],
        "generator": {
            "provider": "subset-reviewed-map",
            "sourceDataset": source_dataset_id,
            "sourceContentVersion": source_dataset["contentVersion"],
            "sourceReviewedMapSha256": source_map_sha256,
            "sourceGenerator": dict(reviewed_map.get("generator") or {}),
        },
        "items": target_items,
    }
    changed = write_json_if_changed(output_path, output)
    return {
        "output": str(output_path),
        "changed": changed,
        "locale": locale,
        "sourceDataset": source_dataset_id,
        "targetDataset": target_dataset_id,
        "sourceItems": len(source_item_keys),
        "items": len(target_items),
        "translatedFields": len(target_segments),
        "sourceReviewedMapSha256": source_map_sha256,
    }


def _read_json_object(path: Path, description: str) -> Mapping[str, Any]:
    if not path.is_file():
        raise PipelineError(f"Missing {description}: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise PipelineError(f"{description} must be a JSON object: {path}")
    return payload


def _load_publish_plan(
    output_dir: Path, locale: str, library_id: str
) -> tuple[Mapping[str, Any], list[Mapping[str, Any]], Mapping[str, Any]]:
    artifact_name = safe_filename(library_id)
    catalog_dir = output_dir / "admin" / "catalog" / safe_filename(locale)
    draft = _read_json_object(
        catalog_dir / f"{artifact_name}.draft.json", "draft catalog artifact"
    )
    ready = _read_json_object(
        catalog_dir / f"{artifact_name}.ready.json", "ready catalog artifact"
    )
    for name, payload in (("draft", draft), ("ready", ready)):
        if payload.get("schemaVersion") != SCHEMA_VERSION:
            raise PipelineError(f"Unsupported {name} catalog schemaVersion")
        if payload.get("locale") != locale:
            raise PipelineError(f"{name} catalog locale does not match {locale!r}")
        libraries = payload.get("libraries") or []
        if len(libraries) != 1 or libraries[0].get("id") != library_id:
            raise PipelineError(f"{name} catalog must contain only library {library_id!r}")
    draft_library = draft["libraries"][0]
    ready_library = ready["libraries"][0]
    if draft_library.get("status") != "draft":
        raise PipelineError("Draft catalog artifact must have status 'draft'")
    if ready_library.get("status") not in {"ready", "reviewed"}:
        raise PipelineError("Ready catalog artifact must have status 'ready' or 'reviewed'")
    version = str(draft.get("contentVersion") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", version):
        raise PipelineError("Catalog contentVersion must be a 64-character lowercase hash")
    if ready.get("contentVersion") != version:
        raise PipelineError("Draft and ready catalog contentVersion values differ")
    if draft_library.get("sourceLibraryId") != ready_library.get("sourceLibraryId"):
        raise PipelineError("Draft and ready sourceLibraryId values differ")
    dataset = str(ready_library.get("dataset") or "")
    if not dataset or draft_library.get("dataset") != dataset:
        raise PipelineError("Draft and ready catalog datasets differ or are missing")
    build_checkpoint_path = (
        output_dir
        / ".checkpoints"
        / safe_filename(dataset)
        / f"{safe_filename(locale)}.json"
    )
    build_checkpoint = _read_json_object(
        build_checkpoint_path,
        "complete build checkpoint",
    )
    if build_checkpoint.get("complete") is not True:
        raise PipelineError("Build checkpoint is incomplete; refusing stale publish artifacts")
    if (
        build_checkpoint.get("dataset") != dataset
        or build_checkpoint.get("locale") != locale
    ):
        raise PipelineError("Build checkpoint target does not match publish artifacts")
    if build_checkpoint.get("contentVersion") != version:
        raise PipelineError("Build checkpoint contentVersion does not match catalog artifacts")
    checkpoint_library_ids = [
        str(value) for value in (build_checkpoint.get("libraryIds") or [])
    ]
    if library_id not in checkpoint_library_ids:
        raise PipelineError("Build checkpoint does not include the requested library")
    bundle_path = (
        output_dir
        / "bundles"
        / safe_filename(dataset)
        / f"{safe_filename(locale)}.json"
    )
    expected_bundle_relative = str(bundle_path.relative_to(output_dir)).replace("\\", "/")
    if build_checkpoint.get("bundle") != expected_bundle_relative:
        raise PipelineError("Build checkpoint bundle path does not match the catalog dataset")
    expected_bundle_sha256 = str(build_checkpoint.get("bundleSha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_bundle_sha256):
        raise PipelineError("Build checkpoint is missing a valid bundle fingerprint")
    bundle = _read_json_object(bundle_path, "localized content bundle")
    if sha256_file(bundle_path) != expected_bundle_sha256:
        raise PipelineError("Localized content bundle fingerprint does not match checkpoint")
    if (
        bundle.get("schemaVersion") != SCHEMA_VERSION
        or bundle.get("kind") != BUNDLE_KIND
        or bundle.get("dataset") != dataset
        or bundle.get("locale") != locale
        or bundle.get("contentVersion") != version
    ):
        raise PipelineError("Localized content bundle metadata does not match publish artifacts")

    item_dir = (
        output_dir
        / "admin"
        / "library-items"
        / safe_filename(locale)
        / artifact_name
    )
    item_paths = sorted(item_dir.glob("*.json")) if item_dir.is_dir() else []
    batches: list[Mapping[str, Any]] = []
    seen_keys: set[str] = set()
    seen_positions: set[int] = set()
    admin_items_by_key: dict[str, tuple[int, Mapping[str, Any]]] = {}
    source_library_id = str(ready_library.get("sourceLibraryId") or "")
    for path in item_paths:
        batch = _read_json_object(path, "library-item batch")
        if batch.get("schemaVersion") != SCHEMA_VERSION:
            raise PipelineError(f"Unsupported library-item schemaVersion in {path}")
        if batch.get("locale") != locale or batch.get("libraryId") != library_id:
            raise PipelineError(f"Library-item target mismatch in {path}")
        if batch.get("contentVersion") != version:
            raise PipelineError(f"Library-item contentVersion mismatch in {path}")
        items = batch.get("items") or []
        if not isinstance(items, list) or not 1 <= len(items) <= 100:
            raise PipelineError(f"Library-item batch must contain 1..100 items: {path}")
        for item in items:
            if not isinstance(item, Mapping):
                raise PipelineError(f"Malformed item in {path}")
            item_key = str(item.get("itemKey") or "")
            if not item_key or item_key in seen_keys:
                raise PipelineError(f"Missing or duplicate itemKey {item_key!r} in {path}")
            seen_keys.add(item_key)
            try:
                position = int(item.get("position"))
            except (TypeError, ValueError) as error:
                raise PipelineError(f"Invalid position for {item_key!r} in {path}") from error
            if position < 0 or position in seen_positions:
                raise PipelineError(f"Invalid or duplicate position {position} in {path}")
            seen_positions.add(position)
            if not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sourceHash") or "")):
                raise PipelineError(f"Invalid sourceHash for {item_key!r} in {path}")
            if item.get("status") != "ready":
                raise PipelineError(f"Item {item_key!r} must have status 'ready'")
            item_payload = item.get("payload") or {}
            if str(item_payload.get("contentKey") or "") != item_key:
                raise PipelineError(f"Payload contentKey mismatch for {item_key!r}")
            if str(item_payload.get("sourceLibraryId") or "") != source_library_id:
                raise PipelineError(f"Payload sourceLibraryId mismatch for {item_key!r}")
            admin_items_by_key[item_key] = (position, item_payload)
        batches.append(batch)
    try:
        expected_count = int(ready_library.get("itemCount") or 0)
    except (TypeError, ValueError) as error:
        raise PipelineError("Ready catalog itemCount must be an integer") from error
    if expected_count <= 0:
        raise PipelineError("Ready catalog must contain at least one item")
    if len(seen_keys) != expected_count:
        raise PipelineError(
            f"Catalog itemCount is {expected_count}, but item batches contain {len(seen_keys)}"
        )
    if expected_count and seen_positions != set(range(expected_count)):
        raise PipelineError("Library-item positions must be contiguous from zero")
    raw_bundle_content = bundle.get("content")
    if not isinstance(raw_bundle_content, list):
        raise PipelineError("Localized content bundle content must be an array")
    bundle_items_by_key: dict[str, tuple[int, Mapping[str, Any]]] = {}
    for index, entry in enumerate(raw_bundle_content):
        if not isinstance(entry, Mapping):
            raise PipelineError(f"Malformed bundle content entry at index {index}")
        if str(entry.get("libraryId") or "") != library_id:
            continue
        item_key = str(entry.get("itemKey") or "")
        payload = entry.get("payload")
        if not item_key or item_key in bundle_items_by_key or not isinstance(payload, Mapping):
            raise PipelineError(f"Malformed or duplicate bundle item {item_key!r}")
        try:
            position = int(entry.get("position"))
        except (TypeError, ValueError) as error:
            raise PipelineError(f"Invalid bundle position for {item_key!r}") from error
        bundle_items_by_key[item_key] = (position, payload)
    if set(bundle_items_by_key) != seen_keys:
        raise PipelineError("Bundle items do not match the generated admin item batches")
    for item_key, admin_value in admin_items_by_key.items():
        if bundle_items_by_key[item_key] != admin_value:
            raise PipelineError(
                f"Bundle payload or position differs from admin artifact for {item_key!r}"
            )
    return draft, batches, ready


def _post_admin_json(
    url: str, payload: Mapping[str, Any], token: str, timeout: float
) -> Mapping[str, Any]:
    request = urllib.request.Request(
        url,
        data=canonical_json_bytes(payload),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "X-Admin-Token": token,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(1024 * 1024)
            decoded = raw.decode("utf-8", errors="replace").strip()
            body = json.loads(decoded) if decoded else {}
            return {"status": int(response.status), "body": body}
    except urllib.error.HTTPError as error:
        detail = error.read(4096).decode("utf-8", errors="replace").strip()
        if token:
            detail = detail.replace(token, "[redacted]")
        if error.code == 429:
            return {
                "status": 429,
                "body": detail[:500],
                "retryAfter": error.headers.get("Retry-After") if error.headers else None,
            }
        raise PipelineError(
            f"Admin import failed with HTTP {error.code} at {url}: {detail[:500]}"
        ) from error
    except urllib.error.URLError as error:
        raise PipelineError(f"Admin import connection failed at {url}: {error.reason}") from error


def _retry_after_seconds(value: Any, *, now: float | None = None) -> float | None:
    """Parse an RFC Retry-After delta or HTTP date without trusting its size."""

    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        seconds = float(text)
    except ValueError:
        try:
            retry_at = email.utils.parsedate_to_datetime(text)
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=datetime.timezone.utc)
        current = datetime.datetime.fromtimestamp(
            time.time() if now is None else now,
            tz=datetime.timezone.utc,
        )
        seconds = (retry_at - current).total_seconds()
    if not math.isfinite(seconds):
        return None
    if seconds < 0:
        return 0.0
    return seconds


def publish_library_artifacts(
    *,
    output_dir: Path,
    locale: str,
    library_id: str,
    api_base: str,
    token: str = "",
    dry_run: bool = False,
    allow_http: bool = False,
    restart: bool = False,
    timeout: float = 30.0,
    rate_limit_retries: int = 5,
    rate_limit_wait_limit: float = 600.0,
    post_json: Any | None = None,
    sleep_fn: Any | None = None,
) -> Mapping[str, Any]:
    """Publish one generated library in draft/items/ready order, with resume."""

    split = urllib.parse.urlsplit(api_base.strip())
    if split.scheme not in {"http", "https"} or not split.netloc:
        raise PipelineError("--api-base must be an absolute HTTP(S) URL")
    if split.query or split.fragment:
        raise PipelineError("--api-base must not contain a query string or fragment")
    is_loopback = (split.hostname or "").casefold() in {"localhost", "127.0.0.1", "::1"}
    if split.scheme != "https" and not (allow_http or is_loopback):
        raise PipelineError("Refusing to send an admin token over HTTP; use HTTPS or --allow-http")
    if timeout <= 0:
        raise PipelineError("--timeout must be greater than zero")
    if not 0 <= rate_limit_retries <= 100:
        raise PipelineError("--rate-limit-retries must be between 0 and 100")
    if not 0 <= rate_limit_wait_limit <= 86_400:
        raise PipelineError("--rate-limit-wait-limit must be between 0 and 86400 seconds")

    draft, batches, ready = _load_publish_plan(output_dir, locale, library_id)
    base = api_base.rstrip("/")
    catalog_url = f"{base}/v1/admin/i18n/catalog"
    items_url = f"{base}/v1/admin/i18n/library-items"
    steps: list[tuple[str, str, Mapping[str, Any]]] = [
        ("catalog:draft", catalog_url, draft),
        *[
            (f"items:{index:04d}", items_url, batch)
            for index, batch in enumerate(batches, 1)
        ],
        ("catalog:ready", catalog_url, ready),
    ]
    plan_hash = content_version(
        {
            "apiBase": base,
            "locale": locale,
            "libraryId": library_id,
            "steps": [
                {"name": name, "url": url, "payloadHash": content_version(payload)}
                for name, url, payload in steps
            ],
        }
    )
    if dry_run:
        return {
            "dryRun": True,
            "apiBase": base,
            "locale": locale,
            "libraryId": library_id,
            "contentVersion": draft["contentVersion"],
            "steps": [name for name, _, _ in steps],
            "itemBatches": len(batches),
            "items": sum(len(batch.get("items") or []) for batch in batches),
            "planHash": plan_hash,
        }
    if not token:
        raise PipelineError("Admin token is required unless --dry-run is used")

    checkpoint_path = (
        output_dir
        / ".publish-checkpoints"
        / safe_filename(locale)
        / f"{safe_filename(library_id)}.json"
    )
    completed_steps: list[str] = []
    if not restart and checkpoint_path.is_file():
        try:
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            checkpoint = {}
        if checkpoint.get("planHash") == plan_hash:
            recorded = [str(value) for value in checkpoint.get("completedSteps") or []]
            expected_names = [name for name, _, _ in steps]
            for expected, value in zip(expected_names, recorded):
                if value != expected:
                    break
                completed_steps.append(value)
    completed_set = set(completed_steps)
    sender = post_json or _post_admin_json
    sleeper = sleep_fn or time.sleep
    posted = 0
    rate_limit_retry_count = 0
    rate_limit_waited = 0.0
    statuses: list[dict[str, Any]] = []
    for name, url, payload in steps:
        if name in completed_set:
            continue
        step_rate_limit_retries = 0
        while True:
            result = sender(url, payload, token, timeout)
            status = int((result or {}).get("status", 0))
            if status != 429:
                break
            step_rate_limit_retries += 1
            rate_limit_retry_count += 1
            if step_rate_limit_retries > rate_limit_retries:
                raise PipelineError(
                    f"Admin import remained rate-limited at {url} after "
                    f"{rate_limit_retries} retries"
                )
            retry_after = _retry_after_seconds((result or {}).get("retryAfter"))
            if retry_after is None:
                retry_after = float(min(60, 2 ** (step_rate_limit_retries - 1)))
            retry_after = max(1.0, retry_after)
            if rate_limit_waited + retry_after > rate_limit_wait_limit:
                raise PipelineError(
                    "Admin import rate-limit wait would exceed the configured "
                    f"{rate_limit_wait_limit:g}-second total limit"
                )
            sleeper(retry_after)
            rate_limit_waited += retry_after
        if not 200 <= status < 300:
            raise PipelineError(f"Admin import returned unexpected status {status} at {url}")
        completed_steps.append(name)
        completed_set.add(name)
        posted += 1
        statuses.append({"step": name, "status": status})
        write_json_if_changed(
            checkpoint_path,
            {
                "schemaVersion": SCHEMA_VERSION,
                "planHash": plan_hash,
                "apiBase": base,
                "locale": locale,
                "libraryId": library_id,
                "contentVersion": draft["contentVersion"],
                "completedSteps": completed_steps,
                "complete": len(completed_set) == len(steps),
            },
        )
    return {
        "apiBase": base,
        "locale": locale,
        "libraryId": library_id,
        "contentVersion": draft["contentVersion"],
        "posted": posted,
        "resumed": len(steps) - posted,
        "rateLimitRetries": rate_limit_retry_count,
        "rateLimitWaitSeconds": rate_limit_waited,
        "complete": len(completed_set) == len(steps),
        "statuses": statuses,
        "checkpoint": str(checkpoint_path),
    }


def read_manifest(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schemaVersion") != SCHEMA_VERSION or payload.get("kind") != MANIFEST_KIND:
        raise PipelineError(f"Unsupported source manifest: {path}")
    return payload


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-dataset", required=True)
    parser.add_argument("--output-dataset", required=True)
    parser.add_argument("--locale", choices=SUPPORTED_LOCALES, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--library-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", default="")
    parser.add_argument("--force", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    export = subparsers.add_parser("export", help="export a stable canonical source manifest")
    export.add_argument("--project-root", type=Path, default=Path.cwd())
    export.add_argument("--output", type=Path, required=True)
    export.add_argument("--wordbook-json", action="append", default=[])
    export.add_argument("--presence-token", default=None)

    wikdict = subparsers.add_parser("wikdict", help="build an independent word library")
    add_common_arguments(wikdict)
    wikdict.add_argument("--sqlite", type=Path, required=True)
    wikdict.add_argument("--source-url", required=True)

    kaikki = subparsers.add_parser("kaikki", help="build a word library from Kaikki JSONL")
    add_common_arguments(kaikki)
    kaikki.add_argument("--jsonl", type=Path, required=True)
    kaikki.add_argument("--source-url", required=True)

    korean = subparsers.add_parser(
        "korean-dict",
        help="build a Korean word library from open-english-korean-dict JSON/SQLite",
    )
    add_common_arguments(korean)
    korean.add_argument("--source", type=Path, required=True)
    korean.add_argument(
        "--source-url",
        default="https://github.com/jhseo1211/open-english-korean-dict",
    )

    yaitron = subparsers.add_parser(
        "yaitron", help="build a Thai word library from Yaitron NDJSON/TEI"
    )
    add_common_arguments(yaitron)
    yaitron.add_argument("--source", type=Path, required=True)
    yaitron.add_argument(
        "--source-url", default="https://github.com/veer66/Yaitron"
    )

    freedict = subparsers.add_parser("freedict", help="build a word library from FreeDict TEI")
    add_common_arguments(freedict)
    freedict.add_argument("--tei", type=Path, required=True)
    freedict.add_argument("--source-url", required=True)
    freedict.add_argument("--license-name", required=True)
    freedict.add_argument("--license-url", required=True)

    tatoeba = subparsers.add_parser("tatoeba", help="build an independent Tatoeba sentence library")
    add_common_arguments(tatoeba)
    tatoeba.add_argument("--links", type=Path, required=True)
    tatoeba.add_argument("--target-sentences", type=Path, required=True)
    tatoeba.add_argument("--english-sentences", type=Path)

    tatoeba_direct = subparsers.add_parser(
        "tatoeba-direct",
        help="build a standalone library directly from official bilingual Tatoeba exports",
    )
    tatoeba_direct.add_argument("--output-dataset", default="sentences-common")
    tatoeba_direct.add_argument("--locale", choices=tuple(TATOEBA_CODES), required=True)
    tatoeba_direct.add_argument("--output-dir", type=Path, required=True)
    tatoeba_direct.add_argument("--library-id", required=True)
    tatoeba_direct.add_argument("--source-library-id")
    tatoeba_direct.add_argument("--name", required=True)
    tatoeba_direct.add_argument("--description", default="")
    tatoeba_direct.add_argument("--english-sentences", type=Path, required=True)
    tatoeba_direct.add_argument("--links", type=Path, required=True)
    tatoeba_direct.add_argument("--target-sentences", type=Path, required=True)
    tatoeba_direct.add_argument(
        "--target-count",
        "--count",
        dest="target_count",
        type=int,
        default=1000,
    )
    tatoeba_direct.add_argument("--min-words", type=int, default=2)
    tatoeba_direct.add_argument("--max-words", type=int, default=16)
    tatoeba_direct.add_argument("--max-english-chars", type=int, default=115)
    tatoeba_direct.add_argument("--max-target-chars", type=int, default=240)
    tatoeba_direct.add_argument("--force", action="store_true")

    reviewed = subparsers.add_parser(
        "reviewed", help="materialise reviewed translations, including articles"
    )
    add_common_arguments(reviewed)
    reviewed.add_argument("--translations", type=Path, required=True)
    reviewed.add_argument("--provider", required=True)
    reviewed.add_argument("--model", default="")
    reviewed.add_argument("--source-url", default="")
    reviewed.add_argument("--license-name", default="Project content")
    reviewed.add_argument("--license-url", default="")

    argos = subparsers.add_parser(
        "argos-translate",
        help="pre-generate an article reviewed-map with an installed offline Argos model",
    )
    argos.add_argument("--manifest", type=Path, required=True)
    argos.add_argument("--source-dataset", default="articles-graded")
    argos.add_argument("--locale", choices=tuple(TATOEBA_CODES), required=True)
    argos.add_argument("--output", type=Path, required=True)
    argos.add_argument("--checkpoint-dir", type=Path)
    argos.add_argument("--batch-size", type=int, default=16)
    argos.add_argument("--force", action="store_true")

    opencc_hant = subparsers.add_parser(
        "opencc-hant",
        help="convert one dataset's complete zh-Hans fields to a zh-Hant reviewed-map",
    )
    opencc_hant.add_argument("--manifest", type=Path, required=True)
    opencc_hant.add_argument("--source-dataset", required=True)
    opencc_hant.add_argument("--output", type=Path, required=True)
    opencc_hant.add_argument("--checkpoint-dir", type=Path)
    opencc_hant.add_argument("--batch-size", type=int, default=100)
    opencc_hant.add_argument("--force", action="store_true")

    subset_reviewed = subparsers.add_parser(
        "subset-reviewed-map",
        help="derive a complete article shelf map from an aggregate reviewed-map",
    )
    subset_reviewed.add_argument("--manifest", type=Path, required=True)
    subset_reviewed.add_argument("--source-dataset", default="articles-graded")
    subset_reviewed.add_argument("--target-dataset", required=True)
    subset_reviewed.add_argument("--source-reviewed-map", type=Path, required=True)
    subset_reviewed.add_argument("--output", type=Path, required=True)

    publish = subparsers.add_parser(
        "publish", help="publish one generated library with safe ordered resume"
    )
    publish.add_argument("--output-dir", type=Path, required=True)
    publish.add_argument("--locale", choices=SUPPORTED_LOCALES, required=True)
    publish.add_argument("--library-id", required=True)
    publish.add_argument("--api-base", required=True)
    publish.add_argument(
        "--token",
        default=None,
        help="admin token (prefer --token-env so it is absent from shell history)",
    )
    publish.add_argument("--token-env", default="ENPLAY_ADMIN_TOKEN")
    publish.add_argument("--dry-run", action="store_true")
    publish.add_argument("--allow-http", action="store_true")
    publish.add_argument("--restart", action="store_true")
    publish.add_argument("--timeout", type=float, default=30.0)
    publish.add_argument("--rate-limit-retries", type=int, default=5)
    publish.add_argument("--rate-limit-wait-limit", type=float, default=600.0)
    return parser


def run(arguments: argparse.Namespace) -> Mapping[str, Any]:
    if arguments.command == "export":
        manifest = build_source_manifest(
            arguments.project_root,
            arguments.wordbook_json,
            presence_token=arguments.presence_token,
        )
        changed = write_json_if_changed(arguments.output, manifest)
        return {
            "output": str(arguments.output),
            "changed": changed,
            "manifestVersion": manifest["manifestVersion"],
            "datasets": len(manifest["datasets"]),
        }

    if arguments.command == "argos-translate":
        return generate_argos_article_translations(
            read_manifest(arguments.manifest),
            source_dataset_id=arguments.source_dataset,
            locale=arguments.locale,
            output_path=arguments.output,
            checkpoint_dir=arguments.checkpoint_dir,
            batch_size=arguments.batch_size,
            force=arguments.force,
        )

    if arguments.command == "opencc-hant":
        return generate_opencc_hant_translations(
            read_manifest(arguments.manifest),
            source_dataset_id=arguments.source_dataset,
            output_path=arguments.output,
            checkpoint_dir=arguments.checkpoint_dir,
            batch_size=arguments.batch_size,
            force=arguments.force,
        )

    if arguments.command == "subset-reviewed-map":
        return derive_subset_reviewed_map(
            read_manifest(arguments.manifest),
            source_dataset_id=arguments.source_dataset,
            target_dataset_id=arguments.target_dataset,
            source_reviewed_map_path=arguments.source_reviewed_map,
            output_path=arguments.output,
        )

    if arguments.command == "publish":
        token = arguments.token or os.environ.get(arguments.token_env, "")
        return publish_library_artifacts(
            output_dir=arguments.output_dir,
            locale=arguments.locale,
            library_id=arguments.library_id,
            api_base=arguments.api_base,
            token=token,
            dry_run=arguments.dry_run,
            allow_http=arguments.allow_http,
            restart=arguments.restart,
            timeout=arguments.timeout,
            rate_limit_retries=arguments.rate_limit_retries,
            rate_limit_wait_limit=arguments.rate_limit_wait_limit,
        )

    if arguments.command == "tatoeba-direct":
        return build_tatoeba_direct_library(
            output_dataset_id=arguments.output_dataset,
            locale=arguments.locale,
            english_sentences_path=arguments.english_sentences,
            links_path=arguments.links,
            target_sentences_path=arguments.target_sentences,
            output_dir=arguments.output_dir,
            library_id=arguments.library_id,
            source_library_id=arguments.source_library_id,
            name=arguments.name,
            description=arguments.description,
            target_count=arguments.target_count,
            min_words=arguments.min_words,
            max_words=arguments.max_words,
            max_english_chars=arguments.max_english_chars,
            max_target_chars=arguments.max_target_chars,
            force=arguments.force,
        )

    manifest = read_manifest(arguments.manifest)
    common = {
        "manifest": manifest,
        "source_dataset_id": arguments.source_dataset,
        "output_dataset_id": arguments.output_dataset,
        "locale": arguments.locale,
        "output_dir": arguments.output_dir,
        "library_id": arguments.library_id,
        "name": arguments.name,
        "description": arguments.description,
        "force": arguments.force,
    }
    if arguments.command == "wikdict":
        with WikDictSQLiteAdapter(arguments.sqlite) as adapter:
            return build_lexical_library(
                adapter=adapter,
                source_url=arguments.source_url,
                license_info=WIKDICT_LICENSE,
                **common,
            )
    if arguments.command == "kaikki":
        source_dataset = get_dataset(manifest, arguments.source_dataset)
        wanted = [(item.get("payload") or {}).get("word", item["itemKey"]) for item in source_dataset["items"]]
        adapter = KaikkiJsonlAdapter(arguments.jsonl, wanted)
        return build_lexical_library(
            adapter=adapter,
            source_url=arguments.source_url,
            license_info=KAIKKI_WIKTIONARY_LICENSE,
            **common,
        )
    if arguments.command == "korean-dict":
        if arguments.locale != "ko":
            raise PipelineError("korean-dict requires --locale ko")
        source_dataset = get_dataset(manifest, arguments.source_dataset)
        wanted = [
            (item.get("payload") or {}).get("word", item["itemKey"])
            for item in source_dataset["items"]
        ]
        with OpenEnglishKoreanAdapter(arguments.source, wanted) as adapter:
            return build_lexical_library(
                adapter=adapter,
                source_url=arguments.source_url,
                license_info=OPEN_ENGLISH_KOREAN_LICENSE,
                **common,
            )
    if arguments.command == "yaitron":
        if arguments.locale != "th":
            raise PipelineError("yaitron requires --locale th")
        source_dataset = get_dataset(manifest, arguments.source_dataset)
        wanted = [
            (item.get("payload") or {}).get("word", item["itemKey"])
            for item in source_dataset["items"]
        ]
        adapter = YaitronAdapter(arguments.source, wanted)
        return build_lexical_library(
            adapter=adapter,
            source_url=arguments.source_url,
            license_info=YAITRON_LICENSE,
            **common,
        )
    if arguments.command == "freedict":
        source_dataset = get_dataset(manifest, arguments.source_dataset)
        wanted = [(item.get("payload") or {}).get("word", item["itemKey"]) for item in source_dataset["items"]]
        adapter = FreeDictTeiAdapter(arguments.tei, wanted)
        return build_lexical_library(
            adapter=adapter,
            source_url=arguments.source_url,
            license_info={"name": arguments.license_name, "url": arguments.license_url},
            **common,
        )
    if arguments.command == "tatoeba":
        return build_tatoeba_library(
            links_path=arguments.links,
            target_sentences_path=arguments.target_sentences,
            english_sentences_path=arguments.english_sentences,
            **common,
        )
    if arguments.command == "reviewed":
        return build_reviewed_translation_libraries(
            translations_path=arguments.translations,
            provider=arguments.provider,
            model=arguments.model,
            source_url=arguments.source_url,
            license_info={"name": arguments.license_name, "url": arguments.license_url},
            **common,
        )
    raise PipelineError(f"Unknown command: {arguments.command}")


def main(argv: Sequence[str] | None = None) -> int:
    try:
        result = run(build_parser().parse_args(argv))
    except (
        PipelineError,
        OSError,
        sqlite3.Error,
        json.JSONDecodeError,
        ET.ParseError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import html
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy import inspect, select, text

from .database import SessionLocal, engine
from .import_ecdict import compact_text, open_source, score_sentence
from .models import Wordbook, WordbookEntry


CET6_SLUG = "ecdict-cet6"
OPEN_DICTIONARY_BASE = "https://mhollingshead.github.io/open-dictionary/api"
WIKTIONARY_SOURCE_URL = "https://en.wiktionary.org/"
WIKTIONARY_LICENSE_URL = "https://en.wiktionary.org/wiki/Wiktionary:Copyrights"


def ensure_definition_column() -> None:
    columns = {column["name"] for column in inspect(engine).get_columns("wordbook_entries")}
    if "definition_en" in columns:
        return
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE wordbook_entries "
                "ADD COLUMN definition_en TEXT NULL AFTER definition"
            )
        )


def read_builtin_definitions() -> dict[str, str]:
    source_location = os.getenv("BUILTIN_EXAMPLES_SOURCE")
    if not source_location:
        return {}
    with open_source(source_location) as response:
        source_text = response.read().decode("utf-8-sig")
    match = re.search(r"const\s+cet4Words\s*=\s*(\[.*\])\s*;?\s*$", source_text, re.S)
    if not match:
        raise ValueError("Unable to locate cet4Words in the built-in word source")
    return {
        str(item["word"]).casefold(): compact_text(item.get("definition"))
        for item in json.loads(match.group(1))
        if item.get("word") and item.get("definition")
    }


def dictionary_prefix(word: str) -> tuple[str, str] | None:
    letters = "".join(character for character in word.casefold() if character.isalpha())
    if not letters or not letters[0].isascii():
        return None
    return letters[0], letters[:2] if len(letters) > 1 else letters[0]


def clean_sense(value: object) -> str:
    if not value:
        return ""
    cleaned = re.sub(r"<[^>]+>", "", html.unescape(str(value)))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def choose_definition(entry: object) -> str:
    if not isinstance(entry, dict):
        return ""
    selected: list[str] = []
    for etymology in entry.get("etymologies", []):
        for part in etymology.get("partsOfSpeech", []):
            part_name = clean_sense(part.get("partOfSpeech"))
            candidates = [
                clean_sense(sense.get("sense"))
                for sense in part.get("senses", [])
                if isinstance(sense, dict)
            ]
            candidates = [candidate for candidate in candidates if candidate]
            preferred = next(
                (
                    candidate
                    for candidate in candidates
                    if not re.match(
                        r"^\([^)]*(obsolete|archaic|rare|dated|historical)[^)]*\)",
                        candidate,
                        re.I,
                    )
                ),
                candidates[0] if candidates else "",
            )
            if preferred:
                selected.append(f"{part_name}: {preferred}" if part_name else preferred)
            if len(selected) == 3:
                return compact_text("；".join(selected))
    return compact_text("；".join(selected))


def choose_example(entry: object) -> str:
    if not isinstance(entry, dict):
        return ""
    selected = ""
    selected_score = 10_000
    for etymology in entry.get("etymologies", []):
        for part in etymology.get("partsOfSpeech", []):
            for sense in part.get("senses", []):
                if not isinstance(sense, dict):
                    continue
                for value in sense.get("examples", []):
                    example = clean_sense(value)
                    scored = score_sentence(example)
                    if scored is None:
                        continue
                    score, _ = scored
                    if score < selected_score:
                        selected = example
                        selected_score = score
    return compact_text(selected)


def fetch_prefix(prefix: tuple[str, str]) -> tuple[tuple[str, str], dict[str, object]]:
    directory, filename = prefix
    source_url = f"{OPEN_DICTIONARY_BASE}/{directory}/{filename}.json"
    try:
        request = Request(
            source_url, headers={"User-Agent": "Enplay-Wordbook-Importer/1.1"}
        )
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return prefix, payload if isinstance(payload, dict) else {}
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return prefix, {}


def read_open_dictionary_content(
    target_words: set[str],
) -> tuple[dict[str, str], dict[str, str]]:
    words_by_prefix: dict[tuple[str, str], set[str]] = {}
    for word in target_words:
        prefix = dictionary_prefix(word)
        if prefix:
            words_by_prefix.setdefault(prefix, set()).add(word)

    definitions: dict[str, str] = {}
    examples: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {
            executor.submit(fetch_prefix, prefix): prefix for prefix in words_by_prefix
        }
        for future in as_completed(futures):
            prefix, payload = future.result()
            normalized_payload = {key.casefold(): value for key, value in payload.items()}
            for word in words_by_prefix[prefix]:
                entry = normalized_payload.get(word)
                definition = choose_definition(entry)
                if definition:
                    definitions[word] = definition
                example = choose_example(entry)
                if example:
                    examples[word] = example
    return definitions, examples


def read_open_dictionary_definitions(target_words: set[str]) -> dict[str, str]:
    definitions, _ = read_open_dictionary_content(target_words)
    return definitions


def fill_cet6_english_definitions() -> None:
    ensure_definition_column()
    with SessionLocal() as db:
        wordbook = db.scalar(select(Wordbook).where(Wordbook.slug == CET6_SLUG))
        if wordbook is None:
            raise RuntimeError(f"Wordbook not found: {CET6_SLUG}")
        records = list(
            db.scalars(
                select(WordbookEntry)
                .where(WordbookEntry.wordbook_id == wordbook.id)
                .order_by(WordbookEntry.rank, WordbookEntry.id)
            )
        )

        builtin_definitions = read_builtin_definitions()
        for record in records:
            record.definition_en = (
                record.definition_en
                or builtin_definitions.get(record.word.casefold())
            )

        missing_words = {
            record.word.casefold() for record in records if not record.definition_en
        }
        open_definitions = read_open_dictionary_definitions(missing_words)
        for record in records:
            if not record.definition_en:
                record.definition_en = open_definitions.get(record.word.casefold())

        covered = sum(bool(record.definition_en) for record in records)
        wordbook.description = (
            "大学英语六级考试词汇，包含音标、英汉双解释义和英语例句。"
            "释义来自 ECDICT、Enplay 内置词库及 Wiktionary；"
            "例句来自 Enplay 内置词库及 Tatoeba 英语语料。"
        )
        wordbook.source_name = "ECDICT + Enplay + Wiktionary + Tatoeba"
        wordbook.source_url = WIKTIONARY_SOURCE_URL
        wordbook.license_name = "MIT + CC BY-SA 4.0 + CC BY 2.0 FR"
        wordbook.license_url = WIKTIONARY_LICENSE_URL
        db.commit()
        print(
            "CET-6 English definitions: "
            f"{covered}/{len(records)} covered "
            f"({len(builtin_definitions)} built-in candidates, "
            f"{len(open_definitions)} Wiktionary matches)"
        )


if __name__ == "__main__":
    fill_cet6_english_definitions()

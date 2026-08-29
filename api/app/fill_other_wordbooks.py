import csv
import io
import os
import sys

from sqlalchemy import select

from .database import SessionLocal
from .fill_cet6_english_definitions import (
    WIKTIONARY_LICENSE_URL,
    WIKTIONARY_SOURCE_URL,
    ensure_definition_column,
    read_open_dictionary_content,
)
from .import_ecdict import (
    SOURCE_URL,
    compact_text,
    open_source,
    read_builtin_examples,
    read_tatoeba_examples,
)
from .models import Wordbook, WordbookEntry


TARGET_BOOKS = {
    "ecdict-kaoyan": "面向全国硕士研究生招生考试的英语词汇。",
    "ecdict-ielts": "雅思阅读、听力和写作常见考试词汇。",
    "ecdict-toefl": "托福考试常见学术英语词汇。",
    "ecdict-gre": "GRE 文字推理和学术阅读常见词汇。",
}


def read_ecdict_definitions(target_words: set[str]) -> dict[str, str]:
    source_location = os.getenv("ECDICT_SOURCE", SOURCE_URL)
    csv.field_size_limit(min(sys.maxsize, 2_147_483_647))
    definitions: dict[str, str] = {}
    with open_source(source_location) as response:
        stream = io.TextIOWrapper(response, encoding="utf-8-sig", newline="")
        for row in csv.DictReader(stream):
            word = compact_text(row.get("word"), 120).casefold()
            if word not in target_words:
                continue
            definition = compact_text(row.get("definition"))
            if definition:
                definitions.setdefault(word, definition)
    return definitions


def fill_other_wordbooks() -> None:
    ensure_definition_column()
    with SessionLocal() as db:
        wordbooks = list(
            db.scalars(select(Wordbook).where(Wordbook.slug.in_(TARGET_BOOKS)))
        )
        found_slugs = {wordbook.slug for wordbook in wordbooks}
        missing_slugs = set(TARGET_BOOKS).difference(found_slugs)
        if missing_slugs:
            raise RuntimeError(f"Wordbooks not found: {', '.join(sorted(missing_slugs))}")

        records_by_slug: dict[str, list[WordbookEntry]] = {}
        for wordbook in wordbooks:
            records_by_slug[wordbook.slug] = list(
                db.scalars(
                    select(WordbookEntry)
                    .where(WordbookEntry.wordbook_id == wordbook.id)
                    .order_by(WordbookEntry.rank, WordbookEntry.id)
                )
            )

        all_records = [
            record for records in records_by_slug.values() for record in records
        ]
        target_words = {record.word.casefold() for record in all_records}

        ecdict_definitions = read_ecdict_definitions(target_words)
        for record in all_records:
            if not record.definition_en:
                record.definition_en = ecdict_definitions.get(record.word.casefold())

        builtin_examples = read_builtin_examples()
        for record in all_records:
            if not record.example:
                record.example = builtin_examples.get(record.word.casefold())

        missing_example_words = {
            record.word.casefold() for record in all_records if not record.example
        }
        tatoeba_examples = read_tatoeba_examples(missing_example_words)
        for record in all_records:
            if not record.example:
                record.example = tatoeba_examples.get(record.word.casefold())

        open_dictionary_words = {
            record.word.casefold()
            for record in all_records
            if not record.definition_en or not record.example
        }
        open_definitions, open_examples = read_open_dictionary_content(
            open_dictionary_words
        )
        for record in all_records:
            normalized_word = record.word.casefold()
            if not record.definition_en:
                record.definition_en = open_definitions.get(normalized_word)
            if not record.example:
                record.example = open_examples.get(normalized_word)

        for wordbook in wordbooks:
            records = records_by_slug[wordbook.slug]
            english_covered = sum(bool(record.definition_en) for record in records)
            examples_covered = sum(bool(record.example) for record in records)
            missing_definitions = [
                record.word for record in records if not record.definition_en
            ]
            missing_examples = [record.word for record in records if not record.example]
            wordbook.description = (
                f"{TARGET_BOOKS[wordbook.slug]}包含音标、英汉双解释义和英语例句。"
                "释义来自 ECDICT 及 Wiktionary；"
                "例句来自 Enplay 内置词库、Tatoeba 及 Wiktionary。"
            )
            wordbook.source_name = "ECDICT + Enplay + Wiktionary + Tatoeba"
            wordbook.source_url = WIKTIONARY_SOURCE_URL
            wordbook.license_name = "MIT + CC BY-SA 4.0 + CC BY 2.0 FR"
            wordbook.license_url = WIKTIONARY_LICENSE_URL
            print(
                f"{wordbook.slug}: English definitions "
                f"{english_covered}/{len(records)}, examples "
                f"{examples_covered}/{len(records)}"
            )
            if missing_definitions:
                print(
                    f"{wordbook.slug} missing definitions: "
                    f"{', '.join(missing_definitions[:30])}"
                )
            if missing_examples:
                print(
                    f"{wordbook.slug} missing examples: "
                    f"{', '.join(missing_examples[:30])}"
                )

        db.commit()
        print(
            "Source matches: "
            f"{len(ecdict_definitions)} ECDICT definitions, "
            f"{len(builtin_examples)} built-in examples, "
            f"{len(tatoeba_examples)} Tatoeba examples, "
            f"{len(open_definitions)} Wiktionary definitions, "
            f"{len(open_examples)} Wiktionary examples"
        )


if __name__ == "__main__":
    fill_other_wordbooks()

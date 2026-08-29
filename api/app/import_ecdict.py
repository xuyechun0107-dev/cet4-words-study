import csv
import io
import os
import re
import sys
from urllib.request import Request, urlopen

from sqlalchemy import delete, select

from .database import Base, SessionLocal, engine
from .models import Wordbook, WordbookEntry


SOURCE_URL = "https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv"
SOURCE_PAGE = "https://github.com/skywind3000/ECDICT"
LICENSE_URL = "https://github.com/skywind3000/ECDICT/blob/master/LICENSE"

BOOKS = (
    {
        "tag": "cet6",
        "slug": "ecdict-cet6",
        "name": "CET-6 六级词汇",
        "description": "大学英语六级考试词汇，包含音标和英汉释义。",
    },
    {
        "tag": "ky",
        "slug": "ecdict-kaoyan",
        "name": "考研英语词汇",
        "description": "面向全国硕士研究生招生考试的英语词汇。",
    },
    {
        "tag": "ielts",
        "slug": "ecdict-ielts",
        "name": "IELTS 雅思词汇",
        "description": "雅思阅读、听力和写作常见考试词汇。",
    },
    {
        "tag": "toefl",
        "slug": "ecdict-toefl",
        "name": "TOEFL 托福词汇",
        "description": "托福考试常见学术英语词汇。",
    },
    {
        "tag": "gre",
        "slug": "ecdict-gre",
        "name": "GRE 核心词汇",
        "description": "GRE 文字推理和学术阅读常见词汇。",
    },
)


def compact_text(value: str | None, limit: int = 1200) -> str:
    if not value:
        return ""
    normalized = value.replace("\\n", "；").replace("\r", " ").replace("\n", "；")
    normalized = re.sub(r"\s+", " ", normalized).strip(" ；")
    return normalized[:limit]


def frequency_rank(row: dict[str, str], fallback: int) -> int:
    for field in ("frq", "bnc"):
        value = (row.get(field) or "").strip()
        if value.isdigit() and int(value) > 0:
            return int(value)
    return 1_000_000 + fallback


def read_source() -> dict[str, list[dict[str, object]]]:
    entries_by_tag: dict[str, list[dict[str, object]]] = {
        book["tag"]: [] for book in BOOKS
    }
    seen_by_tag: dict[str, set[str]] = {book["tag"]: set() for book in BOOKS}
    source_location = os.getenv("ECDICT_SOURCE", SOURCE_URL)
    csv.field_size_limit(sys.maxsize)

    if source_location.startswith(("http://", "https://")):
        request = Request(
            source_location, headers={"User-Agent": "Enplay-Wordbook-Importer/1.0"}
        )
        source = urlopen(request, timeout=600)
    else:
        source = open(source_location, "rb")

    with source as response:
        stream = io.TextIOWrapper(response, encoding="utf-8-sig", newline="")
        for source_index, row in enumerate(csv.DictReader(stream), start=1):
            tags = set((row.get("tag") or "").lower().split())
            matching_tags = tags.intersection(entries_by_tag)
            if not matching_tags:
                continue

            word = compact_text(row.get("word"), 120)
            definition = compact_text(row.get("translation") or row.get("definition"))
            if not word or not definition:
                continue

            entry = {
                "word": word,
                "phonetic": compact_text(row.get("phonetic"), 255) or None,
                "definition": definition,
                "example": None,
                "rank": frequency_rank(row, source_index),
            }
            normalized_word = word.casefold()
            for tag in matching_tags:
                if normalized_word in seen_by_tag[tag]:
                    continue
                seen_by_tag[tag].add(normalized_word)
                entries_by_tag[tag].append(entry.copy())

    for entries in entries_by_tag.values():
        entries.sort(key=lambda item: (int(item["rank"]), str(item["word"]).casefold()))
    return entries_by_tag


def import_wordbooks() -> None:
    Base.metadata.create_all(bind=engine)
    entries_by_tag = read_source()
    with SessionLocal() as db:
        for display_order, config in enumerate(BOOKS, start=10):
            wordbook = db.scalar(select(Wordbook).where(Wordbook.slug == config["slug"]))
            if wordbook is None:
                wordbook = Wordbook(
                    slug=config["slug"],
                    name=config["name"],
                    description=config["description"],
                    source_name="ECDICT 英汉词典",
                    source_url=SOURCE_PAGE,
                    license_name="MIT",
                    license_url=LICENSE_URL,
                    display_order=display_order,
                )
                db.add(wordbook)

            wordbook.name = config["name"]
            wordbook.description = config["description"]
            wordbook.source_name = "ECDICT 英汉词典"
            wordbook.source_url = SOURCE_PAGE
            wordbook.license_name = "MIT"
            wordbook.license_url = LICENSE_URL
            wordbook.display_order = display_order
            db.flush()

            db.execute(delete(WordbookEntry).where(WordbookEntry.wordbook_id == wordbook.id))
            entries = entries_by_tag[config["tag"]]
            for start in range(0, len(entries), 1000):
                batch = [
                    {**entry, "wordbook_id": wordbook.id}
                    for entry in entries[start : start + 1000]
                ]
                db.bulk_insert_mappings(WordbookEntry, batch)
            wordbook.item_count = len(entries)
            print(f"{wordbook.slug}: {wordbook.item_count} entries")

        db.commit()


if __name__ == "__main__":
    import_wordbooks()

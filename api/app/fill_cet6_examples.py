import os

from sqlalchemy import select

from .database import SessionLocal
from .import_ecdict import (
    TATOEBA_LICENSE_URL,
    TATOEBA_SOURCE_PAGE,
    CET6_EXAMPLE_OVERRIDES,
    add_cet6_examples,
)
from .models import Wordbook, WordbookEntry


CET6_SLUG = "ecdict-cet6"


def fill_cet6_examples() -> None:
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
        if os.getenv("CET6_MANUAL_ONLY") == "1":
            for record in records:
                override = CET6_EXAMPLE_OVERRIDES.get(record.word.casefold())
                if override:
                    record.example = override
        else:
            entries: list[dict[str, object]] = [
                {"word": record.word, "example": record.example} for record in records
            ]
            add_cet6_examples(entries)
            for record, entry in zip(records, entries, strict=True):
                record.example = entry["example"] or None

        covered = sum(record.example is not None for record in records)
        wordbook.description = (
            "大学英语六级考试词汇，包含音标、英汉释义和英语例句。"
            "例句来自 Enplay 内置词库及 Tatoeba 英语语料。"
        )
        wordbook.source_name = "ECDICT + Enplay + Tatoeba"
        wordbook.source_url = TATOEBA_SOURCE_PAGE
        wordbook.license_name = "MIT + CC BY 2.0 FR"
        wordbook.license_url = TATOEBA_LICENSE_URL
        db.commit()
        print(f"CET-6 database update complete: {covered}/{len(records)} examples")


if __name__ == "__main__":
    fill_cet6_examples()

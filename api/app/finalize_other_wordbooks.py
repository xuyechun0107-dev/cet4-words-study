import re

from sqlalchemy import select

from .database import SessionLocal
from .fill_other_wordbooks import TARGET_BOOKS
from .import_ecdict import CET6_EXAMPLE_OVERRIDES, compact_text
from .models import Wordbook, WordbookEntry


MANUAL_DEFINITIONS = {
    "byline": "n. a line in a newspaper or magazine article that names the writer",
    "underutilized": "adj. not used as much as possible or to full capacity",
    "breezeway": "n. a roofed, open-sided passage connecting two buildings",
    "adlib": "v. to speak or perform without preparation",
    "double-cross": "v. to deceive or betray someone after pretending to cooperate",
    "far-reaching": "adj. having a broad influence or significant effects",
    "hardbitten": "adj. tough and cynical because of difficult experiences",
    "heavy-handedness": "n. the use of excessive force or insensitive control",
    "oafishness": "n. clumsy, stupid, or ill-mannered behavior",
    "other-directed": "adj. guided by the expectations and opinions of other people",
    "renunciate": "n. a person who renounces a belief, claim, or way of life",
    "sangfroid": "n. composure or coolness in a difficult situation",
    "scutter": "v. to run hurriedly with short, quick steps",
    "synergic": "adj. relating to combined action that produces a greater effect",
    "xenophobe": "n. a person who fears or dislikes foreigners or foreign cultures",
    "forbes": "n. a surname and proper name used by several organizations",
    "booklist": "n. a list of recommended or required books",
    "helpline": "n. a telephone service that provides advice or assistance",
    "account for": "v. to explain, cause, or form a particular proportion of something",
    "bring about": "v. to cause something to happen",
    "close-up": "n. a photograph or view taken at very close range",
    "co-operation": "n. the act of working together toward a shared purpose",
    "co-operative": "adj. willing to work with others toward a shared purpose",
    "drop-out": "n. a person who leaves a course of study before completing it",
    "first-aid": "n. immediate basic treatment given to an injured or ill person",
    "low-risk": "adj. involving only a small chance of danger, loss, or failure",
    "non-drinker": "n. a person who does not drink alcoholic beverages",
    "ohp": "n. abbreviation for overhead projector",
    "open-book": "adj. allowing reference books to be used during an examination",
    "second-hand": "adj. previously owned or obtained indirectly from another person",
    "water-clock": "n. a device that measures time by the regulated flow of water",
    "water-proof": "adj. not allowing water to pass through",
    "wollongong": "n. a coastal city in New South Wales, Australia",
    "assistantship": "n. a paid academic position or award for a graduate assistant",
    "geomagnetic": "adj. relating to the magnetic field of the Earth",
    "supercontinent": "n. a former landmass made up of most or all continents",
    "in spite of": "prep. despite; without being prevented by",
    "long-standing": "adj. having existed or continued for a long time",
    "per capita": "adv. or adj. for each person",
    "semimolten": "adj. partially melted",
    "space shuttle": "n. a reusable spacecraft designed to travel between Earth and orbit",
    "stereophotograph": "n. a pair of photographs viewed together to create a three-dimensional image",
    "telecommuter": "n. a person who works from home using telecommunications",
}

MANUAL_EXAMPLES = {
    "appal": "The scale of the destruction appalled everyone who visited the town.",
    "goodby": "He waved goodby before boarding the train.",
    "retrospection": "In retrospection, the warning signs had been clear.",
}


def definition_gloss(definition: str) -> str:
    first_sense = definition.split("；", 1)[0]
    cleaned = re.sub(r"^(?:adj|adv|n|v|a|s|r)\.?\s+", "", first_sense, flags=re.I)
    cleaned = cleaned.strip().rstrip(".;")
    return cleaned or "the meaning given in this wordbook"


def build_learning_example(word: str, definition: str) -> str:
    label = "phrase" if " " in word else "word"
    return compact_text(
        f'The {label} "{word}" means {definition_gloss(definition)}.',
        1200,
    )


def finalize_other_wordbooks() -> None:
    with SessionLocal() as db:
        wordbooks = list(
            db.scalars(select(Wordbook).where(Wordbook.slug.in_(TARGET_BOOKS)))
        )
        found_slugs = {wordbook.slug for wordbook in wordbooks}
        missing_slugs = set(TARGET_BOOKS).difference(found_slugs)
        if missing_slugs:
            raise RuntimeError(f"Wordbooks not found: {', '.join(sorted(missing_slugs))}")

        generated_examples = 0
        manual_examples = 0
        manual_definitions = 0
        for wordbook in wordbooks:
            records = list(
                db.scalars(
                    select(WordbookEntry)
                    .where(WordbookEntry.wordbook_id == wordbook.id)
                    .order_by(WordbookEntry.rank, WordbookEntry.id)
                )
            )
            for record in records:
                normalized_word = record.word.casefold()
                if not record.definition_en:
                    record.definition_en = MANUAL_DEFINITIONS.get(normalized_word)
                    if record.definition_en:
                        manual_definitions += 1
                if not record.example:
                    record.example = (
                        CET6_EXAMPLE_OVERRIDES.get(normalized_word)
                        or MANUAL_EXAMPLES.get(normalized_word)
                    )
                    if record.example:
                        manual_examples += 1
                if not record.example and record.definition_en:
                    record.example = build_learning_example(
                        record.word, record.definition_en
                    )
                    generated_examples += 1

            missing_definitions = [
                record.word for record in records if not record.definition_en
            ]
            missing_examples = [record.word for record in records if not record.example]
            if missing_definitions or missing_examples:
                raise RuntimeError(
                    f"{wordbook.slug} is incomplete: "
                    f"{len(missing_definitions)} definitions and "
                    f"{len(missing_examples)} examples missing"
                )

            wordbook.description = (
                f"{TARGET_BOOKS[wordbook.slug]}包含音标、英汉双解释义和英语例句。"
                "释义来自 ECDICT、Wiktionary 及人工校准；"
                "例句来自 Enplay、Tatoeba、Wiktionary，少量缺项使用基于释义的学习句。"
            )
            wordbook.source_name = "ECDICT + Enplay + Wiktionary + Tatoeba"
            print(
                f"{wordbook.slug}: {len(records)}/{len(records)} English definitions, "
                f"{len(records)}/{len(records)} examples"
            )

        db.commit()
        print(
            f"Finalized with {manual_definitions} manually reviewed definitions, "
            f"{manual_examples} curated examples, and "
            f"{generated_examples} definition-based learning examples"
        )


if __name__ == "__main__":
    finalize_other_wordbooks()

from sqlalchemy import select

from .database import SessionLocal
from .models import Wordbook, WordbookEntry


CET6_SLUG = "ecdict-cet6"
MANUAL_DEFINITIONS = {
    "france": "n. a country in western Europe",
    "jesus": "n. the central figure of Christianity",
    "jewish": "adj. relating to Jews or Judaism",
    "seriously": "adv. in a sincere, earnest, or severe manner",
    "sector": "n. a distinct part or area of an economy, society, or system",
    "selection": "n. the act of choosing or something that has been chosen",
    "italian": "n. a person or language of Italy; adj. relating to Italy",
    "senator": "n. an elected or appointed member of a senate",
    "segment": "n. a separate part of something; v. to divide into parts",
    "islam": "n. the monotheistic religion based on the teachings of Muhammad",
    "seemingly": "adv. in a way that appears to be true",
    "separation": "n. the act or state of being moved or kept apart",
    "sentiment": "n. a feeling, attitude, or opinion",
    "sensation": "n. a physical feeling or a state of great public excitement",
    "sensitivity": "n. the quality of responding readily to changes or feelings",
    "severely": "adv. in a very serious, strict, or harsh manner",
    "seminar": "n. a class or meeting for discussion of a particular subject",
    "seldom": "adv. not often; rarely",
    "seller": "n. a person or organization that sells something",
    "sensor": "n. a device that detects or measures a physical property",
    "separately": "adv. apart from others or as a distinct item",
    "semester": "n. one of the main periods into which an academic year is divided",
    "egyptian": "n. a person of Egypt; adj. relating to Egypt",
    "seventeen": "number. the number 17",
    "sermon": "n. a religious or moral talk delivered to an audience",
    "secondly": "adv. used to introduce a second point or reason",
    "setback": "n. a problem or delay that hinders progress",
    "selfish": "adj. concerned mainly with one's own advantage or pleasure",
    "seventy": "number. the number 70",
    "seam": "n. a line where two edges are joined; v. to join along such a line",
    "portuguese": "n. a person or language of Portugal; adj. relating to Portugal",
    "buddhism": "n. a religion and philosophy based on the teachings of the Buddha",
    "arabian": "adj. relating to Arabia or its people",
    "serpent": "n. a large snake, especially in literary or religious use",
    "seaside": "n. an area by the sea; adj. located by the sea",
    "segregate": "v. to separate one group or thing from others",
    "senseless": "adj. lacking meaning or good judgment; unconscious",
    "sedentary": "adj. involving much sitting and little physical activity",
    "seaman": "n. a sailor or person who works aboard a ship",
    "moslem": "n. or adj. an older spelling of Muslim",
    "seaport": "n. a town or harbor where ships load and unload",
    "by-product": "n. a secondary product or incidental result of a process",
    "equipe": "n. a team and its equipment, especially in sport",
    "father-in-law": "n. the father of one's spouse",
    "first-rate": "adj. of excellent quality",
    "i.e.": "adv. that is; in other words",
    "second-hand": "adj. previously owned or obtained indirectly",
    "seminate": "v. to sow, spread, or disseminate",
    "sitting-room": "n. a room used for relaxing and receiving visitors",
    "so-called": "adj. commonly named or described in a particular way",
    "up-to-date": "adj. modern, current, or containing the latest information",
    "upside-down": "adj. with the upper part where the lower part should be",
    "world-wide": "adj. extending or occurring throughout the world",
}


def finalize_cet6_definitions() -> None:
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
        reviewed = 0
        for record in records:
            if not record.definition_en:
                record.definition_en = MANUAL_DEFINITIONS.get(record.word.casefold())
                if record.definition_en:
                    reviewed += 1

        missing_definitions = [record.word for record in records if not record.definition_en]
        missing_examples = [record.word for record in records if not record.example]
        if missing_definitions or missing_examples:
            raise RuntimeError(
                f"CET-6 is incomplete: {len(missing_definitions)} definitions and "
                f"{len(missing_examples)} examples missing"
            )

        wordbook.description = (
            "大学英语六级考试词汇，包含音标、英汉双解释义和英语例句。"
            "释义来自 ECDICT、Enplay、Wiktionary 及人工校准；"
            "例句来自 Enplay 内置词库及 Tatoeba 英语语料。"
        )
        db.commit()
        print(
            f"CET-6 complete: {len(records)}/{len(records)} English definitions, "
            f"{len(records)}/{len(records)} examples; "
            f"{reviewed} definitions manually reviewed"
        )


if __name__ == "__main__":
    finalize_cet6_definitions()

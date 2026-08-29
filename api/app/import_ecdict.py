import bz2
import csv
import io
import json
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
BUILTIN_EXAMPLES_URL = (
    "https://raw.githubusercontent.com/xuyechun0107-dev/"
    "cet4-words-study/main/words.js"
)
TATOEBA_SENTENCES_URL = (
    "https://downloads.tatoeba.org/exports/per_language/eng/"
    "eng_sentences.tsv.bz2"
)
TATOEBA_SOURCE_PAGE = "https://tatoeba.org/en/downloads"
TATOEBA_LICENSE_URL = (
    "https://en.wiki.tatoeba.org/articles/show/using-the-tatoeba-corpus"
)
CET6_EXAMPLE_OVERRIDES = {
    "resultant": "The resultant force pushed the object steadily to the left.",
    "maturation": "The maturation of the cheese takes several months.",
    "calibration": "Regular calibration keeps the laboratory instruments accurate.",
    "tabulate": "The researchers will tabulate the survey results by age group.",
    "firmness": "She tested the firmness of the mattress before buying it.",
    "pedlar": "A travelling pedlar sold small household goods from door to door.",
    "lamentation": "The poem is a lamentation for those lost in the war.",
    "strangler": "The strangler fig gradually wrapped its roots around the host tree.",
    "dynamical": "The researchers developed a dynamical model of the climate system.",
    "telex": "Before email, the company sent urgent orders by telex.",
    "workpiece": "The operator secured the workpiece firmly before starting the machine.",
    "touchable": "The museum created a touchable model for visually impaired visitors.",
    "subscript": "In the formula H₂O, the number two is written as a subscript.",
    "accessary": "The court found him guilty as an accessary to the crime.",
    "attent": "The attent guard noticed the unusual movement near the gate.",
    "by-product": "Heat is a by-product of many industrial processes.",
    "equipe": "The cycling equipe prepared its riders and equipment for the race.",
    "father-in-law": "My father-in-law taught me how to repair the old bicycle.",
    "first-rate": "The hotel provides first-rate service at a reasonable price.",
    "i.e.": "The deadline is next Friday, i.e. seven days from today.",
    "protend": "Certain insects can protend their jaws to catch prey.",
    "reflexion": "The reflexion of light from the water made the surface shine.",
    "second-hand": "She bought a second-hand desk for her new apartment.",
    "seminate": "The organization works to seminate practical knowledge among farmers.",
    "sitting-room": "The family gathered in the sitting-room after dinner.",
    "so-called": "The so-called expert could not answer a basic question.",
    "up-to-date": "Please keep your contact information up-to-date.",
    "upside-down": "The box fell upside-down and spilled its contents.",
    "vitamine": "Older scientific texts sometimes use vitamine as a spelling of vitamin.",
    "world-wide": "The discovery attracted world-wide attention.",
}

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


def open_source(source_location: str):
    if source_location.startswith(("http://", "https://")):
        request = Request(
            source_location, headers={"User-Agent": "Enplay-Wordbook-Importer/1.1"}
        )
        return urlopen(request, timeout=600)
    return open(source_location, "rb")


def word_forms(word: str) -> set[str]:
    normalized = word.casefold()
    if not re.fullmatch(r"[a-z]+", normalized):
        return {normalized}

    forms = {normalized, f"{normalized}s", f"{normalized}ed", f"{normalized}ing"}
    if normalized.endswith("y") and len(normalized) > 2:
        forms.update({f"{normalized[:-1]}ies", f"{normalized[:-1]}ied"})
    if normalized.endswith(("s", "x", "z", "ch", "sh")):
        forms.add(f"{normalized}es")
    if normalized.endswith("e"):
        forms.update({f"{normalized}d", f"{normalized[:-1]}ing"})
    return forms


def score_sentence(sentence: str) -> tuple[int, set[str]] | None:
    if not 24 <= len(sentence) <= 180:
        return None
    if "http://" in sentence or "https://" in sentence or "www." in sentence:
        return None
    if re.search(r"[\[\]{}<>]", sentence):
        return None
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", sentence)
    if not 5 <= len(words) <= 28:
        return None
    ascii_ratio = sum(character.isascii() for character in sentence) / len(sentence)
    if ascii_ratio < 0.98:
        return None
    punctuation_penalty = 0 if sentence[-1] in ".!?" else 15
    tokens = {word.casefold() for word in words}
    return abs(len(sentence) - 82) + punctuation_penalty, tokens


def read_builtin_examples() -> dict[str, str]:
    source_location = os.getenv("BUILTIN_EXAMPLES_SOURCE", BUILTIN_EXAMPLES_URL)
    with open_source(source_location) as response:
        source_text = response.read().decode("utf-8-sig")
    match = re.search(r"const\s+cet4Words\s*=\s*(\[.*\])\s*;?\s*$", source_text, re.S)
    if not match:
        raise ValueError("Unable to locate cet4Words in the built-in word source")
    items = json.loads(match.group(1))
    return {
        str(item["word"]).casefold(): compact_text(item.get("example"), 1200)
        for item in items
        if item.get("word") and item.get("example")
    }


def read_tatoeba_examples(target_words: set[str]) -> dict[str, str]:
    if not target_words:
        return {}

    form_to_words: dict[str, set[str]] = {}
    for word in target_words:
        for form in word_forms(word):
            form_to_words.setdefault(form, set()).add(word)

    examples: dict[str, str] = {}
    scores: dict[str, int] = {}
    source_location = os.getenv("TATOEBA_SENTENCES_SOURCE", TATOEBA_SENTENCES_URL)
    with open_source(source_location) as response:
        decompressor = bz2.BZ2Decompressor()
        buffer = ""
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                decoded = ""
                finished = True
            else:
                decoded = decompressor.decompress(chunk).decode("utf-8", errors="ignore")
                finished = False

            buffer += decoded
            lines = buffer.split("\n")
            buffer = lines.pop()
            if finished and buffer:
                lines.append(buffer)
                buffer = ""

            for line in lines:
                parts = line.rstrip("\r").split("\t", 2)
                sentence = parts[-1].strip() if len(parts) >= 2 else ""
                scored_sentence = score_sentence(sentence)
                if scored_sentence is None:
                    continue
                score, tokens = scored_sentence
                matching_words: set[str] = set()
                for token in tokens.intersection(form_to_words):
                    matching_words.update(form_to_words[token])
                for word in matching_words:
                    exact_bonus = -20 if word in tokens else 0
                    candidate_score = score + exact_bonus
                    if candidate_score < scores.get(word, 10_000):
                        scores[word] = candidate_score
                        examples[word] = sentence

            if finished:
                break
    return examples


def add_cet6_examples(entries: list[dict[str, object]]) -> None:
    builtin_examples = read_builtin_examples()
    for entry in entries:
        normalized_word = str(entry["word"]).casefold()
        entry["example"] = (
            builtin_examples.get(normalized_word)
            or CET6_EXAMPLE_OVERRIDES.get(normalized_word)
        )

    missing_words = {
        str(entry["word"]).casefold() for entry in entries if not entry["example"]
    }
    tatoeba_examples = read_tatoeba_examples(missing_words)
    for entry in entries:
        if not entry["example"]:
            entry["example"] = tatoeba_examples.get(str(entry["word"]).casefold())

    remaining = sum(not entry["example"] for entry in entries)
    print(
        "CET-6 examples: "
        f"{len(entries) - remaining}/{len(entries)} covered "
        f"({len(builtin_examples)} built-in candidates, "
        f"{len(tatoeba_examples)} Tatoeba matches)"
    )
    if remaining:
        print(f"CET-6 examples still missing: {remaining}")


def read_source() -> dict[str, list[dict[str, object]]]:
    entries_by_tag: dict[str, list[dict[str, object]]] = {
        book["tag"]: [] for book in BOOKS
    }
    seen_by_tag: dict[str, set[str]] = {book["tag"]: set() for book in BOOKS}
    source_location = os.getenv("ECDICT_SOURCE", SOURCE_URL)
    csv.field_size_limit(sys.maxsize)

    source = open_source(source_location)

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
    add_cet6_examples(entries_by_tag["cet6"])
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
            if config["tag"] == "cet6":
                wordbook.description = (
                    f'{config["description"]}例句来自 Enplay 内置词库及 Tatoeba 英语语料。'
                )
                wordbook.source_name = "ECDICT + Enplay + Tatoeba"
                wordbook.source_url = TATOEBA_SOURCE_PAGE
                wordbook.license_name = "MIT + CC BY 2.0 FR"
                wordbook.license_url = TATOEBA_LICENSE_URL
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

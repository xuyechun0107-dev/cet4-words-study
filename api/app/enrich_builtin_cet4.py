import argparse
import csv
import json
import re
import sys
from pathlib import Path


MANUAL_DEFINITIONS = {
    "collarborate": "v. 合作；协作（collaborate 的误拼）",
    "independ": "v. 独立；自主；不受他人影响",
    "knocker-up": "n. 敲窗叫醒工；（旧时）受雇敲门或敲窗叫人起床的人",
    "knowledge-based": "adj. 以知识为基础的；知识密集型的",
    "kolsch": "n. 科隆啤酒；源自德国科隆的淡色啤酒",
    "koshari": "n. 库莎丽；由米饭、扁豆、鹰嘴豆和炸洋葱等制成的埃及食物",
}


def compact_text(value: str | None, limit: int = 1200) -> str:
    if not value:
        return ""
    normalized = value.replace("\\n", "；").replace("\r", " ").replace("\n", "；")
    normalized = re.sub(r"\s+", " ", normalized).strip(" ；")
    return normalized[:limit]


def read_words(path: Path) -> list[dict[str, object]]:
    source_text = path.read_text(encoding="utf-8-sig")
    match = re.search(r"const\s+cet4Words\s*=\s*(\[.*\])\s*;?\s*$", source_text, re.S)
    if not match:
        raise ValueError(f"Unable to locate cet4Words in {path}")
    items = json.loads(match.group(1))
    if not isinstance(items, list):
        raise ValueError("cet4Words must be a JSON array")
    return items


def read_chinese_definitions(path: Path) -> dict[str, str]:
    csv.field_size_limit(min(sys.maxsize, 2_147_483_647))
    definitions: dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            word = compact_text(row.get("word"), 120)
            definition = compact_text(row.get("translation"))
            if word and definition:
                definitions.setdefault(word.casefold(), definition)
    return definitions


def enrich_words(words_path: Path, source_path: Path) -> tuple[int, int]:
    items = read_words(words_path)
    definitions = read_chinese_definitions(source_path)
    matched = 0
    for item in items:
        word = str(item.get("word") or "").casefold()
        definition = definitions.get(word) or MANUAL_DEFINITIONS.get(word)
        if definition:
            item["definitionZh"] = definition
            matched += 1

    output = "// 四级词汇数据库\nconst cet4Words = "
    output += json.dumps(items, ensure_ascii=False, indent=2)
    output += "\n"
    words_path.write_text(output, encoding="utf-8", newline="\n")
    return matched, len(items)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add ECDICT Chinese definitions to the built-in CET-4 words file."
    )
    parser.add_argument("--words", type=Path, required=True)
    parser.add_argument("--ecdict", type=Path, required=True)
    args = parser.parse_args()
    matched, total = enrich_words(args.words.resolve(), args.ecdict.resolve())
    print(f"CET-4 Chinese definitions: {matched}/{total} covered")
    if matched != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

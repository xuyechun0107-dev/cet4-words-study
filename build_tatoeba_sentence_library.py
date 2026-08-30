"""Build curated Enplay sentence libraries from official Tatoeba exports.

The input files are the English and Mandarin sentence exports plus their
direct-link export. Text remains attributed to Tatoeba and is distributed
under CC BY 2.0 FR. This script intentionally applies deterministic filters
only; it does not invent or rewrite translations.
"""

from __future__ import annotations

import argparse
import bz2
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


CATEGORY_PATTERNS = {
    "greetingsSocial": r"\b(hello|hi|goodbye|welcome|thank|thanks|sorry|please|meet|name|help)\b",
    "dailyRoutine": r"\b(wake|breakfast|lunch|dinner|sleep|shower|home|room|clean|cook|wash|morning|evening)\b",
    "familyFriends": r"\b(mother|father|mom|dad|parent|brother|sister|family|friend|husband|wife|child|children)\b",
    "foodDining": r"\b(food|eat|drink|water|coffee|tea|restaurant|menu|meal|hungry|thirsty|bread|rice|fruit)\b",
    "shoppingMoney": r"\b(buy|sell|shop|store|price|cost|money|pay|cash|card|cheap|expensive|dollar)\b",
    "travelTransport": r"\b(travel|trip|train|bus|taxi|airport|station|ticket|hotel|flight|drive|road|street|map)\b",
    "workBusiness": r"\b(work|job|office|business|company|meeting|manager|customer|project|email|report)\b",
    "schoolStudy": r"\b(school|study|learn|student|teacher|class|lesson|book|read|write|exam|test|question|answer)\b",
    "healthWellness": r"\b(health|healthy|doctor|hospital|medicine|sick|hurt|pain|exercise|rest|tired|sleep)\b",
    "weatherTime": r"\b(weather|rain|snow|sunny|cloud|wind|hot|cold|today|tomorrow|yesterday|week|month|year|time)\b",
    "technologyCommunication": r"\b(phone|computer|internet|online|message|call|website|password|video|photo|camera)\b",
    "feelingsOpinions": r"\b(feel|think|believe|like|love|hate|happy|sad|angry|afraid|hope|want|need|prefer)\b",
}

COMMON_WORDS = set(
    "a about after again all also am an and any are as ask at away back be because been before best better big but by "
    "call can come could day did do does doing don't down each even every feel find first for from get give go good got "
    "had has have he help her here him his home how i if in into is it its just keep know last left let like little live "
    "long look made make many may me might more most much must my need never new next no not now of off old on one only "
    "or other our out over people please put really right said same say see she should so some something still take tell "
    "than thank that the their them then there these they thing think this those time to too try two up us use very want "
    "was way we well were what when where which who why will with work would yes you your".split()
)

BANNED_ENGLISH = re.compile(
    r"\b(kill|killed|murder|suicide|rape|sex|porn|naked|gun|rifle|bomb|terrorist|corpse|blood)\b",
    re.IGNORECASE,
)
BANNED_CHINESE = re.compile(r"(杀人|谋杀|自杀|强奸|色情|裸体|枪支|炸弹|恐怖分子|尸体)")
TRADITIONAL_MARKERS = set(
    "這個們為會說學習時裡後麼還從對與車書電話體來見聽買賣錢長開關讓應該問題樣點"
    "萬專業東兩嚴喪豐臨麗舉義烏樂喬鄉亂爭於虧雲亞產親億僅侖倉價眾優傘偉傳傷倫僞餘傭傾儀儘償兒黨"
    "蘭關興養獸內冊寫軍農沖況凍淨準幾擊劃別劑勁動務勝勞勢勵勸區醫華協單賣盧衛卻廠廳歷壓厭厲參雙"
    "發變葉號嘆嚇嗎啟員問啞喚喫團園圍國圖圓聖場壞塊堅壇墳墜壯聲殼處備復夠頭誇夾奪奮婦媽嬰孫寧"
    "寶實寵將尋導層屬歲島嶺嶽幣幹廣廁廚廢張強彈彙徑徹憶憂態慣戲戶撲執擔擇擋搶護報擬擴擺搖敵數"
    "斷無舊曆術樹橋機檔檢權條極標樓歡歸殘毀氣漢湯溝滅滿漁灣濕濟燈靈爐爺牆獨獲環現畫異療監盤著"
    "礦碼禮離種穩窮競筆筍簡糧糾紀紅約級細組結給絕統經綠網緊線編緣縣縱總績繼續罷羅職聯聰腦腳"
    "臉臺艱艦藝節範薦藥蘇虛蟲裝複覺觀觸計訂認討訊訓託記講謝識譯議貝負財責賬貨質購貴貸費資賭贏"
    "趕趨軌轉輪輕載輛辦辭邊進遠連選遞遺鄧釋針鈴鐵鐘鑰門閉間聞隊陽陰陳險際雜雞難電靜頂項順須預"
    "領頻題顏風飛飯飲館馬駕驚髮魚鳥麥黃齊幫決當"
)
ENGLISH_SHAPE = re.compile(r"^[A-Za-z][A-Za-z0-9 '\",.!?;:()\-]+[.!?]$")
WORD_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--links", type=Path, required=True)
    parser.add_argument("--english", type=Path, required=True)
    parser.add_argument("--chinese", type=Path, required=True)
    parser.add_argument("--english-audio-index", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--basic-count", type=int, default=1000)
    parser.add_argument("--intermediate-count", type=int, default=1000)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_links(path: Path) -> list[tuple[int, int]]:
    pairs = []
    with bz2.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            left, right = line.rstrip("\n").split("\t")[:2]
            pairs.append((int(left), int(right)))
    return pairs


def read_selected_sentences(path: Path, wanted: set[int]) -> dict[int, str]:
    sentences: dict[int, str] = {}
    with bz2.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            sentence_id, _language, text = line.rstrip("\n").split("\t", 2)
            numeric_id = int(sentence_id)
            if numeric_id in wanted:
                sentences[numeric_id] = text.strip()
    return sentences


def read_audio_sentence_ids(path: Path) -> set[int]:
    sentence_ids = set()
    with bz2.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            sentence_id = line.split("\t", 1)[0]
            sentence_ids.add(int(sentence_id))
    return sentence_ids


def normalized_key(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def choose_category(text: str) -> str:
    lowered = text.casefold()
    for category, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, lowered):
            return category
    return "generalConversation"


def candidate_score(english: str, chinese: str) -> float:
    words = [word.casefold() for word in WORD_PATTERN.findall(english)]
    common_ratio = sum(word in COMMON_WORDS for word in words) / max(len(words), 1)
    score = common_ratio * 10
    score -= abs(len(words) - 8) * 0.18
    score -= sum(char in TRADITIONAL_MARKERS for char in chinese) * 2
    if english.endswith("?"):
        score += 0.4
    if "'" in english:
        score += 0.2
    return score


def is_suitable(english: str, chinese: str) -> bool:
    if not (ENGLISH_SHAPE.fullmatch(english) and re.search(r"[\u3400-\u9fff]", chinese)):
        return False
    words = WORD_PATTERN.findall(english)
    if not 2 <= len(words) <= 16 or not 8 <= len(english) <= 115 or len(chinese) > 60:
        return False
    if max(map(len, words), default=0) > 15:
        return False
    if BANNED_ENGLISH.search(english) or BANNED_CHINESE.search(chinese):
        return False
    if any(char in TRADITIONAL_MARKERS for char in chinese):
        return False
    if english.split()[0].rstrip(".,!?") in {"Tom", "Mary", "John", "Boston"}:
        return False
    interior_proper_nouns = sum(
        token[0].isupper() and token.casefold() not in {"i", "i'm", "i've", "i'll", "i'd"}
        for token in words[1:]
    )
    return interior_proper_nouns <= 1


def build_candidates(
    links: list[tuple[int, int]], english: dict[int, str], chinese: dict[int, str]
) -> list[dict[str, object]]:
    candidates = []
    seen_pairs = set()
    for english_id, chinese_id in links:
        english_text = english.get(english_id, "")
        chinese_text = chinese.get(chinese_id, "")
        pair_key = (normalized_key(english_text), normalized_key(chinese_text))
        if not english_text or not chinese_text or pair_key in seen_pairs:
            continue
        if not is_suitable(english_text, chinese_text):
            continue
        seen_pairs.add(pair_key)
        candidates.append(
            {
                "scene": choose_category(english_text),
                "text": english_text,
                "note": chinese_text,
                "sourceIds": [english_id, chinese_id],
                "wordCount": len(WORD_PATTERN.findall(english_text)),
                "score": candidate_score(english_text, chinese_text),
            }
        )
    return candidates


def balanced_select(candidates: list[dict[str, object]], count: int) -> list[dict[str, object]]:
    buckets: dict[str, list[dict[str, object]]] = defaultdict(list)
    for candidate in candidates:
        buckets[str(candidate["scene"])].append(candidate)
    for bucket in buckets.values():
        bucket.sort(key=lambda item: (-float(item["score"]), str(item["text"])))

    selected = []
    categories = list(CATEGORY_PATTERNS) + ["generalConversation"]
    while len(selected) < count:
        added = False
        for category in categories:
            if buckets[category]:
                selected.append(buckets[category].pop(0))
                added = True
                if len(selected) >= count:
                    break
        if not added:
            break
    return selected


def public_item(candidate: dict[str, object]) -> dict[str, object]:
    return {
        "scene": candidate["scene"],
        "text": candidate["text"],
        "note": candidate["note"],
        "sourceIds": candidate["sourceIds"],
    }


def render_javascript(libraries: list[dict[str, object]], fingerprints: dict[str, str]) -> str:
    payload = json.dumps(libraries, ensure_ascii=False, separators=(",", ":"))
    fingerprints_json = json.dumps(fingerprints, ensure_ascii=False, separators=(",", ":"))
    return (
        ";(function(global){\n"
        "// Generated from Tatoeba English–Mandarin exports; do not edit by hand.\n"
        "// Text license: CC BY 2.0 FR — https://creativecommons.org/licenses/by/2.0/fr/\n"
        f"const sourceFingerprints={fingerprints_json};\n"
        f"const libraries={payload};\n"
        "if(global&&typeof global==='object'){\n"
        "  global.TATOEBA_SENTENCE_SOURCE_FINGERPRINTS=sourceFingerprints;\n"
        "  global.TATOEBA_SENTENCE_LIBRARIES=libraries;\n"
        "}\n"
        "})(typeof window!=='undefined'?window:(typeof globalThis!=='undefined'?globalThis:this));\n"
    )


def main() -> None:
    args = parse_args()
    links = read_links(args.links)
    english_ids = {left for left, _right in links}
    chinese_ids = {right for _left, right in links}
    english = read_selected_sentences(args.english, english_ids)
    chinese = read_selected_sentences(args.chinese, chinese_ids)
    candidates = build_candidates(links, english, chinese)
    if args.english_audio_index:
        audio_sentence_ids = read_audio_sentence_ids(args.english_audio_index)
        candidates = [
            item for item in candidates if int(item["sourceIds"][0]) in audio_sentence_ids
        ]

    basic_pool = [item for item in candidates if int(item["wordCount"]) <= 8]
    intermediate_pool = [item for item in candidates if int(item["wordCount"]) >= 9]
    basic = balanced_select(basic_pool, args.basic_count)
    used_english = {normalized_key(str(item["text"])) for item in basic}
    intermediate = balanced_select(
        [item for item in intermediate_pool if normalized_key(str(item["text"])) not in used_english],
        args.intermediate_count,
    )

    source_url = "https://tatoeba.org"
    license_url = "https://creativecommons.org/licenses/by/2.0/fr/"
    libraries = [
        {
            "id": "builtin-sentences-tatoeba-basic",
            "type": "sentences",
            "name": "基础英汉句库",
            "format": "Tatoeba · CC BY",
            "description": "精选短句；文本来源 Tatoeba，采用 CC BY 2.0 FR 许可。",
            "sourceUrl": source_url,
            "licenseUrl": license_url,
            "items": [public_item(item) for item in basic],
        },
        {
            "id": "builtin-sentences-tatoeba-intermediate",
            "type": "sentences",
            "name": "进阶英汉句库",
            "format": "Tatoeba · CC BY",
            "description": "精选中长句；文本来源 Tatoeba，采用 CC BY 2.0 FR 许可。",
            "sourceUrl": source_url,
            "licenseUrl": license_url,
            "items": [public_item(item) for item in intermediate],
        },
    ]
    fingerprints = {
        "links": sha256(args.links),
        "english": sha256(args.english),
        "chinese": sha256(args.chinese),
    }
    if args.english_audio_index:
        fingerprints["englishAudioIndex"] = sha256(args.english_audio_index)
    args.output.write_text(render_javascript(libraries, fingerprints), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "candidate_count": len(candidates),
                "basic_count": len(basic),
                "intermediate_count": len(intermediate),
                "output": str(args.output),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

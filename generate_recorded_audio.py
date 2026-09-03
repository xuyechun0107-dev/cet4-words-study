"""Generate content-addressed Kokoro MP3 clips for Enplay learning content."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path
from time import perf_counter

import lameenc
import numpy as np
from kokoro_onnx import Kokoro


DEFAULT_API_BASE = "https://api-enplay.ningboaoke.com"
DEFAULT_VOICES = ("af_heart", "af_bella", "bf_emma", "am_michael", "bm_george")
API_USER_AGENT = "EnplayAudioBuilder/1.0"
TARGET_RMS_DB = -17.0
PEAK_CEILING_DB = -1.5


def normalize_text(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    return re.sub(r"\s+", " ", text).strip()


def extract_array_fragment(source: str, array_start: int) -> str:
    depth = 0
    quote = ""
    escaped = False
    in_line_comment = False
    in_block_comment = False
    index = array_start
    while index < len(source):
        character = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""

        if in_line_comment:
            if character in "\r\n":
                in_line_comment = False
            index += 1
            continue
        if in_block_comment:
            if character == "*" and following == "/":
                in_block_comment = False
                index += 2
            else:
                index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = ""
            index += 1
            continue
        if character in {'"', "'", "`"}:
            quote = character
            index += 1
            continue
        if character == "/" and following == "/":
            in_line_comment = True
            index += 2
            continue
        if character == "/" and following == "*":
            in_block_comment = True
            index += 2
            continue
        if character == "[":
            depth += 1
        elif character == "]":
            depth -= 1
            if depth == 0:
                return source[array_start : index + 1]
        index += 1
    raise ValueError("JavaScript array is not closed")


def strip_js_comments(source: str) -> str:
    output: list[str] = []
    quote = ""
    escaped = False
    index = 0
    while index < len(source):
        character = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if quote:
            output.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = ""
            index += 1
            continue
        if character in {'"', "'", "`"}:
            quote = character
            output.append(character)
            index += 1
            continue
        if character == "/" and following == "/":
            index += 2
            while index < len(source) and source[index] not in "\r\n":
                index += 1
            continue
        if character == "/" and following == "*":
            index += 2
            while index + 1 < len(source) and source[index : index + 2] != "*/":
                if source[index] in "\r\n":
                    output.append(source[index])
                index += 1
            index += 2
            continue
        output.append(character)
        index += 1
    return "".join(output)


def normalize_js_object_array(source: str) -> str:
    source = strip_js_comments(source)
    output: list[str] = []
    quote = ""
    escaped = False
    index = 0
    while index < len(source):
        character = source[index]
        if quote:
            output.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = ""
            index += 1
            continue
        if character in {'"', "'", "`"}:
            quote = character
            output.append(character)
            index += 1
            continue
        if character.isalpha() or character in "_$":
            identifier_start = index
            index += 1
            while index < len(source) and (
                source[index].isalnum() or source[index] in "_$"
            ):
                index += 1
            identifier = source[identifier_start:index]
            following = index
            while following < len(source) and source[following].isspace():
                following += 1
            output.append(json.dumps(identifier) if source[following:following + 1] == ":" else identifier)
            continue
        if character == ",":
            following = index + 1
            while following < len(source) and source[following].isspace():
                following += 1
            if source[following:following + 1] in {"}", "]"}:
                index += 1
                continue
        output.append(character)
        index += 1
    return "".join(output)


def extract_json_array(path: Path, variable_name: str) -> list[dict[str, object]]:
    source = path.read_text(encoding="utf-8")
    marker = re.search(rf"\bconst\s+{re.escape(variable_name)}\s*=", source)
    if not marker:
        raise ValueError(f"{path} does not contain a variable named {variable_name}")
    start = marker.end()
    array_start = source.index("[", start)
    decoder = json.JSONDecoder()
    try:
        value, _ = decoder.raw_decode(source[array_start:])
    except json.JSONDecodeError:
        fragment = extract_array_fragment(source, array_start)
        value = json.loads(normalize_js_object_array(fragment))
    if not isinstance(value, list):
        raise ValueError(f"{path} does not contain an array named {variable_name}")
    return value


def fetch_json(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    payload: object | None = None,
) -> object:
    request_headers = {"User-Agent": API_USER_AGENT}
    if headers:
        request_headers.update(headers)
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(url, data=body, headers=request_headers)
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


class PresenceAwareApiClient:
    """Fetch Enplay API data and transparently maintain a visitor lease."""

    def __init__(self, api_base: str) -> None:
        self.api_base = api_base.rstrip("/")
        self.presence_token: str | None = None

    def join_presence(self) -> None:
        status = fetch_json(
            f"{self.api_base}/v1/presence/join",
            payload={"token": self.presence_token},
        )
        if not isinstance(status, dict) or not status.get("admitted"):
            raise RuntimeError("Enplay API visitor capacity is full; retry later")
        token = status.get("token")
        if not isinstance(token, str) or not token:
            raise ValueError("Enplay API presence response did not contain a token")
        self.presence_token = token

    def fetch(self, path: str) -> object:
        url = f"{self.api_base}/{path.lstrip('/')}"
        headers = (
            {"X-Presence-Token": self.presence_token}
            if self.presence_token
            else None
        )
        try:
            return fetch_json(url, headers=headers)
        except urllib.error.HTTPError as error:
            if error.code != 401:
                raise
            error.close()

        # A first protected request establishes the lease lazily. If an existing
        # lease expired during a long collection, joining with its signed token
        # renews the same visitor and the request is retried once.
        self.join_presence()
        return fetch_json(
            url,
            headers={"X-Presence-Token": self.presence_token},
        )


def collect_tatoeba_texts(workspace: Path) -> list[str]:
    texts: dict[str, None] = {}
    tatoeba_path = workspace / "sentences_tatoeba.js"
    if not tatoeba_path.exists():
        return []
    for library in extract_json_array(tatoeba_path, "libraries"):
        for item in library.get("items", []):
            sentence = normalize_text(item.get("text"))
            if sentence:
                texts.setdefault(sentence, None)
    return list(texts)


def collect_article_texts(workspace: Path) -> list[str]:
    texts: dict[str, None] = {}
    articles_path = workspace / "articles_graded.js"
    if not articles_path.exists():
        return []
    for library in extract_json_array(articles_path, "gradedArticleLibraries"):
        for article in library.get("items", []):
            for sentence in article.get("sentences", []):
                english = normalize_text(
                    sentence.get("en") if isinstance(sentence, dict) else sentence
                )
                if english:
                    texts.setdefault(english, None)
    return list(texts)


def collect_texts(workspace: Path, api_base: str, source_mode: str = "all") -> list[str]:
    if source_mode == "tatoeba":
        return collect_tatoeba_texts(workspace)
    if source_mode == "articles":
        return collect_article_texts(workspace)

    texts: dict[str, None] = {}

    for item in extract_json_array(workspace / "words.js", "cet4Words"):
        example = normalize_text(item.get("example"))
        if example:
            texts.setdefault(example, None)

    for item in extract_json_array(workspace / "phrases_normalized.js", "phrases"):
        sentence = normalize_text(item.get("sentence"))
        if sentence:
            texts.setdefault(sentence, None)

    for sentence in collect_tatoeba_texts(workspace):
        texts.setdefault(sentence, None)

    for sentence in collect_article_texts(workspace):
        texts.setdefault(sentence, None)

    api = PresenceAwareApiClient(api_base)
    catalog = api.fetch("/v1/wordbooks")
    if not isinstance(catalog, list):
        raise ValueError("Wordbook catalog response is not a list")
    for summary in catalog:
        slug = summary["slug"]
        wordbook = api.fetch(f"/v1/wordbooks/{slug}")
        for item in wordbook.get("items", []):
            example = normalize_text(item.get("example"))
            if example:
                texts.setdefault(example, None)

    offset = 0
    while True:
        page = api.fetch(f"/v1/sentences?offset={offset}&limit=200")
        if not isinstance(page, list) or not page:
            break
        for item in page:
            sentence = normalize_text(item.get("text"))
            if sentence:
                texts.setdefault(sentence, None)
        offset += len(page)
        if len(page) < 200:
            break

    return list(texts)


def output_path(root: Path, voice: str, text: str) -> Path:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return root / "v1" / voice / digest[:2] / f"{digest}.mp3"


def normalize_loudness(samples: np.ndarray) -> np.ndarray:
    audio = np.asarray(samples, dtype=np.float32)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    if not audio.size:
        return audio

    rms = float(np.sqrt(np.mean(np.square(audio), dtype=np.float64)))
    if rms <= 1e-8 or float(np.max(np.abs(audio))) <= 1e-8:
        return audio

    target_rms = 10 ** (TARGET_RMS_DB / 20)
    peak_ceiling = 10 ** (PEAK_CEILING_DB / 20)

    def limited(gain: float) -> np.ndarray:
        return peak_ceiling * np.tanh((audio * gain) / peak_ceiling)

    lower_gain = 0.0
    upper_gain = max(target_rms / rms, 1.0)
    while upper_gain < 64.0:
        candidate = limited(upper_gain)
        candidate_rms = float(np.sqrt(np.mean(np.square(candidate), dtype=np.float64)))
        if candidate_rms >= target_rms:
            break
        upper_gain *= 2.0

    for _ in range(18):
        gain = (lower_gain + upper_gain) / 2.0
        candidate = limited(gain)
        candidate_rms = float(np.sqrt(np.mean(np.square(candidate), dtype=np.float64)))
        if candidate_rms < target_rms:
            lower_gain = gain
        else:
            upper_gain = gain

    return limited(upper_gain)


def encode_mp3(samples: np.ndarray, sample_rate: int) -> bytes:
    pcm = normalize_loudness(samples)
    pcm = (pcm * 32767).astype("<i2", copy=False)
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(64)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(2)
    return encoder.encode(pcm.tobytes()) + encoder.flush()


def language_for_voice(voice: str) -> str:
    return "en-gb" if voice.startswith("b") else "en-us"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--voices-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--voices", nargs="+", default=list(DEFAULT_VOICES))
    parser.add_argument(
        "--source-mode", choices=("all", "tatoeba", "articles"), default="all"
    )
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.shard_count < 1 or not 0 <= args.shard_index < args.shard_count:
        parser.error("shard index must be within the configured shard count")
    texts = collect_texts(args.workspace.resolve(), args.api_base, args.source_mode)
    texts = texts[args.shard_index :: args.shard_count]
    if args.limit > 0:
        texts = texts[: args.limit]
    total = len(texts) * len(args.voices)
    print(f"Collected {len(texts)} unique texts; target clips: {total}", flush=True)
    if args.dry_run:
        return

    started = perf_counter()
    completed = 0
    skipped = 0
    failed = 0
    kokoro = Kokoro(str(args.model.resolve()), str(args.voices_file.resolve()))

    for voice in args.voices:
        for text in texts:
            destination = output_path(args.output.resolve(), voice, text)
            if destination.exists() and destination.stat().st_size > 0:
                skipped += 1
                completed += 1
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            try:
                samples, sample_rate = kokoro.create(
                    text,
                    voice=voice,
                    speed=1.0,
                    lang=language_for_voice(voice),
                )
                temporary = destination.with_suffix(".mp3.tmp")
                temporary.write_bytes(encode_mp3(samples, sample_rate))
                temporary.replace(destination)
            except Exception as error:
                failed += 1
                print(f"FAILED voice={voice} text={text!r}: {error}", flush=True)
            completed += 1
            if completed % args.progress_every == 0 or completed == total:
                elapsed = perf_counter() - started
                rate = completed / elapsed if elapsed else 0
                remaining = (total - completed) / rate if rate else 0
                print(
                    f"{completed}/{total} clips; {rate:.2f} clips/s; "
                    f"ETA {remaining / 3600:.2f}h; skipped {skipped}; failed {failed}",
                    flush=True,
                )

    print(f"Finished: completed={completed} skipped={skipped} failed={failed}", flush=True)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

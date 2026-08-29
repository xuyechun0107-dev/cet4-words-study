"""Generate content-addressed Kokoro MP3 clips for Enplay examples and sentences."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
import urllib.request
from pathlib import Path
from time import perf_counter

import lameenc
import numpy as np
from kokoro_onnx import Kokoro


DEFAULT_API_BASE = "https://api-enplay.ningboaoke.com"
DEFAULT_VOICES = ("af_heart", "af_bella", "bf_emma")


def normalize_text(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    return re.sub(r"\s+", " ", text).strip()


def extract_json_array(path: Path, variable_name: str) -> list[dict[str, object]]:
    source = path.read_text(encoding="utf-8")
    marker = f"const {variable_name} ="
    start = source.index(marker) + len(marker)
    array_start = source.index("[", start)
    decoder = json.JSONDecoder()
    value, _ = decoder.raw_decode(source[array_start:])
    if not isinstance(value, list):
        raise ValueError(f"{path} does not contain an array named {variable_name}")
    return value


def fetch_json(url: str) -> object:
    request = urllib.request.Request(url, headers={"User-Agent": "EnplayAudioBuilder/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def collect_texts(workspace: Path, api_base: str) -> list[str]:
    texts: dict[str, None] = {}

    for item in extract_json_array(workspace / "words.js", "cet4Words"):
        example = normalize_text(item.get("example"))
        if example:
            texts.setdefault(example, None)

    for item in extract_json_array(workspace / "phrases_normalized.js", "phrases"):
        sentence = normalize_text(item.get("sentence"))
        if sentence:
            texts.setdefault(sentence, None)

    catalog = fetch_json(f"{api_base.rstrip('/')}/v1/wordbooks")
    if not isinstance(catalog, list):
        raise ValueError("Wordbook catalog response is not a list")
    for summary in catalog:
        slug = summary["slug"]
        wordbook = fetch_json(f"{api_base.rstrip('/')}/v1/wordbooks/{slug}")
        for item in wordbook.get("items", []):
            example = normalize_text(item.get("example"))
            if example:
                texts.setdefault(example, None)

    offset = 0
    while True:
        page = fetch_json(f"{api_base.rstrip('/')}/v1/sentences?offset={offset}&limit=200")
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


def encode_mp3(samples: np.ndarray, sample_rate: int) -> bytes:
    pcm = np.clip(samples, -1.0, 1.0)
    pcm = (pcm * 32767).astype("<i2", copy=False)
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(64)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(2)
    return encoder.encode(pcm.tobytes()) + encoder.flush()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--voices-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--voices", nargs="+", default=list(DEFAULT_VOICES))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--progress-every", type=int, default=25)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    texts = collect_texts(args.workspace.resolve(), args.api_base)
    if args.limit > 0:
        texts = texts[: args.limit]
    total = len(texts) * len(args.voices)
    print(f"Collected {len(texts)} unique texts; target clips: {total}", flush=True)
    if args.dry_run:
        return

    started = perf_counter()
    completed = 0
    skipped = 0
    kokoro = Kokoro(str(args.model.resolve()), str(args.voices_file.resolve()))

    for voice in args.voices:
        for text in texts:
            destination = output_path(args.output.resolve(), voice, text)
            if destination.exists() and destination.stat().st_size > 0:
                skipped += 1
                completed += 1
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            samples, sample_rate = kokoro.create(text, voice=voice, speed=1.0, lang="en-us")
            destination.write_bytes(encode_mp3(samples, sample_rate))
            completed += 1
            if completed % args.progress_every == 0 or completed == total:
                elapsed = perf_counter() - started
                rate = completed / elapsed if elapsed else 0
                remaining = (total - completed) / rate if rate else 0
                print(
                    f"{completed}/{total} clips; {rate:.2f} clips/s; "
                    f"ETA {remaining / 3600:.2f}h; skipped {skipped}",
                    flush=True,
                )


if __name__ == "__main__":
    main()

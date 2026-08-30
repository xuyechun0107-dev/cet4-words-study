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
DEFAULT_VOICES = ("af_heart", "af_bella", "bf_emma", "am_michael", "bm_george")
TARGET_RMS_DB = -17.0
PEAK_CEILING_DB = -1.5


def normalize_text(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    return re.sub(r"\s+", " ", text).strip()


def extract_json_array(path: Path, variable_name: str) -> list[dict[str, object]]:
    source = path.read_text(encoding="utf-8")
    marker = re.search(rf"\bconst\s+{re.escape(variable_name)}\s*=", source)
    if not marker:
        raise ValueError(f"{path} does not contain a variable named {variable_name}")
    start = marker.end()
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


def collect_texts(workspace: Path, api_base: str, source_mode: str = "all") -> list[str]:
    if source_mode == "tatoeba":
        return collect_tatoeba_texts(workspace)

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
    parser.add_argument("--source-mode", choices=("all", "tatoeba"), default="all")
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


if __name__ == "__main__":
    main()

"""Normalize existing Enplay MP3 clips to a consistent speech loudness."""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from time import perf_counter

import lameenc
import numpy as np
import soundfile as sf

from generate_recorded_audio import PEAK_CEILING_DB, TARGET_RMS_DB, normalize_loudness


NORMALIZATION_TOLERANCE_DB = 0.8


def encode_mp3(samples: np.ndarray, sample_rate: int) -> bytes:
    pcm = (samples * 32767).astype("<i2", copy=False)
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(64)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(2)
    return encoder.encode(pcm.tobytes()) + encoder.flush()


def db(value: float) -> float:
    return 20 * np.log10(max(value, 1e-12))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--progress-every", type=int, default=250)
    parser.add_argument("--sample-size", type=int, default=0)
    parser.add_argument("--seed", type=int, default=20260830)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = sorted(args.root.resolve().rglob("*.mp3"))
    if args.sample_size > 0 and len(files) > args.sample_size:
        files = random.Random(args.seed).sample(files, args.sample_size)
    print(
        f"Found {len(files)} clips; target RMS {TARGET_RMS_DB:.1f} dBFS; "
        f"peak ceiling {PEAK_CEILING_DB:.1f} dBFS",
        flush=True,
    )
    started = perf_counter()
    rewritten = 0
    skipped = 0
    failed = 0
    observed_rms_db: list[float] = []
    observed_peak_db: list[float] = []

    for index, path in enumerate(files, start=1):
        try:
            samples, sample_rate = sf.read(path, dtype="float32", always_2d=False)
            if samples.ndim > 1:
                samples = np.mean(samples, axis=1)
            rms = float(np.sqrt(np.mean(np.square(samples), dtype=np.float64))) if samples.size else 0.0
            peak = float(np.max(np.abs(samples))) if samples.size else 0.0
            if rms > 1e-8 and peak > 1e-8:
                observed_rms_db.append(db(rms))
                observed_peak_db.append(db(peak))
            normalized = normalize_loudness(samples)
            normalized_rms = (
                float(np.sqrt(np.mean(np.square(normalized), dtype=np.float64)))
                if normalized.size
                else 0.0
            )
            gain_db = db(normalized_rms) - db(rms) if rms > 1e-8 else 0.0

            if abs(gain_db) < NORMALIZATION_TOLERANCE_DB or peak <= 1e-8:
                skipped += 1
            elif not args.dry_run:
                temporary = path.with_suffix(".mp3.tmp")
                temporary.write_bytes(encode_mp3(normalized, sample_rate))
                temporary.replace(path)
                rewritten += 1
            else:
                rewritten += 1
        except Exception as error:
            failed += 1
            print(f"FAILED {path}: {error}", flush=True)

        if index % args.progress_every == 0 or index == len(files):
            elapsed = perf_counter() - started
            rate = index / elapsed if elapsed else 0.0
            print(
                f"{index}/{len(files)} clips; {rate:.2f} clips/s; "
                f"rewritten {rewritten}; skipped {skipped}; failed {failed}",
                flush=True,
            )

    if failed:
        raise SystemExit(1)
    if observed_rms_db:
        rms_percentiles = np.percentile(observed_rms_db, [10, 50, 90])
        print(
            "Observed RMS p10/median/p90: "
            + "/".join(f"{value:.2f}" for value in rms_percentiles)
            + f" dBFS; maximum peak: {max(observed_peak_db):.2f} dBFS",
            flush=True,
        )


if __name__ == "__main__":
    main()

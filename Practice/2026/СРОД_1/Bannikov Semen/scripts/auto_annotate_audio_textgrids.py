from __future__ import annotations

import subprocess
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
RAW_AUDIO_DIR = ROOT / "data" / "raw" / "audio"
OUT_DIR = ROOT / "data" / "annotations" / "audio"


@dataclass
class Interval:
    xmin: float
    xmax: float
    text: str


def fmt(v: float) -> str:
    return f"{v:.12f}".rstrip("0").rstrip(".")


def get_species_id(stem: str) -> str:
    m = re.match(r"(SP\d{3})_aud_\d{2}", stem, flags=re.IGNORECASE)
    if not m:
        return "SP000"
    return m.group(1).upper()


def decode_audio_mono_f32(path: Path, sample_rate: int = 16000) -> Tuple[np.ndarray, int]:
    """
    Декодирование любых форматов (mp3/wav/ogg/flac) через ffmpeg в mono float32.
    """
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(path),
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-f",
        "f32le",
        "pipe:1",
    ]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    if not proc.stdout:
        return np.zeros((0,), dtype=np.float32), sample_rate
    samples = np.frombuffer(proc.stdout, dtype="<f4").astype(np.float32, copy=False)
    return samples, sample_rate


def smooth_activity(active: np.ndarray, min_active_frames: int, min_silence_frames: int) -> np.ndarray:
    """
    Сглаживание бинарной маски:
    1) заполняем короткие паузы между активными сегментами;
    2) удаляем слишком короткие активные сегменты.
    """
    a = active.copy()
    n = len(a)
    if n == 0:
        return a

    # Fill short inactive gaps.
    i = 0
    while i < n:
        if a[i]:
            i += 1
            continue
        start = i
        while i < n and not a[i]:
            i += 1
        end = i
        gap_len = end - start
        left_on = start > 0 and a[start - 1]
        right_on = end < n and a[end]
        if left_on and right_on and gap_len <= min_silence_frames:
            a[start:end] = True

    # Remove short active runs.
    i = 0
    while i < n:
        if not a[i]:
            i += 1
            continue
        start = i
        while i < n and a[i]:
            i += 1
        end = i
        run_len = end - start
        if run_len < min_active_frames:
            a[start:end] = False
    return a


def detect_bird_activity_intervals(samples: np.ndarray, sr: int) -> List[Tuple[float, float]]:
    if samples.size == 0:
        return []

    frame = max(256, int(0.03 * sr))  # ~30 ms
    hop = max(128, int(0.01 * sr))    # ~10 ms
    if samples.size < frame:
        return []

    n_frames = 1 + (samples.size - frame) // hop
    shape = (n_frames, frame)
    strides = (samples.strides[0] * hop, samples.strides[0])
    framed = np.lib.stride_tricks.as_strided(samples, shape=shape, strides=strides)
    rms = np.sqrt(np.mean(framed * framed, axis=1) + 1e-12)

    noise = float(np.percentile(rms, 30))
    peak = float(np.percentile(rms, 95))
    # Адаптивный порог между шумовым полом и пиками.
    threshold = noise + 0.30 * max(peak - noise, 1e-6)
    active = rms >= threshold

    active = smooth_activity(
        active,
        min_active_frames=max(1, int(0.18 / (hop / sr))),
        min_silence_frames=max(1, int(0.12 / (hop / sr))),
    )

    intervals: List[Tuple[float, float]] = []
    i = 0
    while i < len(active):
        if not active[i]:
            i += 1
            continue
        start = i
        while i < len(active) and active[i]:
            i += 1
        end = i
        t0 = (start * hop) / sr
        t1 = min(((end - 1) * hop + frame) / sr, samples.size / sr)
        if t1 - t0 >= 0.12:
            intervals.append((t0, t1))
    return intervals


def build_intervals_from_activity(
    duration: float,
    species_id: str,
    activity: List[Tuple[float, float]],
) -> Tuple[List[Interval], List[Interval], List[Interval]]:
    bird: List[Interval] = []
    t = 0.0
    for s, e in activity:
        s = max(0.0, min(s, duration))
        e = max(0.0, min(e, duration))
        if s > t:
            bird.append(Interval(t, s, ""))
        if e > s:
            bird.append(
                Interval(
                    s,
                    e,
                    f"species_id={species_id};signal_type=song;overlap_flag=no",
                )
            )
        t = max(t, e)
    if t < duration:
        bird.append(Interval(t, duration, ""))

    # Фоновые интервалы зеркально относительно BirdCallSegment.
    bg: List[Interval] = []
    for iv in bird:
        if iv.text:
            bg.append(Interval(iv.xmin, iv.xmax, ""))
        else:
            bg.append(Interval(iv.xmin, iv.xmax, "type=background;intensity=unknown"))

    meta = [Interval(0.0, duration, "quality=auto_generated_energy")]
    return bird, bg, meta


def render_tier(tier_name: str, intervals: List[Interval], tier_idx: int, xmin: float, xmax: float) -> str:
    lines: List[str] = []
    lines.append(f"    item [{tier_idx}]:")
    lines.append('        class = "IntervalTier"')
    lines.append(f'        name = "{tier_name}"')
    lines.append(f"        xmin = {fmt(xmin)}")
    lines.append(f"        xmax = {fmt(xmax)}")
    lines.append(f"        intervals: size = {len(intervals)}")
    for i, iv in enumerate(intervals, start=1):
        lines.append(f"        intervals [{i}]:")
        lines.append(f"            xmin = {fmt(iv.xmin)}")
        lines.append(f"            xmax = {fmt(iv.xmax)}")
        lines.append(f'            text = "{iv.text}"')
    return "\n".join(lines)


def write_textgrid(out_path: Path, duration: float, bird: List[Interval], bg: List[Interval], meta: List[Interval]) -> None:
    body = [
        'File type = "ooTextFile"',
        'Object class = "TextGrid"',
        "",
        "xmin = 0",
        f"xmax = {fmt(duration)}",
        "tiers? <exists>",
        "size = 3",
        "item []:",
        render_tier("BirdCallSegment", bird, 1, 0.0, duration),
        render_tier("BackgroundSound", bg, 2, 0.0, duration),
        render_tier("Meta", meta, 3, 0.0, duration),
        "",
    ]
    out_path.write_text("\n".join(body), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audio_files = sorted(
        p for p in RAW_AUDIO_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in {".mp3", ".wav", ".ogg", ".flac"}
    )

    if not audio_files:
        raise SystemExit("No audio files found in data/raw/audio.")

    generated = 0
    for path in audio_files:
        species_id = get_species_id(path.stem)
        try:
            samples, sr = decode_audio_mono_f32(path, sample_rate=16000)
            dur = len(samples) / float(sr) if sr else 0.0
            activity = detect_bird_activity_intervals(samples, sr)
            bird, bg, meta = build_intervals_from_activity(dur, species_id, activity)
        except Exception as exc:
            # Если декодирование/анализ сорвались, сохраняем один пустой интервал.
            print(f"[WARN] Fallback for {path.name}: {exc}")
            dur = 30.0
            bird = [Interval(0.0, dur, "")]
            bg = [Interval(0.0, dur, "type=background;intensity=unknown")]
            meta = [Interval(0.0, dur, "quality=auto_generated_fallback")]

        out_name = f"{path.stem}_auto.TextGrid"
        out_path = OUT_DIR / out_name
        write_textgrid(out_path, dur, bird, bg, meta)
        generated += 1

    print(f"Generated draft TextGrid files: {generated}")


if __name__ == "__main__":
    main()

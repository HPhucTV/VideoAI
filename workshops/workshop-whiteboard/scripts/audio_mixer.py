#!/usr/bin/env python3
"""
OmniVideo Studio - Whiteboard Audio Mixer
Hệ thống xử lý âm thanh đa tầng cho Truyện Audio:
- Trộn giọng đọc (Voice) và nhạc nền (BGM)
- Cơ chế Audio Ducking tự động qua sidechaincompress:
  + Khi nhân vật nói: BGM tự động hạ xuống ~12-15%
  + Khi ngắt nghỉ hoặc lau bảng: BGM tự động dâng lên ~35-40%
- Sinh nhạc nền ambient thư giãn mặc định nếu chưa có
"""
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import numpy as np
except ImportError:
    np = None


def build_ducking_filter_complex(
    bgm_base_vol: float = 0.35,
    duck_ratio: float = 6.0,
    attack_ms: int = 100,
    release_ms: int = 700,
    threshold: float = 0.03,
) -> str:
    """Tạo chuỗi filter_complex cho FFmpeg để thực hiện Audio Ducking."""
    return (
        f"[0:a]asplit=2[voice_sc][voice_mix];"
        f"[1:a]volume={bgm_base_vol}[bgm];"
        f"[bgm][voice_sc]sidechaincompress=threshold={threshold}:ratio={duck_ratio}:attack={attack_ms}:release={release_ms}[ducked_bgm];"
        f"[voice_mix][ducked_bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]"
    )


def resolve_bgm_path(bgm_arg: str | Path | None, root_dir: Path | None = None) -> Path | None:
    """Tìm đường dẫn tệp BGM từ tham số hoặc asset mặc định."""
    if bgm_arg:
        p = Path(bgm_arg)
        if p.exists():
            return p

    if root_dir is None:
        root_dir = Path(__file__).resolve().parent.parent.parent.parent

    default_bgm = root_dir / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "healing-piano.mp3"
    if default_bgm.exists():
        return default_bgm

    return None


def generate_default_ambient_bgm(output_path: Path, duration_sec: float = 32.0, ffmpeg_bin: str = "ffmpeg") -> Path:
    """
    Sinh vòng lặp hợp âm piano/ambient êm dịu (Cmaj7 - Am9 - Fmaj7 - Gsus4) bằng NumPy.
    """
    if np is None:
        raise RuntimeError("Cần cài đặt NumPy để tự động sinh nhạc nền ambient")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sr = 44100
    total_samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, total_samples, endpoint=False)

    # 4 hợp âm lofi/healing (mỗi hợp âm 8 giây): Cmaj7, Am9, Fmaj7, Gsus4
    chords = [
        [261.63, 329.63, 392.00, 493.88],  # C4, E4, G4, B4 (Cmaj7)
        [220.00, 261.63, 329.63, 493.88],  # A3, C4, E4, B4 (Am9)
        [174.61, 220.00, 261.63, 329.63],  # F3, A3, C4, E4 (Fmaj7)
        [196.00, 261.63, 293.66, 392.00],  # G3, C4, D4, G4 (Gsus4)
    ]
    chord_dur = duration_sec / len(chords)

    audio_left = np.zeros(total_samples, dtype=np.float32)
    audio_right = np.zeros(total_samples, dtype=np.float32)

    for i, chord in enumerate(chords):
        c_start = int(i * chord_dur * sr)
        c_end = int((i + 1) * chord_dur * sr)
        c_t = np.linspace(0, chord_dur, c_end - c_start, endpoint=False)
        envelope = np.exp(-c_t * 0.45) * (1.0 - np.exp(-c_t * 20.0))

        for note_idx, freq in enumerate(chord):
            # Harmonics
            h1 = np.sin(2 * np.pi * freq * c_t)
            h2 = 0.35 * np.sin(2 * np.pi * (freq * 2) * c_t)
            h3 = 0.15 * np.sin(2 * np.pi * (freq * 3) * c_t)
            tone = (h1 + h2 + h3) * envelope

            pan = 0.4 + 0.2 * (note_idx / max(1, len(chord) - 1))
            audio_left[c_start:c_end] += tone * (1.0 - pan)
            audio_right[c_start:c_end] += tone * pan

    # Normalize
    max_val = max(np.max(np.abs(audio_left)), np.max(np.abs(audio_right)), 1e-5)
    audio_left = (audio_left / max_val * 0.75 * 32767).astype(np.int16)
    audio_right = (audio_right / max_val * 0.75 * 32767).astype(np.int16)

    interleaved = np.empty((total_samples, 2), dtype=np.int16)
    interleaved[:, 0] = audio_left
    interleaved[:, 1] = audio_right
    raw_bytes = interleaved.tobytes()

    cmd = [
        ffmpeg_bin, "-y",
        "-f", "s16le",
        "-ar", str(sr),
        "-ac", "2",
        "-i", "pipe:0",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(output_path),
    ]
    res = subprocess.run(cmd, input=raw_bytes, capture_output=True)
    if res.returncode != 0:
        raise RuntimeError(f"Lỗi khi mã hóa BGM bằng FFmpeg: {res.stderr}")

    return output_path


def mix_voice_and_bgm(
    voice_path: Path,
    bgm_path: Path,
    output_path: Path,
    bgm_base_vol: float = 0.35,
    duck_ratio: float = 6.0,
    ffmpeg_bin: str = "ffmpeg",
) -> Path:
    """Trộn voice và BGM có hiệu ứng Audio Ducking."""
    filter_complex = build_ducking_filter_complex(
        bgm_base_vol=bgm_base_vol,
        duck_ratio=duck_ratio,
    )
    cmd = [
        ffmpeg_bin, "-y",
        "-i", str(voice_path),
        "-stream_loop", "-1",
        "-i", str(bgm_path),
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-ac", "2",
        str(output_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        raise RuntimeError(f"Lỗi khi trộn âm thanh FFmpeg: {res.stderr}")
    return output_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Trộn âm thanh Voice và BGM với hiệu ứng Audio Ducking")
    parser.add_argument("--voice", required=True, help="Đường dẫn file voice audio (mp3/wav)")
    parser.add_argument("--bgm", default=None, help="Đường dẫn file BGM (mặc định tự tìm hoặc tự tạo)")
    parser.add_argument("--output", required=True, help="Đường dẫn file audio sau khi trộn")
    parser.add_argument("--bgm-vol", type=float, default=0.35, help="Âm lượng nền BGM cơ bản (0.1 - 1.0)")
    parser.add_argument("--duck-ratio", type=float, default=6.0, help="Tỷ lệ nén ducking khi có giọng đọc")
    args = parser.parse_args(argv)

    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    bgm_file = resolve_bgm_path(args.bgm, root_dir=root_dir)

    if bgm_file is None:
        default_bgm = root_dir / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "healing-piano.mp3"
        print(f"[*] Đang tự động tạo BGM ambient thư giãn: {default_bgm}...")
        generate_default_ambient_bgm(default_bgm)
        bgm_file = default_bgm

    out_file = Path(args.output)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"[*] Đang trộn âm thanh với BGM Ducking: {args.voice} + {bgm_file} -> {out_file}...")
    mix_voice_and_bgm(
        Path(args.voice),
        bgm_file,
        out_file,
        bgm_base_vol=args.bgm_vol,
        duck_ratio=args.duck_ratio,
    )
    print(f"[OK] Đã xuất tệp âm thanh hoàn chỉnh: {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4 (Cinematic AI Video Studio)
Synthesize Master Audio (Edge-TTS 48kHz Stereo) for all beats in a job.json.
"""
import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

# Add workshop-cinematic root to path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agent.services.edge_tts_service import synthesize_edge_tts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AudioSynthesizer")


def get_audio_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 0.0


def synthesize_all_beats(job_path: Path, output_dir: Path = None, speed_factor: float = 1.25):
    job_data = json.loads(job_path.read_text(encoding="utf-8"))
    job_id = job_data.get("jobId", "cinematic-job")
    beats = job_data.get("beats", [])

    if not output_dir:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        output_dir = repo_root / "output" / "cinematic" / job_id / "audio"

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    total_duration = 0.0

    print("=" * 65)
    print(f" 🎙️ BẮT ĐẦU TẠO MASTER AUDIO 48KHZ STEREO CHO JOB: {job_id} (Tốc độ: {speed_factor}x)")
    print(f" 📋 Tổng số Beats: {len(beats)}")
    print("=" * 65)

    for idx, beat in enumerate(beats, start=1):
        raw_text = beat.get("rawText", "").strip()
        speaker = beat.get("speaker") or "Người Kể Chuyện"
        beat_id = beat.get("id", f"beat_{idx:02d}")
        out_file = output_dir / f"scene_{idx:02d}_{beat_id}.mp3"

        if not raw_text:
            continue

        print(f"\n[{idx:02d}/{len(beats):02d}] ({speaker}): \"{raw_text}\"")
        synthesize_edge_tts(raw_text, out_file, speaker_name=speaker, speed_factor=speed_factor)
        dur = get_audio_duration(out_file)
        total_duration += dur

        manifest.append({
            "index": idx,
            "beat_id": beat_id,
            "speaker": speaker,
            "text": raw_text,
            "file": str(out_file.relative_to(output_dir.parent.parent.parent)),
            "duration": round(dur, 2)
        })
        print(f"      => Đã tạo xong: {out_file.name} ({dur:.2f}s)")

    manifest_path = output_dir / "audio_manifest.json"
    manifest_path.write_text(json.dumps({
        "jobId": job_id,
        "speedFactor": speed_factor,
        "totalBeats": len(manifest),
        "totalDurationSeconds": round(total_duration, 2),
        "tracks": manifest
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 65)
    print(f" 🎉 HOÀN THÀNH TẠO AUDIO ({speed_factor}x): {len(manifest)} tracks | Tổng thời lượng: {total_duration:.1f}s (~{total_duration/60:.1f} phút)")
    print(f" 💾 Manifest lưu tại: {manifest_path}")
    print("=" * 65)
    return manifest_path


def main():
    parser = argparse.ArgumentParser(description="Tạo âm thanh Edge-TTS 48kHz cho job.json")
    parser.add_argument("job", help="Đường dẫn file job.json hoặc job ID")
    parser.add_argument("--output-dir", "-o", default=None, help="Thư mục xuất âm thanh")
    parser.add_argument("--speed-factor", "-s", type=float, default=1.25, help="Hệ số tốc độ (mặc định 1.25)")
    args = parser.parse_args()

    from scripts.run_pipeline import resolve_job_path
    job_p = resolve_job_path(args.job)
    synthesize_all_beats(job_p, Path(args.output_dir) if args.output_dir else None, speed_factor=args.speed_factor)


if __name__ == "__main__":
    main()

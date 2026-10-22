from __future__ import annotations
import argparse
import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import edge_tts

logger = logging.getLogger("gate4_audio")

# Character voice pitch/rate modulation rules (voice speed x1.25 standard)
CHARACTER_VOICE_MODULATION: dict[str, dict[str, str]] = {
    "nam_chinh": {"voice": "vi-VN-NamMinhNeural", "rate": "+22%", "pitch": "-4Hz"},
    "phan_dien": {"voice": "vi-VN-NamMinhNeural", "rate": "+30%", "pitch": "+3Hz"},
    "truong_boi": {"voice": "vi-VN-NamMinhNeural", "rate": "+20%", "pitch": "-6Hz"},
    "nu_chinh": {"voice": "vi-VN-HoaiMyNeural", "rate": "+23%", "pitch": "+1Hz"},
    "narrator": {"voice": "vi-VN-NamMinhNeural", "rate": "+25%", "pitch": "-2Hz"},
}


def get_audio_duration_ffprobe(file_path: Path) -> float:
    """Runs ffprobe to get exact audio duration in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    val = res.stdout.strip()
    return round(float(val), 2) if val else 0.0


def synthesize_voice_clip(text: str, speaker: str, out_file: Path) -> tuple[Path, float]:
    """
    Synthesizes audio using Edge-TTS with character modulation and saves to out_file.
    Measures duration with ffprobe and returns (out_file, duration).
    """
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    speaker_key = speaker.lower().strip().replace("-", "_").replace(" ", "_")
    config = CHARACTER_VOICE_MODULATION.get(speaker_key)
    if not config:
        config = CHARACTER_VOICE_MODULATION.get(speaker.lower(), CHARACTER_VOICE_MODULATION["narrator"])

    communicate = edge_tts.Communicate(text, config["voice"], rate=config["rate"], pitch=config["pitch"])
    asyncio.run(communicate.save(str(out_file)))
    dur = get_audio_duration_ffprobe(out_file)
    return out_file, dur


def run_gate4_audio(job_data: dict, output_dir: Path | str) -> dict:
    """
    Executes Gate 4 Audio Generation:
    - Synthesizes all beats in job_data['beats'].
    - Saves individual mp3s to output_dir / 'audio' / 'shots' / f'{shot_id}.mp3'.
    - Writes output_dir / 'audio' / 'audio_manifest.json'.
    - Returns the manifest dict.
    """
    job_id = job_data.get("jobId", "audio-job")
    beats = job_data.get("beats", [])
    output_dir = Path(output_dir)
    audio_dir = output_dir / "audio" / "shots"
    audio_dir.mkdir(parents=True, exist_ok=True)

    shots_manifest = []
    total_dur = 0.0

    for idx, beat in enumerate(beats, 1):
        shot_id = beat.get("id") or beat.get("shot_id") or f"beat_{idx:03d}"
        text = beat.get("rawText") or beat.get("text") or beat.get("dialogue") or ""
        speaker = beat.get("speaker") or beat.get("character") or "narrator"
        out_mp3 = audio_dir / f"{shot_id}.mp3"

        _, dur = synthesize_voice_clip(text, speaker, out_mp3)
        total_dur += dur
        shots_manifest.append({
            "shot": idx,
            "id": shot_id,
            "speaker": speaker,
            "dialogue": text,
            "audio_file": str(out_mp3),
            "duration": dur,
        })

    manifest = {
        "jobId": job_id,
        "total_shots": len(shots_manifest),
        "total_duration": round(total_dur, 2),
        "shots": shots_manifest,
    }

    manifest_file = output_dir / "audio" / "audio_manifest.json"
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Gate 4 Audio generated {len(shots_manifest)} shots, total duration {total_dur:.2f}s")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Gate 4: Edge-TTS 48kHz Audio Suite Runner")
    parser.add_argument("--job", type=Path, required=True, help="Path to job JSON file")
    parser.add_argument("--out", type=Path, required=True, help="Output workspace directory")
    args = parser.parse_args()

    with open(args.job, "r", encoding="utf-8") as f:
        job_data = json.load(f)

    manifest = run_gate4_audio(job_data, args.out)
    print(f"Generated {manifest['total_shots']} shots ({manifest['total_duration']}s) at {args.out / 'audio'}")


if __name__ == "__main__":
    main()

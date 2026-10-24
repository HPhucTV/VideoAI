#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4: Generate 48kHz Stereo Master Audio for 1-Minute AI Agent
"""
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

# Add workshop root to sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agent.services.edge_tts_service import synthesize_edge_tts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AudioAI_Agent")

JOB_PATH = Path("output/jobs/job-ai-agent-explained-1min.json")
OUTPUT_AUDIO_DIR = Path("output/cinematic/job-ai-agent-explained-1min/audio")


def get_audio_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return round(float(res.stdout.strip()), 2)


def main():
    if not JOB_PATH.exists():
        logger.error("Job file not found: %s", JOB_PATH)
        sys.exit(1)

    job_data = json.loads(JOB_PATH.read_text(encoding="utf-8"))
    beats = job_data.get("beats", [])
    logger.info("Found %d beats for job %s", len(beats), job_data.get("jobId"))

    OUTPUT_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    tracks = []
    total_duration = 0.0

    for idx, beat in enumerate(beats, 1):
        beat_id = beat["id"]
        speaker = beat["speaker"]
        text = beat["rawText"]
        out_file = OUTPUT_AUDIO_DIR / f"scene_{idx:02d}_{beat_id}.mp3"

        logger.info("[%d/%d] Generating audio for %s (%s)...", idx, len(beats), beat_id, speaker)
        synthesize_edge_tts(
            text=text,
            output_path=out_file,
            speaker_name=speaker,
            speed_factor=1.05,  # Nhịp nói sinh động, dứt khoát
        )

        dur = get_audio_duration(out_file)
        total_duration += dur

        tracks.append({
            "index": idx,
            "beat_id": beat_id,
            "speaker": speaker,
            "text": text,
            "file": str(out_file.relative_to(Path("output"))),
            "duration": dur,
        })
        logger.info(" -> File: %s | Duration: %.2fs", out_file.name, dur)

    manifest = {
        "jobId": job_data.get("jobId"),
        "totalBeats": len(beats),
        "totalDurationSeconds": round(total_duration, 2),
        "tracks": tracks,
    }

    manifest_file = OUTPUT_AUDIO_DIR / "audio_manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Master Audio Complete! Total duration: %.2fs (12 shots). Manifest: %s", total_duration, manifest_file)


if __name__ == "__main__":
    main()

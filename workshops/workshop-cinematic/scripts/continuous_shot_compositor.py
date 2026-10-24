#!/usr/bin/env python3
"""
OmniVideo Studio - Continuous Incremental Shot Compositor
Composites video clips + Cyber Chatbox + 48kHz audio into rendered_shots/shot_XXX.mp4
in real-time as soon as each video is saved to disk by the sync daemon.
"""
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ShotCompositor")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-mcp-explained-7min"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
VIDEOS_DIR = OUTPUT_DIR / "videos"
AUDIO_DIR = OUTPUT_DIR / "audio"
OVERLAYS_DIR = OUTPUT_DIR / "dialogue_overlays"
RENDERED_DIR = OUTPUT_DIR / "rendered_shots"
MANIFEST_PATH = OUTPUT_DIR / "audio_manifest_105_shots.json"

RENDERED_DIR.mkdir(parents=True, exist_ok=True)

def composite_shot(s: dict):
    s_num = s["shot_num"]
    dur = s.get("duration", 4.0)
    out_clip = RENDERED_DIR / f"shot_{s_num:03d}.mp4"

    if out_clip.exists() and out_clip.stat().st_size > 100_000:
        return True

    v_file = VIDEOS_DIR / f"shot_{s_num:03d}.mp4"
    if not v_file.exists() or v_file.stat().st_size < 500_000:
        return False

    c_file = OVERLAYS_DIR / f"chatbox_shot_{s_num:03d}.png"
    a_file = AUDIO_DIR / f"shot_{s_num:03d}.mp3"

    filter_str = (
        "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=60[base]; "
        "[base][1:v]overlay=160:909[v_comp]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(v_file),
        "-i", str(c_file),
        "-i", str(a_file),
        "-filter_complex", filter_str,
        "-map", "[v_comp]",
        "-map", "2:a",
        "-t", f"{dur:.2f}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-ac", "2",
        "-shortest",
        str(out_clip)
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info("Composited Shot %03d -> %s (size: %.2f MB)", s_num, out_clip.name, out_clip.stat().st_size / (1024*1024))
        return True
    except Exception as e:
        logger.error("Failed to composite Shot %03d: %s", s_num, e)
        return False

def main():
    logger.info("🚀 Continuous Incremental Shot Compositor started...")
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        shots_data = json.load(f)

    while True:
        rendered_count = len(list(RENDERED_DIR.glob("shot_*.mp4")))
        for s in shots_data:
            composite_shot(s)

        current_rendered = len(list(RENDERED_DIR.glob("shot_*.mp4")))
        logger.info("Compositor Progress: %d / 105 shots rendered", current_rendered)

        if current_rendered >= 105:
            logger.info("🎉 ALL 105 SHOTS COMPOSITED INTO RENDERED_DIR!")
            break

        time.sleep(6)

if __name__ == "__main__":
    main()

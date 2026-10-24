import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import math
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-ai-agent-giaimatech-10min"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
AUDIO_DIR = OUTPUT_DIR / "audio"
SHOTS_AUDIO_DIR = AUDIO_DIR / "shots"
SEGMENTS_DIR = OUTPUT_DIR / "segments"
OVERLAYS_DIR = OUTPUT_DIR / "overlays"
FRAMES_DIR = OUTPUT_DIR / "frames"

SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

BRANDING_DIR = BASE_DIR / "shared-assets" / "branding"
INTRO_PATH = BRANDING_DIR / "intro_horizontal_16x9.mp4"
OUTRO_PATH = BRANDING_DIR / "outro_horizontal_16x9.mp4"
LOGO_PATH = BRANDING_DIR / "giaimatech_logo.png"
BGM_PATH = BASE_DIR / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "healing-piano.mp3"

FINAL_VIDEO_MP4 = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.mp4"
FINAL_SRT = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.srt"

SPEC_PATH = OUTPUT_DIR / "STORYBOARD_SPEC_104_SHOTS.md"
JOB_JSON_PATH = BASE_DIR / "output" / "jobs" / f"{JOB_ID}.json"

def format_srt_time(seconds: float) -> str:
    millis = int(round((seconds - int(seconds)) * 1000))
    total_sec = int(seconds)
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def get_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return round(float(res.stdout.strip()), 2)

def generate_srt(shots_data: list, srt_path: Path):
    lines = []
    current_time = 2.0  # After intro bumper (2.0s)
    for idx, s in enumerate(shots_data, 1):
        dur = s["duration"]
        start_t = current_time
        end_t = current_time + dur
        lines.append(f"{idx}\n{format_srt_time(start_t)} --> {format_srt_time(end_t)}\n{s['dialogue']}\n")
        current_time = end_t

    srt_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Đã tạo file phụ đề SRT chuẩn YouTube: {srt_path}")

print("Assembly module initialized.")

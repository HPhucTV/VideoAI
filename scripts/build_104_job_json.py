import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import re
from pathlib import Path

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
SPEC_PATH = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "STORYBOARD_SPEC_104_SHOTS.md"
JOB_OUT = BASE_DIR / "output" / "jobs" / "job-ai-agent-giaimatech-10min.json"

CAMERA_MAPPING = {
    "establishing shot": "dolly_out",
    "medium ots": "dolly_in",
    "macro focus": "dolly_in",
    "tilt down": "tilt_down",
    "tilt up": "tilt_up",
    "pan ngang": "pan_right",
    "pan left": "pan_left",
    "pan right": "pan_right",
    "hero reveal": "orbit_360",
    "hero shot": "dolly_in",
    "medium shot": "static",
    "split screen": "static",
    "pov": "fpv",
    "first-person": "fpv",
    "zoom in": "zoom_in_punch",
    "pull back": "dolly_out",
    "reaction": "static",
    "insert": "dolly_in"
}

def map_camera(shot_type: str) -> str:
    s = shot_type.lower()
    for k, v in CAMERA_MAPPING.items():
        if k in s:
            return v
    return "dolly_in"

def build_job_json():
    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    beats = []
    current_chapter = "Chương 1: Hook"
    
    # Locked Media IDs
    CHAR_MEDIA_ID = "ce05075f-0ea2-4680-8b5b-1e76b60d784e"
    LAB_MEDIA_ID = "399589db-c733-4c0f-9ce5-0bd9007ea967"
    VECTOR_MEDIA_ID = "2653c891-2191-445c-8b96-29ab6311fb0d"

    for line in lines:
        if line.startswith("#### Chương"):
            current_chapter = line.replace("####", "").strip()
        m = re.search(r'\*\s*\*\*Shot\s+(\d+)\s*\((.*?)\)\s*\[(.*?)\]:\*\*\s*(.*?)\s*\*\(Thoại:\s*\"(.*?)\"\)\*', line)
        if m:
            shot_num = int(m.group(1))
            time_spec = m.group(2).strip()
            shot_type = m.group(3).strip()
            action = m.group(4).strip()
            dialogue = m.group(5).strip()

            cam = map_camera(shot_type)

            # Assign master background
            bg_media = VECTOR_MEDIA_ID if (50 <= shot_num <= 75) else LAB_MEDIA_ID

            # Visual prompt tailored with enlarged 3D screen
            visual_prompt = (
                f"3D Donghua Cyber-Chibi style, 16:9. {action}. "
                f"In the virtual high-tech lab, large floating 3D holographic display occupying 70% of the frame "
                f"with ultra high contrast crystal glassmorphism and sharp glowing UI, glowing neon cyan and electric gold, "
                f"Bé Byte chibi robot with expressive glowing LED eyes, photorealistic cinematic lighting, 8k render."
            )

            video_prompt = (
                f"{action}. Large floating 3D holographic screen occupying 70% of frame showing sharp text and UI. "
                f"{cam} cinematic smooth camera movement, luminous neon accents, subtle character gestures, professional 60fps."
            )

            beats.append({
                "id": f"beat-{shot_num:03d}",
                "order": shot_num,
                "chapter": current_chapter,
                "time_spec": time_spec,
                "shot_type": shot_type,
                "speaker": "Bé Byte",
                "rawText": dialogue,
                "cues": {
                    "camera": cam
                },
                "visual": {
                    "prompt": visual_prompt,
                    "video_prompt": video_prompt,
                    "image_media_id": bg_media,
                    "character_media_id": CHAR_MEDIA_ID
                }
            })

    job_data = {
        "jobId": "job-ai-agent-giaimatech-10min",
        "channel": "Giải Mã Tech",
        "channel_handle": "@giaimatech-s8t",
        "title": "AI Agent Là Gì? Khi AI Không Chỉ Trả Lời Mà Còn Biết Hành Động",
        "workshop": "workshop-cinematic",
        "target_duration_seconds": 600,
        "format": "16:9 Landscape (1920x1080 @ 60fps)",
        "canvas": {
            "width": 1920,
            "height": 1080,
            "fps": 60,
            "colorGradingPreset": "cyberpunk_teal_orange"
        },
        "metadata": {
            "language": "vi",
            "characters": ["Bé Byte"],
            "virtual_sets": ["Viện Công Nghệ Tí Hon", "Kho Dữ Liệu Vector"],
            "total_shots": len(beats),
            "asl_seconds": 5.7
        },
        "branding": {
            "intro_path": "shared-assets/branding/intro_horizontal_16x9.mp4",
            "outro_path": "shared-assets/branding/outro_horizontal_16x9.mp4",
            "logo_path": "shared-assets/branding/giaimatech_logo.png",
            "intro_duration": 2.0,
            "outro_duration": 4.5
        },
        "beats": beats
    }

    JOB_OUT.parent.mkdir(parents=True, exist_ok=True)
    JOB_OUT.write_text(json.dumps(job_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Đã tạo job.json với {len(beats)} beats: {JOB_OUT}")

if __name__ == "__main__":
    build_job_json()

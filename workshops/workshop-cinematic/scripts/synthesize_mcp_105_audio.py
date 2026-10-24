#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4 (Cinematic 3D Video Studio)
Synthesize 105 Shots Audio & Cyber Chatbox Overlays for Episode 2: Giải Mã MCP
Standards:
- Edge-TTS Vietnamese Neural (vi-VN-NamMinhNeural @ 48kHz Stereo AAC 192k)
- Strictly Voice x1.25 (rate='+25%')
- Cyber Chatbox Overlay (1600x126px, Cyan Neon 2px, Speaker Badge)
"""
import concurrent.futures
import json
import logging
import shutil
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add workshop root
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agent.services.edge_tts_service import synthesize_edge_tts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SynthesizeMCP105")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-mcp-explained-7min"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
AUDIO_DIR = OUTPUT_DIR / "audio"
OVERLAYS_DIR = OUTPUT_DIR / "dialogue_overlays"
MANIFEST_PATH = OUTPUT_DIR / "mcp_105_manifest.json"
FINAL_AUDIO_MANIFEST = OUTPUT_DIR / "audio_manifest_105_shots.json"
BRAIN_DIR = Path(r"C:\Users\tranh\.gemini\antigravity\brain\74745d7e-e139-4bc8-b6d1-fbc945ef19d8")

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)

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

def get_font(size=32, bold=True):
    font_paths = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for p in font_paths:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()

def generate_chatbox_overlay(shot_num: int, speaker_badge: str, text: str, output_path: Path):
    """
    Renders 1920x1080 transparent PNG with Cyber Chatbox (1600x126px).
    """
    canvas_w, canvas_h = 1920, 1080
    box_w, box_h = 1600, 126
    box_x = (canvas_w - box_w) // 2  # 160
    box_y = canvas_h - box_h - 45    # 909
    radius = 16

    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Box container (Dark translucent 88% alpha)
    box_bg_color = (11, 15, 23, 225)
    border_color = (0, 218, 245, 255)  # Cyan Neon
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=radius,
        fill=box_bg_color,
        outline=border_color,
        width=2
    )

    # 2. Speaker Pill Badge
    badge_h = 28
    font_badge = get_font(18, bold=True)
    bbox_b = font_badge.getbbox(speaker_badge)
    badge_text_w = bbox_b[2] - bbox_b[0]
    badge_w = badge_text_w + 24
    badge_x = box_x + 24
    badge_y = box_y - 14  # overlap slightly on top border

    badge_bg = (0, 180, 216, 255)
    if "SERVER" in speaker_badge:
        badge_bg = (142, 68, 173, 255)  # Purple
    elif "BẢO MẬT" in speaker_badge:
        badge_bg = (230, 126, 34, 255)  # Amber/Orange

    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=8,
        fill=badge_bg,
        outline=(255, 255, 255, 200),
        width=1
    )
    badge_tx = badge_x + (badge_w - badge_text_w) // 2
    badge_ty = badge_y + 4
    draw.text((badge_tx, badge_ty), speaker_badge, font=font_badge, fill=(255, 255, 255, 255))

    # 3. Text Dialogue Centered
    font_dialogue = get_font(32, bold=True)
    bbox_d = font_dialogue.getbbox(text)
    text_w = bbox_d[2] - bbox_d[0]
    text_h = bbox_d[3] - bbox_d[1]

    # Handle text scaling if dialogue is wide
    if text_w > (box_w - 60):
        font_dialogue = get_font(28, bold=True)
        bbox_d = font_dialogue.getbbox(text)
        text_w = bbox_d[2] - bbox_d[0]
        text_h = bbox_d[3] - bbox_d[1]

    text_x = box_x + (box_w - text_w) // 2
    text_y = box_y + (box_h - text_h) // 2 - 2

    # Subtle drop shadow
    draw.text((text_x + 2, text_y + 2), text, font=font_dialogue, fill=(0, 0, 0, 200))
    # Crisp white text
    draw.text((text_x, text_y), text, font=font_dialogue, fill=(255, 255, 255, 255))

    img.save(str(output_path), "PNG")

def process_single_shot(shot):
    num = shot["shot_num"]
    dialogue = shot["dialogue"]
    badge = shot["speaker_badge"]
    
    audio_path = AUDIO_DIR / f"shot_{num:03d}.mp3"
    overlay_path = OVERLAYS_DIR / f"chatbox_shot_{num:03d}.png"
    
    # Synthesize Audio (Voice x1.25)
    if not audio_path.exists() or audio_path.stat().st_size == 0:
        synthesize_edge_tts(
            text=dialogue,
            output_path=audio_path,
            speaker_name="người kể chuyện",
            speed_factor=1.25
        )
    
    dur = get_audio_duration(audio_path)
    
    # Generate Overlay
    generate_chatbox_overlay(num, badge, dialogue, overlay_path)
    
    return {
        "shot_num": num,
        "timing": shot["timing"],
        "shot_type": shot["shot_type"],
        "visual_desc": shot["visual_desc"],
        "dialogue": dialogue,
        "speaker_badge": badge,
        "audio_file": str(audio_path),
        "overlay_file": str(overlay_path),
        "duration": dur
    }

def main():
    if not MANIFEST_PATH.exists():
        logger.error("Manifest not found: %s", MANIFEST_PATH)
        return
    
    shots = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    logger.info("Starting synthesis for %d shots (Voice x1.25)...", len(shots))
    
    results = []
    # Use ThreadPoolExecutor for concurrent edge-tts synthesis
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_shot = {executor.submit(process_single_shot, s): s for s in shots}
        for future in concurrent.futures.as_completed(future_to_shot):
            s = future_to_shot[future]
            try:
                res = future.result()
                results.append(res)
                if len(results) % 15 == 0 or len(results) == len(shots):
                    logger.info("Progress: %d / %d shots processed", len(results), len(shots))
            except Exception as e:
                logger.error("Error processing shot %d: %s", s["shot_num"], e)
                
    results.sort(key=lambda x: x["shot_num"])
    total_dur = sum(x["duration"] for x in results)
    
    FINAL_AUDIO_MANIFEST.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Audio manifest written: %s", FINAL_AUDIO_MANIFEST)
    logger.info("Total Spoken Duration across 105 shots: %.2f seconds (%.2f minutes)", total_dur, total_dur / 60.0)

    # Copy sample audio & overlay to brain directory for user inspection
    sample_nums = [1, 20, 50, 75, 105]
    for sn in sample_nums:
        shutil.copy(AUDIO_DIR / f"shot_{sn:03d}.mp3", BRAIN_DIR / f"sample_shot_{sn:03d}.mp3")
        shutil.copy(OVERLAYS_DIR / f"chatbox_shot_{sn:03d}.png", BRAIN_DIR / f"preview_chatbox_shot_{sn:03d}.png")
    
    logger.info("Copied samples 1, 20, 50, 75, 105 to brain directory.")

if __name__ == "__main__":
    main()

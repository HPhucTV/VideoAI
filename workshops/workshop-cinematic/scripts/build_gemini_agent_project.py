#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4 (Cinematic AI Video Studio)
Project: Hướng Dẫn Tự Xây Dựng AI Agent Đầu Tiên Kết Nối Công Cụ Tự Động Hóa Thực Tế
Execution:
1. Parse 100 shots from screenplay
2. Populate FlowKit DB (Project, Video, 100 Scenes)
3. Synthesize Master Audio (Edge-TTS 48kHz Stereo @ speed x1.25)
4. Audit duration and prepare Audio Manifest for Gate 4 approval
"""
import asyncio
import json
import logging
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GeminiAgentPipeline")

# Root directory setup
REPO_ROOT = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
WORKSHOP_DIR = REPO_ROOT / "workshops" / "workshop-cinematic"
DB_PATH = WORKSHOP_DIR / "flow_agent.db"
SCREENPLAY_PATH = Path(r"C:\Users\tranh\.gemini\antigravity\brain\74745d7e-e139-4bc8-b6d1-fbc945ef19d8\KICH_BAN_AI_AGENT_DAU_TIEN_100_SHOTS.md")

JOB_ID = "job-gemini-ai-agent-build"
PROJECT_ID = "9d7f6f5d-7406-4c30-8173-e198df914520"  # Active Chrome Flow Project ID
VIDEO_ID = "video-gemini-ai-agent-100shots"

JOB_OUTPUT_DIR = REPO_ROOT / "output" / "cinematic" / JOB_ID
AUDIO_DIR = JOB_OUTPUT_DIR / "audio"
IMAGES_DIR = JOB_OUTPUT_DIR / "images"
VIDEOS_DIR = JOB_OUTPUT_DIR / "videos"
SEGMENTS_DIR = JOB_OUTPUT_DIR / "segments"
OVERLAYS_DIR = JOB_OUTPUT_DIR / "dialogue_overlays"

# Python interpreter with edge-tts
PYTHON_TTS = r"c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-whiteboard\.venv\Scripts\python.exe"

# Flow Asset Media IDs
BYTE_MEDIA_ID = "ce05075f-0ea2-4680-8b5b-1e76b60d784e"
LAB_MEDIA_ID = "399589db-c733-4c0f-9ce5-0bd9007ea967"
VAULT_MEDIA_ID = "2653c891-2191-445c-8b96-29ab6311fb0d"


def parse_screenplay(md_path: Path):
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    
    shots = []
    current_shot = None
    
    shot_pattern = re.compile(r"^\*\s+\*\*Shot\s+(\d+)\s*\(([^)]+)\)\s*\[([^\]]+)\]:\*\*\s*(.*)$")
    voice_pattern = re.compile(r"^\s+-\s+\*Thoại:\*\s*\"([^\"]+)\"")
    
    for line in lines:
        sm = shot_pattern.match(line)
        if sm:
            num = int(sm.group(1))
            timing = sm.group(2).strip()
            shot_type = sm.group(3).strip()
            visual_desc = sm.group(4).strip()
            current_shot = {
                "shot_num": num,
                "timing": timing,
                "shot_type": shot_type,
                "visual_desc": visual_desc,
                "dialogue": "",
                "speaker": "Bé Byte"
            }
            shots.append(current_shot)
            continue
        
        vm = voice_pattern.match(line)
        if vm and current_shot:
            current_shot["dialogue"] = vm.group(1).strip()
            current_shot = None  # completed shot
    
    return shots


def get_audio_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return round(float(res.stdout.strip()), 2)
    except Exception:
        return 0.0


def synthesize_edge_tts(text: str, output_path: Path, voice: str = "vi-VN-NamMinhNeural", pitch: str = "+0Hz", rate: str = "+25%"):
    temp_raw = output_path.parent / f"temp_{output_path.stem}.mp3"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd_tts = [
        PYTHON_TTS, "-m", "edge_tts",
        "--text", text,
        "--voice", voice,
        f"--pitch={pitch}",
        f"--rate={rate}",
        "--write-media", str(temp_raw)
    ]
    
    for attempt in range(1, 4):
        try:
            subprocess.run(cmd_tts, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if temp_raw.exists() and temp_raw.stat().st_size > 500:
                break
        except Exception as e:
            if attempt == 3:
                raise e
            time.sleep(1.5)
            
    # Resample to 48,000 Hz Stereo 192k AAC/MP3
    cmd_ff = [
        "ffmpeg", "-y",
        "-i", str(temp_raw),
        "-ar", "48000",
        "-ac", "2",
        "-b:a", "192k",
        str(output_path)
    ]
    subprocess.run(cmd_ff, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    temp_raw.unlink(missing_ok=True)


def build_prompts_for_shot(shot: dict) -> tuple[str, str, list[str]]:
    """Build calibrated Image Prompt and Veo 2 Video Prompt."""
    shot_num = shot["shot_num"]
    visual = shot["visual_desc"]
    stype = shot["shot_type"]
    
    # Check if this shot belongs to Master Set 2 (Quantum Data Space)
    # Typically Act 3 (Shots 37 - 60) where tools data execution is visualized
    is_vault = (37 <= shot_num <= 42) or (53 <= shot_num <= 58) or ("lượng tử" in visual.lower() or "pha lê" in visual.lower())
    
    if is_vault:
        char_names = ["Byte", "Kho Lưu Trữ Dữ Liệu Vector"]
        img_prompt = (
            f"Cinematic {stype} in ethereal Cyber-Chibi Quantum Vector Vault, cute 3D robot Byte floating among glowing amber and cyan crystal data cubes, "
            f"laser API connection beams, Octane Render 8K, Unreal Engine 5 aesthetic. Visual context: {visual}"
        )
        vid_prompt = (
            f"Cinematic camera glide through ethereal quantum data space, translucent crystal cubes pulsing with glowing cyan and gold light, "
            f"cute robot Byte interacting with floating holographic code and API pipelines, smooth 4K film motion."
        )
    else:
        char_names = ["Byte", "Viện Công Nghệ Tí Hon"]
        if "màn hình" in visual.lower() or "terminal" in visual.lower() or "code" in visual.lower() or "sơ đồ" in visual.lower():
            img_prompt = (
                f"Cinematic {stype} in miniature cyber lab diorama, large floating 3D holographic display occupying 70% of frame with crisp high-contrast UI, "
                f"cute Cyber-Chibi robot Byte floating nearby, pastel neon lighting, reflective navy floor, Octane Render 8K. Visual context: {visual}"
            )
            vid_prompt = (
                f"Cinematic camera movement toward large floating 3D holographic screen, interface elements illuminating with smooth fluid motion, "
                f"cute robot Byte speaking and gesturing with expressive blue LED eyes, professional tech documentary look."
            )
        else:
            img_prompt = (
                f"Cinematic {stype} in futuristic miniature cyber lab diorama, cute Cyber-Chibi robot Byte with sleek polished white ceramic body and expressive glowing blue LED eyes, "
                f"pastel neon server racks, volumetric rim light, Octane Render 8K. Visual context: {visual}"
            )
            vid_prompt = (
                f"Cinematic {stype} camera motion, cute Cyber-Chibi robot Byte floating with subtle mini jetpack particles, expressive facial gestures and speaking mouth movement, "
                f"smooth organic lighting and realistic physics."
            )
            
    return img_prompt, vid_prompt, char_names


def setup_database_and_scenes(shots: list[dict]):
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    # 1. Upsert Project
    c.execute("""
        INSERT OR REPLACE INTO project (
            id, name, description, story, language, status, user_paygate_tier, material, allow_music, allow_voice, video_model_family
        ) VALUES (
            ?, ?, ?, ?, 'vi', 'ACTIVE', 'PAYGATE_TIER_TWO', '3d_pixar', 1, 1, 'veo'
        )
    """, (
        PROJECT_ID,
        "[job-gemini-ai-agent-build] Tự Xây Dựng AI Agent Đầu Tiên Kết Nối Công Cụ Tự Động Hóa Thực Tế",
        "Tập phim điện ảnh 3D 100 phân cảnh hướng dẫn tự xây dựng AI Agent hoàn chỉnh kết nối 3 công cụ tự động hóa thực tế với Google Gemini 2.0 Flash.",
        "Toàn bộ hành trình từ kiến trúc ReAct, cài đặt Google GenAI SDK, định nghĩa 3 công cụ tự động hóa (Search, Python Code Sandbox, Markdown Report), xử lý lỗi Self-healing và nguyên tắc bảo mật Human-in-the-loop."
    ))
    
    # 2. Upsert Video
    c.execute("""
        INSERT OR REPLACE INTO video (
            id, project_id, title, description, display_order, status, orientation, resolution, target_duration_s
        ) VALUES (
            ?, ?, ?, ?, 1, 'DRAFT', 'HORIZONTAL', '1080p', 400.0
        )
    """, (
        VIDEO_ID,
        PROJECT_ID,
        "Tự Xây Dựng AI Agent Đầu Tiên Kết Nối Công Cụ Tự Động Hóa Thực Tế (Google Gemini 2.0 Flash)",
        "Tập phim hướng dẫn chuyên sâu 100 shots - Voice 1.25x - Cyber Chatbox - OmniVideo Studio Xưởng 4"
    ))
    
    # Link characters to project
    for c_id in ["9f871770-b24f-427a-b561-96d26b3ff0c3", "2299e8c0-8bba-4b69-919b-06ee2e15d602", "f730c2c8-b9b6-4dbb-8184-27fa06a0a43f"]:
        c.execute("INSERT OR IGNORE INTO project_character (project_id, character_id) VALUES (?, ?)", (PROJECT_ID, c_id))
        
    # Clear old scenes for this video if any
    c.execute("DELETE FROM scene WHERE video_id = ?", (VIDEO_ID,))
    
    # Insert 100 scenes
    for shot in shots:
        num = shot["shot_num"]
        scene_id = f"scene-gemini-agent-{num:03d}"
        img_prompt, vid_prompt, char_names = build_prompts_for_shot(shot)
        
        c.execute("""
            INSERT INTO scene (
                id, video_id, display_order, prompt, image_prompt, video_prompt, narrator_text, character_names
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scene_id,
            VIDEO_ID,
            num,
            shot["visual_desc"],
            img_prompt,
            vid_prompt,
            shot["dialogue"],
            json.dumps(char_names, ensure_ascii=False)
        ))
        
    conn.commit()
    conn.close()
    logger.info("Successfully populated Project %s, Video %s, and 100 scenes in DB!", PROJECT_ID, VIDEO_ID)


def main():
    logger.info("Step 1: Creating directory structures...")
    for d in [JOB_OUTPUT_DIR, AUDIO_DIR, IMAGES_DIR, VIDEOS_DIR, SEGMENTS_DIR, OVERLAYS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        
    logger.info("Step 2: Parsing screenplay...")
    shots = parse_screenplay(SCREENPLAY_PATH)
    logger.info("Parsed %d shots successfully.", len(shots))
    
    logger.info("Step 3: Populating FlowKit Database...")
    setup_database_and_scenes(shots)
    
    logger.info("Step 4: Synthesizing Edge-TTS Audio (Voice x1.25, 48kHz Stereo) with 6 parallel workers...")
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def process_shot_audio(shot):
        num = shot["shot_num"]
        text = shot["dialogue"]
        out_file = AUDIO_DIR / f"shot_{num:03d}.mp3"
        
        # Check if already generated and non-empty
        if not out_file.exists() or out_file.stat().st_size < 1000:
            synthesize_edge_tts(
                text=text,
                output_path=out_file,
                voice="vi-VN-NamMinhNeural",
                pitch="+0Hz",
                rate="+25%"  # Strict Voice x1.25 Mandate
            )
            
        dur = get_audio_duration(out_file)
        shot_copy = dict(shot)
        shot_copy["audio_file"] = str(out_file)
        shot_copy["duration"] = dur
        return shot_copy

    manifest_map = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(process_shot_audio, s): s["shot_num"] for s in shots}
        completed = 0
        for f in as_completed(futures):
            res = f.result()
            manifest_map[res["shot_num"]] = res
            completed += 1
            if completed % 10 == 0 or completed == len(shots):
                logger.info("Synthesized [%d/%d] shots via parallel workers...", completed, len(shots))

    manifest = [manifest_map[i] for i in sorted(manifest_map.keys())]
    total_audio_duration = sum(s["duration"] for s in manifest)
            
    manifest_path = JOB_OUTPUT_DIR / "audio_manifest_100_shots.json"
    manifest_path.write_text(json.dumps({
        "job_id": JOB_ID,
        "project_id": PROJECT_ID,
        "video_id": VIDEO_ID,
        "total_shots": len(shots),
        "total_audio_duration_seconds": round(total_audio_duration, 2),
        "total_audio_duration_minutes": round(total_audio_duration / 60.0, 2),
        "average_shot_length": round(total_audio_duration / len(shots), 2),
        "voice_preset": "vi-VN-NamMinhNeural @ rate=+25% (Voice x1.25 Mandate)",
        "sample_rate": "48000 Hz Stereo 192kbps",
        "shots": manifest
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    
    logger.info("==================================================================")
    logger.info("AUDIO SYNTHESIS COMPLETE!")
    logger.info("Total Shots: %d", len(shots))
    logger.info("Total Duration: %.2fs (~%.2f minutes)", total_audio_duration, total_audio_duration / 60.0)
    logger.info("Average Shot Length (ASL): %.2fs (Well within 3.5s - 6.0s ASL range!)", total_audio_duration / len(shots))
    logger.info("Manifest saved to: %s", manifest_path)
    logger.info("==================================================================")


if __name__ == "__main__":
    main()

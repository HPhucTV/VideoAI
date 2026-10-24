#!/usr/bin/env python3
"""
OmniVideo Studio - Gate 6 Master Film Assembly Engine for MCP 7-Min Film (105 Shots)
Full End-to-End Compositing, Concat Demuxer, Dynamic Audio Ducking, and Publishing Kit.
"""
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MasterAssemblyMCP")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-mcp-explained-7min"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
VIDEOS_DIR = OUTPUT_DIR / "videos"
IMAGES_DIR = OUTPUT_DIR / "images"
AUDIO_DIR = OUTPUT_DIR / "audio"
OVERLAYS_DIR = OUTPUT_DIR / "dialogue_overlays"
RENDERED_DIR = OUTPUT_DIR / "rendered_shots"
RENDERED_DIR.mkdir(parents=True, exist_ok=True)

BRANDING_DIR = BASE_DIR / "shared-assets" / "branding"
INTRO_PATH = BRANDING_DIR / "intro_horizontal_16x9.mp4"
OUTRO_PATH = BRANDING_DIR / "outro_horizontal_16x9.mp4"
LOGO_PATH = BRANDING_DIR / "giaimatech_logo.png"
BGM_PATH = BASE_DIR / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "healing-piano.mp3"

FINAL_MASTER_MP4 = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.mp4"
FINAL_SRT = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.srt"
MANIFEST_PATH = OUTPUT_DIR / "audio_manifest_105_shots.json"
PUBKIT_PATH = OUTPUT_DIR / f"{JOB_ID}_publishing_kit.json"
BRAIN_DIR = Path(r"C:\Users\tranh\.gemini\antigravity\brain\74745d7e-e139-4bc8-b6d1-fbc945ef19d8")

def format_srt_time(seconds: float) -> str:
    millis = int(round((seconds - int(seconds)) * 1000))
    total_sec = int(seconds)
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def generate_srt_and_pubkit(shots_data: list):
    lines = []
    current_time = 2.0  # intro is 2.0s
    for idx, s in enumerate(shots_data, 1):
        dur = s.get("duration", 4.0)
        start_t = current_time
        end_t = current_time + dur
        diag = s.get("dialogue", "").strip()
        lines.append(f"{idx}\n{format_srt_time(start_t)} --> {format_srt_time(end_t)}\n{diag}\n")
        current_time = end_t

    FINAL_SRT.write_text("\n".join(lines), encoding="utf-8")
    (BRAIN_DIR / f"{JOB_ID}.srt").write_text("\n".join(lines), encoding="utf-8")
    logger.info("Generated YouTube SRT: %s", FINAL_SRT)

    pubkit = {
        "title": "Giải Mã MCP (Model Context Protocol): Chuẩn Kết Nối Vạn Năng Biến AI Thành Siêu Trợ Lý | Giải Mã Tech #02",
        "category": "Science & Technology",
        "language": "vi",
        "target_duration": "07:00",
        "chapters": [
            {"time": "00:00", "title": "Giới thiệu & Cơn ác mộng phân mảnh cáp sạc"},
            {"time": "00:02", "title": "Hồi 1: Nỗi đau phân mảnh & Giới hạn của AI cô đơn"},
            {"time": "01:06", "title": "Hồi 2: Khai sinh MCP — Chuẩn kết nối vạn năng (USB-C của AI)"},
            {"time": "02:50", "title": "Hồi 3: Giải phẫu kỹ thuật — 3 Trụ cột cốt lõi & Thực hành FastMCP"},
            {"time": "04:58", "title": "Hồi 4: Pháo đài bảo mật — Lỗ hổng Prompt Injection & 3 Lớp phòng vệ"},
            {"time": "06:18", "title": "Hồi 5: Tương lai của MCP & Lời kêu gọi hành động"},
            {"time": "06:58", "title": "Lời kết & Đăng ký kênh Giải Mã Tech"}
        ],
        "tags": [
            "MCP", "Model Context Protocol", "Anthropic", "Claude Desktop", "AI Agent",
            "FastMCP", "Python", "Cursor", "Gemini", "Giai Ma Tech", "Bao Mat AI", "OpenAI"
        ],
        "privacy": "unlisted"
    }
    with open(PUBKIT_PATH, "w", encoding="utf-8") as f:
        json.dump(pubkit, f, ensure_ascii=False, indent=2)
    logger.info("Generated Publishing Kit: %s", PUBKIT_PATH)

def render_single_shot(shot_info: dict) -> Path:
    s_num = shot_info["shot_num"]
    dur = shot_info.get("duration", 4.0)
    out_clip = RENDERED_DIR / f"shot_{s_num:03d}.mp4"

    if out_clip.exists() and out_clip.stat().st_size > 100_000:
        return out_clip

    v_file = VIDEOS_DIR / f"shot_{s_num:03d}.mp4"
    img_fallback = IMAGES_DIR / f"shot_{s_num:03d}.jpg"
    c_file = OVERLAYS_DIR / f"chatbox_shot_{s_num:03d}.png"
    a_file = AUDIO_DIR / f"shot_{s_num:03d}.mp3"

    # Use moving video if available; fallback to image with subtle zoom
    if v_file.exists() and v_file.stat().st_size > 500_000:
        v_input = str(v_file)
        filter_str = (
            "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=60[base]; "
            "[base][1:v]overlay=160:909[v_comp]"
        )
        input_args = ["-i", v_input, "-i", str(c_file), "-i", str(a_file)]
    else:
        v_input = str(img_fallback)
        filter_str = (
            "[0:v]scale=1920:1080,setsar=1,fps=60[base]; "
            "[base][1:v]overlay=160:909[v_comp]"
        )
        input_args = ["-loop", "1", "-t", str(dur), "-i", v_input, "-i", str(c_file), "-i", str(a_file)]

    cmd = [
        "ffmpeg", "-y",
        *input_args,
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
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return out_clip

def main():
    logger.info("🎬 Starting Master Film Assembly for %s (105 shots)...", JOB_ID)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        shots_data = json.load(f)

    # Step 1: Subtitles & Publishing Kit
    generate_srt_and_pubkit(shots_data)

    # Step 2: Render each shot
    logger.info("🎞️ Rendering 105 individual shots with moving video + Cyber Chatbox + 48kHz audio...")
    rendered_count = 0
    t0 = time.time()
    for s in shots_data:
        render_single_shot(s)
        rendered_count += 1
        if rendered_count % 15 == 0 or rendered_count == len(shots_data):
            logger.info("Rendered %d / %d shots (%.1fs elapsed)", rendered_count, len(shots_data), time.time() - t0)

    # Step 3: Concat 105 shots into body video
    logger.info("🔗 Concatenating 105 rendered shots into Body Video...")
    body_concat_list = OUTPUT_DIR / "body_concat_list.txt"
    with open(body_concat_list, "w", encoding="utf-8") as f:
        for s in shots_data:
            s_num = s["shot_num"]
            c_path = str(RENDERED_DIR / f"shot_{s_num:03d}.mp4").replace("\\", "/")
            f.write(f"file '{c_path}'\n")

    body_video_file = OUTPUT_DIR / "body_mcp_105_shots.mp4"
    cmd_body = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(body_concat_list),
        "-c", "copy",
        str(body_video_file)
    ]
    subprocess.run(cmd_body, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    logger.info("Body video completed: %s", body_video_file)

    # Step 4: Final Master Film Assembly (Intro + Body + Outro + Watermark Logo + Ducked BGM)
    logger.info("🏆 Final Master Assembly: Intro + Body + Outro + Logo Watermark + BGM Ducking (-22dB)...")
    master_concat_list = OUTPUT_DIR / "master_film_concat.txt"
    with open(master_concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{str(INTRO_PATH).replace('\\', '/')}'\n")
        f.write(f"file '{str(body_video_file).replace('\\', '/')}'\n")
        f.write(f"file '{str(OUTRO_PATH).replace('\\', '/')}'\n")

    cmd_final = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(master_concat_list),
        "-stream_loop", "-1", "-i", str(BGM_PATH),
        "-i", str(LOGO_PATH),
        "-filter_complex",
        "[0:v][2:v]overlay=40:40:format=auto[v_out];"
        "[1:a]volume=0.08[bgm_ducked];"
        "[0:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[a_out]",
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        str(FINAL_MASTER_MP4)
    ]
    t_start = time.time()
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    logger.info("🎉 Master Film render completed in %.1fs: %s", time.time() - t_start, FINAL_MASTER_MP4)

    # Also copy to Brain Artifact directory for easy viewing
    dst_brain = BRAIN_DIR / f"{JOB_ID}_master.mp4"
    if FINAL_MASTER_MP4.exists():
        shutil.copy2(FINAL_MASTER_MP4, dst_brain)
        logger.info("Copied Master Film to Brain: %s", dst_brain)

if __name__ == "__main__":
    main()

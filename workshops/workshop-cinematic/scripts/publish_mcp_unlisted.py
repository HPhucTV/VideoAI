#!/usr/bin/env python3
"""
OmniVideo Studio - Gate 7 YouTube Unlisted Auto-Publisher
Uploads Master Film MP4, sets 3D High-CTR Thumbnail, attaches Vietnamese SRT,
and keeps privacy strictly as 'unlisted'.
"""
import json
import logging
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Gate7_YouTubePublisher")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "workshops" / "workshop-cinematic"))

from scripts.youtube_publisher import upload_unlisted_video

JOB_ID = "job-mcp-explained-7min"
MASTER_MP4 = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.mp4"
THUMBNAIL = BASE_DIR / "output" / "cinematic" / JOB_ID / f"{JOB_ID}_thumb_3d.jpg"
SRT_PATH = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.srt"
PUBKIT_PATH = BASE_DIR / "output" / "cinematic" / JOB_ID / f"{JOB_ID}_publishing_kit.json"

def main():
    logger.info("🚀 Starting Gate 7: Upload Unlisted Master Film to YouTube Channel 'Giai Ma Tech'...")

    with open(PUBKIT_PATH, "r", encoding="utf-8") as f:
        pubkit = json.load(f)

    title = pubkit.get("title")
    tags = pubkit.get("tags", [])
    chapters = pubkit.get("chapters", [])

    desc_lines = [
        "Giải Mã MCP (Model Context Protocol): Chuẩn Kết Nối Vạn Năng Biến AI Thành Siêu Trợ Lý.",
        "Phim hoạt hình 3D chuẩn điện ảnh phân tích chi tiết chuẩn kết nối vạn năng MCP của Anthropic, kiến trúc Client-Host-Server và giải pháp bảo mật dữ liệu cho AI Agent thời đại tự chủ.",
        "",
        "⏱️ NỘI DUNG / TIMESTAMPS:"
    ]
    for ch in chapters:
        desc_lines.append(f"{ch['time']} - {ch['title']}")

    desc_lines.extend([
        "",
        "🔔 Đăng ký kênh Giải Mã Tech để khám phá các tập phim điện ảnh công nghệ tiếp theo!",
        "#MCP #ModelContextProtocol #Anthropic #AIAgent #FastMCP #ClaudeDesktop #GiaiMaTech #AI #Python"
    ])
    description = "\n".join(desc_lines)

    result = upload_unlisted_video(
        channel_name="Giai Ma Tech",
        video_path=MASTER_MP4,
        title=title,
        description=description,
        tags=tags,
        thumbnail_path=THUMBNAIL,
        srt_path=SRT_PATH,
        privacy_status="unlisted",
        category_id="28"  # Science & Technology
    )

    logger.info("🎉 SUCCESSFUL GATE 7 PUBLISH:")
    logger.info("Video URL: %s", result.get("url"))
    logger.info("Video ID: %s", result.get("video_id"))
    logger.info("Privacy: %s", result.get("privacy"))

    out_json = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}_youtube_result.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Copy to Brain
    brain_dir = Path(r"C:\Users\tranh\.gemini\antigravity\brain\74745d7e-e139-4bc8-b6d1-fbc945ef19d8")
    shutil_copy = brain_dir / f"{JOB_ID}_youtube_result.json"
    with open(shutil_copy, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("YOUTUBE_PUBLISH_RESULT:", json.dumps(result))

if __name__ == "__main__":
    main()

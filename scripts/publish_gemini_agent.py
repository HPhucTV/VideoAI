"""
Publish job-gemini-ai-agent-build.mp4 to YouTube channel 'Giai Ma Tech'
Mode: PUBLIC (per user explicit mandate)
Includes: Custom 3D Thumbnail, Chapters/Timestamps, and Vietnamese Subtitles (SRT).
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# Configure utf-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("publish_gemini_agent")

from scripts.youtube_publisher import upload_unlisted_video
from scripts.master_assembly_engine import generate_srt_file


def main():
    root = Path(__file__).resolve().parent.parent
    job_dir = root / "output" / "cinematic"
    video_path = job_dir / "job-gemini-ai-agent-build.mp4"
    thumb_path = job_dir / "job-gemini-ai-agent-build_thumb_3d.jpg"
    manifest_path = job_dir / "job-gemini-ai-agent-build" / "audio_manifest_100_shots.json"
    srt_path = job_dir / "job-gemini-ai-agent-build.srt"

    logger.info("Checking files...")
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not thumb_path.exists():
        raise FileNotFoundError(f"Thumbnail file not found: {thumb_path}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    # 1. Generate SRT subtitle file if not exists
    if not srt_path.exists():
        logger.info("Generating SRT subtitle file from audio manifest...")
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        generate_srt_file(manifest_data["shots"], srt_path, intro_offset=2.0)
    logger.info("SRT file ready: %s (%d bytes)", srt_path, srt_path.stat().st_size)

    # 2. Prepare Title, Description, and Tags
    title = "Tự Xây Dựng AI Agent Đầu Tiên Bằng Python & Gemini 2.0 Flash | Giải Mã Tech"

    description = """🎬 Tự Xây Dựng AI Agent Đầu Tiên Bằng Python & Gemini 2.0 Flash | Giải Mã Tech

Bạn muốn sở hữu một AI không chỉ dừng lại ở việc trả lời lý thuyết mà thực sự biết "làm việc" — tự tìm kiếm dữ liệu, tự tính toán số liệu và tự động xuất báo cáo? 

Trong video này, Bé Byte cùng Giải Mã Tech sẽ bóc tách toàn bộ kiến trúc 3 trụ cột của một AI Agent thực chiến, hướng dẫn bạn tự tay viết từng dòng code Python kết nối mô hình Google Gemini 2.0 Flash với tính năng Function Calling cực kỳ mạnh mẽ.

━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ NỘI DUNG TỪNG PHẦN (TIMESTAMPS):
00:00 - Mở đầu: Chatbot thông thường vs AI Agent hành động thực tế
00:53 - Kiến trúc 3 trụ cột cốt lõi & Cơ chế Vòng lặp ReAct
02:21 - Thực chiến code Python: Kết nối Gemini 2.0 Flash SDK
04:28 - Demo trực tiếp: Tự research dữ liệu, tính toán CAGR & tự sửa lỗi
05:55 - Rào chắn an toàn khi triển khai: Sandbox & Human-in-the-loop
06:23 - Tổng kết, Mã nguồn GitHub & Lời chào kết

━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 CÁC TÀI NGUYÊN TRONG VIDEO:
- Model: Google Gemini 2.0 Flash (Function Calling / Tool Calling)
- Ngôn ngữ: Python 3.12 thuần túy
- Studio sản xuất: OmniVideo Studio (Xưởng 4: Phim Điện Ảnh 3D & AI Agent Bé Byte)

💡 Đừng quên bấm Like, Chia sẻ và ĐĂNG KÝ KÊNH @giaimatech-s8t để đón xem những tập phim công nghệ 3D đột phá tiếp theo!

#AIAgent #Gemini2Flash #GoogleGemini #Python #LapTrinhAI #GiaiMaTech #FunctionCalling #TuDongHoa #AI2026"""

    tags = [
        "AI Agent",
        "Gemini 2.0 Flash",
        "Google Gemini",
        "Python AI",
        "Lập trình AI",
        "Function Calling",
        "ReAct Loop",
        "Giải Mã Tech",
        "Tự động hóa",
        "Bé Byte",
        "OmniVideo Studio",
        "Machine Learning",
        "Học máy",
        "Coding Tutorial",
        "AI 2026",
    ]

    logger.info("Uploading video to YouTube (Channel: Giai Ma Tech, Mode: PUBLIC)...")
    logger.info("Video path: %s (%.1f MB)", video_path, video_path.stat().st_size / (1024 * 1024))
    logger.info("Title: %s", title)

    result = upload_unlisted_video(
        channel_name="Giai Ma Tech",
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        thumbnail_path=thumb_path,
        srt_path=srt_path,
        privacy_status="public",
        category_id="28",
    )

    result_file = job_dir / "job-gemini-ai-agent-build_publishing_result.json"
    result_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Publishing complete! Result saved to %s", result_file)
    logger.info("YouTube Video URL: %s", result.get("url"))


if __name__ == "__main__":
    main()

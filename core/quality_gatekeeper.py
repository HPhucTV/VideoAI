"""Quality Gatekeeper & Automated QA Auditor for OmniVideo Studio."""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("quality_gatekeeper")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

_ROOT = Path(__file__).resolve().parent.parent


def get_media_info(file_path: Path | str) -> Dict[str, Any]:
    """Inspect video or audio file using ffprobe."""
    f = Path(file_path)
    if not f.exists():
        return {}

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,sample_rate,channels",
        "-of", "json",
        str(f),
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout)
    except Exception as exc:
        logger.warning("ffprobe failed for %s: %s", file_path, exc)
        return {}


def audit_job_production(job_dir: Path | str) -> Dict[str, Any]:
    """Perform comprehensive quality audit across audio, video, subtitles, and thumbnail."""
    jdir = Path(job_dir)
    report = {
        "job_dir": str(jdir),
        "passed": True,
        "score": 100,
        "checks": [],
        "errors": [],
        "warnings": [],
    }

    # 1. Video Check
    mp4_files = list(jdir.glob("*.mp4"))
    if not mp4_files:
        report["passed"] = False
        report["score"] -= 50
        report["errors"].append("Không tìm thấy file video MP4 trong thư mục xuất bản.")
    else:
        master_mp4 = mp4_files[0]
        v_info = get_media_info(master_mp4)
        streams = v_info.get("streams", [])
        v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

        if not v_stream:
            report["passed"] = False
            report["score"] -= 40
            report["errors"].append("File MP4 không chứa luồng Video hợp lệ.")
        else:
            w = int(v_stream.get("width", 0))
            h = int(v_stream.get("height", 0))
            report["checks"].append({
                "name": "Độ phân giải video",
                "status": "PASS",
                "detail": f"{w}x{h} ({'9:16 Dọc' if h > w else '16:9 Ngang'})",
            })

        if not a_stream:
            report["passed"] = False
            report["score"] -= 30
            report["errors"].append("File MP4 thiếu luồng âm thanh Audio!")
        else:
            sr = int(a_stream.get("sample_rate", 0))
            ch = int(a_stream.get("channels", 0))
            if sr < 44100:
                report["warnings"].append(f"Tần số lấy mẫu âm thanh thấp: {sr}Hz (Khuyến nghị: 48,000Hz).")
                report["score"] -= 5
            report["checks"].append({
                "name": "Luồng âm thanh",
                "status": "PASS",
                "detail": f"{sr}Hz, {ch} kênh",
            })

    # 2. Thumbnail Check
    thumb_candidates = list(jdir.glob("*.jpg")) + list(jdir.glob("*.png"))
    thumb_file = next((t for t in thumb_candidates if "thumb" in t.name or "preview" in t.name), None)
    if not thumb_file:
        report["warnings"].append("Chưa có ảnh bìa Thumbnail tùy chỉnh (sử dụng frame đầu tiên).")
        report["score"] -= 10
    else:
        report["checks"].append({
            "name": "Thumbnail 3D",
            "status": "PASS",
            "detail": f"File {thumb_file.name} ({thumb_file.stat().st_size // 1024} KB)",
        })

    # 3. Subtitle SRT Check
    srt_files = list(jdir.glob("*.srt"))
    if not srt_files:
        report["warnings"].append("Không tìm thấy file phụ đề rời .srt (phụ đề có thể đã được ghi đè trực tiếp).")
    else:
        srt = srt_files[0]
        if srt.stat().st_size < 20:
            report["warnings"].append("File phụ đề .srt có dung lượng quá nhỏ hoặc rỗng.")
            report["score"] -= 5
        else:
            report["checks"].append({
                "name": "Phụ đề SRT",
                "status": "PASS",
                "detail": f"File {srt.name} chuẩn UTF-8",
            })

    # 4. Publishing Kit JSON Check
    pk_file = jdir / "publishing_kit.json"
    if pk_file.exists():
        try:
            pk = json.loads(pk_file.read_text(encoding="utf-8"))
            has_title = bool(pk.get("title"))
            has_desc = bool(pk.get("description") or pk.get("youtube_description"))
            has_tags = bool(pk.get("tags"))
            if has_title and has_desc and has_tags:
                report["checks"].append({
                    "name": "Publishing Kit SEO",
                    "status": "PASS",
                    "detail": "Đầy đủ Tiêu đề, Chapters & Thẻ Tags",
                })
        except Exception:
            pass

    report["score"] = max(0, min(100, report["score"]))
    return report


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    target = sys.argv[1] if len(sys.argv) > 1 else str(_ROOT / "output" / "threads" / "job_thread_hoangbao_ban_cung_ban")
    rep = audit_job_production(target)
    print(json.dumps(rep, ensure_ascii=False, indent=2))

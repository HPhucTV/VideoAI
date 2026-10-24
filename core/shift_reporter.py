"""Shift Briefing Reporter: Generates executive studio reports for Omni-Commander AI."""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

_ROOT = Path(__file__).resolve().parent.parent
_OUTPUT_DIR = _ROOT / "output"


def generate_shift_report() -> Dict[str, Any]:
    """Analyze output directory and generate executive production report."""
    workshops = ["threads", "cinematic", "explainer", "whiteboard", "news"]
    total_videos = 0
    by_workshop: Dict[str, int] = {ws: 0 for ws in workshops}
    recent_videos: List[Dict[str, Any]] = []
    published_videos: List[Dict[str, Any]] = []
    total_bytes = 0

    now_ts = time.time()
    one_day_sec = 24 * 3600

    for ws in workshops:
        ws_dir = _OUTPUT_DIR / ws
        if not ws_dir.exists():
            continue

        for mp4 in ws_dir.glob("**/*.mp4"):
            total_videos += 1
            by_workshop[ws] = by_workshop.get(ws, 0) + 1
            f_stat = mp4.stat()
            total_bytes += f_stat.st_size

            # Check publishing kit
            parent_dir = mp4.parent
            pk_file = parent_dir / "publishing_kit.json"
            status_file = parent_dir / "upload_status.json"

            yt_info = None
            if status_file.exists():
                try:
                    s_data = json.loads(status_file.read_text(encoding="utf-8"))
                    if s_data.get("status") == "completed" and s_data.get("url"):
                        yt_info = s_data
                except Exception:
                    pass

            item = {
                "name": mp4.name,
                "job_id": parent_dir.name,
                "workshop": ws,
                "size_mb": round(f_stat.st_size / (1024 * 1024), 1),
                "modified_at": datetime.fromtimestamp(f_stat.st_mtime, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "is_recent": (now_ts - f_stat.st_mtime) < one_day_sec,
                "youtube": yt_info,
            }

            if item["is_recent"]:
                recent_videos.append(item)
            if yt_info:
                published_videos.append(item)

    # Markdown Briefing Text
    md_lines = [
        "# 📋 OMNI-COMMANDER: BÁO CÁO TỔNG KẾT CA TRỰC STUDIO",
        f"**Thời gian xuất báo cáo:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "",
        "### 📊 1. Thống Kê Tổng Quan",
        f"- **Tổng số video trong kho:** `{total_videos}` video",
        f"- **Video sản xuất trong 24h qua:** `{len(recent_videos)}` video",
        f"- **Video đã xuất bản lên YouTube:** `{len(published_videos)}` video",
        f"- **Tổng dung lượng lưu trữ:** `{round(total_bytes / (1024 * 1024 * 1024), 2)} GB`",
        "",
        "### 🏭 2. Phân Bổ Theo Phân Xưởng",
    ]

    for ws, count in by_workshop.items():
        if count > 0:
            md_lines.append(f"- **{ws.upper()}:** `{count}` video")

    if published_videos:
        md_lines.append("\n### 🚀 3. Video Đã Lên Kênh YouTube")
        for pub in published_videos:
            yt = pub["youtube"]
            md_lines.append(f"- **{pub['job_id']}** ({pub['workshop']}): [{yt.get('url')}]({yt.get('url')}) • Chế độ: `{yt.get('privacy', 'unlisted').upper()}`")

    briefing_md = "\n".join(md_lines)

    return {
        "timestamp": datetime.now().isoformat(),
        "total_videos": total_videos,
        "recent_count": len(recent_videos),
        "published_count": len(published_videos),
        "total_gb": round(total_bytes / (1024 * 1024 * 1024), 2),
        "by_workshop": by_workshop,
        "recent_videos": recent_videos,
        "published_videos": published_videos,
        "briefing_markdown": briefing_md,
    }


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    report = generate_shift_report()
    print(report["briefing_markdown"])

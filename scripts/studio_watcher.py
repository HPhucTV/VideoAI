"""
OmniVideo Studio - Autonomous Pipeline Watcher
Tự động giám sát toàn bộ tư liệu sinh ra trong output/cinematic (Audio, Storyboard, Videos, Subtitles, Master Film)
và stream log trực tiếp thời gian thực lên Dashboard http://localhost:8100/ mà không cần sự can thiệp thủ công từ agent.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
CINEMATIC_DIR = ROOT_DIR / "output" / "cinematic"
UPDATE_URL = "http://127.0.0.1:8100/api/studio/progress/job-chatbot-vs-agent-chibi/update"
COMPLETE_URL = "http://127.0.0.1:8100/api/studio/progress/job-chatbot-vs-agent-chibi/complete"


def post_api(url: str, payload: dict):
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            pass
    except Exception:
        pass


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def main():
    print("[OmniVideo Watcher] Bắt đầu giám sát tự động tiến trình pipeline...", flush=True)
    known_videos = set()
    master_completed = False

    vid_dir = CINEMATIC_DIR / "videos"

    # Seed and sync current videos immediately on startup
    if vid_dir.exists():
        initial_vids = sorted([f.name for f in vid_dir.glob("*.mp4")])
        for v in initial_vids:
            known_videos.add(v)
        
        total_vids = len(known_videos)
        pct = min(98, 85 + (total_vids * 2))
        post_api(
            UPDATE_URL,
            {
                "progress": pct,
                "step_id": "gate_6",
                "step_detail": f"Veo 2 AI ({total_vids}/9 Clips - Đang xử lý)",
                "log_line": f"🎬 [CỔNG 6 ĐANG BẤM MÁY] Đã sinh {total_vids}/9 video clips Veo 2 ({', '.join(initial_vids)})",
            },
        )

    while True:
        try:
            time.sleep(2)

            # 1. Check for new video clips in output/cinematic/videos/
            if vid_dir.exists():
                current_vids = set(f.name for f in vid_dir.glob("*.mp4"))
                new_vids = current_vids - known_videos
                for nv in sorted(new_vids):
                    known_videos.add(nv)
                    vpath = vid_dir / nv
                    fsize = vpath.stat().st_size
                    total_vids = len(known_videos)
                    pct = min(98, 85 + (total_vids * 2))

                    post_api(
                        UPDATE_URL,
                        {
                            "progress": pct,
                            "step_id": "gate_6",
                            "step_detail": f"Veo 2 AI ({total_vids}/9 Clips - Vừa xong {nv})",
                            "log_line": f"🎬 [Veo 2 AI] Hoàn tất sinh clip: {nv} ({format_size(fsize)}) [{total_vids}/9 clips]",
                        },
                    )
                    print(f"[WATCHER] New video clip detected: {nv} ({format_size(fsize)})", flush=True)

            # 2. Check for Master Film Assembly completion
            if not master_completed:
                master_candidates = [
                    CINEMATIC_DIR / "master_film_chatbot_vs_agent_16x9.mp4",
                    CINEMATIC_DIR / "master_film.mp4",
                    CINEMATIC_DIR / "final_output.mp4",
                ]
                for mf in master_candidates:
                    if mf.exists() and mf.stat().st_size > 1024 * 1024:
                        master_completed = True
                        msize = format_size(mf.stat().st_size)
                        post_api(
                            UPDATE_URL,
                            {
                                "progress": 100,
                                "step_id": "gate_6",
                                "step_detail": f"Master Film Xuất Xưởng Thành Công ({msize})",
                                "log_line": f"🎉 [MASTER FILM HOÀN TẤT] Video điện ảnh {mf.name} ({msize}) đã xuất xưởng thành công 100%!",
                            },
                        )
                        post_api(
                            COMPLETE_URL,
                            {
                                "summary": f"Video điện ảnh 100% Veo 2 AI {mf.name} ({msize}) đã xuất xưởng thành công!",
                                "output_video_path": str(mf),
                            },
                        )
                        print(f"[WATCHER] 🎉 Master Film completed: {mf.name} ({msize})", flush=True)
                        break

        except Exception:
            pass


if __name__ == "__main__":
    main()

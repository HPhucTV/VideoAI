#!/usr/bin/env python3
"""
Continuous Background Sync Daemon for 104-Shot Cinematic Production (Cổng 6 - GEN V).
Continuously monitors flow_agent.db, downloads all completed Veo 2 videos,
and updates the production dashboard in real-time.
"""
import time
import sys
import os
import sqlite3
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = BASE_DIR / "workshops" / "workshop-cinematic" / "flow_agent.db"
JOB_ID = "job-ai-agent-giaimatech-10min"
VIDEO_ID = "92a3ff94-c592-4910-b2c2-facbb2754132"
AGENT_URL = "http://127.0.0.1:8100"

OUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID / "videos"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def update_dashboard(completed_count, processing_count, pending_count):
    pct = int(60 + (completed_count / 104) * 35)
    payload = {
        "progress": pct,
        "step_id": "gate_6",
        "step_detail": f"Đang sinh {completed_count}/104 video AI Veo 2 (GEN V)...",
        "log_line": f"GEN V Hoàn tất: {completed_count}/104 | Đang sinh: {processing_count} | Chờ: {pending_count}"
    }
    try:
        requests.post(f"{AGENT_URL}/api/studio/progress/{JOB_ID}/update", json=payload, timeout=3)
    except Exception:
        pass

def sync_once():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        SELECT type, status, count(*) 
        FROM request 
        WHERE type='GENERATE_VIDEO' 
        GROUP BY status
    """)
    stats = {row[0]: row[1] for row in c.fetchall()}
    completed = stats.get("COMPLETED", 0)
    processing = stats.get("PROCESSING", 0)
    pending = stats.get("PENDING", 0)
    
    c.execute("""
        SELECT display_order, horizontal_video_url 
        FROM scene 
        WHERE video_id=? AND horizontal_video_url IS NOT NULL AND horizontal_video_url != ''
        ORDER BY display_order
    """, (VIDEO_ID,))
    rows = c.fetchall()
    conn.close()

    new_downloads = 0
    for order, url in rows:
        dest = OUT_DIR / f"shot_{order:03d}.mp4"
        if not dest.exists() or dest.stat().st_size < 100000:
            try:
                r = requests.get(url, timeout=60)
                if r.status_code == 200 and len(r.content) > 100000:
                    dest.write_bytes(r.content)
                    print(f"[{time.strftime('%H:%M:%S')}] 📥 Đã tải Shot {order:03d} ({len(r.content):,} bytes)")
                    new_downloads += 1
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] ⚠️ Lỗi tải Shot {order:03d}: {e}")

    total_on_disk = len(list(OUT_DIR.glob("*.mp4")))
    update_dashboard(completed, processing, pending)
    return completed, processing, pending, total_on_disk, new_downloads

def main():
    print("=" * 65)
    print("🎬 AUTO SYNC & PROGRESS DAEMON (CỔNG 6 - GEN V VEO 2)")
    print("=" * 65)
    last_completed = -1
    
    while True:
        try:
            completed, processing, pending, on_disk, new_dl = sync_once()
            if completed != last_completed or new_dl > 0:
                print(f"[{time.strftime('%H:%M:%S')}] Tiến độ Veo 2: {completed}/104 xong | {processing} đang sinh | {pending} chờ | Trên ổ cứng: {on_disk} files")
                last_completed = completed
            
            if completed >= 104 and on_disk >= 104:
                print(f"[{time.strftime('%H:%M:%S')}] 🎉 TẤT CẢ 104/104 VIDEO AI ĐÃ HOÀN TẤT VÀ TẢI VỀ ĐỦ!")
                break
        except Exception as e:
            print(f"Lỗi vòng lặp sync: {e}")
            
        time.sleep(10)

if __name__ == "__main__":
    main()

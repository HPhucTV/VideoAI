#!/usr/bin/env python3
"""
OmniVideo Studio — Live Monitor & Sync for 104-Shot Cinematic Production (Cổng 5 & Cổng 6)
Tracks:
- Cổng 5: GENERATE_IMAGE (104 Google Flow Imagen 3 images)
- Cổng 6: GENERATE_VIDEO (104 Google Flow Veo 2 / Omni Flash videos)
Automatically downloads all assets locally and updates dashboard.
"""
import sys
import time
import requests
import sqlite3
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

AGENT_URL = "http://127.0.0.1:8100"
VIDEO_ID = "92a3ff94-c592-4910-b2c2-facbb2754132"
JOB_ID = "job-ai-agent-giaimatech-10min"

OUTPUT_DIR = Path("output/cinematic") / JOB_ID
IMAGES_DIR = OUTPUT_DIR / "images"
VIDEOS_DIR = OUTPUT_DIR / "videos"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def update_dashboard(progress: int, step_id: str, detail: str, log: str):
    try:
        payload = {
            "progress": progress,
            "step_id": step_id,
            "step_detail": detail,
            "log_line": log
        }
        requests.post(f"{AGENT_URL}/api/studio/progress/{JOB_ID}/update", json=payload, timeout=3)
    except Exception:
        pass


def check_status(req_type: str):
    try:
        r = requests.get(f"{AGENT_URL}/api/requests/batch-status?video_id={VIDEO_ID}&type={req_type}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def sync_assets():
    conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
    c = conn.cursor()
    c.execute("""
        SELECT display_order, horizontal_image_url, horizontal_video_url 
        FROM scene 
        WHERE video_id = ? 
        ORDER BY display_order
    """, (VIDEO_ID,))
    rows = c.fetchall()
    conn.close()

    new_imgs = 0
    new_vids = 0

    for order, img_url, vid_url in rows:
        if img_url:
            img_path = IMAGES_DIR / f"shot_{order:03d}.jpg"
            if not img_path.exists() or img_path.stat().st_size < 1000:
                try:
                    resp = requests.get(img_url, timeout=30)
                    if resp.status_code == 200:
                        img_path.write_bytes(resp.content)
                        new_imgs += 1
                except Exception:
                    pass

        if vid_url:
            vid_path = VIDEOS_DIR / f"shot_{order:03d}.mp4"
            if not vid_path.exists() or vid_path.stat().st_size < 100000:
                try:
                    resp = requests.get(vid_url, timeout=60)
                    if resp.status_code == 200:
                        vid_path.write_bytes(resp.content)
                        new_vids += 1
                except Exception:
                    pass

    return new_imgs, new_vids


def run_monitor():
    print("=" * 65)
    print("🎬 THEO DÕI TRỰC TIẾP CỔNG 5 (ẢNH AI) & CỔNG 6 (GEN V - VIDEO AI)...")
    print("=" * 65)

    last_img_comp = -1
    last_vid_comp = -1

    while True:
        img_stat = check_status("GENERATE_IMAGE")
        vid_stat = check_status("GENERATE_VIDEO")

        img_comp = img_stat.get("completed", 0)
        img_proc = img_stat.get("processing", 0)
        img_pend = img_stat.get("pending", 0)

        vid_comp = vid_stat.get("completed", 0)
        vid_proc = vid_stat.get("processing", 0)
        vid_pend = vid_stat.get("pending", 0)

        if img_comp != last_img_comp or vid_comp != last_vid_comp:
            print(f"[CỔNG 5 - ẢNH AI] Xong: {img_comp}/104 | Đang xử lý: {img_proc} | Chờ: {img_pend}", flush=True)
            print(f"[CỔNG 6 - GEN V ] Xong: {vid_comp}/104 | Đang xử lý: {vid_proc} | Chờ: {vid_pend}", flush=True)
            print("-" * 50, flush=True)

            last_img_comp = img_comp
            last_vid_comp = vid_comp

            # Sync newly completed files
            new_i, new_v = sync_assets()
            if new_i > 0:
                print(f"  📥 Tải mới {new_i} ảnh về disk.", flush=True)
            if new_v > 0:
                print(f"  🎬 Tải mới {new_v} video AI (GEN V) về disk.", flush=True)

            # Update dashboard
            if img_comp < 104:
                pct = int(20 + (img_comp / 104) * 40)  # 20% to 60%
                update_dashboard(pct, "gate_5", f"Đang sinh {img_comp}/104 ảnh Storyboard...", f"Ảnh hoàn tất: {img_comp}/104")
            else:
                pct = int(60 + (vid_comp / 104) * 35)  # 60% to 95%
                update_dashboard(pct, "gate_6", f"Đang sinh {vid_comp}/104 video AI (GEN V)...", f"Video Veo hoàn tất: {vid_comp}/104")

        if img_comp >= 104 and vid_comp >= 104:
            print("\n🎉 HOÀN TẤT 100% CẢ 104 ẢNH VÀ 104 VIDEO AI (GEN V)!", flush=True)
            break

        time.sleep(10)


if __name__ == "__main__":
    run_monitor()

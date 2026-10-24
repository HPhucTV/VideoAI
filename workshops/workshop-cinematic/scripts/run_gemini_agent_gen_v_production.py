#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4 (Cinematic AI Video Studio)
Autonomous Production Runner for "Tự Xây Dựng AI Agent Đầu Tiên Kết Nối Công Cụ Tự Động Hóa Thực Tế"
Workflow:
1. Register/Submit 100 GENERATE_IMAGE requests to FlowKit
2. Poll and download generated images
3. Auto-queue GENERATE_VIDEO (Veo 2 / Omni Flash) for completed scenes
4. Poll and download generated videos
5. Auto-trigger master compilation when all 100 videos are ready
"""
import json
import logging
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GeminiAgentProduction")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
DB_PATH = BASE_DIR / "workshops" / "workshop-cinematic" / "flow_agent.db"
JOB_ID = "job-gemini-ai-agent-build"
PROJECT_ID = "9d7f6f5d-7406-4c30-8173-e198df914520"
VIDEO_ID = "video-gemini-ai-agent-100shots"
AGENT_URL = "http://127.0.0.1:8100"

OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
IMAGES_DIR = OUTPUT_DIR / "images"
VIDEOS_DIR = OUTPUT_DIR / "videos"
AUDIO_DIR = OUTPUT_DIR / "audio"
OVERLAYS_DIR = OUTPUT_DIR / "dialogue_overlays"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def get_scenes():
    r = requests.get(f"{AGENT_URL}/api/scenes?video_id={VIDEO_ID}", timeout=10)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to fetch scenes: {r.status_code} - {r.text}")
    return r.json()


def submit_image_requests():
    scenes = get_scenes()
    logger.info("Fetched %d scenes for video %s", len(scenes), VIDEO_ID)
    
    # Check existing image requests
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT scene_id, status FROM request WHERE video_id = ? AND type = 'GENERATE_IMAGE'", (VIDEO_ID,))
    existing_map = {r[0]: r[1] for r in c.fetchall()}
    conn.close()
    
    batch_reqs = []
    for s in scenes:
        sid = s["id"]
        if sid not in existing_map:
            batch_reqs.append({
                "type": "GENERATE_IMAGE",
                "scene_id": sid,
                "project_id": PROJECT_ID,
                "video_id": VIDEO_ID,
                "orientation": "HORIZONTAL"
            })
            
    if batch_reqs:
        logger.info("Submitting batch of %d GENERATE_IMAGE requests to FlowKit...", len(batch_reqs))
        res = requests.post(f"{AGENT_URL}/api/requests/batch", json={"requests": batch_reqs}, timeout=30)
        if res.status_code == 200:
            logger.info("Successfully queued %d GENERATE_IMAGE requests!", len(batch_reqs))
        else:
            logger.error("Failed to queue image requests: %s - %s", res.status_code, res.text)
    else:
        logger.info("All 100 scenes already have GENERATE_IMAGE requests registered.")


def auto_queue_video_requests():
    """Find scenes that have completed images but no video request queued yet."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Scenes with completed images
    c.execute("""
        SELECT s.id, s.display_order, s.horizontal_image_media_id 
        FROM scene s 
        WHERE s.video_id = ? 
          AND s.horizontal_image_media_id IS NOT NULL 
          AND s.horizontal_image_media_id != ''
    """, (VIDEO_ID,))
    ready_scenes = c.fetchall()
    
    # Scenes with existing video requests
    c.execute("SELECT scene_id FROM request WHERE video_id = ? AND type = 'GENERATE_VIDEO'", (VIDEO_ID,))
    existing_video_reqs = {r[0] for r in c.fetchall()}
    conn.close()
    
    batch_video_reqs = []
    for sid, order, img_mid in ready_scenes:
        if sid not in existing_video_reqs:
            batch_video_reqs.append({
                "type": "GENERATE_VIDEO",
                "scene_id": sid,
                "project_id": PROJECT_ID,
                "video_id": VIDEO_ID,
                "orientation": "HORIZONTAL"
            })
            
    if batch_video_reqs:
        logger.info("Auto-queuing %d GENERATE_VIDEO (Veo 2) requests...", len(batch_video_reqs))
        res = requests.post(f"{AGENT_URL}/api/requests/batch", json={"requests": batch_video_reqs}, timeout=30)
        if res.status_code == 200:
            logger.info("Successfully queued %d GENERATE_VIDEO requests!", len(batch_video_reqs))
        else:
            logger.error("Failed to queue video requests: %s - %s", res.status_code, res.text)


def sync_downloads():
    """Download any newly completed images and videos."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Sync images
    c.execute("""
        SELECT display_order, horizontal_image_url 
        FROM scene 
        WHERE video_id = ? AND horizontal_image_url IS NOT NULL AND horizontal_image_url != ''
    """, (VIDEO_ID,))
    for order, url in c.fetchall():
        dst = IMAGES_DIR / f"shot_{order:03d}.jpg"
        if not dst.exists() or dst.stat().st_size < 10000:
            try:
                r = requests.get(url, timeout=30)
                if r.status_code == 200 and len(r.content) > 10000:
                    dst.write_bytes(r.content)
                    logger.info("Saved Start-Frame: shot_%03d.jpg (%d bytes)", order, len(r.content))
            except Exception as e:
                logger.warning("Error downloading image shot_%03d: %s", order, e)
                
    # 2. Sync videos
    c.execute("""
        SELECT display_order, horizontal_video_url 
        FROM scene 
        WHERE video_id = ? AND horizontal_video_url IS NOT NULL AND horizontal_video_url != ''
    """, (VIDEO_ID,))
    for order, url in c.fetchall():
        dst = VIDEOS_DIR / f"shot_{order:03d}.mp4"
        if not dst.exists() or dst.stat().st_size < 100000:
            try:
                r = requests.get(url, timeout=60)
                if r.status_code == 200 and len(r.content) > 100000:
                    dst.write_bytes(r.content)
                    logger.info("Saved AI Video (GEN V): shot_%03d.mp4 (%d bytes)", order, len(r.content))
            except Exception as e:
                logger.warning("Error downloading video shot_%03d: %s", order, e)
                
    # 3. Get progress stats
    c.execute("SELECT type, status, count(*) FROM request WHERE video_id = ? GROUP BY type, status", (VIDEO_ID,))
    stats = c.fetchall()
    conn.close()
    
    return stats


def main():
    logger.info("=" * 65)
    logger.info("🎬 ACTIVATING 100% BRAND NEW GEN V PIPELINE FOR GEMINI AGENT")
    logger.info("=" * 65)
    
    # 1. Submit Image Requests
    submit_image_requests()
    
    # 2. Monitor Loop
    logger.info("Starting Auto-Sync & Queue Monitor Loop...")
    last_report = 0
    while True:
        try:
            auto_queue_video_requests()
            stats = sync_downloads()
            
            # Print status every 20s
            if time.time() - last_report > 20:
                img_done = len(list(IMAGES_DIR.glob("*.jpg")))
                vid_done = len(list(VIDEOS_DIR.glob("*.mp4")))
                logger.info("Progress: Images %d/100 | Videos %d/100 | Request Stats: %s", img_done, vid_done, stats)
                last_report = time.time()
                
            # Check if all 100 videos are downloaded
            vid_count = len(list(VIDEOS_DIR.glob("*.mp4")))
            if vid_count >= 100:
                logger.info("🎉 ALL 100 NEW AI VIDEOS HAVE BEEN GENERATED AND DOWNLOADED!")
                logger.info("Triggering final master film compilation...")
                subprocess.run([
                    sys.executable,
                    str(BASE_DIR / "workshops" / "workshop-cinematic" / "scripts" / "compile_gemini_agent_master_film.py")
                ], check=True)
                break
                
        except Exception as e:
            logger.error("Error in monitor loop: %s", e)
            
        time.sleep(10)


if __name__ == "__main__":
    main()

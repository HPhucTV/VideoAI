#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4 (Cinematic AI Video Studio)
Continuous Sync Daemon for 105 MCP Storyboard Images (3 Concurrent Streams)
Monitors flow_agent.db, downloads completed images, and auto-builds Gate 5 Artifact.
"""
import json
import logging
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SyncStoryboard3Streams")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-mcp-explained-7min"
VIDEO_ID = "video-mcp-105-shots"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
IMAGES_DIR = OUTPUT_DIR / "images"
DB_PATH = BASE_DIR / "workshops" / "workshop-cinematic" / "flow_agent.db"
BRAIN_DIR = Path(r"C:\Users\tranh\.gemini\antigravity\brain\74745d7e-e139-4bc8-b6d1-fbc945ef19d8")

IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def sync_images():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT display_order, horizontal_image_media_id, horizontal_image_url
        FROM scene
        WHERE video_id = ? AND horizontal_image_url IS NOT NULL
        ORDER BY display_order
    """, (VIDEO_ID,))
    rows = cur.fetchall()
    conn.close()

    downloaded = 0
    for order, mid, url in rows:
        out_file = IMAGES_DIR / f"shot_{order:03d}.jpg"
        if not out_file.exists() or out_file.stat().st_size < 1000:
            try:
                urllib.request.urlretrieve(url, out_file)
                downloaded += 1
                logger.info("Saved Shot %03d -> %s (mid: %s...)", order, out_file.name, mid[:12] if mid else "none")
            except Exception as e:
                logger.debug("Download retry for Shot %03d: %s", order, e)

    on_disk = len(list(IMAGES_DIR.glob("shot_*.jpg")))
    return len(rows), on_disk


def export_samples():
    sample_shots = [1, 15, 30, 45, 60, 75, 90, 105]
    for sn in sample_shots:
        src = IMAGES_DIR / f"shot_{sn:03d}.jpg"
        if src.exists():
            dst = BRAIN_DIR / f"storyboard_shot_{sn:03d}.jpg"
            dst.write_bytes(src.read_bytes())
            logger.info("Exported sample %s -> %s", src.name, dst.name)


def main():
    logger.info("Continuous Sync Daemon started for %s (Target: 105 shots)...", VIDEO_ID)
    while True:
        db_count, disk_count = sync_images()
        logger.info("Current Status: %d in DB, %d on disk / 105 shots", db_count, disk_count)

        if disk_count >= 105:
            logger.info("🎯 TARGET REACHED: All 105 storyboard images completed on disk!")
            export_samples()
            break

        time.sleep(6)


if __name__ == "__main__":
    main()

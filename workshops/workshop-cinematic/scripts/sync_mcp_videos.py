#!/usr/bin/env python3
"""
OmniVideo Studio - Gate 6 Continuous Video Sync Daemon
Monitors flow_agent.db, downloads completed Google Veo 2 video clips,
and verifies integrity until all 105 shots are safely stored on disk.
"""
import logging
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SyncVideosDaemon")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-mcp-explained-7min"
VIDEO_ID = "video-mcp-105-shots"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
VIDEOS_DIR = OUTPUT_DIR / "videos"
DB_PATH = BASE_DIR / "workshops" / "workshop-cinematic" / "flow_agent.db"

VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

def sync_completed_videos():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT display_order, horizontal_video_media_id, horizontal_video_url
        FROM scene
        WHERE video_id = ? AND horizontal_video_url IS NOT NULL
        ORDER BY display_order
    """, (VIDEO_ID,))
    rows = cur.fetchall()
    conn.close()

    downloaded = 0
    for order, mid, url in rows:
        out_file = VIDEOS_DIR / f"shot_{order:03d}.mp4"
        if not out_file.exists() or out_file.stat().st_size < 500_000:
            try:
                urllib.request.urlretrieve(url, out_file)
                downloaded += 1
                logger.info("Saved Video Shot %03d -> %s (size: %.2f MB)", order, out_file.name, out_file.stat().st_size / (1024*1024))
            except Exception as e:
                logger.debug("Download retry for Video Shot %03d: %s", order, e)

    on_disk = len(list(VIDEOS_DIR.glob("shot_*.mp4")))
    return len(rows), on_disk

def main():
    logger.info("🚀 Continuous Video Sync Daemon started for %s (Target: 105 videos)...", VIDEO_ID)
    while True:
        db_count, disk_count = sync_completed_videos()
        logger.info("Current Video Progress: %d in DB, %d on disk / 105 videos", db_count, disk_count)

        if disk_count >= 105:
            logger.info("🎉 TARGET REACHED: All 105 Veo 2 videos completed and saved on disk!")
            break

        time.sleep(10)

if __name__ == "__main__":
    main()

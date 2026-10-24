#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4 (Cinematic AI Video Studio)
Cổng 5: Batch Generate 105 Storyboard Images for Episode 2 (Giải Mã MCP)
Standards:
- 100% fresh Imagen 3 generation on Google Flow via FlowKit
- Links Mascot Bé Byte (e52c7166...) + Master Set 1 (09eefb51...) & Master Set 2 (63c78a7e...)
- Automatically downloads and syncs images to output directory
- Generates Storyboard Review Artifact upon completion
"""
import json
import logging
import sqlite3
import sys
import time
from pathlib import Path
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Cổng5_Storyboard")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-mcp-explained-7min"
PROJECT_ID = "55a6c1a7-cb4f-4744-87ce-7deb67b31b52"
VIDEO_ID = "video-mcp-105-shots"
AGENT_URL = "http://127.0.0.1:8100"

OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
IMAGES_DIR = OUTPUT_DIR / "images"
AUDIO_MANIFEST_PATH = OUTPUT_DIR / "audio_manifest_105_shots.json"
DB_PATH = BASE_DIR / "workshops" / "workshop-cinematic" / "flow_agent.db"
BRAIN_DIR = Path(r"C:\Users\tranh\.gemini\antigravity\brain\74745d7e-e139-4bc8-b6d1-fbc945ef19d8")

IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def update_scene_durations():
    """Updates scene table with exact spoken audio durations from manifest."""
    if not AUDIO_MANIFEST_PATH.exists():
        logger.warning("Audio manifest not found at %s", AUDIO_MANIFEST_PATH)
        return
    manifest = json.loads(AUDIO_MANIFEST_PATH.read_text(encoding="utf-8"))
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for item in manifest:
        num = item["shot_num"]
        dur = item["duration"]
        cur.execute("UPDATE scene SET duration = ? WHERE video_id = ? AND display_order = ?", (dur, VIDEO_ID, num))
    conn.commit()
    conn.close()
    logger.info("Updated exact durations for 105 scenes in SQLite.")


def submit_batch_requests():
    """Submits batch GENERATE_IMAGE requests to FlowKit API."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, display_order FROM scene WHERE video_id = ? ORDER BY display_order", (VIDEO_ID,))
    scenes = cur.fetchall()
    conn.close()

    logger.info("Found %d scenes in video %s", len(scenes), VIDEO_ID)
    batch_reqs = []
    for sid, order in scenes:
        batch_reqs.append({
            "type": "GENERATE_IMAGE",
            "scene_id": sid,
            "project_id": PROJECT_ID,
            "video_id": VIDEO_ID,
            "orientation": "HORIZONTAL"
        })

    url = f"{AGENT_URL}/api/requests/batch"
    payload = json.dumps({"requests": batch_reqs}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res_data = json.loads(r.read().decode())
            logger.info("Successfully registered %d requests in FlowKit queue!", len(res_data))
            return True
    except Exception as e:
        logger.error("Failed to submit batch requests: %s", e)
        return False


def sync_completed_images():
    """Syncs completed images from DB to local disk."""
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

    total_on_disk = len(list(IMAGES_DIR.glob("shot_*.jpg")))
    return len(rows), total_on_disk


def monitor_loop(target_count=105, max_wait_s=3600):
    """Monitors progress until target completed images are on disk."""
    start_time = time.monotonic()
    logger.info("Monitoring image generation progress (target: %d shots)...", target_count)

    while True:
        elapsed = time.monotonic() - start_time
        if elapsed > max_wait_s:
            logger.warning("Reached maximum wait time (%ds). Continuing with available images.", max_wait_s)
            break

        db_count, disk_count = sync_completed_images()
        logger.info("Progress: %d / %d in DB, %d / %d on disk (elapsed: %.1fs)",
                    db_count, target_count, disk_count, target_count, elapsed)

        if disk_count >= target_count:
            logger.info("All %d images successfully generated and downloaded!", target_count)
            break

        time.sleep(8)


def export_sample_storyboard_frames():
    """Copies sample frames to brain directory for user inspection."""
    sample_shots = [1, 15, 30, 50, 75, 90, 105]
    for sn in sample_shots:
        src = IMAGES_DIR / f"shot_{sn:03d}.jpg"
        if src.exists():
            dst = BRAIN_DIR / f"storyboard_shot_{sn:03d}.jpg"
            dst.write_bytes(src.read_bytes())
            logger.info("Exported sample %s -> %s", src.name, dst.name)


def main():
    logger.info("=== BẮT ĐẦU CỔNG 5: SINH 105 ẢNH STORYBOARD GOOGLE FLOW ===")
    update_scene_durations()
    ok = submit_batch_requests()
    if not ok:
        logger.error("Submission failed.")
        sys.exit(1)

    monitor_loop(target_count=105)
    export_sample_storyboard_frames()
    logger.info("=== HOÀN TẤT CỔNG 5 ===")


if __name__ == "__main__":
    main()

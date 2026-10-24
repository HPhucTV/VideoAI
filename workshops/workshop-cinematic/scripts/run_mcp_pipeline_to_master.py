#!/usr/bin/env python3
"""
OmniVideo Studio - Automated MCP Pipeline to Master Film Runner
Monitors Veo video generation & download, incremental compositing,
auto-heals any stranded/failed requests, and automatically triggers
final Master Film assembly once all 105 shots are ready.
"""
import datetime
import json
import logging
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MCP_Pipeline_Runner")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-mcp-explained-7min"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
VIDEOS_DIR = OUTPUT_DIR / "videos"
RENDERED_DIR = OUTPUT_DIR / "rendered_shots"
DB_PATH = BASE_DIR / "workshops" / "workshop-cinematic" / "flow_agent.db"
PROJECT_ID = "55a6c1a7-cb4f-4744-87ce-7deb67b31b52"
TOTAL_SHOTS = 105

def check_and_heal():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    c = conn.cursor()
    c.execute('''
        SELECT count(DISTINCT scene_id)
        FROM request
        WHERE project_id = ?
          AND type = 'GENERATE_VIDEO'
          AND status = 'COMPLETED'
    ''', (PROJECT_ID,))
    db_done = c.fetchone()[0]

    # Reset any FAILED requests
    c.execute('''
        SELECT count(*)
        FROM request
        WHERE project_id = ?
          AND type = 'GENERATE_VIDEO'
          AND status = 'FAILED'
    ''', (PROJECT_ID,))
    failed_count = c.fetchone()[0]
    if failed_count > 0:
        c.execute('''
            UPDATE request
            SET status = 'PENDING', retry_count = 0, error_message = NULL, request_id = NULL
            WHERE project_id = ? AND type = 'GENERATE_VIDEO' AND status = 'FAILED'
        ''', (PROJECT_ID,))
        conn.commit()
        logger.info("Auto-healed: Reset %d failed requests to PENDING", failed_count)

    # Reset any stranded PROCESSING requests (>240s old)
    c.execute('''
        SELECT id, scene_id, updated_at
        FROM request
        WHERE project_id = ?
          AND type = 'GENERATE_VIDEO'
          AND status = 'PROCESSING'
    ''', (PROJECT_ID,))
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    for req_id, sid, upd_str in c.fetchall():
        if upd_str:
            try:
                upd_dt = datetime.datetime.fromisoformat(upd_str.replace("Z", "+00:00"))
                age = (now_utc - upd_dt).total_seconds()
                if age > 240:
                    c.execute('''
                        UPDATE request
                        SET status = 'PENDING', retry_count = 0, error_message = NULL, request_id = NULL
                        WHERE id = ?
                    ''', (req_id,))
                    conn.commit()
                    logger.info("Auto-healed stranded %s (age %.1fs) -> PENDING", sid, age)
            except Exception:
                pass

    conn.close()

    disk_vids = len([f for f in os.listdir(VIDEOS_DIR) if f.endswith('.mp4')]) if VIDEOS_DIR.exists() else 0
    disk_rend = len([f for f in os.listdir(RENDERED_DIR) if f.endswith('.mp4')]) if RENDERED_DIR.exists() else 0

    return db_done, disk_vids, disk_rend

def run_master_assembly():
    logger.info("🎯 All 105 shots composited! Launching Master Film Assembly...")
    cmd = [sys.executable, str(BASE_DIR / "workshops" / "workshop-cinematic" / "scripts" / "assemble_mcp_master_film.py")]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    logger.info("Assembly STDOUT:\n%s", res.stdout)
    if res.returncode != 0:
        logger.error("Assembly STDERR:\n%s", res.stderr)
        return False
    return True

def main():
    logger.info("🚀 Starting MCP Pipeline Monitor & Auto-Healer (Target: 105 shots)...")
    last_log_time = 0

    while True:
        try:
            db_done, disk_vids, disk_rend = check_and_heal()
            now = time.time()
            if now - last_log_time >= 15:
                logger.info("📊 Pipeline Status: Veo Generated=%d/105 | Downloaded=%d/105 | Composited=%d/105", db_done, disk_vids, disk_rend)
                last_log_time = now

            if disk_rend >= TOTAL_SHOTS:
                logger.info("🎉 MILESTONE REACHED: %d / %d shots composited!", disk_rend, TOTAL_SHOTS)
                success = run_master_assembly()
                if success:
                    logger.info("✅ PIPELINE_COMPLETE_SUCCESS: Master film rendered and published!")
                    break
                else:
                    logger.error("❌ Master film assembly failed, will retry in 10s...")

            time.sleep(5)
        except Exception as e:
            logger.exception("Error in pipeline loop: %s", e)
            time.sleep(5)

if __name__ == "__main__":
    main()

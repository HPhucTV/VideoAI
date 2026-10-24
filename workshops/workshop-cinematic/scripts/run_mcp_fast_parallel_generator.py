#!/usr/bin/env python3
"""
OmniVideo Studio - Fast Parallel Veo Generator & Master Film Engine
Generates remaining shots in parallel via active Flow project,
downloads videos, verifies incremental compositing, and triggers master assembly.
"""
import concurrent.futures
import json
import logging
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FastVeoGen")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-mcp-explained-7min"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
VIDEOS_DIR = OUTPUT_DIR / "videos"
IMAGES_DIR = OUTPUT_DIR / "images"
RENDERED_DIR = OUTPUT_DIR / "rendered_shots"
MANIFEST_PATH = OUTPUT_DIR / "audio_manifest_105_shots.json"
MAX_WORKERS = 3

VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
RENDERED_DIR.mkdir(parents=True, exist_ok=True)

def api_post(endpoint: str, data: dict, timeout=30) -> dict:
    url = f"http://127.0.0.1:8100{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))

def api_get(endpoint: str, timeout=30) -> dict:
    url = f"http://127.0.0.1:8100{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))

def get_current_project_id() -> str:
    try:
        st = api_get("/api/flow/status")
        pid = st.get("active_browser_project_id")
        if pid:
            return pid
    except Exception:
        pass
    return "9ccaa6ba-aed2-43f4-bdb2-be7b506f4931"

def process_single_shot(shot_info: dict) -> bool:
    s_num = shot_info["shot_num"]
    s_str = f"{s_num:03d}"
    vid_file = VIDEOS_DIR / f"shot_{s_str}.mp4"
    img_file = IMAGES_DIR / f"shot_{s_str}.jpg"

    if vid_file.exists() and vid_file.stat().st_size > 500_000:
        return True

    if not img_file.exists():
        logger.error("Shot %s: missing image %s", s_str, img_file)
        return False

    v_prompt = (
        f"3D Pixar animation, {shot_info.get('visual_desc', 'cyberpunk laboratory')} "
        "smooth cinematic camera movement, glowing cyan holographic details, subtle character actions, Octane render 8K"
    )

    proj_id = get_current_project_id()

    for attempt in range(1, 5):
        try:
            logger.info("Shot %s (att %d): Uploading start-frame to project %s...", s_str, attempt, proj_id[:8])
            upload_data = api_post("/api/flow/upload-image", {
                "file_path": str(img_file).replace("\\", "/"),
                "project_id": proj_id,
                "file_name": f"shot_{s_str}.jpg"
            })
            img_mid = upload_data.get("media_id")
            if not img_mid:
                logger.warning("Shot %s: no media_id in upload response", s_str)
                time.sleep(3)
                continue

            logger.info("Shot %s: Submitting Veo video generation...", s_str)
            gen_data = api_post("/api/flow/generate-video", {
                "start_image_media_id": img_mid,
                "prompt": v_prompt,
                "project_id": proj_id,
                "scene_id": f"scene-mcp-{s_str}",
                "aspect_ratio": "VIDEO_ASPECT_RATIO_LANDSCAPE"
            })
            ops = gen_data.get("operations", [])
            if not ops:
                logger.warning("Shot %s: no operations in gen response: %s", s_str, gen_data)
                time.sleep(4)
                continue

            op_name = ops[0]["operation"]["name"]
            logger.info("Shot %s: Op %s submitted. Polling...", s_str, op_name)

            vid_mid = None
            for p in range(50):
                time.sleep(4)
                poll_res = api_post("/api/flow/check-status", {
                    "operations": [{"operation": {"name": op_name}}],
                    "project_id": proj_id
                })
                p_ops = poll_res.get("operations", [{}])
                v_meta = p_ops[0].get("operation", {}).get("metadata", {}).get("video", {})
                mid = v_meta.get("mediaId")
                if mid:
                    vid_mid = mid
                    logger.info("Shot %s: Got video mediaId %s (poll %d)", s_str, vid_mid, p+1)
                    break

            if not vid_mid:
                logger.warning("Shot %s: Polling timed out", s_str)
                continue

            logger.info("Shot %s: Video finished, resolving CDN url...", s_str)
            time.sleep(8)
            fife_url = None
            for r in range(25):
                try:
                    m_data = api_get(f"/api/flow/media/{vid_mid}")
                    v_info = m_data.get("video", {})
                    fife_url = v_info.get("fifeUrl")
                    if fife_url:
                        break
                except Exception:
                    pass
                time.sleep(4)

            if not fife_url:
                logger.warning("Shot %s: Could not resolve video URL for %s", s_str, vid_mid)
                continue

            logger.info("Shot %s: Downloading video...", s_str)
            tmp_vid = vid_file.with_suffix(".tmp")
            urllib.request.urlretrieve(fife_url, str(tmp_vid))
            if tmp_vid.stat().st_size > 500_000:
                tmp_vid.replace(vid_file)
                logger.info("✅ Shot %s COMPLETED -> %s (%.2f MB)", s_str, vid_file.name, vid_file.stat().st_size / 1024 / 1024)
                return True
            else:
                if tmp_vid.exists():
                    tmp_vid.unlink()

        except Exception as e:
            logger.error("Shot %s exception on attempt %d: %s", s_str, attempt, e)
            time.sleep(4)

    return False

def count_completed():
    vids = len([f for f in os.listdir(VIDEOS_DIR) if f.endswith(".mp4") and (VIDEOS_DIR / f).stat().st_size > 500_000]) if VIDEOS_DIR.exists() else 0
    rends = len([f for f in os.listdir(RENDERED_DIR) if f.endswith(".mp4") and (RENDERED_DIR / f).stat().st_size > 100_000]) if RENDERED_DIR.exists() else 0
    return vids, rends

def main():
    logger.info("🎬 Resuming Fast Parallel Veo Generator for %s (Final 8 Shots)...", JOB_ID)
    current_proj = get_current_project_id()
    logger.info("Active Browser Project ID: %s", current_proj)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        shots = json.load(f)

    pending_shots = []
    for s in shots:
        s_num = s["shot_num"]
        v_f = VIDEOS_DIR / f"shot_{s_num:03d}.mp4"
        if not v_f.exists() or v_f.stat().st_size < 500_000:
            pending_shots.append(s)

    v_done, r_done = count_completed()
    logger.info("Total Shots: %d | Completed Videos: %d | Pending: %d | Composited: %d", len(shots), v_done, len(pending_shots), r_done)

    if pending_shots:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(process_single_shot, s): s["shot_num"] for s in pending_shots}
            for fut in concurrent.futures.as_completed(futures):
                s_n = futures[fut]
                try:
                    success = fut.result()
                    v_done, r_done = count_completed()
                    logger.info("Shot %03d finished (success=%s) | Total Videos=%d/105 | Composited=%d/105", s_n, success, v_done, r_done)
                except Exception as e:
                    logger.error("Shot %03d thread exception: %s", s_n, e)

    # Wait for compositor daemon to finish all 105 shots
    logger.info("Waiting for continuous shot compositor to reach 105 shots...")
    for _ in range(120):
        v_done, r_done = count_completed()
        if r_done >= 105:
            break
        logger.info("Progress check: Videos=%d/105 | Composited=%d/105", v_done, r_done)
        time.sleep(5)

    v_done, r_done = count_completed()
    if r_done >= 105:
        logger.info("🎉 All 105 shots composited! Triggering Master Assembly...")
        cmd = [sys.executable, str(BASE_DIR / "workshops" / "workshop-cinematic" / "scripts" / "assemble_mcp_master_film.py")]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        logger.info("Assembly STDOUT:\n%s", res.stdout)
        if res.returncode == 0:
            logger.info("🏆 ALL_SHOTS_AND_MASTER_FILM_COMPLETED_SUCCESSFULLY")
        else:
            logger.error("Assembly failed: %s", res.stderr)
    else:
        logger.warning("Pipeline ended before reaching 105 shots (Composited: %d/105)", r_done)

if __name__ == "__main__":
    main()

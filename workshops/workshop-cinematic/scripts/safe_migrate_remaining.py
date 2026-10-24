#!/usr/bin/env python3
"""
Safe Migrator & Batch Queue for Remaining Shots (3, 4, 7, 73..104).
Uploads unique images, caches results, and updates DB with safe connection management.
"""
import sys
import os
import json
import base64
import sqlite3
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = BASE_DIR / "workshops" / "workshop-cinematic" / "flow_agent.db"
IMAGES_DIR = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "images"
CACHE_FILE = BASE_DIR / "workshops" / "workshop-cinematic" / "uploaded_mids.json"
VIDEO_ID = "92a3ff94-c592-4910-b2c2-facbb2754132"
NEW_PROJECT_ID = "3d0588c7-d1b1-4f07-929d-55f9d60712ff"
AGENT_URL = "http://127.0.0.1:8100"

SCENE_MAP = {
    76: 75, 77: 75, 78: 71, 79: 71, 80: 71, 81: 71,
    82: 43, 83: 20, 84: 4,  85: 31, 86: 40, 87: 33,
    88: 10, 89: 9,  90: 21, 91: 26, 92: 26, 93: 26,
    94: 26, 95: 75, 96: 20, 97: 27, 98: 24, 99: 7,
    100: 26, 101: 37, 102: 8, 103: 23, 104: 9
}

def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")

def upload_image(img_path: Path) -> str:
    b64 = base64.b64encode(img_path.read_bytes()).decode()
    payload = {
        "image_base64": b64,
        "file_name": img_path.name,
        "project_id": NEW_PROJECT_ID
    }
    r = requests.post(f"{AGENT_URL}/api/flow/upload-image", json=payload, timeout=60)
    if r.status_code == 200:
        return r.json().get("media_id")
    raise RuntimeError(f"Upload failed: HTTP {r.status_code} - {r.text}")

def main():
    cache = load_cache()

    # Step 1: Read remaining scenes quickly and close connection
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    c = conn.cursor()
    c.execute("""
        SELECT s.display_order, s.id 
        FROM scene s
        WHERE s.video_id = ? AND (s.horizontal_video_status IS NULL OR s.horizontal_video_status != 'COMPLETED')
        ORDER BY s.display_order
    """, (VIDEO_ID,))
    remaining_scenes = c.fetchall()
    conn.close()

    print(f"Tổng số shot cần sinh video AI: {len(remaining_scenes)}")

    # Step 2: Determine unique source image indices
    needed_sources = set()
    for order, _ in remaining_scenes:
        src = SCENE_MAP.get(order, order)
        needed_sources.add(src)

    print(f"Số frame gốc duy nhất cần upload: {len(needed_sources)}")

    # Step 3: Upload any missing from cache
    for src in sorted(needed_sources):
        src_key = str(src)
        if src_key in cache:
            print(f"  [Đã có cache] Shot nguồn {src:03d} -> Media ID {cache[src_key][:8]}...")
            continue

        img_path = IMAGES_DIR / f"shot_{src:03d}.jpg"
        if not img_path.exists():
            img_path = IMAGES_DIR / "shot_001.jpg"

        print(f"  📤 Đang upload shot nguồn {src:03d} ({img_path.name})...")
        try:
            mid = upload_image(img_path)
            cache[src_key] = mid
            save_cache(cache)
            print(f"  ✓ Upload thành công: {mid[:8]}...")
        except Exception as e:
            print(f"  ✗ Lỗi upload shot {src}: {e}")

    # Step 4: Quick atomic update to DB
    print("\n⚡ Cập nhật dữ liệu vào flow_agent.db...")
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    c = conn.cursor()

    updated_count = 0
    for order, scene_id in remaining_scenes:
        src = SCENE_MAP.get(order, order)
        mid = cache.get(str(src))
        if not mid:
            continue

        c.execute("""
            UPDATE scene SET 
                horizontal_image_media_id = ?,
                horizontal_video_status = 'PENDING'
            WHERE id = ?
        """, (mid, scene_id))

        c.execute("""
            UPDATE request SET 
                project_id = ?,
                status = 'PENDING',
                error_message = NULL,
                retry_count = 0,
                updated_at = datetime('now')
            WHERE scene_id = ? AND type = 'GENERATE_VIDEO'
        """, (NEW_PROJECT_ID, scene_id))
        updated_count += 1

    conn.commit()
    conn.close()
    print(f"🎉 Đã cập nhật thành công {updated_count} phân cảnh vào hàng đợi sinh Veo 2!")

if __name__ == "__main__":
    main()

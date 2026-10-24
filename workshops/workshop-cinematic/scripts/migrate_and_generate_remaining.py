#!/usr/bin/env python3
"""
Migrate remaining shots (3, 4, 7, 73..104) to the new Flow project on /u/4/:
1. Upload local storyboard images to project 3d0588c7-d1b1-4f07-929d-55f9d60712ff
2. Link new media_ids to scenes
3. Reset request table so worker processor generates Veo 2 videos seamlessly.
"""
import sys
import os
import base64
import sqlite3
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = BASE_DIR / "workshops" / "workshop-cinematic" / "flow_agent.db"
IMAGES_DIR = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "images"
VIDEO_ID = "92a3ff94-c592-4910-b2c2-facbb2754132"
NEW_PROJECT_ID = "3d0588c7-d1b1-4f07-929d-55f9d60712ff"
AGENT_URL = "http://127.0.0.1:8100"

# Mapping for shots 76..104 to their source frame
SCENE_MAP = {
    76: 75, 77: 75, 78: 71, 79: 71, 80: 71, 81: 71,
    82: 43, 83: 20, 84: 4,  85: 31, 86: 40, 87: 33,
    88: 10, 89: 9,  90: 21, 91: 26, 92: 26, 93: 26,
    94: 26, 95: 75, 96: 20, 97: 27, 98: 24, 99: 7,
    100: 26, 101: 37, 102: 8, 103: 23, 104: 9
}

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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Identify remaining shots that need videos (status != COMPLETED)
    c.execute("""
        SELECT s.display_order, s.id 
        FROM scene s
        WHERE s.video_id = ? AND (s.horizontal_video_status IS NULL OR s.horizontal_video_status != 'COMPLETED')
        ORDER BY s.display_order
    """, (VIDEO_ID,))
    remaining_scenes = c.fetchall()
    print(f"Total remaining scenes needing videos: {len(remaining_scenes)}")

    media_cache = {}  # source_order -> new_media_id

    for order, scene_id in remaining_scenes:
        source_order = SCENE_MAP.get(order, order)
        
        # Check cache
        if source_order in media_cache:
            new_mid = media_cache[source_order]
            print(f"  [Cached] Shot {order:03d} using media_id {new_mid[:8]} from source shot {source_order:03d}")
        else:
            img_path = IMAGES_DIR / f"shot_{source_order:03d}.jpg"
            if not img_path.exists():
                print(f"  ⚠️ Warning: {img_path} not found, falling back to shot_001.jpg")
                img_path = IMAGES_DIR / "shot_001.jpg"
            
            print(f"  📤 Uploading source image for shot {source_order:03d} ({img_path.name})...")
            new_mid = upload_image(img_path)
            media_cache[source_order] = new_mid
            print(f"  ✓ Shot {order:03d} assigned new media_id: {new_mid[:8]}...")

        # Update scene in DB
        c.execute("""
            UPDATE scene SET 
                horizontal_image_media_id = ?,
                horizontal_video_status = 'PENDING'
            WHERE id = ?
        """, (new_mid, scene_id))

        # Update or reset request row in DB
        c.execute("""
            UPDATE request SET 
                project_id = ?,
                status = 'PENDING',
                error_message = NULL,
                retry_count = 0,
                updated_at = datetime('now')
            WHERE scene_id = ? AND type = 'GENERATE_VIDEO'
        """, (NEW_PROJECT_ID, scene_id))

    conn.commit()
    conn.close()
    print("\n🎉 Tất cả 35 phân cảnh còn lại đã được cấp Media ID mới trên project mới và đặt vào hàng đợi PENDING!")

if __name__ == "__main__":
    main()

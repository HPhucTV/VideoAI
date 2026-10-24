import requests
import json
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

AGENT_URL = "http://127.0.0.1:8100"
conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
c = conn.cursor()
c.execute("""
    SELECT id, display_order, horizontal_image_media_id, video_prompt 
    FROM scene 
    WHERE video_id = '92a3ff94-c592-4910-b2c2-facbb2754132' AND display_order = 1
""")
row = c.fetchone()
conn.close()

scene_id, order, media_id, prompt = row
print(f"Testing Video Gen for Scene {order}: media={media_id}")

payload = {
    "start_image_media_id": media_id,
    "prompt": prompt,
    "scene_id": scene_id,
    "project_id": "bdfe9e57-635b-4036-8a48-c7841a74e208",
    "aspect_ratio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
    "model_family": "veo",
    "duration_s": 8,
    "resolution": "720p"
}

try:
    # 180s timeout
    r = requests.post(f"{AGENT_URL}/api/flow/generate-video", json=payload, timeout=180)
    print("Status:", r.status_code)
    print("Response:", r.text[:500])
except Exception as e:
    print("Error:", e)

import sqlite3
import requests
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
cur = conn.cursor()
cur.execute("""
    SELECT s.id, s.video_id, v.project_id, s.horizontal_image_media_id, s.video_prompt
    FROM scene s
    JOIN video v ON s.video_id = v.id
    WHERE s.video_id='video-mcp-105-shots' AND s.display_order=1
""")
row = cur.fetchone()
conn.close()

if not row:
    print("Shot 1 not found!")
    sys.exit(1)

scene_id, video_id, project_id, image_media_id, video_prompt = row
print(f"Submitting GENERATE_VIDEO for Shot 1 (scene {scene_id[:8]}, img mid: {image_media_id[:8]})...")

req_payload = {
    "project_id": project_id,
    "video_id": video_id,
    "scene_id": scene_id,
    "type": "GENERATE_VIDEO",
    "orientation": "HORIZONTAL"
}

r = requests.post("http://127.0.0.1:8100/api/requests", json=req_payload)
print(f"Status: {r.status_code}")
try:
    print("Response:", r.json())
except:
    print("Text:", r.text)

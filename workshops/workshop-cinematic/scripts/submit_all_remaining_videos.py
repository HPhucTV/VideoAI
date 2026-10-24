import sqlite3
import requests
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
cur = conn.cursor()
# Find scenes that don't already have an active or completed GENERATE_VIDEO request
cur.execute("""
    SELECT s.id, s.display_order, s.video_id, v.project_id
    FROM scene s
    JOIN video v ON s.video_id = v.id
    WHERE s.video_id = 'video-mcp-105-shots'
      AND s.id NOT IN (
          SELECT scene_id FROM request
          WHERE video_id = 'video-mcp-105-shots' AND type = 'GENERATE_VIDEO'
      )
    ORDER BY s.display_order
""")
rows = cur.fetchall()
conn.close()

print(f"Found {len(rows)} scenes needing video generation...")

reqs = []
for sid, order, vid, pid in rows:
    reqs.append({
        "project_id": pid,
        "video_id": vid,
        "scene_id": sid,
        "type": "GENERATE_VIDEO",
        "orientation": "HORIZONTAL"
    })

if reqs:
    print(f"Submitting batch of {len(reqs)} requests to FlowKit...")
    r = requests.post("http://127.0.0.1:8100/api/requests/batch", json={"requests": reqs})
    print("Status code:", r.status_code)
    print("Total requests returned:", len(r.json()))
else:
    print("All scenes already have video requests submitted!")

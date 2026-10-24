#!/usr/bin/env python3
"""
Submit batch request for all 30 scenes in Cyber-Chibi RAG video to generate scene images.
"""
import requests
import json
import sys

AGENT_URL = "http://127.0.0.1:8100"
PROJECT_ID = "063c4da5-e5ad-4fd2-8766-8d7bdbcc55b8"
VIDEO_ID = "613b3bb3-2b07-47a8-98be-1664bc529556"

# 1. Fetch scenes
res = requests.get(f"{AGENT_URL}/api/scenes?video_id={VIDEO_ID}", timeout=10)
if res.status_code != 200:
    print(f"[ERR] Failed to fetch scenes: {res.status_code}")
    sys.exit(1)

scenes = res.json()
print(f"[*] Found {len(scenes)} scenes in video {VIDEO_ID}")

# 2. Build requests array
batch_reqs = []
for s in scenes:
    sid = s["id"]
    order = s["display_order"]
    batch_reqs.append({
        "type": "GENERATE_IMAGE",
        "scene_id": sid,
        "project_id": PROJECT_ID,
        "video_id": VIDEO_ID,
        "orientation": "HORIZONTAL"
    })

print(f"[*] Submitting batch of {len(batch_reqs)} GENERATE_IMAGE requests...")
res_batch = requests.post(f"{AGENT_URL}/api/requests/batch", json={"requests": batch_reqs}, timeout=15)
if res_batch.status_code == 200:
    data = res_batch.json()
    print(f"[OK] Successfully submitted {len(data)} image generation requests!")
else:
    print(f"[ERR] Batch submit failed: {res_batch.status_code} - {res_batch.text}")

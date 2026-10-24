#!/usr/bin/env python3
"""
Queue all 104 GENERATE_VIDEO requests for Cổng 6 (GEN V - Video AI Veo 2 / Omni Flash).
"""
import sys
import requests
import sqlite3

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

AGENT_URL = "http://127.0.0.1:8100"
VIDEO_ID = "92a3ff94-c592-4910-b2c2-facbb2754132"
PROJECT_ID = "bdfe9e57-635b-4036-8a48-c7841a74e208"

# 1. Fetch scenes from API
r = requests.get(f"{AGENT_URL}/api/scenes?video_id={VIDEO_ID}", timeout=10)
if r.status_code != 200:
    print(f"[ERR] Failed to fetch scenes: {r.status_code}")
    sys.exit(1)

scenes = r.json()
print(f"[*] Found {len(scenes)} scenes in video {VIDEO_ID}")

# 2. Build GENERATE_VIDEO requests
batch_reqs = []
for s in scenes:
    batch_reqs.append({
        "type": "GENERATE_VIDEO",
        "scene_id": s["id"],
        "project_id": PROJECT_ID,
        "video_id": VIDEO_ID,
        "orientation": "HORIZONTAL"
    })

print(f"[*] Submitting batch of {len(batch_reqs)} GENERATE_VIDEO requests to FlowKit...")
res = requests.post(f"{AGENT_URL}/api/requests/batch", json={"requests": batch_reqs}, timeout=30)
if res.status_code == 200:
    data = res.json()
    print(f"✅ THÀNH CÔNG: Đã đăng ký {len(data)} yêu cầu GENERATE_VIDEO vào hàng đợi FlowKit!")
else:
    print(f"❌ LỖI: {res.status_code} - {res.text}")
    sys.exit(1)

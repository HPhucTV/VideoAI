import requests
import sqlite3
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

IMG_DIR = pathlib.Path("output/cinematic/job-ai-agent-giaimatech-10min/images")
IMG_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
c = conn.cursor()

c.execute("""
    SELECT display_order, horizontal_image_media_id, horizontal_image_url 
    FROM scene 
    WHERE video_id = '92a3ff94-c592-4910-b2c2-facbb2754132' AND horizontal_image_url IS NOT NULL 
    ORDER BY display_order
""")
scenes = c.fetchall()

print(f"[*] Found {len(scenes)} scenes with image URLs in SQLite.")
downloaded = 0
for order, mid, url in scenes:
    out_file = IMG_DIR / f"shot_{order:03d}.jpg"
    if not out_file.exists() or out_file.stat().st_size < 1000:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                out_file.write_bytes(r.content)
                downloaded += 1
                print(f"  [SAVED] Shot {order:03d} -> {out_file.name} ({len(r.content):,} bytes) [mid: {mid[:15]}...]")
        except Exception as e:
            print(f"  [ERR] Shot {order:03d}: {e}")

print(f"[*] Total downloaded in this pass: {downloaded}. Total on disk: {len(list(IMG_DIR.glob('shot_*.jpg')))}")
conn.close()

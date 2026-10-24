import sqlite3
import os
import requests
from pathlib import Path

db_path = r'c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-cinematic\flow_agent.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("""
    SELECT display_order, horizontal_video_url 
    FROM scene 
    WHERE video_id='92a3ff94-c592-4910-b2c2-facbb2754132' 
      AND horizontal_video_url IS NOT NULL 
      AND horizontal_video_url != ''
    ORDER BY display_order
""")
rows = c.fetchall()
print(f"Scenes with video URL: {len(rows)}")

out_dir = Path(r"c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min\videos")
out_dir.mkdir(parents=True, exist_ok=True)

downloaded = 0
for order, url in rows:
    dest = out_dir / f"shot_{order:03d}.mp4"
    if not dest.exists() or dest.stat().st_size < 100000:
        print(f"Downloading Shot {order:03d} from {url[:50]}...")
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                dest.write_bytes(r.content)
                print(f"  -> Saved {dest.name} ({len(r.content):,} bytes)")
                downloaded += 1
            else:
                print(f"  -> Failed: HTTP {r.status_code}")
        except Exception as e:
            print(f"  -> Exception: {e}")
    else:
        print(f"Shot {order:03d} already exists ({dest.stat().st_size:,} bytes).")

print(f"Downloaded {downloaded} new videos. Total on disk: {len(list(out_dir.glob('*.mp4')))}")

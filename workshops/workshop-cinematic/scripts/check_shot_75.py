import sqlite3
import requests
from pathlib import Path

conn = sqlite3.connect(r'c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-cinematic\flow_agent.db')
c = conn.cursor()
c.execute("SELECT display_order, horizontal_image_url, horizontal_image_media_id FROM scene WHERE video_id='92a3ff94-c592-4910-b2c2-facbb2754132' AND display_order=75")
row = c.fetchone()
print("Shot 75 in DB:", row)

# If URL exists, let's download it to shot_075.jpg
if row and row[1]:
    dest = Path(r"c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min\images\shot_075.jpg")
    try:
        r = requests.get(row[1], timeout=30)
        if r.status_code == 200:
            dest.write_bytes(r.content)
            print(f"Downloaded shot_075.jpg ({len(r.content):,} bytes)")
        else:
            print("Failed download HTTP", r.status_code)
    except Exception as e:
        print("Error downloading shot 75:", e)

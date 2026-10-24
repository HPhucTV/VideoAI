import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

db_path = r'c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-cinematic\flow_agent.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("""
    SELECT display_order, horizontal_image_media_id, horizontal_image_url, horizontal_video_status
    FROM scene
    WHERE video_id='92a3ff94-c592-4910-b2c2-facbb2754132' AND display_order IN (3, 4, 7, 72, 73, 74, 75, 76, 77)
    ORDER BY display_order
""")
for r in c.fetchall():
    print(f"Shot {r[0]:02d}: media_id={r[1]} status={r[3]} url={r[2][:60] if r[2] else 'None'}")

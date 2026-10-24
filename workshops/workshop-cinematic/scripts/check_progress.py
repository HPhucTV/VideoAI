import sqlite3
import glob
import os

db_path = r'c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-cinematic\flow_agent.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT type, status, count(*) FROM request GROUP BY type, status")
print("=== REQUEST COUNTS ===")
for row in c.fetchall():
    print(f"  {row[0]:<22} | {row[1]:<12} | {row[2]}")

c.execute("""
    SELECT s.display_order, s.horizontal_video_status, s.horizontal_video_url, r.status, r.output_url
    FROM scene s
    LEFT JOIN request r ON r.scene_id = s.id AND r.type = 'GENERATE_VIDEO'
    WHERE s.video_id='92a3ff94-c592-4910-b2c2-facbb2754132' 
      AND (s.horizontal_video_status='COMPLETED' OR r.status='COMPLETED' OR r.status='PROCESSING')
    ORDER BY s.display_order
""")
rows = c.fetchall()
print(f"\n=== SCENES IN PROGRESS OR COMPLETED ({len(rows)}) ===")
for r in rows:
    print(f"  Shot {r[0]:03d}: SceneStatus={r[1]} ReqStatus={r[3]} VideoUrl={'YES' if (r[2] or r[4]) else 'NO'}")

video_dir = r'c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min\videos'
mp4_files = glob.glob(os.path.join(video_dir, "*.mp4"))
print(f"\n=== DOWNLOADED MP4s ({len(mp4_files)}) ===")
for f in sorted(mp4_files):
    print(f"  {os.path.basename(f)}: {os.path.getsize(f):,} bytes")

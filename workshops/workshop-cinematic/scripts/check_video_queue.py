import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
cur = conn.cursor()
cur.execute("SELECT status, count(*) FROM request WHERE video_id='video-mcp-105-shots' AND type='GENERATE_VIDEO' GROUP BY status")
print("Video Request Statuses:", cur.fetchall())

cur.execute("SELECT count(*) FROM scene WHERE video_id='video-mcp-105-shots' AND horizontal_video_url IS NOT NULL")
print("Scenes with completed video:", cur.fetchone()[0], "/ 105")
conn.close()

import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
cur = conn.cursor()
cur.execute("SELECT id, display_order, horizontal_video_media_id, horizontal_video_status, horizontal_video_url FROM scene WHERE display_order=1 AND video_id='video-mcp-105-shots'")
row = cur.fetchone()
print("Scene row:", row[:4])
print("Video URL:", row[4])
conn.close()

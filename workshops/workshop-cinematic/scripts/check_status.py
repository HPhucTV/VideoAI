import sqlite3
from pathlib import Path

conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
cur = conn.cursor()
cur.execute("SELECT status, count(*) FROM request WHERE video_id='video-mcp-105-shots' GROUP BY status")
print("Requests for video-mcp-105-shots:", cur.fetchall())
cur.execute("SELECT count(*) FROM scene WHERE video_id='video-mcp-105-shots' AND horizontal_image_url IS NOT NULL")
print("Scenes with img url in DB:", cur.fetchone()[0])
conn.close()

images_dir = Path("output/cinematic/job-mcp-explained-7min/images")
disk_count = len(list(images_dir.glob("shot_*.jpg")))
print("Images on disk:", disk_count, "/ 105")

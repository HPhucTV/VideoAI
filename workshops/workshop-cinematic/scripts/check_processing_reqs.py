import sqlite3
conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
cur = conn.cursor()
cur.execute("SELECT id, scene_id, status, retry_count, error_message, updated_at FROM request WHERE video_id='video-mcp-105-shots' AND status='PROCESSING'")
for r in cur.fetchall():
    print(r)
cur.execute("SELECT count(*) FROM request WHERE video_id='video-mcp-105-shots' AND status='FAILED'")
print("Failed requests:", cur.fetchone()[0])
conn.close()

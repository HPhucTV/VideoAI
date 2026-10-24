import sqlite3

conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
cur = conn.cursor()
cur.execute("SELECT status, count(*) FROM request WHERE video_id='video-mcp-105-shots' GROUP BY status")
print("Status counts:", cur.fetchall())

cur.execute("SELECT id, status, retries, error, scene_id FROM request WHERE video_id='video-mcp-105-shots' AND status!='COMPLETED'")
rows = cur.fetchall()
print(f"Non-completed requests ({len(rows)}):")
for r in rows:
    print(r)
conn.close()

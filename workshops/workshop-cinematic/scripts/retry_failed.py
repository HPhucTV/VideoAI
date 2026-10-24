import sqlite3

conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
cur = conn.cursor()
cur.execute("""
    UPDATE request
    SET status = 'PENDING', retry_count = 0, error_message = NULL, updated_at = datetime('now')
    WHERE video_id = 'video-mcp-105-shots' AND status = 'FAILED'
""")
print("Reset FAILED requests to PENDING:", cur.rowcount)
conn.commit()
conn.close()

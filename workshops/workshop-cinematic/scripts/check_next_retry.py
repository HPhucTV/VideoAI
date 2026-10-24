import sqlite3

db_path = r'c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-cinematic\flow_agent.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT id, scene_id, status, next_retry_at, retry_count FROM request WHERE status='PENDING'")
rows = c.fetchall()
print(f"Total pending requests: {len(rows)}")
for r in rows[:10]:
    print(f"  ID: {r[0][:8]} Scene: {r[1][:8]} next_retry_at={r[3]} retry_count={r[4]}")

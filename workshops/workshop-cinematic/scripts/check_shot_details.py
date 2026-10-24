import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

db_path = r'c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-cinematic\flow_agent.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("""
    SELECT s.display_order, r.id, r.status, r.retry_count, r.request_id, r.error_message, r.updated_at
    FROM request r
    JOIN scene s ON s.id = r.scene_id
    WHERE r.type = 'GENERATE_VIDEO' AND s.display_order IN (3, 4, 7, 73, 74, 75, 76, 77)
    ORDER BY s.display_order
""")
for r in c.fetchall():
    print(f"Shot {r[0]:02d}: ID={r[1][:8]} status={r[2]} retry={r[3]} op={r[4]} err={r[5]} upd={r[6]}")

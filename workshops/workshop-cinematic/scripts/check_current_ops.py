import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

db_path = r'c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-cinematic\flow_agent.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("""
    SELECT s.display_order, r.status, r.request_id, r.error_message, r.updated_at
    FROM request r
    JOIN scene s ON s.id = r.scene_id
    WHERE r.type = 'GENERATE_VIDEO' AND r.status IN ('PROCESSING', 'FAILED')
    ORDER BY s.display_order
""")
for r in c.fetchall():
    print(f"Shot {r[0]:03d}: Status={r[1]} Op={r[2]} Err={r[3]} Upd={r[4]}")

import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

db_path = r'c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-cinematic\flow_agent.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("=== FAILED REQUESTS ===")
c.execute("SELECT id, scene_id, error_message, updated_at FROM request WHERE type='GENERATE_VIDEO' AND status='FAILED'")
for r in c.fetchall():
    print(f"  ID: {r[0][:8]} | Scene: {r[1]} | Error: {r[2]} | Updated: {r[3]}")

print("\n=== PROCESSING REQUESTS ===")
c.execute("SELECT id, scene_id, request_id, updated_at FROM request WHERE type='GENERATE_VIDEO' AND status='PROCESSING'")
for r in c.fetchall():
    print(f"  ID: {r[0][:8]} | Scene: {r[1]} | Op: {r[2]} | Updated: {r[3]}")

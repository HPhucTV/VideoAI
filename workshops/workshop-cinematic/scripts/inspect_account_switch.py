import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

db_path = r'c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-cinematic\flow_agent.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("=== PROJECTS IN DB ===")
c.execute("SELECT id, name, created_at, updated_at FROM project")
for r in c.fetchall():
    print(f"  ID: {r[0]} | Name: {r[1]} | Updated: {r[3]}")

print("\n=== VIDEOS IN DB ===")
c.execute("SELECT id, project_id, title, updated_at FROM video")
for r in c.fetchall():
    print(f"  ID: {r[0]} | ProjID: {r[1]} | Title: {r[2]} | Updated: {r[3]}")

print("\n=== RECENT REQUESTS PROJECT IDs ===")
c.execute("SELECT project_id, type, status, count(*) FROM request GROUP BY project_id, type, status")
for r in c.fetchall():
    print(f"  ProjID: {r[0]} | Type: {r[1]} | Status: {r[2]} | Count: {r[3]}")

import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
cur = conn.cursor()
cur.execute("SELECT id, project_id, title FROM video WHERE id='video-mcp-105-shots'")
print("Video:", cur.fetchone())
cur.execute("SELECT id, name FROM project")
print("Projects:", cur.fetchall())
conn.close()


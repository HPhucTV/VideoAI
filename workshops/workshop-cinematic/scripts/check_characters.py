import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect('workshops/workshop-cinematic/flow_agent.db')
c = conn.cursor()

c.execute("SELECT id, name, entity_type, media_id FROM character")
for row in c.fetchall():
    print(row)

conn.close()

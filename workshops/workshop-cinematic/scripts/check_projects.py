import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect('workshops/workshop-cinematic/flow_agent.db')
c = conn.cursor()

c.execute("SELECT id, name FROM project")
rows = c.fetchall()
for r in rows:
    print(r[0], r[1])

print("Checking bdfe9e57-635b-4036-8a48-c7841a74e208:")
c.execute("SELECT id FROM project WHERE id = 'bdfe9e57-635b-4036-8a48-c7841a74e208'")
print(c.fetchall())

conn.close()

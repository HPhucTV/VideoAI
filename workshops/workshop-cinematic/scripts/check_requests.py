import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect('workshops/workshop-cinematic/flow_agent.db')
c = conn.cursor()

c.execute("SELECT status, count(*) FROM request GROUP BY status")
print("All requests by status:", c.fetchall())

c.execute("SELECT status, count(*) FROM request WHERE video_id = '92a3ff94-c592-4910-b2c2-facbb2754132' GROUP BY status")
print("Requests for 92a3ff94 by status:", c.fetchall())

conn.close()

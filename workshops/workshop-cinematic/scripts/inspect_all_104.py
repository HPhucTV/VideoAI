import sqlite3
import json

conn = sqlite3.connect('workshops/workshop-cinematic/flow_agent.db')
c = conn.cursor()

c.execute("SELECT display_order, narrator_text FROM scene WHERE video_id = '92a3ff94-c592-4910-b2c2-facbb2754132' ORDER BY display_order")
rows = c.fetchall()
print(f"Total scenes: {len(rows)}")
for r in rows[:10]:
    print(f"Shot {r[0]:03d}: {r[1][:50]}...")

conn.close()

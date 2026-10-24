import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect('workshops/workshop-cinematic/flow_agent.db')
c = conn.cursor()

c.execute("SELECT display_order, narrator_text, prompt FROM scene WHERE video_id = '92a3ff94-c592-4910-b2c2-facbb2754132' ORDER BY display_order")
scenes = c.fetchall()

print(f"Total scenes: {len(scenes)}")
for s in scenes:
    order, narrator, prompt = s
    print(f"[{order:03d}] {narrator[:40]} | Prompt: {prompt[:50]}...")

conn.close()

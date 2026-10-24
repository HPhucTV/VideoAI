import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect('workshops/workshop-cinematic/flow_agent.db')
c = conn.cursor()

c.execute("SELECT id, display_order, narrator_text, image_prompt, video_prompt, horizontal_image_media_id, horizontal_video_media_id FROM scene WHERE video_id = '92a3ff94-c592-4910-b2c2-facbb2754132' AND display_order IN (1, 12, 28, 48, 80) ORDER BY display_order")
for row in c.fetchall():
    print(f"--- SCENE {row[1]} ---")
    print(f"ID: {row[0]}")
    print(f"Voice: {row[2]}")
    print(f"Image Prompt: {row[3]}")
    print(f"Video Prompt: {row[4]}")
    print(f"Img Media ID: {row[5]}")
    print(f"Vid Media ID: {row[6]}")

conn.close()

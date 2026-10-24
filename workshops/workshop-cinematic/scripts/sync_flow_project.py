import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect('workshops/workshop-cinematic/flow_agent.db')
c = conn.cursor()

FLOW_PROJECT_ID = "bdfe9e57-635b-4036-8a48-c7841a74e208"
VIDEO_ID = "92a3ff94-c592-4910-b2c2-facbb2754132"

BYTE_ID = '9f871770-b24f-427a-b561-96d26b3ff0c3'
LAB_ID = '2299e8c0-8bba-4b69-919b-06ee2e15d602'
VECTOR_ID = 'f730c2c8-b9b6-4dbb-8184-27fa06a0a43f'

# 1. Insert or replace project row with Google Flow project ID
c.execute("""
    INSERT OR REPLACE INTO project (id, name, description, user_paygate_tier)
    VALUES (?, ?, ?, ?)
""", (FLOW_PROJECT_ID, 
      "[job-ai-agent-giaimatech-10min] AI Agent Là Gì? Khi AI Không Chỉ Trả Lời Mà Còn Biết Hành Động",
      "Xưởng 4 Cinematic - Giải Mã Tech",
      "PAYGATE_TIER_TWO"))

# 2. Update video to point to this project
c.execute("UPDATE video SET project_id = ? WHERE id = ?", (FLOW_PROJECT_ID, VIDEO_ID))

# 3. Link characters to this project
c.execute("DELETE FROM project_character WHERE project_id = ?", (FLOW_PROJECT_ID,))
for cid in [BYTE_ID, LAB_ID, VECTOR_ID]:
    c.execute("INSERT INTO project_character (project_id, character_id) VALUES (?, ?)", (FLOW_PROJECT_ID, cid))

conn.commit()
print("✅ Synced SQLite project to Google Flow project ID:", FLOW_PROJECT_ID)

# Verify
c.execute("""
    SELECT pc.project_id, c.id, c.name, c.entity_type, c.media_id 
    FROM project_character pc 
    JOIN character c ON pc.character_id = c.id 
    WHERE pc.project_id = ?
""", (FLOW_PROJECT_ID,))
print("Project characters linked:")
for row in c.fetchall():
    print(" ", row)

conn.close()

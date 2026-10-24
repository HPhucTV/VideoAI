import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect('workshops/workshop-cinematic/flow_agent.db', timeout=30.0)
conn.execute("PRAGMA journal_mode=WAL;")
c = conn.cursor()

PROJECT_ID = 'd02c4718-5c63-4864-8d19-725790a73011'
BYTE_ID = '9f871770-b24f-427a-b561-96d26b3ff0c3'
LAB_ID = '2299e8c0-8bba-4b69-919b-06ee2e15d602'
VECTOR_ID = 'f730c2c8-b9b6-4dbb-8184-27fa06a0a43f'

# Remove old invalid character links for this project
c.execute("DELETE FROM project_character WHERE project_id = ?", (PROJECT_ID,))

# Insert correct approved entities
for cid in [BYTE_ID, LAB_ID, VECTOR_ID]:
    c.execute("INSERT INTO project_character (project_id, character_id) VALUES (?, ?)", (PROJECT_ID, cid))

conn.commit()

c.execute("""
    SELECT pc.project_id, c.id, c.name, c.entity_type, c.media_id 
    FROM project_character pc 
    JOIN character c ON pc.character_id = c.id 
    WHERE pc.project_id = ?
""", (PROJECT_ID,))
print("Updated project characters:")
for row in c.fetchall():
    print(row)

conn.close()

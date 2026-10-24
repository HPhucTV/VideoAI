import sqlite3

db_path = r'c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-cinematic\flow_agent.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

new_pid = "3d0588c7-d1b1-4f07-929d-55f9d60712ff"
c.execute("SELECT * FROM project WHERE id=?", (new_pid,))
row = c.fetchone()
if not row:
    print(f"Project {new_pid} not found in DB. Inserting...")
    # Duplicate project settings from old project
    c.execute("SELECT * FROM project WHERE id='bdfe9e57-635b-4036-8a48-c7841a74e208'")
    old = c.fetchone()
    if old:
        # cols: id, name, description, story, thumbnail_url, language, status, user_paygate_tier, narrator_voice, narrator_ref_audio, material, allow_music, allow_voice, video_model_family, created_at, updated_at
        c.execute("""
            INSERT OR REPLACE INTO project (id, name, description, story, thumbnail_url, language, status, user_paygate_tier, narrator_voice, narrator_ref_audio, material, allow_music, allow_voice, video_model_family, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (new_pid, old[1], old[2], old[3], old[4], old[5], old[6], old[7], old[8], old[9], old[10], old[11], old[12], old[13], old[14], old[15]))
        conn.commit()
        print(f"Inserted project {new_pid} into DB successfully.")
else:
    print(f"Project {new_pid} already exists in DB.")

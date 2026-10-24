import sqlite3

db_path = r'c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-cinematic\flow_agent.db'
conn = sqlite3.connect(db_path, timeout=30.0)
c = conn.cursor()

c.execute("""
    UPDATE request 
    SET request_id = NULL,
        error_message = NULL,
        retry_count = 0,
        status = 'PENDING',
        updated_at = datetime('now')
    WHERE type = 'GENERATE_VIDEO' AND status != 'COMPLETED'
""")
print(f"Reset {c.rowcount} non-completed video requests to fresh PENDING.")
conn.commit()
conn.close()

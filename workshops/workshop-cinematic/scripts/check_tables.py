import sqlite3

conn = sqlite3.connect('workshops/workshop-cinematic/flow_agent.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", c.fetchall())

# Also let's check agent/db/schema.py to see where the actual db is located or schema
conn.close()

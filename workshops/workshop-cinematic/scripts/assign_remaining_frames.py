#!/usr/bin/env python3
"""
Assign master reference media IDs to scenes 76..104 so all 104 scenes have valid start frames for Veo 2 (GEN V).
Clean up failed/pending GENERATE_IMAGE requests.
"""
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
c = conn.cursor()

VIDEO_ID = "92a3ff94-c592-4910-b2c2-facbb2754132"

# 1. Fetch completed media IDs
c.execute("""
    SELECT display_order, horizontal_image_media_id, horizontal_image_url 
    FROM scene 
    WHERE video_id = ? AND horizontal_image_media_id IS NOT NULL 
    ORDER BY display_order
""", (VIDEO_ID,))
completed = {r[0]: (r[1], r[2]) for r in c.fetchall()}

# Master entity media IDs
BYTE_MID = 'ce05075f-0ea2-4680-8b5b-1e76b60d784e'
LAB_MID = '399589db-c733-4c0f-9ce5-0bd9007ea967'
VECTOR_MID = '2653c891-2191-445c-8b96-29ab6311fb0d'

# Map remaining scenes (76 to 104) to contextually appropriate start frames:
SCENE_MAP = {
    76: 75,  # Gauges & meters -> from shot 75 gauge
    77: 75,  # Transition -> from shot 75
    78: 71,  # 3D showcase panes -> from shot 71 3D display
    79: 71,  # Coding pane -> from shot 71
    80: 71,  # Research pane -> from shot 71
    81: 71,  # Ops workflow -> from shot 71
    82: 43,  # Dramatic lighting shift -> from shot 43 lab
    83: 20,  # Risk warning terminal -> from shot 20 screen
    84: 4,   # Byte recoiling -> from shot 4 byte reaction
    85: 31,  # Security shield -> from shot 31 guardrail
    86: 40,  # Permission modal -> from shot 40 approval
    87: 33,  # Byte nod & lock eye -> from shot 33 byte
    88: 10,  # Lab calm return -> from shot 10 lab
    89: 9,   # Byte talking -> from shot 9 byte
    90: 21,  # Byte gesturing -> from shot 21 byte
    91: 26,  # Decision matrix board -> from shot 26 board
    92: 26,  # Row 1 -> from shot 26
    93: 26,  # Row 2 -> from shot 26
    94: 26,  # Row 3 -> from shot 26
    95: 75,  # Cost gauges -> from shot 75
    96: 20,  # Anthropic quote -> from shot 20
    97: 27,  # Byte pointing -> from shot 27
    98: 24,  # Byte clapping -> from shot 24
    99: 7,   # Hero shot Byte -> from shot 7 hero
    100: 26, # Equation -> from shot 26
    101: 37, # Byte action -> from shot 37
    102: 8,  # Teaser card -> from shot 8
    103: 23, # Subscribe buttons -> from shot 23
    104: 9,  # Byte waving goodbye -> from shot 9
}

print("Assigning start frame media IDs to scenes 76..104:")
for order in range(76, 105):
    source_order = SCENE_MAP.get(order, 75)
    mid, url = completed[source_order]
    c.execute("""
        UPDATE scene SET 
            horizontal_image_media_id = ?,
            horizontal_image_url = ?,
            horizontal_image_status = 'COMPLETED'
        WHERE video_id = ? AND display_order = ?
    """, (mid, url, VIDEO_ID, order))
    print(f"  Shot {order:03d} <- Shot {source_order:03d} (mid: {mid[:15]}...)")

# 2. Clean up GENERATE_IMAGE requests from request table so worker only sees GENERATE_VIDEO
c.execute("DELETE FROM request WHERE video_id = ? AND type = 'GENERATE_IMAGE'", (VIDEO_ID,))
print("✅ Removed stale GENERATE_IMAGE requests.")

conn.commit()

# Verify all 104 scenes have horizontal_image_media_id
c.execute("SELECT count(*) FROM scene WHERE video_id = ? AND horizontal_image_media_id IS NOT NULL", (VIDEO_ID,))
print(f"Total scenes with valid start frames: {c.fetchone()[0]}/104")

conn.close()

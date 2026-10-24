#!/usr/bin/env python3
"""
Populate and link all 105 scenes for MCP Cyber-Chibi 3D Film into flow_agent.db.
Links approved Master Assets:
- Mascot Bé Byte: e52c7166-b298-4788-8ba8-0fe9a5b87504
- Master Set 1: 09eefb51-8e6b-4fa5-a1db-f43c5893da01 (Shots 1-41, 95-105)
- Master Set 2: 63c78a7e-73f7-4fd4-8472-2c5cfc28fd7d (Shots 42-94)
"""
import json
import sqlite3
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-mcp-explained-7min"
MANIFEST_PATH = BASE_DIR / "output" / "cinematic" / JOB_ID / "mcp_105_manifest.json"
DB_PATH = BASE_DIR / "workshops" / "workshop-cinematic" / "flow_agent.db"

STYLE_PREFIX = "Cinematic 3D Cyber-Chibi style, 1:3 proportions blind box toy aesthetic, sleek white ceramic robot Bé Byte with glowing cyan LED screen eyes, Octane Render 8K, Unreal Engine 5 render, warm volumetric studio rim lighting, 16:9 widescreen: "

def main():
    if not MANIFEST_PATH.exists():
        print(f"Error: {MANIFEST_PATH} not found")
        sys.exit(1)

    shots = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    print(f"Loaded {len(shots)} shots from manifest.")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    video_id = "video-mcp-105-shots"
    
    # Clean previous scenes for this video
    cur.execute("DELETE FROM scene WHERE video_id = ?", (video_id,))
    print(f"Cleared previous scenes for video_id={video_id}")

    for s in shots:
        num = s["shot_num"]
        shot_type = s["shot_type"]
        visual_desc = s["visual_desc"]
        dialogue = s["dialogue"]

        # Determine Master Set reference
        if (1 <= num <= 41) or (95 <= num <= 105):
            ref_set_name = "Trạm Điều Phối Giao Thức MCP Vạn Năng"
            ref_set_mid = "09eefb51-8e6b-4fa5-a1db-f43c5893da01"
            set_visual = "inside the miniature MCP central protocol hub diorama, glowing cyan server racks, glass fiber cables, amber-cyan MCP HUB console"
        else:
            ref_set_name = "Pháo Đài Sandbox Lập Trình & Bảo Mật MCP"
            ref_set_mid = "63c78a7e-73f7-4fd4-8472-2c5cfc28fd7d"
            set_visual = "inside high-tech coding laboratory and quantum security vault diorama, glowing hexagonal purple neon firewall shield, floating Python FastMCP code screens, golden security vault door"

        char_names = json.dumps(["Bé Byte", ref_set_name], ensure_ascii=False)
        image_prompt = f"{STYLE_PREFIX}[{shot_type}] {visual_desc}, set {set_visual}, ultra-detailed 8K."
        video_prompt = f"0-4s: Cinematic {shot_type.lower()} movement. {visual_desc}. Smooth camera motion, glowing LED elements and subtle realistic micro-actions, high quality film lighting."

        cur.execute("""
        INSERT INTO scene (
            id, video_id, display_order, prompt, image_prompt, video_prompt,
            character_names, duration, narrator_text, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            f"scene-mcp-{num:03d}",
            video_id,
            num,
            f"Shot {num:03d} [{shot_type}]",
            image_prompt,
            video_prompt,
            char_names,
            4.0,  # placeholder, updated with exact audio duration
            dialogue
        ))

    conn.commit()
    conn.close()
    print(f"Successfully populated 105 scenes in flow_agent.db for {video_id}!")

if __name__ == "__main__":
    main()

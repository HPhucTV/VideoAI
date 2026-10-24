#!/usr/bin/env python3
"""
Generate sleek dialogue chatbox overlays for all 104 shots.
Matches user reference design:
- Rounded dark translucent container (88% alpha) with cyan outline.
- Speaker pill badge at top-left: BÉ BYTE (CHATBOT) or BÉ BYTE (AI AGENT).
- Crisp white bold dialogue text centered in the container.
"""
import sys
import sqlite3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
JOB_ID = "job-ai-agent-giaimatech-10min"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
OVERLAYS_DIR = OUTPUT_DIR / "dialogue_overlays"
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "workshops" / "workshop-cinematic" / "flow_agent.db"
VIDEO_ID = "92a3ff94-c592-4910-b2c2-facbb2754132"

def get_font(font_name="arialbd.ttf", size=32):
    font_paths = [
        Path(f"C:/Windows/Fonts/{font_name}"),
        Path(f"C:/Windows/Fonts/{font_name.lower()}"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for p in font_paths:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()

def create_dialogue_overlay(shot_idx: int, text: str, output_path: Path, width=1920, height=1080):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Determine speaker badge label
    # Shots 12, 13, 14, 15, 21 represent Chatbot comparison
    if shot_idx in (12, 13, 14, 15, 21):
        speaker_label = "BÉ BYTE (CHATBOT)"
    else:
        speaker_label = "BÉ BYTE (AI AGENT)"

    # Chat box geometry
    box_w = 1600
    box_h = 126
    box_x = (width - box_w) // 2
    box_y = height - box_h - 45

    # 1. Rounded dark container backplate (88% opacity)
    draw.rounded_rectangle(
        [(box_x, box_y), (box_x + box_w, box_y + box_h)],
        radius=16,
        fill=(11, 15, 23, 225),
        outline=(0, 218, 245, 130),
        width=2
    )

    # 2. Speaker Pill Badge at top-left
    font_badge = get_font("arialbd.ttf", 20)
    badge_pad_x, badge_pad_y = 16, 6
    bbox = draw.textbbox((0, 0), speaker_label, font=font_badge)
    bw = (bbox[2] - bbox[0]) + badge_pad_x * 2
    bh = (bbox[3] - bbox[1]) + badge_pad_y * 2
    badge_x = box_x + 24
    badge_y = box_y - 16

    draw.rounded_rectangle(
        [(badge_x, badge_y), (badge_x + bw, badge_y + bh)],
        radius=8,
        fill=(0, 220, 250, 255)
    )
    draw.text((badge_x + badge_pad_x, badge_y + badge_pad_y - 2), speaker_label, fill=(10, 22, 35, 255), font=font_badge)

    # 3. Subtitle Dialogue Text (crisp white bold, centered)
    font_sub = get_font("arialbd.ttf", 32)
    words = text.strip().split()
    lines = []
    cur = []
    for w in words:
        test = " ".join(cur + [w])
        if draw.textbbox((0, 0), test, font=font_sub)[2] < (box_w - 70):
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))

    line_h = 42
    text_y = box_y + (box_h - len(lines) * line_h) // 2 + 4
    for line in lines:
        tbox = draw.textbbox((0, 0), line, font=font_sub)
        tx = (width - (tbox[2] - tbox[0])) // 2
        # Subtle drop shadow for maximum cinema legibility
        draw.text((tx + 2, text_y + 2), line, fill=(0, 0, 0, 210), font=font_sub)
        draw.text((tx, text_y), line, fill=(255, 255, 255, 255), font=font_sub)
        text_y += line_h

    img.save(output_path, "PNG")

def main():
    print(f"Connecting to DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT display_order, narrator_text FROM scene WHERE video_id = ? ORDER BY display_order",
        (VIDEO_ID,)
    )
    scenes = c.fetchall()
    conn.close()

    print(f"Generating 104 chatbox overlays in: {OVERLAYS_DIR}")
    for order, text in scenes:
        out_png = OVERLAYS_DIR / f"overlay_{order:03d}.png"
        create_dialogue_overlay(order, text, out_png)
        if order % 20 == 0 or order == len(scenes):
            print(f"  [Overlay] Generated {order}/{len(scenes)}: {out_png.name}")

    print("All 104 overlays generated successfully!")

if __name__ == "__main__":
    main()

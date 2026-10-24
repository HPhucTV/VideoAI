#!/usr/bin/env python3
"""
Generate sleek dialogue chatbox overlays for all 100 shots of Gemini Agent project.
Standards compliant with CINEMATIC_STANDARDS.md Section 11 & AGENTS.md Rule 10:
- Box width: 1600px, height: 126px, centered horizontally at x=160, bottom offset y=909.
- Rounded dark translucent container (88% alpha) with cyan neon 2px outline.
- Speaker pill badge: BÉ BYTE (AI AGENT) or BÉ BYTE (CHATBOT) for chatbot comparison shots.
- Crisp white bold typography centered in the container.
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-gemini-ai-agent-build"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
OVERLAYS_DIR = OUTPUT_DIR / "dialogue_overlays"
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)

MANIFEST_PATH = OUTPUT_DIR / "audio_manifest_100_shots.json"


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
    # Shots 2, 3, 4 compare passive chatbot
    if shot_idx in (2, 3, 4):
        speaker_label = "BÉ BYTE (CHATBOT)"
        badge_color = (255, 90, 95, 255)  # Soft red badge for passive chatbot
    else:
        speaker_label = "BÉ BYTE (AI AGENT)"
        badge_color = (0, 220, 250, 255)  # Cyan neon badge for active agent

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
        fill=badge_color
    )
    # Badge text
    draw.text(
        (badge_x + badge_pad_x, badge_y + badge_pad_y - 2),
        speaker_label,
        font=font_badge,
        fill=(10, 20, 30, 255)
    )

    # 3. Main Dialogue Typography (Crisp white bold with drop shadow)
    font_text = get_font("arialbd.ttf", 32)

    # Auto wrap if too long for 1500px inner width
    max_text_w = 1520
    words = text.split()
    lines = []
    cur_line = []
    for w in words:
        test_line = " ".join(cur_line + [w])
        tb = draw.textbbox((0, 0), test_line, font=font_text)
        if (tb[2] - tb[0]) > max_text_w and cur_line:
            lines.append(" ".join(cur_line))
            cur_line = [w]
        else:
            cur_line.append(w)
    if cur_line:
        lines.append(" ".join(cur_line))

    # Calculate vertical centering
    line_h = 38
    total_h = len(lines) * line_h
    start_y = box_y + (box_h - total_h) // 2 + 6

    for i, l in enumerate(lines):
        tb = draw.textbbox((0, 0), l, font=font_text)
        lw = tb[2] - tb[0]
        lx = box_x + (box_w - lw) // 2
        ly = start_y + i * line_h

        # Shadow
        draw.text((lx + 2, ly + 2), l, font=font_text, fill=(0, 0, 0, 200))
        # Main text
        draw.text((lx, ly), l, font=font_text, fill=(255, 255, 255, 255))

    img.save(output_path, "PNG")


def main():
    if not MANIFEST_PATH.exists():
        print(f"Error: {MANIFEST_PATH} not found.")
        sys.exit(1)

    manifest_data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    shots = manifest_data.get("shots", [])
    print(f"Generating Cyber Chatbox Overlays for {len(shots)} shots...")

    for shot in shots:
        num = shot["shot_num"]
        dialogue = shot["dialogue"]
        out_file = OVERLAYS_DIR / f"overlay_{num:03d}.png"
        create_dialogue_overlay(num, dialogue, out_file)

    print(f"Successfully generated all {len(shots)} dialogue overlays in: {OVERLAYS_DIR}")


if __name__ == "__main__":
    main()

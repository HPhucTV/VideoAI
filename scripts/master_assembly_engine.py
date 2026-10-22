"""
scripts/master_assembly_engine.py
OmniVideo Studio — Master Assembly & 3D Thumbnail Engine (Cổng 6)

Implements cinematic subtitle overlays, YouTube SRT generator, and high-CTR 3D thumbnails
per Cinematic Grade Mandate (AGENTS.md & docs/CINEMATIC_STANDARDS.md).
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont


def get_font(size: int = 32, name: str = "arialbd.ttf") -> ImageFont.ImageFont:
    """
    Retrieve TrueType bold font for Vietnamese typography with system fallbacks.
    """
    if isinstance(size, str):
        name, size = size, 32

    candidate_paths = [
        Path(f"C:/Windows/Fonts/{name}"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]

    for p in candidate_paths:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue

    # Attempt direct font name lookup across system font paths
    try:
        return ImageFont.truetype(name, size)
    except Exception:
        pass

    return ImageFont.load_default()


def format_srt_time(seconds: float) -> str:
    """
    Format floating seconds into standard SRT timestamp 'HH:MM:SS,mmm'.
    Handles millisecond rounding without precision overflow.
    """
    total_millis = max(0, int(round(seconds * 1000)))
    millis = total_millis % 1000
    total_sec = total_millis // 1000
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def generate_srt_file(shots: List[Dict[str, Any]], out_path: Path, intro_offset: float = 2.0) -> Path:
    """
    Generate YouTube-compliant UTF-8 SRT subtitle file from shots manifest.
    Each shot's duration is respected with seamless sequential timeline.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    current_time = float(intro_offset)

    for idx, s in enumerate(shots, 1):
        dur = float(s.get("duration", s.get("audio_duration", 4.0)))
        start_t = current_time
        end_t = current_time + dur
        dialogue = str(s.get("dialogue") or s.get("text") or s.get("rawText") or "").strip()

        lines.append(f"{idx}\n{format_srt_time(start_t)} --> {format_srt_time(end_t)}\n{dialogue}\n")
        current_time = end_t

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def generate_cyber_chatbox_overlay(speaker: str, text: str, out_path: Path) -> Path:
    """
    Render 1920x1080 transparent overlay PNG with standard Cyber Chatbox subtitle.

    Standard Dimensions (AGENTS.md Rule 10):
    - Canvas: 1920x1080 RGBA transparent.
    - Chatbox width: 1600px, height: 125px.
    - Horizontally centered: x = (1920 - 1600) // 2 = 160.
    - Vertical placement: y = 1080 - 125 - 45 = 910.
    - Corner radius: 16px.
    - Background: Semi-transparent glass rgba(11, 15, 23, 225).
    - Outline: Cyan Neon rgba(0, 218, 245, 255) with 2px stroke.
    - Speaker Pill Badge: badge_x = box_x + 24 (184), badge_y = box_y - 16 (894),
      radius 8px, Cyan Neon background, high contrast bold dark text.
    - Dialogue Typography: Arial/Segoe UI Bold size 30, crisp white with subtle drop shadow.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1920, 1080
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    box_w = 1600
    box_h = 125
    box_x = (width - box_w) // 2  # 160
    box_y = height - box_h - 45   # 910
    radius = 16

    # 1. Glassmorphic Chatbox Backplate
    draw.rounded_rectangle(
        [(box_x, box_y), (box_x + box_w, box_y + box_h)],
        radius=radius,
        fill=(11, 15, 23, 225),
        outline=(0, 218, 245, 255),
        width=2,
    )

    # 2. Speaker Pill Badge
    speaker_label = (speaker or "BÉ BYTE (AI AGENT)").strip().upper()
    font_badge = get_font(size=18, name="arialbd.ttf")

    tbbox = draw.textbbox((0, 0), speaker_label, font=font_badge)
    text_w = tbbox[2] - tbbox[0]
    text_h = tbbox[3] - tbbox[1]

    pad_x = 16
    badge_w = text_w + pad_x * 2
    badge_h = 32
    badge_x = box_x + 24  # 184
    badge_y = box_y - 16  # 894

    draw.rounded_rectangle(
        [(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)],
        radius=8,
        fill=(0, 218, 245, 255),
    )

    badge_text_x = badge_x + pad_x
    badge_text_y = badge_y + (badge_h - text_h) // 2 - tbbox[1]
    draw.text(
        (badge_text_x, badge_text_y),
        speaker_label,
        fill=(11, 15, 23, 255),
        font=font_badge,
    )

    # 3. Subtitle Dialogue Typography (Size 30 Bold, Centered, Drop Shadow)
    font_sub = get_font(size=30, name="arialbd.ttf")
    words = text.strip().split()
    max_line_w = box_w - 80

    lines = []
    current_line_words = []
    for w in words:
        candidate = " ".join(current_line_words + [w])
        cand_bbox = draw.textbbox((0, 0), candidate, font=font_sub)
        cand_w = cand_bbox[2] - cand_bbox[0]
        if cand_w <= max_line_w:
            current_line_words.append(w)
        else:
            if current_line_words:
                lines.append(" ".join(current_line_words))
            current_line_words = [w]
    if current_line_words:
        lines.append(" ".join(current_line_words))
    if not lines:
        lines = [""]

    line_height = 38
    total_text_h = len(lines) * line_height
    start_y = box_y + (box_h - total_text_h) // 2

    for idx, line in enumerate(lines):
        line_bbox = draw.textbbox((0, 0), line, font=font_sub)
        line_w = line_bbox[2] - line_bbox[0]
        tx = box_x + (box_w - line_w) // 2
        ty = start_y + idx * line_height

        # Soft drop shadow for legibility over motion
        draw.text((tx + 2, ty + 2), line, fill=(0, 0, 0, 255), font=font_sub)
        # Crisp White Subtitle
        draw.text((tx, ty), line, fill=(255, 255, 255, 255), font=font_sub)

    img.save(out_path, format="PNG")
    return out_path


def generate_3d_thumbnail(
    hero_frame: Optional[Path],
    hook_title: str,
    out_path: Path,
    subtitle_pill: str = "KỶ NGUYÊN TỰ CHỦ 2026",
) -> Path:
    """
    Generate High-CTR Cinematic 3D Thumbnail (AGENTS.md Rule 11).
    - Resizes hero frame to 1920x1080 (or creates high-tech dark background if missing).
    - Renders hook_title with font size 80-95, thick black stroke outline (5-7px), neon cyan text.
    - Exports to JPEG quality 95.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    width, height = 1920, 1080

    if hero_frame and Path(hero_frame).exists():
        hero_img = Image.open(hero_frame).convert("RGBA")
        img = hero_img.resize((width, height), Image.Resampling.LANCZOS)
        # Add subtle top and bottom dark gradient overlays for maximum contrast
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        # Bottom dark gradient plate for title
        draw_ov.rectangle([(0, 600), (width, height)], fill=(8, 12, 22, 180))
        # Top gradient plate for branding
        draw_ov.rectangle([(0, 0), (width, 180)], fill=(8, 12, 22, 140))
        img = Image.alpha_composite(img, overlay)
    else:
        # High-tech dark cyber background
        img = Image.new("RGBA", (width, height), (8, 14, 26, 255))
        draw_bg = ImageDraw.Draw(img)

        # Subtle cyber grid
        for x in range(0, width, 60):
            draw_bg.line([(x, 0), (x, height)], fill=(0, 180, 216, 30), width=1)
        for y in range(0, height, 60):
            draw_bg.line([(0, y), (width, y)], fill=(0, 180, 216, 30), width=1)

        # Holographic glow frame
        draw_bg.rounded_rectangle(
            [(120, 100), (width - 120, height - 100)],
            radius=24,
            outline=(0, 229, 255, 60),
            width=3,
        )

    draw = ImageDraw.Draw(img)

    # 1. Branding Pill Badge (Top Left / Above Title)
    if subtitle_pill:
        font_pill = get_font(size=26, name="arialbd.ttf")
        pill_text = subtitle_pill.upper().strip()
        pbbox = draw.textbbox((0, 0), pill_text, font=font_pill)
        pw = pbbox[2] - pbbox[0] + 32
        ph = 44
        px = (width - pw) // 2
        py = 720

        draw.rounded_rectangle(
            [(px, py), (px + pw, py + ph)],
            radius=12,
            fill=(0, 229, 255, 230),
        )
        draw.text(
            (px + 16, py + 8),
            pill_text,
            fill=(10, 20, 35, 255),
            font=font_pill,
        )

    # 2. Main Hook Title (High-CTR 80-95px, 6px black stroke, Neon Cyan)
    font_title = get_font(size=88, name="arialbd.ttf")
    words = hook_title.strip().split()
    max_title_w = 1700

    title_lines = []
    cur_line = []
    for w in words:
        test = " ".join(cur_line + [w])
        t_w = draw.textbbox((0, 0), test, font=font_title)[2] - draw.textbbox((0, 0), test, font=font_title)[0]
        if t_w <= max_title_w:
            cur_line.append(w)
        else:
            if cur_line:
                title_lines.append(" ".join(cur_line))
            cur_line = [w]
    if cur_line:
        title_lines.append(" ".join(cur_line))
    if not title_lines:
        title_lines = [hook_title]

    line_spacing = 105
    total_h = len(title_lines) * line_spacing
    title_start_y = 790 if subtitle_pill else (height - total_h) // 2

    for i, line in enumerate(title_lines):
        tbbox = draw.textbbox((0, 0), line, font=font_title)
        lw = tbbox[2] - tbbox[0]
        tx = (width - lw) // 2
        ty = title_start_y + i * line_spacing

        draw.text(
            (tx, ty),
            line,
            fill=(0, 229, 255, 255),
            font=font_title,
            stroke_width=6,
            stroke_fill=(0, 0, 0, 255),
        )

    # 3. Export to JPEG quality 95
    img.convert("RGB").save(out_path, "JPEG", quality=95)
    return out_path


if __name__ == "__main__":
    print("Master Assembly Engine ready.")

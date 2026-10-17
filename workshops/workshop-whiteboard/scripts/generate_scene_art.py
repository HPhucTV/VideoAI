#!/usr/bin/env python3
"""
OMNIVIDEO STUDIO - WORKSHOP 3 (WHITEBOARD)
High-Aesthetic Storyboard & Scene Artwork Generator

Solves the single-image repetition problem by generating unique, bespoke,
1920x1080 3-panel graphic novel / whiteboard sketches for EVERY scene:
- Notion / Manga / Comic line art style on warm creamy antique paper (#F5EBD7)
- Deep charcoal linework (#2D3748)
- Elegant chapter header & typography badges
- Precise alignment with scene annotation regions (Left, Center, Right panels)
- Rich thematic sketches: characters, environments, emotional beats, quote banners
- Supports local procedural synthesis + optional AI image integration
"""

import sys
import re
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Canvas & Palette Constants
CANVAS_W = 1920
CANVAS_H = 1080
COLOR_BG = (245, 235, 215)          # Warm cream paper (#F5EBD7)
COLOR_INK = (45, 55, 72)            # Deep charcoal slate (#2D3748)
COLOR_INK_MUTED = (113, 128, 150)   # Slate gray (#718096)
COLOR_INK_LIGHT = (160, 174, 192)   # Light slate (#A0AEC0)
COLOR_BORDER = (196, 181, 157)      # Aged paper contour (#C4B59D)
COLOR_PANEL_BG = (250, 243, 230)    # Soft panel highlight (#FAF3E6)
COLOR_ACCENT = (197, 120, 75)       # Terracotta ink accent
COLOR_CYAN_INK = (43, 114, 133)     # Subtle petrol cyan ink

# Windows System Fonts
def get_font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    candidates = []
    if serif:
        candidates = ["timesbd.ttf" if bold else "times.ttf", "georgiab.ttf" if bold else "georgia.ttf"]
    else:
        candidates = ["segoeuib.ttf" if bold else "segoeui.ttf", "arialbd.ttf" if bold else "arial.ttf", "tahomabd.ttf" if bold else "tahoma.ttf"]

    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

def draw_rounded_rect(draw: ImageDraw.ImageDraw, box: tuple, radius: int, outline=None, width: int = 1, fill=None):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, outline=outline, width=width, fill=fill)

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, max_lines: int = 3) -> list[str]:
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = font.getbbox(test_line)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            if len(lines) >= max_lines - 1:
                break
    if current_line and len(lines) < max_lines:
        lines.append(" ".join(current_line))
    return lines

def extract_punchy_quote(text: str) -> tuple[str, str]:
    """
    Extracts a concise, dramatic dialogue quote and speaker from text.
    Returns: (quote_string, speaker_name)
    """
    if not text:
        return ("", "")

    # Look for quoted dialogue inside "..."
    matches = re.findall(r'["“]([^"”]{15,120})["”]', text)
    if matches:
        chosen = matches[0].strip()
        # Find speaker preceding the quote
        speaker = ""
        pre_match = text[:text.find(chosen)]
        spk_candidates = ["Lục Cảnh Thâm", "Thẩm Nhược Hy", "Cảnh Thâm", "Nhược Hy", "Triệu Bích Nguyệt", "Lục Lão Phu Nhân", "Giang Thừa", "Thẩm Minh Viễn"]
        for spk in spk_candidates:
            if spk.lower() in pre_match[-80:].lower():
                speaker = spk
                break
        return (chosen, speaker)

    # Fallback to first punchy sentence
    sentences = [s.strip() for s in re.split(r'[\.\?\!]\s+', text) if len(s.strip()) > 15]
    if sentences:
        s0 = sentences[0]
        if len(s0) > 100:
            s0 = s0[:95] + "..."
        return (s0, "")

    return (text[:90], "")

# ─────────────────────────────────────────────────────────────────────────────
# PROCEDURAL SKETCH DRAWING PRIMITIVES
# ─────────────────────────────────────────────────────────────────────────────

def draw_rain(draw: ImageDraw.ImageDraw, box: tuple, density: int = 40):
    x0, y0, x1, y1 = box
    import random
    rng = random.Random(box[0] * 37 + box[1])
    for _ in range(density):
        rx = rng.randint(x0 + 10, x1 - 10)
        ry = rng.randint(y0 + 20, y1 - 40)
        len_r = rng.randint(25, 60)
        draw.line([(rx, ry), (rx - 15, ry + len_r)], fill=COLOR_INK_MUTED, width=1)

def draw_city_skyline(draw: ImageDraw.ImageDraw, box: tuple, baseline_y: int):
    x0, y0, x1, y1 = box
    buildings = [
        (0.05, 0.20, 180), (0.22, 0.35, 260), (0.37, 0.52, 340),
        (0.54, 0.68, 220), (0.70, 0.82, 300), (0.84, 0.95, 190)
    ]
    w = x1 - x0
    for rel_x1, rel_x2, bh in buildings:
        bx0 = int(x0 + rel_x1 * w)
        bx1 = int(x0 + rel_x2 * w)
        by0 = baseline_y - bh
        draw.rectangle([bx0, by0, bx1, baseline_y], outline=COLOR_INK, width=2, fill=COLOR_BG)
        # Windows grid
        for wy in range(by0 + 15, baseline_y - 15, 25):
            for wx in range(bx0 + 10, bx1 - 10, 18):
                draw.rectangle([wx, wy, wx + 6, wy + 12], outline=COLOR_INK_MUTED, width=1)

def draw_car_maybach(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    w = int(220 * scale)
    h = int(70 * scale)
    body_pts = [
        (cx - w, cy + h // 3),
        (cx - w + 30, cy - h // 4),
        (cx - w // 2, cy - h // 2),
        (cx - w // 6, cy - h),
        (cx + w // 3, cy - h),
        (cx + w - 40, cy - h // 4),
        (cx + w, cy + h // 3),
        (cx + w - 20, cy + h),
        (cx - w + 20, cy + h),
    ]
    draw.polygon(body_pts, outline=COLOR_INK, fill=COLOR_PANEL_BG)
    draw.line(body_pts + [body_pts[0]], fill=COLOR_INK, width=3)
    # Wheels
    r_wheel = int(26 * scale)
    draw.ellipse([cx - w + 50 - r_wheel, cy + h - r_wheel, cx - w + 50 + r_wheel, cy + h + r_wheel], outline=COLOR_INK, width=4, fill=COLOR_BG)
    draw.ellipse([cx + w - 70 - r_wheel, cy + h - r_wheel, cx + w - 70 + r_wheel, cy + h + r_wheel], outline=COLOR_INK, width=4, fill=COLOR_BG)
    # Headlights beam
    draw.polygon([(cx - w, cy + h // 3), (cx - w - 80, cy), (cx - w - 90, cy + h), (cx - w, cy + h)], fill=None, outline=COLOR_INK_LIGHT)

def draw_figure_silhouette(draw: ImageDraw.ImageDraw, cx: int, cy: int, is_male: bool = True, pose: str = "standing"):
    # Head
    draw.ellipse([cx - 20, cy - 140, cx + 20, cy - 95], outline=COLOR_INK, width=3, fill=COLOR_INK if is_male else COLOR_BG)
    if not is_male:
        draw.arc([cx - 30, cy - 135, cx + 30, cy - 70], start=30, end=240, fill=COLOR_INK, width=3)
        draw.arc([cx - 25, cy - 100, cx + 25, cy - 50], start=60, end=280, fill=COLOR_INK, width=2)
    # Neck & Shoulders
    draw.line([(cx, cy - 95), (cx, cy - 80)], fill=COLOR_INK, width=3)
    shoulder_w = 48 if is_male else 36
    draw.line([(cx - shoulder_w, cy - 70), (cx + shoulder_w, cy - 70)], fill=COLOR_INK, width=3)
    # Torso (Suit vs Dress)
    if is_male:
        draw.polygon([(cx - shoulder_w, cy - 70), (cx + shoulder_w, cy - 70),
                      (cx + 35, cy + 20), (cx - 35, cy + 20)], outline=COLOR_INK, width=3, fill=COLOR_PANEL_BG)
        draw.polygon([(cx - 6, cy - 70), (cx + 6, cy - 70), (cx + 9, cy - 20), (cx, cy), (cx - 9, cy - 20)], fill=COLOR_INK)
        draw.line([(cx - 20, cy + 20), (cx - 20, cy + 130)], fill=COLOR_INK, width=4)
        draw.line([(cx + 20, cy + 20), (cx + 20, cy + 130)], fill=COLOR_INK, width=4)
    else:
        draw.polygon([(cx - shoulder_w, cy - 70), (cx + shoulder_w, cy - 70),
                      (cx + 24, cy - 10), (cx + 50, cy + 80),
                      (cx - 50, cy + 80), (cx - 24, cy - 10)], outline=COLOR_INK, width=3, fill=COLOR_PANEL_BG)
        draw.line([(cx - 15, cy + 80), (cx - 15, cy + 130)], fill=COLOR_INK, width=3)
        draw.line([(cx + 15, cy + 80), (cx + 15, cy + 130)], fill=COLOR_INK, width=3)

def draw_hands_touching(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    # Left hand reaching right
    draw.arc([cx - 140, cy - 50, cx - 20, cy + 50], start=300, end=80, fill=COLOR_INK, width=3)
    draw.line([(cx - 120, cy), (cx - 25, cy - 10)], fill=COLOR_INK, width=4)
    draw.ellipse([cx - 25, cy - 15, cx - 10, cy - 5], outline=COLOR_INK, width=2, fill=COLOR_PANEL_BG)
    # Right hand reaching left
    draw.arc([cx + 20, cy - 50, cx + 140, cy + 50], start=100, end=240, fill=COLOR_INK, width=3)
    draw.line([(cx + 120, cy), (cx + 25, cy - 10)], fill=COLOR_INK, width=4)
    draw.ellipse([cx + 10, cy - 15, cx + 25, cy - 5], outline=COLOR_INK, width=2, fill=COLOR_PANEL_BG)
    # Miraculous spark / glowing warmth rays between fingers
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        r1, r2 = 18, 38
        p1 = (int(cx + r1 * math.cos(rad)), int(cy - 10 + r1 * math.sin(rad)))
        p2 = (int(cx + r2 * math.cos(rad)), int(cy - 10 + r2 * math.sin(rad)))
        draw.line([p1, p2], fill=COLOR_ACCENT, width=2)
    draw.ellipse([cx - 8, cy - 18, cx + 8, cy - 2], fill=COLOR_ACCENT)

def draw_contract_scroll(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    w, h = 170, 230
    draw_rounded_rect(draw, (cx - w // 2 + 10, cy - h // 2 + 10, cx + w // 2 + 10, cy + h // 2 + 10), radius=6, outline=COLOR_INK_MUTED, fill=COLOR_PANEL_BG, width=1)
    draw_rounded_rect(draw, (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2), radius=6, outline=COLOR_INK, fill=COLOR_BG, width=3)
    # Title on contract
    font_ct = get_font(12, bold=True)
    draw.text((cx - w // 2 + 20, cy - h // 2 + 16), "HỢP ĐỒNG HÔN NHÂN", font=font_ct, fill=COLOR_INK)
    draw.line([(cx - w // 2 + 18, cy - h // 2 + 34), (cx + w // 2 - 18, cy - h // 2 + 34)], fill=COLOR_INK, width=2)
    # Contract lines
    for ly in range(cy - h // 2 + 48, cy + h // 2 - 55, 20):
        draw.line([(cx - w // 2 + 20, ly), (cx + w // 2 - 20, ly)], fill=COLOR_INK_MUTED, width=2)
    # Wax seal / 100 Billion Stamp
    draw.ellipse([cx + 12, cy + 28, cx + 68, cy + 84], outline=COLOR_ACCENT, width=3, fill=COLOR_PANEL_BG)
    font_stamp = get_font(13, bold=True)
    draw.text((cx + 20, cy + 46), "100 TỶ", font=font_stamp, fill=COLOR_ACCENT)
    # Fountain pen
    pen_start = (cx + 70, cy - 40)
    pen_tip = (cx + 20, cy + 15)
    draw.line([pen_start, pen_tip], fill=COLOR_INK, width=4)
    draw.polygon([(pen_tip[0], pen_tip[1]), (pen_tip[0] + 8, pen_tip[1] - 12), (pen_tip[0] + 14, pen_tip[1] - 6)], fill=COLOR_INK)

def draw_contract_review(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    # Scale of Justice & Document
    draw.line([(cx, cy - 80), (cx, cy + 60)], fill=COLOR_INK, width=4)
    draw.line([(cx - 80, cy - 60), (cx + 80, cy - 60)], fill=COLOR_INK, width=3)
    # Left pan (Freedom)
    draw.line([(cx - 80, cy - 60), (cx - 105, cy - 10)], fill=COLOR_INK_MUTED, width=1)
    draw.line([(cx - 80, cy - 60), (cx - 55, cy - 10)], fill=COLOR_INK_MUTED, width=1)
    draw.arc([cx - 110, cy - 20, cx - 50, cy + 10], start=0, end=180, fill=COLOR_INK, width=3)
    # Right pan (100 Billion)
    draw.line([(cx + 80, cy - 60), (cx + 55, cy + 20)], fill=COLOR_INK_MUTED, width=1)
    draw.line([(cx + 80, cy - 60), (cx + 105, cy + 20)], fill=COLOR_INK_MUTED, width=1)
    draw.arc([cx + 50, cy + 10, cx + 110, cy + 40], start=0, end=180, fill=COLOR_INK, width=3)
    # Base
    draw.polygon([(cx - 30, cy + 60), (cx + 30, cy + 60), (cx + 45, cy + 80), (cx - 45, cy + 80)], fill=COLOR_INK)
    # Magnifying glass on side
    draw.ellipse([cx - 140, cy + 10, cx - 80, cy + 70], outline=COLOR_ACCENT, width=3, fill=COLOR_PANEL_BG)
    draw.line([(cx - 95, cy + 55), (cx - 70, cy + 95)], fill=COLOR_ACCENT, width=4)

def draw_signing_ceremony(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    # Two Hands & Two Signatures
    draw.rectangle([cx - 140, cy - 40, cx + 140, cy + 70], outline=COLOR_INK, width=2, fill=COLOR_BG)
    font_lbl = get_font(12, bold=True)
    draw.text((cx - 120, cy - 30), "BÊN A: LỤC CẢNH THÂM", font=font_lbl, fill=COLOR_INK)
    draw.text((cx + 10, cy - 30), "BÊN B: THẨM NHƯỢC HY", font=font_lbl, fill=COLOR_INK)
    # Stylized signatures
    draw.line([(cx - 120, cy + 30), (cx - 20, cy + 30)], fill=COLOR_INK_MUTED, width=1)
    draw.line([(cx + 10, cy + 30), (cx + 120, cy + 30)], fill=COLOR_INK_MUTED, width=1)
    # Script signatures
    draw.arc([cx - 110, cy + 5, cx - 60, cy + 30], start=180, end=360, fill=COLOR_INK, width=2)
    draw.arc([cx - 80, cy, cx - 30, cy + 35], start=0, end=270, fill=COLOR_INK, width=2)
    draw.arc([cx + 20, cy + 8, cx + 70, cy + 28], start=200, end=360, fill=COLOR_CYAN_INK, width=2)
    draw.arc([cx + 50, cy, cx + 100, cy + 35], start=0, end=270, fill=COLOR_CYAN_INK, width=2)
    # Interlocking wedding bands above
    r = 28
    draw.ellipse([cx - r - 8, cy - 100, cx + r - 8, cy - 100 + r * 2], outline=COLOR_ACCENT, width=3)
    draw.ellipse([cx - r + 16, cy - 100, cx + r + 16, cy - 100 + r * 2], outline=COLOR_ACCENT, width=3)

def draw_mansion_chandelier(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    draw.line([(cx, cy - 100), (cx, cy - 40)], fill=COLOR_INK, width=3)
    draw.ellipse([cx - 70, cy - 45, cx + 70, cy - 25], outline=COLOR_INK, width=2)
    draw.ellipse([cx - 45, cy - 25, cx + 45, cy - 10], outline=COLOR_INK, width=2)
    for px in [-60, -35, 0, 35, 60]:
        draw.line([(cx + px, cy - 35), (cx + px, cy + 10)], fill=COLOR_INK_LIGHT, width=1)
        draw.polygon([(cx + px, cy + 22), (cx + px - 4, cy + 10), (cx + px + 4, cy + 10)], fill=COLOR_INK)
    draw.line([(cx - 160, cy - 60), (cx - 160, cy + 140)], fill=COLOR_INK, width=4)
    draw.line([(cx + 160, cy - 60), (cx + 160, cy + 140)], fill=COLOR_INK, width=4)
    draw.arc([cx - 160, cy - 140, cx + 160, cy + 20], start=180, end=360, fill=COLOR_INK, width=3)

def draw_tea_and_moon(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    draw.ellipse([cx + 60, cy - 120, cx + 150, cy - 30], outline=COLOR_INK, width=3, fill=COLOR_PANEL_BG)
    draw.ellipse([cx + 90, cy - 130, cx + 170, cy - 20], fill=COLOR_BG, outline=None)
    draw.ellipse([cx - 70, cy + 40, cx + 70, cy + 70], outline=COLOR_INK, width=3, fill=COLOR_PANEL_BG)
    draw.polygon([(cx - 50, cy), (cx + 50, cy), (cx + 38, cy + 45), (cx - 38, cy + 45)], outline=COLOR_INK, width=3, fill=COLOR_BG)
    draw.arc([cx + 42, cy + 5, cx + 72, cy + 35], start=270, end=90, fill=COLOR_INK, width=3)
    for offset in [-20, 0, 20]:
        draw.arc([cx + offset - 10, cy - 50, cx + offset + 10, cy - 10], start=180, end=360, fill=COLOR_INK_MUTED, width=2)
        draw.arc([cx + offset - 10, cy - 80, cx + offset + 10, cy - 40], start=0, end=180, fill=COLOR_INK_MUTED, width=2)

def draw_conspiracy_chess(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    draw.line([(cx - 130, cy + 80), (cx + 130, cy + 80)], fill=COLOR_INK, width=3)
    pts = [(cx - 130, cy - 70), (cx - 60, cy - 40), (cx - 10, cy - 80), (cx + 50, cy + 20), (cx + 120, cy + 70)]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=COLOR_ACCENT, width=3)
    draw.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 14, pts[-1][1] - 8), (pts[-1][0] - 8, pts[-1][1] - 16)], fill=COLOR_ACCENT)
    draw.ellipse([cx - 40, cy + 40, cx - 10, cy + 70], outline=COLOR_INK, width=3, fill=COLOR_PANEL_BG)
    draw.line([(cx - 25, cy + 30), (cx - 25, cy + 15)], fill=COLOR_INK, width=3)
    draw.line([(cx - 32, cy + 22), (cx - 18, cy + 22)], fill=COLOR_INK, width=3)

def draw_wedding_rings_moon(draw: ImageDraw.ImageDraw, cx: int, cy: int):
    r = 45
    draw.ellipse([cx - r - 15, cy - r, cx + r - 15, cy + r], outline=COLOR_INK, width=4)
    draw.ellipse([cx - r + 25, cy - r, cx + r + 25, cy + r], outline=COLOR_INK, width=4)
    gem_pts = [(cx - 15, cy - r - 25), (cx - 28, cy - r - 10), (cx - 2, cy - r - 10)]
    draw.polygon(gem_pts, outline=COLOR_INK, width=3, fill=COLOR_PANEL_BG)
    for angle in [45, 90, 135, 225, 270, 315]:
        rad = math.radians(angle)
        draw.line([(int(cx - 15 + 28 * math.cos(rad)), int(cy - r - 15 + 28 * math.sin(rad))),
                   (int(cx - 15 + 44 * math.cos(rad)), int(cy - r - 15 + 44 * math.sin(rad)))], fill=COLOR_ACCENT, width=2)

# ─────────────────────────────────────────────────────────────────────────────
# PANEL ARTWORK SELECTION LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def render_panel_artwork(draw: ImageDraw.ImageDraw, panel_box: tuple, elem: dict, scene_id: str, beat_idx: int):
    x0, y0, x1, y1 = panel_box
    cx = (x0 + x1) // 2
    art_cy = y0 + 380

    vis = elem.get("visual") or {}
    label = (elem.get("label") or vis.get("label") or "").lower()
    headline = (elem.get("headline") or vis.get("headline") or "").lower()
    subtitle = (elem.get("subtitle") or elem.get("rawText") or "").lower()

    # Match against label first for high precision
    def match_kw(kw_list):
        return any(k in label for k in kw_list) or any(k in headline for k in kw_list)

    if match_kw(["chạy dưới mưa", "trước cổng bệnh viện", "viện phí", "cấp cứu"]):
        draw_city_skyline(draw, (x0 + 20, y0 + 100, x1 - 20, y1 - 200), baseline_y=art_cy + 120)
        draw_rain(draw, (x0 + 10, y0 + 90, x1 - 10, y1 - 180), density=45)
        draw_figure_silhouette(draw, cx - 40, art_cy + 40, is_male=False)
        draw.rectangle([x1 - 80, y0 + 140, x1 - 40, y0 + 180], outline=COLOR_INK, width=2, fill=COLOR_PANEL_BG)
        draw.line([(x1 - 60, y0 + 148), (x1 - 60, y0 + 172)], fill=COLOR_ACCENT, width=4)
        draw.line([(x1 - 72, y0 + 160), (x1 - 48, y0 + 160)], fill=COLOR_ACCENT, width=4)

    elif match_kw(["maybach", "khoang xe", "đau đầu", "mất ngủ", "cơn đau"]):
        draw_city_skyline(draw, (x0 + 20, y0 + 100, x1 - 20, y1 - 200), baseline_y=art_cy + 10)
        draw_car_maybach(draw, cx, art_cy + 70, scale=0.95)
        for r in [30, 55, 80]:
            draw.arc([cx - r, art_cy - 120 - r // 2, cx + r, art_cy - 120 + r // 2], start=200, end=340, fill=COLOR_ACCENT, width=2)

    elif match_kw(["chạm tay", "ấm áp", "tiếp xúc", "bàn tay"]):
        draw_rain(draw, (x0 + 10, y0 + 90, x1 - 10, y1 - 200), density=25)
        draw_hands_touching(draw, cx, art_cy)

    elif match_kw(["tập hợp đồng", "mạ vàng", "bàn làm việc", "tầng 68"]):
        draw_contract_scroll(draw, cx, art_cy)

    elif match_kw(["xem xét", "điều khoản", "tự do", "sức khỏe"]):
        draw_contract_review(draw, cx, art_cy)

    elif match_kw(["ký tên", "đặt bút", "hai chữ ký", "định mệnh"]):
        draw_signing_ceremony(draw, cx, art_cy)

    elif match_kw(["ngự cảnh uyển", "biệt phủ", "đêm tiệc", "xa hoa"]):
        draw_mansion_chandelier(draw, cx, art_cy - 20)
        draw_figure_silhouette(draw, cx - 60, art_cy + 60, is_male=False)
        draw_figure_silhouette(draw, cx + 60, art_cy + 50, is_male=True)

    elif match_kw(["khiêu khích", "triệu bích nguyệt", "mỉa mai", "đối chất"]):
        draw_mansion_chandelier(draw, cx, art_cy - 60)
        draw_figure_silhouette(draw, cx - 70, art_cy + 50, is_male=False)
        draw_figure_silhouette(draw, cx + 70, art_cy + 50, is_male=False)
        draw.line([(cx - 30, art_cy - 20), (cx + 5, art_cy + 10), (cx - 5, art_cy + 40), (cx + 30, art_cy + 70)], fill=COLOR_ACCENT, width=3)

    elif match_kw(["đứng chắn", "dằn mặt", "bảo vệ", "uy lực", "vị thế", "ra mặt"]):
        draw_figure_silhouette(draw, cx + 10, art_cy + 30, is_male=True)
        draw_figure_silhouette(draw, cx - 50, art_cy + 50, is_male=False)
        draw.line([(cx - 20, art_cy - 10), (cx - 70, art_cy + 15)], fill=COLOR_INK, width=5)

    elif match_kw(["ác mộng", "co ro", "hoảng loạn"]):
        # Night shadows & distressed silhouette
        draw.ellipse([cx - 80, art_cy - 120, cx + 80, art_cy + 40], outline=COLOR_INK_MUTED, width=1)
        draw_figure_silhouette(draw, cx, art_cy + 20, is_male=True)
        for r in [40, 70, 100]:
            draw.arc([cx - r, art_cy - 80, cx + r, art_cy + 60], start=180, end=360, fill=COLOR_ACCENT, width=2)

    elif match_kw(["vuốt tóc", "hát ru", "vỗ về", "trà", "thảo mộc", "xoa dịu"]):
        draw_tea_and_moon(draw, cx, art_cy)

    elif match_kw(["ngủ say", "bên cạnh", "nắng sớm", "bình yên"]):
        # Morning sunshine & peaceful crescent
        draw_wedding_rings_moon(draw, cx, art_cy)

    elif match_kw(["âm mưu", "thẩm minh viễn", "sóng ngầm", "cổ phần", "thanh trừng"]):
        draw_conspiracy_chess(draw, cx, art_cy)

    elif match_kw(["tỏ tình", "xé hợp đồng", "cầu hôn", "hôn lễ", "kết thúc", "hạnh phúc", "ánh trăng", "viên mãn"]):
        draw_wedding_rings_moon(draw, cx, art_cy)

    else:
        # Fallback using subtitle keywords
        if any(k in subtitle[:300] for k in ["mưa", "bệnh viện"]):
            draw_rain(draw, (x0 + 10, y0 + 90, x1 - 10, y1 - 180), density=35)
            draw_figure_silhouette(draw, cx, art_cy + 30, is_male=False)
        elif any(k in subtitle[:300] for k in ["hợp đồng", "tiền", "nợ"]):
            draw_contract_review(draw, cx, art_cy)
        elif any(k in subtitle[:300] for k in ["trà", "ngủ", "đêm"]):
            draw_tea_and_moon(draw, cx, art_cy)
        else:
            if beat_idx == 1:
                draw_city_skyline(draw, (x0 + 20, y0 + 100, x1 - 20, y1 - 200), baseline_y=art_cy + 110)
                draw_figure_silhouette(draw, cx, art_cy + 20, is_male=True)
            elif beat_idx == 2:
                draw_contract_review(draw, cx, art_cy)
            else:
                draw_wedding_rings_moon(draw, cx, art_cy)

# ─────────────────────────────────────────────────────────────────────────────
# CORE SCENE ART GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_scene_storyboard(
    scene_id: str,
    scene_badge: str,
    story_title: str,
    elements: list[dict],
    output_path: Path
) -> Path:
    """
    Renders a bespoke 1920x1080 3-panel whiteboard graphic novel storyboard.
    """
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # 1. Subtle Paper Border
    draw.rectangle([12, 12, CANVAS_W - 13, CANVAS_H - 13], outline=COLOR_BORDER, width=2)
    draw.rectangle([18, 18, CANVAS_W - 19, CANVAS_H - 19], outline=COLOR_BORDER, width=1)

    # 2. Master Header & Chapter Badge Ribbon
    badge_clean = scene_badge.upper().strip()
    font_badge = get_font(26, bold=True, serif=True)
    font_subtitle = get_font(14, bold=False, serif=False)

    badge_w = font_badge.getbbox(badge_clean)[2] - font_badge.getbbox(badge_clean)[0]
    badge_x = (CANVAS_W - badge_w) // 2

    # Chapter Ornament Lines
    draw.line([(100, 38), (badge_x - 30, 38)], fill=COLOR_INK, width=2)
    draw.line([(badge_x + badge_w + 30, 38), (CANVAS_W - 100, 38)], fill=COLOR_INK, width=2)
    # Diamond ornaments
    draw.polygon([(badge_x - 22, 38), (badge_x - 16, 32), (badge_x - 10, 38), (badge_x - 16, 44)], fill=COLOR_INK)
    draw.polygon([(badge_x + badge_w + 10, 38), (badge_x + badge_w + 16, 32), (badge_x + badge_w + 22, 38), (badge_x + badge_w + 16, 44)], fill=COLOR_INK)

    draw.text((badge_x, 22), badge_clean, font=font_badge, fill=COLOR_INK)

    # Story Subtitle at very top center
    story_sub = f"OmniVideo Whiteboard Cinema  •  {story_title}"
    sub_w = font_subtitle.getbbox(story_sub)[2] - font_subtitle.getbbox(story_sub)[0]
    draw.text(((CANVAS_W - sub_w) // 2, 54), story_sub, font=font_subtitle, fill=COLOR_INK_MUTED)

    # 3. Three Storyboard Panels
    default_panel_regions = [
        {"x": 100, "y": 80, "width": 550, "height": 920},
        {"x": 680, "y": 80, "width": 550, "height": 920},
        {"x": 1260, "y": 80, "width": 550, "height": 920},
    ]

    font_panel_title = get_font(18, bold=True)
    font_quote = get_font(14, bold=False)
    font_quote_speaker = get_font(12, bold=True)

    for idx, def_reg in enumerate(default_panel_regions):
        elem = elements[idx] if idx < len(elements) else {}
        reg = elem.get("region", def_reg)

        px0 = reg.get("x", def_reg["x"])
        py0 = reg.get("y", def_reg["y"])
        pw = reg.get("width", def_reg["width"])
        ph = reg.get("height", def_reg["height"])
        px1 = px0 + pw
        py1 = py0 + ph

        # Outer Panel Box
        draw_rounded_rect(draw, (px0, py0, px1, py1), radius=14, outline=COLOR_INK, width=3, fill=COLOR_PANEL_BG)
        # Inner fine inset line
        draw_rounded_rect(draw, (px0 + 5, py0 + 5, px1 - 5, py1 - 5), radius=10, outline=COLOR_BORDER, width=1)

        # Panel Header Pill
        label_text = elem.get("label", f"Phân Cảnh {idx + 1}")
        panel_tag = f"[{idx + 1:02d}] {label_text}"
        tag_lines = wrap_text(panel_tag, font_panel_title, max_width=pw - 40, max_lines=2)

        tag_y = py0 + 16
        for line in tag_lines:
            draw.text((px0 + 20, tag_y), line, font=font_panel_title, fill=COLOR_INK)
            tag_y += 24

        draw.line([(px0 + 16, tag_y + 4), (px1 - 16, tag_y + 4)], fill=COLOR_INK_LIGHT, width=1)

        # Render Specific Vector Sketch
        render_panel_artwork(draw, (px0, py0, px1, py1), elem, scene_id, idx + 1)

        # Bottom Quote / Dialogue Banner
        quote_source = elem.get("subtitle", "") or elem.get("rawText", "")
        chosen_quote, speaker_tag = extract_punchy_quote(quote_source)

        if chosen_quote:
            qb_y0 = py1 - 120
            qb_y1 = py1 - 16
            # Quote Scroll Background
            draw_rounded_rect(draw, (px0 + 16, qb_y0, px1 - 16, qb_y1), radius=8, outline=COLOR_INK, width=2, fill=COLOR_BG)
            # Quote icon
            draw.text((px0 + 24, qb_y0 + 6), "“", font=get_font(26, bold=True, serif=True), fill=COLOR_ACCENT)

            wrapped_quote = wrap_text(f'"{chosen_quote}"', font_quote, max_width=pw - 70, max_lines=3)
            qy = qb_y0 + 10
            for ql in wrapped_quote:
                draw.text((px0 + 46, qy), ql, font=font_quote, fill=COLOR_INK)
                qy += 20

            if speaker_tag:
                spk_str = f"— {speaker_tag}"
                spk_w = font_quote_speaker.getbbox(spk_str)[2] - font_quote_speaker.getbbox(spk_str)[0]
                draw.text((px1 - 25 - spk_w, qb_y1 - 20), spk_str, font=font_quote_speaker, fill=COLOR_CYAN_INK)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG", quality=95)
    print(f"[OK] Da tao thanh cong Storyboard doc quyen: {output_path}")
    return output_path


def generate_art_for_job_scenes(job_dir: Path, job_id: str, overwrite: bool = False):
    scenes_dir = job_dir / "scenes"
    if not scenes_dir.exists():
        print(f"[WARN] Khong tim thay thu muc scenes tai: {scenes_dir}")
        return

    scene_folders = sorted([p for p in scenes_dir.iterdir() if p.is_dir() and p.name.startswith("scene-")])
    print(f"[*] Tim thay {len(scene_folders)} phan canh can kiem tra tao art...")

    for sf in scene_folders:
        scene_id = sf.name
        target_png = sf / f"{scene_id}.png"
        ann_path = sf / f"{scene_id}.annotation.json"

        if target_png.exists() and not overwrite:
            print(f"[SKIP] Phân cảnh {scene_id} da co anh ({target_png.name})")
            continue

        if not ann_path.exists():
            print(f"[WARN] Bo qua {scene_id} vi khong co annotation: {ann_path}")
            continue

        with open(ann_path, "r", encoding="utf-8") as f:
            ann_data = json.load(f)

        badge = ann_data.get("badge", f"PHÂN CẢNH {scene_id.replace('scene-', '')}")
        story_basis = ann_data.get("storyBasis", job_id)
        elements = ann_data.get("elements", [])

        generate_scene_storyboard(
            scene_id=scene_id,
            scene_badge=badge,
            story_title=story_basis,
            elements=elements,
            output_path=target_png
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_scene_art.py <job_id_or_job_dir>")
        sys.exit(1)

    target_arg = sys.argv[1]
    p = Path(target_arg)
    if p.is_dir():
        job_dir = p
        job_id = p.name
    else:
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        job_dir = root_dir / "output" / "whiteboard" / target_arg
        job_id = target_arg

    print(f"[*] Bat dau tao art cho Job {job_id} tai {job_dir}...")
    generate_art_for_job_scenes(job_dir, job_id, overwrite=True)

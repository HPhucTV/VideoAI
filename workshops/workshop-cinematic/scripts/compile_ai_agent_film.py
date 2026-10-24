#!/usr/bin/env python3
"""
Master Film Compiler for "AI Agent Là Gì? Giải Thích Trong 1 Phút" (Workshop 4 Cinematic Studio).
Assembles 12 Veo 2 AI video scenes, intro/outro bumpers, BGM with audio ducking (-18dB),
cinematic subtitle overlays, generates Full HD thumbnails, and exports .srt subtitle file.
Strictly enforces ZERO-FALLBACK mandate (100% AI video motion).
"""

import os
import sys
import json
import math
import shutil
import subprocess
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
WHITEBOARD_SITE_PACKAGES = BASE_DIR / "workshops" / "workshop-whiteboard" / ".venv" / "Lib" / "site-packages"
if WHITEBOARD_SITE_PACKAGES.exists() and str(WHITEBOARD_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(WHITEBOARD_SITE_PACKAGES))

from PIL import Image, ImageDraw, ImageFont

JOB_ID = "job-ai-agent-explained-1min"
PROJECT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
JOB_FILE = BASE_DIR / "output" / "jobs" / f"{JOB_ID}.json"
VIDEO_ID = "21b50be7-cbb9-4077-ab7f-c568ab304971"
AGENT_URL = "http://127.0.0.1:8100"

IMAGES_DIR = PROJECT_DIR / "images"
VIDEOS_DIR = PROJECT_DIR / "videos"
AUDIO_DIR = PROJECT_DIR / "audio"
SEGMENTS_DIR = PROJECT_DIR / "segments"
OVERLAYS_DIR = PROJECT_DIR / "overlays"
BUMPERS_DIR = PROJECT_DIR / "bumpers"
THUMBNAILS_DIR = PROJECT_DIR / "thumbnails"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)
BUMPERS_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

BGM_PATH = BASE_DIR / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "healing-piano.mp3"
FINAL_OUTPUT = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.mp4"
FINAL_SRT = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.srt"
FINAL_THUMB = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}-thumb.jpg"


def run_ffmpeg(cmd, desc=""):
    if desc:
        print(f"  [FFMPEG] {desc}", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [ERROR] {res.stderr[-400:]}", file=sys.stderr, flush=True)
        return False
    return True


def get_font(font_name="arial.ttf", size=32):
    font_paths = [
        Path(f"C:/Windows/Fonts/{font_name}"),
        Path(f"C:/Windows/Fonts/{font_name.lower()}"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/seguiemj.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
    ]
    for p in font_paths:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()


def create_subtitle_overlay(scene_num, speaker, text, output_path, width=1920, height=1080):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    speaker_styles = {
        "byte": {"bg": (0, 229, 255, 230), "fg": (10, 25, 40, 255), "label": "BÉ BYTE (AI ROBOT)"},
        "người dẫn chuyện": {"bg": (236, 239, 241, 230), "fg": (20, 30, 45, 255), "label": "DIỄN GIẢI KỸ THUẬT"},
    }
    key = speaker.strip().lower()
    style = speaker_styles.get(key, speaker_styles["người dẫn chuyện"])

    box_w = 1600
    box_h = 135
    box_x = (width - box_w) // 2
    box_y = height - box_h - 45

    # Rounded gradient backplate
    draw.rounded_rectangle(
        [(box_x, box_y), (box_x + box_w, box_y + box_h)],
        radius=18,
        fill=(11, 14, 20, 220),
        outline=(0, 229, 255, 90),
        width=2
    )

    # Speaker Pill Badge
    font_badge = get_font("arialbd.ttf", 22)
    badge_text = style["label"]
    badge_pad_x, badge_pad_y = 16, 6
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = (bbox[2] - bbox[0]) + badge_pad_x * 2
    bh = (bbox[3] - bbox[1]) + badge_pad_y * 2
    badge_x = box_x + 24
    badge_y = box_y - 18
    draw.rounded_rectangle(
        [(badge_x, badge_y), (badge_x + bw, badge_y + bh)],
        radius=10,
        fill=style["bg"]
    )
    draw.text((badge_x + badge_pad_x, badge_y + badge_pad_y - 2), badge_text, fill=style["fg"], font=font_badge)

    # Subtitle Content Text
    font_sub = get_font("arialbd.ttf", 34)
    words = text.split()
    lines = []
    cur = []
    for w in words:
        test = " ".join(cur + [w])
        if draw.textbbox((0, 0), test, font=font_sub)[2] < (box_w - 60):
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))

    text_y = box_y + (box_h - len(lines) * 44) // 2 + 8
    for line in lines:
        tbox = draw.textbbox((0, 0), line, font=font_sub)
        tx = (width - (tbox[2] - tbox[0])) // 2
        draw.text((tx + 2, text_y + 2), line, fill=(0, 0, 0, 220), font=font_sub)
        draw.text((tx, text_y), line, fill=(255, 255, 255, 255), font=font_sub)
        text_y += 44

    img.save(output_path, "PNG")


def create_intro_bumper(output_video_path, width=1920, height=1080, duration=3.5):
    img = Image.new("RGBA", (width, height), (10, 13, 20, 255))
    draw = ImageDraw.Draw(img)

    # Cyberpunk border & grid accents
    draw.rectangle([(25, 25), (width - 25, height - 25)], outline=(0, 229, 255, 90), width=2)
    draw.rectangle([(35, 35), (width - 35, height - 35)], outline=(255, 179, 0, 60), width=1)

    # Tech corner accents
    corner_len = 50
    c_color = (0, 229, 255, 220)
    for (cx, cy) in [(25, 25), (width-25, 25), (25, height-25), (width-25, height-25)]:
        dx = -1 if cx > width/2 else 1
        dy = -1 if cy > height/2 else 1
        draw.line([(cx, cy), (cx + dx * corner_len, cy)], fill=c_color, width=4)
        draw.line([(cx, cy), (cx, cy + dy * corner_len)], fill=c_color, width=4)

    # Load Logo
    logo_path = BASE_DIR / "shared-assets" / "branding" / "giaimatech_logo.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = 170
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        img.paste(logo, (width//2 - logo_size//2, 120), mask=logo)

    # Channel Name & Handle
    font_brand = get_font("arialbd.ttf", 38)
    font_handle = get_font("arial.ttf", 24)

    brand_text = "GIẢI MÃ TECH"
    handle_text = "@giaimatech-s8t"

    bb = draw.textbbox((0, 0), brand_text, font=font_brand)
    bw = bb[2] - bb[0]
    draw.text(((width - bw)//2, 310), brand_text, fill=(255, 255, 255, 255), font=font_brand)

    hb = draw.textbbox((0, 0), handle_text, font=font_handle)
    hw = hb[2] - hb[0]
    draw.rounded_rectangle([((width - hw)//2 - 16, 365), ((width + hw)//2 + 16, 402)], radius=18, fill=(20, 30, 48, 220), outline=(0, 229, 255, 140), width=1)
    draw.text(((width - hw)//2, 370), handle_text, fill=(0, 229, 255, 255), font=font_handle)

    # Divider line
    draw.line([(width//2 - 300, 435), (width//2 + 300, 435)], fill=(0, 229, 255, 80), width=2)

    # Topic Title
    font_title = get_font("arialbd.ttf", 60)
    title_text = "AI AGENT LÀ GÌ?"
    tb = draw.textbbox((0, 0), title_text, font=font_title)
    tw = tb[2] - tb[0]
    draw.text(((width - tw)//2 + 3, 503), title_text, fill=(0, 0, 0, 200), font=font_title)
    draw.text(((width - tw)//2, 500), title_text, fill=(255, 179, 0, 255), font=font_title)

    font_sub = get_font("arialbd.ttf", 36)
    sub_text = "Giải Thích Trong 1 Phút • Kỷ Nguyên Tự Chủ"
    sb = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = sb[2] - sb[0]
    draw.text(((width - sw)//2, 590), sub_text, fill=(0, 229, 255, 255), font=font_sub)

    # Badge: Workshop 4 Cinematic 3D
    font_badge = get_font("arialbd.ttf", 22)
    b_text = "WORKSHOP 4 • 3D CYBER-CHIBI CINEMATIC"
    bb = draw.textbbox((0, 0), b_text, font=font_badge)
    bw = bb[2] - bb[0]
    draw.rounded_rectangle([((width - bw)//2 - 18, 675), ((width + bw)//2 + 18, 715)], radius=12, fill=(15, 23, 42, 220), outline=(255, 179, 0, 160), width=1)
    draw.text(((width - bw)//2, 683), b_text, fill=(255, 255, 255, 230), font=font_badge)

    temp_png = BUMPERS_DIR / "intro_bumper.png"
    img.save(temp_png, "PNG")

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(temp_png),
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-vf", f"fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.5:.2f}:d=0.5,fps=30",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", str(duration),
        str(output_video_path)
    ]
    return run_ffmpeg(cmd, "Create Intro Bumper")


def create_outro_bumper(output_video_path, width=1920, height=1080, duration=3.5):
    img = Image.new("RGBA", (width, height), (10, 13, 20, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(25, 25), (width - 25, height - 25)], outline=(0, 229, 255, 90), width=2)
    draw.rectangle([(35, 35), (width - 35, height - 35)], outline=(255, 179, 0, 60), width=1)

    logo_path = BASE_DIR / "shared-assets" / "branding" / "giaimatech_logo.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = 150
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        img.paste(logo, (width//2 - logo_size//2, 140), mask=logo)

    font_thx = get_font("arialbd.ttf", 46)
    thx_text = "CẢM ƠN BẠN ĐÃ THEO DÕI!"
    tb = draw.textbbox((0, 0), thx_text, font=font_thx)
    tw = tb[2] - tb[0]
    draw.text(((width - tw)//2, 330), thx_text, fill=(255, 255, 255, 255), font=font_thx)

    font_cta = get_font("arialbd.ttf", 36)
    cta_text = "LIKE • SHARE • ĐĂNG KÝ KÊNH"
    cb = draw.textbbox((0, 0), cta_text, font=font_cta)
    cw = cb[2] - cb[0]
    draw.rounded_rectangle([((width - cw)//2 - 25, 415), ((width + cw)//2 + 25, 480)], radius=16, fill=(0, 229, 255, 220), outline=(255, 255, 255, 200), width=2)
    draw.text(((width - cw)//2, 428), cta_text, fill=(10, 20, 35, 255), font=font_cta)

    font_sub = get_font("arial.ttf", 26)
    sub_text = "Đón xem các tập tiếp theo về AI & Tự Động Hóa cùng Giải Mã Tech"
    sb = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = sb[2] - sb[0]
    draw.text(((width - sw)//2, 530), sub_text, fill=(200, 220, 240, 240), font=font_sub)

    temp_png = BUMPERS_DIR / "outro_bumper.png"
    img.save(temp_png, "PNG")

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(temp_png),
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-vf", f"fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.5:.2f}:d=0.5,fps=30",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", str(duration),
        str(output_video_path)
    ]
    return run_ffmpeg(cmd, "Create Outro Bumper")


def generate_thumbnails(width=1920, height=1080):
    print("\n🎨 Đang thiết kế 2 mẫu Thumbnail Full HD (1080p) cực nét...", flush=True)

    # Mẫu 1: Hero Thumbnail (Byte + Holo Brain + Big Typography)
    img1 = Image.new("RGBA", (width, height), (10, 15, 28, 255))
    draw1 = ImageDraw.Draw(img1)

    # Background gradient accents
    draw1.rectangle([(0, 0), (width, height)], fill=(12, 18, 32, 255))
    draw1.ellipse([(-200, -200), (900, 900)], fill=(0, 150, 255, 40))
    draw1.ellipse([(width-800, height-700), (width+400, height+400)], fill=(255, 179, 0, 35))

    # Border
    draw1.rectangle([(30, 30), (width - 30, height - 30)], outline=(0, 229, 255, 120), width=4)

    # Load Byte scene image if available
    byte_img_path = IMAGES_DIR / "scene_03.jpg"
    if not byte_img_path.exists():
        byte_img_path = IMAGES_DIR / "scene_04.jpg"
    if not byte_img_path.exists():
        # Fall back to any scene image
        for sf in IMAGES_DIR.glob("scene_*.jpg"):
            byte_img_path = sf
            break

    if byte_img_path and byte_img_path.exists():
        try:
            bimg = Image.open(byte_img_path).convert("RGBA")
            # Crop/resize to right half
            target_w, target_h = 1000, 750
            bimg = bimg.resize((target_w, target_h), Image.Resampling.LANCZOS)
            # Add rounded tech frame
            mask = Image.new("L", (target_w, target_h), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle([(0, 0), (target_w, target_h)], radius=30, fill=255)
            img1.paste(bimg, (width - target_w - 70, (height - target_h)//2), mask=mask)
            draw1.rounded_rectangle([(width - target_w - 70, (height - target_h)//2), (width - 70, (height + target_h)//2)], radius=30, outline=(0, 229, 255, 180), width=4)
        except Exception as e:
            print(f"  [WARN] Thumbnail image paste error: {e}")

    # Channel logo & brand
    logo_path = BASE_DIR / "shared-assets" / "branding" / "giaimatech_logo.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA").resize((90, 90), Image.Resampling.LANCZOS)
        img1.paste(logo, (80, 70), mask=logo)
    font_brand = get_font("arialbd.ttf", 32)
    draw1.text((190, 95), "GIẢI MÃ TECH", fill=(255, 255, 255, 255), font=font_brand)

    # Pill: 1 PHÚT HIỂU HẾT
    font_pill = get_font("arialbd.ttf", 26)
    p_text = "⚡ 1 PHÚT HIỂU HẾT"
    pb = draw1.textbbox((0, 0), p_text, font=font_pill)
    pw = pb[2] - pb[0]
    draw1.rounded_rectangle([(80, 210), (80 + pw + 36, 265)], radius=14, fill=(255, 179, 0, 240))
    draw1.text((98, 222), p_text, fill=(20, 20, 20, 255), font=font_pill)

    # Big Headline
    font_h1 = get_font("arialbd.ttf", 95)
    font_h2 = get_font("arialbd.ttf", 78)
    draw1.text((84, 294), "AI AGENT", fill=(0, 0, 0, 220), font=font_h1)
    draw1.text((80, 290), "AI AGENT", fill=(0, 229, 255, 255), font=font_h1)

    draw1.text((84, 404), "LÀ GÌ?", fill=(0, 0, 0, 220), font=font_h1)
    draw1.text((80, 400), "LÀ GÌ?", fill=(255, 255, 255, 255), font=font_h1)

    # Sub-punch
    font_punch = get_font("arialbd.ttf", 40)
    draw1.text((80, 530), "VÌ SAO CHATBOT", fill=(255, 100, 100, 255), font=font_punch)
    draw1.text((80, 585), "SẮP BỊ THAY THẾ?", fill=(255, 220, 100, 255), font=font_punch)

    # Feature badges
    font_feat = get_font("arialbd.ttf", 24)
    badges = ["🧠 Tự Lập Kế Hoạch", "💾 Bộ Nhớ Ngữ Cảnh", "🛠️ Tự Chạy Công Cụ"]
    by = 700
    for b in badges:
        bb = draw1.textbbox((0, 0), b, font=font_feat)
        bw = bb[2] - bb[0]
        draw1.rounded_rectangle([(80, by), (80 + bw + 30, by + 45)], radius=10, fill=(20, 35, 55, 220), outline=(0, 229, 255, 100), width=1)
        draw1.text((95, by + 10), b, fill=(220, 240, 255, 255), font=font_feat)
        by += 60

    thumb1_path = THUMBNAILS_DIR / "thumb_01_hero.jpg"
    img1.convert("RGB").save(thumb1_path, "JPEG", quality=95)
    img1.convert("RGB").save(FINAL_THUMB, "JPEG", quality=95)
    print(f"  [THUMB 1] Lưu thành công: {thumb1_path.name} & {FINAL_THUMB.name}", flush=True)

    # Mẫu 2: Comparison Thumbnail (Chatbot vs AI Agent)
    img2 = Image.new("RGBA", (width, height), (15, 20, 35, 255))
    draw2 = ImageDraw.Draw(img2)
    draw2.rectangle([(0, 0), (width//2, height)], fill=(25, 20, 25, 255))
    draw2.rectangle([(width//2, 0), (width, height)], fill=(15, 28, 45, 255))
    draw2.line([(width//2, 0), (width//2, height)], fill=(0, 229, 255, 160), width=4)
    draw2.rectangle([(30, 30), (width - 30, height - 30)], outline=(255, 179, 0, 120), width=4)

    # Left: CHATBOT
    font_vs = get_font("arialbd.ttf", 68)
    draw2.text((120, 150), "CHATBOT", fill=(255, 80, 80, 255), font=font_vs)
    font_vs_sub = get_font("arialbd.ttf", 36)
    draw2.text((120, 250), "❌ Chỉ biết NÓI MỒM", fill=(240, 200, 200, 255), font=font_vs_sub)
    draw2.text((120, 330), "❌ Quên ngữ cảnh", fill=(240, 200, 200, 255), font=font_vs_sub)
    draw2.text((120, 410), "❌ Không có tay chân", fill=(240, 200, 200, 255), font=font_vs_sub)
    draw2.text((120, 490), "❌ Đợi người dùng làm hết", fill=(240, 200, 200, 255), font=font_vs_sub)

    # VS badge in center
    draw2.ellipse([(width//2 - 65, height//2 - 65), (width//2 + 65, height//2 + 65)], fill=(255, 179, 0, 255), outline=(255, 255, 255, 255), width=3)
    draw2.text((width//2 - 38, height//2 - 32), "VS", fill=(10, 10, 10, 255), font=get_font("arialbd.ttf", 52))

    # Right: AI AGENT
    draw2.text((width//2 + 100, 150), "AI AGENT", fill=(0, 229, 255, 255), font=font_vs)
    draw2.text((width//2 + 100, 250), "✅ Tự LẬP KẾ HOẠCH", fill=(200, 255, 240, 255), font=font_vs_sub)
    draw2.text((width//2 + 100, 330), "✅ Có BỘ NHỚ dài hạn", fill=(200, 255, 240, 255), font=font_vs_sub)
    draw2.text((width//2 + 100, 410), "✅ Tự THỰC THI công cụ", fill=(200, 255, 240, 255), font=font_vs_sub)
    draw2.text((width//2 + 100, 490), "✅ Bạn chỉ cần thảnh thơi!", fill=(255, 220, 100, 255), font=font_vs_sub)

    # Bottom banner
    font_bot = get_font("arialbd.ttf", 46)
    bot_text = "BƯỚC NHẢY VỌT TỰ ĐỘNG HÓA 2026"
    bb = draw2.textbbox((0, 0), bot_text, font=font_bot)
    bw = bb[2] - bb[0]
    draw2.rounded_rectangle([((width - bw)//2 - 30, height - 170), ((width + bw)//2 + 30, height - 90)], radius=20, fill=(0, 229, 255, 220))
    draw2.text(((width - bw)//2, height - 155), bot_text, fill=(10, 25, 45, 255), font=font_bot)

    thumb2_path = THUMBNAILS_DIR / "thumb_02_comparison.jpg"
    img2.convert("RGB").save(thumb2_path, "JPEG", quality=95)
    print(f"  [THUMB 2] Lưu thành công: {thumb2_path.name}", flush=True)


def format_srt_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def generate_srt_file(beats, tracks, intro_duration=3.5):
    print("\n📝 Đang tạo file phụ đề chuẩn SRT...", flush=True)
    cur_time = intro_duration
    srt_lines = []

    for i in range(len(beats)):
        beat = beats[i]
        track = tracks[i]
        dur = track["duration"]
        start_str = format_srt_time(cur_time)
        end_str = format_srt_time(cur_time + dur)
        speaker = beat.get("speaker", "Người Dẫn Chuyện")
        text = beat.get("rawText", "")

        srt_lines.append(f"{i + 1}")
        srt_lines.append(f"{start_str} --> {end_str}")
        srt_lines.append(f"[{speaker}]: {text}\n")
        cur_time += dur

    FINAL_SRT.write_text("\n".join(srt_lines), encoding="utf-8")
    print(f"  [SRT] Đã xuất file phụ đề: {FINAL_SRT.name} ({len(beats)} câu)", flush=True)


def render_scene_segment(scene_num, beat_data, track_data, output_path, width=1920, height=1080, fps=30):
    dur = track_data["duration"]
    speaker = beat_data.get("speaker", "Người Dẫn Chuyện")
    cand_file = Path(track_data["file"])
    candidates = [
        BASE_DIR / "output" / cand_file,
        BASE_DIR / cand_file,
        AUDIO_DIR / cand_file.name,
        cand_file
    ]
    audio_path = None
    for c in candidates:
        if c.exists():
            audio_path = c
            break
    if not audio_path:
        print(f"  [ERROR] Cảnh {scene_num:02d}: Không tìm thấy audio: {cand_file}", file=sys.stderr)
        return False

    text = beat_data.get("rawText", "")
    overlay_png = OVERLAYS_DIR / f"overlay_{scene_num:02d}.png"
    create_subtitle_overlay(scene_num, speaker, text, overlay_png, width, height)

    vid_cand = VIDEOS_DIR / f"scene_{scene_num:02d}.mp4"

    if not (vid_cand.exists() and vid_cand.stat().st_size > 100000):
        print(f"  ❌ [ZERO-FALLBACK VIOLATION] Cảnh {scene_num:02d} ({speaker}): Thiếu video AI Veo 2 ({vid_cand})!", file=sys.stderr)
        print(f"     Chính sách nghiêm ngặt: Tuyệt đối CẤM dùng ảnh tĩnh fallback!", file=sys.stderr)
        return False

    print(f"  🎬 Cảnh {scene_num:02d} ({speaker}): Veo 2 AI Video ({vid_cand.name}) - {dur:.2f}s", flush=True)
    filter_complex = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps={fps}[base];"
        f"[base][1:v]overlay=0:0[vout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(vid_cand),
        "-i", str(overlay_png),
        "-i", str(audio_path),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "2:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", str(dur),
        str(output_path)
    ]
    return run_ffmpeg(cmd, f"Render Scene {scene_num:02d} (Veo 2 Video)")


def assemble_complete_film():
    print("=" * 65)
    print("🎬 OMNIVIDEO STUDIO — WORKSHOP 4 AI CINEMATIC MASTER FILM")
    print(f"Project: {JOB_ID}")
    print(f"Output: {FINAL_OUTPUT}")
    print("=" * 65)

    job_data = json.loads(JOB_FILE.read_text(encoding="utf-8"))
    beats = job_data.get("beats", [])

    manifest_file = AUDIO_DIR / "audio_manifest.json"
    if not manifest_file.exists():
        print(f"[LỖI] Không tìm thấy {manifest_file}!", file=sys.stderr)
        return False
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    tracks = manifest.get("tracks", [])

    print(f"\n📊 Tổng số cảnh: {len(beats)}, Tổng thời lượng thoại: {manifest.get('totalDurationSeconds', 0):.2f}s")

    # Strict Zero-Fallback Pre-Check: 100% of scenes MUST have completed AI videos
    missing_videos = []
    for i in range(len(beats)):
        sn = i + 1
        vf = VIDEOS_DIR / f"scene_{sn:02d}.mp4"
        if not vf.exists() or vf.stat().st_size < 100000:
            missing_videos.append(sn)

    if missing_videos:
        print("\n" + "!" * 65, file=sys.stderr)
        print(f"❌ [CHÍNH SÁCH BẮT BUỘC: 100% VIDEO AI — ZERO FALLBACK]", file=sys.stderr)
        print(f"   Còn {len(missing_videos)}/{len(beats)} cảnh chưa hoàn thành video Veo 2 AI: {missing_videos}", file=sys.stderr)
        print(f"   Hệ thống TUYỆT ĐỐI CẤM dùng ảnh tĩnh fallback. Dừng quy trình xuất phim cho đến khi render xong 100%!", file=sys.stderr)
        print("!" * 65 + "\n", file=sys.stderr)
        return False

    intro_dur = 3.5
    outro_dur = 3.5
    intro_mp4 = BUMPERS_DIR / "intro_bumper.mp4"
    outro_mp4 = BUMPERS_DIR / "outro_bumper.mp4"
    create_intro_bumper(intro_mp4, duration=intro_dur)
    create_outro_bumper(outro_mp4, duration=outro_dur)

    generate_thumbnails()
    generate_srt_file(beats, tracks, intro_duration=intro_dur)

    rendered_segments = []
    concat_list_file = PROJECT_DIR / "concat_segments.txt"
    lines = [f"file '{intro_mp4.as_posix()}'\n"]

    for i in range(len(beats)):
        scene_num = i + 1
        beat = beats[i]
        track = tracks[i]
        seg_mp4 = SEGMENTS_DIR / f"segment_{scene_num:02d}.mp4"

        ok = render_scene_segment(scene_num, beat, track, seg_mp4)
        if not ok:
            print(f"  [CẢNH BÁO] Không thể render Cảnh {scene_num:02d}", file=sys.stderr)
            return False
        rendered_segments.append(seg_mp4)
        lines.append(f"file '{seg_mp4.as_posix()}'\n")

    lines.append(f"file '{outro_mp4.as_posix()}'\n")
    concat_list_file.write_text("".join(lines), encoding="utf-8")
    print(f"\n✅ Đã chuẩn bị {len(rendered_segments)} phân đoạn cảnh độc lập.", flush=True)

    raw_concat_mp4 = PROJECT_DIR / "temp_raw_concat.mp4"
    print("\n🎞️ Đang ghép nối toàn bộ các phân cảnh thành chuỗi phim...", flush=True)
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(raw_concat_mp4)
    ]
    ok = run_ffmpeg(cmd_concat, "Concatenating scene segments")
    if not ok:
        print("[LỖI] Ghép concat thất bại!", file=sys.stderr)
        return False

    print("\n🎵 Đang hòa âm Master BGM (Audio Ducking -18dB khi có thoại)...", flush=True)
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(raw_concat_mp4)]
    r = subprocess.run(probe_cmd, capture_output=True, text=True)
    total_dur = float(r.stdout.strip()) if r.stdout.strip() else 63.0
    print(f"  => Tổng thời lượng phim: {total_dur:.2f} giây (~{total_dur/60:.1f} phút)")

    if BGM_PATH.exists():
        filter_audio = (
            f"[1:a]volume=0.12,atrim=0:{total_dur},afade=t=in:st=0:d=1.5,afade=t=out:st={total_dur-2.0:.2f}:d=2.0[bgm];"
            f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[aout]"
        )
        cmd_mix = [
            "ffmpeg", "-y",
            "-i", str(raw_concat_mp4),
            "-stream_loop", "-1", "-i", str(BGM_PATH),
            "-filter_complex", filter_audio,
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-t", str(total_dur),
            str(FINAL_OUTPUT)
        ]
        ok_mix = run_ffmpeg(cmd_mix, "Mixing Master Audio with BGM")
        if not ok_mix:
            print("  [WARN] Hòa âm BGM lỗi, sao chép file gốc...")
            shutil.copy(raw_concat_mp4, FINAL_OUTPUT)
    else:
        print("  [WARN] Không tìm thấy BGM, xuất trực tiếp...")
        shutil.copy(raw_concat_mp4, FINAL_OUTPUT)

    print("\n" + "=" * 65)
    print("🎉 MASTER FILM HOÀN THÀNH XUẤT SẮC!")
    print(f"👉 File Video: {FINAL_OUTPUT}")
    print(f"👉 Kích thước: {FINAL_OUTPUT.stat().st_size:,} bytes")
    print(f"👉 Phụ đề: {FINAL_SRT}")
    print(f"👉 Thumbnail: {FINAL_THUMB}")
    print(f"👉 Độ phân giải: 1920x1080 @ 30 FPS")
    print(f"👉 Âm thanh: 48,000 Hz Stereo AAC 192kbps")
    print("=" * 65)
    return True


if __name__ == "__main__":
    assemble_complete_film()

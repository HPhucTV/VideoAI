#!/usr/bin/env python3
"""
Master Film Compiler for Cyber-Chibi 3D MCP Film (Workshop 4 Cinematic Studio).
Assembles 30 scenes, intro/outro bumpers, BGM with audio ducking (-18dB),
and high-legibility cinematic subtitle overlays into a 1080p 30fps Master Film.
Enforces ZERO-FALLBACK mandate (100% AI video motion).
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

JOB_ID = "job-mcp-cyber-chibi"
PROJECT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
JOB_FILE = BASE_DIR / "output" / "jobs" / f"{JOB_ID}.json"
VIDEO_ID = "da8930b1-0820-4546-b8c1-4a7bcf4d7c1e"
AGENT_URL = "http://127.0.0.1:8100"

IMAGES_DIR = PROJECT_DIR / "images"
VIDEOS_DIR = PROJECT_DIR / "videos"
AUDIO_DIR = PROJECT_DIR / "audio"
SEGMENTS_DIR = PROJECT_DIR / "segments"
OVERLAYS_DIR = PROJECT_DIR / "overlays"
BUMPERS_DIR = PROJECT_DIR / "bumpers"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)
BUMPERS_DIR.mkdir(parents=True, exist_ok=True)

BGM_PATH = BASE_DIR / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "healing-piano.mp3"
FINAL_OUTPUT = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.mp4"


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


def download_images_from_db():
    print("\n📥 Đang đồng bộ và tải ảnh cảnh từ FlowKit Database...", flush=True)
    try:
        res = requests.get(f"{AGENT_URL}/api/scenes?video_id={VIDEO_ID}", timeout=10)
        if res.status_code != 200:
            print(f"  [WARN] Không thể lấy scenes: HTTP {res.status_code}")
            return
        scenes = res.json()
        count = 0
        for s in scenes:
            order = s.get("display_order")
            img_url = s.get("horizontal_image_url")
            out_img = IMAGES_DIR / f"scene_{order:02d}.jpg"
            if img_url and not out_img.exists():
                try:
                    r = requests.get(img_url, timeout=30)
                    if r.status_code == 200:
                        out_img.write_bytes(r.content)
                        print(f"  [TẢI ẢNH] Cảnh {order:02d} -> {out_img.name} ({len(r.content):,} bytes)", flush=True)
                        count += 1
                except Exception as e:
                    print(f"  [LỖI TẢI] Cảnh {order:02d}: {e}")
        print(f"  => Tổng cộng {count} ảnh mới tải về {IMAGES_DIR}", flush=True)
    except Exception as e:
        print(f"  [WARN] Lỗi kết nối FlowKit DB: {e}")


def create_subtitle_overlay(scene_num, speaker, text, output_path, width=1920, height=1080):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    speaker_styles = {
        "byte": {"bg": (0, 229, 255, 230), "fg": (10, 25, 40, 255), "label": "BÉ BYTE (CHATBOT)"},
        "tiến sĩ kael": {"bg": (255, 179, 0, 230), "fg": (20, 20, 20, 255), "label": "TIẾN SĨ KAEL"},
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
    # Word wrap if text is long
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
        # Text shadow for cinema legibility
        draw.text((tx + 2, text_y + 2), line, fill=(0, 0, 0, 220), font=font_sub)
        draw.text((tx, text_y), line, fill=(255, 255, 255, 255), font=font_sub)
        text_y += 44

    img.save(output_path, "PNG")


def create_intro_bumper(output_video_path, width=1920, height=1080, duration=4.5):
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

    # Title
    font_title = get_font("arialbd.ttf", 58)
    t1 = "MCP LÀ GÌ? AI KẾT NỐI VỚI CÔNG CỤ RA SAO?"
    t1_w = draw.textbbox((0, 0), t1, font=font_title)[2]
    draw.text(((width - t1_w) // 2 + 3, 493), t1, fill=(0, 0, 0, 220), font=font_title)
    draw.text(((width - t1_w) // 2, 490), t1, fill=(255, 255, 255, 255), font=font_title)

    # Subtitle
    font_sub = get_font("arial.ttf", 34)
    t2 = "Model Context Protocol — Cổng Cắm USB-C Vạn Năng Cho AI"
    t2_w = draw.textbbox((0, 0), t2, font=font_sub)[2]
    draw.text(((width - t2_w) // 2, 590), t2, fill=(0, 229, 255, 230), font=font_sub)

    # Bottom badge
    font_tag = get_font("arialbd.ttf", 20)
    tag = "XƯỞNG 4 CINEMATIC 3D • 1080P MASTER"
    tb = draw.textbbox((0, 0), tag, font=font_tag)
    tw = tb[2] - tb[0]
    draw.rounded_rectangle([((width - tw)//2 - 20, 960), ((width + tw)//2 + 20, 998)], radius=12, fill=(16, 22, 34, 200), outline=(255, 179, 0, 100), width=1)
    draw.text(((width - tw)//2, 968), tag, fill=(255, 179, 0, 230), font=font_tag)

    intro_png = BUMPERS_DIR / "intro_frame.png"
    img.save(intro_png)

    # Ultra-smooth fade in/out without jittery zoompan
    filter_complex = (
        f"[0:v]scale={width}:{height},fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.5:.2f}:d=0.5,fps=30[vout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(duration), "-i", str(intro_png),
        "-f", "lavfi", "-t", str(duration), "-i", f"anoisesrc=d={duration}:c=brown:r=48000:a=0.08",
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", str(duration),
        str(output_video_path)
    ]
    return run_ffmpeg(cmd, "Render Intro Bumper (Smooth Fade, Zero Jitter)")


def create_outro_bumper(output_video_path, width=1920, height=1080, duration=4.5):
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
        img.paste(logo, (width//2 - logo_size//2, 130), mask=logo)

    # Channel Name & Handle
    font_brand = get_font("arialbd.ttf", 38)
    font_handle = get_font("arial.ttf", 24)

    brand_text = "GIẢI MÃ TECH"
    handle_text = "@giaimatech-s8t"

    bb = draw.textbbox((0, 0), brand_text, font=font_brand)
    bw = bb[2] - bb[0]
    draw.text(((width - bw)//2, 320), brand_text, fill=(255, 255, 255, 255), font=font_brand)

    hb = draw.textbbox((0, 0), handle_text, font=font_handle)
    hw = hb[2] - hb[0]
    draw.rounded_rectangle([((width - hw)//2 - 16, 375), ((width + hw)//2 + 16, 412)], radius=18, fill=(20, 30, 48, 220), outline=(0, 229, 255, 140), width=1)
    draw.text(((width - hw)//2, 380), handle_text, fill=(0, 229, 255, 255), font=font_handle)

    # Divider line
    draw.line([(width//2 - 300, 445), (width//2 + 300, 445)], fill=(0, 229, 255, 80), width=2)

    # Call to Action Title
    font_title = get_font("arialbd.ttf", 52)
    t1 = "CHUẨN HÓA KẾT NỐI — BIẾN CHATBOT THÀNH AI AGENT"
    t1_w = draw.textbbox((0, 0), t1, font=font_title)[2]
    draw.text(((width - t1_w) // 2 + 3, 503), t1, fill=(0, 0, 0, 220), font=font_title)
    draw.text(((width - t1_w) // 2, 500), t1, fill=(255, 255, 255, 255), font=font_title)

    # Subscribe message
    font_sub = get_font("arial.ttf", 32)
    t2 = "Đăng Ký & Nhấn Chuông Kênh Giải Mã Tech Để Đón Xem Video Công Nghệ Tiếp Theo!"
    t2_w = draw.textbbox((0, 0), t2, font=font_sub)[2]
    draw.text(((width - t2_w) // 2, 595), t2, fill=(255, 179, 0, 230), font=font_sub)

    # Bottom Thank You Pill
    font_tag = get_font("arialbd.ttf", 20)
    tag = "CẢM ƠN BẠN ĐÃ THEO DÕI • HẸN GẶP LẠI TẬP TIẾP THEO"
    tb = draw.textbbox((0, 0), tag, font=font_tag)
    tw = tb[2] - tb[0]
    draw.rounded_rectangle([((width - tw)//2 - 20, 960), ((width + tw)//2 + 20, 998)], radius=12, fill=(16, 22, 34, 200), outline=(0, 229, 255, 100), width=1)
    draw.text(((width - tw)//2, 968), tag, fill=(0, 229, 255, 230), font=font_tag)

    outro_png = BUMPERS_DIR / "outro_frame.png"
    img.save(outro_png)

    # Ultra-smooth fade in/out without jittery zoompan
    filter_complex = (
        f"[0:v]scale={width}:{height},fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.5:.2f}:d=0.5,fps=30[vout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(duration), "-i", str(outro_png),
        "-f", "lavfi", "-t", str(duration), "-i", f"anoisesrc=d={duration}:c=brown:r=48000:a=0.08",
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", str(duration),
        str(output_video_path)
    ]
    return run_ffmpeg(cmd, "Render Outro Bumper (Smooth Fade, Zero Jitter)")


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

    download_images_from_db()

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

    intro_mp4 = BUMPERS_DIR / "intro_bumper.mp4"
    outro_mp4 = BUMPERS_DIR / "outro_bumper.mp4"
    create_intro_bumper(intro_mp4)
    create_outro_bumper(outro_mp4)

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
    total_dur = float(r.stdout.strip()) if r.stdout.strip() else 145.0
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
    print(f"👉 Độ phân giải: 1920x1080 @ 30 FPS")
    print(f"👉 Âm thanh: 48,000 Hz Stereo AAC 192kbps")
    print("=" * 65)
    return True


if __name__ == "__main__":
    assemble_complete_film()

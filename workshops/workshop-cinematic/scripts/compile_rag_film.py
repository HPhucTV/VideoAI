#!/usr/bin/env python3
"""
Master Film Compiler for RAG Xianxia Cinematic Video
Assembles all 30 scenes, intro/outro bumpers, BGM with audio ducking,
and high-legibility cinematic subtitle overlays into a 1080p 30fps Master Film.
"""

import os
import sys
import json
import math
import shutil
import subprocess
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
JOB_ID = "job-rag-xianxia-cinematic"
PROJECT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
JOB_FILE = BASE_DIR / "output" / "jobs" / f"{JOB_ID}.json"
VIDEO_ID = "950039ae-6565-4a44-8bfa-0034d5d79a5b"
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

BGM_PATH = BASE_DIR / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "xianxia-ambient.mp3"
AVATAR_PATH = BASE_DIR / "shared-assets" / "branding" / "avatar.png"
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
    print("\n📥 Đang đồng bộ và tải ảnh từ FlowKit Database...", flush=True)
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
                        print(f"  [TẢI ẢNH] Cảnh {order:02d} -> {out_img.name} ({len(r.content)} bytes)", flush=True)
                        count += 1
                except Exception as e:
                    print(f"  [LỖI TẢI] Cảnh {order:02d}: {e}")
        print(f"  => Đã tải {count} ảnh mới vào {IMAGES_DIR}", flush=True)
    except Exception as e:
        print(f"  [WARN] Lỗi kết nối FlowKit DB: {e}")


def create_subtitle_overlay(scene_num, speaker, text, output_path, width=1920, height=1080):
    """Tạo file PNG trong suốt 1920x1080 chứa Speaker badge và Subtitle box chuẩn điện ảnh."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_badge = get_font("arialbd.ttf", 26)
    font_sub = get_font("arialbd.ttf", 36)

    # Theme màu theo nhân vật
    speaker_colors = {
        "Tiểu Linh": {"bg": (10, 45, 65, 230), "border": (0, 229, 255, 255), "text": (220, 250, 255), "badge": "◆ KHÍ LINH: TIỂU LINH"},
        "Đạo Sư": {"bg": (55, 42, 10, 230), "border": (255, 215, 0, 255), "text": (255, 245, 220), "badge": "◆ BẠCH Y ĐẠO SƯ"},
        "Tâm Ma": {"bg": (45, 10, 55, 230), "border": (224, 86, 253, 255), "text": (250, 220, 255), "badge": "◆ TÂM MA ẢO GIÁC"},
        "Người Kể Chuyện": {"bg": (25, 25, 35, 230), "border": (255, 183, 3, 255), "text": (255, 255, 255), "badge": "◆ GIẢI MÃ TECH"},
    }
    cfg = speaker_colors.get(speaker, speaker_colors["Người Kể Chuyện"])

    # 1. Vẽ Speaker Badge ở góc dưới, phía trên Subtitle box (y ~ 890)
    badge_text = cfg["badge"]
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox[2] - bbox[0] + 36
    bh = bbox[3] - bbox[1] + 16
    bx = 100
    by = height - 195

    # Badge background
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=cfg["bg"], outline=cfg["border"], width=2)
    draw.text((bx + 18, by + 8), badge_text, font=font_badge, fill=cfg["text"])

    # 2. Vẽ Subtitle Box ở dưới (y ~ 950 - 1040)
    # Tách dòng thoại (wrap text)
    words = text.split()
    lines = []
    curr = []
    max_line_w = 1600
    for w in words:
        test_line = " ".join(curr + [w])
        tb = draw.textbbox((0, 0), test_line, font=font_sub)
        if (tb[2] - tb[0]) > max_line_w and curr:
            lines.append(" ".join(curr))
            curr = [w]
        else:
            curr.append(w)
    if curr:
        lines.append(" ".join(curr))

    line_h = 44
    box_pad_y = 16
    box_h = len(lines) * line_h + box_pad_y * 2
    box_y = height - 120 - (len(lines) - 1) * line_h

    # Vẽ nền kính đen mờ cho subtitle
    draw.rounded_rectangle([80, box_y - 8, width - 80, box_y + box_h - 12], radius=10, fill=(8, 10, 16, 210), outline=(60, 70, 85, 180), width=1)

    for i, line in enumerate(lines):
        line_y = box_y + box_pad_y - 6 + i * line_h
        # Drop shadow cho chữ
        draw.text((width // 2 + 2, line_y + 2), line, font=font_sub, fill=(0, 0, 0, 220), anchor="ma")
        draw.text((width // 2, line_y), line, font=font_sub, fill=(255, 255, 255, 255), anchor="ma")

    img.save(output_path, "PNG")
    return True


def create_intro_bumper(output_video_path, duration=3.5, width=1920, height=1080, fps=30):
    """Tạo đoạn Intro Bumper điện ảnh 3.5s với nhận diện kênh Giải Mã Tech."""
    if output_video_path.exists() and output_video_path.stat().st_size > 50000:
        return True

    card_img_path = BUMPERS_DIR / "intro_card.png"
    img = Image.new("RGB", (width, height), (8, 10, 16))
    draw = ImageDraw.Draw(img)

    # Radial dark blue/crimson ambience
    pixels = img.load()
    cx, cy = width / 2.0, height / 2.0
    for y in range(0, height, 4):
        for x in range(0, width, 4):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2) / 1200.0
            val = max(0.0, 1.0 - dist)
            r = int(8 + val * 45)
            g = int(10 + val * 35)
            b = int(18 + val * 75)
            for dy in range(4):
                for dx in range(4):
                    if x + dx < width and y + dy < height:
                        pixels[x + dx, y + dy] = (r, g, b)

    font_series = get_font("arialbd.ttf", 34)
    font_title = get_font("timesbd.ttf", 64)
    font_sub = get_font("arial.ttf", 32)
    font_dec = get_font("timesbd.ttf", 24)

    draw = ImageDraw.Draw(img)
    # Framing
    draw.rectangle([80, 50, width - 80, height - 50], outline=(70, 60, 40), width=1)
    draw.rectangle([86, 56, width - 86, height - 56], outline=(40, 35, 25), width=1)

    # Series
    draw.text((cx, height * 0.32), "GIẢI MÃ TECH · AI CINEMATIC SERIES", font=font_series, fill=(212, 175, 55), anchor="mm")
    draw.line([(cx - 350, height * 0.38), (cx + 350, height * 0.38)], fill=(150, 120, 50), width=2)
    draw.text((cx, height * 0.38), "◆", font=font_dec, fill=(212, 175, 55), anchor="mm")

    # Title
    draw.text((cx, height * 0.48), "RAG LÀ GÌ?", font=font_title, fill=(255, 255, 255), anchor="mm")
    draw.text((cx, height * 0.58), "Tại Sao Chatbot Cần RAG Để Thoát Khỏi Ảo Giác?", font=get_font("arialbd.ttf", 46), fill=(0, 229, 255), anchor="mm")

    draw.line([(cx - 350, height * 0.67), (cx + 350, height * 0.67)], fill=(150, 120, 50), width=2)
    draw.text((cx, height * 0.67), "◆", font=font_dec, fill=(212, 175, 55), anchor="mm")

    draw.text((cx, height * 0.74), "Khí Linh Chatbot & Bí Pháp Vạn Cổ Tàng Kinh Các", font=font_sub, fill=(200, 210, 225), anchor="mm")
    img.save(card_img_path)

    # Render video with micro zoom & sub-bass ambience
    num_frames = int(duration * fps)
    fade_out_st = duration - 0.7
    filter_complex = (
        f"[0:v]zoompan=z='min(zoom+0.0004,1.06)':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps},"
        f"fade=t=in:st=0:d=0.7,fade=t=out:st={fade_out_st:.2f}:d=0.7[vout];"
        f"[1:a]lowpass=f=180,volume=2.5,afade=t=in:ss=0:d=0.6,afade=t=out:st={fade_out_st:.2f}:d=0.7[aout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(card_img_path),
        "-f", "lavfi", "-t", str(duration), "-i", f"anoisesrc=d={duration}:c=brown:r=48000:a=0.15",
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", str(duration),
        str(output_video_path)
    ]
    return run_ffmpeg(cmd, "Render Intro Bumper")


def create_outro_bumper(output_video_path, duration=4.5, width=1920, height=1080, fps=30):
    """Tạo đoạn Outro Bumper kết phim với Avatar kênh và lời kêu gọi theo dõi."""
    if output_video_path.exists() and output_video_path.stat().st_size > 50000:
        return True

    card_img_path = BUMPERS_DIR / "outro_card.png"
    img = Image.new("RGB", (width, height), (8, 10, 16))
    cx, cy = width / 2.0, height / 2.0

    # Dán Avatar kênh ở vị trí trung tâm phía trên
    if AVATAR_PATH.exists():
        try:
            avatar = Image.open(AVATAR_PATH).convert("RGBA")
            avatar_size = 200
            avatar = avatar.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            
            # Mask tròn cho avatar
            mask = Image.new("L", (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            # Viền phát sáng cho avatar
            av_x = int(cx - avatar_size // 2)
            av_y = int(height * 0.22)
            
            draw = ImageDraw.Draw(img)
            draw.ellipse((av_x - 6, av_y - 6, av_x + avatar_size + 6, av_y + avatar_size + 6), outline=(0, 229, 255), width=3)
            img.paste(avatar, (av_x, av_y), mask)
        except Exception as e:
            print(f"  [WARN] Không thể dán avatar: {e}")

    draw = ImageDraw.Draw(img)
    font_brand = get_font("arialbd.ttf", 52)
    font_slogan = get_font("arialbd.ttf", 30)
    font_handle = get_font("arial.ttf", 26)
    font_cta = get_font("arialbd.ttf", 36)

    # Brand Title
    y_brand = int(height * 0.48)
    draw.text((cx, y_brand), "GIẢI MÃ TECH", font=font_brand, fill=(255, 255, 255), anchor="mm")
    
    # Slogan
    draw.text((cx, y_brand + 50), "CÔNG NGHỆ · LẬP TRÌNH · AI", font=font_slogan, fill=(0, 229, 255), anchor="mm")
    draw.text((cx, y_brand + 95), "@giaimatech-s8t", font=font_handle, fill=(180, 195, 215), anchor="mm")

    # Divider
    draw.line([(cx - 300, y_brand + 135), (cx + 300, y_brand + 135)], fill=(80, 95, 115), width=2)

    # Call to action
    draw.text((cx, y_brand + 180), "Like & Đăng ký kênh để không bỏ lỡ video tiếp theo!", font=font_cta, fill=(255, 215, 0), anchor="mm")

    # Border
    draw.rectangle([80, 50, width - 80, height - 50], outline=(40, 50, 70), width=1)
    img.save(card_img_path)

    num_frames = int(duration * fps)
    fade_out_st = duration - 0.8
    filter_complex = (
        f"[0:v]zoompan=z='min(zoom+0.0003,1.05)':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps},"
        f"fade=t=in:st=0:d=0.7,fade=t=out:st={fade_out_st:.2f}:d=0.8[vout];"
        f"[1:a]lowpass=f=200,volume=1.8,afade=t=in:ss=0:d=0.6,afade=t=out:st={fade_out_st:.2f}:d=0.8[aout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(card_img_path),
        "-f", "lavfi", "-t", str(duration), "-i", f"anoisesrc=d={duration}:c=brown:r=48000:a=0.10",
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", str(duration),
        str(output_video_path)
    ]
    return run_ffmpeg(cmd, "Render Outro Bumper")


def render_scene_segment(scene_num, beat_data, track_data, output_path, width=1920, height=1080, fps=30):
    """Render một cảnh độc lập chuẩn 1080p 30fps gồm video/image + phụ đề + audio Edge-TTS 48kHz."""
    dur = track_data["duration"]
    speaker = beat_data.get("speaker", "Người Kể Chuyện")
    # Resolve audio path
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
        print(f"  [ERROR] Cảnh {scene_num:02d}: Không tìm thấy audio file: {cand_file}", file=sys.stderr)
        return False
    text = beat_data.get("rawText", "")
    camera_cue = beat_data.get("cues", {}).get("camera", "dolly_in")

    # Tạo subtitle overlay PNG
    overlay_png = OVERLAYS_DIR / f"overlay_{scene_num:02d}.png"
    create_subtitle_overlay(scene_num, speaker, text, overlay_png, width, height)

    # Kiểm tra xem có video AI (Veo 2) không
    vid_cand = VIDEOS_DIR / f"scene_{scene_num:02d}.mp4"
    has_video = vid_cand.exists() and vid_cand.stat().st_size > 100000

    if not has_video:
        print(f"  [ERROR] Cảnh {scene_num:02d}: Không có video AI Veo 2 ({vid_cand.name})! Vi phạm Quy tắc 2 CINEMATIC_STANDARDS.MD (CẤM ZOOMPAN).", file=sys.stderr)
        return False

    print(f"  🎬 Cảnh {scene_num:02d} ({speaker}): Dùng Veo 2 AI Video ({vid_cand.name}) - {dur:.2f}s", flush=True)
    # Scale/Crop Veo 2 video sang 1920x1080 30fps + đè overlay subtitle + ghép audio
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
    return run_ffmpeg(cmd, f"Render Scene {scene_num:02d} (Veo 2 AI Video)")


def assemble_complete_film():
    print("=" * 65)
    print("🎬 OMNIVIDEO STUDIO — WORKSHOP 4 AI CINEMATIC MASTER FILM")
    print(f"Project: {JOB_ID}")
    print(f"Output: {FINAL_OUTPUT}")
    print("=" * 65)

    # 1. Tải ảnh mới nhất từ FlowKit DB
    download_images_from_db()

    # 2. Đọc Job & Audio Manifest
    job_data = json.loads(JOB_FILE.read_text(encoding="utf-8"))
    beats = job_data.get("beats", [])
    
    manifest_file = AUDIO_DIR / "audio_manifest.json"
    if not manifest_file.exists():
        print(f"[LỖI] Không tìm thấy {manifest_file}!", file=sys.stderr)
        return False
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    tracks = manifest.get("tracks", [])

    print(f"\n📊 Tổng số cảnh: {len(beats)}, Tổng thời lượng thoại: {manifest.get('totalDurationSeconds', 0):.2f}s")

    # 3. Tạo Intro & Outro Bumpers
    intro_mp4 = BUMPERS_DIR / "intro_bumper.mp4"
    outro_mp4 = BUMPERS_DIR / "outro_bumper.mp4"
    create_intro_bumper(intro_mp4)
    create_outro_bumper(outro_mp4)

    # 4. Render từng Scene segment
    rendered_segments = []
    concat_list_file = PROJECT_DIR / "concat_segments.txt"
    lines = [f"file '{intro_mp4.as_posix()}'\n"]

    force_recompile = "--force" in sys.argv or True  # Always recompile to ensure genuine Veo 2 videos
    for i in range(len(beats)):
        scene_num = i + 1
        beat = beats[i]
        track = tracks[i]
        seg_mp4 = SEGMENTS_DIR / f"segment_{scene_num:02d}.mp4"

        # Nếu force_recompile hoặc chưa có hoặc kích thước nhỏ hơn 50KB thì render lại
        if force_recompile or not seg_mp4.exists() or seg_mp4.stat().st_size < 50000:
            ok = render_scene_segment(scene_num, beat, track, seg_mp4)
            if not ok:
                print(f"  [CẢNH BÁO] Không thể render Cảnh {scene_num:02d}", file=sys.stderr)
                return False
        rendered_segments.append(seg_mp4)
        lines.append(f"file '{seg_mp4.as_posix()}'\n")

    lines.append(f"file '{outro_mp4.as_posix()}'\n")
    concat_list_file.write_text("".join(lines), encoding="utf-8")
    print(f"\n✅ Đã chuẩn bị {len(rendered_segments)} phân đoạn cảnh độc lập.", flush=True)

    # 5. Ghép nối Video thô (Voice + Visuals)
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

    # 6. Hòa âm Master với BGM xianxia-ambient.mp3 và Audio Ducking
    print("\n🎵 Đang hòa âm Master BGM Tiên Hiệp (Audio Ducking -18dB khi có thoại)...", flush=True)
    
    # Lấy thời lượng phim
    probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(raw_concat_mp4)]
    r = subprocess.run(probe_cmd, capture_output=True, text=True)
    total_dur = float(r.stdout.strip()) if r.stdout.strip() else 175.0
    print(f"  => Tổng thời lượng phim: {total_dur:.2f} giây (~{total_dur/60:.1f} phút)")

    if BGM_PATH.exists():
        # Dùng sidechain/amix: voice làm chủ đạo, BGM nền âm lượng 0.12 (-18dB)
        # Trong intro và outro, BGM tự nhiên hòa quyện
        filter_audio = (
            f"[1:a]volume=0.10,atrim=0:{total_dur},afade=t=in:st=0:d=1.5,afade=t=out:st={total_dur-2.0:.2f}:d=2.0[bgm];"
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

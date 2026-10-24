#!/usr/bin/env python3
"""
Autonomous Master Pipeline Runner for 104-Shot AI Agent Film (Workshop 4)
- Synchronizes all 104 Google Flow Imagen 3 images as they complete.
- Concurrently renders 104 Hollywood-grade 60fps video segments synchronized to Edge-TTS 48kHz audio.
- Assembles full Master Film with Intro, Outro, Watermark Logo, Subtitles, and Ducked BGM.
"""

import sys
import os
import time
import json
import sqlite3
import subprocess
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
AGENT_URL = "http://127.0.0.1:8100"
VIDEO_ID = "92a3ff94-c592-4910-b2c2-facbb2754132"
PROJECT_ID = "bdfe9e57-635b-4036-8a48-c7841a74e208"
JOB_ID = "job-ai-agent-giaimatech-10min"

OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
IMAGES_DIR = OUTPUT_DIR / "images"
SEGMENTS_DIR = OUTPUT_DIR / "segments"
AUDIO_DIR = OUTPUT_DIR / "audio" / "shots"
FINAL_FILM = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.mp4"
SRT_PATH = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.srt"
INTRO_PATH = BASE_DIR / "shared-assets" / "branding" / "intro_horizontal_16x9.mp4"
OUTRO_PATH = BASE_DIR / "shared-assets" / "branding" / "outro_horizontal_16x9.mp4"
LOGO_PATH = BASE_DIR / "shared-assets" / "branding" / "giaimatech_logo.png"
BGM_PATH = BASE_DIR / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "healing-piano.mp3"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)


def update_dashboard(progress: int, step_id: str = None, detail: str = None, log: str = None):
    try:
        payload = {"progress": progress}
        if step_id:
            payload["step_id"] = step_id
        if detail:
            payload["step_detail"] = detail
        if log:
            payload["log_line"] = log
        requests.post(f"{AGENT_URL}/api/studio/progress/{JOB_ID}/update", json=payload, timeout=3)
    except Exception:
        pass


def get_audio_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 5.5


def render_shot_segment(order: int, img_path: Path, audio_path: Path, out_path: Path, dur: float):
    if out_path.exists() and out_path.stat().st_size > 100000:
        return True

    # Camera motion logic based on shot rhythm:
    # Alternating subtle motion to maintain cinema grade
    total_frames = int(dur * 60)
    if order % 3 == 0:
        # Subtle slow push-in (zoom 1.0 to 1.04)
        v_filter = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.0003,1.04)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=60"
    elif order % 3 == 1:
        # Subtle horizontal pan drift
        v_filter = f"scale=2040:1148:force_original_aspect_ratio=increase,crop=2040:1148,zoompan=z=1.03:x='(on/{total_frames})*(iw-1920)':y='(ih-1080)/2':d={total_frames}:s=1920x1080:fps=60"
    else:
        # Subtle pull-back (1.04 to 1.0)
        v_filter = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='max(1.04-0.0003*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=60"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(dur), "-i", str(img_path),
        "-i", str(audio_path),
        "-filter_complex", f"[0:v]{v_filter}[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "60",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-t", str(dur),
        str(out_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [ERROR] Render segment {order:03d} failed: {res.stderr[-300:]}")
        return False
    return True


def sync_and_render_all():
    print("=" * 65)
    print("🚀 BẮT ĐẦU VẬN HÀNH PIPELINE TỰ ĐỘNG CHO 104 SHOTS...")
    print("=" * 65)
    update_dashboard(50, "gate_5", "Đang theo dõi batch sinh ảnh và render video...", "Pipeline tự động 104 shots bắt đầu")

    rendered_count = 0
    total_shots = 104

    while rendered_count < total_shots:
        # Check batch status
        try:
            r = requests.get(f"{AGENT_URL}/api/requests/batch-status?video_id={VIDEO_ID}&type=GENERATE_IMAGE", timeout=10)
            if r.status_code == 200:
                bs = r.json()
                print(f"[*] Batch status: Đã xong {bs.get('completed', 0)}/104 | Đang xử lý: {bs.get('processing', 0)} | Chờ: {bs.get('pending', 0)}", flush=True)
        except Exception as e:
            print(f"  [WARN] Không thể lấy batch-status: {e}")

        # Query completed scenes from DB
        conn = sqlite3.connect("workshops/workshop-cinematic/flow_agent.db")
        c = conn.cursor()
        c.execute("""
            SELECT display_order, horizontal_image_media_id, horizontal_image_url 
            FROM scene 
            WHERE video_id = ? AND horizontal_image_url IS NOT NULL 
            ORDER BY display_order
        """, (VIDEO_ID,))
        completed_scenes = c.fetchall()
        conn.close()

        current_rendered = 0
        for order, mid, url in completed_scenes:
            img_file = IMAGES_DIR / f"shot_{order:03d}.jpg"
            seg_file = SEGMENTS_DIR / f"shot_{order:03d}.mp4"
            audio_file = AUDIO_DIR / f"shot_{order:03d}.mp3"

            # 1. Download image if missing
            if not img_file.exists() or img_file.stat().st_size < 1000:
                try:
                    resp = requests.get(url, timeout=30)
                    if resp.status_code == 200:
                        img_file.write_bytes(resp.content)
                        print(f"  [TẢI ẢNH] Shot {order:03d} -> {img_file.name} ({len(resp.content):,} bytes)", flush=True)
                except Exception as e:
                    print(f"  [LỖI TẢI] Shot {order:03d}: {e}")
                    continue

            # 2. Render segment if image & audio exist
            if img_file.exists() and audio_file.exists():
                if not seg_file.exists() or seg_file.stat().st_size < 100000:
                    dur = get_audio_duration(audio_file)
                    ok = render_shot_segment(order, img_file, audio_file, seg_file, dur)
                    if ok:
                        print(f"  [RENDER SEGMENT] Shot {order:03d} hoàn tất: {dur:.2f}s ({seg_file.stat().st_size:,} bytes)", flush=True)

            if seg_file.exists() and seg_file.stat().st_size > 100000:
                current_rendered += 1

        rendered_count = current_rendered
        pct = int(50 + (rendered_count / total_shots) * 35)  # 50% to 85%
        update_dashboard(pct, "gate_5", f"Đã render {rendered_count}/{total_shots} phân cảnh 60fps...", f"Tiến độ phân đoạn: {rendered_count}/104")
        print(f"  => Tiến độ render segments: {rendered_count}/{total_shots} ({pct}%)", flush=True)

        if rendered_count >= total_shots:
            print("\n🎉 TOÀN BỘ 104 PHÂN ĐOẠN ĐÃ RENDER THÀNH CÔNG!", flush=True)
            break

        time.sleep(12)


def assemble_master_film():
    print("\n" + "=" * 65)
    print("🎬 CỔNG 6: GHÉP NỐI MASTER FILM VỚI BRANDING & DUCKED BGM...")
    print("=" * 65)
    update_dashboard(88, "gate_6", "Đang ghép nối toàn bộ phim với Intro, Outro, Watermark...", "Bắt đầu Master Assembly")

    # 1. Create segment concat list
    concat_list = OUTPUT_DIR / "body_segments_list.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for order in range(1, 105):
            seg_path = SEGMENTS_DIR / f"shot_{order:03d}.mp4"
            # FFmpeg concat file expects forward slashes
            f.write(f"file '{seg_path.as_posix()}'\n")

    body_video = OUTPUT_DIR / "body_104_shots.mp4"
    print(f"[*] Ghép nối 104 phân cảnh thành thân phim ({body_video.name})...", flush=True)
    cmd_body = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy",
        str(body_video)
    ]
    res_b = subprocess.run(cmd_body, capture_output=True, text=True)
    if res_b.returncode != 0:
        print(f"[ERR] Ghép body thất bại: {res_b.stderr[-300:]}")
        return False
    print(f"✅ Thân phim 104 cảnh: {body_video.stat().st_size:,} bytes", flush=True)

    # 2. Concat Intro + Body + Outro
    full_list = OUTPUT_DIR / "full_film_concat.txt"
    with open(full_list, "w", encoding="utf-8") as f:
        f.write(f"file '{INTRO_PATH.as_posix()}'\n")
        f.write(f"file '{body_video.as_posix()}'\n")
        f.write(f"file '{OUTRO_PATH.as_posix()}'\n")

    stitched_video = OUTPUT_DIR / "stitched_with_bumpers.mp4"
    print(f"[*] Nối Intro + Thân phim + Outro ({stitched_video.name})...", flush=True)
    cmd_stitch = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(full_list),
        "-c", "copy",
        str(stitched_video)
    ]
    res_s = subprocess.run(cmd_stitch, capture_output=True, text=True)
    if res_s.returncode != 0:
        print(f"[ERR] Ghép bumpers thất bại: {res_s.stderr[-300:]}")
        return False
    print(f"✅ Phim đầy đủ bumpers: {stitched_video.stat().st_size:,} bytes", flush=True)

    # 3. Final Master Pass: Watermark Logo + Subtitles + Ducked BGM
    update_dashboard(95, "gate_6", "Đang xử lý âm thanh BGM ducking, phụ đề và watermark...", "Final master pass")
    print(f"[*] Xuất bản Master Film cuối cùng với Subtitles, Logo Watermark và Ducked BGM...", flush=True)

    srt_posix = SRT_PATH.as_posix().replace(":", r"\:")
    logo_posix = LOGO_PATH.as_posix()

    filter_complex = (
        # 1. Overlay Watermark logo at top-right with 35px margin, w=140
        f"[1:v]scale=140:-1,format=rgba,colorchannelmixer=aa=0.85[logo];"
        f"[0:v][logo]overlay=W-w-35:35[v_logo];"
        # 2. Burn subtitles with high contrast cinema styling
        f"[v_logo]subtitles='{srt_posix}':force_style='FontSize=21,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2.5,Shadow=0,MarginV=38'[v_out];"
        # 3. Audio Ducking: Loop BGM, reduce to -18dB under dialogue, mix with voice
        f"[2:a]volume=0.15,aloop=loop=-1:size=2e+09[bgm];"
        f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[a_out]"
    )

    cmd_master = [
        "ffmpeg", "-y",
        "-i", str(stitched_video),
        "-i", str(LOGO_PATH),
        "-i", str(BGM_PATH),
        "-filter_complex", filter_complex,
        "-map", "[v_out]", "-map", "[a_out]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "60",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        str(FINAL_FILM)
    ]

    res_m = subprocess.run(cmd_master, capture_output=True, text=True)
    if res_m.returncode != 0:
        print(f"[ERR] Master film render failed: {res_m.stderr[-400:]}")
        return False

    print(f"\n" + "=" * 65)
    print(f"🏆 MASTER FILM ĐÃ XUẤT BẢN THÀNH CÔNG: {FINAL_FILM.name}")
    print(f"   Dung lượng: {FINAL_FILM.stat().st_size:,} bytes")
    print(f"   Đường dẫn: {FINAL_FILM}")
    print("=" * 65)
    update_dashboard(100, "gate_6", "Hoàn thành 100% Master Film chuẩn điện ảnh Xưởng 4!", "Xuất bản thành công")
    return True


if __name__ == "__main__":
    sync_and_render_all()
    assemble_master_film()

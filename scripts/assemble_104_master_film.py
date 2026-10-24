import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import math
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-ai-agent-giaimatech-10min"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
AUDIO_DIR = OUTPUT_DIR / "audio"
SHOTS_AUDIO_DIR = AUDIO_DIR / "shots"
FRAMES_DIR = OUTPUT_DIR / "frames"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

BRANDING_DIR = BASE_DIR / "shared-assets" / "branding"
INTRO_PATH = BRANDING_DIR / "intro_horizontal_16x9.mp4"
OUTRO_PATH = BRANDING_DIR / "outro_horizontal_16x9.mp4"
LOGO_PATH = BRANDING_DIR / "giaimatech_logo.png"
BGM_PATH = BASE_DIR / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "healing-piano.mp3"

FINAL_VIDEO_MP4 = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.mp4"
FINAL_SRT = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.srt"
FINAL_THUMB = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}-thumb.jpg"

MANIFEST_PATH = AUDIO_DIR / "audio_manifest_104_shots.json"
SPEC_PATH = OUTPUT_DIR / "STORYBOARD_SPEC_104_SHOTS.md"

def get_font(name="arialbd.ttf", size=32):
    paths = [
        Path(f"C:/Windows/Fonts/{name}"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/arial.ttf")
    ]
    for p in paths:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()

def format_srt_time(seconds: float) -> str:
    millis = int(round((seconds - int(seconds)) * 1000))
    total_sec = int(seconds)
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def generate_srt(shots_data: list, srt_path: Path):
    lines = []
    current_time = 2.0  # intro is 2.0s
    for idx, s in enumerate(shots_data, 1):
        dur = s.get("duration", 5.0)
        start_t = current_time
        end_t = current_time + dur
        lines.append(f"{idx}\n{format_srt_time(start_t)} --> {format_srt_time(end_t)}\n{s['dialogue']}\n")
        current_time = end_t
    srt_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ Đã tạo file phụ đề SRT chuẩn YouTube: {srt_path}", flush=True)

def get_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return round(float(res.stdout.strip()), 2)

def render_shot_frame(shot_info: dict, out_path: Path):
    """Render a 1920x1080 frame with enlarged 3D floating screen (70% frame) and subtitle."""
    width, height = 1920, 1080
    shot_num = shot_info["shot"]
    action = shot_info["action"]
    dialogue = shot_info["dialogue"]
    chapter = shot_info.get("chapter", "Giải Mã AI Agent")

    # Base background: Deep Cyber Navy / Tech Lab
    img = Image.new("RGBA", (width, height), (8, 12, 22, 255))
    draw = ImageDraw.Draw(img)

    # 1. Subtle Cyber Grid & Vignette
    grid_color = (0, 180, 216, 20)
    for x in range(0, width, 60):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, 60):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # 2. ENLARGED 3D FLOATING HOLOGRAPHIC DISPLAY (Occupies 70% of frame)
    # Dimensions: 1400 x 620 centered horizontally at top/mid
    screen_w = 1420
    screen_h = 620
    screen_x = (width - screen_w) // 2
    screen_y = 65

    # Glassmorphic glow outline
    draw.rounded_rectangle(
        [(screen_x - 4, screen_y - 4), (screen_x + screen_w + 4, screen_y + screen_h + 4)],
        radius=24,
        outline=(0, 229, 255, 60),
        width=4
    )
    # Glassmorphic backplate
    draw.rounded_rectangle(
        [(screen_x, screen_y), (screen_x + screen_w, screen_y + screen_h)],
        radius=20,
        fill=(12, 18, 32, 240),
        outline=(0, 229, 255, 180),
        width=2
    )

    # Screen Header Bar
    draw.rounded_rectangle(
        [(screen_x, screen_y), (screen_x + screen_w, screen_y + 55)],
        radius=20,
        fill=(16, 28, 48, 255)
    )
    # Window dots
    draw.ellipse([(screen_x + 20, screen_y + 20), (screen_x + 34, screen_y + 34)], fill=(255, 95, 86, 255))
    draw.ellipse([(screen_x + 44, screen_y + 20), (screen_x + 58, screen_y + 34)], fill=(255, 189, 46, 255))
    draw.ellipse([(screen_x + 68, screen_y + 20), (screen_x + 82, screen_y + 34)], fill=(39, 201, 63, 255))

    # Header title
    font_header = get_font("arialbd.ttf", 22)
    header_text = f"GIẢI MÃ TECH • VIRTUAL LAB 3D • {chapter.upper()}"
    draw.text((screen_x + 105, screen_y + 14), header_text, fill=(0, 229, 255, 240), font=font_header)

    # Shot badge in header
    font_badge = get_font("arialbd.ttf", 18)
    badge_str = f"SHOT {shot_num:03d} / 104"
    draw.text((screen_x + screen_w - 180, screen_y + 16), badge_str, fill=(255, 179, 0, 240), font=font_badge)

    # Screen Content: Action description & Tech Visuals
    font_action_title = get_font("arialbd.ttf", 26)
    draw.text((screen_x + 40, screen_y + 80), "⚡ HỆ THỐNG ĐIỀU PHỐI TỰ ĐỘNG (AUTONOMOUS DISPATCHER):", fill=(255, 214, 0, 255), font=font_action_title)

    font_action_desc = get_font("arial.ttf", 24)
    # Word wrap action
    words = action.split()
    action_lines = []
    cur_line = []
    for w in words:
        test_line = " ".join(cur_line + [w])
        if draw.textbbox((0, 0), test_line, font=font_action_desc)[2] < (screen_w - 100):
            cur_line.append(w)
        else:
            action_lines.append(" ".join(cur_line))
            cur_line = [w]
    if cur_line:
        action_lines.append(" ".join(cur_line))

    ay = screen_y + 125
    for al in action_lines[:3]:
        draw.text((screen_x + 40, ay), f"► {al}", fill=(220, 240, 255, 240), font=font_action_desc)
        ay += 36

    # Tech Status Mockup Box inside screen
    mock_box_y = ay + 20
    mock_box_h = screen_y + screen_h - mock_box_y - 25
    if mock_box_h > 80:
        draw.rounded_rectangle(
            [(screen_x + 40, mock_box_y), (screen_x + screen_w - 40, mock_box_y + mock_box_h)],
            radius=12,
            fill=(6, 10, 18, 220),
            outline=(0, 229, 255, 80),
            width=1
        )
        font_code = get_font("consola.ttf", 20)
        code_lines = [
            f"[AgentCore] State: EXECUTING_TASK | Goal: Autonomous IT Research 2026",
            f"[Model] Claude 3.5 / GPT-4o Reasoning Loop: Step {shot_num % 12 + 1}/12",
            f"[Tools] Connected: WebSearch, DocsReader, DockerClient, CodeSandbox",
            f"[Security] Guardrails: ACTIVE | Human-in-the-Loop Checkpoint: PASSED"
        ]
        cy = mock_box_y + 18
        for cl in code_lines:
            if cy + 24 < mock_box_y + mock_box_h:
                draw.text((screen_x + 60, cy), cl, fill=(79, 195, 247, 230), font=font_code)
                cy += 28

    # 3. Chibi Bé Byte Anchor Indicator (Bottom Left)
    font_char = get_font("arialbd.ttf", 20)
    draw.rounded_rectangle(
        [(screen_x, height - 215), (screen_x + 280, height - 165)],
        radius=14,
        fill=(0, 229, 255, 230)
    )
    draw.text((screen_x + 20, height - 202), "🤖 BÉ BYTE • AI ROBOT", fill=(10, 20, 35, 255), font=font_char)

    # 4. LOWER THIRD SUBTITLE BOX (High contrast, clean typography)
    sub_box_w = 1420
    sub_box_h = 135
    sub_box_x = (width - sub_box_w) // 2
    sub_box_y = height - sub_box_h - 20

    # Subtitle glass backplate
    draw.rounded_rectangle(
        [(sub_box_x, sub_box_y), (sub_box_x + sub_box_w, sub_box_y + sub_box_h)],
        radius=18,
        fill=(8, 12, 20, 245),
        outline=(0, 229, 255, 120),
        width=2
    )

    # Subtitle Text wrapping
    font_sub = get_font("arialbd.ttf", 34)
    words = dialogue.split()
    sub_lines = []
    cur_sub = []
    for w in words:
        test = " ".join(cur_sub + [w])
        if draw.textbbox((0, 0), test, font=font_sub)[2] < (sub_box_w - 60):
            cur_sub.append(w)
        else:
            sub_lines.append(" ".join(cur_sub))
            cur_sub = [w]
    if cur_sub:
        sub_lines.append(" ".join(cur_sub))

    text_y = sub_box_y + (sub_box_h - len(sub_lines) * 44) // 2 + 6
    for line in sub_lines:
        tbox = draw.textbbox((0, 0), line, font=font_sub)
        tx = (width - (tbox[2] - tbox[0])) // 2
        # Drop shadow
        draw.text((tx + 2, text_y + 2), line, fill=(0, 0, 0, 255), font=font_sub)
        # Main text (Crisp White)
        draw.text((tx, text_y), line, fill=(255, 255, 255, 255), font=font_sub)
        text_y += 44

    # Save PNG/JPG
    img.convert("RGB").save(out_path, "JPEG", quality=95)

def main():
    print("=" * 70, flush=True)
    print("🎬 CỔNG 6: TIẾN TRÌNH LẮP GHÉP MASTER FILM 10 PHÚT — KÊNH GIẢI MÃ TECH", flush=True)
    print("=" * 70, flush=True)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        spec_text = f.read()

    # Parse spec for actions and chapters
    spec_lines = spec_text.splitlines()
    spec_map = {}
    current_chapter = "Chương 1: Hook"
    for line in spec_lines:
        if line.startswith("#### Chương"):
            current_chapter = line.replace("####", "").strip()
        m = re.search(r'\*\s*\*\*Shot\s+(\d+)\s*\((.*?)\)\s*\[(.*?)\]:\*\*\s*(.*?)\s*\*\(Thoại:\s*\"(.*?)\"\)\*', line)
        if m:
            s_num = int(m.group(1))
            spec_map[s_num] = {
                "chapter": current_chapter,
                "action": m.group(4).strip(),
                "dialogue": m.group(5).strip(),
                "type": m.group(3).strip()
            }

    shots_data = manifest["shots"]
    for s in shots_data:
        s_num = s["shot"]
        if s_num in spec_map:
            s["action"] = spec_map[s_num]["action"]
            s["chapter"] = spec_map[s_num]["chapter"]
        else:
            s["action"] = f"Phân cảnh {s_num}: Hệ thống AI Agent vận hành"
            s["chapter"] = "Giải Mã Tech"

    # Step 1: Generate SRT Subtitles
    generate_srt(shots_data, FINAL_SRT)

    # Step 2: Render all 104 shot frames
    print("\n🎨 [BƯỚC 1/3] Đang kết xuất 104 khung hình điện ảnh 1080p với Màn hình 3D phóng to 70%...", flush=True)
    concat_list_file = OUTPUT_DIR / "concat_frames_list.txt"
    concat_lines = []

    for idx, s in enumerate(shots_data, 1):
        s_num = s["shot"]
        frame_file = FRAMES_DIR / f"frame_{s_num:03d}.jpg"
        render_shot_frame(s, frame_file)
        dur = s["duration"]
        # Format for FFmpeg concat demuxer:
        # file 'path'
        # duration X
        clean_path = str(frame_file).replace("\\", "/")
        concat_lines.append(f"file '{clean_path}'")
        concat_lines.append(f"duration {dur:.2f}")

    # Repeat last frame as per FFmpeg concat demuxer spec
    last_frame = str(FRAMES_DIR / f"frame_{shots_data[-1]['shot']:03d}.jpg").replace("\\", "/")
    concat_lines.append(f"file '{last_frame}'")

    concat_list_file.write_text("\n".join(concat_lines), encoding="utf-8")
    print(f"  ✅ Đã kết xuất 104 khung hình và lập lịch Concat: {concat_list_file}", flush=True)

    # Step 3: Concatenate all 104 voice audios into single master voice track
    print("\n🎙️ [BƯỚC 2/3] Đang nối 104 tệp âm thanh thành một luồng Master Voice 48kHz...", flush=True)
    audio_concat_list = AUDIO_DIR / "audio_concat_list.txt"
    a_lines = []
    for s in shots_data:
        f_path = str(BASE_DIR / s["file"]).replace("\\", "/")
        a_lines.append(f"file '{f_path}'")
    audio_concat_list.write_text("\n".join(a_lines), encoding="utf-8")

    master_voice_file = AUDIO_DIR / "master_voice_104_shots.mp3"
    cmd_audio = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(audio_concat_list),
        "-c", "copy",
        str(master_voice_file)
    ]
    subprocess.run(cmd_audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"  ✅ Đã xuất luồng Master Voice: {master_voice_file} ({get_duration(master_voice_file):.2f}s)", flush=True)

    # Step 4: Render Visual Slideshow + Master Voice -> Body Video
    body_video_file = OUTPUT_DIR / "body_104_shots.mp4"
    print(f"\n🎞️ [BƯỚC 3/3] Đang mã hóa video thân phim (Body 104 Shots @ 60fps 1080p)...", flush=True)
    cmd_body = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-i", str(master_voice_file),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-ac", "2",
        "-shortest",
        str(body_video_file)
    ]
    t0 = time.time()
    subprocess.run(cmd_body, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"  ✅ Thân phim 104 shots hoàn tất: {body_video_file} (Thời gian encode: {time.time()-t0:.1f}s)", flush=True)

    # Step 5: Final Master Assembly (Intro + Body + Outro + Watermark + BGM Ducking)
    print("\n🏆 TIẾN HÀNH GHÉP MASTER FILM HOÀN CHỈNH:", flush=True)
    master_concat_list = OUTPUT_DIR / "master_film_concat.txt"
    m_lines = [
        f"file '{str(INTRO_PATH).replace('\\', '/')}'",
        f"file '{str(body_video_file).replace('\\', '/')}'",
        f"file '{str(OUTRO_PATH).replace('\\', '/')}'"
    ]
    master_concat_list.write_text("\n".join(m_lines), encoding="utf-8")

    # Final Concat & Audio Mix
    cmd_final = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(master_concat_list),
        "-stream_loop", "-1", "-i", str(BGM_PATH),
        "-i", str(LOGO_PATH),
        "-filter_complex",
        "[0:v][2:v]overlay=40:40:format=auto[v_out];"
        "[1:a]volume=0.08[bgm_ducked];"
        "[0:a][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[a_out]",
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-r", "60",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        str(FINAL_VIDEO_MP4)
    ]
    t_start = time.time()
    subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    dur_final = get_duration(FINAL_VIDEO_MP4)
    print(f"\n🎉🎉🎉 MASTER FILM ĐÃ XUẤT THÀNH CÔNG RỰC RỠ!", flush=True)
    print(f"  • File MP4 Master: {FINAL_VIDEO_MP4}")
    print(f"  • Thời lượng video: {dur_final:.2f}s (~{dur_final/60:.2f} phút)")
    print(f"  • Định dạng: 1920x1080 @ 60 FPS, Âm thanh 48,000 Hz Stereo AAC")
    print(f"  • File phụ đề YouTube: {FINAL_SRT}")
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()

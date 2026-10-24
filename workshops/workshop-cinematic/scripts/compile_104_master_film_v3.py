#!/usr/bin/env python3
"""
OmniVideo Studio — Production Master Film Compiler V3 (Cinema Grade with Chatbox Dialogue)
Film: "AI Agent Là Gì? Khi AI Không Chỉ Trả Lời Mà Còn Biết Hành Động"
Channel: Giải Mã Tech (@giaimatech-s8t)

Features:
1. Replaces ugly solid black box subtitle with sleek semi-transparent cyber chatbox dialog
   (matching user reference screenshot with cyan speaker pill and white bold typography).
2. 100% audible Microsoft Edge-TTS 48kHz Vietnamese voiceover.
3. Natural 1.0x cinematic motion speed (no speedrun, no artificial compression).
4. Uniform 30.0 FPS across Intro bumper, 104 film segments, and Outro bumper.
5. Multithreaded parallel segment overlay rendering (6 workers).
6. Channel watermark logo + BGM audio ducking (-20dB) for studio broadcast balance.
"""
import sys
import os
import time
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
JOB_ID = "job-ai-agent-giaimatech-10min"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
VIDEOS_DIR = OUTPUT_DIR / "videos"
AUDIO_DIR = OUTPUT_DIR / "audio" / "shots"
SEGMENTS_V2_DIR = OUTPUT_DIR / "segments_v2"
SEGMENTS_V3_DIR = OUTPUT_DIR / "segments_v3"
SEGMENTS_V3_DIR.mkdir(parents=True, exist_ok=True)
OVERLAYS_DIR = OUTPUT_DIR / "dialogue_overlays"

FINAL_FILM = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}.mp4"
INTRO_SRC = BASE_DIR / "shared-assets" / "branding" / "intro_horizontal_16x9.mp4"
OUTRO_SRC = BASE_DIR / "shared-assets" / "branding" / "outro_horizontal_16x9.mp4"
LOGO_PATH = BASE_DIR / "shared-assets" / "branding" / "giaimatech_logo.png"
BGM_PATH = BASE_DIR / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "healing-piano.mp3"

INTRO_30FPS = OUTPUT_DIR / "intro_30fps.mp4"
OUTRO_30FPS = OUTPUT_DIR / "outro_30fps.mp4"


def get_duration(file_path: Path) -> float:
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
        return 5.0


def overlay_single_segment(shot_idx: int) -> tuple[int, Path]:
    src_seg = SEGMENTS_V2_DIR / f"segment_{shot_idx:03d}.mp4"
    overlay_png = OVERLAYS_DIR / f"overlay_{shot_idx:03d}.png"
    out_seg = SEGMENTS_V3_DIR / f"segment_{shot_idx:03d}.mp4"

    if not src_seg.exists():
        raise FileNotFoundError(f"Missing src segment {src_seg}")
    if not overlay_png.exists():
        raise FileNotFoundError(f"Missing overlay {overlay_png}")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(src_seg),
        "-i", str(overlay_png),
        "-filter_complex", "[0:v][1:v]overlay=0:0[v]",
        "-map", "[v]",
        "-map", "0:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(out_seg)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return shot_idx, out_seg


def build_master_film(total_shots: int = 104):
    start_time = time.time()
    print("=" * 75)
    print("🎬 OMNIVIDEO STUDIO — RE-RENDERING MASTER FILM V3 (CHATBOX DIALOGUE)")
    print("=" * 75)

    # 1. Overlay dialogue chatbox on all 104 segments concurrently
    print(f"\n⚡ [1/5] Đang phủ hộp thoại Chatbox Cyber lên {total_shots} phân cảnh song song...")
    results = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(overlay_single_segment, i): i for i in range(1, total_shots + 1)}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                shot_idx, p = future.result()
                results[shot_idx] = p
                if len(results) % 20 == 0 or len(results) == total_shots:
                    print(f"  -> Đã phủ Chatbox hoàn tất {len(results)}/{total_shots} phân đoạn.")
            except Exception as e:
                print(f"  ✗ Lỗi tại shot {idx}: {e}")
                return False

    # 2. Concat all 104 segments in exact numerical order
    print(f"\n🔗 [2/5] Đang ghép nối liên tục {total_shots} phân cảnh đã có Chatbox...")
    concat_list = OUTPUT_DIR / "concat_segments_v3.txt"
    lines = [f"file '{results[i].as_posix()}'" for i in range(1, total_shots + 1)]
    with open(concat_list, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    raw_body = OUTPUT_DIR / "raw_104_body_v3.mp4"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(raw_body)
    ]
    subprocess.run(cmd_concat, capture_output=True, check=True)
    body_dur = get_duration(raw_body)
    print(f"  -> Thân phim V3 hoàn tất: {body_dur:.1f}s ({raw_body.stat().st_size:,} bytes)")

    # 3. Overlay Watermark Logo onto raw body (top-right)
    print(f"\n🎨 [3/5] Đang gắn Watermark Logo kênh Giải Mã Tech...")
    logoed_body = OUTPUT_DIR / "logoed_104_body_v3.mp4"

    filter_complex_body = []
    inputs_body = ["-i", str(raw_body)]
    v_stream = "0:v"

    has_logo = LOGO_PATH.exists()
    if has_logo:
        inputs_body.extend(["-i", str(LOGO_PATH)])
        filter_complex_body.append("[1:v]scale=180:-1,format=rgba,colorchannelmixer=aa=0.85[wm]")
        filter_complex_body.append(f"[{v_stream}][wm]overlay=W-w-35:35[v_wm]")
        v_stream = "v_wm"

    cmd_logo = ["ffmpeg", "-y"] + inputs_body
    if filter_complex_body:
        cmd_logo.extend(["-filter_complex", ";".join(filter_complex_body)])
        cmd_logo.extend(["-map", f"[{v_stream}]", "-map", "0:a"])
    else:
        cmd_logo.extend(["-map", "0:v", "-map", "0:a"])

    cmd_logo.extend([
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(logoed_body)
    ])
    subprocess.run(cmd_logo, capture_output=True, check=True)
    print(f"  -> Gắn Logo thành công ({logoed_body.stat().st_size:,} bytes).")

    # 4. Concat Intro + Body + Outro
    print(f"\n🎞 [4/5] Đang ghép Intro bumper & Outro bumper...")
    full_concat_list = OUTPUT_DIR / "full_concat_v3.txt"
    full_lines = []
    if INTRO_30FPS.exists():
        full_lines.append(f"file '{INTRO_30FPS.as_posix()}'")
    full_lines.append(f"file '{logoed_body.as_posix()}'")
    if OUTRO_30FPS.exists():
        full_lines.append(f"file '{OUTRO_30FPS.as_posix()}'")

    with open(full_concat_list, "w", encoding="utf-8") as f:
        f.write("\n".join(full_lines))

    assembled_no_bgm = OUTPUT_DIR / "assembled_no_bgm_v3.mp4"
    cmd_full = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(full_concat_list),
        "-c", "copy",
        str(assembled_no_bgm)
    ]
    subprocess.run(cmd_full, capture_output=True, check=True)
    assembled_dur = get_duration(assembled_no_bgm)
    print(f"  -> Phim ghép đầy đủ: {assembled_dur:.1f}s ({assembled_no_bgm.stat().st_size:,} bytes).")

    # 5. Master Audio Mix (Voice Boost + BGM Ducking -20dB)
    print(f"\n🔊 [5/5] Đang mix Master Audio (Voice Boost 1.25x + BGM Ducking -20dB)...")
    if BGM_PATH.exists():
        filter_audio = (
            f"[0:a]volume=1.25[voice];"
            f"[1:a]aloop=loop=-1:size=2e+09,volume=0.08,atrim=0:{assembled_dur:.2f},afade=t=out:st={assembled_dur-4.0:.2f}:d=4.0[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a_out]"
        )
        cmd_final = [
            "ffmpeg", "-y",
            "-i", str(assembled_no_bgm),
            "-i", str(BGM_PATH),
            "-filter_complex", filter_audio,
            "-map", "0:v",
            "-map", "[a_out]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest",
            str(FINAL_FILM)
        ]
    else:
        cmd_final = [
            "ffmpeg", "-y",
            "-i", str(assembled_no_bgm),
            "-c", "copy",
            str(FINAL_FILM)
        ]

    subprocess.run(cmd_final, capture_output=True, check=True)
    total_elapsed = time.time() - start_time

    final_dur = get_duration(FINAL_FILM)
    final_size_mb = FINAL_FILM.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 75)
    print("🏆 XUẤT XƯỞNG MASTER FILM V3 HOÀN HẢO THÀNH CÔNG!")
    print("=" * 75)
    print(f"📍 Đường dẫn file: {FINAL_FILM}")
    print(f"⏱ Thời lượng tổng: {final_dur:.1f} giây (~{final_dur/60:.2f} phút)")
    print(f"💾 Dung lượng: {final_size_mb:.1f} MB")
    print(f"⚡ Thời gian render: {total_elapsed:.1f} giây")
    print("=" * 75)
    return True


if __name__ == "__main__":
    success = build_master_film(104)
    if not success:
        sys.exit(1)

#!/usr/bin/env python3
"""
Whiteboard Job Adapter v2.0
Converts unified job.json into whiteboard assets:
- Calls core/bin/tts.js & core/bin/phonetics.js (Single Source of Truth)
- Synthesizes & probes audio with microsecond accuracy via ffprobe
- Concatenates audio into input.mp3 with silence gaps
- Outputs synchronized input.srt and scene-01.annotation.json
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Đảm bảo stdout/stderr luôn dùng UTF-8 trên Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def get_node_env():
    env = os.environ.copy()
    node_dir = r"C:\Program Files\nodejs"
    choco_bin = r"C:\ProgramData\chocolatey\bin"
    current_path = env.get("PATH", "")
    paths_to_add = [node_dir, choco_bin]
    for p in paths_to_add:
        if p not in current_path and os.path.exists(p):
            current_path = f"{p};{current_path}"
    env["PATH"] = current_path
    return env

def call_core_tts(text: str, voice: str = "vi-VN-NamMinhNeural", fps: int = 30) -> dict:
    root_dir = Path(__file__).resolve().parent.parent.parent
    tts_cli = root_dir / "core" / "bin" / "tts.js"
    cmd = [
        "node",
        "--experimental-strip-types",
        str(tts_cli),
        "--text", text,
        "--voice", voice,
        "--fps", str(fps),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", shell=True, env=get_node_env())
    if res.returncode != 0:
        raise RuntimeError(f"Core TTS call failed: {res.stderr or res.stdout}")
    return json.loads(res.stdout.strip())

def call_core_phonetics(text: str) -> str:
    root_dir = Path(__file__).resolve().parent.parent.parent
    phonetics_cli = root_dir / "core" / "bin" / "phonetics.js"
    cmd = [
        "node",
        "--experimental-strip-types",
        str(phonetics_cli),
        "--text", text,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", shell=True, env=get_node_env())
    if res.returncode != 0:
        return text
    return res.stdout.strip()

def fmt_srt_time(ms: int) -> str:
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def concat_audio_files(audio_files: list[str], output_path: str, gap_ms: int = 250):
    """Gộp các file MP3 với khoảng lặng bằng FFmpeg concat filter."""
    if not audio_files:
        return
    if len(audio_files) == 1:
        shutil.copy(audio_files[0], output_path)
        return

    filter_complex = []
    inputs = []
    for idx, f in enumerate(audio_files):
        inputs.extend(["-i", f])
        filter_complex.append(f"[{idx}:a]adelay={gap_ms if idx > 0 else 0}|{gap_ms if idx > 0 else 0}[a{idx}];")

    concat_inputs = "".join(f"[a{i}]" for i in range(len(audio_files)))
    filter_complex.append(f"{concat_inputs}concat=n={len(audio_files)}:v=0:a=1[outa]")

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", "".join(filter_complex),
        "-map", "[outa]",
        "-ac", "2",
        "-ar", "44100",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, env=get_node_env(), check=True)

def convert_job_to_whiteboard(job_path: str, output_dir: str):
    with open(job_path, "r", encoding="utf-8") as f:
        job = json.load(f)

    out_p = Path(output_dir)
    out_p.mkdir(parents=True, exist_ok=True)
    voice_dir = out_p / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)

    voice_config = job.get("voice", {})
    voice_id = voice_config.get("voiceId", "vi-VN-NamMinhNeural")
    fps = job.get("canvas", {}).get("fps", 30)

    srt_lines = []
    current_ms = 0
    annotations_elements = []
    audio_files = []

    print(f"[*] Bat dau tong hop am thanh & dong bo phan canh cho {len(job.get('beats', []))} nhip...")

    for idx, beat in enumerate(job.get("beats", []), start=1):
        raw_text = beat.get("rawText", "")
        tts_res = call_core_tts(raw_text, voice=voice_id, fps=fps)
        
        cached_mp3 = tts_res["filePath"]
        beat_mp3 = voice_dir / f"beat-{idx:02d}.mp3"
        shutil.copy(cached_mp3, beat_mp3)
        audio_files.append(str(beat_mp3))

        dur_sec = tts_res["probe"]["durationSec"]
        dur_ms = int(dur_sec * 1000)
        start_ms = current_ms
        end_ms = start_ms + dur_ms

        normalized_text = tts_res.get("normalizedText", raw_text)

        # Dòng SRT
        srt_lines.append(f"{idx}")
        srt_lines.append(f"{fmt_srt_time(start_ms)} --> {fmt_srt_time(end_ms)}")
        srt_lines.append(normalized_text)
        srt_lines.append("")

        # Element cho annotation skeleton
        vis = beat.get("visual", {})
        annotations_elements.append({
            "id": beat.get("id", f"elem_{idx}"),
            "label": vis.get("label", f"Phan canh {idx}"),
            "sequence": idx,
            "narrativeRole": beat.get("role", "story"),
            "subtitle": normalized_text,
            "type": vis.get("type", "character"),
            "region": vis.get("region", { "x": 100 + (idx * 50) % 500, "y": 100, "width": 400, "height": 400 }),
            "reveal": {
                "direction": "top_to_bottom",
                "startMs": start_ms,
                "durationMs": dur_ms,
                "maskPaddingPx": 0,
                "protectedRegions": []
            }
        })

        current_ms = end_ms + 250  # 250ms gap giữa các câu

    # 1. Gộp audio thành input.mp3
    input_mp3_path = out_p / "input.mp3"
    try:
        concat_audio_files(audio_files, str(input_mp3_path), gap_ms=250)
        print(f"[OK] Da tao am thanh tong hop: {input_mp3_path}")
    except Exception as e:
        print(f"[WARN] Khong the gop am thanh bang FFmpeg: {e}")

    # 2. Sinh file input.srt
    srt_path = out_p / "input.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
    print(f"[OK] Da tao phu de SRT dong bo chinh xac: {srt_path}")

    # 3. Sinh file scene skeleton
    canvas = job.get("canvas", { "width": 1920, "height": 1080 })
    annotation_data = {
        "sceneId": "scene-01",
        "canvas": { "width": canvas.get("width", 1920), "height": canvas.get("height", 1080) },
        "storyBasis": job.get("title", ""),
        "sceneDurationMs": current_ms + 500,
        "elements": annotations_elements
    }

    annotation_path = out_p / "scene-01.annotation.json"
    with open(annotation_path, "w", encoding="utf-8") as f:
        json.dump(annotation_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Da tao khung phan canh: {annotation_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python job_adapter.py <path_to_job.json> <output_dir>")
        sys.exit(1)
    convert_job_to_whiteboard(sys.argv[1], sys.argv[2])

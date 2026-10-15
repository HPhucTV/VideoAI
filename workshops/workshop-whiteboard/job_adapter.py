#!/usr/bin/env python3
"""
Whiteboard Job Adapter v2.0 - Multi-scene Support
Converts unified job.json into whiteboard assets:
- Clusters beats into distinct scenes by badge, sceneId, or size threshold
- Calls core/bin/tts.js & core/bin/phonetics.js (Single Source of Truth)
- Generates scene directories: scenes/scene-XX/ with local SRT, annotation, audio & IMAGE_PROMPT.md
- Outputs global input.mp3, input.srt, and scene-01.annotation.json for full backward compatibility
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

def call_core_tts(text: str, voice: str = "vi-VN-NamMinhNeural", rate: str = "+0%", pitch: str = "+0Hz", volume: str = "+0%", fps: int = 90) -> dict:
    root_dir = Path(__file__).resolve().parent.parent.parent
    tts_cli = root_dir / "core" / "bin" / "tts.js"
    cmd = [
        "node",
        "--experimental-strip-types",
        str(tts_cli),
        "--text", text,
        "--voice", voice,
        "--rate", rate,
        "--pitch", pitch,
        "--volume", volume,
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

def cluster_beats_into_scenes(beats: list, max_beats_per_scene: int = 4) -> list[dict]:
    """
    Phân cụm nhịp (beats) thành các phân cảnh (scenes) khi:
    - beat.visual.badge thay đổi, HOẶC
    - beat.visual.sceneId thay đổi, HOẶC
    - len(current_scene_beats) >= max_beats_per_scene.
    
    Mỗi scene trả về:
    {"sceneId": f"scene-{scene_counter:02d}", "beats": current_scene_beats, "badge": current_badge or f"PHÂN CẢNH {scene_counter}"}
    """
    if not beats:
        return []

    scenes = []
    current_scene_beats = []
    current_badge = None
    current_scene_id = None
    scene_counter = 1

    for beat in beats:
        vis = beat.get("visual") or {}
        badge = vis.get("badge")
        scene_id = vis.get("sceneId")

        should_split = False
        if current_scene_beats:
            badge_changed = (badge != current_badge) if (badge is not None and current_badge is not None) else (badge is not None and current_badge is None)
            scene_id_changed = (scene_id != current_scene_id) if (scene_id is not None and current_scene_id is not None) else (scene_id is not None and current_scene_id is None)
            count_reached = len(current_scene_beats) >= max_beats_per_scene

            if badge_changed or scene_id_changed or count_reached:
                should_split = True

        if should_split:
            scenes.append({
                "sceneId": f"scene-{scene_counter:02d}",
                "beats": current_scene_beats,
                "badge": current_badge or f"PHÂN CẢNH {scene_counter}"
            })
            scene_counter += 1
            current_scene_beats = []
            current_badge = None
            current_scene_id = None

        if not current_scene_beats:
            current_badge = badge
            current_scene_id = scene_id
        else:
            if current_badge is None and badge is not None:
                current_badge = badge
            if current_scene_id is None and scene_id is not None:
                current_scene_id = scene_id

        current_scene_beats.append(beat)

    if current_scene_beats:
        scenes.append({
            "sceneId": f"scene-{scene_counter:02d}",
            "beats": current_scene_beats,
            "badge": current_badge or f"PHÂN CẢNH {scene_counter}"
        })

    return scenes

def generate_image_prompt_md(scene_id: str, scene_badge: str, job_title: str, elements_text: str, beats: list) -> str:
    """Tạo file hướng dẫn prompt ảnh Notion doodle style cho phân cảnh."""
    headlines = []
    for b in beats:
        vis = b.get("visual") or {}
        hl = vis.get("headline") or vis.get("label") or ""
        if hl:
            headlines.append(hl)
    visual_summary = ", ".join(headlines) if headlines else scene_badge

    return f"""# Visual Prompt Guidance: {scene_id} ({scene_badge})

## 1. Scene Overview
- **Scene ID**: `{scene_id}`
- **Chapter / Badge**: {scene_badge}
- **Story Context**: {job_title}
- **Number of Beats**: {len(beats)}

## 2. Visual Style Guidelines (Notion Doodle Style)
- **Style**: Minimal hand-drawn sketch, clean line art, charming whimsical vector doodle.
- **Background**: Warm cream background `#F5EBD7` (solid, clean, textured paper feel).
- **Linework**: Dark gray outlines (`#2D3748` / `#222222`), delicate pen stroke thickness, no harsh black borders.
- **Color Accents**: Extremely minimal muted pastel accents if any (or monochrome ink on cream).
- **Composition**: 16:9 widescreen layout (1920x1080), well-spaced panels or elements positioned across the canvas with ample negative space.
- **STRICT Negative Prompt**: NO text, NO typography, NO letters, NO words, NO watermark, NO 3D rendering, NO photorealism.

## 3. Scene Breakdown
{elements_text}

## 4. Suggested Image Generation Prompt (AI Image Models)
> **Prompt**: Minimalist hand-drawn doodle illustration, Notion art style, clean dark gray outline sketch on warm cream paper (#F5EBD7), whiteboard storyboard depicting {visual_summary}, charming simple character and environment line art, spacious composition, warm and cozy aesthetic, 16:9 aspect ratio, --no text words letters watermark labels typography signature
"""

def convert_job_to_whiteboard(job_path: str, output_dir: str):
    with open(job_path, "r", encoding="utf-8") as f:
        job = json.load(f)

    out_p = Path(output_dir)
    out_p.mkdir(parents=True, exist_ok=True)
    voice_dir = out_p / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)
    scenes_base_dir = out_p / "scenes"
    scenes_base_dir.mkdir(parents=True, exist_ok=True)

    voice_config = job.get("voice", {})
    voice_id = voice_config.get("voiceId", "vi-VN-NamMinhNeural")
    fps = job.get("canvas", {}).get("fps", 90)
    canvas = job.get("canvas", {"width": 1920, "height": 1080})

    beats = job.get("beats", [])
    print(f"[*] Bat dau tong hop am thanh & dong bo phan canh cho {len(beats)} nhip...")

    scenes = cluster_beats_into_scenes(beats, max_beats_per_scene=4)
    print(f"[*] Da phan cum thanh {len(scenes)} phan canh (scenes).")

    global_srt_lines = []
    global_current_ms = 0
    all_audio_files = []
    global_annotations_elements = []

    global_beat_idx = 1
    first_scene_annotation = None

    for s_idx, scene in enumerate(scenes, start=1):
        scene_id = scene["sceneId"]
        scene_badge = scene.get("badge", f"PHÂN CẢNH {s_idx}")
        scene_beats = scene["beats"]

        scene_dir = scenes_base_dir / scene_id
        scene_dir.mkdir(parents=True, exist_ok=True)

        scene_srt_lines = []
        scene_audio_files = []
        scene_annotations_elements = []
        scene_current_ms = 0
        image_prompt_elements = []

        print(f"[*] Xu ly {scene_id} ({scene_badge}) gom {len(scene_beats)} nhip...")

        for local_idx, beat in enumerate(scene_beats, start=1):
            raw_text = beat.get("rawText", "")
            beat_voice = beat.get("voice", {})
            b_voice = beat_voice.get("voiceId", voice_id)
            b_rate = beat_voice.get("rate", voice_config.get("rate", "+0%"))
            b_pitch = beat_voice.get("pitch", voice_config.get("pitch", "+0Hz"))
            b_volume = beat_voice.get("volume", voice_config.get("volume", "+0%"))

            tts_res = call_core_tts(raw_text, voice=b_voice, rate=b_rate, pitch=b_pitch, volume=b_volume, fps=fps)

            cached_mp3 = tts_res["filePath"]
            beat_mp3 = voice_dir / f"beat-{global_beat_idx:02d}.mp3"
            shutil.copy(cached_mp3, beat_mp3)

            all_audio_files.append(str(beat_mp3))
            scene_audio_files.append(str(beat_mp3))

            dur_sec = tts_res["probe"]["durationSec"]
            dur_ms = int(dur_sec * 1000)

            # Local timing (starts at 0)
            local_start_ms = scene_current_ms
            local_end_ms = local_start_ms + dur_ms

            # Global timing (continuous)
            global_start_ms = global_current_ms
            global_end_ms = global_start_ms + dur_ms

            normalized_text = tts_res.get("normalizedText", raw_text)

            # Local scene SRT
            scene_srt_lines.append(f"{local_idx}")
            scene_srt_lines.append(f"{fmt_srt_time(local_start_ms)} --> {fmt_srt_time(local_end_ms)}")
            scene_srt_lines.append(normalized_text)
            scene_srt_lines.append("")

            # Global SRT
            global_srt_lines.append(f"{global_beat_idx}")
            global_srt_lines.append(f"{fmt_srt_time(global_start_ms)} --> {fmt_srt_time(global_end_ms)}")
            global_srt_lines.append(normalized_text)
            global_srt_lines.append("")

            # Visual config
            vis = beat.get("visual") or {}
            region = vis.get("region", {
                "x": 100 + ((local_idx - 1) % 3) * 580,
                "y": 80 if local_idx <= 3 else 560,
                "width": 550,
                "height": 450
            })

            # Local annotation element
            scene_annotations_elements.append({
                "id": beat.get("id", f"elem_{global_beat_idx}"),
                "label": vis.get("label", f"Phan canh {global_beat_idx}"),
                "sequence": local_idx,
                "narrativeRole": beat.get("role", "story"),
                "subtitle": normalized_text,
                "type": vis.get("type", "character"),
                "region": region,
                "reveal": {
                    "direction": "top_to_bottom",
                    "startMs": local_start_ms,
                    "durationMs": dur_ms,
                    "maskPaddingPx": 0,
                    "protectedRegions": []
                }
            })

            # Global annotation element
            global_annotations_elements.append({
                "id": beat.get("id", f"elem_{global_beat_idx}"),
                "label": vis.get("label", f"Phan canh {global_beat_idx}"),
                "sequence": global_beat_idx,
                "narrativeRole": beat.get("role", "story"),
                "subtitle": normalized_text,
                "type": vis.get("type", "character"),
                "region": region,
                "reveal": {
                    "direction": "top_to_bottom",
                    "startMs": global_start_ms,
                    "durationMs": dur_ms,
                    "maskPaddingPx": 0,
                    "protectedRegions": []
                }
            })

            # Prompt elements
            headline = vis.get("headline", "")
            subhead = vis.get("subhead", "")
            label = vis.get("label", "")
            image_prompt_elements.append(
                f"- **Nhịp {local_idx} ({beat.get('id', '')})**: {label or headline} — {subhead or normalized_text[:120]}"
            )

            pause_gap = beat.get("voice", {}).get("pauseAfterMs", 250)
            scene_current_ms = local_end_ms + pause_gap
            global_current_ms = global_end_ms + pause_gap
            global_beat_idx += 1

        # 1. Write local scene-XX.srt
        scene_srt_path = scene_dir / f"{scene_id}.srt"
        with open(scene_srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(scene_srt_lines))

        # 2. Write local scene-XX.annotation.json
        scene_duration_ms = scene_current_ms + 500
        scene_annotation_data = {
            "sceneId": scene_id,
            "badge": scene_badge,
            "canvas": {"width": canvas.get("width", 1920), "height": canvas.get("height", 1080)},
            "storyBasis": job.get("title", ""),
            "sceneDurationMs": scene_duration_ms,
            "elements": scene_annotations_elements
        }
        scene_annotation_path = scene_dir / f"{scene_id}.annotation.json"
        with open(scene_annotation_path, "w", encoding="utf-8") as f:
            json.dump(scene_annotation_data, f, ensure_ascii=False, indent=2)

        if s_idx == 1:
            first_scene_annotation = scene_annotation_data

        # 3. Concatenate audio for this scene into scenes/scene-XX/scene-XX.mp3
        scene_mp3_path = scene_dir / f"{scene_id}.mp3"
        try:
            concat_audio_files(scene_audio_files, str(scene_mp3_path), gap_ms=250)
            print(f"[OK] Da tao am thanh phan canh {scene_id}: {scene_mp3_path}")
        except Exception as e:
            print(f"[WARN] Khong the gop am thanh cho {scene_id}: {e}")

        # 4. Write scenes/scene-XX/IMAGE_PROMPT.md
        prompt_content = generate_image_prompt_md(
            scene_id=scene_id,
            scene_badge=scene_badge,
            job_title=job.get("title", ""),
            elements_text="\n".join(image_prompt_elements),
            beats=scene_beats
        )
        scene_prompt_path = scene_dir / "IMAGE_PROMPT.md"
        with open(scene_prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt_content)
        print(f"[OK] Da tao tai nguyen phan canh: {scene_dir}")

    # Backward compatibility: global concatenated input.mp3 and input.srt at output_dir
    input_mp3_path = out_p / "input.mp3"
    try:
        concat_audio_files(all_audio_files, str(input_mp3_path), gap_ms=250)
        print(f"[OK] Da tao am thanh tong hop: {input_mp3_path}")
    except Exception as e:
        print(f"[WARN] Khong the gop am thanh bang FFmpeg: {e}")

    srt_path = out_p / "input.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(global_srt_lines))
    print(f"[OK] Da tao phu de SRT tong hop: {srt_path}")

    # Also write scene-01.annotation.json at output_dir for backward compatibility
    annotation_path = out_p / "scene-01.annotation.json"
    legacy_annotation_data = first_scene_annotation or {
        "sceneId": "scene-01",
        "canvas": {"width": canvas.get("width", 1920), "height": canvas.get("height", 1080)},
        "storyBasis": job.get("title", ""),
        "sceneDurationMs": global_current_ms + 500,
        "elements": global_annotations_elements
    }
    with open(annotation_path, "w", encoding="utf-8") as f:
        json.dump(legacy_annotation_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Da tao khung phan canh tuong thich: {annotation_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python job_adapter.py <path_to_job.json> <output_dir>")
        sys.exit(1)
    convert_job_to_whiteboard(sys.argv[1], sys.argv[2])

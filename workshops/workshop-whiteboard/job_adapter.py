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
import re
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
    env = get_node_env()
    node_bin = shutil.which("node", path=env.get("PATH")) or "node"
    cmd = [
        node_bin,
        "--experimental-strip-types",
        str(tts_cli),
        "--text", text,
        "--voice", voice,
        "--rate", rate,
        "--pitch", pitch,
        "--volume", volume,
        "--fps", str(fps),
    ]
    import time
    for attempt in range(1, 4):
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", shell=False, env=env)
        if res.returncode == 0:
            try:
                return json.loads(res.stdout.strip())
            except Exception:
                pass
        time.sleep(attempt * 1.5)
    raise RuntimeError(f"Core TTS call failed after 3 attempts: {res.stderr or res.stdout}")

def call_core_phonetics(text: str) -> str:
    root_dir = Path(__file__).resolve().parent.parent.parent
    phonetics_cli = root_dir / "core" / "bin" / "phonetics.js"
    env = get_node_env()
    node_bin = shutil.which("node", path=env.get("PATH")) or "node"
    cmd = [
        node_bin,
        "--experimental-strip-types",
        str(phonetics_cli),
        "--text", text,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", shell=False, env=env)
    if res.returncode != 0:
        return text
    return res.stdout.strip()

def fmt_srt_time(ms: int) -> str:
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def extract_characters_from_metadata(metadata: dict | None) -> list[str]:
    if not metadata:
        return []
    raw_chars = metadata.get("characters", [])
    known = []
    for c in raw_chars:
        base_name = re.split(r"[\(,:;\-]", c)[0].strip()
        if base_name:
            known.append(base_name)
            words = base_name.split()
            if len(words) >= 3:
                known.append(" ".join(words[-2:]))
    return list(dict.fromkeys(known))

def resolve_speaker_voice(speaker_name: str, job_meta: dict | None = None, default_voice_config: dict | None = None) -> dict:
    name_clean = speaker_name.lower().strip()

    if job_meta and "characters_voice" in job_meta:
        chars_voice = job_meta["characters_voice"]
        # Check narrator aliases first if speaker is narrator
        is_narrator = any(w in name_clean for w in ["narrator", "kể chuyện", "người kể", "dẫn truyện"])
        if is_narrator:
            for k, v in chars_voice.items():
                if any(w in k.lower() for w in ["narrator", "kể chuyện", "người kể", "dẫn truyện"]):
                    return v

        for k, v in chars_voice.items():
            k_lower = k.lower().strip()
            if k_lower in name_clean or name_clean in k_lower:
                return v

    default_rate = default_voice_config.get("rate", "-4%") if default_voice_config else "-4%"
    default_pitch = default_voice_config.get("pitch", "+0Hz") if default_voice_config else "+0Hz"
    default_volume = default_voice_config.get("volume", "+0%") if default_voice_config else "+0%"

    # Female voice (Hạ Vi, Nhược Hy, etc.)
    if any(k in name_clean for k in ["hạ vi", "ha vi", "nhược hy", "nhuoc hy", "nữ", "female", "cô gái", "bà", "mẹ"]):
        return {
            "voice": "vi-VN-HoaiMyNeural",
            "rate": default_rate,
            "pitch": "+0Hz",
            "volume": default_volume,
        }

    # Male boss / cold / deep voice (Đình Phong, Cảnh Thâm, etc.)
    if any(k in name_clean for k in ["đình phong", "dinh phong", "cảnh thâm", "canh tham", "tổng tài", "chủ tịch", "boss"]):
        return {
            "voice": "vi-VN-NamMinhNeural",
            "rate": default_rate,
            "pitch": "-5Hz",
            "volume": default_volume,
        }

    # Assistant / younger male voice (Kiên, Giang Thừa, etc.)
    if any(k in name_clean for k in ["kiên", "kien", "giang thừa", "giang thua", "trợ lý", "tro ly"]):
        return {
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+0%",
            "pitch": "+2Hz",
            "volume": default_volume,
        }

    # Default Narrator voice
    return {
        "voice": default_voice_config.get("voiceId", "vi-VN-NamMinhNeural") if default_voice_config else "vi-VN-NamMinhNeural",
        "rate": default_rate,
        "pitch": default_pitch,
        "volume": default_volume,
    }

def parse_dialogue_segments(text: str, known_speakers: list[str] | None = None) -> list[dict]:
    if not text or not text.strip():
        return []

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    script_pattern = re.compile(r"^([A-ZÀ-Ỹa-zà-ỹ0-9_ ]+?)(?:\s*\([^)]*\))?\s*:\s*(.+)$", re.UNICODE)

    # 1. Script format across multiple lines
    if len(lines) > 1 and all(script_pattern.match(l) for l in lines):
        segments = []
        for line in lines:
            m = script_pattern.match(line)
            if m:
                spk = m.group(1).strip()
                dlg = m.group(2).strip()
                segments.append({"speaker": spk, "text": dlg})
        return segments

    # 2. Single line script format: "Speaker: dialogue"
    if len(lines) == 1:
        m = script_pattern.match(lines[0])
        if m:
            spk = m.group(1).strip()
            dlg = m.group(2).strip()
            if len(spk.split()) <= 4:
                return [{"speaker": spk, "text": dlg}]

    # 3. Embedded narrative prose
    if not known_speakers:
        known_speakers = ["Hạ Vi", "Lâm Hạ Vi", "Đình Phong", "Trần Đình Phong", "Kiên", "Trợ lý Kiên"]

    if ":" in text:
        parts = text.split(":")
        segments = []

        p0 = parts[0].strip()
        current_speaker = "narrator"
        for spk in known_speakers:
            if spk.lower() in p0.lower():
                current_speaker = spk
                break

        segments.append({"speaker": "narrator", "text": p0 + ":"})

        for i in range(1, len(parts)):
            part_content = parts[i].strip()
            is_last = (i == len(parts) - 1)

            if is_last:
                if part_content:
                    segments.append({"speaker": current_speaker, "text": part_content})
            else:
                sentences = re.split(r"(?<=[.!?])\s+", part_content)
                split_idx = len(sentences)
                next_speaker = "narrator"

                for s_idx in range(len(sentences) - 1, -1, -1):
                    s = sentences[s_idx]
                    found = False
                    for spk in known_speakers:
                        if spk.lower() in s.lower():
                            next_speaker = spk
                            found = True
                            break
                    if found:
                        split_idx = s_idx
                        break

                dialogue_text = " ".join(sentences[:split_idx]).strip()
                narration_text = " ".join(sentences[split_idx:]).strip()

                if dialogue_text:
                    segments.append({"speaker": current_speaker, "text": dialogue_text})
                if narration_text:
                    segments.append({"speaker": "narrator", "text": narration_text + ":"})

                current_speaker = next_speaker

        segments = [s for s in segments if s["text"].strip()]
        if segments:
            return segments

    return [{"speaker": "narrator", "text": text.strip()}]

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
    try:
        subprocess.run(cmd, capture_output=True, env=get_node_env(), check=True)
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else str(e.stderr)
        print(f"[ERR] FFmpeg concat audio failed: {err_msg}", file=sys.stderr)
        raise RuntimeError(f"FFmpeg concat audio failed: {err_msg}") from e

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

def generate_subagent_prompt(scene_id: str, scene_badge: str, job_title: str, beats: list, target_path: str = "") -> str:
    """Tạo prompt chuẩn hóa cho subagent 'image-generator' tạo ảnh minh họa 3 khung cảnh 16:9."""
    vignettes = []
    positions = ["Left vignette", "Center vignette", "Right vignette"]
    for i, b in enumerate(beats[:3]):
        vis = b.get("visual") or {}
        hl = vis.get("headline", "")
        sub = vis.get("subhead", "")
        lbl = vis.get("label", "")
        pos = positions[i] if i < len(positions) else f"Vignette {i+1}"
        desc_parts = [p for p in [hl, sub, lbl] if p]
        desc = " — ".join(desc_parts) if desc_parts else f"Visual scene for beat {b.get('id', i+1)}"
        vignettes.append(f"  {i+1}. {pos}: {desc}")

    vignettes_str = "\n".join(vignettes)
    save_instruction = f"\nSave the image as an opaque 16:9 PNG file at:\n{target_path}\nReport back the absolute path of the generated image." if target_path else ""

    return (
        f"Create one landscape 16:9 source illustration for a whiteboard animation of '{job_title}' - {scene_badge} ({scene_id}).\n"
        f"Style requirements:\n"
        f"- Absolutely NO text, letters, words, numbers, captions, labels, logos, or watermarks anywhere.\n"
        f"- Minimal hand-drawn sketch, clean Notion-like doodle aesthetic, dark gray crisp outlines (#2D3748) on uniform warm cream paper (#F5EBD7), lots of negative space.\n"
        f"- Layout: {len(beats[:3])} distinct narrative vignettes arranged neatly side-by-side from left to right with clear empty space between them (Landscape 16:9, 1920x1080):\n"
        f"{vignettes_str}\n"
        f"- Color: Solid warm cream background (#F5EBD7), dark gray outlines, minimal subtle pastel or monochrome ink accents only.{save_instruction}"
    )

def generate_image_prompt_md(scene_id: str, scene_badge: str, job_title: str, elements_text: str, beats: list) -> str:
    """Tạo file hướng dẫn prompt ảnh Notion doodle style cho phân cảnh."""
    headlines = []
    for b in beats:
        vis = b.get("visual") or {}
        hl = vis.get("headline") or vis.get("label") or ""
        if hl:
            headlines.append(hl)
    visual_summary = ", ".join(headlines) if headlines else scene_badge
    subagent_prompt = generate_subagent_prompt(scene_id, scene_badge, job_title, beats)

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

## 5. Antigravity 'image-generator' Subagent Protocol
```text
{subagent_prompt}
```
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

    voice_config = job.get("voice") or {}
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
    manifest_scenes = []

    job_meta = job.get("metadata") or {}
    known_speakers = extract_characters_from_metadata(job_meta)
    if known_speakers:
        print(f"[*] Nhan dien {len(known_speakers)} nhan vat trong kich ban: {known_speakers}")

    global_beat_idx = 1

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
            beat_voice = beat.get("voice") or {}
            explicit_speaker = beat.get("speaker") or (beat.get("voice") or {}).get("speaker")

            if explicit_speaker:
                segments = [{"speaker": explicit_speaker, "text": raw_text}]
            elif beat_voice.get("voiceId"):
                segments = [{"speaker": "custom", "text": raw_text, "voice": beat_voice}]
            else:
                segments = parse_dialogue_segments(raw_text, known_speakers=known_speakers)

            segment_audio_files = []
            segment_normalized_texts = []
            beat_start_local_ms = scene_current_ms
            beat_start_global_ms = global_current_ms

            for seg_idx, seg in enumerate(segments, start=1):
                seg_text = seg["text"]
                seg_spk = seg.get("speaker", "narrator")

                if "voice" in seg:
                    v_cfg = seg["voice"]
                else:
                    v_cfg = resolve_speaker_voice(seg_spk, job_meta, default_voice_config=voice_config)

                s_voice = v_cfg.get("voice", beat_voice.get("voiceId", voice_id))
                s_rate = v_cfg.get("rate", beat_voice.get("rate", voice_config.get("rate", "+0%")))
                s_pitch = v_cfg.get("pitch", beat_voice.get("pitch", voice_config.get("pitch", "+0Hz")))
                s_volume = v_cfg.get("volume", beat_voice.get("volume", voice_config.get("volume", "+0%")))

                tts_res = call_core_tts(seg_text, voice=s_voice, rate=s_rate, pitch=s_pitch, volume=s_volume, fps=fps)
                cached_mp3 = Path(tts_res["filePath"])
                if not cached_mp3.exists() or cached_mp3.stat().st_size == 0:
                    raise RuntimeError(f"TTS result empty or missing: {cached_mp3}")
                seg_mp3 = voice_dir / f"beat-{global_beat_idx:02d}-seg-{seg_idx:02d}.mp3"
                shutil.copy(cached_mp3, seg_mp3)
                segment_audio_files.append(str(seg_mp3))

                seg_dur_sec = tts_res["probe"]["durationSec"]
                seg_dur_ms = int(seg_dur_sec * 1000)

                seg_local_start = scene_current_ms
                seg_local_end = seg_local_start + seg_dur_ms
                seg_global_start = global_current_ms
                seg_global_end = seg_global_start + seg_dur_ms

                scene_current_ms += seg_dur_ms
                global_current_ms += seg_dur_ms

                norm_text = tts_res.get("normalizedText", seg_text)
                segment_normalized_texts.append(norm_text)

                # Local scene SRT
                scene_srt_idx = len(scene_srt_lines) // 4 + 1
                scene_srt_lines.append(f"{scene_srt_idx}")
                scene_srt_lines.append(f"{fmt_srt_time(seg_local_start)} --> {fmt_srt_time(seg_local_end)}")
                scene_srt_lines.append(norm_text)
                scene_srt_lines.append("")

                # Global SRT
                global_srt_idx = len(global_srt_lines) // 4 + 1
                global_srt_lines.append(f"{global_srt_idx}")
                global_srt_lines.append(f"{fmt_srt_time(seg_global_start)} --> {fmt_srt_time(seg_global_end)}")
                global_srt_lines.append(norm_text)
                global_srt_lines.append("")

            # Concat segments into beat_mp3
            beat_mp3 = voice_dir / f"beat-{global_beat_idx:02d}.mp3"
            concat_audio_files(segment_audio_files, str(beat_mp3), gap_ms=100)

            all_audio_files.append(str(beat_mp3))
            scene_audio_files.append(str(beat_mp3))

            dur_ms = scene_current_ms - beat_start_local_ms
            local_start_ms = beat_start_local_ms
            local_end_ms = scene_current_ms
            global_start_ms = beat_start_global_ms
            global_end_ms = global_current_ms

            normalized_text = " ".join(segment_normalized_texts)

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

            pause_gap = (beat.get("voice") or {}).get("pauseAfterMs", 250)
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

        # 5. Write scenes/scene-XX/image_generator_brief.json
        target_scene_png = scene_dir / f"{scene_id}.png"
        subagent_prompt_full = generate_subagent_prompt(
            scene_id=scene_id,
            scene_badge=scene_badge,
            job_title=job.get("title", ""),
            beats=scene_beats,
            target_path=str(target_scene_png.resolve())
        )
        brief_data = {
            "sceneId": scene_id,
            "badge": scene_badge,
            "jobTitle": job.get("title", ""),
            "targetPng": str(target_scene_png.resolve()),
            "beatsCount": len(scene_beats),
            "subagentPrompt": subagent_prompt_full
        }
        with open(scene_dir / "image_generator_brief.json", "w", encoding="utf-8") as bf:
            json.dump(brief_data, bf, ensure_ascii=False, indent=2)
        manifest_scenes.append(brief_data)

        print(f"[OK] Da tao tai nguyen phan canh: {scene_dir}")

    # Export consolidated IMAGE_GENERATOR_MANIFEST.json for the full video production
    manifest_data = {
        "jobId": job.get("jobId", out_p.name),
        "jobTitle": job.get("title", ""),
        "standardGenerator": "image-generator",
        "style": {
            "aspectRatio": "16:9",
            "resolution": "1920x1080",
            "paperColor": "#F5EBD7",
            "strokeColor": "#2D3748",
            "aesthetic": "Notion Doodle Minimalist Sketch"
        },
        "totalScenes": len(scenes),
        "scenes": manifest_scenes
    }
    manifest_path = out_p / "IMAGE_GENERATOR_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest_data, mf, ensure_ascii=False, indent=2)
    print(f"[OK] Da tao manifest Generative AI 'image-generator': {manifest_path}")

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

    # Root backward-compatibility annotation sync: full global timeline matching input.mp3 & input.srt
    annotation_path = out_p / "scene-01.annotation.json"
    legacy_annotation_data = {
        "sceneId": "scene-01",
        "canvas": {"width": canvas.get("width", 1920), "height": canvas.get("height", 1080)},
        "storyBasis": job.get("title", ""),
        "sceneDurationMs": global_current_ms + 500,
        "elements": global_annotations_elements
    }
    with open(annotation_path, "w", encoding="utf-8") as f:
        json.dump(legacy_annotation_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Da tao khung phan canh tuong thich toan cuc: {annotation_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python job_adapter.py <path_to_job.json> <output_dir>")
        sys.exit(1)
    convert_job_to_whiteboard(sys.argv[1], sys.argv[2])

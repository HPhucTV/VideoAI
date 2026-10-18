#!/usr/bin/env python3
"""
Blender Job Adapter
Converts unified job.json into Blender 3D timeline specification:
- Computes start/end frames per shot based on audio duration and fps
- Maps camera movements from visual cues and beat roles (dolly_in, orbit, dolly_out, static)
- Cleans dialogue text and resolves character voices/roles
"""
import json
import os
import re
import sys
from pathlib import Path

# Đảm bảo stdout/stderr luôn dùng UTF-8 trên Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from pose_engine import map_beat_to_pose
except ImportError:
    from workshops.workshop_blender.pose_engine import map_beat_to_pose

FEMALE_INDICATORS = ("tiên tử", "nữ", "muội", "cô", "nàng", "vân hy")

NARRATOR_ALIASES = {"người kể chuyện", "dẫn truyện", "kể chuyện", "narrator"}
REPORTING_VERBS = {
    "nói", "hỏi", "gầm lên", "quát", "đáp", "nghĩ",
    "cười lớn", "la lên", "thì thầm", "hô", "thốt", "kêu", "hét"
}

CAMERA_CUE_MAP = {
    "zoom_in_punch": "dolly_in",
    "dolly_in": "dolly_in",
    "zoom_in": "dolly_in",
    "pan_right": "orbit",
    "pan_left": "orbit",
    "orbit": "orbit",
    "zoom_out_slow": "dolly_out",
    "dolly_out": "dolly_out",
    "zoom_out": "dolly_out",
    "static": "static",
}

ROLE_CAMERA_MAP = {
    "hook_teaser": "dolly_in",
    "climax": "dolly_in",
    "action": "dolly_in",
    "hook_intro": "orbit",
    "intro": "orbit",
}

def sanitize_dialogue_text(raw_text: str, known_speakers: list[str] | None = None) -> tuple[str | None, str]:
    """
    Tách tiền tố tên nhân vật / vai dẫn truyện ra khỏi lời thoại theo quy tắc ngữ nghĩa chặt chẽ.
    Trả về (speaker_name, clean_text) hoặc (None, raw_text.strip()).
    """
    if not raw_text or ":" not in raw_text:
        return None, raw_text.strip() if raw_text else ""

    parts = raw_text.split(":", 1)
    prefix = parts[0].strip()
    rest = parts[1].strip()

    # Loại trừ nếu prefix chứa chữ số (ví dụ mốc thời gian "10:30", tập số, v.v.)
    if any(c.isdigit() for c in prefix):
        return None, raw_text.strip()

    # Loại bỏ biểu cảm trong ngoặc đơn: "Sở Thiên Kiêu (lạnh lùng)" -> "Sở Thiên Kiêu"
    base_prefix = re.sub(r"\s*\([^)]*\)", "", prefix).strip()
    if not base_prefix:
        return None, raw_text.strip()

    base_prefix_clean = base_prefix.strip(" -—\"'“”")
    if not base_prefix_clean:
        return None, raw_text.strip()

    base_lower = base_prefix_clean.lower()

    # 1. Kiểm tra Whitelist: known_speakers hoặc bí danh dẫn truyện
    if known_speakers:
        for k in known_speakers:
            if base_lower == k.strip().lower():
                return k, rest

    if base_lower in NARRATOR_ALIASES:
        return base_prefix_clean, rest

    # 2. Kiểm tra Heuristic Title Case (1 đến 4 từ)
    words = base_prefix_clean.split()
    if 1 <= len(words) <= 4:
        # Nếu tận cùng bằng động từ tường thuật -> câu kể, không phải tên nhân vật
        is_reporting = any(
            base_lower == rv or base_lower.endswith(" " + rv)
            for rv in REPORTING_VERBS
        )
        if is_reporting:
            return None, raw_text.strip()

        # Nếu tất cả các từ đều viết hoa chữ cái đầu
        if all(w[0].isupper() for w in words):
            return base_prefix_clean, rest

    return None, raw_text.strip()

def resolve_camera_action(cues: dict | None, role: str) -> str:
    """
    Ánh xạ camera action từ cues hoặc suy luận từ role.
    Cues có độ ưu tiên cao hơn role.
    """
    if cues and isinstance(cues, dict):
        cam = cues.get("camera")
        if cam:
            cam_str = str(cam).strip().lower()
            if cam_str in CAMERA_CUE_MAP:
                return CAMERA_CUE_MAP[cam_str]

    # Suy luận từ role nếu cues không chỉ định camera
    role_key = (role or "").strip().lower()
    return ROLE_CAMERA_MAP.get(role_key, "static")

def resolve_character_model(speaker: str | None, character_models: dict | None = None) -> str:
    """
    Xác định model ID cho nhân vật (ví dụ: 'nam-chinh', 'nu-chinh')
    dựa trên cấu hình metadata.character_models hoặc suy luận ngữ nghĩa từ tên/vai.
    """
    if not speaker:
        return "nam-chinh"

    spk_norm = str(speaker).strip().lower()

    # 1. Tra cứu cấu hình tường minh từ metadata
    if character_models and isinstance(character_models, dict):
        for k, v in character_models.items():
            if k.strip().lower() == spk_norm:
                return v

    # 2. Heuristic phát hiện nhân vật nữ
    if any(ind in spk_norm for ind in FEMALE_INDICATORS):
        return "nu-chinh"

    # 3. Fallback mặc định cho nam chính / người kể chuyện / nhân vật nam
    return "nam-chinh"

def build_blender_timeline_spec(
    job_dict: dict,
    audio_durations: dict[str, float],
    default_fps: int = 30
) -> dict:
    """
    Xây dựng timeline spec cho Blender từ job_dict và thời lượng audio từng beat.
    """
    canvas = job_dict.get("canvas") or {}
    fps = canvas.get("fps", default_fps)
    res = [canvas.get("width", 1280), canvas.get("height", 720)]
    metadata = job_dict.get("metadata") or {}
    known_speakers = metadata.get("characters", [])
    char_models_map = metadata.get("character_models", {})

    current_frame = 1
    shots = []

    for beat in job_dict.get("beats", []):
        beat_id = beat.get("id", "")
        dur_sec = audio_durations.get(beat_id, 3.0)
        beat_frames = max(1, round(dur_sec * fps))
        start_f = current_frame
        end_f = current_frame + beat_frames - 1

        spk, clean = sanitize_dialogue_text(beat.get("rawText", ""), known_speakers)
        speaker = beat.get("speaker") or spk or "Người Kể Chuyện"
        cam_act = resolve_camera_action(beat.get("cues"), beat.get("role", ""))
        char_model = resolve_character_model(speaker, char_models_map)
        char_pose = map_beat_to_pose(beat.get("role", ""), speaker)

        shot = {
            "id": beat_id,
            "role": beat.get("role", ""),
            "speaker": speaker,
            "clean_text": clean,
            "raw_text": beat.get("rawText", ""),
            "duration_sec": dur_sec,
            "start_frame": start_f,
            "end_frame": end_f,
            "camera_action": cam_act,
            "character_model": char_model,
            "character_pose": char_pose,
        }
        shots.append(shot)
        current_frame = end_f + 1

    total_frames = current_frame - 1 if shots else 0

    return {
        "jobId": job_dict.get("jobId", "untitled"),
        "fps": fps,
        "resolution": res,
        "total_frames": total_frames,
        "shots": shots,
        "metadata": metadata,
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python job_adapter.py <path_to_job.json> <output_spec.json>")
        sys.exit(1)

    job_file = Path(sys.argv[1])
    out_file = Path(sys.argv[2])

    with open(job_file, "r", encoding="utf-8") as f:
        job_data = json.load(f)

    # Nếu không có file audio duration, mặc định 3.0s mỗi beat
    durations = {b.get("id", ""): 3.0 for b in job_data.get("beats", [])}
    spec = build_blender_timeline_spec(job_data, durations)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)

    print(f"[OK] Da tao Blender Timeline Spec: {out_file}")

#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4 (Cinematic AI Video Studio)
Job Adapter: Chuyển đổi hợp đồng dữ liệu job.json sang FlowKit Project, Characters và Scenes.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add workshop-cinematic root to path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agent.db.schema import init_db, close_db
from agent.db import crud

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("cinematic_adapter")


def map_camera_to_video_prompt(camera_cue: str | None, base_prompt: str) -> str:
    """Ánh xạ visual cues camera trong job.json sang câu lệnh chuyển động camera của Veo / Omni Flash."""
    cam_map = {
        "orbit_360": "360-degree smooth cinematic orbit camera movement circling around the subject",
        "dolly_in": "Slow dramatic dolly in zoom approaching the character",
        "dolly_out": "Epic wide dolly out crane shot revealing the grand surrounding environment",
        "pan_left": "Smooth horizontal camera pan from right to left",
        "pan_right": "Smooth horizontal camera pan from left to right",
        "tilt_up": "Dramatic tilt up from ground to the towering scene above",
        "tilt_down": "High-angle tilt down focusing on the character",
        "fpv": "First-person perspective dynamic flying camera movement",
        "zoom_in_punch": "Fast sudden zoom punch in emphasizing critical tension",
        "shake_impact": "Subtle handheld camera vibration capturing high-action impact",
        "static": "Locked-off stable tripod cinematic shot with natural ambient motion",
    }
    cue_text = cam_map.get(camera_cue, "Cinematic camera movement with natural atmospheric depth")
    if base_prompt:
        return f"{base_prompt}. {cue_text}, photorealistic lighting, 4K composition."
    return f"{cue_text}, photorealistic lighting, 4K composition."


async def convert_job_to_flowkit(job_data: Union[dict, str, Path], default_material: str = "realistic") -> dict:
    """Nạp job.json vào SQLite database của FlowKit."""
    if isinstance(job_data, (str, Path)):
        job_data = json.loads(Path(job_data).read_text(encoding="utf-8"))

    await init_db()

    job_id = job_data.get("jobId", "cinematic-job")
    title = job_data.get("title", "Untitled Film")
    beats = job_data.get("beats", [])
    metadata = job_data.get("metadata", {})
    canvas = job_data.get("canvas", {})
    
    orientation = "VERTICAL" if canvas.get("height", 1920) > canvas.get("width", 1080) else "HORIZONTAL"

    # 1. Tạo hoặc nạp Project
    project = await crud.create_project(
        name=f"[{job_id}] {title}",
        description=f"Auto-generated from OmniVideo Job: {job_id}",
        story="\n\n".join(b.get("rawText", "") for b in beats),
        language=metadata.get("language", "vi"),
        material=default_material,
        video_model_family="veo",
    )
    project_id = project["id"]
    logger.info("Created FlowKit Project: %s (id=%s)", project["name"], project_id)

    # 2. Tạo hoặc liên kết Nhân Vật (Characters)
    created_char_ids = []
    characters_meta = metadata.get("characters", [])
    for char_name in characters_meta:
        # Check existing character
        existing_chars = await crud.list_characters()
        found = next((c for c in existing_chars if c["name"].strip().lower() == char_name.strip().lower()), None)
        if found:
            char_id = found["id"]
        else:
            c = await crud.create_character(
                name=char_name,
                entity_type="character",
                description=f"Character {char_name} in film {title}",
                image_prompt=f"Cinematic portrait of {char_name}, highly detailed, photorealistic lighting, 8k render",
            )
            char_id = c["id"]
            logger.info("Created Character: %s (id=%s)", char_name, char_id)
        
        await crud.link_character_to_project(project_id, char_id)
        created_char_ids.append(char_id)

    # 3. Tạo Video entity
    video = await crud.create_video(
        project_id=project_id,
        title=title,
        description=f"Cinematic video for job {job_id}",
        orientation=orientation,
    )
    video_id = video["id"]
    logger.info("Created FlowKit Video: %s (id=%s, orientation=%s)", title, video_id, orientation)

    # 4. Tạo từng Scene từ danh sách Beats
    created_scenes = []
    for idx, beat in enumerate(beats):
        raw_text = beat.get("rawText", "")
        visual = beat.get("visual", {})
        cues = beat.get("cues", {})
        speaker = beat.get("speaker") or beat.get("voice", {}).get("speaker")

        char_names = [speaker] if speaker else []
        image_prompt = visual.get("prompt") or f"Cinematic shot of {raw_text[:120]}, atmospheric lighting, master shot"
        video_prompt = map_camera_to_video_prompt(cues.get("camera"), visual.get("prompt", raw_text[:100]))

        scene = await crud.create_scene(
            video_id=video_id,
            display_order=idx + 1,
            prompt=raw_text,
            image_prompt=image_prompt,
            video_prompt=video_prompt,
            character_names=char_names,
        )
        if raw_text:
            scene = await crud.update_scene(scene["id"], narrator_text=raw_text)
        created_scenes.append(scene)
        logger.info("  -> Created Scene %02d: %s (id=%s)", idx + 1, raw_text[:40], scene["id"])

    result = {
        "jobId": job_id,
        "projectId": project_id,
        "videoId": video_id,
        "scenesCount": len(created_scenes),
        "orientation": orientation,
        "colorGradingPreset": canvas.get("colorGradingPreset", "none"),
        "scenes": [{"id": s["id"], "display_order": s["display_order"], "prompt": s["prompt"]} for s in created_scenes],
    }

    await close_db()
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Chuyển đổi job.json sang FlowKit Project & Scenes")
    parser.add_argument("job_file", help="Đường dẫn file job.json")
    parser.add_argument("--material", default="realistic", help="Phong cách đồ họa (realistic, anime, dark_fantasy...)")
    parser.add_argument("--output-json", default=None, help="Đường dẫn file JSON xuất kết quả ánh xạ")
    args = parser.parse_args(argv)

    job_path = Path(args.job_file)
    if not job_path.exists():
        print(f"[ERR] Không tìm thấy file job: {job_path}", file=sys.stderr)
        return 1

    job_data = json.loads(job_path.read_text(encoding="utf-8"))
    print(f"[*] Đang nạp job '{job_data.get('jobId')}' vào FlowKit Studio...")

    result = asyncio.run(convert_job_to_flowkit(job_data, default_material=args.material))
    print(f"[OK] Đã tạo thành công FlowKit Project ({result['projectId']}) với {result['scenesCount']} scenes!")

    if args.output_json:
        out_p = Path(args.output_json)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[*] Đã xuất kết quả ánh xạ: {out_p}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Auto-generate, poll, and download Veo 2 video clips for scenes.
"""
import sys
import time
import requests
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

AGENT_URL = "http://127.0.0.1:8100"
VIDEO_ID = "950039ae-6565-4a44-8bfa-0034d5d79a5b"
JOB_ID = "job-rag-xianxia-cinematic"
OUTPUT_DIR = Path(f"output/cinematic/{JOB_ID}/videos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_scenes():
    res = requests.get(f"{AGENT_URL}/api/scenes?video_id={VIDEO_ID}", timeout=10)
    return res.json()


def trigger_video_for_scene(scene):
    scene_id = scene["id"]
    display_order = scene["display_order"]
    start_media_id = scene.get("horizontal_image_media_id")
    video_prompt = scene.get("video_prompt") or scene.get("prompt")

    if not start_media_id:
        print(f"  [SKIP] Scene {display_order:02d}: No start_image_media_id")
        return None

    payload = {
        "start_image_media_id": start_media_id,
        "prompt": video_prompt,
        "scene_id": scene_id,
        "aspect_ratio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
        "model_family": "veo",
        "duration_s": 8,
        "resolution": "720p",
    }
    print(f"  [SUBMIT VEO] Scene {display_order:02d} ({video_prompt[:40]}...)...", flush=True)
    res = requests.post(f"{AGENT_URL}/api/flow/generate-video", json=payload, timeout=60)
    if res.status_code in (200, 201, 202):
        data = res.json()
        ops = data.get("operations") or (data.get("data", {}).get("operations") if isinstance(data.get("data"), dict) else [])
        if ops:
            op_name = ops[0].get("name") or (ops[0].get("operation") or {}).get("name")
            print(f"  [ACCEPTED] Scene {display_order:02d}: Op ID = {op_name}", flush=True)
            return op_name
    print(f"  [FAILED] Scene {display_order:02d}: {res.status_code} {res.text[:100]}", flush=True)
    return None


def poll_and_download(op_name, scene):
    scene_id = scene["id"]
    display_order = scene["display_order"]
    out_file = OUTPUT_DIR / f"scene_{display_order:02d}.mp4"

    print(f"  [POLLING] Scene {display_order:02d} (Op {op_name[:12]}...)", flush=True)
    start_t = time.time()
    while time.time() - start_t < 300: # 5 mins max
        try:
            res = requests.post(f"{AGENT_URL}/api/flow/check-status", json={"operations": [{"name": op_name}]}, timeout=30)
            if res.status_code == 200:
                data = res.json()
                ops = data.get("operations") or (data.get("data", {}).get("operations") if isinstance(data.get("data"), dict) else [])
                if ops:
                    status = ops[0].get("status")
                    if status == "MEDIA_GENERATION_STATUS_SUCCESSFUL":
                        meta = ops[0].get("operation", {}).get("metadata", {})
                        video_meta = meta.get("video", {})
                        fife_url = video_meta.get("fifeUrl")
                        vid_media_id = video_meta.get("mediaId")
                        if fife_url:
                            print(f"  [SUCCESS] Scene {display_order:02d}: Downloading video from {fife_url[:50]}...", flush=True)
                            r = requests.get(fife_url, stream=True, timeout=60)
                            out_file.write_bytes(r.content)
                            print(f"  [SAVED] Scene {display_order:02d} -> {out_file.name} ({out_file.stat().st_size} bytes)", flush=True)

                            # Patch scene
                            patch_data = {
                                "horizontal_video_media_id": vid_media_id,
                                "horizontal_video_url": str(out_file),
                                "horizontal_video_status": "COMPLETED"
                            }
                            requests.patch(f"{AGENT_URL}/api/scenes/{scene_id}", json=patch_data, timeout=10)
                            return True
                    elif status == "MEDIA_GENERATION_STATUS_FAILED":
                        print(f"  [ERROR] Scene {display_order:02d} generation failed: {ops[0].get('error')}", flush=True)
                        return False
        except Exception as e:
            print(f"    [WARN] Poll exception: {e}", flush=True)
        time.sleep(12)

    print(f"  [TIMEOUT] Scene {display_order:02d} polling timed out.", flush=True)
    return False


def main(target_scenes=[2, 3]):
    scenes = get_scenes()
    selected = [s for s in scenes if s["display_order"] in target_scenes]

    for s in selected:
        op_name = trigger_video_for_scene(s)
        if op_name:
            poll_and_download(op_name, s)


if __name__ == "__main__":
    targets = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [2, 3]
    main(targets)

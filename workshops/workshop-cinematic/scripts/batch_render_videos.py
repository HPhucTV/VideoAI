#!/usr/bin/env python3
"""
Batch Video Renderer for Google Flow Veo 2 / Omni Flash
Renders genuine AI motion videos (GEN V) for all scenes in parallel.
Eliminates 2D static zoompan jittering and produces 100% cinema-grade motion.
"""

import sys
import time
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
AGENT_URL = "http://127.0.0.1:8100"
VIDEO_ID = "950039ae-6565-4a44-8bfa-0034d5d79a5b"
JOB_ID = "job-rag-xianxia-cinematic"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID / "videos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_scenes():
    res = requests.get(f"{AGENT_URL}/api/scenes?video_id={VIDEO_ID}", timeout=10)
    return res.json()


def trigger_video(scene, model_family="veo"):
    scene_id = scene["id"]
    display_order = scene["display_order"]
    start_media_id = scene.get("horizontal_image_media_id")
    video_prompt = scene.get("video_prompt") or scene.get("prompt")

    if not start_media_id:
        print(f"  [SKIP] Scene {display_order:02d}: Chưa có image_media_id")
        return None

    payload = {
        "start_image_media_id": start_media_id,
        "prompt": video_prompt,
        "scene_id": scene_id,
        "aspect_ratio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
        "model_family": model_family,
        "duration_s": 8,
        "resolution": "720p",
    }
    print(f"  [SUBMIT VEO] Scene {display_order:02d} ({video_prompt[:45]}...)...", flush=True)
    try:
        res = requests.post(f"{AGENT_URL}/api/flow/generate-video", json=payload, timeout=60)
        if res.status_code in (200, 201, 202):
            data = res.json()
            ops = data.get("operations") or (data.get("data", {}).get("operations") if isinstance(data.get("data"), dict) else [])
            if ops:
                op_name = ops[0].get("name") or (ops[0].get("operation") or {}).get("name")
                print(f"  [ACCEPTED] Scene {display_order:02d}: Op ID = {op_name}", flush=True)
                return op_name
        print(f"  [FAILED] Scene {display_order:02d}: {res.status_code} {res.text[:100]}", flush=True)
    except Exception as e:
        print(f"  [ERROR] Scene {display_order:02d} submit: {e}", flush=True)
    return None


def poll_and_download(op_name, scene):
    scene_id = scene["id"]
    display_order = scene["display_order"]
    out_file = OUTPUT_DIR / f"scene_{display_order:02d}.mp4"

    print(f"  [POLLING] Scene {display_order:02d} (Op {op_name[:12]}...)", flush=True)
    start_t = time.time()
    while time.time() - start_t < 360:
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
                            print(f"  [SUCCESS] Scene {display_order:02d}: Tải video AI từ {fife_url[:50]}...", flush=True)
                            r = requests.get(fife_url, stream=True, timeout=90)
                            out_file.write_bytes(r.content)
                            print(f"  [SAVED] Scene {display_order:02d} -> {out_file.name} ({out_file.stat().st_size:,} bytes)", flush=True)

                            # Patch scene trong DB
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


def render_all_missing(concurrency=2):
    scenes = get_scenes()
    missing = []
    for s in scenes:
        order = s["display_order"]
        vid_file = OUTPUT_DIR / f"scene_{order:02d}.mp4"
        if not vid_file.exists() or vid_file.stat().st_size < 100000:
            missing.append(s)

    print(f"\n🎬 Tổng số cảnh: {len(scenes)} | Đã có video: {len(scenes) - len(missing)} | Cần sinh: {len(missing)}")
    if not missing:
        print("✅ Tất cả các cảnh đã có video AI!")
        return

    # Chạy lần lượt từng cảnh để đảm bảo ổn định đường truyền WebSocket
    for s in missing:
        order = s["display_order"]
        op_name = trigger_video(s)
        if op_name:
            poll_and_download(op_name, s)


if __name__ == "__main__":
    targets = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else None
    if targets:
        scenes = [s for s in get_scenes() if s["display_order"] in targets]
        for s in scenes:
            op = trigger_video(s)
            if op:
                poll_and_download(op, s)
    else:
        render_all_missing()

#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4 Cinematic Studio
Batch Video Generator for Cyber-Chibi RAG Film: Missing Veo 2 AI Motion Videos.
Generates genuine AI motion video clips (GEN V) for scenes 1, 2, 3, 20, 23-30.
"""

import sys
import time
import requests
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

AGENT_URL = "http://127.0.0.1:8100"
VIDEO_ID = "613b3bb3-2b07-47a8-98be-1664bc529556"
JOB_ID = "job-rag-cyber-chibi"

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
VIDEOS_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID / "videos"
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def get_scenes():
    try:
        r = requests.get(f"{AGENT_URL}/api/scenes?video_id={VIDEO_ID}", timeout=10)
        if r.status_code == 200:
            return sorted(r.json(), key=lambda x: x.get("display_order", 0))
    except Exception as e:
        print(f"[ERROR] Cannot fetch scenes: {e}", file=sys.stderr)
    return []


def trigger_video_for_scene(scene):
    scene_id = scene["id"]
    display_order = scene["display_order"]
    start_media_id = scene.get("horizontal_image_media_id")
    video_prompt = scene.get("video_prompt") or scene.get("prompt") or ""

    if not start_media_id:
        print(f"  [BỎ QUA] Cảnh {display_order:02d}: Không có start_image_media_id", flush=True)
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
    print(f"  [BẤM MÁY VEO 2] Cảnh {display_order:02d}: \"{video_prompt[:40]}...\"", flush=True)
    try:
        res = requests.post(f"{AGENT_URL}/api/flow/generate-video", json=payload, timeout=60)
        if res.status_code in (200, 201, 202):
            data = res.json()
            ops = data.get("operations") or (data.get("data", {}).get("operations") if isinstance(data.get("data"), dict) else [])
            if ops:
                op_name = ops[0].get("name") or (ops[0].get("operation") or {}).get("name")
                print(f"  [TIẾP NHẬN] Cảnh {display_order:02d}: Op ID = {op_name}", flush=True)
                return op_name
        print(f"  [THẤT BẠI] Cảnh {display_order:02d}: {res.status_code} {res.text[:80]}", flush=True)
    except Exception as e:
        print(f"  [ERROR] Cảnh {display_order:02d} submit: {e}", flush=True)
    return None


def poll_and_download_video(op_name, scene):
    scene_id = scene["id"]
    display_order = scene["display_order"]
    out_file = VIDEOS_DIR / f"scene_{display_order:02d}.mp4"

    print(f"  [POLL VIDEO] Cảnh {display_order:02d} (Op {op_name[:12]}...)", flush=True)
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
                            print(f"  [THÀNH CÔNG] Cảnh {display_order:02d}: Đang tải video Veo 2...", flush=True)
                            r = requests.get(fife_url, stream=True, timeout=90)
                            out_file.write_bytes(r.content)
                            print(f"  [LƯU VIDEO] Cảnh {display_order:02d} -> {out_file.name} ({out_file.stat().st_size:,} bytes)", flush=True)

                            patch_data = {
                                "horizontal_video_media_id": vid_media_id,
                                "horizontal_video_url": str(out_file),
                                "horizontal_video_status": "COMPLETED"
                            }
                            requests.patch(f"{AGENT_URL}/api/scenes/{scene_id}", json=patch_data, timeout=10)
                            return True
                    elif status == "MEDIA_GENERATION_STATUS_FAILED":
                        print(f"  [LỖI] Cảnh {display_order:02d} sinh video thất bại: {ops[0].get('error')}", flush=True)
                        return False
        except Exception as e:
            print(f"    [WARN] Poll exception: {e}", flush=True)
        time.sleep(12)

    print(f"  [TIMEOUT] Cảnh {display_order:02d} hết thời gian chờ.", flush=True)
    return False


def main():
    scenes = get_scenes()
    if not scenes:
        print("[LỖI] Không thể đọc danh sách scenes!", file=sys.stderr)
        sys.exit(1)

    # Determine scenes that need video rendering
    missing_scenes = []
    for s in scenes:
        order = s["display_order"]
        vid_file = VIDEOS_DIR / f"scene_{order:02d}.mp4"
        if not vid_file.exists() or vid_file.stat().st_size < 100000:
            missing_scenes.append(s)

    print("=" * 65)
    print(f"🎬 KÍCH HOẠT SINH VIDEO AI VEO 2 CHO CÁC CẢNH THIẾU")
    print(f"   Tổng số cảnh: {len(scenes)} | Đã có video: {len(scenes) - len(missing_scenes)} | Cần sinh: {len(missing_scenes)}")
    print(f"   Danh sách cảnh cần sinh: {[s['display_order'] for s in missing_scenes]}")
    print("=" * 65)

    if not missing_scenes:
        print("✅ Tất cả các cảnh đã có video AI Veo 2 hoàn thiện!")
        return

    success_count = 0
    for s in missing_scenes:
        order = s["display_order"]
        print(f"\n▶ Đang xử lý Cảnh {order:02d}/{len(scenes)}...")
        op_name = trigger_video_for_scene(s)
        if op_name:
            ok = poll_and_download_video(op_name, s)
            if ok:
                success_count += 1
            else:
                print(f"⚠️ Cảnh {order:02d} chưa tải được video, chuyển cảnh kế tiếp...", flush=True)
        else:
            print(f"⚠️ Cảnh {order:02d} không tạo được operation, chuyển cảnh kế tiếp...", flush=True)

    print("\n" + "=" * 65)
    print(f"🎉 HOÀN THÀNH BATCH VEO 2: {success_count}/{len(missing_scenes)} cảnh thành công!")
    print("=" * 65)


if __name__ == "__main__":
    main()

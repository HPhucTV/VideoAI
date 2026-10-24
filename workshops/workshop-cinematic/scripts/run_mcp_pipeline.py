#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4 Cinematic Pipeline Runner for Cyber-Chibi MCP Film
1. Submits batch image generation requests for all 30 scenes.
2. Monitors image generation until complete and downloads images.
3. Kicks off Veo 2 video generation sequentially for 100% of scenes (ZERO FALLBACK).
4. Compiles the final 1080p Master Film.
"""

import sys
import time
import requests
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

AGENT_URL = "http://127.0.0.1:8100"
PROJECT_ID = "12154154-4455-4aed-94c2-e4b98b2d88a9"
VIDEO_ID = "da8930b1-0820-4546-b8c1-4a7bcf4d7c1e"
JOB_ID = "job-mcp-cyber-chibi"

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
PROJECT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
IMAGES_DIR = PROJECT_DIR / "images"
VIDEOS_DIR = PROJECT_DIR / "videos"
AUDIO_DIR = PROJECT_DIR / "audio"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def check_agent():
    try:
        r = requests.get(f"{AGENT_URL}/health", timeout=5)
        return r.status_code == 200 and r.json().get("extension_connected", False)
    except Exception:
        return False


def submit_image_requests():
    print("=" * 65)
    print("📤 ĐĂNG KÝ BATCH SINH 30 KHUNG ẢNH STORYBOARD (CỔNG 5)...")
    print("=" * 65)
    try:
        r = requests.get(f"{AGENT_URL}/api/scenes?video_id={VIDEO_ID}", timeout=10)
        if r.status_code != 200:
            print(f"[ERROR] Không thể lấy danh sách cảnh: {r.status_code}")
            return False
        scenes = r.json()
        print(f"[*] Tìm thấy {len(scenes)} scenes trong Video ID: {VIDEO_ID}")

        batch_reqs = []
        for s in scenes:
            sid = s["id"]
            # Only submit if no image media id yet
            if not s.get("horizontal_image_media_id"):
                batch_reqs.append({
                    "type": "GENERATE_IMAGE",
                    "scene_id": sid,
                    "project_id": PROJECT_ID,
                    "video_id": VIDEO_ID,
                    "orientation": "HORIZONTAL"
                })

        if not batch_reqs:
            print("  [OK] Tất cả các cảnh đều đã có yêu cầu sinh ảnh hoặc đã xong!")
            return True

        print(f"[*] Gửi {len(batch_reqs)} yêu cầu GENERATE_IMAGE đến FlowKit...")
        res = requests.post(f"{AGENT_URL}/api/requests/batch", json={"requests": batch_reqs}, timeout=15)
        if res.status_code == 200:
            print(f"✅ Gửi thành công {len(res.json())} yêu cầu ảnh vào hàng đợi!")
            return True
        else:
            print(f"[ERR] Gửi batch thất bại: {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"[EXC] submit_image_requests error: {e}")
        return False


def wait_for_images(timeout_s=900):
    print("\n" + "=" * 65)
    print("🎨 ĐANG THEO DÕI TIẾN ĐỘ SINH 30 KHUNG ẢNH STORYBOARD...")
    print("=" * 65)
    start_t = time.time()
    last_completed = -1

    while time.time() - start_t < timeout_s:
        try:
            r = requests.get(f"{AGENT_URL}/api/requests/batch-status?video_id={VIDEO_ID}&type=GENERATE_IMAGE", timeout=10)
            if r.status_code == 200:
                data = r.json()
                total = data.get("total", 30)
                completed = data.get("completed", 0)
                processing = data.get("processing", 0)
                pending = data.get("pending", 0)
                failed = data.get("failed", 0)
                done = data.get("done", False)

                if completed != last_completed:
                    print(f"  [TIẾN ĐỘ ẢNH] Đã xong {completed}/{total} | Đang xử lý: {processing} | Chờ: {pending} | Lỗi: {failed}", flush=True)
                    last_completed = completed

                if done or (completed + failed >= total and processing == 0 and pending == 0):
                    print(f"\n✅ Hoàn thành sinh ảnh Storyboard: {completed}/{total} thành công!", flush=True)
                    return True
        except Exception as e:
            print(f"  [WARN] Lỗi kiểm tra status: {e}", flush=True)
        time.sleep(10)

    print("⚠️ Hết thời gian chờ sinh ảnh (tiến hành đồng bộ các ảnh hiện có)...", flush=True)
    return False


def sync_images():
    print("\n📥 Đang đồng bộ ảnh về thư mục cục bộ...", flush=True)
    try:
        r = requests.get(f"{AGENT_URL}/api/scenes?video_id={VIDEO_ID}", timeout=10)
        if r.status_code != 200:
            return
        scenes = r.json()
        count = 0
        for s in scenes:
            order = s.get("display_order")
            url = s.get("horizontal_image_url")
            out_file = IMAGES_DIR / f"scene_{order:02d}.jpg"
            if url and not out_file.exists():
                try:
                    resp = requests.get(url, timeout=30)
                    if resp.status_code == 200:
                        out_file.write_bytes(resp.content)
                        count += 1
                        print(f"  [LƯU ẢNH] Cảnh {order:02d} -> {out_file.name} ({len(resp.content):,} bytes)", flush=True)
                except Exception as e:
                    print(f"  [LỖI TẢI] Cảnh {order:02d}: {e}")
        print(f"  => Tổng cộng {count} ảnh mới được tải về.", flush=True)
    except Exception as e:
        print(f"  [WARN] Lỗi sync images: {e}")


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
        "project_id": PROJECT_ID,
        "aspect_ratio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
        "model_family": "veo",
        "duration_s": 8,
        "resolution": "720p",
    }
    print(f"  [BẤM MÁY VEO 2] Cảnh {display_order:02d}: \"{video_prompt[:45]}...\"", flush=True)
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
        elapsed = int(time.time() - start_t)
        try:
            res = requests.post(f"{AGENT_URL}/api/flow/check-status", json={"operations": [{"name": op_name}], "project_id": PROJECT_ID}, timeout=30)
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
                            print(f"  [THÀNH CÔNG] Cảnh {display_order:02d}: Tải video AI Veo 2 sau {elapsed}s...", flush=True)
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
                    else:
                        print(f"    ... Cảnh {display_order:02d} đang render ({elapsed}s)...", flush=True)
        except Exception as e:
            print(f"    [WARN] Poll exception: {e}", flush=True)
        time.sleep(12)

    print(f"  [TIMEOUT] Cảnh {display_order:02d} hết thời gian chờ.", flush=True)
    return False


def render_all_veo_videos():
    print("\n" + "=" * 65)
    print("🎬 KÍCH HOẠT SINH VIDEO CHUYỂN ĐỘNG AI THỰC SỰ (GEN V) - 100% ZERO FALLBACK")
    print("=" * 65)

    max_rounds = 3
    for round_num in range(1, max_rounds + 1):
        r = requests.get(f"{AGENT_URL}/api/scenes?video_id={VIDEO_ID}", timeout=10)
        scenes = sorted(r.json(), key=lambda x: x.get("display_order", 0))

        to_render = []
        for s in scenes:
            order = s["display_order"]
            vid_file = VIDEOS_DIR / f"scene_{order:02d}.mp4"
            if not vid_file.exists() or vid_file.stat().st_size < 100000:
                if s.get("horizontal_image_media_id"):
                    to_render.append(s)

        if not to_render:
            print(f"🎉 TẤT CẢ 30 CẢNH ĐỀU ĐÃ CÓ VIDEO VEO 2 AI ĐẦY ĐỦ!")
            return True

        print(f"\n--- VÒNG {round_num}/{max_rounds}: Cần render {len(to_render)}/30 cảnh thiếu video ---")
        for s in to_render:
            order = s["display_order"]
            op_name = trigger_video_for_scene(s)
            if op_name:
                poll_and_download_video(op_name, s)
            time.sleep(5)  # Safe spacing between video triggers

    # Final check
    missing = []
    for i in range(1, 31):
        vf = VIDEOS_DIR / f"scene_{i:02d}.mp4"
        if not vf.exists() or vf.stat().st_size < 100000:
            missing.append(i)

    if missing:
        print(f"❌ Vẫn còn {len(missing)} cảnh thiếu video: {missing}")
        return False
    return True


def compile_final_film():
    print("\n" + "=" * 65)
    print("🎞️ RÁP MASTER FILM HOÀN CHỈNH (CỔNG 6)...")
    print("=" * 65)
    compiler = Path(__file__).resolve().parent / "compile_mcp_cyber_chibi_film.py"
    py_bin = sys.executable
    res = subprocess.run([py_bin, str(compiler)])
    return res.returncode == 0


def main():
    if not check_agent():
        print("[LỖI] FlowKit Agent hoặc Chrome Extension chưa sẵn sàng!", file=sys.stderr)
        sys.exit(1)

    print("🚀 BẮT ĐẦU PIPELINE XƯỞNG 4: MCP CYBER-CHIBI 3D FILM")

    # 1. Đăng ký batch sinh 30 khung ảnh
    submit_image_requests()

    # 2. Chờ ảnh Storyboard hoàn tất
    wait_for_images(timeout_s=900)

    # 3. Đồng bộ toàn bộ ảnh về máy
    sync_images()

    # 4. Kích hoạt sinh video AI Veo 2 cho toàn bộ 30 cảnh (Zero Fallback)
    ok_videos = render_all_veo_videos()
    if not ok_videos:
        print("[LỖI] Chưa đủ 100% video Veo 2 AI. Tuân thủ Zero-Fallback, không xuất phim!", file=sys.stderr)
        sys.exit(1)

    # 5. Xuất phim Master Film hoàn chỉnh
    ok_film = compile_final_film()
    if ok_film:
        print("\n🏆 QUY TRÌNH SẢN XUẤT WORKSHOP 4 HOÀN TẤT THÀNH CÔNG!")
    else:
        print("\n[ERR] Biên tập Master Film thất bại!", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

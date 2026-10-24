#!/usr/bin/env python3
"""
FlowKit Cinematic Pipeline Runner — OmniVideo Studio Workshop 4
Unified CLI to import jobs, inspect health, trigger generation (Veo 2 / Omni Flash),
and assemble master films.

Usage:
    # 1. Kiểm tra trạng thái Agent và Chrome Extension
    python workshops/workshop-cinematic/scripts/run_pipeline.py --check

    # 2. Nạp job.json vào FlowKit Database
    python workshops/workshop-cinematic/scripts/run_pipeline.py --job output/jobs/job-xianxia-3d-sample.json --import-only

    # 3. Xem tiến độ các cảnh trong video đã nạp
    python workshops/workshop-cinematic/scripts/run_pipeline.py --job job-xianxia-3d-sample --status

    # 4. Kích hoạt sinh ảnh hàng loạt qua Google Imagen 3
    python workshops/workshop-cinematic/scripts/run_pipeline.py --job job-xianxia-3d-sample --generate-images

    # 5. Kích hoạt sinh video hàng loạt qua Google Veo 2
    python workshops/workshop-cinematic/scripts/run_pipeline.py --job job-xianxia-3d-sample --generate-videos --model-family veo

    # 6. Ghép thành phim hoàn chỉnh
    python workshops/workshop-cinematic/scripts/run_pipeline.py --job job-xianxia-3d-sample --build-film
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FlowKitPipeline")

AGENT_BASE_URL = os.environ.get("FLOWKIT_AGENT_URL", "http://127.0.0.1:8100")


def check_agent_health():
    """Kiểm tra xem FlowKit Agent server và Chrome Extension có sẵn sàng không."""
    print("=" * 65)
    print(" 🔍 KIỂM TRA TRẠNG THÁI FLOWKIT AGENT (XƯỞNG 4 CINEMATIC)")
    print("=" * 65)
    health_url = f"{AGENT_BASE_URL}/health"
    try:
        res = requests.get(health_url, timeout=4)
        if res.status_code == 200:
            data = res.json()
            ext_ok = data.get("extension_connected", False)
            version = data.get("version", "unknown")
            print(f"  [OK] FlowKit FastAPI Agent: ONLINE (v{version}) tại {AGENT_BASE_URL}")
            if ext_ok:
                print("  [OK] Chrome Extension: ĐÃ KẾT NỐI (Sẵn sàng tạo ảnh/video)")
                return True
            else:
                print("  [CẢNH BÁO] Chrome Extension: CHƯA KẾT NỐI!")
                print("  👉 Các bước kết nối Extension:")
                print("     1. Mở Chrome -> vào chrome://extensions")
                print("     2. Bật 'Developer mode' (Góc trên bên phải)")
                print("     3. Chọn 'Load unpacked' -> trỏ vào: workshops/workshop-cinematic/extension")
                print("     4. Mở 1 tab trình duyệt vào https://flow.google.com/ và đăng nhập Google")
                return False
        else:
            print(f"  [LỖI] Agent trả về mã trạng thái: {res.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"  [OFFLINE] Không thể kết nối tới FlowKit Agent tại {AGENT_BASE_URL}")
        print("  👉 Khởi động Agent bằng lệnh:")
        print("     workshops/workshop-cinematic/.venv/Scripts/python.exe -m agent.main")
        print("     (hoặc chọn mục [8] -> [1] trong studio.ps1)")
        return False


def resolve_job_path(job_input: str) -> Path:
    """Tìm file job.json từ tên file hoặc job ID."""
    p = Path(job_input)
    if p.exists() and p.is_file():
        return p.resolve()

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    clean_id = job_input.replace(".json", "")
    candidates = [
        Path(f"output/jobs/{job_input}"),
        Path(f"output/jobs/{job_input}.json"),
        Path(f"{job_input}.json"),
        Path(f"output/jobs/job-{job_input}.json"),
        repo_root / "output" / "jobs" / job_input,
        repo_root / "output" / "jobs" / f"{job_input}.json",
        repo_root / "output" / "jobs" / f"job-{clean_id}.json",
        Path.cwd().parent.parent / "output" / "jobs" / f"{job_input}.json",
    ]
    for c in candidates:
        if c.exists() and c.is_file():
            return c.resolve()

    raise FileNotFoundError(f"Không tìm thấy file kịch bản cho: {job_input}")


def run_import_job(job_path: Path):
    """Nạp job.json vào FlowKit SQLite DB qua job_adapter.py."""
    print(f"\n📥 Đang nạp kịch bản vào FlowKit DB từ: {job_path.name}...")
    root_ws = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root_ws))
    from job_adapter import convert_job_to_flowkit

    result = asyncio.run(convert_job_to_flowkit(str(job_path)))
    print(f"  [XONG] Project ID: {result['projectId']}")
    print(f"  [XONG] Video ID:   {result['videoId']}")
    print(f"  [XONG] Tổng số Scene: {result['scenesCount']}")

    out_json = Path(f"output/cinematic/{result['jobId']}-flowkit.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [LƯU] Bản ghi ánh xạ lưu tại: {out_json}")
    return result


def get_video_status(video_id: str):
    """Lấy danh sách các scene và trạng thái render từ FlowKit Agent."""
    scenes_url = f"{AGENT_BASE_URL}/api/scenes?video_id={video_id}"
    try:
        res = requests.get(scenes_url, timeout=5)
        if res.status_code == 200:
            scenes = res.json()
            print(f"\n📊 TRẠNG THÁI CÁC CẢNH CHO VIDEO [{video_id}]: ({len(scenes)} cảnh)")
            print("-" * 65)
            for s in scenes:
                idx = s.get("display_order", 0)
                prompt = s.get("prompt", "")[:50]
                img_url = s.get("image_url") or s.get("image_media_id") or "chưa có ảnh"
                vid_url = s.get("video_url") or s.get("vertical_video_url") or "chưa có video"
                print(f"  Cảnh {idx:02d}: {prompt}")
                print(f"         Ảnh:   {img_url}")
                print(f"         Video: {vid_url}")
            return scenes
        else:
            print(f"Lỗi khi lấy thông tin scene: {res.status_code}")
            return None
    except Exception as e:
        print(f"Không thể kết nối Agent để lấy trạng thái: {e}")
        return None


def trigger_generate_images(video_id: str, scenes: list):
    """Gửi yêu cầu tạo ảnh cho tất cả scene chưa có ảnh và cập nhật DB."""
    print(f"\n🎨 Bắt đầu kích hoạt sinh ảnh cho {len(scenes)} cảnh...")
    gen_url = f"{AGENT_BASE_URL}/api/flow/generate-image"
    success_count = 0

    for s in scenes:
        idx = s.get("display_order", 0)
        scene_id = s.get("id")
        existing_img = s.get("horizontal_image_url") or s.get("horizontal_image_media_id")
        if existing_img:
            print(f"  [ĐÃ CÓ ẢNH] Cảnh {idx:02d}: {existing_img[:30]}...")
            success_count += 1
            continue

        img_prompt = s.get("image_prompt") or s.get("prompt")
        aspect = "IMAGE_ASPECT_RATIO_LANDSCAPE"

        payload = {
            "prompt": img_prompt,
            "aspect_ratio": aspect,
        }
        try:
            print(f"  [ĐANG TẠO] Cảnh {idx:02d}: {img_prompt[:45]}...", flush=True)
            res = requests.post(gen_url, json=payload, timeout=90)
            if res.status_code in (200, 201, 202):
                data = res.json()
                media_list = data.get("media") or (data.get("data", {}).get("media") if isinstance(data.get("data"), dict) else [])
                media_id = None
                img_url = None
                if media_list and len(media_list) > 0:
                    first = media_list[0]
                    gen_img = first.get("image", {}).get("generatedImage", {})
                    media_id = gen_img.get("mediaId") or first.get("name") or first.get("media_id")
                    img_url = gen_img.get("fifeUrl") or first.get("url") or first.get("image_url")

                # Cập nhật scene trong DB
                if scene_id and (media_id or img_url):
                    patch_url = f"{AGENT_BASE_URL}/api/scenes/{scene_id}"
                    patch_data = {
                        "horizontal_image_media_id": media_id,
                        "horizontal_image_url": img_url,
                        "horizontal_image_status": "COMPLETED"
                    }
                    requests.patch(patch_url, json=patch_data, timeout=10)

                print(f"  [THÀNH CÔNG] Cảnh {idx:02d}: media_id={media_id or 'ok'}", flush=True)
                success_count += 1
            else:
                print(f"  [GỬI THẤT BẠI] Cảnh {idx:02d}: HTTP {res.status_code} - {res.text[:80]}", flush=True)
        except Exception as e:
            print(f"  [LỖI] Cảnh {idx:02d}: {e}", flush=True)

    print(f"  => Đã hoàn thành/gửi yêu cầu tạo ảnh cho {success_count}/{len(scenes)} cảnh.", flush=True)


def trigger_generate_videos(video_id: str, scenes: list, model_family: str = "veo"):
    """Gửi yêu cầu tạo video (Veo 2 hoặc Omni Flash) cho các cảnh đã có ảnh và cập nhật DB."""
    print(f"\n🎬 Bắt đầu kích hoạt sinh video ({model_family.upper()}) cho các cảnh...")
    gen_url = f"{AGENT_BASE_URL}/api/flow/generate-video"
    success_count = 0

    for s in scenes:
        idx = s.get("display_order", 0)
        scene_id = s.get("id")
        start_media_id = s.get("horizontal_image_media_id") or s.get("image_media_id")
        video_prompt = s.get("video_prompt") or s.get("prompt")

        existing_vid = s.get("horizontal_video_url") or s.get("horizontal_video_media_id")
        if existing_vid:
            print(f"  [ĐÃ CÓ VIDEO] Cảnh {idx:02d}: {existing_vid[:30]}...")
            success_count += 1
            continue

        if not start_media_id:
            print(f"  [BỎ QUA] Cảnh {idx:02d}: Chưa có image_media_id (Cần tạo ảnh trước)", flush=True)
            continue

        payload = {
            "start_image_media_id": start_media_id,
            "prompt": video_prompt,
            "scene_id": scene_id,
            "aspect_ratio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
            "model_family": model_family,
            "duration_s": 8,
            "resolution": "720p",
        }
        try:
            print(f"  [ĐANG TẠO VIDEO] Cảnh {idx:02d}: {video_prompt[:45]}...", flush=True)
            res = requests.post(gen_url, json=payload, timeout=120)
            if res.status_code in (200, 201, 202):
                data = res.json()
                print(f"  [GỬI THÀNH CÔNG] Cảnh {idx:02d}: HTTP {res.status_code}", flush=True)
                success_count += 1
            else:
                print(f"  [GỬI THẤT BẠI] Cảnh {idx:02d}: HTTP {res.status_code} - {res.text[:80]}", flush=True)
        except Exception as e:
            print(f"  [LỖI] Cảnh {idx:02d}: {e}", flush=True)

    print(f"  => Đã gửi yêu cầu tạo video cho {success_count} cảnh.", flush=True)


def main():
    parser = argparse.ArgumentParser(description="FlowKit Cinematic Pipeline Runner")
    parser.add_argument("--job", "-j", type=str, help="Đường dẫn hoặc ID của job.json")
    parser.add_argument("--check", "-c", action="store_true", help="Kiểm tra trạng thái Agent và Extension")
    parser.add_argument("--import-only", action="store_true", help="Chỉ nạp job.json vào FlowKit SQLite")
    parser.add_argument("--status", "-s", action="store_true", help="Kiểm tra tiến độ các cảnh của video")
    parser.add_argument("--generate-images", action="store_true", help="Kích hoạt sinh ảnh hàng loạt")
    parser.add_argument("--generate-videos", action="store_true", help="Kích hoạt sinh video hàng loạt")
    parser.add_argument("--model-family", type=str, default="veo", choices=["veo", "omni_flash"], help="Model video (veo hoặc omni_flash)")
    parser.add_argument("--limit", "-l", type=int, default=None, help="Giới hạn số lượng scene xử lý")
    parser.add_argument("--scenes", type=int, nargs="+", default=None, help="Chỉ định danh sách display_order của các scene cần xử lý (ví dụ: --scenes 1 2 3)")
    parser.add_argument("--build-film", action="store_true", help="Ghép master film từ các cảnh đã hoàn thành")
    args = parser.parse_args()

    if args.check:
        check_agent_health()
        return

    if not args.job:
        # Nếu không có tham số gì, mặc định kiểm tra health
        check_agent_health()
        print("\n💡 Gợi ý: Chạy với tham số `--job [file/id]` để xử lý kịch bản cụ thể.")
        return

    job_path = resolve_job_path(args.job)
    job_id = job_path.stem

    # Kiểm tra xem đã có flowkit mapping chưa
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    mapping_candidates = [
        Path(f"output/cinematic/{job_id}-flowkit.json"),
        repo_root / "output" / "cinematic" / f"{job_id}-flowkit.json",
        Path(__file__).resolve().parent.parent / "output" / "cinematic" / f"{job_id}-flowkit.json",
    ]
    mapping = None
    for mc in mapping_candidates:
        if mc.exists():
            try:
                mapping = json.loads(mc.read_text(encoding="utf-8"))
                break
            except Exception:
                pass

    if args.import_only or not mapping:
        mapping = run_import_job(job_path)
        if args.import_only:
            return

    video_id = mapping.get("videoId")
    if not video_id:
        print(f"[LỖI] Không tìm thấy videoId trong mapping của job {job_id}")
        return

    if args.status:
        get_video_status(video_id)
        return

    if args.generate_images:
        scenes = get_video_status(video_id) or []
        if args.scenes:
            scenes = [s for s in scenes if s.get("display_order") in args.scenes]
        if args.limit:
            scenes = scenes[:args.limit]
        trigger_generate_images(video_id, scenes)
        return

    if args.generate_videos:
        scenes = get_video_status(video_id) or []
        if args.scenes:
            scenes = [s for s in scenes if s.get("display_order") in args.scenes]
        if args.limit:
            scenes = scenes[:args.limit]
        trigger_generate_videos(video_id, scenes, model_family=args.model_family)
        return

    if args.build_film:
        print(f"\n🎞️ Tiến hành ghép phim Master Film cho job {job_id}...")
        builder_script = Path(__file__).resolve().parent / "build_master_film.py"
        proj_dir = Path(f"output/cinematic/{job_id}")
        cmd = [sys.executable, str(builder_script), "--project-dir", str(proj_dir)]
        subprocess.run(cmd)
        return

    # Nếu chỉ truyền --job mà không truyền action
    print(f"\nJob: {job_id} (Video ID: {video_id})")
    get_video_status(video_id)


if __name__ == "__main__":
    main()

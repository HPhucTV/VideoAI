#!/usr/bin/env python3
"""
OmniVideo Studio - AI Art Orchestrator
Quản lý và điều phối tranh vẽ từ Generative AI Model (image-generator subagent):
1. Quản lý danh mục yêu cầu sinh ảnh: IMAGE_GENERATOR_MANIFEST.json
2. Tự động chuẩn hóa và nạp ảnh AI (JPG/PNG -> chuẩn 1920x1080 nền kem #F5EBD7)
3. Hỗ trợ CLI kiểm tra trạng thái và xuất prompt cho subagent
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BG_CREAM = (245, 235, 215)  # #F5EBD7


def normalize_image_to_storyboard(src_path: Path, dst_path: Path, target_w: int = 1920, target_h: int = 1080):
    """Mở file ảnh bất kỳ (JPG, PNG), chuẩn hóa về 1920x1080 RGB nền kem ấm #F5EBD7."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src_path) as im:
        im = im.convert("RGBA")
        
        # Tạo canvas nền kem ấm chuẩn
        canvas = Image.new("RGBA", (target_w, target_h), (*BG_CREAM, 255))
        
        # Scale giữ tỉ lệ
        sw, sh = im.size
        scale = min(target_w / sw, target_h / sh)
        new_w = int(round(sw * scale))
        new_h = int(round(sh * scale))
        
        resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        paste_x = (target_w - new_w) // 2
        paste_y = (target_h - new_h) // 2
        
        canvas.paste(resized, (paste_x, paste_y), mask=resized)
        final_rgb = canvas.convert("RGB")
        final_rgb.save(dst_path, format="PNG", optimize=True)
        print(f"[OK] Đã chuẩn hóa ảnh AI thành công: {dst_path} ({target_w}x{target_h})")


def try_auto_ingest_from_brain(job_dir: Path, scene_id: str, target_png: Path) -> bool:
    """Tìm kiếm trong thư mục brain artifact xem subagent image-generator vừa tạo ảnh nào phù hợp không."""
    user_home = Path.home()
    brain_dir = user_home / ".gemini" / "antigravity" / "brain"
    if not brain_dir.exists():
        return False

    job_slug = job_dir.name.replace("job-", "")
    patterns = [
        f"*{scene_id}*.jpg", f"*{scene_id}*.png",
        f"*{job_slug}*{scene_id}*.jpg", f"*{job_slug}*{scene_id}*.png"
    ]

    found_files = []
    for pat in patterns:
        found_files.extend(list(brain_dir.glob(f"*/{pat}")))

    if not found_files:
        return False

    # Lấy file mới nhất
    found_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    best_match = found_files[0]
    try:
        normalize_image_to_storyboard(best_match, target_png)
        print(f"[OK] Đã tự động nạp ảnh AI từ brain ({best_match.name}) vào {target_png}")
        return True
    except Exception as e:
        print(f"[WARN] Lỗi khi nạp ảnh từ brain: {e}")
        return False


def get_job_manifest(job_id: str) -> dict | None:
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    job_dir = root_dir / "output" / "whiteboard" / job_id
    manifest_file = job_dir / "IMAGE_GENERATOR_MANIFEST.json"
    if manifest_file.exists():
        with open(manifest_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def show_status(job_id: str):
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    job_dir = root_dir / "output" / "whiteboard" / job_id
    if not job_dir.exists():
        print(f"[ERR] Không tìm thấy thư mục job: {job_dir}")
        return

    scenes_dir = job_dir / "scenes"
    if not scenes_dir.exists():
        print(f"[ERR] Không tìm thấy scenes trong: {job_dir}")
        return

    scenes = sorted(list(scenes_dir.glob("scene-*")), key=lambda p: p.name)
    print("=" * 70)
    print(f"TRẠNG THÁI TRANH VẼ GENERATIVE AI CHO JOB: {job_id}")
    print(f"Tổng số phân cảnh: {len(scenes)}")
    print("=" * 70)

    for sc in scenes:
        sc_id = sc.name
        img_file = sc / f"{sc_id}.png"
        brief_file = sc / "image_generator_brief.json"
        badge = sc_id
        if brief_file.exists():
            try:
                with open(brief_file, "r", encoding="utf-8") as bf:
                    data = json.load(bf)
                    badge = data.get("badge", sc_id)
            except Exception:
                pass

        if img_file.exists():
            size_kb = img_file.stat().st_size / 1024
            status = f"ĐÃ CÓ ẢNH ({size_kb:.1f} KB)"
        else:
            status = "CHỜ SINH ẢNH (image-generator)"

        print(f" - [{sc_id}] {badge:<35} : {status}")

    print("=" * 70)


def list_prompts(job_id: str):
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    job_dir = root_dir / "output" / "whiteboard" / job_id
    scenes_dir = job_dir / "scenes"
    if not scenes_dir.exists():
        print(f"[ERR] Không tìm thấy scenes trong: {job_dir}")
        return

    scenes = sorted(list(scenes_dir.glob("scene-*")), key=lambda p: p.name)
    print("=" * 70)
    print(f"DANH SÁCH PROMPT SUBAGENT 'image-generator' CHO JOB: {job_id}")
    print("=" * 70)

    for sc in scenes:
        sc_id = sc.name
        brief_file = sc / "image_generator_brief.json"
        if brief_file.exists():
            with open(brief_file, "r", encoding="utf-8") as bf:
                data = json.load(bf)
            print(f"\n>>> [PHÂN CẢNH {sc_id}]: {data.get('badge', '')}")
            print("-" * 50)
            print(data.get("subagentPrompt", "").strip())
            print("-" * 50)


def main():
    parser = argparse.ArgumentParser(description="Quản lý và điều phối tranh vẽ Generative AI (image-generator)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_status = subparsers.add_parser("status", help="Xem trạng thái tranh vẽ của job")
    p_status.add_argument("job_id", help="ID của job (ví dụ: job-hop-dong-100-ty-tong-tai)")

    p_prompts = subparsers.add_parser("prompts", help="In danh sách prompt sẵn sàng cho subagent image-generator")
    p_prompts.add_argument("job_id", help="ID của job")

    p_ingest = subparsers.add_parser("ingest", help="Nạp file ảnh từ image-generator vào đúng cảnh")
    p_ingest.add_argument("job_id", help="ID của job")
    p_ingest.add_argument("source_image", help="Đường dẫn file ảnh nguồn (JPG/PNG)")
    p_ingest.add_argument("--scene", required=True, help="Tên cảnh (ví dụ: scene-01)")

    args = parser.parse_args()

    if args.command == "status":
        show_status(args.job_id)
    elif args.command == "prompts":
        list_prompts(args.job_id)
    elif args.command == "ingest":
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        dst = root_dir / "output" / "whiteboard" / args.job_id / "scenes" / args.scene / f"{args.scene}.png"
        src = Path(args.source_image)
        if not src.exists():
            print(f"[ERR] File nguồn không tồn tại: {src}")
            sys.exit(1)
        normalize_image_to_storyboard(src, dst)


if __name__ == "__main__":
    main()

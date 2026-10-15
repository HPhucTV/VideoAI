#!/usr/bin/env python3
"""
OmniVideo Studio - Whiteboard Video Exporter
Pipeline xuất video bảng trắng vẽ tay hoàn chỉnh:
1. Chuẩn bị tài nguyên (Job -> Audio TTS + SRT + Annotation)
2. Render hoạt cảnh nét vẽ tay theo thời gian thực (90 FPS)
3. Ghép nối âm thanh chất lượng cao bằng FFmpeg
4. Tạo thumbnail xem trước cho Dashboard
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def get_node_env():
    env = os.environ.copy()
    current_path = env.get("PATH", "")
    node_paths = [
        r"C:\Program Files\nodejs",
        r"C:\ProgramData\chocolatey\bin",
    ]
    for p in node_paths:
        if p not in current_path and os.path.exists(p):
            current_path = f"{p};{current_path}"
    env["PATH"] = current_path
    return env

def export_whiteboard_video(job_id: str, fps: int = 90, cap_long_edge: int = 1080):
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    output_wb = root_dir / "output" / "whiteboard"
    job_dir = output_wb / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    
    jobs_json_dir = root_dir / "output" / "jobs"
    job_json_file = jobs_json_dir / f"{job_id}.json"
    
    print("=" * 60)
    print(f"[*] OMNIVIDEO - XUAT VIDEO BANG TRANG 90 FPS: {job_id}")
    print("=" * 60)
    
    # 1. Đảm bảo âm thanh & annotation đã được tạo
    mp3_file = job_dir / "input.mp3"
    ann_file = job_dir / "scene-01.annotation.json"
    
    if not (mp3_file.exists() and ann_file.exists()):
        if not job_json_file.exists():
            print(f"[ERR] Không tìm thấy file kịch bản: {job_json_file}")
            sys.exit(1)
        print("[1/3] Đang tổng hợp giọng đọc & đồng bộ phụ đề (job_adapter.py)...")
        adapter_script = Path(__file__).resolve().parent.parent / "job_adapter.py"
        res_adapter = subprocess.run([
            sys.executable,
            str(adapter_script),
            str(job_json_file),
            str(job_dir)
        ], cwd=str(root_dir), env=get_node_env())
        if res_adapter.returncode != 0:
            print("[ERR] Tổng hợp job_adapter thất bại!")
            sys.exit(res_adapter.returncode)
    else:
        print("[1/3] Dữ liệu âm thanh & kịch bản đã sẵn sàng.")
        
    # 2. Đảm bảo ảnh minh họa scene-01.png
    scene_png = job_dir / "scene-01.png"
    if not scene_png.exists():
        # Tìm trong assets
        possible_assets = [
            root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / job_id.replace("job-", "") / "scene-01-storyboard.png",
            root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / job_id.replace("job-", "") / "scene-01.png",
            root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / "ban-hop-dong-luc-0-gio" / "scene-01-storyboard.png",
            root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / "tam-cam" / "scene-tam-cam.png"
        ]
        found_asset = None
        for p in possible_assets:
            if p.exists():
                found_asset = p
                break
        if found_asset:
            print(f"[*] Sao chép ảnh phân cảnh từ: {found_asset}")
            shutil.copy(found_asset, scene_png)
        else:
            print(f"[ERR] Không tìm thấy ảnh minh họa cho {job_id} tại {scene_png}")
            sys.exit(1)

    # 3. Render video nét vẽ không lời (video-silent.mp4)
    silent_mp4 = job_dir / "video-silent.mp4"
    render_script = Path(__file__).resolve().parent / "render_stream_whiteboard.py"
    
    print(f"[2/3] Đang vẽ tay từng nét chuyển động ở {fps} FPS (Stream Renderer)...")
    cmd_render = [
        sys.executable,
        str(render_script),
        str(scene_png),
        str(ann_file),
        str(silent_mp4),
        "--fps", str(fps),
        "--cap-long-edge", str(cap_long_edge)
    ]
    res_render = subprocess.run(cmd_render, cwd=str(root_dir), env=get_node_env())
    if res_render.returncode != 0:
        print("[ERR] Lỗi khi render hoạt cảnh vẽ tay!")
        sys.exit(res_render.returncode)

    # 4. Mux audio với ffmpeg
    final_mp4 = output_wb / f"{job_id}.mp4"
    thumb_png = output_wb / f"{job_id}-thumb.png"
    
    print("[3/3] Đang lồng tiếng và khớp khung hình cuối cùng bằng FFmpeg...")
    ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
    cmd_ffmpeg = [
        ffmpeg_bin, "-y",
        "-i", str(silent_mp4),
        "-i", str(mp3_file),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(final_mp4)
    ]
    res_ffmpeg = subprocess.run(cmd_ffmpeg, env=get_node_env())
    if res_ffmpeg.returncode != 0:
        print("[ERR] Lỗi khi ghép âm thanh bằng FFmpeg!")
        sys.exit(res_ffmpeg.returncode)

    # 5. Tạo thumbnail
    if scene_png.exists():
        shutil.copy(scene_png, thumb_png)
        
    size_mb = final_mp4.stat().st_size / (1024 * 1024)
    print("=" * 60)
    print(f"[HOAN THANH] XUAT VIDEO THANH CONG: {final_mp4} ({size_mb:.2f} MB)")
    print(f"OUTPUT={final_mp4}")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Xuất video Whiteboard hoàn chỉnh")
    parser.add_argument("job_id", nargs="?", default="job-ban-hop-dong-luc-0-gio", help="ID của job cần xuất")
    parser.add_argument("--fps", type=int, default=90, help="Số khung hình / giây (mặc định 90)")
    parser.add_argument("--cap-long-edge", type=int, default=1080, help="Giới hạn cạnh dài khung hình (mặc định 1080)")
    args = parser.parse_args()
    
    export_whiteboard_video(args.job_id, fps=args.fps, cap_long_edge=args.cap_long_edge)

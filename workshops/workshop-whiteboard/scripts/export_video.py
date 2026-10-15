#!/usr/bin/env python3
"""
OmniVideo Studio - Whiteboard Video Exporter (Multi-scene Support)
Pipeline xuất video bảng trắng vẽ tay hoàn chỉnh:
1. Chuẩn bị tài nguyên (Job -> Audio TTS + SRT + Annotation + Phân cụm scenes)
2. Hỗ trợ đa phân cảnh (Multi-scene):
   - Duyệt từng scene-XX trong job_dir/scenes
   - Render video vẽ tay từng nét ở 90 FPS với hiệu ứng bàn tay xóa bảng giữa các cảnh
   - Ghép âm thanh cục bộ scene-XX.mp3 vào scene-XX.mp4
3. Ghép nối tất cả các phân cảnh thành video tổng bằng merge_scenes
4. Hỗ trợ cờ --scene để render lại một phân cảnh cụ thể
5. Tương thích ngược với định dạng đơn cảnh cũ
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from audio_mixer import resolve_bgm_path, generate_default_ambient_bgm
from export_metadata import generate_youtube_metadata

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def get_node_env() -> dict:
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


def sort_scene_folders(scene_folders: list[Path]) -> list[Path]:
    def sort_key(p: Path):
        name = p.name
        parts = name.replace("_", "-").split("-")
        for part in parts:
            if part.isdigit():
                return (int(part), name)
        return (9999, name)

    return sorted(scene_folders, key=sort_key)


def ensure_scene_image(scene_folder: Path, job_id: str, root_dir: Path, job_dir: Path) -> Path:
    scene_id = scene_folder.name
    scene_png = scene_folder / f"{scene_id}.png"
    if scene_png.exists():
        return scene_png

    job_slug = job_id.replace("job-", "")
    possible_assets = [
        root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / job_slug / f"{scene_id}.png",
        root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / job_slug / f"{scene_id}-storyboard.png",
        root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / job_slug / "scene-01.png",
        root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / job_slug / "scene-01-storyboard.png",
        job_dir / f"{scene_id}.png",
        job_dir / "scene-01.png",
        root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / "ban-hop-dong-luc-0-gio" / f"{scene_id}.png",
        root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / "ban-hop-dong-luc-0-gio" / f"{scene_id}-storyboard.png",
        root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / "ban-hop-dong-luc-0-gio" / "scene-01-storyboard.png",
        root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / "tam-cam" / "scene-tam-cam.png",
    ]
    found_asset = None
    for p in possible_assets:
        if p.exists():
            found_asset = p
            break

    if found_asset:
        print(f"[*] Sao chép ảnh phân cảnh {scene_id} từ: {found_asset}")
        shutil.copy(found_asset, scene_png)
        return scene_png
    else:
        raise FileNotFoundError(f"Không tìm thấy ảnh minh họa cho {scene_id} tại {scene_png}")


def render_scene(
    scene_folder: Path,
    scene_idx: int,
    total_scenes: int,
    root_dir: Path,
    job_dir: Path,
    job_id: str,
    fps: int,
    cap_long_edge: int,
    eraser_seconds: float,
    ffmpeg_bin: str,
    node_env: dict,
    bgm_path: Path | None = None,
    bgm_vol: float = 0.35,
    duck_ratio: float = 6.0,
    with_subtitles: bool = True,
) -> Path:
    scene_id = scene_folder.name
    print(f"\n--- Đang xử lý phân cảnh [{scene_idx + 1}/{total_scenes}]: {scene_id} ---")

    scene_png = ensure_scene_image(scene_folder, job_id, root_dir, job_dir)
    ann_file = scene_folder / f"{scene_id}.annotation.json"
    mp3_file = scene_folder / f"{scene_id}.mp3"
    srt_file = scene_folder / f"{scene_id}.srt"

    if not ann_file.exists():
        raise FileNotFoundError(f"Không tìm thấy file annotation {ann_file}")
    if not mp3_file.exists():
        raise FileNotFoundError(f"Không tìm thấy file audio {mp3_file}")

    is_last = (scene_idx == total_scenes - 1)
    with_eraser = not is_last
    eraser_sec = eraser_seconds if with_eraser else 0.0

    silent_mp4 = scene_folder / "video-silent.mp4"
    scene_mp4 = scene_folder / f"{scene_id}.mp4"
    render_script = Path(__file__).resolve().parent / "render_stream_whiteboard.py"

    print(f"[*] Vẽ nét tay {scene_id} ({fps} FPS, with_eraser={with_eraser}, eraser_sec={eraser_sec}s)...")
    cmd_render = [
        sys.executable,
        str(render_script),
        str(scene_png),
        str(ann_file),
        str(silent_mp4),
        "--fps", str(fps),
        "--cap-long-edge", str(cap_long_edge),
    ]
    if with_eraser:
        cmd_render.extend(["--with-eraser", "--eraser-seconds", str(eraser_sec)])

    res_render = subprocess.run(cmd_render, cwd=str(root_dir), env=node_env)
    if res_render.returncode != 0:
        raise RuntimeError(f"Lỗi khi render hoạt cảnh vẽ tay cho {scene_id} (code {res_render.returncode})")

    print(f"[*] Lồng tiếng, BGM ducking & phụ đề cho {scene_id} bằng FFmpeg...")
    cmd_ffmpeg = [
        ffmpeg_bin, "-y",
        "-i", str(silent_mp4),
        "-i", str(mp3_file),
    ]

    has_bgm = bgm_path is not None and bgm_path.exists()
    if has_bgm:
        cmd_ffmpeg.extend(["-stream_loop", "-1", "-i", str(bgm_path)])
        audio_filter = (
            f"[1:a]apad,asplit=2[voice_sc][voice_mix];"
            f"[2:a]volume={bgm_vol}[bgm];"
            f"[bgm][voice_sc]sidechaincompress=threshold=0.03:ratio={duck_ratio}:attack=100:release=700[ducked_bgm];"
            f"[voice_mix][ducked_bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]"
        )
    else:
        audio_filter = "[1:a]apad[outa]"

    has_sub = with_subtitles and srt_file.exists()
    if has_sub:
        escaped_srt = str(srt_file.resolve()).replace("\\", "/").replace(":", r"\:")
        sub_style = "FontName=Arial,FontSize=15,PrimaryColour=&H002C2C2C,BackColour=&H60FFFFFF,BorderStyle=3,Outline=0,Shadow=1,MarginV=35,Alignment=2"
        filter_complex = f"[0:v]subtitles='{escaped_srt}':force_style='{sub_style}'[outv];{audio_filter}"
        cmd_ffmpeg.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-crf", "20",
            "-preset", "faster",
            "-r", str(fps),
            "-pix_fmt", "yuv420p",
        ])
    else:
        cmd_ffmpeg.extend([
            "-filter_complex", audio_filter,
            "-map", "0:v",
            "-map", "[outa]",
            "-c:v", "copy",
        ])

    cmd_ffmpeg.extend([
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-ac", "2",
        "-shortest",
        str(scene_mp4),
    ])

    res_ffmpeg = subprocess.run(cmd_ffmpeg, env=node_env)
    if res_ffmpeg.returncode != 0:
        raise RuntimeError(f"Lỗi khi ghép âm thanh cho {scene_id} bằng FFmpeg (code {res_ffmpeg.returncode})")

    print(f"[OK] Đã hoàn thành phân cảnh {scene_id}: {scene_mp4}")
    return scene_mp4


def export_whiteboard_video(
    job_id: str = "job-ban-hop-dong-luc-0-gio",
    fps: int = 90,
    cap_long_edge: int = 1080,
    scene: str | None = None,
    eraser_seconds: float = 1.3,
    bgm: str | None = None,
    bgm_vol: float = 0.35,
    duck_ratio: float = 6.0,
    with_subtitles: bool = True,
    root_dir: Path | None = None,
) -> Path | None:
    if root_dir is None:
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
    output_wb = root_dir / "output" / "whiteboard"

    job_dir = output_wb / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    node_env = get_node_env()
    os.environ["PATH"] = node_env["PATH"]
    ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"

    jobs_json_dir = root_dir / "output" / "jobs"
    job_json_file = jobs_json_dir / f"{job_id}.json"

    print("=" * 60)
    print(f"[*] OMNIVIDEO - XUAT VIDEO BANG TRANG {fps} FPS: {job_id}")
    if scene:
        print(f"[*] Mục tiêu: Chỉ render phân cảnh '{scene}'")
    print("=" * 60)

    # 1. Đảm bảo âm thanh & annotation đã được tạo
    mp3_file = job_dir / "input.mp3"
    ann_file = job_dir / "scene-01.annotation.json"
    scenes_dir = job_dir / "scenes"

    has_scenes = scenes_dir.exists() and any(scenes_dir.glob("scene-*"))
    has_single = mp3_file.exists() and ann_file.exists()

    if not (has_scenes or has_single):
        if not job_json_file.exists():
            raise FileNotFoundError(f"Không tìm thấy file kịch bản: {job_json_file}")
        print("[1/3] Đang tổng hợp giọng đọc & đồng bộ phụ đề (job_adapter.py)...")
        adapter_script = Path(__file__).resolve().parent.parent / "job_adapter.py"
        res_adapter = subprocess.run([
            sys.executable,
            str(adapter_script),
            str(job_json_file),
            str(job_dir),
        ], cwd=str(root_dir), env=node_env)
        if res_adapter.returncode != 0:
            raise RuntimeError(f"Tổng hợp job_adapter thất bại (code {res_adapter.returncode})")
    else:
        print("[1/3] Dữ liệu âm thanh & kịch bản đã sẵn sàng.")

    # 2. Xử lý đường dẫn nhạc nền BGM (Audio Ducking)
    if bgm in ("none", "off", "no"):
        bgm_path = None
    else:
        bgm_path = resolve_bgm_path(bgm, root_dir=root_dir)
        if bgm_path is None and bgm is None:
            default_bgm = root_dir / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "healing-piano.mp3"
            if not default_bgm.exists():
                print(f"[*] Đang tự động tạo nhạc nền ambient mặc định: {default_bgm}...")
                generate_default_ambient_bgm(default_bgm)
            bgm_path = default_bgm if default_bgm.exists() else None

    if bgm_path:
        print(f"[*] Nhạc nền BGM: {bgm_path.name} (vol={bgm_vol}, ducking={duck_ratio}:1)")
    if with_subtitles:
        print("[*] Phụ đề: Bật khắc chữ nghệ thuật (Burn-in Subtitles) phong cách giấy kem")

    # 3. Kiểm tra chế độ đa phân cảnh (Multi-Scene)
    all_scene_folders = []
    if scenes_dir.exists() and scenes_dir.is_dir():
        all_scene_folders = sort_scene_folders([
            d for d in scenes_dir.iterdir() if d.is_dir() and d.name.startswith("scene-")
        ])

    final_mp4 = output_wb / f"{job_id}.mp4"
    thumb_png = output_wb / f"{job_id}-thumb.png"

    if all_scene_folders:
        print(f"[*] Phát hiện {len(all_scene_folders)} phân cảnh trong {scenes_dir}: {[d.name for d in all_scene_folders]}")
        if scene:
            target_scene_dir = scenes_dir / scene
            if not (target_scene_dir.exists() and target_scene_dir.is_dir()):
                raise ValueError(f"Không tìm thấy phân cảnh {scene} tại {target_scene_dir}")
            scenes_to_render = [target_scene_dir]
            print(f"[*] Chỉ render phân cảnh: {scene}")
        else:
            scenes_to_render = all_scene_folders
            print(f"[*] Sẽ render toàn bộ {len(all_scene_folders)} phân cảnh")

        for scene_folder in scenes_to_render:
            scene_idx = all_scene_folders.index(scene_folder)
            render_scene(
                scene_folder=scene_folder,
                scene_idx=scene_idx,
                total_scenes=len(all_scene_folders),
                root_dir=root_dir,
                job_dir=job_dir,
                job_id=job_id,
                fps=fps,
                cap_long_edge=cap_long_edge,
                eraser_seconds=eraser_seconds,
                ffmpeg_bin=ffmpeg_bin,
                node_env=node_env,
                bgm_path=bgm_path,
                bgm_vol=bgm_vol,
                duck_ratio=duck_ratio,
                with_subtitles=with_subtitles,
            )

        # Verify all scene-XX.mp4 exist
        all_scene_mp4s = [s / f"{s.name}.mp4" for s in all_scene_folders]
        missing_mp4s = [s.name for s, p in zip(all_scene_folders, all_scene_mp4s) if not p.exists()]
        if missing_mp4s:
            if scene is not None:
                print(f"[WARN] Chưa thể ghép video hoàn chỉnh vì thiếu các phân cảnh chưa render: {', '.join(missing_mp4s)}")
                print(f"[*] Phân cảnh {scene} đã được xuất thành công tại: {scenes_dir / scene / f'{scene}.mp4'}")
                return scenes_dir / scene / f"{scene}.mp4"
            raise RuntimeError(f"Thiếu các file video phân cảnh: {', '.join(missing_mp4s)}")

        print(f"\n[*] Đang ghép nối {len(all_scene_mp4s)} phân cảnh bằng merge_scenes...")
        scripts_dir = Path(__file__).resolve().parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from merge_scenes import _ffmpeg_concat_copy, _pyav_concat

        concat_ok = _ffmpeg_concat_copy(all_scene_mp4s, final_mp4)
        if not concat_ok:
            concat_ok = _pyav_concat(all_scene_mp4s, final_mp4)
        if not concat_ok:
            raise RuntimeError("Lỗi khi ghép nối các phân cảnh!")

        # Thumbnail từ scene đầu tiên
        first_scene_png = ensure_scene_image(all_scene_folders[0], job_id, root_dir, job_dir)
        shutil.copy(first_scene_png, thumb_png)

        # 4. Sinh tài liệu YouTube Metadata & Chapters
        if job_json_file.exists():
            scenes_info = []
            for sc in all_scene_folders:
                sc_id = sc.name
                ann_path = sc / f"{sc_id}.annotation.json"
                dur_s = 0.0
                sc_title = sc_id
                if ann_path.exists():
                    try:
                        with open(ann_path, "r", encoding="utf-8") as af:
                            ann = json.load(af)
                            dur_s = ann.get("sceneDurationMs", 0) / 1000.0
                            if ann.get("badge"):
                                sc_title = ann["badge"]
                    except Exception:
                        pass
                if sc_title == sc_id:
                    prompt_file = sc / "IMAGE_PROMPT.md"
                    if prompt_file.exists():
                        try:
                            for line in prompt_file.read_text(encoding="utf-8").splitlines():
                                if line.startswith("# ") and any(k in line for k in ["Phân cảnh", "CHƯƠNG", "Scene", "scene"]):
                                    clean_t = line.replace("# ", "").replace("Visual Prompt Guidance:", "").strip()
                                    if clean_t:
                                        sc_title = clean_t
                                        break
                        except Exception:
                            pass
                scenes_info.append({"scene_id": sc_id, "title": sc_title, "duration_sec": dur_s})

            meta_file = job_dir / "YOUTUBE_METADATA.md"
            generate_youtube_metadata(job_json_file, scenes_info, meta_file)
            shutil.copy(meta_file, output_wb / f"{job_id}-youtube.md")
            print(f"[*] Đã xuất gói YouTube Metadata & Chapters: {output_wb / f'{job_id}-youtube.md'}")

        size_mb = final_mp4.stat().st_size / (1024 * 1024)
        print("=" * 60)
        print(f"[HOAN THANH] XUAT VIDEO THANH CONG: {final_mp4} ({size_mb:.2f} MB)")
        print(f"OUTPUT={final_mp4}")
        print("=" * 60)
        return final_mp4

    else:
        # Chế độ tương thích ngược (đơn cảnh)
        if scene:
            raise ValueError("Không thể dùng tham số --scene vì job này không có thư mục scenes/")

        scene_png = job_dir / "scene-01.png"
        if not scene_png.exists():
            job_slug = job_id.replace("job-", "")
            possible_assets = [
                root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / job_slug / "scene-01-storyboard.png",
                root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / job_slug / "scene-01.png",
                root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / "ban-hop-dong-luc-0-gio" / "scene-01-storyboard.png",
                root_dir / "workshops" / "workshop-whiteboard" / "assets" / "whiteboard" / "tam-cam" / "scene-tam-cam.png",
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
                raise FileNotFoundError(f"Không tìm thấy ảnh minh họa cho {job_id} tại {scene_png}")

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
            "--cap-long-edge", str(cap_long_edge),
        ]
        res_render = subprocess.run(cmd_render, cwd=str(root_dir), env=node_env)
        if res_render.returncode != 0:
            raise RuntimeError(f"Lỗi khi render hoạt cảnh vẽ tay (code {res_render.returncode})")

        print("[3/3] Đang lồng tiếng, phụ đề & khớp khung hình bằng FFmpeg...")
        cmd_ffmpeg = [ffmpeg_bin, "-y", "-i", str(silent_mp4), "-i", str(mp3_file)]
        has_bgm = bgm_path is not None and bgm_path.exists()
        if has_bgm:
            cmd_ffmpeg.extend(["-stream_loop", "-1", "-i", str(bgm_path)])
            audio_filter = (
                f"[1:a]apad,asplit=2[voice_sc][voice_mix];"
                f"[2:a]volume={bgm_vol}[bgm];"
                f"[bgm][voice_sc]sidechaincompress=threshold=0.03:ratio={duck_ratio}:attack=100:release=700[ducked_bgm];"
                f"[voice_mix][ducked_bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]"
            )
        else:
            audio_filter = "[1:a]apad[outa]"

        srt_file = job_dir / "input.srt"
        has_sub = with_subtitles and srt_file.exists()
        if has_sub:
            escaped_srt = str(srt_file.resolve()).replace("\\", "/").replace(":", r"\:")
            sub_style = "FontName=Arial,FontSize=15,PrimaryColour=&H002C2C2C,BackColour=&H60FFFFFF,BorderStyle=3,Outline=0,Shadow=1,MarginV=35,Alignment=2"
            filter_complex = f"[0:v]subtitles='{escaped_srt}':force_style='{sub_style}'[outv];{audio_filter}"
            cmd_ffmpeg.extend([
                "-filter_complex", filter_complex,
                "-map", "[outv]",
                "-map", "[outa]",
                "-c:v", "libx264",
                "-crf", "20",
                "-preset", "faster",
                "-r", str(fps),
                "-pix_fmt", "yuv420p",
            ])
        else:
            cmd_ffmpeg.extend([
                "-filter_complex", audio_filter,
                "-map", "0:v",
                "-map", "[outa]",
                "-c:v", "copy",
            ])

        cmd_ffmpeg.extend([
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "44100",
            "-ac", "2",
            "-shortest",
            str(final_mp4),
        ])
        res_ffmpeg = subprocess.run(cmd_ffmpeg, env=node_env)
        if res_ffmpeg.returncode != 0:
            raise RuntimeError(f"Lỗi khi ghép âm thanh bằng FFmpeg (code {res_ffmpeg.returncode})")

        if scene_png.exists():
            shutil.copy(scene_png, thumb_png)

        size_mb = final_mp4.stat().st_size / (1024 * 1024)
        print("=" * 60)
        print(f"[HOAN THANH] XUAT VIDEO THANH CONG: {final_mp4} ({size_mb:.2f} MB)")
        print(f"OUTPUT={final_mp4}")
        print("=" * 60)
        return final_mp4


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Xuất video Whiteboard hoàn chỉnh (hỗ trợ đa phân cảnh & YouTube Audio)")
    parser.add_argument("job_id", nargs="?", default="job-ban-hop-dong-luc-0-gio", help="ID của job cần xuất")
    parser.add_argument("--fps", type=int, default=90, help="Số khung hình / giây (mặc định 90)")
    parser.add_argument("--cap-long-edge", type=int, default=1080, help="Giới hạn cạnh dài khung hình (mặc định 1080)")
    parser.add_argument("--scene", type=str, default=None, help="Chỉ render phân cảnh này (ví dụ: scene-01), sau đó ghép lại toàn bộ")
    parser.add_argument("--eraser-seconds", type=float, default=1.3, help="Thời lượng hiệu ứng xóa bảng giữa các scene (giây, mặc định 1.3)")
    parser.add_argument("--bgm", type=str, default=None, help="Đường dẫn file BGM, hoặc 'none'/'off' để tắt nhạc nền")
    parser.add_argument("--bgm-vol", type=float, default=0.35, help="Âm lượng nền BGM cơ bản (mặc định 0.35)")
    parser.add_argument("--duck-ratio", type=float, default=6.0, help="Tỷ lệ nén ducking khi có giọng đọc (mặc định 6.0)")
    parser.add_argument("--with-subtitles", dest="with_subtitles", action="store_true", default=True, help="Khắc phụ đề nghệ thuật lên video (mặc định Bật)")
    parser.add_argument("--no-subtitles", dest="with_subtitles", action="store_false", help="Tắt hiển thị phụ đề")
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    try:
        export_whiteboard_video(
            args.job_id,
            fps=args.fps,
            cap_long_edge=args.cap_long_edge,
            scene=args.scene,
            eraser_seconds=args.eraser_seconds,
            bgm=args.bgm,
            bgm_vol=args.bgm_vol,
            duck_ratio=args.duck_ratio,
            with_subtitles=args.with_subtitles,
        )
    except Exception as e:
        print(f"[ERR] {e}", file=sys.stderr)
        sys.exit(1)

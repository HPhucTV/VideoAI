"""
Xưởng 5: Threads & Social Drama (workshop-threads)
Module: compositor.py
Tính năng:
- Lắp ráp video hoàn chỉnh 9:16 (1080x1920) chuẩn Shorts / TikTok / Reels.
- Hỗ trợ video nền gameplay lặp mượt mà (-stream_loop -1).
- Chèn âm thanh Pop SFX tại từng mốc đổi thẻ bài viết / bình luận.
- Hỗ trợ nhạc nền BGM với tính năng auto-ducking nhẹ nhàng.
- Chồng lớp các thẻ PNG trong suốt bằng bộ lọc filter_complex của FFmpeg.
"""
from __future__ import annotations

import glob
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("workshop_threads.compositor")


def get_video_duration(video_path: str | Path) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())


def make_threads_video(
    background_path: str | Path,
    segments: List[Dict[str, Any]],
    output_path: str | Path,
    sfx_pop_path: Optional[str | Path] = None,
    bgm_path: Optional[str | Path] = None,
    width: int = 1080,
    height: int = 1920,
    pause_between: float = 0.35,
) -> Path:
    """
    Render video Threads hoàn chỉnh 9:16:
    - background_path: file video nền (gameplay Minecraft, Subway Surfers, GTA5,...)
    - segments: danh sách dict gồm:
        {
          "card_png": "path/to/card.png",
          "audio_mp3": "path/to/voice.mp3",
          "duration": 4.2  # giây
        }
    - sfx_pop_path: âm thanh pop khi chuyển card
    - bgm_path: nhạc nền chill
    - output_path: đường dẫn file .mp4 xuất ra
    """
    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = out_file.parent / f"temp_{out_file.stem}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 1. Tính toán timeline từng phân đoạn
    timeline = []
    current_time = 0.0
    for idx, seg in enumerate(segments):
        start_t = current_time
        seg_dur = float(seg["duration"]) + pause_between
        end_t = start_t + seg_dur
        timeline.append({
            "index": idx,
            "card_png": str(Path(seg["card_png"]).resolve()),
            "audio_mp3": str(Path(seg["audio_mp3"]).resolve()),
            "start": start_t,
            "end": end_t,
            "duration": seg_dur,
        })
        current_time = end_t

    total_duration = current_time

    # 2. Xây dựng Master Audio với FFmpeg
    audio_inputs = []
    filter_complex_audio = []
    mix_labels = []

    for idx, item in enumerate(timeline):
        audio_inputs.extend(["-i", item["audio_mp3"]])
        delay_ms = int(item["start"] * 1000)
        filter_complex_audio.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[a_tts_{idx}];")
        mix_labels.append(f"[a_tts_{idx}]")

    # Thêm SFX Pop ở mỗi chuyển cảnh nếu có
    next_input_idx = len(timeline)
    sfx_exists = sfx_pop_path and Path(sfx_pop_path).exists()
    if sfx_exists:
        sfx_idx = next_input_idx
        audio_inputs.extend(["-i", str(Path(sfx_pop_path).resolve())])
        next_input_idx += 1
        for idx, item in enumerate(timeline):
            pop_delay_ms = int(item["start"] * 1000)
            filter_complex_audio.append(
                f"[{sfx_idx}:a]adelay={pop_delay_ms}|{pop_delay_ms},volume=0.9[a_pop_{idx}];"
            )
            mix_labels.append(f"[a_pop_{idx}]")

    # Thêm BGM nếu có
    bgm_exists = bgm_path and Path(bgm_path).exists()
    if bgm_exists:
        bgm_idx = next_input_idx
        audio_inputs.extend(["-stream_loop", "-1", "-i", str(Path(bgm_path).resolve())])
        next_input_idx += 1
        fade_out_start = max(0.5, total_duration - 1.0)
        filter_complex_audio.append(
            f"[{bgm_idx}:a]volume=0.14,afade=t=in:ss=0:d=0.5,afade=t=out:st={fade_out_start:.2f}:d=1.0[a_bgm];"
        )
        mix_labels.append("[a_bgm]")

    # Mix toàn bộ audio
    total_mix_count = len(mix_labels)
    filter_complex_audio.append(
        f"{''.join(mix_labels)}amix=inputs={total_mix_count}:normalize=0:dropout_transition=0[a_master]"
    )

    master_audio_path = temp_dir / "master_audio.wav"
    cmd_audio = [
        "ffmpeg", "-y",
        *audio_inputs,
        "-filter_complex", "".join(filter_complex_audio),
        "-map", "[a_master]",
        "-t", f"{total_duration:.3f}",
        str(master_audio_path),
    ]
    subprocess.run(cmd_audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # 3. Dựng Video tổng hợp (Ghép Nền + Overlay Cards + Master Audio)
    video_cmd_inputs = [
        "-stream_loop", "-1",
        "-i", str(Path(background_path).resolve()),
    ]
    for item in timeline:
        video_cmd_inputs.extend(["-i", item["card_png"]])
    video_cmd_inputs.extend(["-i", str(master_audio_path)])

    # Scale/crop video nền về đúng width x height
    v_filters = [f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}[base];"]
    last_v = "[base]"

    for idx, item in enumerate(timeline):
        card_input_idx = idx + 1
        next_v = f"[v{idx}]" if idx < len(timeline) - 1 else "[v_final]"
        # Căn giữa màn hình (x = (W - w)/2, y = (H - h)/2)
        v_filters.append(
            f"{last_v}[{card_input_idx}:v]overlay=(W-w)/2:(H-h)/2:enable='between(t,{item['start']:.3f},{item['end']:.3f})'{next_v};"
        )
        last_v = next_v

    filter_complex_video = "".join(v_filters)
    audio_stream_idx = len(timeline) + 1

    cmd_video = [
        "ffmpeg", "-y",
        *video_cmd_inputs,
        "-filter_complex", filter_complex_video,
        "-map", "[v_final]",
        "-map", f"{audio_stream_idx}:a",
        "-t", f"{total_duration:.3f}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        str(out_file),
    ]
    subprocess.run(cmd_video, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Dọn dẹp thư mục tạm
    try:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass

    return out_file

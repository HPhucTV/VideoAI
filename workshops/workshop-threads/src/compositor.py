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


_SFX_DIR = Path(__file__).resolve().parent.parent / "assets" / "sfx"
_MEMES_DIR = Path(__file__).resolve().parent.parent / "assets" / "memes"


def find_meme_for_sfx(sfx_name: Optional[str]) -> Optional[Path]:
    """Tìm sticker meme tương ứng với âm thanh SFX."""
    if not sfx_name:
        return None
    stem = Path(sfx_name).stem.lower()
    candidate = _MEMES_DIR / f"{stem}.png"
    if candidate.exists():
        return candidate
    return None


def format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp H:MM:SS.cc (centiseconds)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def generate_karaoke_ass(timeline: List[Dict[str, Any]], out_ass: Path) -> Path:
    """
    Sinh file phụ đề ASS với hiệu ứng Karaoke word-by-word highlight.
    Mỗi từ khi phát âm sẽ tự động chuyển màu sang Neon Cyan / Vàng kim rực rỡ.
    """
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,Arial,44,&H00FFFFFF,&H0000DAF5,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3.5,0,2,50,50,280,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for item in timeline:
        raw_text = item.get("text", "").strip()
        if not raw_text:
            continue
        clean_text = " ".join(raw_text.split())
        words = clean_text.split()
        if not words:
            continue

        start_t = item["start"]
        end_t = item["end"]
        dur_sec = max(0.2, end_t - start_t)
        total_cs = int(dur_sec * 100)

        total_len = sum(max(1, len(w)) for w in words)
        k_tokens = []
        spent_cs = 0
        for idx, w in enumerate(words):
            if idx == len(words) - 1:
                w_cs = max(5, total_cs - spent_cs)
            else:
                w_cs = max(8, int(round((len(w) / total_len) * total_cs)))
                spent_cs += w_cs
            k_tokens.append(f"{{\\k{w_cs}}}{w}")

        karaoke_line = " ".join(k_tokens)
        ass_start = format_ass_time(start_t)
        ass_end = format_ass_time(end_t)
        lines.append(f"Dialogue: 0,{ass_start},{ass_end},Karaoke,,0,0,0,,{karaoke_line}\n")

    out_ass.write_text("".join(lines), encoding="utf-8")
    return out_ass


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
    enable_spring_pop: bool = True,
    enable_karaoke: bool = False,
    bgm_volume: float = 0.38,
    enable_ducking: bool = True,
) -> Path:
    """
    Render video Threads hoàn chỉnh 9:16:
    - background_path: file video nền (gameplay Minecraft, Subway Surfers, GTA5,...)
    - segments: danh sách dict gồm:
        {
          "card_png": "path/to/card.png",
          "audio_mp3": "path/to/voice.mp3",
          "duration": 4.2,  # giây
          "text": "câu thoại...",
          "sfx": "vine_boom.wav", # tùy chọn
          "shake": True # rung màn hình nhẹ
        }
    - sfx_pop_path: âm thanh pop khi chuyển card
    - bgm_path: nhạc nền chill / hài hước
    - output_path: đường dẫn file .mp4 xuất ra
    - enable_spring_pop: hiệu ứng nảy thẻ lò xo vật lý
    - enable_karaoke: phụ đề karaoke word-by-word highlight (mặc định False)
    - bgm_volume: âm lượng nhạc nền (mặc định 0.38 rõ ràng, không bị chìm)
    - enable_ducking: tự động hạ âm nhạc nền khi nhân vật nói và nâng lên khi im lặng
    """
    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = out_file.parent / f"temp_{out_file.stem}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 1. Tính toán timeline từng phân đoạn & Điểm rơi Punchline Meme
    timeline = []
    current_time = 0.0
    for idx, seg in enumerate(segments):
        start_t = current_time
        seg_dur = float(seg["duration"]) + pause_between
        end_t = start_t + seg_dur

        custom_sfx = seg.get("sfx")
        meme_candidate = find_meme_for_sfx(custom_sfx)

        # Tính toán mốc thời gian punchline cho Meme SFX & Sticker
        if custom_sfx and custom_sfx != "pop.wav":
            punch_offset = seg.get("punchline_offset")
            if punch_offset is not None:
                punch_t = start_t + float(punch_offset)
            else:
                # Đặt punchline rơi vào đoạn kết thúc câu thoại (khoảng 1.2s - 1.4s trước khi chuyển card)
                punch_t = max(start_t + 0.6, end_t - 1.4)
        else:
            punch_t = None

        timeline.append({
            "index": idx,
            "card_png": str(Path(seg["card_png"]).resolve()),
            "audio_mp3": str(Path(seg["audio_mp3"]).resolve()),
            "text": seg.get("text") or seg.get("content", ""),
            "sfx": custom_sfx,
            "punchline_t": punch_t,
            "meme_png": str(meme_candidate.resolve()) if meme_candidate else None,
            "shake": seg.get("shake", False),
            "start": start_t,
            "end": end_t,
            "duration": seg_dur,
        })
        current_time = end_t

    total_duration = current_time

    # 2. Xây dựng Master Audio với FFmpeg
    audio_inputs = []
    filter_complex_audio = []
    tts_labels = []

    for idx, item in enumerate(timeline):
        audio_inputs.extend(["-i", item["audio_mp3"]])
        delay_ms = int(item["start"] * 1000)
        filter_complex_audio.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[a_tts_{idx}];")
        tts_labels.append(f"[a_tts_{idx}]")

    # Gom toàn bộ giọng đọc TTS thành voice bus
    if len(tts_labels) == 1:
        voice_bus_label = tts_labels[0]
    else:
        filter_complex_audio.append(f"{''.join(tts_labels)}amix=inputs={len(tts_labels)}:normalize=0[a_voice_raw];")
        voice_bus_label = "[a_voice_raw]"

    next_input_idx = len(timeline)
    sfx_cache = {}
    default_pop = Path(sfx_pop_path) if sfx_pop_path and Path(sfx_pop_path).exists() else (_SFX_DIR / "pop.wav")
    sfx_labels = []

    # 2.1. Âm thanh Pop chuyển thẻ nhẹ nhàng tại start_t của mỗi phân cảnh
    if default_pop.exists():
        pop_key = str(default_pop.resolve())
        audio_inputs.extend(["-i", pop_key])
        pop_in_idx = next_input_idx
        next_input_idx += 1
        for item in timeline:
            delay_ms = int(item["start"] * 1000)
            tag = f"[a_pop_{item['index']}]"
            filter_complex_audio.append(
                f"[{pop_in_idx}:a]adelay={delay_ms}|{delay_ms},volume=0.65{tag};"
            )
            sfx_labels.append(tag)

    # 2.2. Âm thanh Meme SFX chính xác vang lên tại mốc PUNCHLINE (punchline_t)
    for item in timeline:
        custom_sfx = item.get("sfx")
        punch_t = item.get("punchline_t")
        if custom_sfx and custom_sfx != "pop.wav" and punch_t is not None:
            sfx_candidate = (_SFX_DIR / custom_sfx)
            if sfx_candidate.exists():
                sfx_key = str(sfx_candidate.resolve())
                if sfx_key not in sfx_cache:
                    audio_inputs.extend(["-i", sfx_key])
                    sfx_cache[sfx_key] = next_input_idx
                    next_input_idx += 1
                s_idx = sfx_cache[sfx_key]
                delay_ms = int(punch_t * 1000)
                vol = 0.95
                tag = f"[a_meme_sfx_{item['index']}]"
                filter_complex_audio.append(
                    f"[{s_idx}:a]adelay={delay_ms}|{delay_ms},volume={vol}{tag};"
                )
                sfx_labels.append(tag)

    # Thêm BGM với Dynamic Audio Ducking chuyên nghiệp
    bgm_exists = bgm_path and Path(bgm_path).exists()
    final_mix_labels = []

    if bgm_exists:
        bgm_idx = next_input_idx
        audio_inputs.extend(["-stream_loop", "-1", "-i", str(Path(bgm_path).resolve())])
        next_input_idx += 1
        fade_out_start = max(0.5, total_duration - 1.0)
        filter_complex_audio.append(
            f"[{bgm_idx}:a]volume={bgm_volume:.2f},afade=t=in:ss=0:d=0.5,afade=t=out:st={fade_out_start:.2f}:d=1.0[a_bgm_base];"
        )
        if enable_ducking:
            filter_complex_audio.append(f"{voice_bus_label}asplit=2[a_voice_mix][a_voice_sc];")
            filter_complex_audio.append(
                "[a_bgm_base][a_voice_sc]sidechaincompress=threshold=0.035:ratio=3.8:attack=25:release=250[a_bgm_ducked];"
            )
            final_mix_labels.append("[a_voice_mix]")
            final_mix_labels.append("[a_bgm_ducked]")
        else:
            final_mix_labels.append(voice_bus_label)
            final_mix_labels.append("[a_bgm_base]")
    else:
        final_mix_labels.append(voice_bus_label)

    final_mix_labels.extend(sfx_labels)

    # Mix toàn bộ audio
    total_mix_count = len(final_mix_labels)
    if total_mix_count == 1:
        filter_complex_audio.append(f"{final_mix_labels[0]}anull[a_master]")
    else:
        filter_complex_audio.append(
            f"{''.join(final_mix_labels)}amix=inputs={total_mix_count}:normalize=0:dropout_transition=0[a_master]"
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

    # 3. Dựng Video tổng hợp (Ghép Nền + Overlay Cards + Spring Pop + Meme Stickers + Karaoke + Master Audio)
    video_cmd_inputs = [
        "-stream_loop", "-1",
        "-i", str(Path(background_path).resolve()),
    ]
    for item in timeline:
        video_cmd_inputs.extend(["-i", item["card_png"]])

    # Đăng ký input cho từng Meme Sticker
    meme_input_map = {}
    current_v_in_idx = len(timeline) + 1
    for item in timeline:
        if item.get("meme_png"):
            video_cmd_inputs.extend(["-i", item["meme_png"]])
            meme_input_map[item["index"]] = current_v_in_idx
            current_v_in_idx += 1

    audio_stream_idx = current_v_in_idx
    video_cmd_inputs.extend(["-i", str(master_audio_path)])

    # Scale/crop video nền về đúng width x height
    v_filters = [f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}[base];"]
    last_v = "[base]"

    for idx, item in enumerate(timeline):
        card_input_idx = idx + 1
        next_v = f"[v{idx}]"
        st = item["start"]
        et = item["end"]

        # 3.1. Overlay thẻ bài viết
        if enable_spring_pop:
            x_expr = "(W-w)/2"
            if item.get("shake"):
                x_expr = f"(W-w)/2+if(lt(t-{st:.3f},0.16),8*sin(50*(t-{st:.3f}))*exp(-14*(t-{st:.3f})),0)"
            y_expr = f"(H-h)/2+if(lt(t-{st:.3f},0.22),35*exp(-14*(t-{st:.3f}))*cos(18*(t-{st:.3f})),0)"
            v_filters.append(
                f"{last_v}[{card_input_idx}:v]overlay=x='{x_expr}':y='{y_expr}':enable='between(t,{st:.3f},{et:.3f})'{next_v};"
            )
        else:
            v_filters.append(
                f"{last_v}[{card_input_idx}:v]overlay=(W-w)/2:(H-h)/2:enable='between(t,{st:.3f},{et:.3f})'{next_v};"
            )
        last_v = next_v

        # 3.2. Overlay Meme Sticker đồng bộ với punchline
        if idx in meme_input_map and item.get("punchline_t") is not None:
            meme_in = meme_input_map[idx]
            meme_v = f"[vm_{idx}]"
            pt = item["punchline_t"]
            # Nảy sticker lò xo vật lý tại khoảng trống dưới card (y = 1220)
            m_y_expr = f"1220+if(lt(t-{pt:.3f},0.22),35*exp(-14*(t-{pt:.3f}))*cos(18*(t-{pt:.3f})),0)"
            v_filters.append(
                f"{last_v}[{meme_in}:v]overlay=x='(W-w)/2':y='{m_y_expr}':enable='between(t,{pt:.3f},{et:.3f})'{meme_v};"
            )
            last_v = meme_v

    # Thêm Karaoke ASS subtitles nếu bật
    if enable_karaoke and any(item.get("text") for item in timeline):
        ass_path = temp_dir / "karaoke.ass"
        generate_karaoke_ass(timeline, ass_path)
        v_filters.append(f"{last_v}subtitles=karaoke.ass[v_final];")
    else:
        v_filters.append(f"{last_v}null[v_final];")

    filter_complex_video = "".join(v_filters)

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
    subprocess.run(cmd_video, cwd=temp_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Dọn dẹp thư mục tạm
    try:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass

    return out_file

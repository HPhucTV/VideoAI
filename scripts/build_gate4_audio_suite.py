"""
Build all 16 Shots Master Audio with Edge-TTS + Rubberband 48kHz Stereo
Robust phonetic fallback to ensure 100% success on Microsoft Edge-TTS server.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
import edge_tts

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = ROOT_DIR / "output" / "cinematic" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

SHOTS = [
    {
        "shot_id": "shot_01",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "variants": [
            "Chào mừng bạn đến với thế giới của những bộ não nhân tạo thông minh nhất."
        ]
    },
    {
        "shot_id": "shot_02",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.10,
        "tempo_factor": 1.05,
        "variants": [
            "Tớ là Chatty! Hỏi tớ bất cứ điều gì, tớ đều có câu trả lời ngay!"
        ]
    },
    {
        "shot_id": "shot_03",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.04,
        "tempo_factor": 1.03,
        "variants": [
            "Còn tớ là Agent-X. Tớ không chỉ trả lời, tớ giải quyết vấn đề bằng hành động."
        ]
    },
    {
        "shot_id": "shot_04",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "variants": [
            "Bất ngờ, một sự cố rò rỉ dữ liệu nghiêm trọng bùng nổ toàn hệ thống!"
        ]
    },
    {
        "shot_id": "shot_05",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.12,
        "tempo_factor": 1.08,
        "variants": [
            "Nguy hiểm quá! Các bạn nên ngắt kết nối mạng và gõ lệnh vá lỗi ngay!"
        ]
    },
    {
        "shot_id": "shot_06",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.08,
        "tempo_factor": 1.02,
        "variants": [
            "Nhưng tớ chỉ là trợ lý ảo, tớ không có quyền truy cập để sửa nó!",
            "Nhưng tớ chỉ là chát bót, tớ không có quyền truy cập để sửa nó!"
        ]
    },
    {
        "shot_id": "shot_07",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "variants": [
            "Chatbot biết mọi giải pháp, nhưng hoàn toàn bất lực trong việc can thiệp thực tế."
        ]
    },
    {
        "shot_id": "shot_08",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.04,
        "tempo_factor": 1.03,
        "variants": [
            "Đừng lo! Hãy để tớ lập kế hoạch và kích hoạt công cụ xử lý."
        ]
    },
    {
        "shot_id": "shot_09",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "variants": [
            "Agent tự động chia nhỏ mục tiêu, mở hệ thống và gọi các công cụ cứu hộ.",
            "Chiến binh Agent tự động chia nhỏ mục tiêu, mở dòng lệnh và gọi các công cụ cứu hộ."
        ]
    },
    {
        "shot_id": "shot_10",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "variants": [
            "Nếu gặp lỗi, Agent sẽ tự tư duy, sửa sai và thử lại đến khi thành công.",
            "Nếu gặp lỗi trong quá trình chạy, hệ thống sẽ tự sửa sai và thử lại thành công."
        ]
    },
    {
        "shot_id": "shot_11",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.04,
        "tempo_factor": 1.04,
        "variants": [
            "Nhiệm vụ hoàn tất! Tường lửa đã phục hồi và báo cáo đã gửi về sếp."
        ]
    },
    {
        "shot_id": "shot_12",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.10,
        "tempo_factor": 1.05,
        "variants": [
            "Cậu đỉnh thật đấy! Vậy điều gì làm cậu khác biệt hoàn toàn với tớ?"
        ]
    },
    {
        "shot_id": "shot_13",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.03,
        "tempo_factor": 1.02,
        "variants": [
            "Tớ có bốn thứ: Não bộ phân tích, Bộ nhớ dài hạn, Bộ công cụ thực thi, và Quyền tự chủ."
        ]
    },
    {
        "shot_id": "shot_14",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "variants": [
            "Chatbot là cố vấn thông thái trong phòng họp, còn Agent là chiến binh trực tiếp ra trận.",
            "Một bên là cố vấn thông thái trong phòng họp, còn một bên là chiến binh trực tiếp ra trận."
        ]
    },
    {
        "shot_id": "shot_15",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.04,
        "tempo_factor": 1.03,
        "variants": [
            "Tương lai không còn là gõ lệnh chờ đợi, mà là giao việc cho các Agent tự làm.",
            "Tương lai không còn là gõ prompt chờ đợi, mà là để cho các trợ lý tự hành động."
        ]
    },
    {
        "shot_id": "shot_16",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.10,
        "tempo_factor": 1.06,
        "variants": [
            "Đăng ký kênh Giải Mã Tếch để cùng làm chủ làn sóng công nghệ mới ngay hôm nay nhé!",
            "Hãy theo dõi kênh Giải Mã Tếch để cùng làm chủ làn sóng trí tuệ nhân tạo mới nhé!"
        ]
    }
]

async def process_shot(item):
    raw_mp3 = AUDIO_DIR / f"{item['shot_id']}_raw.mp3"
    final_wav = AUDIO_DIR / f"{item['shot_id']}.wav"

    # If already exists and valid, skip
    if final_wav.exists() and final_wav.stat().st_size > 100000:
        cmd_probe = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(final_wav)
        ]
        dur = float(subprocess.run(cmd_probe, capture_output=True, text=True).stdout.strip() or 0.0)
        print(f"⏩ [{item['shot_id']}] (Ready {dur:.2f}s): {item['variants'][0]}")
        return {
            "shot_id": item["shot_id"],
            "speaker": item["speaker"],
            "audio_file": str(final_wav.name),
            "duration_s": round(dur, 2),
            "text": item["variants"][0]
        }

    chosen_text = None
    for text in item["variants"]:
        for attempt in range(1, 3):
            try:
                c = edge_tts.Communicate(text, item["voice"])
                await c.save(str(raw_mp3))
                if raw_mp3.exists() and raw_mp3.stat().st_size > 5000:
                    chosen_text = text
                    break
            except Exception:
                await asyncio.sleep(1.0)
        if chosen_text:
            break

    if not chosen_text:
        raise RuntimeError(f"All variants failed for {item['shot_id']}")

    # Apply rubberband pitch/tempo modulation + 48kHz Stereo 16-bit WAV + 0.35s tail breath
    p = item["pitch_factor"]
    t = item["tempo_factor"]
    filter_str = f"rubberband=pitch={p}:tempo={t},apad=pad_dur=0.35,aformat=sample_rates=48000:channel_layouts=stereo"

    cmd_ffmpeg = [
        "ffmpeg", "-y", "-i", str(raw_mp3),
        "-af", filter_str,
        "-c:a", "pcm_s16le", str(final_wav)
    ]
    subprocess.run(cmd_ffmpeg, capture_output=True, check=True)

    if raw_mp3.exists():
        raw_mp3.unlink()

    # Probe duration
    cmd_probe = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(final_wav)
    ]
    dur = float(subprocess.run(cmd_probe, capture_output=True, text=True).stdout.strip() or 0.0)

    print(f"✅ [{item['shot_id']}] {item['speaker']} ({dur:.2f}s): {chosen_text}")
    return {
        "shot_id": item["shot_id"],
        "speaker": item["speaker"],
        "audio_file": str(final_wav.name),
        "duration_s": round(dur, 2),
        "text": chosen_text
    }

async def main():
    print("🎙 Generating Studio 48kHz Master Audio for all 16 Shots...")
    manifest = []
    for item in SHOTS:
        res = await process_shot(item)
        manifest.append(res)
        await asyncio.sleep(1.0)

    # Save manifest
    manifest_file = AUDIO_DIR / "audio_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    total_dur = sum(x["duration_s"] for x in manifest)
    print(f"\n✨ Generated {len(manifest)} audio files! Total dialogue duration: {total_dur:.2f}s")

    # Concatenate master dialogue track
    concat_txt = AUDIO_DIR / "concat_list.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for m in manifest:
            f.write(f"file '{m['audio_file']}'\n")

    master_wav = AUDIO_DIR / "master_dialogue_48k.wav"
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy", str(master_wav)
    ]
    subprocess.run(cmd_concat, capture_output=True, check=True)
    if concat_txt.exists():
        concat_txt.unlink()

    print(f"🎧 Master Dialogue Timeline Exported: {master_wav} ({total_dur:.2f}s)")

if __name__ == "__main__":
    asyncio.run(main())

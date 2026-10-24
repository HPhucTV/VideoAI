"""
Generate Voice Lines for all 16 Shots of "Chatbot AI vs AI Agent (Chibi 3D)"
Uses Microsoft Edge-TTS direct Python API with character modulation, resampled to 48kHz Stereo 16-bit WAV.
"""

import asyncio
import json
import os
import subprocess
import sys
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
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": "Chào mừng bạn đến với thế giới của những bộ não nhân tạo thông minh nhất."
    },
    {
        "shot_id": "shot_02",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+8%",
        "pitch": "+14Hz",
        "text": "Tớ là Chatty! Hỏi tớ bất cứ điều gì, tớ đều có câu trả lời ngay!"
    },
    {
        "shot_id": "shot_03",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+5%",
        "pitch": "+6Hz",
        "text": "Còn tớ là Agent-X. Tớ không chỉ trả lời, tớ giải quyết vấn đề bằng hành động."
    },
    {
        "shot_id": "shot_04",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": "Bất ngờ, một sự cố rò rỉ dữ liệu nghiêm trọng bùng nổ toàn hệ thống!"
    },
    {
        "shot_id": "shot_05",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+10%",
        "pitch": "+16Hz",
        "text": "Nguy hiểm quá! Theo tài liệu 2026, các bạn nên ngắt mạng và gõ lệnh vá lỗi!"
    },
    {
        "shot_id": "shot_06",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+6%",
        "pitch": "+10Hz",
        "text": "Nhưng tớ... tớ chỉ là Chatbot, tớ không có quyền truy cập để sửa nó!"
    },
    {
        "shot_id": "shot_07",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": "Chatbot biết mọi giải pháp, nhưng hoàn toàn bất lực trong việc can thiệp thực tế."
    },
    {
        "shot_id": "shot_08",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+4%",
        "pitch": "+6Hz",
        "text": "Đừng lo. Hãy để tớ lập kế hoạch và kích hoạt công cụ xử lý."
    },
    {
        "shot_id": "shot_09",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": "Agent tự động chia nhỏ mục tiêu, mở terminal và trực tiếp gọi các API cứu hộ."
    },
    {
        "shot_id": "shot_10",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": "Nếu gặp lỗi, Agent sẽ tự tư duy, sửa sai và thử lại đến khi thành công."
    },
    {
        "shot_id": "shot_11",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+5%",
        "pitch": "+6Hz",
        "text": "Nhiệm vụ hoàn tất! Tường lửa đã phục hồi và báo cáo đã gửi về sếp."
    },
    {
        "shot_id": "shot_12",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+8%",
        "pitch": "+14Hz",
        "text": "Cậu đỉnh thật đấy! Vậy điều gì làm cậu khác biệt hoàn toàn với tớ?"
    },
    {
        "shot_id": "shot_13",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+3%",
        "pitch": "+5Hz",
        "text": "Tớ có 4 thứ: Não bộ phân tích, Bộ nhớ dài hạn, Bộ công cụ thực thi, và Quyền tự chủ."
    },
    {
        "shot_id": "shot_14",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
        "text": "Chatbot là cố vấn thông thái trong phòng họp, còn Agent là chiến binh trực tiếp ra trận."
    },
    {
        "shot_id": "shot_15",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+4%",
        "pitch": "+6Hz",
        "text": "Tương lai không còn là gõ prompt chờ đợi, mà là giao việc cho các Agent tự làm."
    },
    {
        "shot_id": "shot_16",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+8%",
        "pitch": "+14Hz",
        "text": "Đăng ký kênh GiaiMaTech để cùng làm chủ làn sóng AI Agent ngay hôm nay nhé!"
    }
]

async def generate_shot(item):
    raw_mp3 = AUDIO_DIR / f"{item['shot_id']}_raw.mp3"
    clean_wav = AUDIO_DIR / f"{item['shot_id']}.wav"

    # 1. Edge-TTS direct Python async call
    comm = edge_tts.Communicate(
        text=item["text"],
        voice=item["voice"],
        rate=item["rate"],
        pitch=item["pitch"]
    )
    await comm.save(str(raw_mp3))

    # 2. Convert to Studio 48kHz Stereo 16-bit WAV with gentle padding
    cmd_ffmpeg = [
        "ffmpeg", "-y", "-i", str(raw_mp3),
        "-af", "apad=pad_dur=0.35,aformat=sample_rates=48000:channel_layouts=stereo",
        "-c:a", "pcm_s16le", str(clean_wav)
    ]
    subprocess.run(cmd_ffmpeg, capture_output=True)

    if raw_mp3.exists():
        raw_mp3.unlink()

    # 3. Get exact duration
    cmd_probe = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(clean_wav)
    ]
    dur_res = subprocess.run(cmd_probe, capture_output=True, text=True)
    dur = float(dur_res.stdout.strip() or 0.0)

    print(f"✅ [{item['shot_id']}] {item['speaker']} ({dur:.2f}s): {item['text']}")
    return {
        **item,
        "audio_file": str(clean_wav.name),
        "duration_s": round(dur, 2)
    }

async def main():
    print("🎙 Generating 16 Voice Lines with Microsoft Edge-TTS...")
    manifest = []
    for item in SHOTS:
        res = await generate_shot(item)
        manifest.append(res)
        await asyncio.sleep(0.3)

    manifest_path = AUDIO_DIR / "audio_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    total_dur = sum(x["duration_s"] for x in manifest)
    print(f"\n✨ Generated {len(manifest)} audio files! Total voice duration: {total_dur:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())

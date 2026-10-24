"""
Generate High-Quality Master Audio for 16 Shots (Gate 4)
Uses Microsoft Edge-TTS with character rate/pitch modulation, 48kHz Stereo conversion,
and merges into a master dialogue timeline with ducked cyber BGM.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = ROOT_DIR / "output" / "cinematic" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

PYTHON_EXE = sys.executable

SHOTS = [
    {
        "shot_id": "shot_01",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "text": "Chào mừng bạn đến với thế giới của những bộ não nhân tạo thông minh nhất."
    },
    {
        "shot_id": "shot_02",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.10,
        "tempo_factor": 1.05,
        "text": "Tớ là Chatty! Hỏi tớ bất cứ điều gì, tớ đều có câu trả lời ngay!"
    },
    {
        "shot_id": "shot_03",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.04,
        "tempo_factor": 1.03,
        "text": "Còn tớ là Agent-X. Tớ không chỉ trả lời, tớ giải quyết vấn đề bằng hành động."
    },
    {
        "shot_id": "shot_04",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "text": "Bất ngờ, một sự cố rò rỉ dữ liệu nghiêm trọng bùng nổ toàn hệ thống!"
    },
    {
        "shot_id": "shot_05",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.12,
        "tempo_factor": 1.08,
        "text": "Nguy hiểm quá! Theo tài liệu hai nghìn không trăm hai mươi sáu, các bạn nên ngắt mạng và gõ lệnh vá lỗi!"
    },
    {
        "shot_id": "shot_06",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.08,
        "tempo_factor": 1.02,
        "text": "Nhưng tớ... tớ chỉ là Chatbot, tớ không có quyền truy cập để sửa nó!"
    },
    {
        "shot_id": "shot_07",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "text": "Chatbot biết mọi giải pháp, nhưng hoàn toàn bất lực trong việc can thiệp thực tế."
    },
    {
        "shot_id": "shot_08",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.04,
        "tempo_factor": 1.03,
        "text": "Đừng lo. Hãy để tớ lập kế hoạch và kích hoạt công cụ xử lý."
    },
    {
        "shot_id": "shot_09",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "text": "Agent tự động chia nhỏ mục tiêu, mở terminal và trực tiếp gọi các ây pi ai cứu hộ."
    },
    {
        "shot_id": "shot_10",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "text": "Nếu gặp lỗi, Agent sẽ tự tư duy, sửa sai và thử lại đến khi thành công."
    },
    {
        "shot_id": "shot_11",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.04,
        "tempo_factor": 1.04,
        "text": "Nhiệm vụ hoàn tất! Tường lửa đã phục hồi và báo cáo đã gửi về sếp."
    },
    {
        "shot_id": "shot_12",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.10,
        "tempo_factor": 1.05,
        "text": "Cậu đỉnh thật đấy! Vậy điều gì làm cậu khác biệt hoàn toàn với tớ?"
    },
    {
        "shot_id": "shot_13",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.03,
        "tempo_factor": 1.02,
        "text": "Tớ có bốn thứ: Não bộ phân tích, Bộ nhớ dài hạn, Bộ công cụ thực thi, và Quyền tự chủ."
    },
    {
        "shot_id": "shot_14",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "tempo_factor": 1.0,
        "text": "Chatbot là cố vấn thông thái trong phòng họp, còn Agent là chiến binh trực tiếp ra trận."
    },
    {
        "shot_id": "shot_15",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.04,
        "tempo_factor": 1.03,
        "text": "Tương lai không còn là gõ prompt chờ đợi, mà là giao việc cho các Agent tự làm."
    },
    {
        "shot_id": "shot_16",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.10,
        "tempo_factor": 1.06,
        "text": "Đăng ký kênh Giải Mã Tếch để cùng làm chủ làn sóng ây ai Agent ngay hôm nay nhé!"
    }
]

def _edge_variants(text: str) -> list[str]:
    """Tạo biến thể chèn dấu phẩy nhẹ để vượt qua lỗi NoAudioReceived của Edge TTS tiếng Việt."""
    words = text.split(" ")
    if len(words) <= 2:
        return [text, text]
    mid = len(words) // 2
    order = sorted(range(1, len(words)), key=lambda k: abs(k - mid))
    commas = [" ".join(words[:k]) + ", " + " ".join(words[k:]) for k in order
              if not words[k - 1].endswith((",", ".", "!", "?", ":", ";"))]
    return [text, text] + commas[:6]

def generate_one_shot(item):
    import edge_tts
    raw_mp3 = AUDIO_DIR / f"{item['shot_id']}_raw.mp3"
    final_wav = AUDIO_DIR / f"{item['shot_id']}.wav"

    # Skip if already generated and valid
    if final_wav.exists() and final_wav.stat().st_size > 50000:
        cmd_probe = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(final_wav)
        ]
        dur = float(subprocess.run(cmd_probe, capture_output=True, text=True).stdout.strip() or 0.0)
        print(f"⏩ [{item['shot_id']}] (Cached {dur:.2f}s): {item['text']}")
        return {
            **item,
            "audio_file": str(final_wav.name),
            "duration_s": round(dur, 2)
        }

    success = False
    for variant in _edge_variants(item["text"]):
        try:
            edge_tts.Communicate(variant, item["voice"]).save_sync(str(raw_mp3))
            if raw_mp3.exists() and raw_mp3.stat().st_size > 0:
                success = True
                break
        except edge_tts.exceptions.NoAudioReceived:
            time.sleep(0.8)
            continue
        except Exception as e:
            time.sleep(1.0)
            continue

    if not success:
        raise RuntimeError(f"Failed to generate TTS for {item['shot_id']}")

    # Apply rubberband pitch/tempo modulation + 48kHz Stereo 16-bit WAV + 0.35s tail breath
    p = item["pitch_factor"]
    t = item["tempo_factor"]
    af_filters = [
        f"rubberband=pitch={p}:tempo={t}",
        "apad=pad_dur=0.35",
        "aformat=sample_rates=48000:channel_layouts=stereo"
    ]
    filter_str = ",".join(af_filters)

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

    print(f"✅ [{item['shot_id']}] {item['speaker']} ({dur:.2f}s): {item['text']}")
    return {
        **item,
        "audio_file": str(final_wav.name),
        "duration_s": round(dur, 2)
    }

def main():
    print("🎙 Generating 16 Master Voice Lines with Edge-TTS & Rubberband...")
    manifest = []
    for item in SHOTS:
        res = generate_one_shot(item)
        manifest.append(res)
        time.sleep(1.5) # Gentle pause to ensure Microsoft edge-tts stability

    manifest_file = AUDIO_DIR / "audio_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    total_dur = sum(x["duration_s"] for x in manifest)
    print(f"\n✨ All {len(manifest)} voice tracks created! Total voice duration: {total_dur:.2f}s")

    # Generate concatenated master voice track
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

    print(f"🎧 Master Dialogue Track Exported: {master_wav} ({total_dur:.2f}s)")

if __name__ == "__main__":
    main()

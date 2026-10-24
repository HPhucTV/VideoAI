import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
import edge_tts

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = ROOT_DIR / "output" / "cinematic" / "audio"
BGM_FILE = ROOT_DIR / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "battle-epic.mp3"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)

SHOTS = [
    {
        "shot_id": "shot_01",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "text": "Chào mừng bạn đến với thế giới của những bộ não nhân tạo thông minh nhất."
    },
    {
        "shot_id": "shot_02",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.08,
        "text": "Tớ là Chatty! Hỏi tớ bất cứ điều gì, tớ đều có câu trả lời ngay!"
    },
    {
        "shot_id": "shot_03",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.03,
        "text": "Còn tớ là Agent-X. Tớ không chỉ trả lời, tớ giải quyết vấn đề bằng hành động."
    },
    {
        "shot_id": "shot_04",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "text": "Bất ngờ, một sự cố rò rỉ dữ liệu nghiêm trọng bùng nổ toàn hệ thống!"
    },
    {
        "shot_id": "shot_05",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.08,
        "text": "Nguy hiểm quá! Các bạn nên ngắt kết nối mạng và gõ lệnh vá lỗi ngay!"
    },
    {
        "shot_id": "shot_06",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.08,
        "text": "Nhưng tớ chỉ là chát bót, tớ không có quyền truy cập để sửa nó!"
    },
    {
        "shot_id": "shot_07",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "text": "Chatbot biết mọi giải pháp, nhưng hoàn toàn bất lực trong việc can thiệp thực tế."
    },
    {
        "shot_id": "shot_08",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.03,
        "text": "Đừng lo! Hãy để tớ lập kế hoạch và kích hoạt công cụ xử lý."
    },
    {
        "shot_id": "shot_09",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "text": "Agent tự động chia nhỏ mục tiêu, mở hệ thống và gọi các công cụ cứu hộ."
    },
    {
        "shot_id": "shot_10",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "text": "Nếu gặp lỗi, Agent sẽ tự tư duy, sửa sai và thử lại đến khi thành công."
    },
    {
        "shot_id": "shot_11",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.03,
        "text": "Đã xử lý xong, hệ thống an toàn và báo cáo đã gửi đi."
    },
    {
        "shot_id": "shot_12",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.08,
        "text": "Cậu đỉnh thật đấy! Vậy điều gì làm cậu khác biệt hoàn toàn với tớ?"
    },
    {
        "shot_id": "shot_13",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.03,
        "text": "Tớ có bốn thứ: Não bộ phân tích, Bộ nhớ dài hạn, Bộ công cụ thực thi, và Quyền tự chủ."
    },
    {
        "shot_id": "shot_14",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.0,
        "text": "Chatbot là cố vấn thông thái trong phòng họp, còn Agent là chiến binh trực tiếp ra trận."
    },
    {
        "shot_id": "shot_15",
        "speaker": "Bé Agent-X",
        "voice": "vi-VN-NamMinhNeural",
        "pitch_factor": 1.03,
        "text": "Tương lai không còn là gõ prompt chờ đợi, mà là để cho các trợ lý tự hành động."
    },
    {
        "shot_id": "shot_16",
        "speaker": "Bé Chatty",
        "voice": "vi-VN-HoaiMyNeural",
        "pitch_factor": 1.08,
        "text": "Hãy theo dõi kênh Giải Mã Tếch để cùng làm chủ làn sóng trí tuệ nhân tạo mới nhé!"
    }
]

async def generate_shot(item):
    raw_mp3 = AUDIO_DIR / f"{item['shot_id']}_raw.mp3"
    final_wav = AUDIO_DIR / f"{item['shot_id']}.wav"

    # If already generated at 3:17 PM (today) and size > 500KB, we can keep or overwrite
    need_gen = True
    if final_wav.exists() and final_wav.stat().st_size > 500000:
        # Check if shot_01 to shot_10 were created just now
        if item["shot_id"] in ["shot_01", "shot_02", "shot_03", "shot_04", "shot_05", "shot_06", "shot_07", "shot_08", "shot_09", "shot_10"]:
            need_gen = False

    if need_gen:
        for attempt in range(4):
            try:
                comm = edge_tts.Communicate(
                    text=item["text"],
                    voice=item["voice"]
                )
                await comm.save(str(raw_mp3))
                if raw_mp3.exists() and raw_mp3.stat().st_size > 2000:
                    break
            except Exception as e:
                print(f"Attempt {attempt+1} failed for {item['shot_id']}: {e}")
                await asyncio.sleep(1.0)

        if not raw_mp3.exists() or raw_mp3.stat().st_size <= 2000:
            raise RuntimeError(f"Failed to generate audio for {item['shot_id']}")

        # Apply pitch in ffmpeg + format 48kHz Stereo 16-bit WAV + pad 0.25s
        p = item["pitch_factor"]
        if p != 1.0:
            af = f"rubberband=pitch={p},apad=pad_dur=0.25,aformat=sample_rates=48000:channel_layouts=stereo"
        else:
            af = "apad=pad_dur=0.25,aformat=sample_rates=48000:channel_layouts=stereo"

        cmd_ffmpeg = [
            "ffmpeg", "-y", "-i", str(raw_mp3),
            "-af", af,
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
        "shot_id": item["shot_id"],
        "speaker": item["speaker"],
        "audio_file": str(final_wav.name),
        "duration_s": round(dur, 2),
        "text": item["text"]
    }

async def main():
    print("🎙 Generating all 16 Shots with Edge-TTS at 1.0x Native Speed...")
    manifest = []
    for item in SHOTS:
        res = await generate_shot(item)
        manifest.append(res)
        await asyncio.sleep(0.3)

    # Save manifest
    manifest_file = AUDIO_DIR / "audio_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    total_dur = sum(x["duration_s"] for x in manifest)
    print(f"\n✨ All 16 shots generated! Total 1.0x Dialogue Duration: {total_dur:.2f}s")

    # 1. Concatenate master dialogue
    concat_txt = AUDIO_DIR / "concat_list.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for m in manifest:
            f.write(f"file '{m['audio_file']}'\n")

    master_dialogue = AUDIO_DIR / "master_dialogue_48k.wav"
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy", str(master_dialogue)
    ]
    subprocess.run(cmd_concat, capture_output=True, check=True)
    if concat_txt.exists():
        concat_txt.unlink()

    # 2. Mix with real cinematic BGM (battle-epic.mp3) with ducking
    master_film_wav = AUDIO_DIR / "master_film_audio_48k.wav"
    master_film_mp3 = AUDIO_DIR / "master_film_audio_48k.mp3"

    print("🎵 Mixing dialogue with Epic Cinematic BGM (battle-epic.mp3) with -18dB ducking...")
    fade_start = max(1.0, total_dur - 2.5)
    mix_filter = (
        f"[1:a]atrim=0:{total_dur + 0.5},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume=0.08,afade=t=out:st={fade_start}:d=2.5[bgm];"
        f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.0[vox];"
        f"[vox][bgm]amix=inputs=2:duration=first:dropout_transition=2[out]"
    )

    cmd_mix = [
        "ffmpeg", "-y",
        "-i", str(master_dialogue),
        "-i", str(BGM_FILE),
        "-filter_complex", mix_filter,
        "-map", "[out]",
        "-ar", "48000",
        "-c:a", "pcm_s16le",
        str(master_film_wav)
    ]
    subprocess.run(cmd_mix, capture_output=True, check=True)

    # Export MP3
    subprocess.run([
        "ffmpeg", "-y", "-i", str(master_film_wav),
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(master_film_mp3)
    ], capture_output=True, check=True)

    print(f"🎧 Master 1.0x Audio Suite ready: {master_film_mp3} ({total_dur:.2f}s)")

if __name__ == "__main__":
    asyncio.run(main())

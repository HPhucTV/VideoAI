import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import asyncio
import json
import os
import re
import subprocess
import time
import unicodedata
from pathlib import Path
import edge_tts

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min"
AUDIO_DIR = OUTPUT_DIR / "audio"
SHOTS_AUDIO_DIR = AUDIO_DIR / "shots"
SPEC_PATH = OUTPUT_DIR / "STORYBOARD_SPEC_104_SHOTS.md"

def resample_48k_stereo(src: Path, dst: Path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-ar", "48000",
        "-ac", "2",
        "-b:a", "192k",
        str(dst)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def get_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return round(float(res.stdout.strip()), 2)

PHONETIC_REPLACEMENTS = {
    "vector memory": "bộ nhớ véc-tơ",
    "vector": "véc-tơ",
    "kỷ nguyên": "thời đại",
    "ai agent": "trí tuệ nhân tạo Agent",
}

def clean_dialogue(text: str) -> str:
    cleaned = text
    for k, v in PHONETIC_REPLACEMENTS.items():
        pattern = re.compile(re.escape(k), re.IGNORECASE)
        cleaned = pattern.sub(v, cleaned)
    return unicodedata.normalize("NFC", cleaned.strip())

async def patch_shot(shot_num: int, original_dialogue: str):
    dst_file = SHOTS_AUDIO_DIR / f"shot_{shot_num:03d}.mp3"
    if dst_file.exists() and dst_file.stat().st_size > 2000:
        return True

    text_to_speak = clean_dialogue(original_dialogue)
    temp_file = SHOTS_AUDIO_DIR / f"patch_temp_{shot_num:03d}.mp3"

    for voice in ["vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural"]:
        for attempt in range(1, 4):
            try:
                comm = edge_tts.Communicate(text_to_speak, voice)
                await comm.save(str(temp_file))
                if temp_file.exists() and temp_file.stat().st_size > 500:
                    resample_48k_stereo(temp_file, dst_file)
                    temp_file.unlink(missing_ok=True)
                    dur = get_duration(dst_file)
                    print(f"  ✅ [ĐÃ VÁ SHOT {shot_num:03d}] {voice}: {dur:.2f}s | {text_to_speak[:35]}...", flush=True)
                    return True
            except Exception as e:
                await asyncio.sleep(1.0 * attempt)

    print(f"  ❌ [THẤT BẠI VÁ SHOT {shot_num:03d}]", flush=True)
    return False

async def main():
    print("=" * 65)
    print("🔧 KIỂM TRA VÀ VÁ CÁC SHOT AUDIO CHƯA HOÀN TẤT CHO CỔNG 4")
    print("=" * 65)

    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    shots_dict = {}
    for line in lines:
        m = re.search(r'\*\s*\*\*Shot\s+(\d+)\s*\((.*?)\)\s*\[(.*?)\]:\*\*\s*(.*?)\s*\*\(Thoại:\s*\"(.*?)\"\)\*', line)
        if m:
            s_num = int(m.group(1))
            shots_dict[s_num] = m.group(5).strip()

    missing = []
    for i in range(1, 105):
        f = SHOTS_AUDIO_DIR / f"shot_{i:03d}.mp3"
        if not f.exists() or f.stat().st_size < 2000:
            missing.append(i)

    print(f"📋 Các shot cần kiểm tra/vá: {missing}")

    for s_num in missing:
        dialogue = shots_dict.get(s_num, "")
        if dialogue:
            await patch_shot(s_num, dialogue)
            await asyncio.sleep(0.5)

    # Re-verify
    final_missing = []
    total_sec = 0.0
    all_shots_info = []
    for i in range(1, 105):
        f = SHOTS_AUDIO_DIR / f"shot_{i:03d}.mp3"
        if f.exists() and f.stat().st_size > 2000:
            d = get_duration(f)
            total_sec += d
            all_shots_info.append({
                "shot": i,
                "file": str(f.relative_to(BASE_DIR)).replace("\\", "/"),
                "duration": d,
                "dialogue": shots_dict.get(i, "")
            })
        else:
            final_missing.append(i)

    print("\n" + "=" * 65)
    print(f"🎉 TỔNG KẾT BỘ MASTER AUDIO 104 SHOTS:")
    print(f"  • Đã hoàn thành: {len(all_shots_info)} / 104 shots")
    print(f"  • Thiếu: {len(final_missing)} shots: {final_missing}")
    print(f"  • Tổng thời lượng Master Audio: {total_sec:.2f}s (~{total_sec/60:.2f} phút)")
    print("=" * 65)

    manifest_file = AUDIO_DIR / "audio_manifest_104_shots.json"
    manifest_data = {
        "channel": "Giải Mã Tech",
        "job_id": "job-ai-agent-giaimatech-10min",
        "format": "1920x1080 @ 60fps",
        "audio_standard": "48,000 Hz, Stereo 2 Channels, 192kbps AAC",
        "bgm_ducking": "-18dB",
        "total_shots": len(all_shots_info),
        "total_audio_duration_seconds": round(total_sec, 2),
        "shots": all_shots_info
    }
    manifest_file.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📁 Manifest hoàn thiện: {manifest_file}")

if __name__ == "__main__":
    asyncio.run(main())

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
SHOTS_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

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

async def synthesize_shot(shot_info: dict, sem: asyncio.Semaphore) -> dict:
    shot_id = shot_info["shot"]
    dialogue = shot_info["dialogue"]
    out_file = SHOTS_AUDIO_DIR / f"shot_{shot_id:03d}.mp3"

    if out_file.exists() and out_file.stat().st_size > 4000:
        dur = get_duration(out_file)
        return {
            "shot": shot_id,
            "file": str(out_file.relative_to(BASE_DIR)).replace("\\", "/"),
            "duration": dur,
            "dialogue": dialogue,
            "status": "cached"
        }

    clean_text = unicodedata.normalize("NFC", dialogue)
    temp_file = SHOTS_AUDIO_DIR / f"temp_shot_{shot_id:03d}.mp3"

    async with sem:
        for attempt in range(1, 6):
            try:
                comm = edge_tts.Communicate(clean_text, "vi-VN-NamMinhNeural", rate="+2%")
                await comm.save(str(temp_file))
                if temp_file.exists() and temp_file.stat().st_size > 500:
                    resample_48k_stereo(temp_file, out_file)
                    temp_file.unlink(missing_ok=True)
                    dur = get_duration(out_file)
                    print(f"  [SHOT {shot_id:03d}/104] Thành công: {dur:.2f}s | {dialogue[:30]}...")
                    return {
                        "shot": shot_id,
                        "file": str(out_file.relative_to(BASE_DIR)).replace("\\", "/"),
                        "duration": dur,
                        "dialogue": dialogue,
                        "status": "success"
                    }
            except Exception as e:
                # Exponential backoff
                wait_sec = 2.0 * attempt
                print(f"  [SHOT {shot_id:03d}] Lỗi lần {attempt}: {e}. Đợi {wait_sec:.1f}s...")
                await asyncio.sleep(wait_sec)

        # Fallback if failed
        print(f"  ❌ [SHOT {shot_id:03d}] Thất bại sau 5 lần thử: {dialogue}")
        return {
            "shot": shot_id,
            "file": None,
            "duration": 5.0,
            "dialogue": dialogue,
            "status": "failed"
        }

async def main():
    print("=" * 70)
    print("🎙️ CỔNG 4: TỔNG HỢP MASTER AUDIO 48KHZ STEREO CHO TOÀN BỘ 104 SHOTS")
    print("=" * 70)

    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    shots_data = []
    current_chapter = "Chương 1"
    for line in lines:
        if line.startswith("#### Chương"):
            current_chapter = line.replace("####", "").strip()
        m = re.search(r'\*\s*\*\*Shot\s+(\d+)\s*\((.*?)\)\s*\[(.*?)\]:\*\*\s*(.*?)\s*\*\(Thoại:\s*\"(.*?)\"\)\*', line)
        if m:
            shots_data.append({
                "shot": int(m.group(1)),
                "time_spec": m.group(2).strip(),
                "shot_type": m.group(3).strip(),
                "action": m.group(4).strip(),
                "dialogue": m.group(5).strip(),
                "chapter": current_chapter
            })

    print(f"📋 Đã tải {len(shots_data)} shots từ bản thiết kế phân cảnh.")

    # Concurrency semaphore to avoid spamming edge_tts websocket
    sem = asyncio.Semaphore(3)

    tasks = [synthesize_shot(s, sem) for s in shots_data]
    results = await asyncio.gather(*tasks)

    # Sort results
    results.sort(key=lambda x: x["shot"])

    # Calculate total duration
    total_audio_sec = sum(r["duration"] for r in results if r["duration"])
    success_count = sum(1 for r in results if r["status"] in ["success", "cached"])

    print("\n" + "=" * 70)
    print(f"🎉 KẾT QUẢ TỔNG HỢP AUDIO 104 SHOTS:")
    print(f"  • Hoàn thành: {success_count} / {len(shots_data)} shots")
    print(f"  • Tổng thời lượng lời thoại thực tế: {total_audio_sec:.2f} giây (~{total_audio_sec/60:.2f} phút)")
    print("=" * 70)

    # Write manifest for 104 shots
    manifest = {
        "channel": "Giải Mã Tech",
        "job_id": "job-ai-agent-giaimatech-10min",
        "format": "1920x1080 @ 60fps",
        "audio_standard": "48,000 Hz, Stereo 2 Channels, 192kbps AAC",
        "bgm_ducking": "-18dB",
        "total_shots": len(results),
        "total_audio_duration_seconds": round(total_audio_sec, 2),
        "shots": results
    }

    manifest_file = AUDIO_DIR / "audio_manifest_104_shots.json"
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📁 Đã lưu Audio Manifest: {manifest_file}")

if __name__ == "__main__":
    asyncio.run(main())

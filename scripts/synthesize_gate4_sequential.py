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

async def synthesize_one(shot_id: int, dialogue: str) -> dict:
    out_file = SHOTS_AUDIO_DIR / f"shot_{shot_id:03d}.mp3"
    if out_file.exists() and out_file.stat().st_size > 2000:
        dur = get_duration(out_file)
        print(f"  [CACHE] Shot {shot_id:03d}/104: {dur:.2f}s | {dialogue[:35]}...", flush=True)
        return {
            "shot": shot_id,
            "file": str(out_file.relative_to(BASE_DIR)).replace("\\", "/"),
            "duration": dur,
            "dialogue": dialogue,
            "status": "cached"
        }

    clean_text = unicodedata.normalize("NFC", dialogue.strip())
    temp_file = SHOTS_AUDIO_DIR / f"temp_{shot_id:03d}.mp3"

    # Voices to try in order of preference
    voices_to_try = ["vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural"]

    for voice in voices_to_try:
        for attempt in range(1, 4):
            try:
                comm = edge_tts.Communicate(clean_text, voice, rate="+2%")
                await comm.save(str(temp_file))
                if temp_file.exists() and temp_file.stat().st_size > 500:
                    resample_48k_stereo(temp_file, out_file)
                    temp_file.unlink(missing_ok=True)
                    dur = get_duration(out_file)
                    v_label = "NamMinh" if "NamMinh" in voice else "HoaiMy(FB)"
                    print(f"  [OK] Shot {shot_id:03d}/104 [{v_label}]: {dur:.2f}s | {dialogue[:35]}...", flush=True)
                    return {
                        "shot": shot_id,
                        "file": str(out_file.relative_to(BASE_DIR)).replace("\\", "/"),
                        "duration": dur,
                        "dialogue": dialogue,
                        "voice": voice,
                        "status": "success"
                    }
            except Exception as e:
                wait = 1.0 * attempt
                await asyncio.sleep(wait)

    print(f"  [FAIL] Shot {shot_id:03d} thất bại: {dialogue}", flush=True)
    return {
        "shot": shot_id,
        "file": None,
        "duration": 5.0,
        "dialogue": dialogue,
        "status": "failed"
    }

async def main():
    print("=" * 70, flush=True)
    print("🎙️ CỔNG 4: TỔNG HỢP MASTER AUDIO 48KHZ CHO TOÀN BỘ 104 SHOTS", flush=True)
    print("=" * 70, flush=True)

    # Clean any lingering temp files
    for tmp in SHOTS_AUDIO_DIR.glob("temp_*.mp3"):
        try:
            tmp.unlink()
        except Exception:
            pass

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

    print(f"📋 Bắt đầu tổng hợp {len(shots_data)} shots...", flush=True)

    results = []
    for s in shots_data:
        r = await synthesize_one(s["shot"], s["dialogue"])
        r["time_spec"] = s["time_spec"]
        r["shot_type"] = s["shot_type"]
        r["chapter"] = s["chapter"]
        results.append(r)
        await asyncio.sleep(0.3)

    total_duration = sum(r["duration"] for r in results if r["duration"])
    success_count = sum(1 for r in results if r["status"] in ["success", "cached"])

    print("\n" + "=" * 70, flush=True)
    print(f"🎉 CỔNG 4 HOÀN TẤT XUẤT SẮC:", flush=True)
    print(f"  • Tổng số shot audio: {success_count}/{len(shots_data)}", flush=True)
    print(f"  • Tổng thời lượng Master Audio: {total_duration:.2f}s (~{total_duration/60:.2f} phút)", flush=True)
    print("=" * 70, flush=True)

    manifest_file = AUDIO_DIR / "audio_manifest_104_shots.json"
    manifest_data = {
        "channel": "Giải Mã Tech",
        "job_id": "job-ai-agent-giaimatech-10min",
        "format": "1920x1080 @ 60fps",
        "audio_standard": "48,000 Hz, Stereo 2 Channels, 192kbps AAC",
        "bgm_ducking": "-18dB",
        "total_shots": len(results),
        "total_audio_duration_seconds": round(total_duration, 2),
        "shots": results
    }
    manifest_file.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📁 Manifest đã ghi nhận: {manifest_file}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())

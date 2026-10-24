import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import asyncio
import json
import subprocess
import unicodedata
from pathlib import Path
import edge_tts

BASE_DIR = Path(__file__).resolve().parent.parent
JOB_FILE = BASE_DIR / "output" / "jobs" / "job-ai-agent-giaimatech-10min.json"
AUDIO_DIR = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

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

async def main():
    job_data = json.loads(JOB_FILE.read_text(encoding="utf-8"))
    beats = job_data.get("beats", [])

    print("=" * 65)
    print("🎙️ CỔNG 4: TỔNG HỢP MASTER AUDIO 48KHZ STEREO (EDGE-TTS VI-VN)")
    print(f"📋 Tổng số phân cảnh cần tổng hợp: {len(beats)}")
    print("=" * 65)

    manifest_tracks = []
    total_duration = 0.0

    for b in beats:
        order = b["order"]
        beat_id = b["id"]
        raw_text = b["rawText"]
        speaker = b.get("speaker", "Người Kể Chuyện")

        # Chuẩn hóa Unicode NFC tuyệt đối
        clean_text = unicodedata.normalize("NFC", raw_text)

        temp_file = AUDIO_DIR / f"temp_{order:02d}.mp3"
        final_file = AUDIO_DIR / f"scene_{order:02d}.mp3"

        print(f"\n[{order:02d}/{len(beats):02d}] ({speaker}): {clean_text[:45]}...")
        comm = edge_tts.Communicate(clean_text, "vi-VN-NamMinhNeural", rate="+2%")
        await comm.save(str(temp_file))

        # Resample sang 48kHz Stereo 192kbps
        resample_48k_stereo(temp_file, final_file)
        temp_file.unlink(missing_ok=True)

        dur = get_duration(final_file)
        total_duration += dur

        print(f"   => ĐÃ TẠO XONG: {final_file.name} | Thời lượng: {dur:.2f}s (48kHz Stereo)")
        manifest_tracks.append({
            "order": order,
            "beat_id": beat_id,
            "speaker": speaker,
            "text": clean_text,
            "file": str(final_file.relative_to(BASE_DIR)).replace("\\", "/"),
            "duration_s": dur
        })
        await asyncio.sleep(0.5)

    manifest_file = AUDIO_DIR / "audio_manifest.json"
    manifest_data = {
        "channel": "Giải Mã Tech",
        "job_id": "job-ai-agent-giaimatech-10min",
        "format": "1920x1080 @ 60fps",
        "audio_standard": "48,000 Hz, Stereo 2 Channels, 192kbps AAC/MP3",
        "total_tracks": len(manifest_tracks),
        "total_audio_duration_seconds": round(total_duration, 2),
        "tracks": manifest_tracks
    }
    manifest_file.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 65)
    print(f"🎉 CỔNG 4 HOÀN THÀNH 100%: Đã tạo xong {len(manifest_tracks)} tracks âm thanh!")
    print(f"⏱️ Tổng thời lượng: {total_duration:.2f}s (~{total_duration/60:.1f} phút)")
    print(f"📁 Manifest: {manifest_file}")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(main())

"""
Accelerate all 16 Shots to 1.25x speed while preserving pitch using FFmpeg Rubberband
Regenerates master dialogue, re-mixes BGM, and updates manifest.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = ROOT_DIR / "output" / "cinematic" / "audio"
ARTIFACT_DIR = Path(r"C:\Users\tranh\.gemini\antigravity\brain\e4e95502-3da3-4c54-80ff-c7025c522886")

SPEED_FACTOR = 1.25

def main():
    manifest_path = AUDIO_DIR / "audio_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print(f"🚀 Speeding up all 16 shots to {SPEED_FACTOR}x speed...")
    updated_manifest = []

    for item in manifest:
        shot_id = item["shot_id"]
        current_wav = AUDIO_DIR / item["audio_file"]
        temp_wav = AUDIO_DIR / f"{shot_id}_speed.wav"

        # Apply rubberband tempo=1.25 with 0.25s padding
        cmd_filter = f"rubberband=tempo={SPEED_FACTOR},apad=pad_dur=0.25,aformat=sample_rates=48000:channel_layouts=stereo"
        cmd = [
            "ffmpeg", "-y", "-i", str(current_wav),
            "-af", cmd_filter,
            "-c:a", "pcm_s16le", str(temp_wav)
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        # Replace original with accelerated version
        temp_wav.replace(current_wav)

        # Probe new duration
        cmd_probe = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(current_wav)
        ]
        new_dur = float(subprocess.run(cmd_probe, capture_output=True, text=True).stdout.strip() or 0.0)

        print(f"⚡ [{shot_id}] {item['speaker']}: {item['duration_s']}s -> {new_dur:.2f}s ({SPEED_FACTOR}x)")
        item["duration_s"] = round(new_dur, 2)
        updated_manifest.append(item)

    # Save updated manifest
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(updated_manifest, f, ensure_ascii=False, indent=2)

    total_dur = sum(x["duration_s"] for x in updated_manifest)
    print(f"\n✨ All 16 shots accelerated! New total duration: {total_dur:.2f}s")

    # 1. Re-concatenate master dialogue track
    concat_txt = AUDIO_DIR / "concat_list.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for m in updated_manifest:
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

    # 2. Generate matched duration BGM (total_dur + 2s)
    bgm_wav = AUDIO_DIR / "bgm_cyber.wav"
    bgm_cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=f=130.81:d={total_dur + 3},volume=0.08",
        "-f", "lavfi", "-i", f"sine=f=196.00:d={total_dur + 3},volume=0.06",
        "-f", "lavfi", "-i", f"anoisesrc=d={total_dur + 3}:c=pink,lowpass=f=400,volume=0.04",
        "-filter_complex", "[0:a][1:a][2:a]amix=inputs=3,aformat=channel_layouts=stereo,volume=0.15[bgm]",
        "-map", "[bgm]", str(bgm_wav)
    ]
    subprocess.run(bgm_cmd, capture_output=True, check=True)

    # 3. Mix master film audio with ducking
    master_film_wav = AUDIO_DIR / "master_film_audio_48k.wav"
    master_film_mp3 = AUDIO_DIR / "master_film_audio_48k.mp3"
    mix_cmd = [
        "ffmpeg", "-y",
        "-i", str(master_dialogue),
        "-i", str(bgm_wav),
        "-filter_complex", "[0:a]volume=1.0[v];[1:a]volume=0.22[b];[v][b]amix=inputs=2:duration=first:dropout_transition=0,aformat=sample_rates=48000:channel_layouts=stereo[out]",
        "-map", "[out]",
        "-c:a", "pcm_s16le", str(master_film_wav)
    ]
    subprocess.run(mix_cmd, capture_output=True, check=True)

    # Convert to MP3
    mp3_cmd = [
        "ffmpeg", "-y", "-i", str(master_film_wav),
        "-c:a", "libmp3lame", "-b:a", "192k", str(master_film_mp3)
    ]
    subprocess.run(mp3_cmd, capture_output=True, check=True)

    # Copy to artifact dir for preview
    import shutil
    shutil.copy(master_film_mp3, ARTIFACT_DIR / "master_film_audio_48k.mp3")

    print(f"🎉 Master Audio 1.25x completed! Length: {total_dur:.2f}s (~{int(total_dur // 60)}m{int(total_dur % 60):02d}s)")

if __name__ == "__main__":
    main()

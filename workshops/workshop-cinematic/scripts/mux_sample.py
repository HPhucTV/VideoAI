#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

base_dir = Path("output/cinematic/job-xianxia-cinematic-sample")
vid1 = base_dir / "videos" / "scene-01-raw.mp4"
vid2 = base_dir / "videos" / "scene-02-raw.mp4"
aud1 = base_dir / "audio" / "scene-01.mp3"
aud2 = base_dir / "audio" / "scene-02.mp3"
bgm = Path("workshops/workshop-whiteboard/assets/audio/bgm/xianxia-ambient.mp3")

out1 = base_dir / "scene-01-final.mp4"
out2 = base_dir / "scene-02-final.mp4"
master = Path("output/cinematic/job-xianxia-cinematic-sample.mp4")

print("[1/4] Muxing Scene 1 (Voice + BGM + Veo 2 Video)...")
cmd1 = [
    "ffmpeg", "-y",
    "-i", str(vid1),
    "-i", str(aud1),
    "-i", str(bgm),
    "-filter_complex",
    "[1:a]volume=1.3[v1];[2:a]volume=0.25[bgm1];[v1][bgm1]amix=inputs=2:duration=first:dropout_transition=2[aout1]",
    "-map", "0:v",
    "-map", "[aout1]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k",
    "-t", "8",
    str(out1)
]
subprocess.run(cmd1, check=True)
print("  -> Created:", out1)

print("[2/4] Muxing Scene 2 (Voice + BGM + Veo 2 Video)...")
cmd2 = [
    "ffmpeg", "-y",
    "-i", str(vid2),
    "-i", str(aud2),
    "-i", str(bgm),
    "-filter_complex",
    "[1:a]volume=1.3[v2];[2:a]volume=0.25[bgm2];[v2][bgm2]amix=inputs=2:duration=first:dropout_transition=2[aout2]",
    "-map", "0:v",
    "-map", "[aout2]",
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k",
    "-t", "8",
    str(out2)
]
subprocess.run(cmd2, check=True)
print("  -> Created:", out2)

print("[3/4] Concatenating Scenes into Master Film...")
concat_list = base_dir / "concat.txt"
with open(concat_list, "w", encoding="utf-8") as f:
    f.write(f"file '{out1.resolve().as_posix()}'\n")
    f.write(f"file '{out2.resolve().as_posix()}'\n")

cmd_concat = [
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_list),
    "-c", "copy",
    str(master)
]
subprocess.run(cmd_concat, check=True)
print("  -> Master Film created:", master)

print("[4/4] Creating Thumbnail...")
thumb = Path("output/cinematic/job-xianxia-cinematic-sample-thumb.png")
cmd_thumb = [
    "ffmpeg", "-y",
    "-ss", "00:00:01",
    "-i", str(master),
    "-vframes", "1",
    str(thumb)
]
subprocess.run(cmd_thumb, check=True)
print("  -> Thumbnail created:", thumb)
print("\n🎬 ALL DONE! Master Film ready at:", master)

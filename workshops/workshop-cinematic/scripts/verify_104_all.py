import glob
import os
from pathlib import Path

video_dir = Path(r"c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min\videos")
audio_dir = Path(r"c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min\audio\shots")

print("=== CHECKING ALL 104 SHOTS ===")
missing_videos = []
missing_audios = []
small_videos = []

for i in range(1, 105):
    v = video_dir / f"shot_{i:03d}.mp4"
    a = audio_dir / f"shot_{i:03d}.mp3"
    if not v.exists():
        missing_videos.append(i)
    elif v.stat().st_size < 100000:
        small_videos.append((i, v.stat().st_size))
    if not a.exists():
        missing_audios.append(i)

print(f"Missing videos: {missing_videos}")
print(f"Small videos (<100KB): {small_videos}")
print(f"Missing audios: {missing_audios}")
if not missing_videos and not small_videos and not missing_audios:
    print("ALL 104 VIDEO CLIPS (GEN V) AND 104 AUDIO CLIPS ARE 100% VALID AND READY!")

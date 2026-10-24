import subprocess
from pathlib import Path

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
vid_path = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "videos" / "shot_001.mp4"
audio_path = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "audio" / "shots" / "shot_001.mp3"
test_out = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "test_fix_shot1.mp4"

def get_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())

v_dur = get_dur(vid_path)
a_dur = get_dur(audio_path)
print(f"Video dur: {v_dur:.3f}s | Audio dur: {a_dur:.3f}s")

# Retime video smoothly to exactly match audio duration:
# setpts = (a_dur / v_dur) * PTS
# fps = 30
vf = f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setpts=({a_dur:.4f}/{v_dur:.4f})*PTS,fps=30"

cmd = [
    "ffmpeg", "-y",
    "-i", str(vid_path),
    "-i", str(audio_path),
    "-vf", vf,
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-t", f"{a_dur:.3f}",
    "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
    str(test_out)
]
subprocess.run(cmd, check=True)
print("Rendered test segment:", test_out)

# Check volume of test_out
r = subprocess.run(["ffmpeg", "-y", "-i", str(test_out), "-af", "volumedetect", "-f", "null", "NUL"], capture_output=True, text=True)
for line in r.stderr.splitlines():
    if "mean_volume" in line or "max_volume" in line:
        print("  Volume:", line.strip())

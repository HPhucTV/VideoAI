import subprocess
from pathlib import Path

video_path = Path(r"c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min.mp4")

timestamps = [10, 60, 150, 240, 350]
print("=== AUDIO VOLUME AUDIT ACROSS MASTER FILM ===")

for t in timestamps:
    cmd = [
        "ffmpeg", "-y", "-ss", str(t), "-t", "5",
        "-i", str(video_path),
        "-af", "volumedetect",
        "-f", "null", "NUL"
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    mean_v = ""
    max_v = ""
    for line in r.stderr.splitlines():
        if "mean_volume" in line:
            mean_v = line.split("mean_volume:")[1].strip()
        if "max_volume" in line:
            max_v = line.split("max_volume:")[1].strip()
    print(f"  At {t:03d}s: mean_volume = {mean_v:<10} | max_volume = {max_v}")

import subprocess
from pathlib import Path

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
FINAL_FILM = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min.mp4"
assembled_no_bgm = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "assembled_no_bgm.mp4"
subbed = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "subbed_104_body.mp4"

# Extract 5 seconds of audio from 00:00:10 to 00:00:15 from subbed, assembled_no_bgm, and final_film
for name, f in [("subbed", subbed), ("assembled_no_bgm", assembled_no_bgm), ("final", FINAL_FILM)]:
    cmd = [
        "ffmpeg", "-y", "-ss", "00:00:10", "-t", "5",
        "-i", str(f),
        "-af", "volumedetect",
        "-f", "null", "NUL"
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if "mean_volume" in line or "max_volume" in line:
            print(f"{name} at 10s: {line.strip()}")

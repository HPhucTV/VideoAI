import subprocess
from pathlib import Path

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
OUT_JOB = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min"
FINAL_FILM = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min.mp4"

for f in [OUT_JOB / "raw_104_body.mp4", OUT_JOB / "subbed_104_body.mp4", OUT_JOB / "assembled_no_bgm.mp4", FINAL_FILM]:
    if f.exists():
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "default=noprint_wrappers=1:nokey=1", str(f)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(f"{f.name}: dur={r.stdout.strip()} size={f.stat().st_size:,} bytes, mtime={f.stat().st_mtime}")

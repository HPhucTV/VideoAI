import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

for name in ["intro_horizontal_16x9.mp4", "outro_horizontal_16x9.mp4"]:
    p = BASE_DIR / "shared-assets" / "branding" / name
    cmd = ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,sample_rate,channels", "-of", "json", str(p)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(name, r.stdout)

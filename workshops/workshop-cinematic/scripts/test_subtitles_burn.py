import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SRT_PATH = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min.srt"
seg_1 = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "segments" / "segment_001.mp4"
test_out = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "test_sub.mp4"

srt_escaped = str(SRT_PATH).replace("\\", "/").replace(":", "\\:")
cmd = [
    "ffmpeg", "-y",
    "-i", str(seg_1),
    "-vf", f"subtitles='{srt_escaped}':force_style='FontSize=22,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=1,Alignment=2,MarginV=35'",
    "-c:v", "libx264", "-c:a", "copy",
    "-t", "3",
    str(test_out)
]
print("Running test subtitle burn...")
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode == 0:
    print(f"Subtitles burned successfully! ({test_out.stat().st_size:,} bytes)")
else:
    print("Error burning subtitles:", r.stderr[-500:])

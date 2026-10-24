from pathlib import Path
import os
import subprocess

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
OUT_JOB = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min"
FINAL_FILM = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min.mp4"

seg_dir = OUT_JOB / "segments"
valid_segs = list(seg_dir.glob("segment_*.mp4"))
print(f"Total valid segments on disk: {len(valid_segs)}/104")

raw_body = OUT_JOB / "raw_104_body.mp4"
subbed_body = OUT_JOB / "subbed_104_body.mp4"
assembled_no_bgm = OUT_JOB / "assembled_no_bgm.mp4"

for f in [raw_body, subbed_body, assembled_no_bgm, FINAL_FILM]:
    if f.exists():
        print(f"  {f.name}: {f.stat().st_size:,} bytes")
    else:
        print(f"  {f.name}: NOT YET CREATED")

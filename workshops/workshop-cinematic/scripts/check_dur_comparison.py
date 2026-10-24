import subprocess
from pathlib import Path

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
vid_dir = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "videos"
audio_dir = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min" / "audio" / "shots"

def get_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())

diffs = []
total_a = 0
total_v = 0

for i in range(1, 105):
    v = vid_dir / f"shot_{i:03d}.mp4"
    a = audio_dir / f"shot_{i:03d}.mp3"
    vd = get_dur(v)
    ad = get_dur(a)
    diffs.append((i, vd, ad, vd - ad))
    total_v += vd
    total_a += ad

print(f"Total Video duration: {total_v:.1f}s | Total Audio duration: {total_a:.1f}s")
print(f"Average Video duration: {total_v/104:.2f}s | Average Audio duration: {total_a/104:.2f}s")

shorter_vids = [x for x in diffs if x[1] < x[2]]
longer_vids = [x for x in diffs if x[1] >= x[2]]
print(f"Videos shorter than audio: {len(shorter_vids)}")
print(f"Videos longer than audio: {len(longer_vids)}")
if shorter_vids:
    print("Sample shorter:", shorter_vids[:5])
if longer_vids:
    print("Sample longer:", longer_vids[:5])

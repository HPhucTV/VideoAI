import subprocess
from pathlib import Path

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
OUT_JOB = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min"
VID_DIR = OUT_JOB / "videos"
AUDIO_DIR = OUT_JOB / "audio" / "shots"
TEST_DIR = OUT_JOB / "test_pipeline"
TEST_DIR.mkdir(parents=True, exist_ok=True)

def get_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())

# Render first 3 segments
seg_paths = []
for i in [1, 2, 3]:
    v = VID_DIR / f"shot_{i:03d}.mp4"
    a = AUDIO_DIR / f"shot_{i:03d}.mp3"
    out_seg = TEST_DIR / f"test_seg_{i:03d}.mp4"
    a_dur = get_dur(a)
    
    # Scale to 1920x1080, fps=30, natural 1.0x motion, trim to exact audio duration
    vf = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(v),
        "-i", str(a),
        "-vf", vf,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-t", f"{a_dur:.3f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        str(out_seg)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    seg_paths.append(out_seg)
    print(f"Segment {i} rendered: dur={get_dur(out_seg):.2f}s")

# Check audio volume of segment 1
r = subprocess.run(["ffmpeg", "-y", "-i", str(seg_paths[0]), "-af", "volumedetect", "-f", "null", "NUL"], capture_output=True, text=True)
for line in r.stderr.splitlines():
    if "mean_volume" in line or "max_volume" in line:
        print("  Seg 1 Volume:", line.strip())

print("Test segments rendered successfully!")

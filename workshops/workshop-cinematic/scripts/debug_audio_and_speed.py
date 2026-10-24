import subprocess
from pathlib import Path

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
OUT_JOB = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min"
FINAL_FILM = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min.mp4"

def inspect_file(f_path):
    print(f"\n--- INSPECTING {f_path.name} ---")
    cmd = ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,duration,r_frame_rate,sample_rate,channels", "-of", "json", str(f_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout)

inspect_file(OUT_JOB / "segments" / "segment_001.mp4")
inspect_file(OUT_JOB / "segments" / "segment_002.mp4")
inspect_file(OUT_JOB / "raw_104_body.mp4")
inspect_file(OUT_JOB / "subbed_104_body.mp4")
inspect_file(OUT_JOB / "assembled_no_bgm.mp4")
inspect_file(FINAL_FILM)

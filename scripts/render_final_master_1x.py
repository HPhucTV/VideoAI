import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

INTRO = ROOT_DIR / "shared-assets" / "branding" / "intro_horizontal_16x9.mp4"
BODY_VIDEO = ROOT_DIR / "output" / "cinematic" / "temp_assembly" / "body_video.mp4"
BODY_AUDIO = ROOT_DIR / "output" / "cinematic" / "audio" / "master_film_audio_48k.mp3"
OUTRO = ROOT_DIR / "shared-assets" / "branding" / "outro_horizontal_16x9.mp4"
OUTPUT = ROOT_DIR / "output" / "cinematic" / "master_film_chatbot_vs_agent_16x9.mp4"

# Subtitle path formatted for FFmpeg
sub_path = "output/cinematic/subtitles/content.srt"

filter_complex = (
    "[0:v]scale=1920:1080:flags=lanczos,fps=60,format=yuv420p,setpts=PTS-STARTPTS[v0]; "
    "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a0]; "
    f"[1:v]scale=1920:1080:flags=lanczos,fps=60,format=yuv420p,setpts=PTS-STARTPTS,subtitles={sub_path}:force_style='FontName=Arial,FontSize=22,Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=4,Outline=1,Shadow=0,Alignment=2,MarginV=40'[v1]; "
    "[2:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a1]; "
    "[3:v]scale=1920:1080:flags=lanczos,fps=60,format=yuv420p,setpts=PTS-STARTPTS[v2]; "
    "[3:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a2]; "
    "[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]"
)

cmd = [
    "ffmpeg", "-y",
    "-i", str(INTRO),
    "-i", str(BODY_VIDEO),
    "-i", str(BODY_AUDIO),
    "-i", str(OUTRO),
    "-filter_complex", filter_complex,
    "-map", "[v]",
    "-map", "[a]",
    "-c:v", "h264_mf",
    "-b:v", "12M",
    "-c:a", "aac",
    "-b:a", "192k",
    "-ar", "48000",
    str(OUTPUT)
]

print("Starting Hardware-Accelerated 1.0x Master Film Assembly...")
print(" ".join(cmd))
sys.stdout.flush()

res = subprocess.run(cmd)

if res.returncode != 0:
    print(f"Error during master assembly, exit code {res.returncode}")
    sys.exit(res.returncode)

size_mb = OUTPUT.stat().st_size / (1024 * 1024)
print(f"\n=======================================================")
print(f"MASTER FILM GENERATION COMPLETED SUCCESSFULLY!")
print(f"Output File: {OUTPUT}")
print(f"File Size: {size_mb:.2f} MB")
print(f"=======================================================")

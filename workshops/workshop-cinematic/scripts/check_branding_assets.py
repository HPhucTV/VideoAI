from pathlib import Path

# scripts -> workshop-cinematic -> workshops -> VideoAI
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
print("BASE_DIR is:", BASE_DIR)

files = [
    BASE_DIR / "shared-assets/branding/intro_horizontal_16x9.mp4",
    BASE_DIR / "shared-assets/branding/outro_horizontal_16x9.mp4",
    BASE_DIR / "shared-assets/branding/giaimatech_logo.png",
    BASE_DIR / "workshops/workshop-whiteboard/assets/audio/bgm/healing-piano.mp3",
    BASE_DIR / "output/cinematic/job-ai-agent-giaimatech-10min.srt"
]

for f in files:
    exists = f.exists()
    size = f.stat().st_size if exists else 0
    print(f"{f.name}: Exists={exists} (size={size:,} bytes)")

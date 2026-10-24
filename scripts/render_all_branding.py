"""
Render all GiaiMaTech Brand Bumpers using Remotion 4.0 + FFmpeg Audio FX
Produces:
- shared-assets/branding/intro_horizontal_16x9.mp4  (1920x1080 @ 60fps, 2.0s)
- shared-assets/branding/intro_vertical_9x16.mp4    (1080x1920 @ 60fps, 2.0s)
- shared-assets/branding/outro_horizontal_16x9.mp4  (1920x1080 @ 60fps, 4.5s)
- shared-assets/branding/outro_vertical_9x16.mp4    (1080x1920 @ 60fps, 4.5s)
"""

import os
import subprocess
import sys
from pathlib import Path

# Force utf-8 for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
EXPL_DIR = ROOT_DIR / "workshops" / "workshop-explainer"
BRANDING_DIR = ROOT_DIR / "shared-assets" / "branding"

def run_cmd(cmd, cwd=None):
    print(f"\n[RUNNING] {cmd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] {res.stderr}")
        raise RuntimeError(f"Command failed with code {res.returncode}")
    print("[SUCCESS]")
    return res.stdout

def main():
    BRANDING_DIR.mkdir(parents=True, exist_ok=True)
    temp_dir = BRANDING_DIR / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 1. Compositions to render
    comps = [
        {
            "id": "IntroBumper-Landscape",
            "raw_video": temp_dir / "intro_land_raw.mp4",
            "final_video": BRANDING_DIR / "intro_horizontal_16x9.mp4",
            "type": "intro"
        },
        {
            "id": "IntroBumper-Portrait",
            "raw_video": temp_dir / "intro_port_raw.mp4",
            "final_video": BRANDING_DIR / "intro_vertical_9x16.mp4",
            "type": "intro"
        },
        {
            "id": "OutroBumper-Landscape",
            "raw_video": temp_dir / "outro_land_raw.mp4",
            "final_video": BRANDING_DIR / "outro_horizontal_16x9.mp4",
            "type": "outro"
        },
        {
            "id": "OutroBumper-Portrait",
            "raw_video": temp_dir / "outro_port_raw.mp4",
            "final_video": BRANDING_DIR / "outro_vertical_9x16.mp4",
            "type": "outro"
        }
    ]

    # 2. Render each composition using Remotion
    for comp in comps:
        print(f"\n==========================================")
        print(f"🎬 Rendering Remotion Composition: {comp['id']}")
        print(f"==========================================")
        cmd = f'cmd /c "npx remotion render src/index.ts {comp["id"]} \"{comp["raw_video"]}\" --concurrency=4 --gl=angle"'
        run_cmd(cmd, cwd=EXPL_DIR)

    # 3. Synthesize Audio SFX
    intro_sfx = temp_dir / "intro_sfx.m4a"
    outro_sfx = temp_dir / "outro_sfx.m4a"

    print("\n==========================================")
    print("🔊 Synthesizing Intro Audio Design (Cyber Riser + Sub-Bass Drop + Ping)...")
    print("==========================================")
    intro_audio_cmd = (
        f'ffmpeg -y '
        f'-f lavfi -i "anoisesrc=d=0.7:c=pink,bandpass=f=800:width_type=h:w=600,volume=0.4,afade=t=out:st=0.35:d=0.35" '
        f'-f lavfi -i "sine=f=75:d=1.5,afade=t=out:st=0.25:d=1.2,volume=0.85" '
        f'-f lavfi -i "sine=f=1108.73:d=0.6,adelay=320|320,afade=t=out:st=0.32:d=0.5,volume=0.3" '
        f'-filter_complex "[0:a][1:a][2:a]amix=inputs=3:duration=first:dropout_transition=0,aformat=channel_layouts=stereo,apad,atrim=0:2.0[a]" '
        f'-map "[a]" -c:a aac -b:a 192k -ar 48000 "{intro_sfx}"'
    )
    run_cmd(intro_audio_cmd)

    print("\n==========================================")
    print("🔊 Synthesizing Outro Audio Design (Warm Ambient Bed + Subscribe Click + Bell Chime)...")
    print("==========================================")
    outro_audio_cmd = (
        f'ffmpeg -y '
        f'-f lavfi -i "sine=f=329.63:d=4.5,volume=0.15,afade=t=in:st=0:d=0.5,afade=t=out:st=3.8:d=0.7" '
        f'-f lavfi -i "sine=f=493.88:d=4.5,volume=0.12,afade=t=in:st=0:d=0.5,afade=t=out:st=3.8:d=0.7" '
        f'-f lavfi -i "anoisesrc=d=0.06:c=white,adelay=1250|1250,volume=0.65,afade=t=out:st=1.26:d=0.05" '
        f'-f lavfi -i "sine=f=987.77:d=1.2,adelay=1280|1280,afade=t=out:st=1.35:d=1.1,volume=0.5" '
        f'-f lavfi -i "sine=f=1479.98:d=1.0,adelay=1330|1330,afade=t=out:st=1.4:d=0.9,volume=0.35" '
        f'-filter_complex "[0:a][1:a][2:a][3:a][4:a]amix=inputs=5:duration=first:dropout_transition=0,aformat=channel_layouts=stereo,apad,atrim=0:4.5[a]" '
        f'-map "[a]" -c:a aac -b:a 192k -ar 48000 "{outro_sfx}"'
    )
    run_cmd(outro_audio_cmd)

    # 4. Mux Video + Audio for each bumper
    print("\n==========================================")
    print("🚀 Muxing High-End Master Bumpers...")
    print("==========================================")
    for comp in comps:
        sfx_file = intro_sfx if comp["type"] == "intro" else outro_sfx
        mux_cmd = (
            f'ffmpeg -y -i "{comp["raw_video"]}" -i "{sfx_file}" '
            f'-c:v copy -c:a copy -map 0:v:0 -map 1:a:0 -shortest "{comp["final_video"]}"'
        )
        run_cmd(mux_cmd)
        print(f"✅ Generated Master: {comp['final_video']}")

    # 5. Clean up temporary files
    for comp in comps:
        if comp["raw_video"].exists():
            comp["raw_video"].unlink()
    if intro_sfx.exists():
        intro_sfx.unlink()
    if outro_sfx.exists():
        outro_sfx.unlink()
    test_files = [BRANDING_DIR / "test_intro.mp4", BRANDING_DIR / "test_frame.png", BRANDING_DIR / "test_intro_sfx.m4a"]
    for tf in test_files:
        if tf.exists():
            tf.unlink()
    try:
        temp_dir.rmdir()
    except Exception:
        pass

    print("\n✨ ALL 4 GIAIMATECH BRAND BUMPERS COMPLETED SUCCESSFULLY! ✨")

if __name__ == "__main__":
    main()

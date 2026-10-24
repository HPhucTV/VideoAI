"""
Generate Storyboard Start-Frames for Gate 5 using Google Flow via FlowKit
Inherits locked Character & Set Media IDs from Gate 3:
- Chatty: 6b41bade-86ff-453f-ad49-0b6a1c2e51b6
- Agent-X: 00d6b6f2-f80b-45ee-b989-70a9e7bf3e10
- Set 1 (Cyber Core): 2118d8a5-9f2d-4c1d-a436-f893ed3fda0a
- Set 2 (Glitch Breach): 21e8c938-dce5-43d4-b693-17b3c6876599
"""

import json
import os
import shutil
import sys
import time
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
STORYBOARD_DIR = ROOT_DIR / "output" / "cinematic" / "storyboard"
STORYBOARD_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\tranh\.gemini\antigravity\brain\e4e95502-3da3-4c54-80ff-c7025c522886")

FLOWKIT_URL = "http://127.0.0.1:8100/api/flow/generate-image"

MEDIA_CHATTY = "6b41bade-86ff-453f-ad49-0b6a1c2e51b6"
MEDIA_AGENTX = "00d6b6f2-f80b-45ee-b989-70a9e7bf3e10"
MEDIA_SET1 = "2118d8a5-9f2d-4c1d-a436-f893ed3fda0a"
MEDIA_SET2 = "21e8c938-dce5-43d4-b693-17b3c6876599"

KEY_FRAMES = [
    {
        "frame_id": "frame_act1_intro",
        "act": "Hồi 1: Giới thiệu 2 Thực Thể",
        "shots": "Shot 01 - 03",
        "title": "Bé Chatty & Bé Agent-X tại Trung Tâm Cyber Core",
        "prompt": (
            "Cinematic 3D Chibi establishing shot of cute robot Chatty (white and cyan) and cool cyborg Agent-X (amber orange armor) "
            "standing side by side in the futuristic Cyber Core Nexus server room with glowing blue server racks and floating hologram screens, "
            "16:9 widescreen, Pixar 3D aesthetic, volumetric neon rim lighting, Octane Render 8k"
        ),
        "refs": [MEDIA_CHATTY, MEDIA_AGENTX]
    },
    {
        "frame_id": "frame_act2_crisis",
        "act": "Hồi 2: Báo Động Đỏ & Chatbot Bất Lực",
        "shots": "Shot 04 - 07",
        "title": "Sự Cố Rò Rỉ Mã Độc & Bé Chatty Bối Rối",
        "prompt": (
            "Cinematic 3D Chibi dramatic shot, flashing red alert emergency lights, cute robot Chatty standing panicking with spinning exclamation mark eyes "
            "as glowing red malicious code tentacles glitch on holographic monitors in the server room, unable to touch physical switches, "
            "16:9 widescreen, dark moody atmospheric red and cyan lighting, Octane Render 8k"
        ),
        "refs": [MEDIA_CHATTY, MEDIA_SET2]
    },
    {
        "frame_id": "frame_act3_action",
        "act": "Hồi 3: AI Agent Xuất Trận",
        "shots": "Shot 08 - 11",
        "title": "Bé Agent-X Kích Hoạt Cánh Tay Máy & Khắc Phục Lỗi",
        "prompt": (
            "Cinematic 3D Chibi action shot of cyborg Agent-X in sleek amber armor with glowing HUD eye scanner, "
            "three miniature robotic arms extending from his tech backpack rapidly typing terminal code on floating golden holographic screens to seal data breach, "
            "16:9 widescreen, dynamic heroic composition, Octane Render 8k, Unreal Engine 5 aesthetic"
        ),
        "refs": [MEDIA_AGENTX]
    },
    {
        "frame_id": "frame_act4_compare",
        "act": "Hồi 4: Bóc Tách Khác Biệt 4 Trụ Cột",
        "shots": "Shot 12 - 14",
        "title": "Bảng So Sánh 4 Trụ Cột Giữa Chatbot & Agent",
        "prompt": (
            "Cinematic 3D Chibi shot, cute robot Chatty clapping in admiration beside cyborg Agent-X who gestures towards four glowing floating holographic pillar icons: "
            "Brain reasoning, Long-term Memory, Digital Tools, and Autonomy, shiny reflective floor, 16:9 widescreen, Octane Render 8k"
        ),
        "refs": [MEDIA_CHATTY, MEDIA_AGENTX]
    },
    {
        "frame_id": "frame_act5_conclusion",
        "act": "Hồi 5: Kết Luận & Kêu Gọi Đăng Ký",
        "shots": "Shot 15 - 16",
        "title": "Hai Bé Chibi Đập Tay & Kêu Gọi Đăng Ký GiaiMaTech",
        "prompt": (
            "Cinematic 3D Chibi cheerful shot, cute robot Chatty and cyborg Agent-X high-fiving happily in the restored peaceful glowing cyan Cyber Core room, "
            "smiling and looking directly at camera, holding a futuristic glowing metallic card with channel branding, 16:9 widescreen, warm studio lighting, Octane Render 8k"
        ),
        "refs": [MEDIA_CHATTY, MEDIA_AGENTX]
    }
]

def generate_frame(kf):
    print(f"\n[STORYBOARD] Generating {kf['frame_id']} ({kf['title']})...")
    payload = {
        "prompt": kf["prompt"],
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE",
        "count": 1,
        "user_paygate_tier": "PAYGATE_TIER_TWO",
        "character_media_ids": kf["refs"]
    }
    req = urllib.request.Request(
        FLOWKIT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        media = data["media"][0]
        media_id = media["name"]
        fife_url = media["image"]["generatedImage"]["fifeUrl"]
        print(f"✅ Generated Media ID: {media_id}")

        # Download local PNG
        local_png = STORYBOARD_DIR / f"{kf['frame_id']}.png"
        urllib.request.urlretrieve(fife_url, local_png)
        # Copy to artifact dir for direct embedding
        shutil.copy(local_png, ARTIFACT_DIR / f"{kf['frame_id']}.png")
        print(f"📥 Saved {local_png}")

        return {
            **kf,
            "media_id": media_id,
            "fife_url": fife_url,
            "local_file": str(local_png.name)
        }

def main():
    manifest = []
    for kf in KEY_FRAMES:
        res = generate_frame(kf)
        manifest.append(res)
        time.sleep(3.0) # Small pause between generations

    out_json = STORYBOARD_DIR / "storyboard_manifest.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n✨ All {len(manifest)} Storyboard Frames completed!")

if __name__ == "__main__":
    main()

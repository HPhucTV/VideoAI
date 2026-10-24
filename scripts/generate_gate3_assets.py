"""
Generate Master Assets for Gate 3 (Chatbot vs Agent Chibi 3D) using Google Flow via FlowKit
"""

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT_DIR / "output" / "cinematic" / "gate3_assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FLOWKIT_URL = "http://127.0.0.1:8100/api/flow/generate-image"

ASSETS = [
    {
        "id": "chibi_chatty",
        "name": "Bé Chatty (Chatbot AI)",
        "prompt": (
            "Cinematic 3D Cyber-Chibi character design of an adorable little futuristic robot named Chatty, "
            "proportion 1:3 chibi blind box toy aesthetic, smooth polished white ceramic body with glowing cyan neon trim, "
            "big cute round expressive digital blue LED eyes, miniature call-center communication headset on head, "
            "small glowing speech bubble hologram on tummy displaying dots, tiny stubby hands, cheerful and curious smile, "
            "soft studio rim lighting, neutral tech studio background, Octane Render 8K, Unreal Engine 5 render, highly detailed"
        ),
        "aspect_ratio": "IMAGE_ASPECT_RATIO_SQUARE"
    },
    {
        "id": "chibi_agentx",
        "name": "Bé Agent-X (AI Agent)",
        "prompt": (
            "Cinematic 3D Cyber-Chibi character design of a cool autonomous little cyborg agent named Agent-X, "
            "proportion 1:3 chibi blind box toy aesthetic, wearing miniature sleek amber orange and dark graphite carbon armor, "
            "glowing holographic orange HUD scanner monocle over one eye, miniature tech backpack with three tiny automated robotic arms holding a digital stylus and tool, "
            "confident determined expression, soft amber rim lighting, neutral tech studio background, Octane Render 8K, Unreal Engine 5 render, highly detailed"
        ),
        "aspect_ratio": "IMAGE_ASPECT_RATIO_SQUARE"
    },
    {
        "id": "set_cyber_core",
        "name": "Set 1: Cyber Core Nexus",
        "prompt": (
            "Cinematic establishing master plate of a futuristic miniature Cyber-Chibi high-tech central server room diorama, "
            "glowing pastel cyan and deep blue neon server racks, floating translucent holographic screens, glossy reflective mirror tech floor, "
            "warm volumetric rim light, peaceful cybernetic atmosphere, Octane Render 8K, Unreal Engine 5 aesthetic, 16:9 widescreen"
        ),
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE"
    },
    {
        "id": "set_glitch_breach",
        "name": "Set 2: The Glitch Breach",
        "prompt": (
            "Cinematic establishing master plate of a futuristic Cyber-Chibi server room in emergency red alert, "
            "flashing crimson warning lights, glowing red malicious code tentacles glitching on floating holographic monitors, "
            "cyber sparks on high-tech cables, dramatic dark moody red and purple lighting, Octane Render 8K, Unreal Engine 5 aesthetic, 16:9 widescreen"
        ),
        "aspect_ratio": "IMAGE_ASPECT_RATIO_LANDSCAPE"
    }
]

def generate_asset(asset):
    print(f"\n[SUBMITTING] {asset['name']}...")
    payload = {
        "prompt": asset["prompt"],
        "aspect_ratio": asset["aspect_ratio"],
        "count": 1,
        "user_paygate_tier": "PAYGATE_TIER_TWO"
    }
    req = urllib.request.Request(
        FLOWKIT_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[RAW RESPONSE] {data}")
            return data
    except Exception as e:
        print(f"[ERROR] Failed to generate {asset['name']}: {e}")
        return None

def main():
    results = {}
    for asset in ASSETS:
        res = generate_asset(asset)
        results[asset["id"]] = {"asset": asset, "response": res}
        time.sleep(3) # Small cooldown between generations

    out_file = OUTPUT_DIR / "manifest.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved manifest to {out_file}")

if __name__ == "__main__":
    main()

import requests
import json

payload = {
    "scene_id": "69bb4381-815e-4f15-be89-eb32405fc15d",
    "prompt": "Tiny cute glowing chibi robot Bé Byte in neon futuristic laboratory, floating in mid-air, expressive LED digital eyes, looking at a floating hologram, 3D donghua animation style, cinematic lighting",
    "start_image_media_id": "52881163-3335-45f2-a86f-630c0525eb24",
    "project_id": "3d0588c7-d1b1-4f07-929d-55f9d60712ff",
    "aspect_ratio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
    "model_family": "veo"
}

print("Submitting video generation for Shot 003 to new project...")
r = requests.post("http://127.0.0.1:8100/api/flow/generate-video", json=payload, timeout=30)
print("Response status:", r.status_code)
print("Response body:", r.text)

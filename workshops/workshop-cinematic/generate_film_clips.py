import httpx
import json
import os
import time

PROJECT_ID = "bdfe9e57-635b-4036-8a48-c7841a74e208"
BASE_URL = "http://127.0.0.1:8100/api/flow"
OUT_DIR = "output/cinematic/videos"
MANIFEST_PATH = os.path.join(OUT_DIR, "videos_manifest.json")

os.makedirs(OUT_DIR, exist_ok=True)

CLIPS_TO_GENERATE = [
    {
        "clip_id": "clip_act1_intro",
        "file_name": "video_act1.mp4",
        "start_image_media_id": "f4aa7199-3879-4488-aec9-9e18b411a06c",
        "prompt": "Cinematic 3D Chibi animation, camera slowly pushes forward, cute robot Chatty happily waving with cyan LED eyes, cyborg Agent-X nods in cyber suit, futuristic glowing server room background, 8k octane render",
        "scene_id": "act1_intro",
        "existing_media_id": "71475107-8790-433c-8923-929bf75432c0"
    },
    {
        "clip_id": "clip_act1_agentx",
        "file_name": "video_act1_agentx.mp4",
        "start_image_media_id": "f4aa7199-3879-4488-aec9-9e18b411a06c",
        "prompt": "Cinematic 3D Chibi video, camera pans right focusing on cyborg Agent-X nodding confidently, adjusting glowing holographic gauntlet, high tech server racks behind",
        "scene_id": "act1_agentx"
    },
    {
        "clip_id": "clip_act2_crisis",
        "file_name": "video_act2_crisis.mp4",
        "start_image_media_id": "792ccce6-4436-4142-91a6-c918e2510192",
        "prompt": "Cinematic 3D Chibi video, flashing red alert sirens, cute robot Chatty panicking with exclamation marks in digital eyes, neon red glitch code ripples across the cyberpunk server room, moody atmospheric lighting",
        "scene_id": "act2_crisis"
    },
    {
        "clip_id": "clip_act2_helpless",
        "file_name": "video_act2_helpless.mp4",
        "start_image_media_id": "792ccce6-4436-4142-91a6-c918e2510192",
        "prompt": "Cinematic 3D Chibi video, medium shot on cute robot Chatty holding hands up helplessly, shaking head with question mark on LED screen under emergency red lights",
        "scene_id": "act2_helpless"
    },
    {
        "clip_id": "clip_act3_action",
        "file_name": "video_act3_action.mp4",
        "start_image_media_id": "5ff50511-d095-4326-800b-ab747c03f431",
        "prompt": "Cinematic 3D Chibi action video, cyborg Agent-X miniature robotic arms furiously typing code on glowing holographic screens, sparks of golden light repairing glitching monitors, dynamic heroic angle",
        "scene_id": "act3_action"
    },
    {
        "clip_id": "clip_act3_success",
        "file_name": "video_act3_success.mp4",
        "start_image_media_id": "5ff50511-d095-4326-800b-ab747c03f431",
        "prompt": "Cinematic 3D Chibi video, red alert fades to soothing cyber cyan glow, system restored checkmark flashes on giant server screen, Agent-X standing tall and proud",
        "scene_id": "act3_success"
    },
    {
        "clip_id": "clip_act4_compare",
        "file_name": "video_act4_compare.mp4",
        "start_image_media_id": "6bbcc50d-0935-44d3-9236-8a25263590d1",
        "prompt": "Cinematic 3D Chibi video, slow camera arc around four glowing floating holographic pillar icons of Brain, Memory, Tools, Autonomy, cute robot Chatty clapping happily while Agent-X points to them",
        "scene_id": "act4_compare"
    },
    {
        "clip_id": "clip_act4_icons",
        "file_name": "video_act4_icons.mp4",
        "start_image_media_id": "6bbcc50d-0935-44d3-9236-8a25263590d1",
        "prompt": "Cinematic 3D Chibi video, camera pushes in on glowing holographic icons of Brain, Memory, Tools, Autonomy floating majestically in mid-air with gentle rotating motion",
        "scene_id": "act4_icons"
    },
    {
        "clip_id": "clip_act5_conclusion",
        "file_name": "video_act5_conclusion.mp4",
        "start_image_media_id": "df0bf23b-d529-4d61-896b-c8e9d97ddaab",
        "prompt": "Cinematic 3D Chibi celebration video, cute robot Chatty and cyborg Agent-X giving each other a joyful high-five, looking and smiling directly at the camera with neon Cyber Core ambient glow",
        "scene_id": "act5_conclusion"
    }
]

def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_manifest(manifest):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

def generate_and_poll():
    manifest = load_manifest()

    for idx, item in enumerate(CLIPS_TO_GENERATE, 1):
        clip_id = item["clip_id"]
        file_path = os.path.join(OUT_DIR, item["file_name"])

        # Check if already downloaded
        if os.path.exists(file_path) and os.path.getsize(file_path) > 100000 and clip_id in manifest:
            print(f"[{idx}/{len(CLIPS_TO_GENERATE)}] Clip {clip_id} already exists ({os.path.getsize(file_path)} bytes), skipping.")
            continue

        print(f"\n=======================================================")
        print(f"[{idx}/{len(CLIPS_TO_GENERATE)}] Processing {clip_id}...")
        print(f"Prompt: {item['prompt']}")
        print(f"Start Frame: {item['start_image_media_id']}")

        # Submit generation
        payload = {
            "start_image_media_id": item["start_image_media_id"],
            "prompt": item["prompt"],
            "project_id": PROJECT_ID,
            "scene_id": item["scene_id"],
            "aspect_ratio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
            "user_paygate_tier": "PAYGATE_TIER_TWO",
            "model_family": "veo"
        }

        try:
            res = httpx.post(f"{BASE_URL}/generate-video", json=payload, timeout=60)
            res.raise_for_status()
            data = res.json()
            ops = data.get("operations", [])
            if not ops:
                print(f"Error submitting {clip_id}: No operations returned: {data}")
                continue
            op_id = (ops[0].get("operation") or {}).get("name") or ops[0].get("name")
            print(f"Submitted successfully! Operation ID: {op_id}")
        except Exception as e:
            print(f"Failed to submit {clip_id}: {e}")
            time.sleep(5)
            continue

        # Poll status
        poll_payload = {
            "operations": [{"operation": {"name": op_id}}],
            "project_id": PROJECT_ID
        }

        video_url = None
        media_id = None
        start_t = time.time()

        for poll_i in range(40): # Poll up to ~200s
            time.sleep(5)
            try:
                poll_res = httpx.post(f"{BASE_URL}/check-status", json=poll_payload, timeout=30)
                poll_data = poll_res.json()
                poll_ops = poll_data.get("operations", [])
                if not poll_ops:
                    print(f"Poll {poll_i+1}: empty response")
                    continue
                op_status = poll_ops[0].get("status")
                elapsed = int(time.time() - start_t)
                print(f"Poll {poll_i+1} ({elapsed}s): status={op_status}")

                if op_status == "MEDIA_GENERATION_STATUS_SUCCESSFUL":
                    meta_video = (poll_ops[0].get("operation") or {}).get("metadata", {}).get("video", {})
                    video_url = meta_video.get("fifeUrl")
                    media_id = meta_video.get("mediaId")
                    print(f"Generation SUCCEEDED! mediaId={media_id}")
                    break
                elif op_status == "MEDIA_GENERATION_STATUS_FAILED":
                    print(f"Generation FAILED: {poll_ops[0]}")
                    break
            except Exception as e:
                print(f"Poll error: {e}")

        if not video_url:
            print(f"Timed out or failed for {clip_id}")
            continue

        # Download video
        print(f"Downloading video from {video_url[:60]}... to {file_path}")
        try:
            dl_res = httpx.get(video_url, timeout=90)
            with open(file_path, "wb") as f:
                f.write(dl_res.content)
            file_size = os.path.getsize(file_path)
            print(f"Saved {file_size} bytes to {file_path}")

            manifest[clip_id] = {
                "file_name": item["file_name"],
                "media_id": media_id,
                "fife_url": video_url,
                "file_size": file_size,
                "prompt": item["prompt"],
                "start_frame": item["start_image_media_id"],
                "timestamp": time.time()
            }
            save_manifest(manifest)
        except Exception as e:
            print(f"Error downloading {clip_id}: {e}")

        # Cooldown between submissions to stay well within limits
        print("Cooling down 5s before next shot...")
        time.sleep(5)

    print("\nALL CLIPS GENERATION FINISHED!")

if __name__ == "__main__":
    generate_and_poll()

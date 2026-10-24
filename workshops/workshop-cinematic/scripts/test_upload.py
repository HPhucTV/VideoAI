import requests
import base64
from pathlib import Path

img_path = Path(r"c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min\images\shot_003.jpg")
if not img_path.exists():
    # pick any shot
    img_path = list(Path(r"c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min\images").glob("*.jpg"))[0]

b64 = base64.b64encode(img_path.read_bytes()).decode()
payload = {
    "image_base64": b64,
    "file_name": "shot_003_test.jpg",
    "project_id": "3d0588c7-d1b1-4f07-929d-55f9d60712ff"
}

r = requests.post("http://127.0.0.1:8100/api/flow/upload-image", json=payload, timeout=30)
print("Upload status:", r.status_code)
print("Upload response:", r.text)

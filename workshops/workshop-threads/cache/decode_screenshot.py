import json
import base64
from pathlib import Path
from PIL import Image

txt_path = Path(r"C:\Users\tranh\.gemini\antigravity\brain\0acabd2b-aa48-4bc8-a2e8-c7a0b0e11f56\.system_generated\steps\1085\output.txt")
content = txt_path.read_text(encoding="utf-8")

prefix = "data:image/png;base64,"
if prefix in content:
    idx = content.find(prefix) + len(prefix)
    end_idx = content.find('"', idx)
    if end_idx == -1:
        end_idx = len(content)
    b64_str = content[idx:end_idx].strip()
    img_data = base64.b64decode(b64_str)
    out_f = Path("workshops/workshop-threads/cache/real_direct_screenshot.png")
    out_f.write_bytes(img_data)
    im = Image.open(out_f)
    print(f"SUCCESS: Direct screenshot saved: {out_f}, Size: {im.size}, Mode: {im.mode}")
else:
    print(f"Prefix not found. Content sample: {content[:200]}")

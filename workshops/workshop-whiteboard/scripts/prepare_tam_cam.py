import os
import sys
from pathlib import Path
import cv2

src_jpg = r"C:\Users\tranh\.gemini\antigravity\brain\343778d2-0dda-4e88-935a-4838b12e3b50\tam_cam_scene_1791969440557.jpg"
out_dir = Path("workshops/workshop-whiteboard/assets/whiteboard/tam-cam")
out_dir.mkdir(parents=True, exist_ok=True)
out_png = out_dir / "scene-tam-cam.png"

img = cv2.imread(src_jpg)
if img is None:
    print(f"Error loading {src_jpg}")
    sys.exit(1)

h, w, _ = img.shape
print(f"Loaded image size: {w}x{h}")
cv2.imwrite(str(out_png), img)
print(f"Successfully saved to {out_png}")

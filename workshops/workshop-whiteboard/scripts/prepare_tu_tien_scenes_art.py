#!/usr/bin/env python3
"""
Chuẩn hóa và nạp 10 tác phẩm nghệ thuật Tu Tiên từ AI Generator vào từng phân cảnh:
output/whiteboard/job-phe-dan-nghich-thien/scenes/scene-XX/scene-XX.png
"""
import sys
from pathlib import Path
from PIL import Image

BG_CREAM = (245, 235, 215)  # #F5EBD7

def normalize_image(src_path: Path, dst_path: Path, target_w: int = 1920, target_h: int = 1080):
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src_path) as im:
        im = im.convert("RGBA")
        canvas = Image.new("RGBA", (target_w, target_h), (*BG_CREAM, 255))
        sw, sh = im.size
        scale = min(target_w / sw, target_h / sh)
        new_w = int(round(sw * scale))
        new_h = int(round(sh * scale))
        resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        paste_x = (target_w - new_w) // 2
        paste_y = (target_h - new_h) // 2
        canvas.paste(resized, (paste_x, paste_y), mask=resized)
        final_rgb = canvas.convert("RGB")
        final_rgb.save(dst_path, format="PNG", optimize=True)
        print(f"[OK] Da nap anh nghe thuat {src_path.name} -> {dst_path}")

def ingest_all():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    brain_dir = Path(r"C:\Users\tranh\.gemini\antigravity\brain\c73914cf-b966-4e75-8c8e-187c48b350bc")
    scenes_dir = root_dir / "output" / "whiteboard" / "job-phe-dan-nghich-thien" / "scenes"

    mapping = {
        "scene-01": "scene_01_1792153949720.jpg",
        "scene-02": "scene_02_1792153958938.jpg",
        "scene-03": "scene_03_1792153948598.jpg",
        "scene-04": "scene_04_1792153951847.jpg",
        "scene-05": "scene_05_1792153949682.jpg",
        "scene-06": "scene_06_1792153966086.jpg",
        "scene-07": "scene_07_1792153962473.jpg",
        "scene-08": "scene_08_1792153960738.jpg",
        "scene-09": "scene_09_1792153985549.jpg",
        "scene-10": "scene_10_1792153960558.jpg",
    }

    for sc_id, filename in mapping.items():
        src = brain_dir / filename
        dst = scenes_dir / sc_id / f"{sc_id}.png"
        if src.exists():
            normalize_image(src, dst)
        else:
            print(f"[WARN] Khong tim thay {src}")

if __name__ == "__main__":
    ingest_all()

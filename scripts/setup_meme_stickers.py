"""
Module tự động tạo & đồng bộ kho Meme Stickers cho Xưởng 5 (workshop-threads).
Mỗi sticker được xử lý:
- Tải ảnh gốc độ nét cao từ Wikimedia Commons API (iiurlwidth=500).
- Cắt tròn / die-cut chuẩn kích thước 360x360.
- Viền trắng Sticker 10px + Bóng đổ mềm (Drop Shadow) chuẩn phong cách TikTok/Reels.
- Huy hiệu biểu cảm (Meme Badge Pill) đi kèm chữ tương phản cao.
"""
from __future__ import annotations

import io
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Fix Windows console UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
MEMES_DIR = ROOT_DIR / "workshops" / "workshop-threads" / "assets" / "memes"
MEMES_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "OmniVideoStudioMemeEngine/1.0 (https://omnivideo.studio; contact@omnivideo.studio)"}


def get_font(size: int = 24, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for fp in font_candidates:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def fetch_commons_thumb(title: str, width: int = 500) -> bytes:
    api = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&iiurlwidth={width}&format=json"
    req = urllib.request.Request(api, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for p in pages.values():
            info = p.get("imageinfo", [{}])[0]
            thumb_url = info.get("thumburl") or info.get("url")
            if thumb_url:
                r_img = urllib.request.Request(thumb_url, headers=HEADERS)
                with urllib.request.urlopen(r_img, timeout=15) as resp_img:
                    return resp_img.read()
    raise ValueError(f"Could not fetch thumb for title: {title}")


def create_meme_sticker(
    img_bytes: bytes,
    out_path: Path,
    badge_text: str,
    badge_bg: tuple[int, int, int] = (255, 60, 60),
    badge_fg: tuple[int, int, int] = (255, 255, 255),
    size: tuple[int, int] = (340, 340),
) -> Path:
    im = Image.open(io.BytesIO(img_bytes)).convert("RGBA")

    # Center crop square
    w, h = im.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    im = im.crop((left, top, left + min_dim, top + min_dim))
    im = im.resize(size, Image.Resampling.LANCZOS)

    # Circular mask for core image
    mask = Image.new("L", size, 0)
    draw_m = ImageDraw.Draw(mask)
    draw_m.ellipse((0, 0, size[0], size[1]), fill=255)

    sticker_core = Image.new("RGBA", size, (0, 0, 0, 0))
    sticker_core.paste(im, (0, 0), mask)

    # Canvas with padding for 10px white border and 16px shadow
    pad = 32
    canvas_w = size[0] + pad * 2
    canvas_h = size[1] + pad * 2 + 35  # Extra room for bottom badge
    canvas_size = (canvas_w, canvas_h)

    final_canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))

    # 1. Soft Drop Shadow
    shadow_mask = Image.new("L", canvas_size, 0)
    s_draw = ImageDraw.Draw(shadow_mask)
    s_draw.ellipse(
        (pad - 4, pad + 10, pad + size[0] + 4, pad + size[1] + 20),
        fill=160,
    )
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(12))
    shadow_img = Image.new("RGBA", canvas_size, (0, 0, 0, 160))
    final_canvas.paste(shadow_img, (0, 0), shadow_mask)

    # 2. White Die-Cut Border (10px thickness)
    border_mask = Image.new("L", canvas_size, 0)
    b_draw = ImageDraw.Draw(border_mask)
    bw = 10
    b_draw.ellipse(
        (pad - bw, pad - bw, pad + size[0] + bw, pad + size[1] + bw),
        fill=255,
    )
    white_border = Image.new("RGBA", canvas_size, (255, 255, 255, 255))
    final_canvas.paste(white_border, (0, 0), border_mask)

    # 3. Paste Core Image
    final_canvas.paste(sticker_core, (pad, pad), mask)

    # 4. Draw Badge Pill at the bottom
    font = get_font(size=22, bold=True)
    badge_draw = ImageDraw.Draw(final_canvas)
    text_bbox = font.getbbox(badge_text)
    t_w = text_bbox[2] - text_bbox[0]
    t_h = text_bbox[3] - text_bbox[1]

    badge_pad_x = 18
    badge_pad_y = 7
    b_box_w = t_w + badge_pad_x * 2
    b_box_h = t_h + badge_pad_y * 2
    b_x = (canvas_w - b_box_w) // 2
    b_y = pad + size[1] - 18

    # Badge white border
    badge_draw.rounded_rectangle(
        [b_x - 3, b_y - 3, b_x + b_box_w + 3, b_y + b_box_h + 3],
        radius=14,
        fill=(255, 255, 255, 255),
    )
    # Badge background
    badge_draw.rounded_rectangle(
        [b_x, b_y, b_x + b_box_w, b_y + b_box_h],
        radius=12,
        fill=(*badge_bg, 255),
    )
    # Badge text
    badge_draw.text(
        (b_x + badge_pad_x, b_y + badge_pad_y - 2),
        badge_text,
        font=font,
        fill=(*badge_fg, 255),
    )

    final_canvas.save(out_path, format="PNG")
    print(f"✅ Đã tạo Sticker Meme: {out_path.name}")
    return out_path


# 10 Meme kinh điển kèm tiêu đề Wikimedia Commons chính xác
MEME_DEFINITIONS = [
    {
        "name": "vine_boom.png",
        "wiki_title": "File:Dwayne Johnson 2, 2013.jpg",
        "badge": "VINE BOOM 🤨",
        "bg": (230, 0, 40),
    },
    {
        "name": "bruh.png",
        "wiki_title": "File:Doge meme example.jpg",
        "badge": "BRUH 😐",
        "bg": (50, 50, 60),
    },
    {
        "name": "sad_trombone.png",
        "wiki_title": "File:Grumpy Cat by Gage Skidmore.jpg",
        "badge": "TOANG 😿",
        "bg": (100, 116, 139),
    },
    {
        "name": "quack.png",
        "wiki_title": "File:Clown face.jpg",
        "badge": "TẤU HÀI 🤡",
        "bg": (245, 158, 11),
    },
    {
        "name": "what.png",
        "wiki_title": "File:Shocked Cat.jpg",
        "badge": "WHAT?! 🙀",
        "bg": (255, 120, 0),
    },
    {
        "name": "huh.png",
        "wiki_title": "File:Baby Gibbon Surprised Face (20940604796).jpg",
        "badge": "HUH?! 🧐",
        "bg": (14, 165, 233),
    },
    {
        "name": "record_scratch.png",
        "wiki_title": "File:Doh.jpg",
        "badge": "SƯỢNG TRÂN ⏸️",
        "bg": (168, 85, 247),
    },
    {
        "name": "metal_pipe.png",
        "wiki_title": "File:Funny-faced bully cat (50539714923).jpg",
        "badge": "SẬP NGUỒN 💥",
        "bg": (220, 38, 38),
    },
    {
        "name": "emotional_damage.png",
        "wiki_title": "File:Paris Tuileries Garden Facepalm statue.jpg",
        "badge": "SÁT THƯƠNG 💔",
        "bg": (190, 24, 93),
    },
    {
        "name": "anime_wow.png",
        "wiki_title": "File:Shocked cat in the HSS.jpg",
        "badge": "ĐỈNH NÓC ✨",
        "bg": (16, 185, 129),
    },
]


def main():
    print(f"🚀 Bắt đầu tải và dựng 10 Meme Stickers tại: {MEMES_DIR}...")
    for item in MEME_DEFINITIONS:
        out_file = MEMES_DIR / item["name"]
        time.sleep(0.5)  # Tránh rate limit
        try:
            raw_bytes = fetch_commons_thumb(item["wiki_title"], width=500)
            create_meme_sticker(
                img_bytes=raw_bytes,
                out_path=out_file,
                badge_text=item["badge"],
                badge_bg=item["bg"],
            )
        except Exception as e:
            print(f"⚠️ Thử thách tải {item['wiki_title']}: {e}")
            if not out_file.exists():
                fallback_im = Image.new("RGBA", (340, 340), item["bg"])
                buf = io.BytesIO()
                fallback_im.save(buf, format="PNG")
                create_meme_sticker(
                    img_bytes=buf.getvalue(),
                    out_path=out_file,
                    badge_text=item["badge"],
                    badge_bg=item["bg"],
                )

    print("\n🎉 HOÀN TẤT THƯ VIỆN MEME STICKERS:")
    for f in sorted(MEMES_DIR.glob("*.png")):
        if f.name == "test_sticker.png":
            continue
        print(f" - {f.name}: {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()

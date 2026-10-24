#!/usr/bin/env python3
"""
OmniVideo Studio - Gate 6 & Publishing Kit High-CTR Thumbnail Generator
Generates high-converting thumbnails for 9:16 Shorts/TikTok/Threads and 16:9 YouTube/Cinematic.
Adheres strictly to Rule 11 of CINEMATIC_STANDARDS.md.
"""
import sys
import os
import json
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
BRANDING_DIR = BASE_DIR / "shared-assets" / "branding"

def get_font(name="arialbd.ttf", size=32):
    paths = [
        Path(f"C:/Windows/Fonts/{name}"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arial.ttf")
    ]
    for p in paths:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_text_with_stroke(draw, pos, text, font, fill_color, stroke_color, stroke_width):
    x, y = pos
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx*dx + dy*dy <= stroke_width * stroke_width:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    draw.text((x, y), text, font=font, fill=fill_color)

def generate_vertical_9x16_thumbnail(base_img_path: Path, out_path: Path, hook_text: str, badge_text: str = "🔥 THREADS VIRAL • HANSHIN", sub_text: str = None):
    target_w, target_h = 1080, 1920

    if not base_img_path.exists():
        raise FileNotFoundError(f"Base image not found: {base_img_path}")

    base_img = Image.open(base_img_path).convert("RGB")
    base_img = ImageOps.fit(base_img, (target_w, target_h), Image.Resampling.LANCZOS)

    # 1. Subtle contrast and saturation pop
    enhancer = ImageEnhance.Contrast(base_img)
    base_img = enhancer.enhance(1.12)
    enhancer_col = ImageEnhance.Color(base_img)
    base_img = enhancer_col.enhance(1.15)

    img = base_img.convert("RGBA")
    draw = ImageDraw.Draw(img)

    # 2. Top Header Gradient & Badge
    header_vignette = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(header_vignette)
    for y in range(0, 360):
        alpha = int((1.0 - (y / 360.0)) ** 1.4 * 180)
        hdraw.line([(0, y), (target_w, y)], fill=(8, 12, 22, alpha))
    img = Image.alpha_composite(img, header_vignette)
    draw = ImageDraw.Draw(img)

    # Avatar Logo in top left
    avatar_path = BRANDING_DIR / "hanshin_avatar.png"
    if not avatar_path.exists():
        avatar_path = BRANDING_DIR / "avatar.png"

    if avatar_path.exists():
        try:
            av = Image.open(avatar_path).convert("RGBA")
            av_size = 76
            av = av.resize((av_size, av_size), Image.Resampling.LANCZOS)
            # Circular mask
            mask = Image.new("L", (av_size, av_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, av_size, av_size), fill=255)
            # White outline circle
            draw.ellipse((48, 48, 48 + av_size + 4, 48 + av_size + 4), fill=(255, 255, 255, 230))
            img.paste(av, (50, 50), mask)
        except Exception as e:
            print(f"Lỗi paste avatar: {e}", file=sys.stderr)

    # Top Pill Badge
    font_badge = get_font("arialbd.ttf", 26)
    badge_box = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = badge_box[2] - badge_box[0]
    bx = 145
    by = 60
    draw.rounded_rectangle([(bx, by), (bx + bw + 36, by + 56)], radius=14, fill=(16, 22, 36, 230), outline=(255, 60, 120, 220), width=2)
    draw.text((bx + 18, by + 12), badge_text, font=font_badge, fill=(255, 240, 245, 255))

    # 3. High-CTR Hook Banner (Upper Center / Punchline Hook)
    if hook_text:
        # Wrap hook text into 1 or 2 lines max
        words = hook_text.strip().split()
        lines = []
        if len(words) <= 5:
            lines = [" ".join(words)]
        else:
            mid = len(words) // 2
            lines = [" ".join(words[:mid]), " ".join(words[mid:])]

        font_hook = get_font("arialbd.ttf", 52)
        line_height = 68
        total_text_h = len(lines) * line_height

        hook_center_y = 260
        # Calculate max line width
        max_lw = 0
        for l in lines:
            bb = draw.textbbox((0, 0), l, font=font_hook)
            lw = bb[2] - bb[0]
            if lw > max_lw:
                max_lw = lw

        pad_x = 44
        pad_y = 24
        banner_w = min(max_lw + pad_x * 2, 980)
        banner_x = (target_w - banner_w) // 2
        banner_y = hook_center_y - (total_text_h // 2) - pad_y

        # Floating Dark Glass Plate with Neon Cyan/Gold border
        draw.rounded_rectangle(
            [(banner_x, banner_y), (banner_x + banner_w, banner_y + total_text_h + pad_y * 2)],
            radius=20,
            fill=(10, 14, 24, 235),
            outline=(0, 229, 255, 230),
            width=3
        )

        # Draw lines of text
        curr_y = banner_y + pad_y
        for i, line in enumerate(lines):
            lbb = draw.textbbox((0, 0), line, font=font_hook)
            lw = lbb[2] - lbb[0]
            lx = (target_w - lw) // 2
            text_color = (255, 230, 0, 255) if i == 0 else (0, 245, 255, 255)
            draw_text_with_stroke(draw, (lx, curr_y), line, font_hook, text_color, (0, 0, 0, 255), 7)
            curr_y += line_height

    # 4. Save Final High-Quality JPG
    final_rgb = img.convert("RGB")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final_rgb.save(out_path, "JPEG", quality=95)
    return out_path

def generate_horizontal_16x9_thumbnail(base_img_path: Path, out_path: Path, hook_text: str, badge_text: str = "4K 60FPS CINEMATIC", sub_text: str = None):
    target_w, target_h = 1920, 1080

    if not base_img_path.exists():
        raise FileNotFoundError(f"Base image not found: {base_img_path}")

    base_img = Image.open(base_img_path).convert("RGB")
    base_img = ImageOps.fit(base_img, (target_w, target_h), Image.Resampling.LANCZOS)

    # Contrast & Color enhance
    enhancer = ImageEnhance.Contrast(base_img)
    base_img = enhancer.enhance(1.18)
    enhancer_col = ImageEnhance.Color(base_img)
    base_img = enhancer_col.enhance(1.22)

    # Bottom Gradient Vignette for dramatic cinematic look
    vignette = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for y in range(480, target_h):
        alpha = int(((y - 480) / (target_h - 480)) ** 1.3 * 230)
        vdraw.line([(0, y), (target_w, y)], fill=(6, 10, 20, alpha))

    img = Image.alpha_composite(base_img.convert("RGBA"), vignette)
    draw = ImageDraw.Draw(img)

    # Top Brand Pill
    font_pill = get_font("arialbd.ttf", 26)
    draw.rounded_rectangle([(60, 50), (460, 115)], radius=12, fill=(11, 18, 32, 230), outline=(0, 229, 255, 200), width=2)
    draw.text((85, 68), "OMNIVIDEO STUDIO • 2026", font=font_pill, fill=(0, 240, 255, 255))

    # Top Right Badge
    draw.rounded_rectangle([(target_w - 420, 50), (target_w - 60, 115)], radius=12, fill=(11, 18, 32, 230), outline=(255, 215, 0, 220), width=2)
    draw.text((target_w - 395, 68), "⚡ AI AUTONOMOUS", font=font_pill, fill=(255, 215, 0, 255))

    # Giant Hook Text (Bottom Center)
    if hook_text:
        words = hook_text.strip().split()
        lines = []
        if len(words) <= 6:
            lines = [" ".join(words)]
        else:
            mid = len(words) // 2
            lines = [" ".join(words[:mid]), " ".join(words[mid:])]

        font_hook = get_font("arialbd.ttf", 88)
        start_y = 700 if len(lines) == 2 else 780
        for i, line in enumerate(lines):
            bb = draw.textbbox((0, 0), line, font=font_hook)
            lw = bb[2] - bb[0]
            lx = (target_w - lw) // 2
            ly = start_y + (i * 110)
            text_color = (0, 245, 255, 255) if i == 0 else (255, 225, 0, 255)
            draw_text_with_stroke(draw, (lx, ly), line, font_hook, text_color, (0, 0, 0, 255), 8)

    # Save Final JPG
    final_rgb = img.convert("RGB")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final_rgb.save(out_path, "JPEG", quality=95)
    return out_path

def main():
    parser = argparse.ArgumentParser(description="OmniVideo High-CTR Thumbnail Generator")
    parser.add_argument("--base-image", required=True, help="Base frame image path")
    parser.add_argument("--output", required=True, help="Destination output jpg path")
    parser.add_argument("--hook", default="VIRAL THREADS 2026", help="Hook headline text")
    parser.add_argument("--workshop", default="threads", help="Workshop type (threads, cinematic, etc.)")
    parser.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"], help="Aspect ratio")
    parser.add_argument("--badge", default=None, help="Badge text")

    args = parser.parse_args()
    base_img = Path(args.base_image).resolve()
    out_path = Path(args.output).resolve()
    badge = args.badge or ("🔥 THREADS VIRAL • HANSHIN" if args.workshop == "threads" else "4K 60FPS CINEMATIC")

    try:
        if args.aspect == "9:16":
            result = generate_vertical_9x16_thumbnail(base_img, out_path, args.hook, badge)
        else:
            result = generate_horizontal_16x9_thumbnail(base_img, out_path, args.hook, badge)

        print(json.dumps({
            "success": True,
            "output": str(result),
            "message": "Đã sinh Thumbnail High-CTR thành công!"
        }, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
OmniVideo Studio - Gate 6 Cinematic 3D High-CTR Thumbnail Generator
Generates a stunning 1920x1080 3D thumbnail using Hero Shot of Bé Byte and Master Set 1.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-mcp-explained-7min"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
IMAGES_DIR = OUTPUT_DIR / "images"
BRANDING_DIR = BASE_DIR / "shared-assets" / "branding"
LOGO_PATH = BRANDING_DIR / "giaimatech_logo.png"
BRAIN_DIR = Path(r"C:\Users\tranh\.gemini\antigravity\brain\74745d7e-e139-4bc8-b6d1-fbc945ef19d8")

OUT_THUMB_JOB = OUTPUT_DIR / f"{JOB_ID}_thumb_3d.jpg"
OUT_THUMB_MASTER = BASE_DIR / "output" / "cinematic" / f"{JOB_ID}_thumb_3d.jpg"
OUT_THUMB_BRAIN = BRAIN_DIR / "thumbnail_3d_high_ctr.jpg"

def get_font(name="arialbd.ttf", size=32):
    paths = [
        Path(f"C:/Windows/Fonts/{name}"),
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
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
    # Draw stroke
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx*dx + dy*dy <= stroke_width * stroke_width:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill_color)

def main():
    print("🎨 Generating Cinematic 3D High-CTR Thumbnail for MCP 7-Min Film...")
    width, height = 1920, 1080

    # 1. Base 3D Hero Frame
    hero_frame = IMAGES_DIR / "shot_011.jpg"
    if not hero_frame.exists():
        hero_frame = IMAGES_DIR / "shot_001.jpg"

    base_img = Image.open(hero_frame).convert("RGB")
    # Resize and crop to 1920x1080
    base_img = base_img.resize((width, height), Image.Resampling.LANCZOS)

    # Enhance contrast and saturation for vibrant 3D look
    enhancer = ImageEnhance.Contrast(base_img)
    base_img = enhancer.enhance(1.18)
    enhancer_color = ImageEnhance.Color(base_img)
    base_img = enhancer_color.enhance(1.22)

    # 2. Add Dark Gradient Vignette at bottom for text legibility
    vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for y in range(450, height):
        alpha = int(((y - 450) / (height - 450)) ** 1.3 * 230)
        vdraw.line([(0, y), (width, y)], fill=(6, 10, 20, alpha))

    # Combine base + vignette
    img = Image.alpha_composite(base_img.convert("RGBA"), vignette)
    draw = ImageDraw.Draw(img)

    # 3. Channel Branding & Badges
    # Top Left: Logo + Channel Pill
    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo.thumbnail((90, 90), Image.Resampling.LANCZOS)
        img.paste(logo, (50, 45), logo)

    font_pill = get_font("arialbd.ttf", 24)
    # Channel badge
    draw.rounded_rectangle([(155, 55), (490, 115)], radius=12, fill=(11, 18, 32, 230), outline=(0, 229, 255, 200), width=2)
    draw.text((175, 72), "GIẢI MÃ TECH • TẬP 02", font=font_pill, fill=(0, 240, 255, 255))

    # Top Right: Theme Pill
    draw.rounded_rectangle([(width - 550, 55), (width - 50, 115)], radius=12, fill=(11, 18, 32, 230), outline=(255, 215, 0, 220), width=2)
    draw.text((width - 525, 72), "⚡ CHUẨN KẾT NỐI VẠN NĂNG 2026", font=font_pill, fill=(255, 215, 0, 255))

    # 4. High-CTR Hook Typography
    # Line 1: GIẢI MÃ MCP (Giant Cyan Neon)
    font_title1 = get_font("arialbd.ttf", 102)
    text1 = "GIẢI MÃ MCP"
    t1_box = draw.textbbox((0, 0), text1, font=font_title1)
    t1_w = t1_box[2] - t1_box[0]
    t1_x = (width - t1_w) // 2
    t1_y = 660

    # Glow under text 1
    glow1 = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw1 = ImageDraw.Draw(glow1)
    gdraw1.text((t1_x, t1_y), text1, font=font_title1, fill=(0, 229, 255, 120))
    glow1 = glow1.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img, glow1)
    draw = ImageDraw.Draw(img)

    draw_text_with_stroke(draw, (t1_x, t1_y), text1, font_title1, (0, 245, 255, 255), (0, 0, 0, 255), 8)

    # Line 2: CỔNG TYPE-C CỦA AI! (Bold Gold Neon)
    font_title2 = get_font("arialbd.ttf", 84)
    text2 = "CỔNG TYPE-C CỦA TRÍ TUỆ NHÂN TẠO!"
    t2_box = draw.textbbox((0, 0), text2, font=font_title2)
    t2_w = t2_box[2] - t2_box[0]
    t2_x = (width - t2_w) // 2
    t2_y = 780

    # Glow under text 2
    glow2 = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw2 = ImageDraw.Draw(glow2)
    gdraw2.text((t2_x, t2_y), text2, font=font_title2, fill=(255, 215, 0, 110))
    glow2 = glow2.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(img, glow2)
    draw = ImageDraw.Draw(img)

    draw_text_with_stroke(draw, (t2_x, t2_y), text2, font_title2, (255, 225, 0, 255), (0, 0, 0, 255), 8)

    # Sub-hook Backplate (Bottom Center)
    font_sub = get_font("arialbd.ttf", 30)
    sub_text = "NỐI MỌI DATABASE & TOOL TRONG 5 PHÚT • FAST-MCP PYTHON CODE DEMO"
    sub_box = draw.textbbox((0, 0), sub_text, font=font_sub)
    sub_w = sub_box[2] - sub_box[0]
    sub_x = (width - sub_w) // 2
    sub_y = 905

    draw.rounded_rectangle([(sub_x - 30, sub_y - 12), (sub_x + sub_w + 30, sub_y + 48)], radius=14, fill=(10, 15, 26, 235), outline=(0, 229, 255, 160), width=2)
    draw.text((sub_x, sub_y), sub_text, font=font_sub, fill=(255, 255, 255, 255))

    # Bottom Right Tech Pill: 4K 60FPS CINEMATIC
    draw.rounded_rectangle([(width - 320, height - 75), (width - 50, height - 25)], radius=10, fill=(0, 229, 255, 240))
    font_badge = get_font("arialbd.ttf", 20)
    draw.text((width - 300, height - 63), "4K 60FPS CINEMATIC", font=font_badge, fill=(8, 12, 22, 255))

    # Save to all required destinations
    final_rgb = img.convert("RGB")
    final_rgb.save(OUT_THUMB_JOB, "JPEG", quality=95)
    final_rgb.save(OUT_THUMB_MASTER, "JPEG", quality=95)
    final_rgb.save(OUT_THUMB_BRAIN, "JPEG", quality=95)
    print(f"✅ Thumbnail 3D saved: {OUT_THUMB_JOB}")
    print(f"✅ Thumbnail 3D saved: {OUT_THUMB_MASTER}")
    print(f"✅ Thumbnail 3D saved: {OUT_THUMB_BRAIN}")

if __name__ == "__main__":
    main()

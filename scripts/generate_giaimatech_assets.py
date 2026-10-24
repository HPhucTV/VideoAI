import os
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
THUMBNAILS_DIR = OUTPUT_DIR / "thumbnails"
CINEMATIC_DIR = OUTPUT_DIR / "cinematic"
SHARED_BRANDING = BASE_DIR / "shared-assets" / "branding"

THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
CINEMATIC_DIR.mkdir(parents=True, exist_ok=True)

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

def create_hero_thumbnail(width=1920, height=1080):
    print("🎨 Đang kết xuất Thumbnail 1 (Hero - 1920x1080)...")
    img = Image.new("RGBA", (width, height), (10, 14, 26, 255))
    draw = ImageDraw.Draw(img)

    # Ambient gradients
    draw.rectangle([(0, 0), (width, height)], fill=(9, 13, 24, 255))
    draw.ellipse([(-150, -150), (950, 950)], fill=(0, 160, 255, 45))
    draw.ellipse([(width - 850, height - 750), (width + 300, height + 300)], fill=(255, 170, 0, 30))
    draw.ellipse([(width//2 - 200, -200), (width//2 + 600, 600)], fill=(0, 230, 200, 25))

    # Tech grid lines (subtle)
    for x in range(0, width, 120):
        draw.line([(x, 0), (x, height)], fill=(0, 229, 255, 12), width=1)
    for y in range(0, height, 120):
        draw.line([(0, y), (width, y)], fill=(0, 229, 255, 12), width=1)

    # Outer Cyber border
    draw.rectangle([(30, 30), (width - 30, height - 30)], outline=(0, 229, 255, 130), width=3)
    draw.rectangle([(42, 42), (width - 42, height - 42)], outline=(255, 179, 0, 70), width=1)

    # Tech brackets on corners
    corner_sz = 60
    c_color = (0, 229, 255, 230)
    for (cx, cy) in [(30, 30), (width - 30, 30), (30, height - 30), (width - 30, height - 30)]:
        dx = -1 if cx > width/2 else 1
        dy = -1 if cy > height/2 else 1
        draw.line([(cx, cy), (cx + dx * corner_sz, cy)], fill=c_color, width=5)
        draw.line([(cx, cy), (cx, cy + dy * corner_sz)], fill=c_color, width=5)

    # Right side: Visual Art / Tech Display
    tech_box_w, tech_box_h = 880, 840
    tech_box_x = width - tech_box_w - 70
    tech_box_y = (height - tech_box_h) // 2

    draw.rounded_rectangle(
        [(tech_box_x, tech_box_y), (tech_box_x + tech_box_w, tech_box_y + tech_box_h)],
        radius=28,
        fill=(14, 22, 40, 230),
        outline=(0, 229, 255, 180),
        width=3
    )

    # Drawing inner network graphic inside tech box
    cx_box = tech_box_x + tech_box_w // 2
    cy_box = tech_box_y + tech_box_h // 2 - 40

    # Concentric glowing rings
    for r in [260, 190, 120]:
        draw.ellipse([(cx_box - r, cy_box - r), (cx_box + r, cy_box + r)], outline=(0, 229, 255, 70), width=2)

    # Center glowing Core
    draw.ellipse([(cx_box - 70, cy_box - 70), (cx_box + 70, cy_box + 70)], fill=(0, 229, 255, 210), outline=(255, 255, 255, 255), width=4)
    font_core = get_font("arialbd.ttf", 30)
    cb = draw.textbbox((0, 0), "LLM", font=font_core)
    cw = cb[2] - cb[0]
    draw.text((cx_box - cw//2, cy_box - 18), "LLM", fill=(10, 20, 35, 255), font=font_core)

    # Satellites (Tools) connected by neon lines
    satellites = [
        ("🌐 Web Tool", cx_box - 210, cy_box - 160, (0, 229, 255, 220)),
        ("💻 Terminal", cx_box + 210, cy_box - 160, (255, 179, 0, 220)),
        ("📁 File Writer", cx_box - 230, cy_box + 140, (120, 255, 180, 220)),
        ("⚡ API Runner", cx_box + 230, cy_box + 140, (255, 110, 200, 220)),
        ("👤 Human Loop", cx_box, cy_box + 240, (255, 230, 100, 220))
    ]

    font_sat = get_font("arialbd.ttf", 26)
    for (label, sx, sy, scolor) in satellites:
        # connecting ray
        draw.line([(cx_box, cy_box), (sx, sy)], fill=(0, 229, 255, 120), width=2)
        sb = draw.textbbox((0, 0), label, font=font_sat)
        sw = sb[2] - sb[0]
        sh = sb[3] - sb[1]
        draw.rounded_rectangle([(sx - sw//2 - 16, sy - sh//2 - 10), (sx + sw//2 + 16, sy + sh//2 + 10)], radius=12, fill=(12, 18, 32, 240), outline=scolor, width=2)
        draw.text((sx - sw//2, sy - sh//2 - 2), label, fill=scolor, font=font_sat)

    # Label on tech box
    font_sub_tech = get_font("arialbd.ttf", 26)
    st_text = "HỆ THỐNG TỰ ĐIỀU PHỐI TỰ CHỦ (VEO 2 / FLOWKIT)"
    stb = draw.textbbox((0, 0), st_text, font=font_sub_tech)
    stw = stb[2] - stb[0]
    draw.text((cx_box - stw//2, tech_box_y + tech_box_h - 60), st_text, fill=(200, 230, 255, 200), font=font_sub_tech)

    # Left Side: Typography & Brand
    # 1. Brand Logo
    logo_file = SHARED_BRANDING / "giaimatech_logo.png"
    if logo_file.exists():
        logo = Image.open(logo_file).convert("RGBA").resize((95, 95), Image.Resampling.LANCZOS)
        img.paste(logo, (90, 75), mask=logo)

    font_brand = get_font("arialbd.ttf", 36)
    draw.text((205, 105), "GIẢI MÃ TECH", fill=(255, 255, 255, 255), font=font_brand)

    # 2. Pill Tag
    font_pill = get_font("arialbd.ttf", 24)
    p_text = "⚡ KỶ NGUYÊN TỰ CHỦ 2026"
    pb = draw.textbbox((0, 0), p_text, font=font_pill)
    pw = pb[2] - pb[0]
    draw.rounded_rectangle([(90, 205), (90 + pw + 36, 258)], radius=12, fill=(255, 179, 0, 240))
    draw.text((108, 218), p_text, fill=(15, 15, 15, 255), font=font_pill)

    # 3. Main Headline
    font_h1 = get_font("arialbd.ttf", 102)
    font_h2 = get_font("arialbd.ttf", 54)

    # Shadow + Main text
    draw.text((95, 285), "AI AGENT", fill=(0, 0, 0, 240), font=font_h1)
    draw.text((90, 280), "AI AGENT", fill=(0, 229, 255, 255), font=font_h1)

    draw.text((95, 400), "LÀ GÌ?", fill=(0, 0, 0, 240), font=font_h1)
    draw.text((90, 395), "LÀ GÌ?", fill=(255, 255, 255, 255), font=font_h1)

    # 4. Punchline
    draw.text((90, 520), "KHI AI KHÔNG CHỈ TRẢ LỜI", fill=(255, 210, 100, 255), font=font_h2)
    draw.text((90, 585), "MÀ BIẾT HÀNH ĐỘNG!", fill=(0, 255, 180, 255), font=font_h2)

    # 5. Badges
    font_badge = get_font("arialbd.ttf", 28)
    badges = [
        ("🧠 Tự Lập Kế Hoạch Đa Bước", (0, 229, 255, 240)),
        ("🛠️ Tự Gọi Tool & Sửa Lỗi", (255, 179, 0, 240)),
        ("⚡ Demo Docker Thực Tế", (120, 255, 180, 240))
    ]
    by = 680
    for text_b, color_b in badges:
        tb = draw.textbbox((0, 0), text_b, font=font_badge)
        tw = tb[2] - tb[0]
        draw.rounded_rectangle([(90, by), (90 + tw + 36, by + 56)], radius=12, fill=(18, 28, 48, 240), outline=color_b, width=2)
        draw.text((108, by + 12), text_b, fill=(255, 255, 255, 255), font=font_badge)
        by += 72

    out_file = THUMBNAILS_DIR / "thumb_01_hero_giaimatech.jpg"
    img.convert("RGB").save(out_file, "JPEG", quality=95)
    img.convert("RGB").save(CINEMATIC_DIR / "thumb_hero_16x9.jpg", "JPEG", quality=95)
    print(f"  ✅ Đã lưu: {out_file.name}")
    return out_file

def create_vs_thumbnail(width=1920, height=1080):
    print("🎨 Đang kết xuất Thumbnail 2 (So sánh Chatbot vs AI Agent - 1920x1080)...")
    img = Image.new("RGBA", (width, height), (12, 16, 28, 255))
    draw = ImageDraw.Draw(img)

    # Split background
    draw.rectangle([(0, 0), (width//2, height)], fill=(28, 16, 22, 255))
    draw.rectangle([(width//2, 0), (width, height)], fill=(12, 28, 42, 255))

    # Divider glowing line
    draw.line([(width//2, 0), (width//2, height)], fill=(0, 229, 255, 200), width=4)
    draw.rectangle([(30, 30), (width - 30, height - 30)], outline=(255, 179, 0, 120), width=3)

    # Brand top left
    logo_file = SHARED_BRANDING / "giaimatech_logo.png"
    if logo_file.exists():
        logo = Image.open(logo_file).convert("RGBA").resize((80, 80), Image.Resampling.LANCZOS)
        img.paste(logo, (70, 60), mask=logo)
    font_brand = get_font("arialbd.ttf", 30)
    draw.text((165, 85), "GIẢI MÃ TECH", fill=(255, 255, 255, 255), font=font_brand)

    # Header Center
    font_top = get_font("arialbd.ttf", 38)
    top_t = "PHÂN BIỆT RÕ RÀNG: BẠN ĐANG DÙNG LOẠI NÀO?"
    ttb = draw.textbbox((0, 0), top_t, font=font_top)
    ttw = ttb[2] - ttb[0]
    draw.text(((width - ttw)//2, 75), top_t, fill=(255, 215, 0, 255), font=font_top)

    # LEFT SIDE: CHATBOT
    font_col_title = get_font("arialbd.ttf", 82)
    font_item = get_font("arialbd.ttf", 36)

    draw.text((100, 180), "CHATBOT", fill=(255, 85, 85, 255), font=font_col_title)
    draw.text((100, 280), "TRUYỀN THỐNG", fill=(240, 180, 180, 255), font=get_font("arialbd.ttf", 40))

    left_items = [
        "❌ Chỉ biết 'NÓI MỒM', sinh chữ",
        "❌ Bạn vẫn phải tự mở trình duyệt",
        "❌ Bạn phải tự đọc và viết báo cáo",
        "❌ Không kết nối được công cụ máy tính",
        "❌ Quên mục tiêu khi hội thoại dài"
    ]
    iy = 370
    for item in left_items:
        draw.rounded_rectangle([(100, iy), (width//2 - 80, iy + 65)], radius=14, fill=(45, 20, 26, 230), outline=(255, 85, 85, 120), width=1)
        draw.text((120, iy + 14), item, fill=(255, 220, 220, 255), font=font_item)
        iy += 85

    # RIGHT SIDE: AI AGENT
    draw.text((width//2 + 90, 180), "AI AGENT", fill=(0, 229, 255, 255), font=font_col_title)
    draw.text((width//2 + 90, 280), "THẾ HỆ MỚI 2026", fill=(180, 240, 255, 255), font=get_font("arialbd.ttf", 40))

    right_items = [
        "✅ TỰ ĐIỀU PHỐI mọi hành động",
        "✅ Tự mở Web, đọc tài liệu chính thống",
        "✅ Tự xuất file Markdown hoàn chỉnh",
        "✅ Tự sửa lỗi và gọi thêm API",
        "✅ Bạn thảnh thơi giám sát kết quả!"
    ]
    iy = 370
    for item in right_items:
        draw.rounded_rectangle([(width//2 + 90, iy), (width - 90, iy + 65)], radius=14, fill=(16, 38, 56, 230), outline=(0, 229, 255, 140), width=1)
        draw.text((width//2 + 110, iy + 14), item, fill=(220, 255, 245, 255), font=font_item)
        iy += 85

    # Center VS Badge
    center_x = width // 2
    center_y = height // 2 - 20
    draw.ellipse([(center_x - 75, center_y - 75), (center_x + 75, center_y + 75)], fill=(255, 179, 0, 255), outline=(255, 255, 255, 255), width=4)
    font_vs = get_font("arialbd.ttf", 58)
    draw.text((center_x - 42, center_y - 36), "VS", fill=(10, 15, 25, 255), font=font_vs)

    # Bottom Banner
    font_banner = get_font("arialbd.ttf", 44)
    b_text = "TƯƠNG LAI CỦA TRÍ TUỆ NHÂN TẠO LÀ HÀNH ĐỘNG!"
    bb = draw.textbbox((0, 0), b_text, font=font_banner)
    bw = bb[2] - bb[0]
    draw.rounded_rectangle([((width - bw)//2 - 35, height - 165), ((width + bw)//2 + 35, height - 85)], radius=20, fill=(0, 229, 255, 240))
    draw.text(((width - bw)//2, height - 148), b_text, fill=(10, 20, 35, 255), font=font_banner)

    out_file = THUMBNAILS_DIR / "thumb_02_vs_comparison_giaimatech.jpg"
    img.convert("RGB").save(out_file, "JPEG", quality=95)
    img.convert("RGB").save(CINEMATIC_DIR / "thumb_vs_16x9.jpg", "JPEG", quality=95)
    print(f"  ✅ Đã lưu: {out_file.name}")
    return out_file

def update_publishing_kit_json():
    print("📋 Đang cập nhật output/publishing_kit.json chuẩn kênh GIẢI MÃ TECH...")
    kit = {
        "channel": "Giải Mã Tech",
        "channel_handle": "@giaimatech-s8t",
        "branding": {
            "logo": "shared-assets/branding/giaimatech_logo.png",
            "intro_video": "shared-assets/branding/intro_horizontal_16x9.mp4",
            "outro_video": "shared-assets/branding/outro_horizontal_16x9.mp4",
            "intro_duration": 2.0,
            "outro_duration": 4.5,
            "format": "16:9 Landscape (1920x1080 @ 60fps)",
            "audio_spec": "48,000 Hz, Stereo 2 Channels, AAC 192kbps"
        },
        "target_duration": "10:00",
        "video_title_options": [
            {
                "id": "seo_primary",
                "type": "Chuẩn SEO YouTube (Đề xuất số 1)",
                "title": "AI Agent Là Gì? Khi AI Không Chỉ Trả Lời Mà Còn Biết Hành Động | Giải Mã Tech",
                "score": "9.8/10",
                "notes": "Chứa đủ từ khóa vàng: AI Agent, Chatbot, Tự Động Hóa, Kênh Giải Mã Tech"
            },
            {
                "id": "viral_hook",
                "type": "Viral & Tò Mò (Click-Through-Rate cao)",
                "title": "Đừng Dùng Chatbot Như Cũ Nữa! AI Agent Mới Là Thứ Thay Đổi Cuộc Chơi 2026",
                "score": "9.4/10",
                "notes": "Tạo sự kích thích tâm lý, thúc đẩy click xem ngay"
            },
            {
                "id": "tech_deep_dive",
                "type": "Kỹ thuật Chuyên sâu (Học sinh, Sinh viên IT)",
                "title": "Giải Mã Kiến Trúc AI Agent: Vòng Lặp Vận Hành, Tools Và Demo Docker Thực Tế",
                "score": "9.2/10",
                "notes": "Nhấn mạnh bản chất kiến trúc và demo kiểm chứng thực tế"
            },
            {
                "id": "comparison",
                "type": "So sánh Đối đầu Trực diện",
                "title": "Chatbot vs AI Agent Khác Nhau Thế Nào? Vì Sao AI Nói Nhiều Sắp Bị Thay Thế?",
                "score": "9.1/10",
                "notes": "Đánh thẳng vào sự so sánh mà mọi người đang nhầm lẫn"
            }
        ],
        "timestamps": [
            {"time": "00:00", "title": "Intro Kênh Giải Mã Tech & Hook: Khi AI Bắt Đầu Hành Động"},
            {"time": "00:40", "title": "Chatbot Khác AI Agent Ở Đâu? (Hỏi - Đáp vs Tự Điều Phối)"},
            {"time": "01:50", "title": "Bên Trong AI Agent Có Gì? (Brain, Rules, Tools)"},
            {"time": "03:20", "title": "Demo Thực Tế: Giao Nhiệm Vụ Nghiên Cứu Docker Cho Agent"},
            {"time": "05:50", "title": "Giải Mã Vòng Lặp Thực Thi (Thought - Action - Observation Loop)"},
            {"time": "07:10", "title": "3 Ứng Dụng Thực Tế & Ranh Giới Nguy Hiểm Cần Kiểm Soát"},
            {"time": "08:40", "title": "Góc Nhìn Kiến Trúc: Khi Nào Nên Dùng Agent, Khi Nào Không?"},
            {"time": "09:35", "title": "Tổng Kết & Teaser Tập Tiếp Theo: Giải Mã MCP (Model Context Protocol)"}
        ],
        "youtube_description": (
            "🤖 Bạn đã từng hỏi AI cách làm một việc, nhận được câu trả lời chi tiết nhưng cuối cùng vẫn phải tự tay làm hết?\n\n"
            "Chào mừng bạn đến với GIẢI MÃ TECH! Trong video hôm nay, chúng ta sẽ cùng bóc tách một khái niệm đang định hình lại toàn bộ nền công nghệ: AI AGENT.\n\n"
            "Không chỉ dừng lại ở lý thuyết suông hay những lời khẳng định phóng đại, video này sẽ đưa bạn đi từ bản chất kiến trúc, giải mã sự khác biệt giữa Chatbot và Agent, quan sát một bản DEMO THỰC TẾ nghiên cứu tài liệu Docker, cho đến cách phòng tránh những rủi ro khi cấp quyền cho AI.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⏱️ NỘI DUNG TỪNG PHẦN (TIMESTAMPS):\n"
            "00:00 - Khi AI bắt đầu hành động\n"
            "00:40 - Chatbot thường khác AI Agent như thế nào?\n"
            "01:50 - 3 Trụ cột bên trong AI Agent: LLM, Instructions & Tools\n"
            "03:20 - Demo thực tế: Agent tự động nghiên cứu Docker & xuất Markdown\n"
            "05:50 - Vòng lặp hành động: Thought - Action - Observation Loop\n"
            "07:10 - Ứng dụng thực tế & Rủi ro khi cấp quyền quá rộng\n"
            "08:40 - Góc nhìn kiến trúc: Có phải việc gì cũng cần Agent?\n"
            "09:35 - Lời khuyên cho sinh viên IT & Teaser tập MCP\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📚 NGUỒN TÀI LIỆU KỸ THUẬT THAM KHẢO:\n"
            "• OpenAI - Defining & Running Agents: https://developers.openai.com/api/docs/guides/agents\n"
            "• Anthropic - Building Effective Agents: https://www.anthropic.com/engineering/building-effective-agents\n"
            "• Docker Documentation - Official Guides: https://docs.docker.com/get-started/\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Đăng ký kênh GIẢI MÃ TECH để cùng khám phá những công nghệ AI, Cloud và kiến trúc phần mềm mới nhất một cách thực chiến và khách quan!\n\n"
            "👉 Nhấn LIKE video nếu nội dung hữu ích, để lại bình luận góc nhìn của bạn, và đón chờ tập tiếp theo: 'MCP (Model Context Protocol) Là Gì?' nhé!"
        ),
        "tags": [
            "AI Agent",
            "AI Agent là gì",
            "Giải Mã Tech",
            "Chatbot vs AI Agent",
            "Trí tuệ nhân tạo 2026",
            "Tự động hóa",
            "Docker demo",
            "LLM Tools",
            "Model Context Protocol",
            "Anthropic Agents",
            "OpenAI Agents",
            "Công nghệ thông tin",
            "Học lập trình"
        ],
        "thumbnails": {
            "hero_thumbnail": "output/thumbnails/thumb_01_hero_giaimatech.jpg",
            "vs_thumbnail": "output/thumbnails/thumb_02_vs_comparison_giaimatech.jpg",
            "aspect_ratio": "16:9",
            "resolution": "1920x1080",
            "color_palette": "Cyber Navy, Neon Cyan, Electric Gold"
        }
    }

    kit_path = OUTPUT_DIR / "publishing_kit.json"
    with open(kit_path, "w", encoding="utf-8") as f:
        json.dump(kit, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Đã lưu publishing kit: {kit_path}")

if __name__ == "__main__":
    t1 = create_hero_thumbnail()
    t2 = create_vs_thumbnail()
    update_publishing_kit_json()
    print("\n🎉 TOÀN BỘ TƯ LIỆU XUẤT BẢN CHO GIẢI MÃ TECH ĐÃ HOÀN TẤT!")

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min"
STORYBOARD_DIR = OUTPUT_DIR / "storyboard"
STORYBOARD_DIR.mkdir(parents=True, exist_ok=True)
BRANDING_DIR = BASE_DIR / "shared-assets" / "branding"

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

SCENES_DATA = [
    {
        "order": 1,
        "title": "CẢNH 1: HOOK — MỞ ĐẦU KHÔNG GIAN ẢO",
        "badge": "00:00 - 00:40 • GIỚI THIỆU AI AGENT",
        "screen_title": "VIRTUAL HIGH-TECH LAB • TERMINAL & WORKSPACE",
        "screen_content": [
            "⚡ SYSTEM: AI Agent Core Initialized",
            "🌐 TASK: Nghiên cứu công nghệ tự động hóa 2026",
            "📁 STATUS: Tự động điều phối công cụ ngoại vi...",
            "💬 CHATBOT: Chỉ trả lời văn bản thụ động",
            "🚀 AGENT: Tự phân tích, truy xuất dữ liệu & ghi file"
        ],
        "accent": (0, 229, 255)
    },
    {
        "order": 2,
        "title": "CẢNH 2: SO SÁNH CHATBOT vs AI AGENT",
        "badge": "00:40 - 01:50 • ĐẤU TRƯỜNG CÔNG NGHỆ",
        "screen_title": "SPLIT-SCREEN COMPARISON VIEWPORT",
        "screen_content": [
            "[TRÁI: CHATBOT THỤ ĐỘNG]          [PHẢI: AI AGENT TỰ CHỦ]",
            "❌ Chỉ sinh chuỗi văn bản            ✅ Tự lập kế hoạch đa bước",
            "❌ Người dùng phải tự làm hết        ✅ Tự mở Web & trích xuất",
            "❌ Không tương tác hệ thống          ✅ Tự chạy terminal & ghi file",
            "👉 ĐÁNH GIÁ: 'Nói nhiều'             👉 ĐÁNH GIÁ: 'Biết hành động'"
        ],
        "accent": (255, 179, 0)
    },
    {
        "order": 3,
        "title": "CẢNH 3: 3 TRỤ CỘT KIẾN TRÚC AGENT",
        "badge": "01:50 - 03:20 • SƠ ĐỒ HỆ THỐNG 3 CHIỀU",
        "screen_title": "3D ARCHITECTURE BLUEPRINT (EXPANDED 70%)",
        "screen_content": [
            "🧠 KHỐI 1: LLM BRAIN (Mô hình suy luận & phân tách bài toán)",
            "🛡️ KHỐI 2: INSTRUCTIONS & GUARDRAILS (Ranh giới an toàn)",
            "🛠️ KHỐI 3: TOOLS & APIS (Đôi tay: Web, Terminal, File Writer)",
            "💾 PHẦN MỞ RỘNG: Vector Memory & Human Approval Gate",
            "🔗 LIÊN KẾT: Luồng dữ liệu khép kín tự sửa lỗi"
        ],
        "accent": (0, 255, 180)
    },
    {
        "order": 4,
        "title": "CẢNH 4: DEMO THỰC TẾ — NGHIÊN CỨU DOCKER",
        "badge": "03:20 - 05:50 • MÀN HÌNH 3D PHÓNG ĐẠI CỰC ĐẠI (75%)",
        "screen_title": "LIVE DEMO VIEWPORT: docs.docker.com & REPORT",
        "screen_content": [
            "🌐 BROWSER TAB: https://docs.docker.com/get-started/",
            "🔍 BÓC TÁCH 5 KHÁI NIỆM: Container, Image, Dockerfile, Compose, Volume",
            "📝 OUTPUT FILE: workspace/docker-basics.md",
            "✅ VERIFICATION: 100% đối chiếu nguồn chính thức, không hallucination",
            "👤 USER ROLE: Quan sát trực quan & thảnh thơi kiểm tra báo cáo"
        ],
        "accent": (0, 229, 255)
    },
    {
        "order": 5,
        "title": "CẢNH 5: VÒNG LẶP THỰC THI (THE AGENT LOOP)",
        "badge": "05:50 - 07:10 • CHU TRÌNH SUY LUẬN & HÀNH ĐỘNG",
        "screen_title": "CYCLICAL REASONING LOOP: THOUGHT - ACTION - OBSERVATION",
        "screen_content": [
            "[1. NHẬN NHIỆM VỤ] ──► [2. LLM SUY LUẬN & CHỌN CÔNG CỤ]",
            "          ▲                              │",
            "          │                              ▼",
            "[4. ĐÁNH GIÁ ĐẦU RA] ◄── [3. GỌI API & NHẬN KẾT QUẢ]",
            "⚠️ ĐIỀU KIỆN DỪNG: Đạt mục tiêu / Hết số bước / Cần Human Approval"
        ],
        "accent": (255, 110, 200)
    },
    {
        "order": 6,
        "title": "CẢNH 6: ỨNG DỤNG & RANH GIỚI BẢO MẬT",
        "badge": "07:10 - 08:40 • SANDBOX AN TOÀN & GIỚI HẠN",
        "screen_title": "SECURITY SHIELD & PERMISSION CONTROLS",
        "screen_content": [
            "🚀 3 ỨNG DỤNG MẠNH NHẤT: Lập trình - Nghiên cứu - Tự động hóa",
            "⚠️ NGUY CƠ: Hiểu sai lệnh, gọi nhầm API, xóa dữ liệu nhạy cảm",
            "🛡️ HÀNG RÀO BẢO VỆ: Cấp quyền tối thiểu (Least Privilege)",
            "🛑 HUMAN CHECKPOINT: Xác nhận trước khi gửi email / thanh toán",
            "💡 NGUYÊN TẮC: Agent hoàn thành tốt nhiệm vụ TRONG TẦM KIỂM SOÁT"
        ],
        "accent": (255, 80, 80)
    },
    {
        "order": 7,
        "title": "CẢNH 7: MA TRẬN QUYẾT ĐỊNH KIẾN TRÚC",
        "badge": "08:40 - 09:35 • KHI NÀO NÊN DÙNG AGENT?",
        "screen_title": "SYSTEM ARCHITECTURE DECISION MATRIX",
        "screen_content": [
            "📌 BÀI TOÁN ĐƠN GIẢN / PHÂN LOẠI   ──► Dùng Single Model Call",
            "📌 QUY TRÌNH NGHIỆP VỤ CỐ ĐỊNH     ──► Dùng Rule-based Workflow",
            "📌 NHIỆM VỤ ĐA BƯỚC / TỰ SỬA LỖI   ──► DÙNG AI AGENT LINH HOẠT",
            "⚖️ ĐÁNH ĐỔI: Linh hoạt cao = Chi phí token cao + Cần kiểm soát chặt",
            "🔑 LỜI KHUYÊN ANTHROPIC: 'Bắt đầu với giải pháp đơn giản nhất!'"
        ],
        "accent": (255, 215, 0)
    },
    {
        "order": 8,
        "title": "CẢNH 8: TỔNG KẾT & KÊU GỌI HÀNH ĐỘNG (CTA)",
        "badge": "09:35 - 10:00 • KẾT THÚC & TEASER TẬP TIẾP THEO",
        "screen_title": "GIẢI MÃ TECH OUTRO & NEXT EPISODE TEASER",
        "screen_content": [
            "🏆 TỔNG KẾT: AI Agent = Trí tuệ LLM + Đôi tay Công cụ",
            "🔔 ĐĂNG KÝ KÊNH: Giải Mã Tech (@giaimatech-s8t)",
            "📺 TẬP TIẾP THEO: Giải Mã MCP (Model Context Protocol)",
            "🤝 KẾT NỐI: Cảm ơn các bạn đã theo dõi video!",
            "🎬 MASTER FILM CHUẨN ĐIỆN ẢNH: 1920x1080 @ 60 FPS"
        ],
        "accent": (0, 229, 255)
    }
]

def render_storyboard_frame(scene, width=1920, height=1080):
    img = Image.new("RGBA", (width, height), (10, 14, 25, 255))
    draw = ImageDraw.Draw(img)

    order = scene["order"]
    accent = scene["accent"]

    # 1. Background Grid & Tech Ambiance
    draw.rectangle([(0, 0), (width, height)], fill=(9, 13, 24, 255))
    draw.ellipse([(-100, -100), (800, 800)], fill=(0, 150, 255, 30))
    draw.ellipse([(width - 800, height - 700), (width + 300, height + 300)], fill=(accent[0], accent[1], accent[2], 25))

    for x in range(0, width, 120):
        draw.line([(x, 0), (x, height)], fill=(0, 229, 255, 12), width=1)
    for y in range(0, height, 120):
        draw.line([(0, y), (width, y)], fill=(0, 229, 255, 12), width=1)

    # 2. Header Bar: Channel & Scene Title
    logo_file = BRANDING_DIR / "giaimatech_logo.png"
    if logo_file.exists():
        logo = Image.open(logo_file).convert("RGBA").resize((70, 70), Image.Resampling.LANCZOS)
        img.paste(logo, (50, 45), mask=logo)

    font_brand = get_font("arialbd.ttf", 26)
    draw.text((135, 52), "GIẢI MÃ TECH • STORYBOARD BOARD (CỔNG 5)", fill=(255, 255, 255, 255), font=font_brand)

    font_badge = get_font("arialbd.ttf", 20)
    draw.rounded_rectangle([(width - 450, 50), (width - 50, 95)], radius=10, fill=(20, 32, 54, 220), outline=accent, width=1)
    draw.text((width - 430, 62), scene["badge"], fill=accent, font=font_badge)

    # Main Scene Title Banner
    font_title = get_font("arialbd.ttf", 36)
    draw.text((50, 130), scene["title"], fill=(255, 255, 255, 255), font=font_title)

    # 3. GIANT 3D HOLOGRAPHIC FLOATING DISPLAY (Chiếm 72% chiều cao & 85% chiều rộng)
    screen_x = 50
    screen_y = 190
    screen_w = width - 100
    screen_h = height - 260

    # Screen backplate with holographic glass effect
    draw.rounded_rectangle(
        [(screen_x, screen_y), (screen_x + screen_w, screen_y + screen_h)],
        radius=24,
        fill=(14, 22, 38, 235),
        outline=accent,
        width=3
    )

    # Screen Title Bar
    draw.rounded_rectangle(
        [(screen_x, screen_y), (screen_x + screen_w, screen_y + 60)],
        radius=20,
        fill=(20, 35, 60, 240)
    )
    # macOS / Terminal control buttons
    for idx, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse([(screen_x + 25 + idx * 26, screen_y + 22), (screen_x + 39 + idx * 26, screen_y + 36)], fill=c)

    font_scr_title = get_font("arialbd.ttf", 22)
    draw.text((screen_x + 130, screen_y + 18), f"MÀN HÌNH NỔI 3D PHÒNG LAB // {scene['screen_title']}", fill=(220, 240, 255, 255), font=font_scr_title)

    # Screen Content Lines (Phóng to, chữ lớn sắc nét theo yêu cầu người dùng)
    font_content = get_font("arialbd.ttf", 32)
    font_subline = get_font("arial.ttf", 26)

    cy = screen_y + 95
    for line in scene["screen_content"]:
        # Line indicator dot
        draw.ellipse([(screen_x + 40, cy + 10), (screen_x + 52, cy + 22)], fill=accent)
        draw.text((screen_x + 70, cy), line, fill=(245, 250, 255, 255), font=font_content)
        cy += 70

    # 4. Avatar Mascot "Bé Byte" Badge at Bottom Right
    byte_box_w = 420
    byte_box_h = 75
    bx = screen_x + screen_w - byte_box_w - 30
    by = screen_y + screen_h - byte_box_h - 25

    draw.rounded_rectangle([(bx, by), (bx + byte_box_w, by + byte_box_h)], radius=16, fill=(10, 18, 30, 240), outline=(0, 229, 255, 180), width=2)
    draw.ellipse([(bx + 15, by + 15), (bx + 60, by + 60)], fill=(0, 229, 255, 220))
    font_byte_icon = get_font("arialbd.ttf", 22)
    draw.text((bx + 26, by + 24), "🤖", fill=(10, 20, 30, 255), font=font_byte_icon)

    font_byte = get_font("arialbd.ttf", 20)
    font_byte_sub = get_font("arial.ttf", 16)
    draw.text((bx + 75, by + 16), "LINH VẬT 3D: BÉ BYTE (ROBOT CHIBI)", fill=(0, 229, 255, 255), font=font_byte)
    draw.text((bx + 75, by + 42), "Tương tác & điều hướng màn hình nổi", fill=(180, 210, 240, 220), font=font_byte_sub)

    # 5. Bottom Info Bar
    font_bot = get_font("arial.ttf", 20)
    bot_text = f"CỔNG 5 STORYBOARD • 1920x1080 FULL HD • KHUNG NỔI 3D PHÓNG ĐẠI TỐI ĐA • XƯỞNG 4 CINEMATIC"
    draw.text((50, height - 45), bot_text, fill=(140, 160, 190, 220), font=font_bot)

    out_file = STORYBOARD_DIR / f"storyboard_scene_{order:02d}.jpg"
    img.convert("RGB").save(out_file, "JPEG", quality=95)
    print(f"  ✅ Đã lưu Storyboard Cảnh {order:02d}: {out_file.name}")
    return out_file

def main():
    print("=" * 65)
    print("🎨 CỔNG 5: KẾT XUẤT 8 KHUNG ẢNH STORYBOARD VỚI MÀN HÌNH NỔI 3D PHÓNG ĐẠI")
    print("=" * 65)
    for s in SCENES_DATA:
        render_storyboard_frame(s)
    print("=" * 65)
    print(f"🎉 CỔNG 5 STORYBOARD ĐÃ HOÀN TẤT VÀ LƯU TẠI: {STORYBOARD_DIR}")
    print("=" * 65)

if __name__ == "__main__":
    main()

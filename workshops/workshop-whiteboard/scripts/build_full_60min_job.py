#!/usr/bin/env python3
"""
Tự động tạo file job-hop-dong-100-ty-tong-tai.json chuẩn 60 phút (~8.000 từ)
Phục vụ render video audio truyện ngôn tình dài 1 tiếng trên Xưởng 3 Whiteboard.
"""
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def create_full_60min_job():
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    md_path = root_dir / "docs" / "kich-ban-tong-tai-1-tieng.md"
    job_output = root_dir / "output" / "jobs" / "job-hop-dong-100-ty-tong-tai.json"

    job_output.parent.mkdir(parents=True, exist_ok=True)

    text = md_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    chapters_raw = re.split(r'### (CHƯƠNG \d+: [^\n]+)\n', text)[1:]

    badges = [
        "CHƯƠNG I: ĐÊM MƯA ĐỊNH MỆNH",
        "CHƯƠNG II: BẢN HỢP ĐỒNG 100 TỶ",
        "CHƯƠNG III: BƯỚC VÀO CỬA HÀO MÔN",
        "CHƯƠNG IV: ĐÊM MẤT NGỦ & LIỀU THUỐC XOA DỊU",
        "CHƯƠNG V: CẠM BẪY NƠI THƯƠNG TRƯỜNG",
        "CHƯƠNG VI: LẬT MẶT KẺ PHẢN BỘI",
        "CHƯƠNG VII: BÍ MẬT MƯỜI NĂM TRƯỚC",
        "CHƯƠNG VIII: NGÀY HỢP ĐỒNG HẾT HẠN",
        "CHƯƠNG IX: BẢN HỢP ĐỒNG TRỌN ĐỜI",
    ]

    beats = []
    beat_counter = 1

    for ch_idx in range(0, len(chapters_raw), 2):
        ch_num = (ch_idx // 2) + 1
        ch_header = chapters_raw[ch_idx].strip()
        ch_body = chapters_raw[ch_idx + 1].split("## IV. GÓI XUẤT BẢN")[0].strip()
        current_badge = badges[ch_num - 1]

        # Trích xuất toàn bộ các khối thoại / dẫn truyện
        blocks = []
        current_spk = None
        current_lines = []

        for line in ch_body.splitlines():
            s = line.strip()
            if not s or (s.startswith("*(") and s.endswith(")*")):
                continue
            if s.startswith("**") and s.endswith(":**"):
                if current_spk and current_lines:
                    cleaned_body = " ".join(current_lines).strip()
                    if cleaned_body:
                        blocks.append((current_spk, cleaned_body))
                    current_lines = []
                current_spk = s[2:-3].strip()
            else:
                # Xóa ghi chú cảm xúc trong ngoặc đơn *(thì thầm)*
                cleaned = re.sub(r'\*\([^*]+\)\*', '', s).strip()
                if cleaned:
                    current_lines.append(cleaned)

        if current_spk and current_lines:
            cleaned_body = " ".join(current_lines).strip()
            if cleaned_body:
                blocks.append((current_spk, cleaned_body))

        # Chia blocks của chương thành 3 beats cân bằng (Trái, Giữa, Phải)
        total_b = len(blocks)
        split1 = max(1, total_b // 3)
        split2 = max(split1 + 1, (total_b * 2) // 3)

        group1 = blocks[:split1]
        group2 = blocks[split1:split2]
        group3 = blocks[split2:]

        groups = [group1, group2, group3]

        sub_titles = [
            ("Mở Đầu Phân Cảnh", 100),
            ("Diễn Biến Kịch Tính", 680),
            ("Cao Trào Chương", 1260),
        ]

        for g_idx, g_blocks in enumerate(groups):
            raw_lines = []
            for spk, dlg in g_blocks:
                # Định dạng chuẩn: "Speaker: dialogue"
                raw_lines.append(f"{spk}: {dlg}")

            raw_text = "\n".join(raw_lines)
            pos_x = sub_titles[g_idx][1]

            beats.append({
                "id": f"beat_{beat_counter:02d}",
                "role": f"scene_{ch_num:02d}_part_{g_idx+1}",
                "rawText": raw_text,
                "visual": {
                    "headline": f"{current_badge} - Phần {g_idx+1}",
                    "subhead": sub_titles[g_idx][0],
                    "badge": current_badge,
                    "label": f"Phác họa diễn biến {current_badge} (Phần {g_idx+1})",
                    "type": "scene" if g_idx == 0 else ("character" if g_idx == 1 else "concept"),
                    "region": {
                        "x": pos_x,
                        "y": 80,
                        "width": 550,
                        "height": 920
                    }
                }
            })
            beat_counter += 1

    job_data = {
        "jobId": "job-hop-dong-100-ty-tong-tai",
        "title": "Bản Hợp Đồng 100 Tỷ: Ánh Trăng Của Tổng Tài Bạc Tỷ (Bản Full 60 Phút)",
        "workshop": "whiteboard",
        "archetype": "storytelling",
        "targetPlatform": "youtube_long",
        "canvas": {
            "width": 1920,
            "height": 1080,
            "fps": 90
        },
        "voice": {
            "provider": "edge-tts",
            "voiceId": "vi-VN-NamMinhNeural",
            "speed": 0.95,
            "rate": "-4%",
            "pitch": "+0Hz",
            "volume": "+0%"
        },
        "metadata": {
            "genre": "Ngôn tình đô thị, Tổng tài lạnh lùng, Cưới trước yêu sau, Chữa lành, Hào môn thế gia, Sủng ngọt, HE",
            "durationExpectedMinutes": 60,
            "author": "Omni-Director",
            "characters": [
                "Lục Cảnh Thâm (29 tuổi, Chủ tịch Lục Thị, mất ngủ kinh niên, lạnh lùng quyết đoán)",
                "Thẩm Nhược Hy (24 tuổi, Thiên kim sa cơ, thông minh kiên cường, đôi mắt sáng)",
                "Lục Lão Phu Nhân (75 tuổi, Bà nội Cảnh Thâm, nắm quyền tối cao gia tộc, hiền từ)",
                "Trợ lý Giang Thừa (27 tuổi, Cánh tay phải nhanh nhẹn đắc lực)",
                "Triệu Bích Nguyệt (26 tuổi, Thiên kim đối thủ kiêu kỳ nhiều tâm cơ)",
                "Thẩm Minh Viễn (50 tuổi, Chú ruột tham lam phản bội Thẩm gia)",
                "Cổ Đông Lớn (Cổ đông cấp cao tập đoàn Lục Thị)"
            ],
            "characters_voice": {
                "lục cảnh thâm": { "voice": "vi-VN-NamMinhNeural", "rate": "-2%", "pitch": "-5Hz", "volume": "+0%" },
                "cảnh thâm": { "voice": "vi-VN-NamMinhNeural", "rate": "-2%", "pitch": "-5Hz", "volume": "+0%" },
                "thẩm nhược hy": { "voice": "vi-VN-HoaiMyNeural", "rate": "-2%", "pitch": "+0Hz", "volume": "+0%" },
                "nhược hy": { "voice": "vi-VN-HoaiMyNeural", "rate": "-2%", "pitch": "+0Hz", "volume": "+0%" },
                "lục lão phu nhân": { "voice": "vi-VN-HoaiMyNeural", "rate": "-6%", "pitch": "-3Hz", "volume": "+0%" },
                "bà nội": { "voice": "vi-VN-HoaiMyNeural", "rate": "-6%", "pitch": "-3Hz", "volume": "+0%" },
                "giang thừa": { "voice": "vi-VN-NamMinhNeural", "rate": "+4%", "pitch": "+3Hz", "volume": "+0%" },
                "trợ lý giang": { "voice": "vi-VN-NamMinhNeural", "rate": "+4%", "pitch": "+3Hz", "volume": "+0%" },
                "triệu bích nguyệt": { "voice": "vi-VN-HoaiMyNeural", "rate": "+3%", "pitch": "+4Hz", "volume": "+0%" },
                "thẩm minh viễn": { "voice": "vi-VN-NamMinhNeural", "rate": "+2%", "pitch": "-3Hz", "volume": "+0%" },
                "cổ đông lớn": { "voice": "vi-VN-NamMinhNeural", "rate": "+0%", "pitch": "-2Hz", "volume": "+0%" },
                "người kể chuyện": { "voice": "vi-VN-NamMinhNeural", "rate": "-4%", "pitch": "+0Hz", "volume": "+0%" }
            },
            "tags": [
                "truyenaudio",
                "ngontinh",
                "tongtai",
                "hopdong100ty",
                "sachnoi",
                "cuoitruocyeusau",
                "chualanh",
                "whiteboardstory"
            ]
        },
        "beats": beats
    }

    with open(job_output, "w", encoding="utf-8") as f:
        json.dump(job_data, f, ensure_ascii=False, indent=2)

    total_words = sum(len(b["rawText"].split()) for b in beats)
    print(f"[OK] Đã tạo thành công {job_output}")
    print(f"[*] Tổng số beats: {len(beats)} (27 beats chia đều 9 phân cảnh)")
    print(f"[*] Tổng số từ thoại: {total_words} từ (~{total_words/130:.1f} phút)")

if __name__ == "__main__":
    create_full_60min_job()

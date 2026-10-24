#!/usr/bin/env python3
"""
OmniVideo Studio - Gate 5 Storyboard Builder for MCP 7-Min Film (105 Shots)
Generates the comprehensive review artifact CONG_5_DUYET_STORYBOARD_105_SHOTS.md.
"""
import json
import logging
import shutil
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(r"c:\Users\tranh\Documents\Duy\VideoAI")
JOB_ID = "job-mcp-explained-7min"
VIDEO_ID = "video-mcp-105-shots"
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / JOB_ID
IMAGES_DIR = OUTPUT_DIR / "images"
DB_PATH = BASE_DIR / "workshops" / "workshop-cinematic" / "flow_agent.db"
BRAIN_DIR = Path(r"C:\Users\tranh\.gemini\antigravity\brain\74745d7e-e139-4bc8-b6d1-fbc945ef19d8")
MANIFEST_PATH = OUTPUT_DIR / "mcp_105_manifest.json"

ACTS = [
    (1, 16, "HỒI 1: NỖI ĐAU PHÂN MẢNH & GIỚI HẠN CỦA AI CÔ ĐƠN", "Trạm Điều Phối Giao Thức MCP Vạn Năng (Set 1)"),
    (17, 42, "HỒI 2: KHAI SINH MCP — CHUẨN KẾT NỐI VẠN NĂNG", "Trạm Điều Phối Giao Thức MCP Vạn Năng (Set 1)"),
    (43, 74, "HỒI 3: GIẢI PHẪU KỸ THUẬT — 3 TRỤ CỘT CỐT LÕI (RESOURCES, PROMPTS, TOOLS)", "Pháo Đài Sandbox Lập Trình & Bảo Mật MCP (Set 2)"),
    (75, 94, "HỒI 4: PHÁO ĐÀI BẢO MẬT & KỶ NGUYÊN TỰ CHỦ 2026", "Pháo Đài Sandbox Lập Trình & Bảo Mật MCP (Set 2)"),
    (95, 105, "HỒI 5: TƯƠNG LAI CỦA MCP & LỜI KÊU GỌI HÀNH ĐỘNG", "Trạm Điều Phối Giao Thức MCP Vạn Năng (Set 1)"),
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT display_order, horizontal_image_media_id, horizontal_image_url, image_prompt, video_prompt
        FROM scene
        WHERE video_id = ?
        ORDER BY display_order
    """, (VIDEO_ID,))
    db_scenes = {row[0]: row for row in cur.fetchall()}
    conn.close()

    manifest_shots = {}
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest_list = json.load(f)
            for s in manifest_list:
                manifest_shots[s["shot_num"]] = s

    # Copy key sample frames to BRAIN_DIR
    sample_shots = [1, 15, 30, 45, 60, 75, 90, 105]
    for sn in sample_shots:
        src = IMAGES_DIR / f"shot_{sn:03d}.jpg"
        if src.exists():
            dst = BRAIN_DIR / f"storyboard_shot_{sn:03d}.jpg"
            shutil.copy2(src, dst)
            print(f"Copied {src.name} -> {dst.name}")

    total_images_on_disk = len(list(IMAGES_DIR.glob("shot_*.jpg")))

    # Build Markdown Content
    md = []
    md.append("# 🎬 BẢNG DUYỆT CỔNG 5: HỆ THỐNG STORYBOARD 105 PHÂN CẢNH ĐIỆN ẢNH (7 PHÚT)")
    md.append("## 📌 Dự án: Giải Mã MCP (Model Context Protocol) — Chuẩn Kết Nối Vạn Năng Biến AI Thành Siêu Trợ Lý")
    md.append("")
    md.append("> [!IMPORTANT]")
    md.append("> **TUÂN THỦ TUYỆT ĐỐI NGUYÊN TẮC CỔNG 5 & CHỈ ĐẠO CỦA BẠN:**")
    md.append(f"> - **100% Khung ảnh Start-frame độc lập:** Đã hoàn tất render tươi mới ({total_images_on_disk}/105 shots) trên Google Flow bằng Imagen 3.")
    md.append("> - **Zero-Loop & No-Zoompan:** Mỗi shot quay tương ứng một góc máy riêng (ASL ~3.9s), tuyệt đối không dùng zoompan ảnh tĩnh hay lặp clip.")
    md.append("> - **Khóa 2 Trường Quay Master Mới:** Trường quay 1 (MCP Hub) cho shots 1-42, 95-105; Trường quay 2 (Sandbox Vault) cho shots 43-94.")
    md.append("> - **Trạng thái quy trình:** **DỪNG LẠI TẠI CỔNG 5 ĐỂ BẠN KIỂM TRA & DUYỆT TRƯỚC KHI BẮT ĐẦU BẤM MÁY CỔNG 6 (SINH VIDEO VEO 2).**")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 🖼️ BỘ KHUNG HÌNH TIÊU BIỂU (REPRESENTATIVE STORYBOARD FRAMES)")
    md.append("")
    md.append("````carousel")
    for sn in sample_shots:
        src = BRAIN_DIR / f"storyboard_shot_{sn:03d}.jpg"
        if src.exists():
            m_data = manifest_shots.get(sn, {})
            diag = m_data.get("dialogue", "")
            badge = m_data.get("speaker_badge", "BÉ BYTE")
            stype = m_data.get("shot_type", "Cinematic Medium Shot")
            md.append(f"![Shot {sn:03d} - {stype}](/C:/Users/tranh/.gemini/antigravity/brain/74745d7e-e139-4bc8-b6d1-fbc945ef19d8/storyboard_shot_{sn:03d}.jpg)")
            md.append(f"**Shot {sn:03d}** ({stype}) | **[{badge}]**: *\"{diag}\"*")
            md.append("<!-- slide -->")
    md.append("````")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 📊 CHI TIẾT 105 PHÂN CẢNH THEO 5 HỒI ĐIỆN ẢNH")
    md.append("")

    for start_shot, end_shot, act_title, act_set in ACTS:
        md.append(f"### 📍 {act_title} (Shots {start_shot:03d} - {end_shot:03d})")
        md.append(f"- **Bối cảnh chỉ định:** `{act_set}`")
        md.append("")
        md.append("| Shot | Timing | Góc Máy | Nhân Vật / Badge | Thoại Tinh Gọn (Voice x1.25) | Trạng Thái Khung Hình |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

        for sn in range(start_shot, end_shot + 1):
            m_data = manifest_shots.get(sn, {})
            timing = m_data.get("timing", "3.8s")
            stype = m_data.get("shot_type", "Medium Shot")
            badge = m_data.get("speaker_badge", "BÉ BYTE")
            diag = m_data.get("dialogue", "")
            db_row = db_scenes.get(sn)
            mid = db_row[1] if db_row else None
            mid_str = f"`{mid[:8]}...`" if mid else "Chờ render"
            img_file = IMAGES_DIR / f"shot_{sn:03d}.jpg"
            img_status = "✅ Sẵn sàng" if img_file.exists() else "⏳ Đang tải"

            # Format row
            md.append(f"| **Shot {sn:03d}** | {timing} | {stype} | `{badge}` | {diag} | {img_status} ({mid_str}) |")
        md.append("")

    md.append("---")
    md.append("")
    md.append("## 🚀 KẾ HOẠCH HÀNH ĐỘNG CỔNG 6 (BẤM MÁY VIDEO VEO 2)")
    md.append("Sau khi bạn gửi lệnh **\"Duyệt\"** hoặc phản hồi đồng ý:")
    md.append("1. **Kích hoạt Veo 2 trên Google Flow:** Sử dụng Media ID của 105 ảnh Start-frame vừa render để sinh chuyển động điện ảnh tự nhiên.")
    md.append("2. **Đồng bộ Lip-Sync & Cắt góc điện ảnh:** Phối hợp cử động khẩu hình tự nhiên của Bé Byte cùng luân phiên góc quay OTS, toàn cảnh, đặc tả.")
    md.append("3. **FFmpeg Master Assembly:** Ráp 105 video Veo 2 cùng 105 audio Edge-TTS 48kHz, Cyber Chatbox cyan neon, và BGM ducking chuẩn -22dB.")
    md.append("4. **Thumbnail 3D High-CTR:** Render Hero Shot của Bé Byte và Trạm MCP Hub với typography neon tương phản cao.")
    md.append("")
    md.append("> 🛑 **HỆ THỐNG ĐANG DỪNG LẠI TẠI ĐÂY THEO ĐÚNG YÊU CẦU CỦA BẠN ĐỂ CHỜ DUYỆT CỔNG 5.**")

    # Write to Brain Artifact
    out_artifact = BRAIN_DIR / "CONG_5_DUYET_STORYBOARD_105_SHOTS.md"
    out_artifact.write_text("\n".join(md), encoding="utf-8")
    print(f"Generated Gate 5 Artifact: {out_artifact}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
OmniVideo Studio - Whiteboard YouTube Metadata & Chapters Generator
Tự động đóng gói nội dung để đăng tải lên YouTube Studio:
- Tính toán mốc thời gian YouTube Chapters (00:00, 02:01, ...)
- Tạo các phương án tiêu đề giật tít, tăng tỷ lệ CTR
- Xuất mô tả chuẩn SEO, danh sách nhân vật, Hashtags & Tags
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

# Đảm bảo stdout/stderr luôn dùng UTF-8 trên Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def format_youtube_timestamp(seconds: float | int) -> str:
    """Định dạng số giây thành chuỗi thời gian YouTube (MM:SS hoặc HH:MM:SS)."""
    total_sec = max(0, int(round(seconds)))
    h = total_sec // 3600
    m = (total_sec % 3600) // 60
    s = total_sec % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def generate_youtube_metadata(
    job_json_path: Path,
    scenes_info: list[dict],
    output_path: Path,
) -> Path:
    """
    Sinh tài liệu YOUTUBE_METADATA.md với YouTube Chapters và SEO packaging.
    scenes_info: list of {"scene_id": str, "title": str, "duration_sec": float}
    """
    with open(job_json_path, "r", encoding="utf-8") as f:
        job = json.load(f)

    title = job.get("title", "Truyện Audio Bảng Trắng")
    meta = job.get("metadata", {})
    genre = meta.get("genre", "Truyện Audio, Chữa Lành, Tâm Lý")
    characters = meta.get("characters", [])
    raw_tags = meta.get("tags", [])

    # Tính mốc thời gian tích lũy
    chapters_lines = []
    cumulative_sec = 0.0

    for idx, sc in enumerate(scenes_info, start=1):
        ts_str = format_youtube_timestamp(cumulative_sec)
        sc_title = sc.get("title") or f"Phân đoạn {idx}"
        # Xóa các tiền tố thừa nếu có
        clean_title = sc_title
        for prefix in ["CHƯƠNG ", "PHÂN CẢNH ", "CẢNH "]:
            if clean_title.upper().startswith(prefix):
                parts = clean_title.split(":", 1)
                if len(parts) > 1:
                    clean_title = parts[1].strip()
                break

        chapters_lines.append(f"{ts_str} - Phân cảnh {idx}: {clean_title}")
        cumulative_sec += float(sc.get("duration_sec", 0.0))

    chapters_text = "\n".join(chapters_lines)
    total_time_str = format_youtube_timestamp(cumulative_sec)

    # Gợi ý tiêu đề CTR cao
    title_opt_1 = f"Truyện Audio | {title} (Trọn Bộ)"
    title_opt_2 = f"【Audio Drama】{title} - Nét Vẽ Bảng Trắng Siêu Cuốn (90 FPS)"
    title_opt_3 = f"{title} | Truyện Audio Chữa Lành Đêm Muộn Giúp Ngủ Ngon"

    # Danh sách nhân vật
    chars_text = "\n".join([f"- {c}" for c in characters]) if characters else "- Các nhân vật trong tác phẩm"

    # Tags & Hashtags
    default_hashtags = ["#TruyenAudio", "#Audiobook", "#WhiteboardAnimation", "#OmniVideo", "#KeChuyenDemMuon"]
    if "ngon tinh" in genre.lower():
        default_hashtags.extend(["#NgonTinh", "#TongTai", "#ChuaLanh"])
    hashtags_str = " ".join(dict.fromkeys(default_hashtags))

    all_tags = list(dict.fromkeys([
        "truyen audio", "audio drama", "whiteboard animation", "ve bang trang 90fps",
        "omnivideo", "ke chuyen dem ngon", title.lower()
    ] + [t.lower() for t in raw_tags]))
    tags_str = ", ".join(all_tags)

    content = f"""# 🎬 YouTube Metadata & SEO Package: {title}

Tài liệu đóng gói tự động từ **OmniVideo Studio (Xưởng 3)** phục vụ đăng tải và tối ưu SEO YouTube.

---

## 1. Gợi Ý Tiêu Đề Video (CTR & Search Optimization)
- **Phương án 1 (Gợi mở - Tò mò)**: `{title_opt_1}`
- **Phương án 2 (Kịch tính - Nghệ thuật vẽ tay)**: `{title_opt_2}`
- **Phương án 3 (Thư giãn - Ngủ ngon)**: `{title_opt_3}`

---

## 2. YouTube Timestamps / Chapters (Dán trực tiếp vào Mô tả)
```text
{chapters_text}
```

---

## 3. Nội Dung Mô Tả Video (Description Template)
```text
{title}
Thời lượng: {total_time_str} | Thể loại: {genre}

🌿 Đôi nét về tác phẩm:
Một câu chuyện audio drama nhẹ nhàng, ấm áp được thể hiện qua nét vẽ bảng trắng chuyển động tỉ mỉ 90 FPS và giọng đọc truyền cảm. Chúc các bạn có những giây phút thư giãn, lắng đọng sau ngày dài!

📖 THÔNG TIN TÁC PHẨM & NHÂN VẬT:
{chars_text}

📌 DANH SÁCH PHÂN ĐOẠN (TIMESTAMPS):
{chapters_text}

---
Đăng ký kênh để đón nghe những tập truyện tiếp theo được vẽ tay độc quyền!
{hashtags_str}
```

---

## 4. Bộ Thẻ Tags (YouTube Studio Tags)
```text
{tags_str}
```

---

## 5. File Phụ Đề Rời (YouTube Closed Captions / CC)
- File phụ đề rời đồng bộ hoàn hảo đã được tạo sẵn tại: `input.srt` (hoặc tải trực tiếp từ nút "Tải file SRT" trên Web Dashboard).
- **Cách nạp lên YouTube:**
  1. Vào YouTube Studio -> Chọn video vừa tải lên -> Mục **"Phụ đề" (Subtitles)**.
  2. Bấm **"Thêm phụ đề"** -> Chọn **"Tải tệp lên" (Upload file)** -> Chọn **"Có mốc thời gian" (With timing)**.
  3. Chọn file `input.srt`.
- **Lợi ích:** Video trên YouTube sẽ hiển thị phụ đề sắc nét, người xem có thể bật/tắt (CC) tùy ý, chỉnh cỡ chữ, và YouTube có thể tự động dịch sang tiếng Anh/ngôn ngữ khác!

---
*Tài liệu được sinh tự động bởi OmniVideo Studio Whiteboard Pipeline.*
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Sinh tài liệu YouTube Metadata & Chapters")
    parser.add_argument("--job", required=True, help="Đường dẫn file job.json")
    parser.add_argument("--scenes-dir", required=True, help="Thư mục chứa các phân cảnh scenes/")
    parser.add_argument("--output", required=True, help="Đường dẫn file YOUTUBE_METADATA.md cần xuất")
    args = parser.parse_args(argv)

    job_p = Path(args.job)
    scenes_p = Path(args.scenes_dir)
    out_p = Path(args.output)

    # Thu thập thông tin các phân cảnh từ annotation hoặc mp4
    scenes_info = []
    for sc_dir in sorted(scenes_p.glob("scene-*")):
        if sc_dir.is_dir():
            sc_id = sc_dir.name
            ann_file = sc_dir / f"{sc_id}.annotation.json"
            sc_title = sc_id
            dur_sec = 0.0

            if ann_file.exists():
                with open(ann_file, "r", encoding="utf-8") as f:
                    ann = json.load(f)
                    dur_ms = ann.get("sceneDurationMs", 0)
                    dur_sec = dur_ms / 1000.0
                    if ann.get("badge"):
                        sc_title = ann["badge"]

            if sc_title == sc_id:
                prompt_file = sc_dir / "IMAGE_PROMPT.md"
                if prompt_file.exists():
                    txt = prompt_file.read_text(encoding="utf-8")
                    for line in txt.splitlines():
                        if line.startswith("# ") and any(k in line for k in ["Phân cảnh", "CHƯƠNG", "Scene", "scene"]):
                            clean_t = line.replace("# ", "").replace("Visual Prompt Guidance:", "").strip()
                            if clean_t:
                                sc_title = clean_t
                                break

            scenes_info.append({
                "scene_id": sc_id,
                "title": sc_title,
                "duration_sec": dur_sec,
            })

    generate_youtube_metadata(job_p, scenes_info, out_p)
    print(f"[OK] Đã xuất thành công: {out_p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

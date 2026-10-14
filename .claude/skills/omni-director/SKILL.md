---
name: omni-director
description: AI Giám Đốc Sản Xuất Video Đa Phân Xưởng. Nhận đầu vào là một URL bài báo, một chủ đề kiến thức, một kịch bản văn bản hoặc file SRT. Tự động đánh giá nội dung, chuẩn hóa ngữ âm tiếng Việt, tạo hợp đồng dữ liệu job.json và điều phối sang Xưởng phù hợp (Xưởng 1: Tin tức HyperFrames, Xưởng 2: Giải thích Remotion React, Xưởng 3: Bảng trắng vẽ tay Python).
---

# Omni-Director Skill: AI Giám Đốc Sản Xuất Video

Kỹ năng điều phối sản xuất video tự động 100% Local dành cho YouTube và TikTok.

## Input

Một chuỗi duy nhất:
- **URL bài báo / GitHub repo:** (bắt đầu bằng `http://` hoặc `https://`)
- **Tên chủ đề / Khái niệm:** ví dụ *"Docker là gì"*, *"Cho đi và nhận lại"*
- **Đường dẫn file:** `.txt`, `.md` hoặc `.srt`

## Quy Trình Xử Lý 5 Bước

### Bước 1: Phân Loại Đầu Vào & Chọn Xưởng Sản Xuất
1. **URL bài báo / Repo GitHub / Bản tin vắn:**
   → Chọn **Xưởng 1 (`workshop-news`)**.
   → Format: 9:16 Dọc @ 30 FPS.
   → Mẫu template: breaking-news, stat-callout, split-screen.
2. **Khái niệm công nghệ / Kiến trúc phần mềm / Lập trình:**
   → Chọn **Xưởng 2 (`workshop-explainer`)**.
   → Format: 9:16 (Shorts/TikTok) hoặc 16:9 (YouTube Video).
   → Mẫu kịch bản: 6 nhịp tâm lý theo Tỉ lệ % ngân sách nhịp (Hook -> Pain -> Solution -> Workflow -> Benefits -> Outro).
3. **Kể chuyện đạo lý / Bài học cuộc sống / Tóm tắt sách / Lịch sử / File SRT:**
   → Chọn **Xưởng 3 (`workshop-whiteboard`)**.
   → Format: 16:9 (YouTube) hoặc 9:16 (TikTok).
   → Kỹ thuật: Bàn tay vẽ thực tế, nét phác ink -> tô màu color trên nền giấy kem `#F5EBD7`.

### Bước 2: Chuẩn Hóa Kịch Bản & Ngữ Âm Tiếng Việt
- Áp dụng các quy tắc trong `docs/WORKSHOPS_SPECIFICATION.md`:
  - Đổi các số phiên bản: `GPT 5.5` → `gí pi tí năm chấm năm`.
  - Đổi số hàng nghìn: `1.000.000` → `một triệu`.
  - Đổi số thập phân: `82.7%` → `tám mươi hai phẩy bảy phần trăm`.
  - Đổi từ viết tắt: `AI` → `ây ai`, `API` → `ây pi ai`.

### Bước 3: Tạo File Hợp Đồng Dữ Liệu `job.json`
Lưu tại thư mục dự án tương ứng:
`output/<workshop>/<jobId>/job.json` tuân thủ đúng schema Zod tại `core/schema/job.ts`.

### Bước 4: Gọi Adapter Của Xưởng Tương Ứng
- **Nếu là Xưởng 1:** Chạy pipeline HyperFrames qua `workshops/workshop-news`.
- **Nếu là Xưởng 2:** Nạp props vào Remotion và render qua `workshops/workshop-explainer`.
- **Nếu là Xưởng 3:** Chuyển đổi thành SRT/Annotation và render stream qua `workshops/workshop-whiteboard`.

### Bước 5: Bàn Giao Thành Phẩm
- Thông báo đường dẫn video MP4 1080p sắc nét.
- Cung cấp file `caption.txt` có sẵn tiêu đề giật tít và 4 hashtag trending để đăng tải ngay lên YouTube / TikTok.

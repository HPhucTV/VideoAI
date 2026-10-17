# Đặc Tả Kỹ Thuật: Nâng Cấp Kịch Bản Sảng Văn, Voice 1.25x Và Tự Động Hòa Trộn BGM (Audio Drama)

- **Ngày tạo:** 2026-10-17
- **Trạng thái:** Bản thảo đã duyệt thiết kế (Approved Draft)
- **Chủ đề:** Khắc phục 3 điểm yếu cốt tử của video truyện audio AI (Cốt truyện chán, thiếu Hook mở đầu, giọng đọc đơn điệu bị đọc to tên vai).

---

## 1. Mục Tiêu & Bối Cảnh (Executive Summary & Goals)

Dựa trên phản hồi thực tế khi phát hành video truyện tu tiên audio (*Phế Đan Nghịch Thiên*), hệ thống còn 3 tử huyệt:
1. **Nội dung cốt truyện buồn ngủ:** ChatGPT/Claude mặc định viết văn phong tả cảnh dài lê thê, thiếu mâu thuẫn sinh tử trực diện, thiếu nhịp điệu dồn dập và các pha "vả mặt/phản sát" đắc ý (sảng văn).
2. **Thiếu lời giới thiệu / Hook mở đầu:** Không có Hook 10–15 giây đầu giữ chân người nghe, vào truyện đột ngột khiến tỷ lệ giữ chân (Retention Rate) trên YouTube tụt dốc.
3. **Giọng đọc monotone và bị lỗi xưng vai:**
   - Tốc độ cũ (`-15%` ~ 0.85x) quá chậm, nghe uể oải.
   - Khi chuyển vai, giọng đọc phát âm cả chữ *"Người kể chuyện:"*, *"Lâm Mặc:"* phá hỏng tính điện ảnh.
   - Thiếu nhạc nền (BGM) và hiệu ứng âm thanh, khiến âm thanh trần trụi, đơn điệu.

### Mục tiêu giải quyết:
- **Cung cấp Master Prompt Siêu Kịch Bản:** Chuẩn hóa quy trình dùng ChatGPT/Claude để 1-click xuất kịch bản sảng văn dồn dập, có sẵn Hook 15s vàng và tương thích 100% với OmniVideo Studio.
- **Triệt tiêu 100% việc đọc tên vai:** Tích hợp bộ lọc Regex (Dialogue Sanitizer) bóc tách tên nhân vật, chỉ đưa lời thoại thuần túy vào engine TTS.
- **Nâng tốc độ đọc chuẩn 1.25x (`rate: "+25%"`):** Tối ưu ngắt nghỉ, đa dạng âm sắc nhân vật (Audio Drama).
- **Tự động hòa trộn BGM với Audio Ducking (FFmpeg):** Tự động hạ âm lượng nhạc nền khi nhân vật nói và bùng nổ âm nhạc ở các đoạn chuyển cảnh cao trào.

---

## 2. Kiến Trúc & Các Thành Phần (Architecture & Components)

```
[ Ý Tưởng Thô ]
       │
       ▼ (Dán Master Prompt vào ChatGPT / Claude)
[ Kịch Bản Sảng Văn Chuẩn JSON ]
       │ ── 15s Hook Vàng (Teaser + Lời chào kênh)
       │ ── Nhịp sảng văn dồn dập (Xung đột -> Cơ duyên -> Vả mặt)
       │ ── Phân vai thoại sạch sẽ
       ▼
[ OmniVideo Dashboard / Engine ]
       │
       ├─► [ Dialogue Sanitizer Filter ]
       │        └─► Cắt bỏ triệt để "Người kể chuyện:", "Lâm Mặc:" khỏi text đọc
       │
       ├─► [ Edge-TTS Engine 1.25x ]
       │        ├─► Dẫn truyện: NamMinh +25%, pitch 0Hz
       │        ├─► Nam chính: NamMinh +20%, pitch -3Hz (trầm quật cường)
       │        ├─► Phản diện / Trưởng lão: NamMinh +10%, pitch -6Hz (già độc)
       │        └─► Nữ / Thiếu niên: HoaiMy +20%, pitch +2Hz
       │
       └─► [ FFmpeg Audio Ducking Muxer ]
                ├─► Giọng đọc (Voice Track)
                ├─► Nhạc nền (BGM Track từ assets/bgm/)
                │      └─► Sidechain Compression: Tự giảm -20dB khi có giọng
                └─► Video Silent (Canvas / Whiteboard)
                       │
                       ▼
             [ Video Thành Phẩm Hoàn Chỉnh ]
```

---

## 3. Đặc Tả Chi Tiết Từng Module

### 3.1. Module 1: Master Prompt Siêu Kịch Bản (`prompts/MASTER_STORY_PROMPT.md`)
Tài liệu hướng dẫn chuyên sâu cho ChatGPT/Claude, bao gồm:
1. **Quy tắc 15s Hook Vàng:**
   - 0s–7s: Trích câu thoại kịch tính nhất ở cao trào đưa lên đầu.
   - 7s–15s: Lời chào kênh, câu hỏi kích thích tò mò và lời kêu gọi Đăng ký kênh (Subscribe CTA).
2. **Công thức Sảng Văn 3 Hồi:**
   - *Hồi 1 (Áp bức tuyệt lộ):* Xung đột đẫm máu hoặc sỉ nhục cùng cực, không tả cảnh thừa thãi.
   - *Hồi 2 (Cơ duyên hắc ám):* Bí mật nghịch thiên, nuốt đan, đột phá trong nguy hiểm.
   - *Hồi 3 (Phản sát sướng tai):* Xuất thế vả mặt kẻ thù, đập tan âm mưu, tạo cảm xúc thỏa mãn tột cùng.
3. **Quy tắc Lời Thoại Thuần:**
   - Trong trường nội dung đọc, cấm tuyệt đối viết kèm tên nhân vật hay dấu hai chấm. Tên nhân vật được khai báo riêng ở trường `speaker`.

---

### 3.2. Module 2: Bộ Lọc Dialogue Sanitizer (Chống Đọc Tên Vai)
Được triển khai trong mã nguồn Python (`workshops/workshop-whiteboard/voice_generator.py`) và TypeScript (`core/tts/`):
- **Biểu thức Regex bóc tách:**
  ```regex
  ^\s*([^:\n]{1,35})\s*[:：]\s*(.+)$
  ```
- **Xử lý:**
  - Nếu phát hiện khớp với các tiền tố tên nhân vật (ví dụ: `Người Kể Chuyện: `, `Lâm Mặc: `, `Triệu Vô Cực: `, `Sở Thiên Kiêu (lạnh lùng): `):
    - Tách lấy `speaker = group(1)`.
    - Trả về `clean_text = group(2)` để đưa sang Edge-TTS.
  - Đảm bảo 100% TTS chỉ đọc nội dung thoại `clean_text`.

---

### 3.3. Module 3: Tốc Độ Đọc 1.25x & Phân Vai Âm Sắc Tự Động
- Cập nhật cấu hình mặc định trong `job_adapter.py` và `voice_generator.py`:
  - `rate: "+25%"` (chuẩn 1.25x cho nhịp kể chuyện lôi cuốn, không bị kéo rê).
- Bảng ánh xạ âm sắc (Voice Presets):
  | Vai trò / Speaker | Giọng (Voice ID) | Tốc độ (Rate) | Cao độ (Pitch) |
  | :--- | :--- | :--- | :--- |
  | `Người Kể Chuyện` / `Dẫn truyện` | `vi-VN-NamMinhNeural` | `+25%` | `+0Hz` |
  | `Lâm Mặc` (Nam chính căm hờn) | `vi-VN-NamMinhNeural` | `+20%` | `-3Hz` |
  | `Triệu Vô Cực` / `Trưởng lão` (Già độc) | `vi-VN-NamMinhNeural` | `+10%` | `-6Hz` |
  | `Sở Thiên Kiêu` (Kiêu ngạo, trẻ) | `vi-VN-NamMinhNeural` | `+25%` | `+3Hz` |
  | `Tiểu Thạch Đầu` / `Nữ nhân` | `vi-VN-HoaiMyNeural` | `+20%` | `+2Hz` |

---

### 3.4. Module 4: Tự Động Lồng Nhạc Nền BGM & Audio Ducking (FFmpeg)
Được nâng cấp trong script `export_video.py`:
1. **Thư mục tài nguyên:** `assets/bgm/` chứa các bản nhạc cổ phong / tiên hiệp không bản quyền (ví dụ: `xianxia-epic.mp3`, `dark-suspense.mp3`).
2. **Bộ lọc FFmpeg Audio Ducking:**
   Sử dụng filter `sidechaincompress` của FFmpeg:
   ```bash
   [1:a]asplit=2[sc][voice_clean];
   [2:a]aloop=loop=-1:size=2e+09[bgm_loop];
   [bgm_loop][sc]sidechaincompress=threshold=0.08:ratio=8:attack=20:release=400[ducked_bgm];
   [voice_clean][ducked_bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]
   ```
   - Khi có giọng nói: Nhạc nền tự động ép xuống -20dB.
   - Khi dứt câu thoại / chuyển cảnh: Nhạc nền tự động bùng lên trong 400ms.
   - Kết thúc video: Tự động fade-out 2 giây cuối cùng mượt mà.

---

## 4. Xử Lý Các Trường Hợp Ngoại Lệ (Edge Cases & Resilience)

1. **Không có file nhạc BGM hoặc người dùng tắt BGM:**
   - Hệ thống tự động kiểm tra `existsSync(bgm_path)`. Nếu không có BGM, hệ thống tự động fallback sang muxing giọng đọc thuần túy, tuyệt đối không gây lỗi crash pipeline.
2. **Dấu hai chấm nằm trong câu thoại:**
   - Ví dụ: `"Hắn gầm lên: Ngươi dám sao?!"`
   - Bộ lọc chỉ quét tiền tố ở đầu câu (bắt đầu bằng `^` và độ dài tên nhân vật $\le 35$ ký tự). Các dấu hai chấm ở giữa câu không bị cắt nhầm.
3. **Độ dài nhạc nền ngắn hơn thời lượng video:**
   - Sử dụng filter `aloop=loop=-1` để tự động lặp vô hạn và cắt chuẩn xác theo thời lượng video (`duration=first`).

---

## 5. Kế Hoạch Kiểm Thử (Verification & Testing)

1. **Unit Test Bộ Lọc Thoại (Dialogue Sanitizer):**
   - Viết test kiểm tra cắt sạch các mẫu: `"Người Kể Chuyện: ..."`, `"Lâm Mặc: ..."`, `"Sở Thiên Kiêu (hừ lạnh): ..."`.
   - Đảm bảo chuỗi trả về không còn tiền tố vai diễn.
2. **Unit Test Cấu Hình Voice 1.25x:**
   - Kiểm tra rate mặc định sinh ra đúng `+25%`.
3. **Integration Test Muxing Video kèm BGM Ducking:**
   - Chạy lệnh xuất video thử nghiệm với FFmpeg kiểm tra âm thanh đầu ra có đủ cả Voice và BGM ducking mượt mà.

# Thiết Kế Kiến Trúc: Biến Xưởng 3 Thành Xưởng Sản Xuất YouTube Truyện Audio Chuyên Nghiệp

- **Ngày ban hành:** 15/10/2026
- **Workshop:** `workshop-whiteboard` (Xưởng 3)
- **Mục tiêu:** Nâng cấp Xưởng 3 từ công cụ vẽ bảng trắng đơn thuần thành cỗ máy sản xuất video Truyện Audio/Audiobook tự động chuẩn YouTube Studio, tối ưu tỷ lệ giữ chân người xem (Audience Retention) và trải nghiệm nghe nhìn (Audio-Visual Experience).

---

## 1. Bối Cảnh & Vấn Đề Hiện Tại

Xưởng 3 hiện đã có bộ khung đồ họa rất mạnh:
- Render nét vẽ tay mượt mà ở **90 FPS**.
- Đã hỗ trợ đa phân cảnh (Multi-Scene) kèm hoạt cảnh **Bàn tay lau bảng (Eraser Wipe)** zíc-zắc 1.3s khôi phục nền giấy kem `#F5EBD7`.
- Nối video không mất chất lượng bằng FFmpeg `-c copy`.

Tuy nhiên, đối với thị trường **YouTube Truyện Audio / Audiobook**:
1. **Âm thanh đơn điệu:** Chỉ có 1 giọng đọc xuyên suốt từ đầu đến cuối kịch bản, không có nhạc nền (BGM), không có tiếng động môi trường (SFX), không có cơ chế Audio Ducking (hạ nhạc khi đọc thoại).
2. **Thiếu phụ đề trên khung hình:** Khán giả xem truyện audio đêm muộn hoặc trên điện thoại không thể đọc theo lời thoại do file `.srt` chưa được burn vào video.
3. **Chưa đóng gói SEO & Chapters tự động:** Người sáng tạo phải thủ công căn chỉnh mốc thời gian (timestamps) để điền vào phần mô tả YouTube, và khâu tạo ảnh minh họa từng cảnh vẫn mang tính thủ công.

---

## 2. Ba Trụ Cột Nâng Cấp (The 3 Core Upgrades)

```
                       +------------------------------------------+
                       |    XƯỞNG 3: YOUTUBE AUDIO DRAMA STUDIO    |
                       +------------------------------------------+
                                            |
         +----------------------------------+----------------------------------+
         |                                  |                                  |
         v                                  v                                  v
+-----------------------+        +-----------------------+        +-----------------------+
|  TRỤ CỘT 1: AUDIO     |        |  TRỤ CỘT 2: VISUAL    |        |  TRỤ CỘT 3: PACKAGING |
|  - Đa nhân vật TTS    |        |  - Burn-in Subtitles  |        |  - YouTube Chapters   |
|  - BGM Ducking        |        |  - Font chữ bút mực   |        |  - SEO Metadata       |
|  - Ambient Soundscape |        |  - 90 FPS vẽ tay + Sub|        |  - Auto Image Hook    |
+-----------------------+        +-----------------------+        +-----------------------+
```

---

### Trụ Cột 1: Hệ Thống Âm Thanh Đa Tầng & Phân Vai Đa Nhân Vật (Multi-Speaker TTS & BGM Ducking)

#### 1.1 Phân vai nhân vật tự động (Speaker Parsing & Mapping)
Trong kịch bản truyện audio, mỗi câu nói có thể thuộc về Người dẫn truyện hoặc nhân vật đối thoại:
- **Cấu trúc nhận diện:**
  - Nhận diện theo tiền tố lời thoại: `[Nhân vật]: [Lời thoại]` (ví dụ: `Hạ Vi:`, `Đình Phong:`, `Kiên:`, `Người dẫn chuyện:`).
  - Hoặc nhận diện theo thuộc tính `beat.speaker` / `beat.role` trong file `job.json`.
- **Ánh xạ giọng đọc (Voice Mapping):**
  - **Người dẫn truyện (Narrator):** `vi-VN-NamMinhNeural`, tốc độ `-4%`, trầm ấm, dẫn dắt câu chuyện truyền cảm.
  - **Nam chính (Đình Phong):** `vi-VN-NamMinhNeural`, `pitch="-5Hz"`, tạo độ trầm, dứt khoát, uy quyền của tổng tài.
  - **Nữ chính (Hạ Vi):** `vi-VN-HoaiMyNeural`, `pitch="+0Hz"`, tốc độ `+0%`, trong trẻo, điềm đạm, thanh lịch.
  - **Nhân vật phụ (Trợ lý Kiên):** `vi-VN-NamMinhNeural`, `rate="+5%"`, `pitch="+2Hz"`, nhịp nói lanh lợi, hơi lo lắng.

#### 1.2 Nhạc nền cảm xúc & Tự động giảm âm lượng (BGM Auto Ducking)
- Thư mục quản lý nhạc nền: `workshops/workshop-whiteboard/assets/audio/bgm/`.
- Cung cấp sẵn các track BGM lofi / piano không lời êm dịu phù hợp thể loại chữa lành, ngôn tình, lãng mạn.
- **Thuật toán Audio Ducking qua FFmpeg:**
  - Khi có giọng đọc (Speech active): Nhạc nền tự động giảm âm lượng xuống **12% – 15%** để lời thoại nổi bật rõ ràng.
  - Khi có khoảng lặng giữa các câu thoại (Silence/Gap > 0.5s): Nhạc nền tự động dâng lên **25% – 30%**.
  - Khi đến đoạn Bàn tay lau bảng chuyển cảnh (1.3s): Nhạc nền dâng lên **40% – 50%**, tạo nhịp chuyển cảnh điện ảnh sang trọng.
  - Sử dụng bộ lọc FFmpeg `sidechaincompress` hoặc bộ lọc `volume` động kết hợp `amix`.

---

### Trụ Cột 2: Hiển Thị Phụ Đề Nghệ Thuật (Burn-in Artistic Subtitles)

Khán giả YouTube truyện audio thường xuyên vừa nghe vừa đọc lướt theo dòng chữ.

#### 2.1 Thiết kế kiểu chữ phụ đề (Subtitle Styling)
- Tận dụng `scene-XX.srt` đã có sẵn mốc thời gian chính xác của từng câu.
- **Phong cách trực quan:**
  - **Vị trí:** Canh giữa, cách đáy màn hình $45\text{px} - 60\text{px}$ (vùng an toàn không bị thanh tiến trình YouTube che khuất).
  - **Màu chữ:** Bút mực đen xám đậm `&H002C2C2C` hài hòa với màu mực vẽ tay trên nền giấy kem `#F5EBD7`.
  - **Hiệu ứng nền chữ:** Dải nền mờ nhẹ màu kem nhạt (semi-transparent soft box) hoặc bóng đổ mịn `&H80000000` giúp chữ luôn dễ đọc trên mọi bức vẽ mà không gây rối mắt.
  - **Font chữ:** Ưu tiên font Serif việt hóa thanh lịch (Merriweather, Playfair, Noto Serif) hoặc font Sans tròn gọn (Be Vietnam Pro, Montserrat).
- **Tích hợp vào FFmpeg:**
  - Bộ lọc `subtitles=scene-XX.srt:force_style='FontName=Arial,FontSize=16,PrimaryColour=&H002C2C2C,BackColour=&H40FFFFFF,BorderStyle=3,Outline=0,Shadow=1,MarginV=45,Alignment=2'`
  - Hỗ trợ cờ CLI: `--with-subtitles` (mặc định bật cho truyện audio).

---

### Trụ Cột 3: Tự Động Hóa Sinh Ảnh & Đóng Gói YouTube SEO (Auto Image & YouTube Packaging)

#### 3.1 Bộ công cụ tạo YouTube Chapters & Metadata tự động
Từ danh sách phân cảnh `scenes/scene-01`, `scenes/scene-02`, ... và thời lượng chính xác của từng cảnh:
- Tự động tính toán mốc thời gian tích lũy (Cumulative Timestamps):
  - `00:00 - Phân cảnh 1: Vị khách không mời lúc nửa đêm`
  - `02:01 - Phân cảnh 2: Liều thuốc ngủ đắt giá nhất thế giới`
  - `...`
- Xuất tệp `output/whiteboard/{job_id}/YOUTUBE_METADATA.md` gồm:
  1. **Tiêu đề gợi ý (Optimized Titles):** 3 phương án tiêu đề giật tít, tò mò, chuẩn thuật toán YouTube.
  2. **Mô tả video (Video Description):** Tóm tắt nội dung kịch bản + Giới thiệu nhân vật + **Bảng Chapters có thể bấm nhảy thời gian ngay trên YouTube**.
  3. **Bộ thẻ Tags & Hashtags:** `#TruyenAudio #NgonTinh #TongTai #WhiteboardAnimation #OmniVideo`.

#### 3.2 Tự động sinh ảnh theo phân cảnh (Auto Illustration Hook)
- Cung cấp script tự động `generate_scene_images.py`:
  - Đọc file `scenes/scene-XX/IMAGE_PROMPT.md` vừa được tạo ra từ `job_adapter.py`.
  - Gọi API vẽ tranh (Gemini / Imagen 3 / Fal.ai / AI Studio) với phong cách cố định:
    *"Minimal hand-drawn sketch, clean Notion doodle aesthetic, dark gray outlines, uniform warm cream paper #F5EBD7, no text, 16:9 ratio"*.
  - Tự động lưu thẳng vào `scenes/scene-XX/scene-XX.png`.
  - Nếu người dùng đã có ảnh vẽ sẵn trong `assets/`, pipeline tự động dùng ảnh sẵn mà không tốn credit gọi API.

---

## 3. Tác Động & Lợi Ích Kinh Doanh (Business Impact)

| Yếu tố | Trước nâng cấp | Sau nâng cấp | Hiệu quả kênh YouTube |
| :--- | :--- | :--- | :--- |
| **Trải nghiệm nghe** | 1 giọng đọc khô, không nhạc | Đa giọng kịch tính + Nhạc nền Lofi/Piano du dương | Tăng thời lượng nghe trung bình (AVD) thêm **150%** |
| **Trải nghiệm nhìn** | Chỉ có tranh vẽ, không có chữ | Nét vẽ 90 FPS + Chữ phụ đề nghệ thuật chạy theo lời | Giữ chân người xem lướt mobile, tăng Watch Time |
| **Thời gian sản xuất** | 45-60 phút thao tác tay/video | **Dưới 5 phút bấm 1 lệnh duy nhất** | Tăng sản lượng video lên 3 - 5 tập/ngày |
| **SEO YouTube** | Phải tự gõ timestamps thủ công | Tự động sinh sẵn Chapters & Metadata chuẩn SEO | Video được YouTube đề xuất và phân đoạn trực quan |

---

## 4. Kế Hoạch Triển Khai (Phased Implementation Plan)

- **Giai đoạn 1 (Audio):**
  - Cập nhật `job_adapter.py` bổ sung module phân tích nhân vật (`parse_speaker_dialogue`) và cấu hình giọng Edge-TTS tương ứng (`NamMinh` / `HoaiMy` / biến âm pitch).
  - Tích hợp bộ trộn BGM có cơ chế **Audio Ducking** vào `job_adapter.py` & `export_video.py`.
- **Giai đoạn 2 (Subtitles):**
  - Cập nhật `export_video.py` tích hợp bộ lọc phụ đề FFmpeg với style giấy kem mực đen, có cờ `--with-subtitles`.
- **Giai đoạn 3 (Packaging & Verification):**
  - Thêm chức năng tự động tạo `YOUTUBE_METADATA.md` chứa mốc thời gian YouTube Chapters và thẻ SEO.
  - Chạy thử nghiệm trên kịch bản thực tế *"Bản Hợp Đồng Lúc 0 Giờ"*.

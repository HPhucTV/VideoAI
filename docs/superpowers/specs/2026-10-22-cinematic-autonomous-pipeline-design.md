# 🎬 THIẾT KẾ ĐẶC TẢ: HỆ THỐNG TỰ ĐỘNG HÓA SẢN XUẤT ĐIỆN ẢNH VÀ XUẤT BẢN YOUTUBE (GATES 1–7)
# OMNIVIDEO STUDIO — WORKSHOP 4 (CINEMATIC AUTONOMOUS PIPELINE)

> **Mã tài liệu:** `SPEC-2026-10-22-CINEMATIC-PIPELINE`  
> **Ngày lập:** 22/10/2026  
> **Trạng thái:** Đã phê duyệt (Approved by User)  
> **Tác giả:** AI Assistant (Pair Programming cùng User)

---

## 1. TỔNG QUAN & MỤC TIÊU (OVERVIEW & GOALS)

### 1.1. Bối cảnh
Trong hệ thống OmniVideo Studio, việc sản xuất phim hoạt hình 3D / Donghua tại Phân xưởng 4 (`workshop-cinematic`) tuân theo **Quy trình 6 Cổng Phê Duyệt Tiền Kỳ (The 6-Gate Protocol)** và tiêu chuẩn điện ảnh tại [`docs/CINEMATIC_STANDARDS.md`](../CINEMATIC_STANDARDS.md).
Hiện tại, khi làm việc trong môi trường IDE, kịch bản (Cổng 1–2) được tạo ra rất nhanh, nhưng việc thực thi các Cổng 3–6 vẫn đòi hỏi chạy nhiều script rời rạc (`generate_gate3_assets.py`, `synthesize_gate4_104_shots.py`, `assemble_104_master_film.py`...), và sau đó người dùng vẫn phải thao tác thủ công để xuất bản video lên YouTube.

### 1.2. Mục tiêu cốt lõi
1. **Hợp nhất Cổng 3 ➔ 6 thành một cỗ máy điều phối duy nhất (`scripts/studio_pipeline.py`)**: Tự động nhận `job.json`, thực hiện trọn vẹn từ sinh asset bối cảnh/nhân vật, tổng hợp âm thanh Edge-TTS 48kHz, sinh storyboard, tạo 100% video chuyển động AI (`GEN V` qua FlowKit Veo 2), và ráp phim hoàn chỉnh với khung thoại Cyber Chatbox và Thumbnail 3D High-CTR.
2. **Mở rộng Cổng 7 (YouTube Auto-Publisher)**: Tự động đóng gói Publishing Kit (Title chuẩn SEO, Description có Timestamps/Chapters tự động tính, Tags), upload file MP4 1080p, đồng bộ file phụ đề `.srt`, gắn Thumbnail 3D, và trả về đường link YouTube.
3. **Quy chuẩn Bảo Mật & Độc Bản**:
   - **Mặc định Không Công Khai (`unlisted`)**: Cổng 7 luôn luôn tải lên ở chế độ Unlisted để người dùng toàn quyền kiểm tra trước khi công khai.
   - **Quy tắc Fresh-Render**: Tuyệt đối không tái sử dụng hình ảnh hay video clip của các job cũ; mỗi tập phim mới đều được render mới 100%.
4. **Đồng bộ hóa tài liệu toàn hệ thống**: Cập nhật `AGENTS.md`, `CLAUDE.md`, `docs/CINEMATIC_STANDARDS.md`, và các Skill của agent để IDE và các AI subagent luôn ghi nhớ và tuân thủ quy trình 7 Cổng.

---

## 2. NGUYÊN TẮC BẤT DI BẤT DỊCH (CORE MANDATES)

1. **QUY TẮC CỔNG 7 — XUẤT BẢN KHÔNG CÔNG KHAI (UNLISTED PRIVACY MANDATE):**
   - Mọi video do Cổng 7 tự động tải lên YouTube đều mang trạng thái `status.privacyStatus = "unlisted"`.
   - Tuyệt đối không tự ý đặt `public` trừ khi có cờ tường minh `--privacy public`.
   - Đảm bảo gắn đầy đủ Thumbnail 3D và phụ đề tiếng Việt `.srt` lên video.

2. **QUY TẮC FRESH-RENDER (TUYỆT ĐỐI CẤM TÁI SỬ DỤNG ASSET CŨ):**
   - Mỗi job sản xuất mới bắt buộc sinh ra các asset độc bản:
     - Cổng 3: Sinh mới ảnh anchor nhân vật và 2–3 master environment plates nếu chưa có media ID mới dành riêng cho job.
     - Cổng 5: Khung ảnh storyboard được render mới theo prompt kịch bản.
     - Cổng 6: 100% video clip là video AI (`GEN V`) do Veo 2 / Omni Flash sinh mới từ start-frame của chính job đó.
   - Cấm sao chép hoặc trỏ clip video từ các job cũ sang job mới để "đốt cháy giai đoạn".

3. **QUY CHUẨN ĐIỆN ẢNH VẪN LÀ TỐI CAO:**
   - Thời lượng trung bình mỗi shot (ASL): **3.5s – 6.0s**.
   - Giọng đọc: **Microsoft Edge-TTS Vietnamese Neural 48kHz Stereo**, tốc độ nền **luôn ở mức x1.25 (`rate='+25%'`)**.
   - Kịch bản 5 Hồi: Mỗi câu thoại tối đa 20 từ tiếng Việt.
   - Khung thoại: Chuẩn kích cỡ **Cyber Chatbox (1600x125px)**, bo góc 16px, có **Speaker Pill Badge** ở góc trên bên trái, chữ trắng in đậm đổ bóng nhẹ. Cấm dùng hộp đen phụ đề cũ.
   - Thumbnail 3D Điện ảnh: Khai thác Beauty Shot 3D của phim, text neon tương phản cao, viền đổ bóng đen dày 5-7px, chuẩn mobile.

---

## 3. KIẾN TRÚC & THIẾT KẾ THÀNH PHẦN (COMPONENT ARCHITECTURE)

```
VideoAI/
├── scripts/
│   ├── studio_pipeline.py          # [MỚI] Bộ điều phối hợp nhất toàn bộ Cổng 3 -> Cổng 7
│   └── studio_reporter.py          # Live reporter đẩy tiến độ lên Dashboard :8100
├── workshops/workshop-cinematic/
│   └── youtube/
│       ├── auth.py                 # OAuth2 Token manager
│       ├── upload.py               # YouTube API client (Upload, Thumbnail, SRT)
│       └── credentials/            # Lưu token của kênh YouTube
├── output/
│   ├── jobs/<job_id>.json          # Kịch bản đầu vào chuẩn VideoJobSchema
│   └── cinematic/<job_id>/
│       ├── audio/                  # Audio Edge-TTS 48kHz từng shot + manifest
│       ├── frames/                 # Storyboard frames
│       ├── videos/                 # 100% video clips Veo 2 (GEN V)
│       ├── overlays/               # Khung thoại Cyber Chatbox
│       ├── <job_id>.mp4            # Master Film hoàn chỉnh
│       ├── <job_id>.srt            # Phụ đề SRT chuẩn xác
│       ├── <job_id>-thumb.jpg      # Thumbnail 3D High-CTR
│       └── publishing_kit.json     # Metadata đóng gói cho Cổng 7
```

### 3.1. Chi tiết thực thi từng Cổng trong `studio_pipeline.py`

#### 🔹 Cổng 1 & 2: Tiền kỳ & Kịch bản (Thực hiện trực tiếp trong IDE)
- Người dùng đưa ý tưởng/chủ đề ➔ AI biên kịch soạn kịch bản 5 Hồi chuẩn `VideoJobSchema`, tối ưu câu thoại <= 20 từ (tốc độ x1.25), phân rã đủ số lượng shot theo định lượng (55–75 shot cho 5 phút, 100–130 shot cho 10 phút).
- Lưu file tại: `output/jobs/<job_id>.json`.

#### 🔹 Cổng 3: Asset Gate (Fresh Visual Anchors)
- Kiểm tra danh sách nhân vật (`metadata.characters`) và bối cảnh chính (`metadata.virtual_sets`).
- Gửi yêu cầu sang FlowKit API để sinh ảnh chân dung nhân vật và 2–3 master environment plates 4K.
- Lưu trữ Media ID mới vào cấu trúc job.

#### 🔹 Cổng 4: Audio Gate (Edge-TTS 48kHz Suite)
- Tự động chuẩn hóa câu thoại qua `core/phonetics/rules.ts` (xử lý dấu chấm hàng nghìn, số thập phân, phiên bản, từ viết tắt).
- Gọi Microsoft Edge-TTS với tốc độ nền x1.25 và cao độ riêng của từng vai (ví dụ nam chính `-4Hz, +22%`, phản diện `+3Hz, +30%`, nữ chính `+1Hz, +23%`).
- Đo thời lượng chính xác micro-giây của từng file audio bằng `ffprobe` và lưu thành `audio_manifest.json`.

#### 🔹 Cổng 5: Storyboard Gate (Keyframe Generation)
- Dựng 100% khung ảnh phân cảnh kế thừa trực tiếp Media ID từ Cổng 3.
- Lưu trữ tại: `output/cinematic/<job_id>/frames/frame_xxx.png`.

#### 🔹 Cổng 6: Master Assembly Gate (100% GEN V + Cyber Chatbox + Thumb 3D)
- Gửi từng start-frame sang FlowKit `/api/flow/generate-video` để tạo video clip chuyển động AI thực sự (`GEN V` bằng Veo 2 / Omni Flash).
- Ghép các clip video bằng FFmpeg, chèn logo thương hiệu góc trên bên trái, intro bumper (2.0s) và outro bumper (4.5s).
- Đè khung thoại Cyber Chatbox (1600x125px, bán trong suốt `rgba(11, 15, 23, 0.88)`, viền cyan neon 2px, Speaker Pill Badge góc trái).
- Hòa âm âm thanh: Voice Track `0dB`, BGM điện ảnh tự động ducking `-18dB` đến `-20dB` khi có thoại, nâng `-6dB` khi chuyển cảnh.
- Tạo file phụ đề `.srt` đồng bộ từng mili-giây.
- Trích xuất beauty shot đẹp nhất và render **Thumbnail 3D High-CTR** (1280x720 hoặc 1920x1080, font chữ cực đại, viền stroke đen 5-7px, neon gradient).
- Xuất master film tại `output/cinematic/<job_id>.mp4`.

#### 🔹 Cổng 7: YouTube Auto-Publisher Gate (Unlisted Upload)
- Tự động tính toán mốc thời gian thực tế để tạo danh sách **Timestamps/Chapters** trong mô tả YouTube (ví dụ: `00:00 Intro`, `00:02 Cao trào`, `01:45 Giải mã kiến trúc`...).
- Tạo file `output/cinematic/<job_id>/publishing_kit.json`.
- Sử dụng OAuth2 token của kênh YouTube đã xác thực (trong `workshops/workshop-cinematic/youtube/credentials/`).
- Tải file master MP4 lên YouTube thông qua cơ chế Resumable Chunk Upload với quyền riêng tư `privacyStatus = "unlisted"`.
- Upload file phụ đề `.srt` và set hình thu nhỏ Thumbnail 3D.
- Trả về đường link YouTube `https://youtu.be/<video_id>` và ghi nhận vào hệ thống.

---

## 4. GIAO DIỆN DÒNG LỆNH & CỜ ĐIỀU KHIỂN (CLI SPECIFICATION)

Cú pháp thực thi chính:
```powershell
python scripts/studio_pipeline.py --job <job_id> [OPTIONS]
```

### Các tùy chọn tham số:
* `--job <id>`: Mã định danh kịch bản (bắt buộc, ví dụ `job-ai-agent-giaimatech-10min`).
* `--publish-youtube`: Kích hoạt Cổng 7 tự động tải lên YouTube sau khi ráp phim xong.
* `--privacy <unlisted|public|private>`: Thiết lập chế độ riêng tư trên YouTube (Mặc định: `unlisted`).
* `--channel <name>`: Tên cấu hình kênh YouTube trong credentials (mặc định đọc từ `metadata.channel`).
* `--gates <3,4,5,6,7>`: Cho phép chỉ định chạy một hoặc nhiều cổng cụ thể.
* `--dry-run`: Chạy kiểm tra quy trình mà không thực sự gọi API tốn credits hoặc upload.
* `--skip-flow`: Tùy chọn kiểm thử ráp master bằng khung frame mô phỏng khi chưa bật daemon FlowKit.

---

## 5. KẾ HOẠCH ĐỒNG BỘ TÀI LIỆU DỰ ÁN (DOCUMENTATION SYNC PLAN)

Để IDE và tất cả các AI agent làm việc trong tương lai luôn ghi nhớ và tuân thủ chuẩn 7 Cổng:
1. **Cập nhật `AGENTS.md` (Gốc & Cinematic)**:
   - Thêm Cổng 7 (YouTube Unlisted Auto-Publisher) vào Quy trình Phê duyệt.
   - Thêm Quy tắc Fresh-Render (cấm dùng lại asset cũ) vào 12 Quy tắc Bất di bất dịch.
2. **Cập nhật `CLAUDE.md`**:
   - Cập nhật quy trình làm phim từ 6 Cổng thành 7 Cổng.
   - Hướng dẫn gọi nhanh `scripts/studio_pipeline.py`.
3. **Cập nhật `docs/CINEMATIC_STANDARDS.md`**:
   - Thêm Chương 13: Đặc tả Cổng 7 (YouTube Unlisted Publishing Protocol & SEO Metadata).
   - Thêm Quy tắc Fresh-Render vào phần General Policy.
4. **Cập nhật Skills (`.agents/skills/cinematic-director/` & `.claude/skills/cinematic-director/`)**:
   - Cập nhật mô tả kỹ năng và quy trình 7 Cổng.

---

## 6. TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA)

* [ ] `scripts/studio_pipeline.py` hoạt động độc lập và nhận bất kỳ file `job.json` hợp lệ nào.
* [ ] Pipeline chạy mượt mà từ Cổng 3 đến Cổng 6, sinh master video MP4 và 3D Thumbnail đạt chuẩn điện ảnh.
* [ ] Cổng 7 tự động upload video với trạng thái `unlisted`, gắn đúng thumbnail và phụ đề SRT, in link xem `https://youtu.be/...`.
* [ ] Không xảy ra tình trạng tái sử dụng video/ảnh của job cũ (Fresh-Render enforced).
* [ ] Toàn bộ tài liệu (`AGENTS.md`, `CLAUDE.md`, `CINEMATIC_STANDARDS.md`, Skills) được đồng bộ nhất quán 100%.

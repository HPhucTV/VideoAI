# 📖 HƯỚNG DẪN SỬ DỤNG VÀ TRA CỨU CÂU LỆNH
# HỆ THỐNG OMNIVIDEO STUDIO LOCAL (V2.0)

> Hệ thống sản xuất video tự động đa phân xưởng, chạy 100% trên máy tính cá nhân (Windows 11), chi phí 0đ, không phụ thuộc API trả phí.

---

## 🧭 1. TỔNG QUAN 3 CÁCH SỬ DỤNG

Bạn có 3 cách sử dụng hệ thống tùy theo nhu cầu:
1. **Cách 1: Menu Terminal Tương Tác (`studio.bat`)** — Thân thiện nhất, chỉ cần chọn số 1, 2, 3, 4, 5.
2. **Cách 2: Điều Phối Bằng AI Agent (`/omni-director`)** — Ra lệnh bằng văn bản tự nhiên, AI tự chọn xưởng và tạo video.
3. **Cách 3: Chạy Trực Tiếp Bằng CLI (Dòng lệnh)** — Dành cho lập trình viên muốn tự động hóa (Scripting / Cron / Batch).

---

## 🖥️ CÁCH 1: MENU TƯƠNG TÁC NHANH (`studio.bat`)

Chỉ cần nhấp đúp vào file `studio.bat` tại thư mục gốc của dự án (hoặc mở PowerShell gõ `.\studio.bat`):

```text
=================================================================
         🎬 OMNIVIDEO STUDIO LOCAL - HỆ THỐNG PHÂN XƯỞNG        
   (100% Cục Bộ · Chi Phí 0đ · Tối Ưu Cho YouTube & TikTok)      
=================================================================

 [1] 🏭 Xưởng 1: Làm video Tin Tức và Đồ Họa Nhanh (HyperFrames 9:16)
 [2] 🏭 Xưởng 2: Làm video Giải Thích Kiến Thức (Remotion Video-as-Code)
 [3] 🏭 Xưởng 3: Làm video Bảng Trắng Vẽ Tay (Python Whiteboard Animation)
 [4] 🖥️ Mở Remotion Studio Live Preview (Xem trước từng frame trên web)
 [5] 🎨 Mở Whiteboard Region Editor (Kéo thả vùng vẽ không cần server)
 [6] 🛠️ Kiểm tra môi trường hệ thống (Node, Python, FFmpeg, FFprobe)
 [0] 🚪 Thoát
```

* **Phím 4:** Khởi chạy Remotion Studio UI, tự động mở trình duyệt tại `http://localhost:3000` để bạn kéo timeline xem chuyển động từng frame của video giải thích.
* **Phím 5:** Mở trình biên tập vẽ tay Bảng Trắng trên trình duyệt để kéo thả trực quan các vùng hình vẽ, chỉnh thời gian (ms) và hướng vẽ.
* **Phím 6:** Kiểm tra nhanh tình trạng cài đặt Node.js, Python, FFmpeg, FFprobe trên máy.

---

## 🤖 CÁCH 2: DÙNG KỸ NĂNG AI AGENT (`/omni-director`)

Khi trò chuyện trong Antigravity hoặc Claude Code, bạn chỉ cần gõ lệnh `/omni-director` kèm yêu cầu:

### 1. Làm video tin tức nóng (Xưởng 1):
```text
/omni-director https://vnexpress.net/bai-viet-cong-nghe-moi-nhat
```
*hoặc:*
```text
/omni-director Tạo video tin tức 45 giây về việc OpenAI vừa ra mắt tính năng Search mới
```
👉 *Hệ thống sẽ:* Trích xuất nội dung, chia 6 cảnh tin tức, ghép SFX tự động, đọc giọng AI Edge TTS và xuất video 9:16 kèm file `caption.txt` cho TikTok/Shorts.

### 2. Làm video giải thích kiến thức (Xưởng 2):
```text
/omni-director Giải thích khái niệm "Docker Container" cho người mới bắt đầu học lập trình
```
👉 *Hệ thống sẽ:* Lên kịch bản 6 nhịp tâm lý (Hook, Problem, Solution, Workflow, Benefits, Outro), tạo props Remotion và render video đồ họa động.

### 3. Làm video vẽ tay bảng trắng (Xưởng 3):
```text
/omni-director Làm video bảng trắng kể câu chuyện ngắn về sự kiên trì trong cuộc sống
```
👉 *Hệ thống sẽ:* Sinh file lời thoại `input.srt`, tổng hợp giọng đọc `input.mp3`, tạo khung phân cảnh `scene-01.annotation.json` và mở Web Editor để bạn kéo thả vùng vẽ nét tay.

---

## ⌨️ CÁCH 3: DANH MỤC CÂU LỆNH DÒNG LỆNH (CLI REFERENCE)

### ⚡ 1. Công Cụ Lõi Dùng Chung (`core/`)

#### a. Thử nghiệm giọng đọc & Tạo cache âm thanh:
```powershell
node --experimental-strip-types core/bin/tts.js --text "Xin chào các bạn, đây là OmniVideo Studio Local bản 2.0."
```
*Tự động chuẩn hóa ngữ âm tiếng Việt (số, phần trăm, từ viết tắt), đo duration chính xác bằng `ffprobe` và lưu cache vào `core/cache/tts/`.*

#### b. Thử nghiệm chuẩn hóa ngữ âm tiếng Việt:
```powershell
node --experimental-strip-types core/bin/phonetics.js --text "GPT 5.5 tiết kiệm 82.7% chi phí và 1.000.000 lượt API"
```
*Kết quả:* `Gí pi tí năm chấm năm tiết kiệm tám mươi hai phẩy bảy phần trăm chi phí và một triệu lượt A P I`

#### c. Đo độ dài file audio chính xác:
```powershell
node --experimental-strip-types core/bin/audio-probe.js --file core/cache/tts/19a3c3676ff2dadf.mp3 --fps 30
```

---

### 🏭 2. Xưởng 1: Tin Tức & Đồ Họa Nóng (`workshops/workshop-news`)

#### a. Render toàn bộ pipeline từ file kịch bản:
```powershell
npm run pipeline -- ../../output/news/script.json --workspace=workshops/workshop-news
```
*Hoặc dùng npx:*
```powershell
npx tsx workshops/workshop-news/src/cli.ts output/news/script.json
```
*Đầu ra tại:* `output/news/video.mp4` và `output/news/caption.txt`.

#### b. Re-render nhanh (Giữ nguyên giọng đọc, chỉ thay đổi visual trong ~30 giây):
```powershell
npm run rerender --workspace=workshops/workshop-news
```

#### c. Chạy bộ kiểm thử tự động của Xưởng 1:
```powershell
npm test --workspace=workshops/workshop-news
```

---

### 🏭 3. Xưởng 2: Giải Thích Kiến Thức & Video-as-Code (`workshops/workshop-explainer`)

#### a. Mở Remotion Studio xem trước trực quan trên Web (Cổng 3000):
```powershell
npm run dev --workspace=workshops/workshop-explainer
```
*Mở trình duyệt truy cập: `http://localhost:3000`.*

#### b. Chuyển đổi `job.json` sang Remotion Props:
```powershell
node --experimental-strip-types workshops/workshop-explainer/src/job-adapter.ts --job output/sample_job.json
```
*Tự động sinh audio cho từng nhịp và lưu file props tại `workshops/workshop-explainer/public/props.json`.*

#### c. Render video 9:16 (Shorts & TikTok):
```powershell
npx remotion render OmniExplainer-Portrait output/explainer/video-shorts.mp4 --props=workshops/workshop-explainer/public/props.json --gl=angle
```

#### d. Render video 16:9 (YouTube Long-form):
```powershell
npx remotion render OmniExplainer-Landscape output/explainer/video-youtube.mp4 --props=workshops/workshop-explainer/public/props.json --gl=angle
```

#### e. Xuất ảnh tĩnh (Still Frame) để làm Thumbnail:
```powershell
npx remotion still OmniExplainer-Portrait output/explainer/thumbnail.png --props=workshops/workshop-explainer/public/props.json --frame=30 --gl=angle
```

---

### 🏭 4. Xưởng 3: Bảng Trắng Vẽ Tay (`workshops/workshop-whiteboard`)

#### a. Chuyển đổi `job.json` sang file SRT và Annotation:
```powershell
.\workshops\workshop-whiteboard\.venv\Scripts\python.exe workshops\workshop-whiteboard\job_adapter.py output\sample_job.json output\whiteboard\du-an-moi
```
*Tự động tạo:*
- `output/whiteboard/du-an-moi/input.srt` (Phụ đề đồng bộ mili-giây)
- `output/whiteboard/du-an-moi/input.mp3` (Âm thanh nối liền có khoảng nghỉ)
- `output/whiteboard/du-an-moi/scene-01.annotation.json` (Khung tọa độ vẽ tay)

#### b. Mở Trình Biên Tập Vùng Vẽ (Web Region Editor):
Mở trực tiếp file sau bằng Chrome hoặc Edge:
```text
workshops/workshop-whiteboard/assets/preview.html
```

#### c. Render video hoạt họa vẽ tay bằng Python:
```powershell
.\workshops\workshop-whiteboard\.venv\Scripts\python.exe workshops\workshop-whiteboard\scripts\render_stream_whiteboard.py <duong_dan_anh_png> <duong_dan_annotation_json> <duong_dan_output_mp4>
```
*Ví dụ render cảnh mẫu:*
```powershell
.\workshops\workshop-whiteboard\.venv\Scripts\python.exe workshops\workshop-whiteboard\scripts\render_stream_whiteboard.py workshops\workshop-whiteboard\assets\whiteboard\cho-di-nhan-lai\scene-01-trao-o.png workshops\workshop-whiteboard\assets\whiteboard\cho-di-nhan-lai\scene-01-trao-o.annotation.json output\whiteboard\video-whiteboard.mp4
```

---

## 📁 5. CẤU TRÚC THƯ MỤC THÀNH PHẨM (`output/`)

Tất cả video và dữ liệu sau khi sản xuất được gom gọn tại thư mục `output/`:

```text
output/
├── sample_job.json                  # File kịch bản mẫu chung
├── news/                            # Thành phẩm Xưởng 1
│   ├── video.mp4                    # Video tin tức dọc 9:16 (1080x1920)
│   ├── caption.txt                  # Tiêu đề & Hashtag sẵn sàng đăng bài
│   ├── voice.mp3                    # Âm thanh hoàn chỉnh đã mix SFX
│   └── script.txt                   # Lời thoại cho CapCut auto-caption
├── explainer/                       # Thành phẩm Xưởng 2
│   ├── job-sample-docker-24.mp4     # Video Remotion Video-as-Code
│   ├── props.json                   # Dữ liệu props Remotion
│   ├── sample-still.png             # Frame ảnh thumbnail 9:16
│   └── sample-still-landscape.png   # Frame ảnh thumbnail 16:9
└── whiteboard/                      # Thành phẩm Xưởng 3
    ├── test-whiteboard-stream.mp4   # Video hoạt họa nét vẽ tay
    └── job-sample-docker-24/
        ├── input.srt                # File phụ đề SRT chuẩn
        ├── input.mp3                # Audio ghép chuẩn xác
        └── scene-01.annotation.json # Tọa độ vùng vẽ
```

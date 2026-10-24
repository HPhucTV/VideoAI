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
 [6] 🛠️ Kiểm tra môi trường hệ thống (Node, Python, FFmpeg, FFprobe, Blender)
 [7] 🌐 Mở Video Library Dashboard (Web UI quản lý kho video)
 [8] 🎥 Xưởng 4: Hoạt hình 3D Blender (EEVEE Next Cinematic Animation)
 [0] 🚪 Thoát
```

* **Phím 4:** Khởi chạy Remotion Studio UI, tự động mở trình duyệt tại `http://localhost:3000` để bạn kéo timeline xem chuyển động từng frame của video giải thích.
* **Phím 5:** Mở trình biên tập vẽ tay Bảng Trắng trên trình duyệt để kéo thả trực quan các vùng hình vẽ, chỉnh thời gian (ms) và hướng vẽ.
* **Phím 6:** Kiểm tra nhanh tình trạng cài đặt Node.js, Python, FFmpeg, FFprobe, Blender trên máy.
* **Phím 7:** Khởi động Web Dashboard tại `http://localhost:3333` để duyệt, xem và tải về kho video thành phẩm từ mọi phân xưởng.
* **Phím 8:** Khởi chạy pipeline render video 3D từ Blender 5.2 (EEVEE Next).

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

### 🏭 4. Xưởng 3: Bảng Trắng Vẽ Tay & YouTube Audio Drama (`workshops/workshop-whiteboard`)

#### a. Chuẩn bị tài nguyên đa phân cảnh từ `job.json`:
```powershell
.\workshops\workshop-whiteboard\.venv\Scripts\python.exe workshops\workshop-whiteboard\job_adapter.py output\jobs\job-hop-dong-100-ty-tong-tai.json output\whiteboard\job-hop-dong-100-ty-tong-tai
```
*Tự động tạo:*
- `scenes/scene-01/` ... `scenes/scene-09/`: Mỗi phân cảnh có đầy đủ `scene-XX.mp3`, `scene-XX.srt`, `scene-XX.annotation.json` và `IMAGE_PROMPT.md`.
- `input.srt` & `input.mp3` (Toàn cục đồng bộ).

#### b. Xuất video hoàn chỉnh đa phân cảnh (90 FPS, BGM Ducking, Hand Eraser):
```powershell
# Xuất bản chuẩn 90 FPS với nhạc nền và hiệu ứng xóa bảng giữa các cảnh:
.\workshops\workshop-whiteboard\.venv\Scripts\python.exe workshops\workshop-whiteboard\scripts\export_video.py job-hop-dong-100-ty-tong-tai --fps 90

# Xuất bản video dài (Audio Drama 60 phút) KHÔNG khắc phụ đề (giữ nét vẽ thanh sạch):
.\workshops\workshop-whiteboard\.venv\Scripts\python.exe workshops\workshop-whiteboard\scripts\export_video.py job-hop-dong-100-ty-tong-tai --fps 90 --no-subtitles

# Render riêng một phân cảnh rồi tự ghép nối lại toàn bộ video:
.\workshops\workshop-whiteboard\.venv\Scripts\python.exe workshops\workshop-whiteboard\scripts\export_video.py job-hop-dong-100-ty-tong-tai --scene scene-02
```

#### c. Mở Trình Biên Tập Vùng Vẽ (Web Region Editor):
Mở trực tiếp file sau bằng Chrome hoặc Edge:
```text
workshops/workshop-whiteboard/assets/preview.html
```

---

---

### 🎥 5. Xưởng 4: Phim Điện Ảnh AI Cinematic (`workshops/workshop-cinematic`) & 3D Blender (`workshops/workshop-blender`)

#### a. Phim Điện Ảnh AI Cinematic (FlowKit / Google Veo 2 & Imagen 3):
*Sử dụng mô hình Veo 2, Imagen 3, Omni Flash tạo video điện ảnh Hollywood nhất quán nhân vật.*
```powershell
# 1. Kiểm tra trạng thái Agent và Chrome Extension (flow.google.com):
.\workshops\workshop-cinematic\.venv\Scripts\python.exe workshops\workshop-cinematic\scripts\run_pipeline.py --check

# 2. Nạp hợp đồng kịch bản job.json vào cơ sở dữ liệu FlowKit:
.\workshops\workshop-cinematic\.venv\Scripts\python.exe workshops\workshop-cinematic\scripts\run_pipeline.py --job output\jobs\job-xianxia-3d-sample.json --import-only

# 3. Kích hoạt sinh ảnh hàng loạt qua Google Imagen 3:
.\workshops\workshop-cinematic\.venv\Scripts\python.exe workshops\workshop-cinematic\scripts\run_pipeline.py --job job-xianxia-3d-sample --generate-images

# 4. Kích hoạt sinh video hàng loạt qua Google Veo 2 (hoặc Omni Flash):
.\workshops\workshop-cinematic\.venv\Scripts\python.exe workshops\workshop-cinematic\scripts\run_pipeline.py --job job-xianxia-3d-sample --generate-videos --model-family veo

# 5. Ghép nối Master Film hoàn chỉnh (obsidian bumper, drone bass, audio crossfade):
.\workshops\workshop-cinematic\.venv\Scripts\python.exe workshops\workshop-cinematic\scripts\run_pipeline.py --job job-xianxia-3d-sample --build-film
```

#### b. Hoạt Hình 3D Blender Local (EEVEE Next 60 FPS):
```powershell
python workshops/workshop-blender/scripts/export_3d_video.py output/jobs/job-xianxia-3d-sample.json --fps 60
```
*Pipeline tự động:*
1. Nạp kịch bản `job.json` qua `job_adapter.py` để tính toán timeline và camera motions.
2. Sinh giọng đọc Edge TTS và đo thời lượng micro-giây.
3. Kích hoạt Blender 5.2 chạy headless (`blender.exe -b -P scripts/blender_renderer.py`).
4. Dựng không gian 3D, nạp nhân vật anime rigged (`assets/characters/nam-chinh`), pose armature qua `pose_engine.py` và render EEVEE Next 60 FPS.
5. Ghép âm thanh lồng tiếng và nhạc nền BGM ducking chuẩn EBU R128 (-14 LUFS).

---

### 🌐 6. Bảng Điều Khiển Quản Lý Kho Video (Video Library Dashboard)

Khởi động Web UI quản lý kho video thành phẩm:
```powershell
npm run dashboard
```
*Truy cập tại: `http://localhost:3333` để duyệt, xem trước, tải về video và sao chép metadata YouTube.*

---

## 📁 7. CẤU TRÚC THƯ MỤC THÀNH PHẨM (`output/`)

Tất cả video và dữ liệu sau khi sản xuất được gom gọn tại thư mục `output/`:

```text
output/
├── jobs/                                # Nơi lưu trữ các hợp đồng kịch bản job.json
│   ├── job-sample-docker-24.json
│   ├── job-hop-dong-100-ty-tong-tai.json
│   └── job-xianxia-3d-sample.json
├── news/                                # Thành phẩm Xưởng 1
│   ├── video.mp4                        # Video tin tức dọc 9:16 (1080x1920)
│   ├── caption.txt                      # Tiêu đề & Hashtag sẵn sàng đăng bài
│   ├── voice.mp3                        # Âm thanh hoàn chỉnh đã mix SFX
│   └── script.txt                       # Lời thoại
├── explainer/                           # Thành phẩm Xưởng 2
│   ├── job-sample-docker-24.mp4         # Video Remotion Video-as-Code
│   ├── props.json                       # Dữ liệu props Remotion
│   ├── sample-still.png                 # Frame ảnh thumbnail 9:16
│   └── sample-still-landscape.png       # Frame ảnh thumbnail 16:9
├── whiteboard/                          # Thành phẩm Xưởng 3
│   ├── job-hop-dong-100-ty-tong-tai.mp4 # Video vẽ tay 90 FPS hoàn chỉnh (60 phút)
│   ├── job-hop-dong-100-ty-tong-tai-thumb.png
│   ├── job-hop-dong-100-ty-tong-tai-youtube.md # SEO, mô tả & Timestamps/Chapters
│   └── job-hop-dong-100-ty-tong-tai/    # Dữ liệu phân cảnh & âm thanh chi tiết
│       └── scenes/
│           ├── scene-01/ ... scene-09/
├── blender/                             # Thành phẩm Xưởng 4 (Blender 3D)
│   ├── job-xianxia-3d-sample.mp4        # Video 3D EEVEE Next 60 FPS
│   └── job-xianxia-3d-sample-thumb.png  # Thumbnail 3D render
└── cinematic/                           # Thành phẩm Xưởng 4 (FlowKit Veo 2 / Imagen 3)
    ├── job-xianxia-3d-sample-flowkit.json # Bản ghi ánh xạ FlowKit SQLite
    └── job-xianxia-3d-sample/           # Video các cảnh, bumpers & master film
```

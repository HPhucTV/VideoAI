# 🗺️ LỘ TRÌNH TRIỂN KHAI DỰ ÁN (PROJECT ROADMAP)
# HỆ THỐNG OMNIVIDEO STUDIO LOCAL (V2.0)

> Checklist theo dõi tiến độ thi công hệ thống. Mọi quy chuẩn về Template, Nhịp điệu và Vùng an toàn đều tuân theo [**Cẩm Nang Chi Tiết (WORKSHOPS_SPECIFICATION.md)**](WORKSHOPS_SPECIFICATION.md).

---

## 📊 TỔNG QUAN 5 GIAI ĐOẠN

```
[Phase 1: Môi trường & Nền tảng] ──► [Phase 2: Lõi Dùng Chung & job.json] ──► [Phase 3: Tích hợp 3 Xưởng] ──► [Phase 4: CLI Launcher & Skills] ──► [Phase 5: Kiểm Thử Thực Tế]
```

---

## 📌 GIAI ĐOẠN 1: CHUẨN BỊ MÔI TRƯỜNG & HẠ TẦNG LOCAL
*Mục tiêu: Đảm bảo máy tính cá nhân của bạn có đủ mọi công cụ cần thiết để chạy 100% offline.*

- [x] **Bước 1.1:** Giải nén và khảo sát toàn bộ 3 mã nguồn gốc (`auto-video-gen`, `remotion-cuongit-template`, `whiteboard-video`).
- [x] **Bước 1.2:** Cài đặt các công cụ nền tảng hệ điều hành Windows:
  - [x] Node.js LTS (phiên bản `v24.21.0` - đáp ứng `>= 20.12.0`).
  - [x] FFmpeg & FFprobe (phiên bản `9.0.2` từ Gyan.dev).
  - [x] Python 3.12 (phiên bản `3.12.10` đã có sẵn và cấu hình venv).
- [x] **Bước 1.3:** Tạo shortcut `studio.bat` với tham số `powershell -ExecutionPolicy Bypass -NoProfile -File studio.ps1` có UTF-8 BOM, chạy mượt mà không bị lỗi cú pháp.
- [x] **Bước 1.4:** Thiết lập file mẫu `.env.example` chuẩn hóa, mặc định Edge TTS 0đ và đường dẫn cache duy nhất `core/cache/tts/`.

---

## 📌 GIAI ĐOẠN 2: HỢP ĐỒNG DỮ LIỆU & LÕI DÙNG CHUNG (SHARED CORE ENGINE)
*Mục tiêu: Xây dựng hợp đồng dữ liệu trung tâm `job.json` và Single Source of Truth cho Phonetics & Duration.*

- [x] **Bước 2.1:** Khởi tạo cấu trúc npm workspaces tại thư mục gốc:
  - `core/` (Lõi chung)
  - `workshops/` (Chứa 3 xưởng sản xuất)
  - `shared-assets/` (SFX, BGM, Fonts, Watermark)
  - `output/` (Nơi xuất video thành phẩm theo từng xưởng)
- [x] **Bước 2.2:** Định nghĩa Schema **`job.json`** bằng Zod tại `core/schema/job.ts`:
  - Quy chuẩn metadata, danh sách beats (theo tỉ lệ % ngân sách nhịp), audio path, visual specs.
- [x] **Bước 2.3:** Xây dựng **Vietnamese Phonetics Engine** (`core/phonetics/`):
  - Viết 1 lần duy nhất bằng TypeScript (`core/phonetics/rules.ts`).
  - Xử lý phân biệt theo ngữ cảnh: số hàng nghìn (`1.000.000` → một triệu), số thập phân (`82.7%` → tám mươi hai phẩy bảy phần trăm), số phiên bản (`GPT 5.5` → gí pi tí năm chấm năm), từ viết tắt (`AI`, `API`).
  - Expose CLI `node --experimental-strip-types core/bin/phonetics.js` để Python (Xưởng 3) gọi trực tiếp.
  - Bảng test fixture tự động `core/phonetics/__tests__/fixtures.json`.
- [x] **Bước 2.4:** Xây dựng **Audio Probing & Cache Hub** (`core/audio/probe.ts` & `core/cache/tts/`):
  - Đo độ dài audio ưu tiên bằng `ffprobe` (chính xác micro-giây), dùng MP3 header parser làm fallback.
  - Expose CLI `node --experimental-strip-types core/bin/audio-probe.js` cho mọi phân xưởng.
  - Tự động băm SHA-256 câu thoại để lưu và tái sử dụng giọng đọc trong `core/cache/tts/`.
- [x] **Bước 2.5:** Chuẩn hóa kho tài nguyên `shared-assets/`:
  - Thư mục SFX (whoosh, pop, camera, typing, ding) và branding (`avatar.png`, `logo.svg`).

---

## 📌 GIAI ĐOẠN 3: TÍCH HỢP & NÂNG CẤP 3 XƯỞNG SẢN XUẤT (WORKSHOPS INTEGRATION)
*Mục tiêu: Đưa từng mã nguồn vào xưởng tương ứng, xây dựng Adapter kết nối với `job.json`.*

### 🏭 Xưởng 1: Tin Tức & Đồ Họa Nóng (`workshops/workshop-news`)
- [x] **Bước 3.1.1:** Di chuyển mã nguồn `auto-video-gen` vào `workshops/workshop-news`.
- [x] **Bước 3.1.2:** Xây dựng Adapter chuyển đổi `job.json` → `script.json` (`workshops/workshop-news/src/job-adapter.ts`).
- [x] **Bước 3.1.3:** Kết nối trực tiếp pipeline với `core/phonetics` và `core/cache/tts/`.
- [x] **Bước 3.1.4:** Tối ưu hóa 6 template HyperFrames cho chuẩn Safe Zone và tốc độ 30 FPS mặc định.
- [x] **Bước 3.1.5:** Tự động xuất file `caption.txt` cho TikTok/Shorts.

### 🏭 Xưởng 2: Giải Thích Kiến Thức & Video-as-Code (`workshops/workshop-explainer`)
- [x] **Bước 3.2.1:** Di chuyển mã nguồn `remotion-cuongit-template` vào `workshops/workshop-explainer`.
- [x] **Bước 3.2.2:** Xây dựng Adapter nạp `job.json` vào Remotion Composition Props động (`workshops/workshop-explainer/src/job-adapter.ts`).
- [x] **Bước 3.2.3:** Áp dụng công thức 6 nhịp tâm lý theo Tỉ lệ phần trăm (%) ngân sách nhịp (`OmniExplainer.tsx`).
- [x] **Bước 3.2.4:** Cấu hình Remotion Studio Web UI (`npm run dev`) để preview trực quan trên trình duyệt.
- [x] **Bước 3.2.5:** Hỗ trợ render cả 9:16 (Shorts/TikTok) và 16:9 (YouTube Video) qua `OmniExplainer-Portrait` & `OmniExplainer-Landscape`.

### 🏭 Xưởng 3: Bảng Trắng Vẽ Tay (`workshops/workshop-whiteboard`)
- [x] **Bước 3.3.1:** Di chuyển mã nguồn `whiteboard-video` vào `workshops/workshop-whiteboard`.
- [x] **Bước 3.3.2:** Khởi tạo môi trường ảo Python độc lập `.venv` bằng `workshops/workshop-whiteboard/prepare_env.py` (đã cài đặt đầy đủ opencv-python, numpy, av, Pillow, edge-tts).
- [x] **Bước 3.3.3:** Xây dựng Adapter chuyển `job.json` → `input.srt` + `scene.annotation.json` (`workshops/workshop-whiteboard/job_adapter.py`).
- [x] **Bước 3.3.4:** Tích hợp gọi CLI `core/bin/phonetics.js` và `core/bin/audio-probe.js` từ Python pipeline với độ chính xác micro-giây.
- [x] **Bước 3.3.5:** Việt hóa và nâng cấp giao diện Web Editor kéo thả vùng vẽ (`preview.html`).

---

## 📌 GIAI ĐOẠN 4: BỘ ĐIỀU HÀNH TRUNG TÂM & KỸ NĂNG AI AGENT (ORCHESTRATION & SKILLS)
*Mục tiêu: Đơn giản hóa tối đa cách sử dụng qua Menu Terminal và AI Slash Commands.*

- [x] **Bước 4.1:** Xây dựng **Menu điều khiển trung tâm (`studio.bat` & `studio.ps1`)**:
  - Giao diện chọn xưởng trực quan tiếng Việt, hỗ trợ kiểm tra môi trường, mở Web Region Editor, Remotion Studio.
- [x] **Bước 4.2:** Đồng bộ bộ kỹ năng AI Agent:
  - Tạo thư mục kỹ năng **`omni-director`** điều phối toàn diện.
  - Script tự động đồng bộ `scripts/sync-skills.ps1` giữa `.agents/skills/` (cho Antigravity IDE) và `.claude/skills/` (cho Claude Code).

---

## 📌 GIAI ĐOẠN 5: KIỂM THỬ THỰC TẾ & XUẤT BẢN THÀNH PHẨM (TESTING & PRODUCTION)
*Mục tiêu: Sản xuất thử nghiệm 3 video thực tế và kiểm tra chất lượng hiển thị trên YouTube và TikTok.*

- [x] **Bước 5.1:** Render thử nghiệm video tin tức từ Xưởng 1 (chuẩn 9:16 @ 30fps):
  - Thành phẩm: `output/news/video.mp4` (158.9 MB, 36.18s, 1185 frames).
  - Phụ trợ: `output/news/caption.txt` & `output/news/voice.mp3`.
- [x] **Bước 5.2:** Render thử nghiệm video giải thích Remotion từ Xưởng 2:
  - Thành phẩm: `output/explainer/job-sample-docker-24.mp4` (4.01 MB @ 30fps).
  - Still Frames: `sample-still.png` (9:16) & `sample-still-landscape.png` (16:9).
- [x] **Bước 5.3:** Render thử nghiệm video bảng trắng vẽ tay từ Xưởng 3:
  - Thành phẩm: `output/whiteboard/test-whiteboard-stream.mp4` (2.27 MB, 60fps).
  - Khung SRT & Annotation: `output/whiteboard/job-sample-docker-24/input.srt` & `scene-01.annotation.json`.
- [x] **Bước 5.4:** Kiểm tra độ khớp âm thanh, vùng an toàn Safe Zones trên thiết bị di động thật (Margin Top 140px, Bottom 360px, Right 120px; thời lượng âm thanh khớp chính xác từng mili-giây).

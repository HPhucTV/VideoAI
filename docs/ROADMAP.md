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
- [ ] **Bước 1.2:** Cài đặt các công cụ nền tảng hệ điều hành Windows:
  - [ ] Node.js LTS (phiên bản `>= 20.12.0`) để chạy Remotion và HyperFrames.
  - [ ] FFmpeg & FFprobe (bắt buộc cho việc đo duration chính xác micro-giây, mix âm thanh và render video).
  - [ ] Python 3.12 (đã có sẵn trên máy) để chạy Xưởng Bảng trắng vẽ tay.
- [ ] **Bước 1.3:** Tạo shortcut `studio.bat` với tham số `powershell -ExecutionPolicy Bypass -NoProfile -File studio.ps1` để chạy mượt mà không bị Windows chặn policy.
- [ ] **Bước 1.4:** Thiết lập file mẫu `.env.example` chuẩn hóa, mặc định Edge TTS 0đ và đường dẫn cache duy nhất `core/cache/tts/`.

---

## 📌 GIAI ĐOẠN 2: HỢP ĐỒNG DỮ LIỆU & LÕI DÙNG CHUNG (SHARED CORE ENGINE)
*Mục tiêu: Xây dựng hợp đồng dữ liệu trung tâm `job.json` và Single Source of Truth cho Phonetics & Duration.*

- [ ] **Bước 2.1:** Khởi tạo cấu trúc npm workspaces tại thư mục gốc:
  - `core/` (Lõi chung)
  - `workshops/` (Chứa 3 xưởng sản xuất)
  - `shared-assets/` (SFX, BGM, Fonts, Watermark)
  - `output/` (Nơi xuất video thành phẩm theo từng xưởng)
- [ ] **Bước 2.2:** Định nghĩa Schema **`job.json`** bằng Zod tại `core/schema/job.ts`:
  - Quy chuẩn metadata, danh sách beats (theo tỉ lệ % ngân sách nhịp), audio path, visual specs.
- [ ] **Bước 2.3:** Xây dựng **Vietnamese Phonetics Engine** (`core/phonetics/`):
  - Viết 1 lần duy nhất bằng TypeScript.
  - Xử lý phân biệt theo ngữ cảnh: số hàng nghìn (`1.000.000`), số thập phân (`82.7%`), số phiên bản (`GPT 5.5`), từ viết tắt (`AI`, `API`).
  - Expose CLI `node core/bin/phonetics.js` để Python (Xưởng 3) gọi trực tiếp.
  - Bảng test fixture tự động `core/phonetics/__tests__/fixtures.json`.
- [ ] **Bước 2.4:** Xây dựng **Audio Probing & Cache Hub** (`core/audio/` & `core/cache/tts/`):
  - Đo độ dài audio ưu tiên bằng `ffprobe`, dùng MP3 header parser làm fallback.
  - Tự động băm SHA-256 câu thoại để lưu và tái sử dụng giọng đọc trong `core/cache/tts/`.
- [ ] **Bước 2.5:** Chuẩn hóa kho tài nguyên `shared-assets/`:
  - Thư mục SFX (whoosh, pop, camera, typing, ding) và BGM bản quyền miễn phí.

---

## 📌 GIAI ĐOẠN 3: TÍCH HỢP & NÂNG CẤP 3 XƯỞNG SẢN XUẤT (WORKSHOPS INTEGRATION)
*Mục tiêu: Đưa từng mã nguồn vào xưởng tương ứng, xây dựng Adapter kết nối với `job.json`.*

### 🏭 Xưởng 1: Tin Tức & Đồ Họa Nóng (`workshops/workshop-news`)
- [ ] **Bước 3.1.1:** Di chuyển mã nguồn `auto-video-gen` vào `workshops/workshop-news`.
- [ ] **Bước 3.1.2:** Xây dựng Adapter chuyển đổi `job.json` → `script.json`.
- [ ] **Bước 3.1.3:** Kết nối với `core/phonetics` và `core/cache/tts/`.
- [ ] **Bước 3.1.4:** Tối ưu hóa 6 template HyperFrames cho chuẩn Safe Zone và tốc độ 30 FPS mặc định.
- [ ] **Bước 3.1.5:** Tự động xuất file `caption.txt` cho TikTok/Shorts.

### 🏭 Xưởng 2: Giải Thích Kiến Thức & Video-as-Code (`workshops/workshop-explainer`)
- [ ] **Bước 3.2.1:** Di chuyển mã nguồn `remotion-cuongit-template` vào `workshops/workshop-explainer`.
- [ ] **Bước 3.2.2:** Xây dựng Adapter nạp `job.json` vào Remotion Composition Props.
- [ ] **Bước 3.2.3:** Áp dụng công thức 6 nhịp tâm lý theo Tỉ lệ phần trăm (%) ngân sách nhịp.
- [ ] **Bước 3.2.4:** Cấu hình Remotion Studio Web UI (`npm run dev`) để preview trực quan trên trình duyệt.
- [ ] **Bước 3.2.5:** Hỗ trợ render cả 9:16 (Shorts/TikTok) và 16:9 (YouTube Video).

### 🏭 Xưởng 3: Bảng Trắng Vẽ Tay (`workshops/workshop-whiteboard`)
- [ ] **Bước 3.3.1:** Di chuyển mã nguồn `whiteboard-video` vào `workshops/workshop-whiteboard`.
- [ ] **Bước 3.3.2:** Khởi tạo môi trường ảo Python độc lập `.venv` bằng `workshops/workshop-whiteboard/prepare_env.py`.
- [ ] **Bước 3.3.3:** Xây dựng Adapter chuyển `job.json` → `input.srt` + `scene.annotation.json`.
- [ ] **Bước 3.3.4:** Tích hợp gọi CLI `core/bin/phonetics.js` và `core/bin/audio-probe.js` từ Python.
- [ ] **Bước 3.3.5:** Việt hóa và nâng cấp giao diện Web Editor kéo thả vùng vẽ (`preview.html`).

---

## 📌 GIAI ĐOẠN 4: BỘ ĐIỀU HÀNH TRUNG TÂM & KỸ NĂNG AI AGENT (ORCHESTRATION & SKILLS)
*Mục tiêu: Đơn giản hóa tối đa cách sử dụng qua Menu Terminal và AI Slash Commands.*

- [ ] **Bước 4.1:** Xây dựng **Menu điều khiển trung tâm (`studio.bat` & `studio.ps1`)**:
  - Giao diện chọn xưởng trực quan, tự động gọi Node/Python mà không cần người dùng nhớ lệnh dài.
- [ ] **Bước 4.2:** Đồng bộ bộ kỹ năng AI Agent:
  - Tạo thư mục kỹ năng **`omni-director`** điều phối toàn diện.
  - Script tự động đồng bộ giữa `.agents/skills/` (cho Antigravity IDE) và `.claude/skills/` (cho Claude Code).
  - Tự động nhận diện ý tưởng để sinh ra file `job.json` chuẩn trước khi phân bổ vào các xưởng.

---

## 📌 GIAI ĐOẠN 5: KIỂM THỬ THỰC TẾ & XUẤT BẢN THÀNH PHẨM (TESTING & PRODUCTION)
*Mục tiêu: Sản xuất thử nghiệm 3 video thực tế và kiểm tra chất lượng hiển thị trên YouTube và TikTok.*

- [ ] **Bước 5.1:** Render thử nghiệm video tin tức từ Xưởng 1 (chuẩn 9:16 @ 30fps).
- [ ] **Bước 5.2:** Render thử nghiệm video giải thích Remotion từ Xưởng 2 (kiểm tra timeline live trên Web Studio).
- [ ] **Bước 5.3:** Render thử nghiệm video bảng trắng vẽ tay từ Xưởng 3 (kiểm tra nét vẽ tay và Web Region Editor).
- [ ] **Bước 5.4:** Kiểm tra độ khớp âm thanh, vùng an toàn Safe Zones trên thiết bị di động thật.

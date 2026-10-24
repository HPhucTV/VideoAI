# 🗺️ LỘ TRÌNH TRIỂN KHAI DỰ ÁN (PROJECT ROADMAP)
# HỆ THỐNG OMNIVIDEO STUDIO LOCAL (V2.0)

> Checklist theo dõi tiến độ thi công hệ thống. Mọi quy chuẩn về Template, Nhịp điệu và Vùng an toàn đều tuân theo [**Cẩm Nang Chi Tiết (WORKSHOPS_SPECIFICATION.md)**](WORKSHOPS_SPECIFICATION.md).

---

## 📊 TỔNG QUAN 8 GIAI ĐOẠN

```
[Phase 1: Nền tảng] ──► [Phase 2: Lõi job.json] ──► [Phase 3: Tích hợp 3 Xưởng] ──► [Phase 4: Launcher & Skills] ──► [Phase 5: Kiểm Thử]
        ──► [Phase 6: Xưởng 3 Đa Cảnh & YouTube 60m] ──► [Phase 7: Xưởng 4 Blender 3D] ──► [Phase 8: Tái Cấu Trúc Xưởng 4 FlowKit]
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

---

## 📌 GIAI ĐOẠN 6: NÂNG CẤP XƯỞNG 3 ĐA PHÂN CẢNH, XÓA BẢNG VÀ TRUYỆN AUDIO 60 PHÚT (COMPLETED)
*Mục tiêu: Đưa Xưởng 3 trở thành cỗ máy sản xuất truyện audio & video dài chuyên nghiệp cho YouTube.*

- [x] **Bước 6.1: Thuật toán phân cụm đa cảnh (`cluster_beats_into_scenes`)**:
  - Tự động nhóm các beat theo chương (`badge`) hoặc số lượng tối đa (`max_beats_per_scene`).
  - Sinh thư mục con cục bộ `scenes/scene-XX/` chứa `scene-XX.mp3`, `scene-XX.srt`, `scene-XX.annotation.json` và `IMAGE_PROMPT.md`.
- [x] **Bước 6.2: Hoạt cảnh bàn tay cầm khăn lau xóa bảng (`--with-eraser`)**:
  - Triển khai thuật toán lau bảng đường ziczac hình sin mềm mại (`sr._feathered_disk`) đưa canvas về nền giấy kem `#F6F1E3`.
  - Kích hoạt giữa các phân cảnh nối tiếp nhau và tự động tắt ở cảnh cuối cùng.
- [x] **Bước 6.3: Nâng cấp pipeline xuất video đa phân cảnh (`export_video.py`)**:
  - Hỗ trợ chuẩn khung hình siêu mượt **90 FPS**.
  - Hòa trộn BGM Ducking 6.0:1 tự động hạ âm nền khi có giọng đọc.
  - Tự động ghép nối các phân cảnh thành video tổng bằng `merge_scenes.py` không suy hao chất lượng.
- [x] **Bước 6.4: Tùy chọn tắt phụ đề (`--no-subtitles`) & Tự động tạo YouTube Metadata**:
  - Tùy chọn `--no-subtitles` giúp render nhanh với `-c:v copy` và giữ khung vẽ nét doodle thanh sạch.
  - Tự động tạo gói YouTube SEO, tiêu đề, mô tả và bảng Timestamps/Chapters (`export_metadata.py`).
- [x] **Bước 6.5: Sản xuất thành công video Audio Drama dài 60 phút**:
  - Thành phẩm: `output/whiteboard/job-hop-dong-100-ty-tong-tai.mp4` (Thời lượng: 01:00:05, 355.5 MB, 90 FPS, 9 chương hồi, 9.319 từ).

---

## 📌 GIAI ĐOẠN 7: KHỞI TẠO XƯỞNG 4 BLENDER 3D VÀ VIDEO LIBRARY DASHBOARD (COMPLETED)
*Mục tiêu: Xây dựng nền tảng đồ họa không gian 3D và Web UI quản lý kho video.*

- [x] **Bước 7.1: Bổ sung enum `"blender"` vào Zod schema `core/schema/job.ts`**.
- [x] **Bước 7.2: Xây dựng `job_adapter.py` cho Xưởng 4**:
  - Đọc `job.json`, tính toán timeline frames, camera motion (dolly, orbit, pan).
- [x] **Bước 7.3: Xây dựng thư viện nhân vật anime 3D rigged**:
  - Cấu trúc `assets/characters/nam-chinh` và `nu-chinh` định dạng GLB/GLTF.
- [x] **Bước 7.4: Xây dựng `pose_engine.py`**:
  - Tự động ánh xạ xương humanoid, thiết lập tư thế và hoạt ảnh chớp mắt ngẫu nhiên tự nhiên.
- [x] **Bước 7.5: Pipeline xuất video 3D (`scripts/export_3d_video.py`)**:
  - Dựng bối cảnh procedural 3D (đài tế, trụ đá phong hóa, thần kiếm, rim lighting).
  - Render bằng EEVEE Next 60 FPS kết hợp hòa trộn âm thanh chuẩn EBU R128 (-14 LUFS).
  - Thành phẩm mẫu: `output/blender/job-xianxia-3d-sample.mp4`.
- [x] **Bước 7.6: Xây dựng Web UI Video Library Dashboard (`dashboard/server.ts`)**:
  - Giao diện web chạy trên cổng `3333` giúp quản lý, xem trước và tải video từ cả 4 xưởng.

---

## 📌 GIAI ĐOẠN 8: TÁI CẤU TRÚC XƯỞNG 4 VỚI NỀN TẢNG FLOWKIT CINEMATIC (COMPLETED)
*Mục tiêu: Đập đi xây dựng lại Xưởng 4, tích hợp công nghệ AI Generative Video (Google Flow / Veo 2 / Imagen 3) thông qua nền tảng FlowKit.*

- [x] **Bước 8.1: Khảo sát và giải mã toàn diện kiến trúc repo FlowKit (`workshops/workshop-cinematic`)**:
  - Phân tích cơ chế Chrome Extension (MV3) bridge kết nối WebSocket (`:9222`) với local FastAPI Agent (`:8100`).
  - Nắm vững cách ký `batchexecute` RPCs và mint token reCAPTCHA single-use trực tiếp trong ngữ cảnh tab đăng nhập `flow.google.com`.
  - Nghiên cứu cơ chế nhất quán nhân vật (Character consistency references), ghép cảnh chéo (scene chaining), và ráp phim Hollywood master film.
- [x] **Bước 8.2: Thiết lập môi trường Python & Dependencies**:
  - Tạo virtualenv Python 3.12 (`workshops/workshop-cinematic/.venv/`).
  - Cài đặt đầy đủ `fastapi`, `uvicorn`, `aiosqlite`, `websockets`, `google-api-python-client`, `pytest`, `pytest-asyncio`.
  - Cài đặt và build thành công React Ops Console Dashboard (`workshops/workshop-cinematic/dashboard`).
- [x] **Bước 8.3: Mở rộng Hợp Đồng Kịch Bản `core/schema/job.ts`**:
  - Bổ sung giá trị `"cinematic"` vào enum `workshop`.
  - Bổ sung các chuyển động camera điện ảnh (`orbit_360`, `dolly_in`, `dolly_out`, `tilt_up`, `tilt_down`, `fpv`) vào `VisualCueSchema`.
  - Đảm bảo 100% tương thích ngược với `"blender"` (Legacy local render).
- [x] **Bước 8.4: Xây dựng Job Adapter (`workshops/workshop-cinematic/job_adapter.py`)**:
  - Ánh xạ tự động từ `job.json` sang FlowKit Project, Characters, Scenes, Cues trong SQLite `flow_agent.db`.
  - Viết bộ unit test `tests/test_cinematic_adapter.py` đạt 100% pass.
- [x] **Bước 8.5: Xây dựng CLI Pipeline Runner (`scripts/run_pipeline.py`)**:
  - Cung cấp lệnh CLI tổng hợp: kiểm tra sức khỏe Agent/Extension (`--check`), nạp kịch bản (`--import-only`), kiểm tra trạng thái (`--status`), kích hoạt sinh ảnh hàng loạt (`--generate-images`), kích hoạt sinh video Veo 2 (`--generate-videos`), và ghép Master Film (`--build-film`).
- [x] **Bước 8.6: Tích hợp vào Studio Launcher (`studio.ps1`)**:
  - Menu [8] nâng cấp thành menu tương tác chuyên biệt cho Cinematic Studio với đầy đủ tùy chọn khởi chạy Agent, Dashboard, Runner và hướng dẫn Extension.



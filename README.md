# 🎬 OmniVideo Studio Local (v2.2)

> **Hệ thống sản xuất video tự động đa phân xưởng, vận hành 100% trên máy tính cá nhân (Windows 11), chi phí 0đ, chuẩn hóa âm thanh - hình ảnh tối ưu cho YouTube & TikTok.**

👉 **Người mới bắt đầu hoặc chưa rành kỹ thuật? Xem ngay: [Hướng Dẫn Cài Đặt Chi Tiết Từ A Đến Z (HUONG_DAN_CAI_DAT.md)](HUONG_DAN_CAI_DAT.md)**

---

## 🧭 Danh Mục 5 Phân Xưởng Sản Xuất

| Phân xưởng | Thư mục | Công nghệ cốt lõi | Chuẩn FPS | Thời lượng tối ưu | Định dạng & Thể loại |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **🏭 Xưởng 1: Tin Tức & Đồ Họa Nhanh** | `workshops/workshop-news` | HyperFrames (HTML/CSS + GSAP) | **30 FPS** | 45 – 65 giây | 9:16 Dọc · Tin tức công nghệ, so sánh, review GitHub |
| **🏭 Xưởng 2: Giải Thích & Video-as-Code** | `workshops/workshop-explainer` | Remotion 4.0 (React 19 + Tailwind v4) | **30 FPS** | 1 – 8 phút | 9:16 & 16:9 · Bài giảng công nghệ, System Design, AI |
| **🏭 Xưởng 3: Vẽ Tay Bảng Trắng & Audio Drama** | `workshops/workshop-whiteboard` | Python 3.12 (OpenCV + PyAV + Edge-TTS) | **90 FPS** | 1 – 60+ phút | 16:9 & 9:16 · Truyện audio YouTube, triết lý, sách nói |
| **🏭 Xưởng 4: Phim Điện Ảnh 3D & Donghua** | `workshops/workshop-cinematic` & `workshop-blender` | Google Veo 2 / Imagen 3 / Blender 5.2 & Edge-TTS | **24 / 60 FPS** | 3 – 10 phút | 16:9 & 9:16 · Phim điện ảnh 3D, Donghua Tiên hiệp, Cyber Chatbox |
| **🏭 Xưởng 5: Threads & Social Drama** | `workshops/workshop-threads` | Headless Chrome Screenshot + FFmpeg + Edge-TTS | **60 FPS** | 45 – 90 giây | 9:16 Dọc · Threads viral, Meme pop, Gameplay Minecraft/GTA |

---

## 🌟 Tính Năng Nổi Bật

- **Lõi Dùng Chung (`core/`)**:
  - Hợp đồng dữ liệu duy nhất `job.json` chuẩn hóa kịch bản, nhịp tâm lý (Beats) và camera cues.
  - Bộ chuẩn hóa ngữ âm tiếng Việt `core/phonetics` thông minh theo ngữ cảnh (số tiền, thập phân, phiên bản, từ viết tắt).
  - Đo thời lượng chính xác micro-giây bằng `ffprobe` và hệ thống băm cache âm thanh SHA-256 (`core/cache/tts/`).
- **Xưởng 3 Đa Phân Cảnh & Audio Drama 60 Phút**:
  - Phân cụm beat thành scene tự động (`cluster_beats_into_scenes`).
  - Hoạt cảnh bàn tay cầm giẻ lau bảng ziczac (**Hand Eraser**) mềm mại giữa các phân cảnh.
  - Tốc độ khung hình **90 FPS** mượt mà, hòa âm BGM Sidechain Audio Ducking 6:1.
  - Tự động xuất gói YouTube SEO Metadata & Timestamps/Chapters.
  - Tùy chọn `--no-subtitles` giữ nét vẽ tay tối giản, sạch sẽ.
- **Xưởng 4 3D Animation**:
  - Thư viện nhân vật anime 3D rigged (`nam-chinh`, `nu-chinh` GLB).
  - Bộ máy điều khiển tư thế xương humanoid & chớp mắt tự động (`pose_engine.py`).
  - Đường bay camera 3D điện ảnh (dolly, orbit, pan tracking).
  - *(Đang nghiên cứu đập đi xây dựng lại với nền tảng FlowKit: Google Flow, Veo 2, Imagen 3)*.
- **Bảng Điều Khiển Video Library Dashboard (`dashboard/`)**:
  - Web UI quản lý kho video thành phẩm, xem trước video và tải về tại `http://localhost:3333`.

---

## 🚀 Khởi Động Nhanh

### 1. Menu Tương Tác Cục Bộ
Chạy file batch tại thư mục gốc:
```powershell
.\studio.bat
```
Chọn các phím chức năng `[1]` đến `[8]` để làm video, mở Remotion Studio (`:3000`), mở Whiteboard Editor, hoặc khởi chạy Dashboard (`:3333`).

### 2. Quản Lý Kho Video (Dashboard)
```powershell
npm run dashboard
```
Mở trình duyệt tại: `http://localhost:3333`.

---

## 📚 Tài Liệu Kỹ Thuật

- [Cẩm Nang 4 Phân Xưởng (WORKSHOPS_SPECIFICATION.md)](file:///c:/Users/tranh/Documents/Duy/VideoAI/docs/WORKSHOPS_SPECIFICATION.md) — Quy chuẩn template, an toàn Safe Zones và ngữ âm.
- [Hướng Dẫn Sử Dụng & Tra Cứu CLI (USER_GUIDE.md)](file:///c:/Users/tranh/Documents/Duy/VideoAI/docs/USER_GUIDE.md) — Danh mục câu lệnh chi tiết từng xưởng.
- [Kiến Trúc Tổng Thể (BRAINSTORMING_AND_ARCHITECTURE.md)](file:///c:/Users/tranh/Documents/Duy/VideoAI/docs/BRAINSTORMING_AND_ARCHITECTURE.md) — Sơ đồ luồng dữ liệu và adapter.
- [Lộ Trình Triển Khai (ROADMAP.md)](file:///c:/Users/tranh/Documents/Duy/VideoAI/docs/ROADMAP.md) — 8 giai đoạn phát triển hệ thống.
- [Đặc Tả Kịch Bản Beat v2.1 (BEATS_SPECIFICATION.md)](file:///c:/Users/tranh/Documents/Duy/VideoAI/docs/BEATS_SPECIFICATION.md) — 5 khuôn mẫu kịch bản và kỹ thuật giữ chân người xem.
- [Cài Đặt Môi Trường Windows 11 (LOCAL_ENVIRONMENT_SETUP.md)](file:///c:/Users/tranh/Documents/Duy/VideoAI/docs/LOCAL_ENVIRONMENT_SETUP.md) — Thiết lập Node.js, Python, FFmpeg, Blender.

# 💻 HƯỚNG DẪN CÀI ĐẶT MÔI TRƯỜNG LOCAL TRÊN WINDOWS 11
# OMNIVIDEO STUDIO - 100% CỤC BỘ & MIỄN PHÍ (V2.0)

> Hệ thống OmniVideo Studio được thiết kế để chạy **100% trên máy tính cá nhân của bạn (Windows 11)**, hoàn toàn riêng tư, không cần chi trả tiền thuê server hay dịch vụ SaaS đắt đỏ.

---

## 1. YÊU CẦU PHẦN CỨNG & CÔNG CỤ CỐT LÕI

| Công cụ | Phiên bản khuyến nghị | Mục đích sử dụng | Trạng thái trên máy |
| :--- | :--- | :--- | :--- |
| **Python** | Python 3.10 – 3.12 | Chạy Xưởng 3 (Bảng trắng vẽ tay), OpenCV, PyAV | **Đã có sẵn** (`Python 3.12.10`) |
| **Chocolatey** | Choco 2.x | Quản lý và cài đặt tự động các gói phần mềm | **Đã có sẵn** (`Choco 2.7.4`) |
| **Node.js** | **Node.js >= 20.12.0 LTS** | Chạy Core Hub, Xưởng 1 (HyperFrames), Xưởng 2 (Remotion) & Dashboard | **Đã có sẵn** (`Node.js v24.21.0`) |
| **FFmpeg & FFprobe** | FFmpeg 6.0+ | Đo thời lượng audio micro-giây, mix âm thanh, render video | **Đã có sẵn** (`FFmpeg 9.0.2`) |
| **Blender** | **Blender 5.2 LTS** | Dựng hoạt hình 3D, camera tracking, render EEVEE Next (Xưởng 4) | **Đã có sẵn** (`Blender 5.2.2`) |

---

## 2. HƯỚNG DẪN CÀI ĐẶT NHANH BẰNG 1 DÒNG LỆNH (CHOCO / WINGET)

### Cách 1: Sử dụng Chocolatey (Khuyên dùng)
Mở cửa sổ **PowerShell với quyền Administrator** (chuột phải vào Start menu → chọn *Terminal (Admin)* hoặc *PowerShell (Admin)*), sau đó chạy lệnh:

```powershell
choco install nodejs-lts ffmpeg -y
```

> 💡 *Lưu ý:* Sau khi cài đặt xong, bạn hãy **tắt Terminal đi và mở lại** để hệ thống nạp các biến môi trường PATH mới.

### Cách 2: Sử dụng Winget
```powershell
winget install OpenJS.NodeJS.LTS
winget install Gyan.FFmpeg
```

---

## 3. KIỂM TRA MÔI TRƯỜNG (VERIFICATION)

Mở PowerShell mới tại thư mục dự án và kiểm tra:

```powershell
node -v           # Yêu cầu: >= v20.12.0
npm -v            # Yêu cầu: >= 10.x
python --version   # Kết quả: Python 3.12.10
ffprobe -version  # Hiển thị thông tin ffprobe (bắt buộc cho việc đo audio chính xác)
ffmpeg -version   # Hiển thị thông tin ffmpeg
```

---

## 4. THIẾT LẬP FILE CẤU HÌNH `.env` TỔNG HỢP

Tạo file `.env` tại thư mục gốc dự án từ `.env.example`:

```env
# ══════════════════════════════════════════════════════════════════════════════
# OMNIVIDEO STUDIO - CẤU HÌNH HỆ THỐNG TRUNG TÂM LOCAL
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. CẤU HÌNH GIỌNG ĐỌC AI (TTS) ─────────────────────────────────────────────
# Mặc định: edge-tts (Hoàn toàn miễn phí, 0đ, không cần API Key)
TTS_PROVIDER=edge-tts

# Cấu hình Microsoft Edge TTS tiếng Việt
# Giọng Nam: vi-VN-NamMinhNeural (Mặc định)
# Giọng Nữ: vi-VN-HoaiMyNeural
EDGE_TTS_VOICE=vi-VN-NamMinhNeural
EDGE_TTS_RATE=+5%
EDGE_TTS_PITCH=+0Hz
EDGE_TTS_VOLUME=+0%

# Cấu hình Vbee (Tùy chọn nếu bạn có tài khoản trả phí Vbee.vn)
VBEE_APP_ID=
VBEE_ACCESS_TOKEN=
VBEE_VOICE_CODE=n_hanoi_male_protrainer_education_vc
VBEE_SPEED_RATE=1.0

# Cấu hình ElevenLabs (Tùy chọn nếu có tài khoản trả phí ElevenLabs)
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL

# ── 2. CẤU HÌNH THƯƠNG HIỆU & MẠNG XÃ HỘI (BRANDING) ─────────────────────────
CHANNEL_NAME="KÊNH CÔNG NGHỆ & BÀI HỌC"
TIKTOK_HANDLE="@videostudio.local"
TIKTOK_DISPLAY_NAME="Video AI Studio"

# ── 3. THÔNG SỐ RENDER CHUẨN MỰC ──────────────────────────────────────────────
# Chuẩn khung hình: 30 FPS mặc định (nhẹ máy, render nhanh gấp 2 lần 60fps)
DEFAULT_FPS=30
VIDEO_THEME=dark-neon

# ── 4. CẤU HÌNH ĐƯỜNG DẪN HỆ THỐNG DUY NHẤT ──────────────────────────────────
CACHE_DIR=core/cache/tts
SHARED_ASSETS_DIR=shared-assets
OUTPUT_DIR=output
```

---

## 5. KHỞI TẠO MÔI TRƯỜNG CHO TỪNG XƯỞNG

### 5.1. Cài đặt Dependencies cho Core & Xưởng 1, 2 (Node.js Workspaces)
Tại thư mục gốc dự án:
```powershell
npm install
```

### 5.2. Khởi tạo Virtual Environment cho Xưởng 3 (Python)
Chạy script tự động thiết lập Python `.venv`:
```powershell
python workshops/workshop-whiteboard/prepare_env.py
```
Script này sẽ tự động tạo thư mục `.venv` độc lập và cài đặt các thư viện:
- `opencv-python`: Xử lý khung hình và luồng nét vẽ
- `numpy`: Tính toán ma trận pixel
- `av` (PyAV): Mã hóa video H.264 trực tiếp cực nhanh
- `Pillow`: Xử lý hình ảnh và text
- `edge-tts`: Gọi giọng đọc AI tiếng Việt

---

## 6. KHỞI CHẠY HỆ THỐNG MƯỢT MÀ KHÔNG BỊ WINDOWS CHẶN POLICY

Tạo file `studio.bat` tại thư mục gốc với nội dung:

```bat
@echo off
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0studio.ps1"
pause
```

Khi bạn double click vào `studio.bat`, Windows sẽ tự động bỏ qua chính sách chặn script (`ExecutionPolicy Bypass`) chỉ trong tiến trình đó mà không làm thay đổi cấu hình bảo mật chung của máy tính.

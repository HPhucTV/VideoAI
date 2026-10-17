# Workshop 4: 3D Animation Studio (Blender & EEVEE Next)

> **Phân xưởng sản xuất video hoạt hình 3D tự động hóa cục bộ (Local 100% · Chi phí 0đ)**  
> Chuyển đổi kịch bản AI (`job.json`) thành phim hoạt hình 3D điện ảnh (Cinematic Xianxia / Fantasy) sử dụng **Blender 5.2.2 LTS (EEVEE Next)** chạy ở chế độ Headless (không cần mở giao diện GUI) và hệ thống âm thanh tiêu chuẩn YouTube (-14 LUFS).

---

## 🎯 Mục Tiêu & Điểm Nổi Bật

- **Tự động hóa toàn trình (Zero-Click Pipeline):** Nhận file kịch bản chuẩn `job.json`, tự động sinh giọng đọc TTS tiếng Việt, tính toán độ dài từng câu thoại theo frame, dựng bối cảnh không gian 3D, tạo chuyển động camera mượt mà và xuất file video MP4 hoàn chỉnh.
- **EEVEE Next Engine:** Sử dụng engine đồ họa thời gian thực thế hệ mới của Blender 5.2, tối ưu tốc độ render nhanh vượt trội so với Cycles trong khi vẫn đạt chất lượng ánh sáng thể tích (volumetric lighting), phát sáng thần kiếm (glow/bloom) và đổ bóng điện ảnh.
- **Camera Choreography thông minh:** Tự động phân tích các visual cues từ kịch bản AI (`zoom_in_punch`, `pan_right`, `pan_left`, `zoom_out_slow`, `static`) và nhịp điệu phân cảnh (`hook_teaser`, `climax`, `action`, `hook_intro`) để điều phối chuyển động camera (Dolly In, Orbit, Dolly Out).
- **Âm thanh chuẩn YouTube (-14 LUFS):** Tự động phối trộn giọng dẫn/lời thoại với nhạc nền (BGM) qua bộ lọc Sidechain Ducking nâng cao của FFmpeg: tự động hạ âm lượng nhạc nền khi nhân vật cất tiếng nói và đưa tổng thể âm lượng về mức chuẩn quốc tế `-14 LUFS`.

---

## 📁 Cấu Trúc Thư Mục

```text
workshops/workshop-blender/
├── job_adapter.py             # Bộ chuyển đổi kịch bản job.json sang Blender Timeline & Camera Spec
├── scripts/
│   ├── blender_renderer.py    # Headless Blender Python script: dựng bối cảnh 3D, keyframe camera, render H.264
│   └── export_3d_video.py     # Pipeline điều phối toàn trình (TTS -> Đo thời lượng -> Render 3D -> BGM Ducking -> Mux)
├── tests/
│   ├── test_blender_adapter.py  # Unit tests kiểm thử bộ chuyển đổi kịch bản và chuẩn hóa lời thoại
│   └── test_export_pipeline.py  # Unit & Integration tests kiểm thử pipeline xuất video và sidechain ducking
└── README.md                  # Tài liệu hướng dẫn sử dụng chi tiết
```

### Chi tiết các module:
1. **`job_adapter.py`**:
   - Đọc dữ liệu beats, visual cues, dialogue từ `job.json`.
   - Làm sạch lời thoại tiếng Việt (`sanitize_dialogue_text`): tách chính xác tên nhân vật (ví dụ: `Sở Thiên Kiêu (lạnh lùng): ...` thành nhân vật và câu thoại thuần).
   - Ánh xạ camera cue hoặc vai trò phân cảnh sang chuyển động 3D (`dolly_in`, `orbit`, `dolly_out`, `static`).
   - Tính toán chính xác frame bắt đầu (`start_frame`) và kết thúc (`end_frame`) cho từng cảnh theo fps (mặc định 30 FPS).
2. **`scripts/blender_renderer.py`**:
   - Chạy trực tiếp trong môi trường Python nhúng của Blender (`bpy`).
   - Dựng bối cảnh Tiên hiệp kỳ ảo (Xianxia Scene) hoàn toàn procedural: đài ngọc (Jade Pedestal), nhân vật (Protagonist silhouette & robe), Thần kiếm cổ đại (Ancient Floating Sword) phát quang kiếm khí, cùng hệ thống ánh sáng 3 điểm điện ảnh (Key, Fill, Rim) và sương mờ thể tích.
   - Gán keyframe camera chuyển động mượt mà (Interpolation BEZIER) theo đúng chỉ dẫn của từng cảnh.
   - Thiết lập cấu hình render EEVEE Next, độ phân giải (720p, 1080p, 4K), codec H.264 / MP4.
3. **`scripts/export_3d_video.py`**:
   - **Bước 1**: Đọc kịch bản và gọi Edge TTS tổng hợp giọng nói tiếng Việt từng beat (tốc độ chuẩn 1.25x hoặc tùy chọn).
   - **Bước 2**: Dùng `ffprobe` đo thời lượng chính xác đến mili-giây của từng file audio.
   - **Bước 3**: Nối các đoạn âm thanh thành voice track tổng thể (`master_voice.wav`).
   - **Bước 4**: Tạo file chỉ dẫn dòng thời gian `blender_spec.json`.
   - **Bước 5**: Kích hoạt Blender headless (`blender.exe -b -P blender_renderer.py -- --spec ...`) để render video raw.
   - **Bước 6**: Ghép video raw và audio với bộ lọc BGM Sidechain Ducking (-14 LUFS, fade-out 2s).
   - **Bước 7**: Lưu file video thành phẩm vào thư mục `output/blender/<jobId>.mp4`.

---

## ⚙️ Yêu Cầu Môi Trường & Cài Đặt

### 1. Phần mềm cần thiết
- **Hệ điều hành**: Windows 10/11 64-bit.
- **Blender 5.2.2 LTS**:
  - Tải và cài đặt tại [blender.org](https://www.blender.org/download/).
  - Đường dẫn mặc định: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (script tự động nhận diện đường dẫn này hoặc qua biến môi trường `BLENDER_PATH` / `BLENDER_BIN`).
- **Python**: Phiên bản 3.10 trở lên (khuyên dùng Python 3.12).
- **FFmpeg & FFprobe**: Đã được cài đặt và cấu hình trong biến môi trường PATH (`choco install ffmpeg -y`).
- **Node.js**: Phiên bản 18+ (phục vụ tổng hợp giọng Edge TTS từ core engine).

### 2. Kiểm tra nhanh môi trường
Bạn có thể dùng công cụ quản lý studio trung tâm:
```powershell
.\studio.ps1
# Chọn [6] để kiểm tra toàn bộ môi trường: Node.js, Python, FFmpeg, FFprobe, Blender
```
Hoặc kiểm tra trực tiếp Blender trong PowerShell:
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -v
```

---

## 🎥 Đặc Tả Chuyển Động Camera (Camera Cues)

Hệ thống tự động biên dịch các chỉ thị thị giác (`visual_cue` hoặc `camera_movement`) trong `job.json` sang chuyển động camera 3D tương ứng:

| Chỉ thị trong `job.json` | Kiểu chuyển động 3D | Mô tả chuyển động camera trong Blender | Ứng dụng điện ảnh |
|---|---|---|---|
| `zoom_in_punch`, `zoom_in`, `dolly_in` | **`dolly_in`** | Camera tiến lại gần chủ thể (từ khoảng cách $Y=-9.8m$ vào $Y=-5.8m$, cao $2.2m$). | Tạo điểm nhấn kịch tính, cận cảnh nhân vật hoặc khoảnh khắc xuất hiện bảo vật. |
| `pan_right`, `pan_left`, `orbit` | **`orbit`** | Camera lượn vòng cung ngang quanh tâm cảnh (từ góc nghiêng $X=-3.5m$ sang $X=3.5m$). | Giới thiệu bối cảnh không gian rộng lớn, bao quát đài ngọc và thần kiếm. |
| `zoom_out_slow`, `zoom_out`, `dolly_out` | **`dolly_out`** | Camera lùi dần ra xa (từ $Y=-5.8m$ ra $Y=-9.8m$, nâng cao góc nhìn lên $3.4m$). | Kết thúc cảnh, mở rộng tầm nhìn để tạo cảm giác kỳ vĩ, trầm lắng. |
| `static` (mặc định) | **`static`** | Camera giữ vị trí tĩnh ổn định tại góc nhìn chuẩn điện ảnh. | Cảnh hội thoại, tập trung hoàn toàn vào diễn biến lời kể. |

> **Quy tắc dự phòng (Fallback):** Nếu phân cảnh không có visual cue rõ ràng, hệ thống sẽ tự động phân loại dựa trên vai trò kịch bản (`role`):
> - `hook_teaser`, `climax`, `action` $\rightarrow$ Tự động chuyển thành **`dolly_in`**.
> - `hook_intro`, `intro` $\rightarrow$ Tự động chuyển thành **`orbit`**.

---

## 🚀 Hướng Dẫn Sử Dụng (CLI)

### 1. Render Video 3D Từ Job Có Sẵn

Chạy pipeline xuất video từ thư mục gốc của repository:

```powershell
# Chạy với Job ID (tự động tìm trong output/jobs/<jobId>.json)
python workshops/workshop-blender/scripts/export_3d_video.py --job job-xianxia-3d-sample --resolution 720p

# Chỉ định đường dẫn file JSON kịch bản cụ thể
python workshops/workshop-blender/scripts/export_3d_video.py --job-file output/jobs/my-xianxia-job.json --resolution 1080p
```

### 2. Chế Độ Xem Trước Nhanh (Dry-Run)
Để dựng scene và kiểm tra cấu trúc timeline mà không mất thời gian render toàn bộ khung hình video:

```powershell
python workshops/workshop-blender/scripts/export_3d_video.py --job job-xianxia-3d-sample --dry-run
```

### 3. Tùy Chọn Tham Số CLI Chi Tiết

| Tham số | Kiểu | Mặc định | Ý nghĩa & Mô tả |
|---|---|---|---|
| `--job` | `string` | `None` | Tên hoặc ID của Job (tự động tìm file `.json` tương ứng trong thư mục `output/jobs/`). |
| `--job-file` | `string` | `None` | Đường dẫn trực tiếp đến file JSON kịch bản. |
| `--resolution` | `choice` | `720p` | Độ phân giải video đầu ra: `720p` (1280x720), `1080p` (1920x1080), hoặc `4k` (3840x2160). |
| `--fps` | `int` | `30` | Tốc độ khung hình trên giây. |
| `--bgm` | `string` | `None` | Đường dẫn file nhạc nền tùy chọn. Nếu không truyền, hệ thống tự động tìm nhạc nền cổ trang trong kho `workshops/workshop-whiteboard/assets/audio/bgm/xianxia-ambient.mp3`. |
| `--bgm-vol` | `float` | `0.25` | Tỉ lệ âm lượng gốc của nhạc nền trước khi bị giọng đọc nén (ducking). |
| `--blender-bin`| `string` | `None` | Đường dẫn cụ thể tới file `blender.exe` (nếu không cài đặt ở thư mục mặc định). |
| `--dry-run` | `flag` | `False` | Khởi tạo bối cảnh, tính toán timeline và xuất spec mà không render video thực sự. |
| `--keep-temp` | `flag` | `False` | Giữ lại thư mục tạm chứa các file audio con, voice ghép và spec để kiểm tra gỡ lỗi. |

### 4. Sử Dụng Qua Menu Điều Khiển `studio.ps1`
1. Mở PowerShell tại thư mục gốc của dự án.
2. Chạy:
   ```powershell
   .\studio.ps1
   ```
3. Nhập phím **`8`** để hiển thị hướng dẫn và lệnh chạy render Xưởng 4:
   ```text
   [8] 🎥 Xưởng 4: Hoạt hình 3D Blender (EEVEE Next Cinematic Animation)
   ```

---

## 🧪 Kiểm Thử Tự Động (Testing)

Xưởng 4 đi kèm bộ kiểm thử tự động toàn diện bao quát:
- Chuyển đổi timeline và ánh xạ camera cues.
- Tách tiền tố tên nhân vật, biểu cảm thoại và nhận diện giọng đọc.
- Sidechain ducking filter string theo tiêu chuẩn YouTube (-14 LUFS).
- Tìm kiếm executable Blender và điều phối pipeline hoàn chỉnh.

### Chạy kiểm thử Xưởng 4:
```powershell
# Chạy toàn bộ tests của workshop-blender
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-blender/tests/ -v
```

### Chạy toàn bộ test suites trong dự án:
```powershell
# 1. Kiểm thử TypeScript Core schemas
cmd.exe /c "npm.cmd --workspace=core test"

# 2. Kiểm thử Workshop 4 (Blender)
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-blender/tests/

# 3. Kiểm thử Workshop 3 (Whiteboard)
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-whiteboard/tests/

# 4. Kiểm thử Master Prompt Schema
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest tests/test_master_prompt_schema.py
```

---

## 🌟 Mẫu File Kịch Bản Chuẩn (`job.json`)

Dưới đây là cấu trúc mẫu một phân cảnh 3D mà Xưởng 4 xử lý:

```json
{
  "id": "job-xianxia-3d-sample",
  "topic": "Vạn Cổ Đệ Nhất Kiếm Thần",
  "style": "3d-blender",
  "resolution": "720p",
  "fps": 30,
  "beats": [
    {
      "id": "beat_01",
      "role": "hook_teaser",
      "dialogue": "Người dẫn chuyện: Một vạn năm trước, Tru Tiên Cổ Kiếm trấn áp yêu tộc tại Côn Lôn Đỉnh...",
      "visual_cue": "pan_right",
      "camera_movement": "orbit"
    },
    {
      "id": "beat_02",
      "role": "climax",
      "dialogue": "Sở Thiên Kiêu (lạnh lùng): Nhân đạo mịt mờ, kiếm đạo độc tôn. Hôm nay, ta lấy mạng ngươi!",
      "visual_cue": "zoom_in_punch",
      "camera_movement": "dolly_in"
    },
    {
      "id": "beat_03",
      "role": "outro",
      "dialogue": "Kiếm khí ngập trời, chấn động bát hoang lục hợp.",
      "visual_cue": "zoom_out_slow",
      "camera_movement": "dolly_out"
    }
  ]
}
```

Video thành phẩm sẽ được lưu tại:
```text
output/blender/job-xianxia-3d-sample.mp4
```

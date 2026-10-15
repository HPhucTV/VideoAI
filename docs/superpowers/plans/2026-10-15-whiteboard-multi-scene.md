# Whiteboard Multi-Scene & Hand Eraser Wipe Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Nâng cấp Xưởng 3 (`workshop-whiteboard`) từ chế độ đơn cảnh 1 hình vẽ sang hệ thống đa cảnh (Multi-Scene) vẽ nhiều bức tranh liên tiếp theo cốt truyện, kết hợp hiệu ứng bàn tay lau bảng (Eraser Wipe) chân thực ở 90 FPS.

**Architecture:** Bộ chuyển đổi `job_adapter.py` tự động gom nhịp thành các scenes con độc lập (tối đa 4–5 beats/cảnh). Bộ vẽ `stream_render.py` tích hợp hoạt cảnh bàn tay lau bảng zíc-zắc khôi phục màu giấy gốc ở cuối mỗi cảnh. Pipeline `export_video.py` render từng cảnh thành MP4 độc lập và ghép nối không mất chất lượng bằng `merge_scenes.py`.

**Tech Stack:** Python 3.12, OpenCV (`cv2`), NumPy, FFmpeg, Subprocess.

---

### File Structure Map
- **Modify:** [`workshops/workshop-whiteboard/job_adapter.py`](file:///c:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py) — Thêm thuật toán phân cụm `cluster_beats_into_scenes()`, sinh cây thư mục `scenes/scene-XX/`, tách audio & subtitle cục bộ.
- **Modify:** [`workshops/workshop-whiteboard/scripts/render_stream_whiteboard.py`](file:///c:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/render_stream_whiteboard.py) — Thêm phương thức `_erase_board()` và cờ `--with-eraser` tạo hiệu ứng bàn tay lau bảng zíc-zắc khôi phục màu nền.
- **Modify:** [`workshops/workshop-whiteboard/scripts/export_video.py`](file:///c:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/export_video.py) — Cập nhật quy trình duyệt qua danh sách các scenes, render từng cảnh ở 90 FPS và gọi `merge_scenes.py` ghép thành video tổng.
- **Create:** [`workshops/workshop-whiteboard/tests/test_multi_scene.py`](file:///c:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/tests/test_multi_scene.py) — Kiểm thử đơn vị cho thuật toán phân nhóm scenes và mốc thời gian SRT cục bộ.

---

### Task 1: Kiểm Thử & Thuật Toán Phân Cụm Đa Cảnh (`job_adapter.py`)

**Files:**
- Create: `workshops/workshop-whiteboard/tests/test_multi_scene.py`
- Modify: `workshops/workshop-whiteboard/job_adapter.py:80-195`

- [ ] **Step 1: Viết test kiểm tra phân cụm cảnh và mốc thời gian cục bộ**

Tạo file [`workshops/workshop-whiteboard/tests/test_multi_scene.py`](file:///c:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/tests/test_multi_scene.py):
```python
import pytest
import sys
from pathlib import Path

# Thêm thư mục whiteboard vào sys.path
root_wb = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_wb))

from job_adapter import cluster_beats_into_scenes

def test_cluster_beats_into_scenes():
    # Tạo 12 beats mẫu với 3 chương
    beats = []
    for i in range(1, 13):
        chapter = "CHƯƠNG I" if i <= 4 else ("CHƯƠNG II" if i <= 9 else "CHƯƠNG III")
        beats.append({
            "id": f"beat_{i:02d}",
            "rawText": f"Noi dung cau {i}",
            "visual": {
                "headline": f"Tieu de {i}",
                "badge": chapter
            }
        })

    scenes = cluster_beats_into_scenes(beats, max_beats_per_scene=4)
    # Kỳ vọng:
    # Chương I (4 beats) -> 1 scene (4 beats)
    # Chương II (5 beats) -> 2 scenes (4 beats + 1 beat vì max=4)
    # Chương III (3 beats) -> 1 scene (3 beats)
    # Tổng cộng: 4 scenes
    assert len(scenes) >= 3
    for s_idx, s in enumerate(scenes):
        assert len(s["beats"]) <= 4
        assert s["sceneId"] == f"scene-{s_idx+1:02d}"
```

- [ ] **Step 2: Chạy test để xác nhận kiểm thử thất bại (Failing Test)**

Chạy trong terminal PowerShell:
```powershell
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-whiteboard/tests/test_multi_scene.py
```
Kỳ vọng: Lỗi `ImportError: cannot import name 'cluster_beats_into_scenes' from 'job_adapter'`.

- [ ] **Step 3: Triển khai hàm `cluster_beats_into_scenes()` trong `job_adapter.py`**

Mở [`workshops/workshop-whiteboard/job_adapter.py`](file:///c:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py) và thêm logic:
```python
def cluster_beats_into_scenes(beats: list, max_beats_per_scene: int = 4) -> list[dict]:
    scenes = []
    current_scene_beats = []
    current_badge = None
    current_scene_id = None
    scene_counter = 1

    for beat in beats:
        vis = beat.get("visual", {})
        badge = vis.get("badge")
        scene_id = vis.get("sceneId")

        # Điều kiện tách cảnh: đổi badge, đổi sceneId rõ ràng, hoặc đầy dung lượng
        badge_changed = current_badge is not None and badge is not None and badge != current_badge
        scene_changed = current_scene_id is not None and scene_id is not None and scene_id != current_scene_id
        overflow = len(current_scene_beats) >= max_beats_per_scene

        if current_scene_beats and (badge_changed or scene_changed or overflow):
            scenes.append({
                "sceneId": f"scene-{scene_counter:02d}",
                "beats": current_scene_beats,
                "badge": current_badge or f"PHÂN CẢNH {scene_counter}"
            })
            scene_counter += 1
            current_scene_beats = []

        current_scene_beats.append(beat)
        if badge:
            current_badge = badge
        if scene_id:
            current_scene_id = scene_id

    if current_scene_beats:
        scenes.append({
            "sceneId": f"scene-{scene_counter:02d}",
            "beats": current_scene_beats,
            "badge": current_badge or f"PHÂN CẢNH {scene_counter}"
        })

    return scenes
```

- [ ] **Step 4: Chạy lại test để xác nhận passed**

Chạy:
```powershell
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-whiteboard/tests/test_multi_scene.py
```
Kỳ vọng: `1 passed in 0.05s`.

- [ ] **Step 5: Nâng cấp `convert_job_to_whiteboard()` để ghi cây thư mục `scenes/scene-XX/`**

Cập nhật [`workshops/workshop-whiteboard/job_adapter.py`](file:///c:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py) để:
1. Tạo thư mục con `scenes/scene-01/`, `scenes/scene-02/`...
2. Ghi `scene-XX.annotation.json` với mốc thời gian bắt đầu từ 0 cho từng cảnh.
3. Ghép audio riêng `scene-XX.mp3` và phụ đề riêng `scene-XX.srt` cho từng cảnh.
4. Tự động sinh `IMAGE_PROMPT.md` gợi ý vẽ tranh Notion/Doodle tương ứng với nội dung các nhịp trong cảnh đó.
5. Vẫn xuất song song `input.mp3` và `input.srt` toàn cục ở thư mục gốc để đảm bảo tương thích 100%.

- [ ] **Step 6: Commit Task 1**

```bash
git add workshops/workshop-whiteboard/job_adapter.py workshops/workshop-whiteboard/tests/test_multi_scene.py
git commit -m "feat(whiteboard): add scene clustering and multi-scene folder structure in job_adapter"
```

---

### Task 2: Triển Khai Hoạt Cảnh Bàn Tay Lau Bảng (`render_stream_whiteboard.py`)

**Files:**
- Modify: [`workshops/workshop-whiteboard/scripts/render_stream_whiteboard.py:350-480`](file:///c:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/render_stream_whiteboard.py)

- [ ] **Step 1: Thêm cờ `--with-eraser` và `--eraser-seconds` vào CLI argument parser**

Trong `_parse_args()` của [`render_stream_whiteboard.py`](file:///c:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/render_stream_whiteboard.py):
```python
p.add_argument("--with-eraser", action="store_true", default=False,
               help="Kích hoạt hoạt cảnh bàn tay lau bảng ở cuối phân cảnh")
p.add_argument("--eraser-seconds", type=float, default=1.3,
               help="Thời lượng lau bảng tính bằng giây (mặc định 1.3s)")
```

- [ ] **Step 2: Cài đặt phương thức `_erase_board()` trong `RegionStreamRenderer`**

Thêm phương thức lau bảng zíc-zắc khôi phục màu nền canvas:
```python
def _erase_board(self, writer, erase_frames: int):
    if erase_frames <= 0:
        return
    cfg = self.cfg
    disk_radius = int(round(self.out_h * 0.08))  # Bán kính khăn lau ~8% chiều cao canvas
    disk = sr._feathered_disk(disk_radius)

    # Quỹ đạo zíc-zắc từ trên xuống dưới
    sweep_lanes = 4  # Số lần lượn qua lại
    for fi in range(erase_frames):
        progress = fi / (erase_frames - 1) if erase_frames > 1 else 1.0
        # Di chuyển y từ 0 đến out_h
        cy = int(round(progress * self.out_h))
        # Di chuyển x theo hàm sine qua lại
        lane_phase = progress * sweep_lanes * math.pi
        cx = int(round((0.5 + 0.42 * math.sin(lane_phase)) * self.out_w))

        # Phục hồi màu nền canvas_bgr tại vệt lau
        y0, y1 = max(0, cy - disk_radius), min(self.out_h, cy + disk_radius + 1)
        x0, x1 = max(0, cx - disk_radius), min(self.out_w, cx + disk_radius + 1)
        if y1 > y0 and x1 > x0:
            by0 = y0 - (cy - disk_radius)
            by1 = disk.shape[0] - ((cy + disk_radius + 1) - y1)
            bx0 = x0 - (cx - disk_radius)
            bx1 = disk.shape[1] - ((cx + disk_radius + 1) - x1)
            m = disk[by0:by1, bx0:bx1, None]
            target = self.drawn[y0:y1, x0:x1]
            canvas_patch = self.canvas_bgr.astype(np.float32)
            target[:] = target * (1.0 - m) + canvas_patch * m

        # Đóng dấu bàn tay cầm khăn lau (hoặc đầu tẩy)
        writer.write(self._snapshot_with_tip(cx, cy))

    # Frame cuối: đảm bảo bảng trắng sạch 100%
    self.drawn[:] = self.canvas_bgr.astype(np.float32)
```

- [ ] **Step 3: Tích hợp `_erase_board()` vào `render_to()`**

Gọi `_erase_board()` sau khi hoàn thành các nhịp vẽ nếu `--with-eraser` được bật.

- [ ] **Step 4: Chạy thử nghiệm vẽ và lau bảng một đoạn ngắn**

Chạy thử trên mẫu 5 giây:
```powershell
workshops/workshop-whiteboard/.venv/Scripts/python.exe workshops/workshop-whiteboard/scripts/render_stream_whiteboard.py workshops/workshop-whiteboard/assets/whiteboard/ban-hop-dong-luc-0-gio/scene-01-storyboard.png output/whiteboard/tam-cam/scene-01.annotation.json output/whiteboard/test-eraser.mp4 --total-ms 5000 --with-eraser --fps 90
```
Xác nhận video `output/whiteboard/test-eraser.mp4` sinh ra có hoạt cảnh lau sạch bảng.

- [ ] **Step 5: Xóa file video thử nghiệm và commit Task 2**

```bash
git add workshops/workshop-whiteboard/scripts/render_stream_whiteboard.py
git commit -m "feat(whiteboard): add zig-zag hand eraser wipe animation in render_stream_whiteboard"
```

---

### Task 3: Nâng Cấp Pipeline Xuất Đa Cảnh (`export_video.py`)

**Files:**
- Modify: [`workshops/workshop-whiteboard/scripts/export_video.py`](file:///c:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/export_video.py)

- [ ] **Step 1: Nâng cấp `export_video.py` để hỗ trợ phát hiện và duyệt qua các scenes**

Đọc danh sách thư mục trong `output/whiteboard/{jobId}/scenes/`:
1. Nếu phát hiện các thư mục `scene-01`, `scene-02`...:
   - Duyệt qua từng scene:
     - Nạp ảnh `scene-XX.png` (nếu chưa có, tự động crop từ ảnh storyboard tổng thể hoặc copy ảnh storyboard mặc định).
     - Render video vẽ tay `video-silent.mp4` có bật `--with-eraser` (riêng cảnh cuối cùng thì không bật lau bảng).
     - Dùng FFmpeg ghép audio `scene-XX.mp3` thành `scene-XX.mp4`.
   - Thu thập danh sách tất cả các `scene-XX.mp4`.
   - Gọi `merge_scenes.py` ghép không mất chất lượng (`-c copy`) thành file tổng `output/whiteboard/{jobId}.mp4`.
2. Nếu chỉ có 1 scene (chế độ tương thích ngược cũ):
   - Giữ nguyên luồng xử lý đơn cảnh.

- [ ] **Step 2: Thêm cờ `--scene <id>` cho phép render lại riêng 1 cảnh cụ thể**

Hỗ trợ tham số `--scene scene-02` để người dùng/dashboard chỉ render lại đúng 1 cảnh khi cần chỉnh sửa hình vẽ, sau đó tự động ghép lại video tổng.

- [ ] **Step 3: Test chạy xuất toàn bộ kịch bản "Bản Hợp Đồng Lúc 0 Giờ" đa cảnh**

Chạy:
```powershell
workshops/workshop-whiteboard/.venv/Scripts/python.exe workshops/workshop-whiteboard/scripts/export_video.py job-ban-hop-dong-luc-0-gio --fps 90
```
Xác nhận:
- Tạo ra 5-6 scenes riêng biệt trong `output/whiteboard/job-ban-hop-dong-luc-0-gio/scenes/`.
- Từng cảnh có audio, phụ đề và tranh vẽ riêng.
- File video tổng `job-ban-hop-dong-luc-0-gio.mp4` được ghép nối hoàn chỉnh.

- [ ] **Step 4: Commit Task 3**

```bash
git add workshops/workshop-whiteboard/scripts/export_video.py
git commit -m "feat(whiteboard): integrate multi-scene rendering and selective re-rendering in export_video"
```

---

### Task 4: Kiểm Thử Tích Hợp Web Dashboard & Kiểm Tra Toàn Diện

**Files:**
- Test: Kiểm tra Web Dashboard tại `http://localhost:3000`
- Modify (nếu cần): [`dashboard/server.ts`](file:///c:/Users/tranh/Documents/Duy/VideoAI/dashboard/server.ts)

- [ ] **Step 1: Chạy test Vitest toàn bộ workspace**

```powershell
npm.cmd --workspace=core test
```
Kỳ vọng: 6/6 tests passed.

- [ ] **Step 2: Kiểm tra video hoàn chỉnh trên trình phát video cục bộ**

Kiểm tra thông số tệp `output/whiteboard/job-ban-hop-dong-luc-0-gio.mp4` bằng `ffprobe` để đảm bảo:
- Chuẩn 90 FPS
- Âm thanh và hình ảnh đồng bộ
- Các đoạn chuyển cảnh bằng tay lau bảng diễn ra mượt mà không bị khựng.

- [ ] **Step 3: Git Status và Push lên origin/master**

Kiểm tra `git status` đảm bảo không có file media (.mp4, .mp3) bị stage, commit và push lên `master`.

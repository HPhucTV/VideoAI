# Kế Hoạch Triển Khai: Khởi Tạo Scaffold Xưởng 4 (Workshop 4 - 3D Animation Studio với Blender)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng khung nền tảng (scaffold) cho Xưởng 4 (`workshops/workshop-blender`), cho phép hệ thống tự động nhận kịch bản `job.json`, điều khiển Blender 5.2 render hoạt hình 3D (nhân vật + bối cảnh + camera chuyển động) và xuất video MP4 10 giây hoàn chỉnh tích hợp giọng đọc TTS 1.25x và BGM ducking.

**Architecture:** 
1. `core/schema/job.ts`: Cập nhật `workshop: z.enum([...])` bổ sung giá trị `"blender"`.
2. `workshops/workshop-blender/job_adapter.py`: Đọc `job.json`, tính toán thời lượng audio của từng beat, phân bổ timeline khung hình (frames) và hành động chuyển động của camera (dolly, orbit, pan).
3. `workshops/workshop-blender/scripts/blender_renderer.py`: Script Python thực thi trong Blender headless (`blender.exe -b -P`), dựng phân cảnh 3D (đài tế, trụ đá, thần kiếm, nhân vật tu sĩ), nạp keyframe camera và render bằng EEVEE Next.
4. `workshops/workshop-blender/scripts/export_3d_video.py`: Pipeline CLI điều phối: sinh audio TTS -> tính timeline -> chạy Blender render video thô -> hòa trộn BGM ducking (-14 LUFS) -> xuất video MP4 cuối cùng.
5. `output/jobs/job-xianxia-3d-sample.json`: Kịch bản mẫu 10 giây kiểm thử toàn diện E2E.
6. `studio.ps1`: Tích hợp menu tùy chọn Xưởng 4 vào giao diện dòng lệnh của OmniVideo Studio.

**Tech Stack:** Python 3.12, Blender 5.2.2 LTS (`bpy`, EEVEE Next), Node.js v24 (TypeScript/Zod/Vitest), Edge-TTS, FFmpeg 9.0.2, Pytest.

---

### Task 1: Cập Nhật Schema Hỗ Trợ `workshop: "blender"`

**Files:**
- Modify: `core/schema/job.ts:56`
- Create Test: `core/schema/__tests__/workshop_blender_schema.test.ts`

- [ ] **Step 1: Viết failing test kiểm tra schema chấp nhận workshop 'blender'**

Tạo file `core/schema/__tests__/workshop_blender_schema.test.ts`:
```typescript
import { describe, it, expect } from "vitest";
import { VideoJobSchema } from "../job.ts";

describe("Job Schema Workshop Blender Support", () => {
  it("chấp nhận workshop là 'blender'", () => {
    const jobData = {
      jobId: "test-blender-job",
      title: "Test 3D Animation",
      workshop: "blender",
      archetype: "storytelling",
      beats: [
        {
          id: "b1",
          role: "hook",
          speaker: "Lâm Mặc",
          rawText: "Vạn kiếm quy tông!",
          cues: { camera: "zoom_in_punch" },
        },
      ],
    };

    const parsed = VideoJobSchema.parse(jobData);
    expect(parsed.workshop).toBe("blender");
  });
});
```

- [ ] **Step 2: Chạy test để xác nhận FAIL**

Lệnh:
```powershell
cmd.exe /c "npm.cmd --workspace=core test -- schema/__tests__/workshop_blender_schema.test.ts"
```
Kỳ vọng: Lỗi Zod validation vì `"blender"` chưa nằm trong enum.

- [ ] **Step 3: Cập nhật `core/schema/job.ts`**

Mở `core/schema/job.ts`, dòng 56 sửa thành:
```typescript
  workshop: z.enum(["news", "explainer", "whiteboard", "blender"]),
```

- [ ] **Step 4: Chạy lại test để xác nhận PASS**

Lệnh:
```powershell
cmd.exe /c "npm.cmd --workspace=core test -- schema/__tests__/workshop_blender_schema.test.ts"
```
Và chạy toàn bộ test của core:
```powershell
cmd.exe /c "npm.cmd --workspace=core test"
```
Kỳ vọng: PASS 100% (tất cả 11 tests pass).

- [ ] **Step 5: Git commit**

```bash
git add core/schema/job.ts core/schema/__tests__/workshop_blender_schema.test.ts
git commit -m "feat(schema): add blender workshop support to VideoJobSchema"
```

---

### Task 2: Cài Đặt `job_adapter.py` Cho Xưởng 4

**Files:**
- Create: `workshops/workshop-blender/job_adapter.py`
- Create Test: `workshops/workshop-blender/tests/test_blender_adapter.py`

- [ ] **Step 1: Viết unit test cho Blender Job Adapter**

Tạo file `workshops/workshop-blender/tests/test_blender_adapter.py`:
```python
import pytest
import sys
from pathlib import Path

wb_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(wb_dir))

from job_adapter import build_blender_timeline_spec, resolve_camera_action

def test_resolve_camera_action_mapping():
    # Khớp từ visual cues
    assert resolve_camera_action({"camera": "zoom_in_punch"}, "hook_teaser") == "dolly_in"
    assert resolve_camera_action({"camera": "pan_right"}, "dialogue") == "orbit"
    assert resolve_camera_action({"camera": "static"}, "dialogue") == "static"
    
    # Suy luận mặc định theo role nếu cues không chỉ định
    assert resolve_camera_action(None, "hook_teaser") == "dolly_in"
    assert resolve_camera_action(None, "hook_intro") == "orbit"
    assert resolve_camera_action(None, "climax") == "dolly_in"
    assert resolve_camera_action(None, "scene_01") == "static"

def test_build_blender_timeline_spec():
    job_dict = {
        "jobId": "job-3d-test",
        "canvas": {"width": 1280, "height": 720, "fps": 30},
        "beats": [
            {
                "id": "beat_01",
                "role": "hook_teaser",
                "speaker": "Lâm Mặc",
                "rawText": "Lâm Mặc: Ta không phục!",
                "cues": {"camera": "zoom_in_punch"}
            },
            {
                "id": "beat_02",
                "role": "hook_intro",
                "speaker": "Người Kể Chuyện",
                "rawText": "Chào mừng đạo hữu.",
                "cues": {"camera": "pan_right"}
            }
        ]
    }
    
    # Giả lập thời lượng audio đo được cho từng beat
    audio_durations = {
        "beat_01": 3.2,
        "beat_02": 2.8
    }
    
    spec = build_blender_timeline_spec(job_dict, audio_durations)
    
    assert spec["jobId"] == "job-3d-test"
    assert spec["fps"] == 30
    assert spec["resolution"] == [1280, 720]
    # Tổng thời lượng 6.0s * 30fps = 180 frames
    assert spec["total_frames"] == 180
    assert len(spec["shots"]) == 2
    
    # Shot 1
    s1 = spec["shots"][0]
    assert s1["id"] == "beat_01"
    assert s1["camera_action"] == "dolly_in"
    assert s1["start_frame"] == 1
    assert s1["end_frame"] == 96 # 3.2 * 30
    assert s1["clean_text"] == "Ta không phục!" # Đã lọc sạch tên vai
    
    # Shot 2
    s2 = spec["shots"][1]
    assert s2["id"] == "beat_02"
    assert s2["camera_action"] == "orbit"
    assert s2["start_frame"] == 97
    assert s2["end_frame"] == 180
```

- [ ] **Step 2: Chạy test để xác nhận FAIL**

Lệnh:
```powershell
python -m pytest workshops/workshop-blender/tests/test_blender_adapter.py
```
Kỳ vọng: Lỗi `ModuleNotFoundError` do chưa có file `job_adapter.py`.

- [ ] **Step 3: Tạo `workshops/workshop-blender/job_adapter.py`**

Triển khai logic:
- Nhập hoặc tái sử dụng bộ lọc `sanitize_dialogue_text` (tách sạch tên nhân vật/narrator khỏi lời thoại thoại).
- Cài đặt `resolve_camera_action(cues, role)`: ánh xạ `zoom_in_punch` -> `dolly_in`, `pan_right` / `pan_left` -> `orbit`, `zoom_out_slow` -> `dolly_out`, `static` -> `static`.
- Cài đặt `build_blender_timeline_spec(job_dict, audio_durations, fps=30)`:
  + Duyệt từng beat, tính số frames từ `audio_durations[beat_id] * fps`.
  + Gán `start_frame` và `end_frame` liên tục từ frame 1.
  + Ghi thông tin camera shot, speaker, clean_text vào cấu trúc `spec`.

- [ ] **Step 4: Chạy lại test để xác nhận PASS**

Lệnh:
```powershell
python -m pytest workshops/workshop-blender/tests/test_blender_adapter.py
```
Kỳ vọng: PASS 100%.

- [ ] **Step 5: Git commit**

```bash
git add workshops/workshop-blender/job_adapter.py workshops/workshop-blender/tests/test_blender_adapter.py
git commit -m "feat(blender): implement job_adapter with camera motion mapping and timeline calculation"
```

---

### Task 3: Viết Script Blender Headless Renderer (`blender_renderer.py`)

**Files:**
- Create: `workshops/workshop-blender/scripts/blender_renderer.py`

- [ ] **Step 1: Viết script `blender_renderer.py` thực thi trong môi trường Python của Blender**

Script hỗ trợ nhận tham số từ dòng lệnh:
`blender.exe -b -P workshops/workshop-blender/scripts/blender_renderer.py -- --spec <path_to_spec.json> --output <path_to_raw.mp4>`

Nội dung chính của `blender_renderer.py`:
1. **Scene Builder**:
   - Xóa bỏ toàn bộ objects cũ trong scene.
   - Thiết lập World màu tối huyền ảo (Mystic World).
   - Dựng bệ đài đá bát giác (Altar) + 4 cột trụ cổ kính gắn đá phát quang xanh lam (*Spirit Aura*).
   - Dựng thanh Thần Kiếm cắm ở trung tâm đài tế (*Divine Sword*).
   - Dựng nhân vật Tu Sĩ áo lam đứng trước thanh kiếm.
   - Thiết lập 3 nguồn sáng điện ảnh: Ánh trăng xanh lạnh (*MoonKey*), Ánh ấm (*WarmFill*), Nguồn sáng thanh kiếm (*AuraLight*).
2. **Camera Animator**:
   - Tạo Camera đặt tại bệ đài.
   - Đọc danh sách `shots` từ file `spec.json`.
   - Với mỗi shot từ `start_frame` đến `end_frame`:
     + Nếu `action == "dolly_in"`: Đặt keyframe vị trí camera dịch chuyển từ `(0, -10, 3.5)` lại gần `(0, -6.5, 2.5)` hướng vào nhân vật.
     + Nếu `action == "orbit"`: Đặt keyframe camera quay quanh tọa độ `(0, 0, 1.5)` một góc 35 độ.
     + Nếu `action == "dolly_out"`: Lùi dần camera ra xa để bao quát toàn cảnh.
     + Nếu `action == "static"`: Giữ cố định góc máy điện ảnh.
3. **Render Settings (EEVEE Next)**:
   - Đặt render engine là `BLENDER_EEVEE_NEXT` (hoặc `BLENDER_EEVEE`).
   - Đặt resolution (mặc định 1280x720 cho tốc độ render siêu tốc).
   - Frame rate: 30 fps.
   - Output format: `FFMPEG`, Video codec `H264`, Container `MPEG4`, Quality `HIGH`.
   - Đặt `bpy.context.scene.frame_start = 1`, `bpy.context.scene.frame_end = total_frames`.
   - Đặt đường dẫn xuất video: `output_video_path`.
   - Chạy `bpy.ops.render.render(animation=True)`.

- [ ] **Step 2: Viết test kiểm tra cú pháp và khả năng chạy độc lập của renderer**

Chạy thử script với cờ `--help` hoặc chế độ dry-run qua Blender:
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P workshops/workshop-blender/scripts/blender_renderer.py -- --help
```
Kỳ vọng: Script in ra hướng dẫn tham số dòng lệnh và thoát an toàn với mã lỗi 0.

- [ ] **Step 3: Git commit**

```bash
git add workshops/workshop-blender/scripts/blender_renderer.py
git commit -m "feat(blender): implement headless 3D scene and camera animation renderer"
```

---

### Task 4: Cài Đặt Pipeline Điều Phối Xuất Video (`export_3d_video.py`)

**Files:**
- Create: `workshops/workshop-blender/scripts/export_3d_video.py`

- [ ] **Step 1: Viết script `export_3d_video.py` tích hợp toàn trình**

Quy trình hoạt động:
1. Đọc file `job.json`.
2. Kiểm tra/Tạo thư mục làm việc tạm: `output/blender/_temp_<jobId>/`.
3. Sinh giọng đọc TTS cho từng beat (kế thừa `core/bin/tts.js`, rate `+25%`, lọc thoại bằng `sanitize_dialogue_text`).
4. Dùng `ffprobe` đo chính xác thời lượng từng file audio của beat.
5. Ghép nối các file audio thoại thành một track giọng đọc liền mạch `_voice_track.wav` bằng FFmpeg concat.
6. Gọi `job_adapter.build_blender_timeline_spec()` xuất file `_render_spec.json`.
7. Gọi `blender.exe -b -P workshops/workshop-blender/scripts/blender_renderer.py -- --spec _render_spec.json --output _raw_3d.mp4`.
8. Sau khi Blender hoàn tất xuất `_raw_3d.mp4`:
   - Lấy BGM (ví dụ `healing-piano.mp3` hoặc `xianxia-ambient.mp3`).
   - Sử dụng filter `build_final_bgm_ducking_filter` (đã có ở `workshops/workshop-whiteboard/scripts/audio_mixer.py` hoặc tạo module dùng chung) để hòa trộn giọng đọc + BGM ducking với fade-out 2s và chuẩn hóa âm lượng YouTube `-14 LUFS`.
   - Ghép track audio hoàn chỉnh vào video `_raw_3d.mp4` bằng FFmpeg (`-c:v copy -c:a aac -b:a 192k`).
9. Xuất file video hoàn thiện vào `output/blender/<jobId>.mp4`.
10. Dọn dẹp các tệp tạm.

- [ ] **Step 2: Viết unit test mock cho pipeline**

Tạo `workshops/workshop-blender/tests/test_export_pipeline.py` để verify các hàm helper (tìm `blender.exe`, nối audio beats, tính toán tham số ffmpeg).

- [ ] **Step 3: Chạy test pipeline**

```powershell
python -m pytest workshops/workshop-blender/tests/test_export_pipeline.py
```
Kỳ vọng: PASS 100%.

- [ ] **Step 4: Git commit**

```bash
git add workshops/workshop-blender/scripts/export_3d_video.py workshops/workshop-blender/tests/test_export_pipeline.py
git commit -m "feat(blender): implement end-to-end 3D video export pipeline with audio muxing"
```

---

### Task 5: Tạo Kịch Bản Mẫu & Kiểm Thử E2E Video Hoạt Hình 3D 10 Giây

**Files:**
- Create: `output/jobs/job-xianxia-3d-sample.json`

- [ ] **Step 1: Soạn file kịch bản mẫu 10s `job-xianxia-3d-sample.json`**

```json
{
  "jobId": "job-xianxia-3d-sample",
  "title": "Thần Kiếm Xuất Thế 3D",
  "workshop": "blender",
  "archetype": "storytelling",
  "targetPlatform": "youtube_long",
  "canvas": {
    "width": 1280,
    "height": 720,
    "fps": 30
  },
  "voice": {
    "provider": "edge-tts",
    "voiceId": "vi-VN-NamMinhNeural",
    "rate": "+25%",
    "pitch": "+0Hz",
    "volume": "+0%"
  },
  "metadata": {
    "channel": "OmniVideo 3D Studio",
    "characters": ["Lâm Mặc", "Người Kể Chuyện"],
    "characters_voice": {
      "lâm mặc": { "voice": "vi-VN-NamMinhNeural", "rate": "+20%", "pitch": "-3Hz" },
      "người kể chuyện": { "voice": "vi-VN-NamMinhNeural", "rate": "+25%", "pitch": "+0Hz" }
    }
  },
  "beats": [
    {
      "id": "beat_01",
      "role": "hook_teaser",
      "speaker": "Lâm Mặc",
      "rawText": "Vạn kiếm quy tông! Hôm nay ta sẽ phá vỡ phong ấn thần kiếm này!",
      "cues": { "camera": "zoom_in_punch" }
    },
    {
      "id": "beat_02",
      "role": "hook_intro",
      "speaker": "Người Kể Chuyện",
      "rawText": "Thần kiếm thức tỉnh, kiếm khí ngút trời rung chuyển cả tiên môn tam đại giới!",
      "cues": { "camera": "pan_right" }
    }
  ]
}
```

- [ ] **Step 2: Chạy pipeline xuất video thật**

Lệnh:
```powershell
python workshops/workshop-blender/scripts/export_3d_video.py --job job-xianxia-3d-sample
```
Kỳ vọng:
- Render video 3D chuyển động từ Blender bằng GPU EEVEE Next.
- Tạo video thành phẩm: `output/blender/job-xianxia-3d-sample.mp4`.

- [ ] **Step 3: Kiểm tra định dạng và chất lượng video bằng ffprobe & ebur128**

Lệnh:
```powershell
ffprobe -v error -show_entries format=duration,size -show_streams -of json output/blender/job-xianxia-3d-sample.mp4
ffmpeg -i output/blender/job-xianxia-3d-sample.mp4 -af "ebur128" -f null -
```
Kỳ vọng:
- Video có độ dài xấp xỉ 8-10 giây.
- Video stream H264 1280x720, Audio stream AAC 192kbps.
- Âm lượng đạt chuẩn YouTube ~ -14 LUFS.

- [ ] **Step 4: Git commit**

```bash
git add output/jobs/job-xianxia-3d-sample.json
git commit -m "test(blender): add 10s sample 3D xianxia job and verify end-to-end rendering"
```

---

### Task 6: Tích Hợp Menu `studio.ps1` & Viết Tài Liệu Hướng Dẫn Xưởng 4

**Files:**
- Modify: `studio.ps1`
- Create: `workshops/workshop-blender/README.md`

- [ ] **Step 1: Cập nhật `studio.ps1`**

Thêm mục menu số 8:
```powershell
Write-Host " [8] 🎥 Xưởng 4: Hoạt hình 3D Blender (EEVEE Next Cinematic Animation)" -ForegroundColor White
```
Và xử lý sự kiện:
```powershell
"8" {
    Write-Host ""
    Write-Host "👉 XƯỞNG 4: Chạy lệnh render hoạt hình 3D Blender:" -ForegroundColor Cyan
    Write-Host "python workshops/workshop-blender/scripts/export_3d_video.py --job [jobId]" -ForegroundColor Yellow
    Read-Host "Bấm Enter để tiếp tục..."
}
```

- [ ] **Step 2: Soạn thảo `workshops/workshop-blender/README.md`**

Mô tả chi tiết:
- Giới thiệu Xưởng 4 (3D Animation Studio).
- Cách chuẩn bị môi trường: Yêu cầu Blender 5.0+ (khuyên dùng 5.2.2 LTS), Card đồ họa hỗ trợ EEVEE Next.
- Hướng dẫn cấu trúc kịch bản `job.json` với các hiệu ứng camera (`zoom_in_punch`, `pan_right`, `orbit`, `static`).
- Cách chạy lệnh xuất video.

- [ ] **Step 3: Chạy toàn bộ test suites của repo để đảm bảo 100% pass**

```powershell
npm.cmd --workspace=core test
python -m pytest workshops/workshop-blender/tests/
python -m pytest workshops/workshop-whiteboard/tests/
```
Kỳ vọng: Toàn bộ các test của hệ thống đều PASS 100%.

- [ ] **Step 4: Git commit**

```bash
git add studio.ps1 workshops/workshop-blender/README.md
git commit -m "docs(blender): integrate workshop-blender into studio.ps1 and add documentation"
```

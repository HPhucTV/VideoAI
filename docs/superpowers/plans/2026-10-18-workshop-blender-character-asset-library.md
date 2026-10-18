# Kế Hoạch Triển Khai: Hướng 2 - Nâng Cấp Thư Viện Nhân Vật 3D & Bối Cảnh Tiên Hiệp Đẹp Mắt (Workshop 4)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Thay thế hoàn toàn các hình nhân primitive (hình trụ thô sơ) của bản demo bằng hệ thống nhân vật 3D Anime/Tiên Hiệp chất lượng cao (mesh điêu khắc chi tiết, mắt/mũi/miệng sắc nét, tóc nhiều lớp, trang phục hoàn chỉnh, khung xương 59 bones có diễn hoạt pose và biểu cảm chớp mắt) cùng bối cảnh đền đài tiên hiệp nâng cấp vật liệu PBR và ánh sáng điện ảnh EEVEE Next.

**Architecture:** 
1. `workshops/workshop-blender/assets/characters/`: Thư mục chứa các mô hình Humanoid rigged chuẩn (`.glb`) kèm metadata `config.json` theo từng vai trò (`nam-chinh`, `nu-chinh`, `truong-lao`).
2. `scripts/download-character-assets.ps1`: Script tự động tải các mô hình 3D anime mở (CC0/Royalty-free) về kho asset cục bộ.
3. `workshops/workshop-blender/pose_engine.py`: Module điều khiển khung xương Humanoid (59 bones) với thư viện tư thế diễn hoạt (`idle_stand`, `hands_clasped_back`, `cast_spell`, `swordsman_ready`, `talking`) và tự động chớp mắt/nhấp môi qua facial shape keys.
4. `workshops/workshop-blender/job_adapter.py`: Mở rộng hỗ trợ trường `metadata.character_models` và tự động ánh xạ pose diễn hoạt khớp với từng beat thoại.
5. `workshops/workshop-blender/scripts/blender_renderer.py`: Nạp mô hình 3D thực tế, gắn xương, keyframe chuyển động nhân vật kết hợp camera chuyển động và bối cảnh nâng cấp vật liệu đá rêu PBR + ánh sáng volumetric.
6. `workshops/workshop-blender/scripts/export_3d_video.py`: Pipeline điều phối render video 3D anime đẹp mắt hoàn chỉnh với TTS 1.25x và BGM ducking.

**Tech Stack:** Python 3.12, Blender 5.2.2 LTS (`bpy`, `mathutils`, EEVEE Next), VRM / glTF 2.0 Humanoid Armature, FFmpeg 9.0.2, Pytest.

---

### Task 1: Xây Dựng Kho Asset Nhân Vật 3D & Script Tải Model Mẫu

**Files:**
- Create: `scripts/download-character-assets.ps1`
- Create: `workshops/workshop-blender/assets/characters/nam-chinh/config.json`
- Create: `workshops/workshop-blender/assets/characters/nu-chinh/config.json`
- Create: `workshops/workshop-blender/assets/characters/LICENSES.md`
- Create Test: `workshops/workshop-blender/tests/test_character_assets.py`

- [x] **Step 1: Viết test kiểm tra tính toàn vẹn của Character Asset Library**
- [x] **Step 2: Chạy test để xác nhận FAIL**
- [x] **Step 3: Viết `scripts/download-character-assets.ps1` và các file `config.json`**
- [x] **Step 4: Chạy lại test xác nhận PASS 100%**
- [x] **Step 5: Git commit**

```bash
git add scripts/download-character-assets.ps1 workshops/workshop-blender/assets/characters/ workshops/workshop-blender/tests/test_character_assets.py
git commit -m "feat(blender): scaffold 3D character asset library and model downloader"
```

---

### Task 2: Cài Đặt Pose Engine Cho Khung Xương Humanoid (`pose_engine.py`)

**Files:**
- Create: `workshops/workshop-blender/pose_engine.py`
- Create Test: `workshops/workshop-blender/tests/test_pose_engine.py`

- [x] **Step 1: Viết failing test cho `pose_engine.py`**

Tạo `workshops/workshop-blender/tests/test_pose_engine.py`:
```python
import pytest
import sys
from pathlib import Path

wb_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(wb_dir))

from pose_engine import get_pose_bone_rotations, map_beat_to_pose

def test_map_beat_to_pose():
    # Hook teaser -> tư thế xuất chiêu hoặc thủ kiếm
    assert map_beat_to_pose("hook_teaser", "Lâm Mặc") in ["cast_spell", "swordsman_ready"]
    # Beat nói chuyện -> tư thế đàm đạo
    assert map_beat_to_pose("dialogue", "Lâm Mặc") == "talking"
    # Người dẫn truyện / cao nhân -> tư thế chắp tay uy nghiêm
    assert map_beat_to_pose("hook_intro", "Người Kể Chuyện") == "hands_clasped_back"

def test_get_pose_bone_rotations():
    rotations = get_pose_bone_rotations("hands_clasped_back")
    assert "J_Bip_L_UpperArm" in rotations or "upperarm_l" in rotations
    # Cánh tay phải hạ xuống khỏi T-pose
    arm_rot = rotations.get("J_Bip_L_UpperArm")
    assert arm_rot is not None
```

- [x] **Step 2: Chạy test để xác nhận FAIL**

```powershell
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-blender/tests/test_pose_engine.py
```

- [x] **Step 3: Cài đặt `workshops/workshop-blender/pose_engine.py`**

Triển khai:
- `map_beat_to_pose(role: str, speaker: str) -> str`: Ánh xạ vai trò và tên nhân vật sang các tư thế: `cast_spell`, `swordsman_ready`, `hands_clasped_back`, `talking`, `idle_stand`.
- `get_pose_bone_rotations(pose_name: str) -> dict[str, tuple[float, float, float]]`: Định nghĩa góc xoay Euler (theo độ/rad) cho các xương cốt lõi (`UpperArm`, `LowerArm`, `Hand`, `Spine`, `Head`) để đưa nhân vật từ T-pose về tư thế sinh động, tự nhiên.
- `apply_pose_to_armature(armature_obj, pose_name: str, keyframe: int | None = None)`: Hàm gọi trong Blender để nạp rotation và gán keyframe.
- `apply_blink_keyframes(face_obj, start_frame: int, end_frame: int, fps: int = 30)`: Tự động lặp lại chu kỳ chớp mắt (cứ 3-4 giây chớp 1 lần khoảng 4-6 frames) bằng shape key `target_0` hoặc `blink`.

- [x] **Step 4: Chạy lại test xác nhận PASS 100%**

```powershell
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-blender/tests/test_pose_engine.py
```

- [x] **Step 5: Git commit**

```bash
git add workshops/workshop-blender/pose_engine.py workshops/workshop-blender/tests/test_pose_engine.py
git commit -m "feat(blender): implement pose_engine for humanoid armature posing and facial blinking"
```

---

### Task 3: Nâng Cấp `job_adapter.py` Hỗ Trợ Character Models & Poses

**Files:**
- Modify: `workshops/workshop-blender/job_adapter.py`
- Modify Test: `workshops/workshop-blender/tests/test_blender_adapter.py`

- [ ] **Step 1: Cập nhật unit test yêu cầu spec chứa thông tin model và pose**

Thêm assertions trong `test_blender_adapter.py` xác nhận mỗi shot trong `spec["shots"]` có trường `character_model` (ví dụ `"nam-chinh"`) và `character_pose` (ví dụ `"cast_spell"` hoặc `"hands_clasped_back"`).

- [ ] **Step 2: Chạy test để xác nhận FAIL**

```powershell
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-blender/tests/test_blender_adapter.py
```

- [ ] **Step 3: Cập nhật `workshops/workshop-blender/job_adapter.py`**

- Đọc `character_models = metadata.get("character_models", {})`.
- Ánh xạ speaker của beat sang character model tương ứng (mặc định fallback về `"nam-chinh"` nếu là nam hoặc không tìm thấy).
- Gọi `map_beat_to_pose(beat.get("role", ""), speaker)` để xác định `character_pose` cho từng shot.

- [ ] **Step 4: Chạy lại test xác nhận PASS 100%**

```powershell
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-blender/tests/test_blender_adapter.py
```

- [ ] **Step 5: Git commit**

```bash
git add workshops/workshop-blender/job_adapter.py workshops/workshop-blender/tests/test_blender_adapter.py
git commit -m "feat(blender): add character model resolution and shot pose mapping to job_adapter"
```

---

### Task 4: Nâng Cấp `blender_renderer.py` Nạp Model Nhân Vật 3D Thực & Diễn Hoạt Pose

**Files:**
- Modify: `workshops/workshop-blender/scripts/blender_renderer.py`

- [ ] **Step 1: Cập nhật `blender_renderer.py` tích hợp import GLB nhân vật thực**

- Thay thế hàm dựng hình trụ thô bằng hàm `load_and_setup_character(model_id: str, location: tuple)`:
  + Tìm file `model.glb` trong `assets/characters/<model_id>/model.glb`.
  + Dùng `bpy.ops.import_scene.gltf(filepath=...)` để nạp nhân vật 3D hoàn chỉnh.
  + Đặt nhân vật tại vị trí trung tâm đài tế, quay mặt hướng về phía trước.
- Diễn hoạt Pose theo từng Shot:
  + Nhập hàm từ `pose_engine.py`.
  + Tại `start_frame` của từng shot, đặt keyframe góc xoay xương cánh tay/thân người khớp với `shot["character_pose"]`.
  + Gán keyframe chớp mắt tự nhiên trên mesh `Face` để nhân vật sống động như thật.

- [ ] **Step 2: Kiểm tra chạy thử nghiệm headless renderer**

Chạy script với cờ `--dry-run` để đảm bảo code nạp model và gắn keyframe chạy trơn tru:
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P workshops/workshop-blender/scripts/blender_renderer.py -- --spec test_spec.json --output test_out.mp4 --dry-run
```

- [ ] **Step 3: Git commit**

```bash
git add workshops/workshop-blender/scripts/blender_renderer.py
git commit -m "feat(blender): render high-fidelity rigged anime character with dynamic poses and blink animations"
```

---

### Task 5: Nâng Cấp Bối Cảnh Tiên Hiệp & Ánh Sáng Thần Điện

**Files:**
- Modify: `workshops/workshop-blender/scripts/blender_renderer.py`

- [ ] **Step 1: Tinh chỉnh bối cảnh và ánh sáng điện ảnh**

- Nâng cấp bệ đài đá bát giác với hoa văn và viền ngọc.
- Thần Kiếm trung tâm phát sáng kiếm khí lam ngọc tỏa sương mù thể tích (*Volumetric Light Shafts / Fog*).
- Đèn chiếu chân dung chuyên dụng (*Portrait Key Light*) làm tôn lên vẻ đẹp của khuôn mặt anime nhân vật.

- [ ] **Step 2: Chạy render thử 1 frame và kiểm tra độ thẩm mỹ**

- [ ] **Step 3: Git commit**

```bash
git add workshops/workshop-blender/scripts/blender_renderer.py
git commit -m "feat(blender): enhance mystic temple environment and cinematic portrait lighting"
```

---

### Task 6: Xuất Video E2E Mới & Nghiệm Thu Chất Lượng Toàn Diện

**Files:**
- Update: `output/jobs/job-xianxia-3d-sample.json`
- Verify: `output/blender/job-xianxia-3d-sample.mp4`

- [ ] **Step 1: Chạy xuất video thực tế**

```powershell
workshops/workshop-whiteboard/.venv/Scripts/python.exe workshops/workshop-blender/scripts/export_3d_video.py --job job-xianxia-3d-sample --resolution 720p
```

- [ ] **Step 2: Trích xuất ảnh render nghiệm thu**

Trích xuất 2 frame từ video MP4 mới để kiểm chứng khuôn mặt nhân vật đẹp mắt, trang phục chi tiết, tư thế sống động.

- [ ] **Step 3: Chạy toàn bộ test suites của repo để đảm bảo 100% xanh**

```powershell
cmd.exe /c "npm.cmd --workspace=core test"
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-blender/tests/
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-whiteboard/tests/
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest tests/test_master_prompt_schema.py
```

- [ ] **Step 4: Git commit & Handoff**

```bash
git add output/jobs/job-xianxia-3d-sample.json
git commit -m "test(blender): verify high-fidelity anime character in 3D video pipeline"
```

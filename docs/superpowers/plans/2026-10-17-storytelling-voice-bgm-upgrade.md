# Kế Hoạch Triển Khai: Nâng Cấp Kịch Bản Sảng Văn, Voice 1.25x Và Tự Động Hòa Trộn BGM (Audio Drama)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Giải quyết triệt để 3 điểm yếu của video truyện audio (cốt truyện chán, thiếu hook 15s mở đầu, giọng đọc monotone bị xưng tên vai) bằng cách cung cấp Master Prompt chuẩn hóa, bộ lọc Dialogue Sanitizer, rate đọc 1.25x và hệ thống trộn BGM Audio Ducking sau khi ghép nối.

**Architecture:** 
1. `prompts/MASTER_STORY_PROMPT.md` chỉ thị ChatGPT/Claude xuất kịch bản chuẩn `VideoJobSchema`.
2. `core/schema/job.ts` và `job_adapter.py` đồng bộ trường `speaker` ở root của beat.
3. `core/tts/index.ts` sửa `computeAudioHash` gồm `pitch` và `volume`.
4. `job_adapter.py` tích hợp `sanitize_dialogue_text` loại bỏ tiền tố vai trước khi gửi sang TTS và cập nhật role presets với rate `+25%`.
5. `export_video.py` và `audio_mixer.py` chuyển việc trộn BGM về hàm `apply_final_bgm_and_mastering()` sau `merge_scenes()` với bộ lọc ducking, `normalize=0`, fade-out 2s và YouTube `loudnorm` -14 LUFS.
6. Script `scripts/download-bgm.ps1` tải BGM royalty-free kèm `LICENSES.md`.

**Tech Stack:** Python 3.12, Node.js v24 (TypeScript/Zod/Vitest), Edge-TTS, FFmpeg 9.0.2 (`sidechaincompress`, `amix`, `afade`, `loudnorm`), Pytest.

---

### Task 1: Sửa Cache Key TTS (Pitch & Volume) Trong `core/tts/index.ts`

**Files:**
- Modify: `core/tts/index.ts:45-48`
- Create Test: `core/tts/__tests__/cache.test.ts`

- [ ] **Step 1: Viết test kiểm tra `computeAudioHash` phải phân biệt `pitch` và `volume`**

Tạo file `core/tts/__tests__/cache.test.ts`:
```typescript
import { describe, it, expect } from "vitest";
import { computeAudioHash, TTSRequest } from "../index.ts";

describe("TTS Cache Hash Key", () => {
  const baseReq: TTSRequest = {
    text: "Hôm nay trời đẹp",
    provider: "edge-tts",
    voice: "vi-VN-NamMinhNeural",
    rate: "+25%",
    pitch: "+0Hz",
    volume: "+0%",
  };

  it("thay đổi hash khi thay đổi pitch", () => {
    const hashNormal = computeAudioHash(baseReq, "Hôm nay trời đẹp");
    const reqDeep: TTSRequest = { ...baseReq, pitch: "-6Hz" };
    const hashDeep = computeAudioHash(reqDeep, "Hôm nay trời đẹp");

    expect(hashDeep).not.toBe(hashNormal);
  });

  it("thay đổi hash khi thay đổi volume", () => {
    const hashNormal = computeAudioHash(baseReq, "Hôm nay trời đẹp");
    const reqQuiet: TTSRequest = { ...baseReq, volume: "-20%" };
    const hashQuiet = computeAudioHash(reqQuiet, "Hôm nay trời đẹp");

    expect(hashQuiet).not.toBe(hashNormal);
  });
});
```

- [ ] **Step 2: Chạy test để xác nhận test THẤT BẠI (Fail do chưa băm pitch/volume)**

Run:
```bash
cmd.exe /c "npm --workspace=core test -- core/tts/__tests__/cache.test.ts"
```
Expected: FAIL (assertion `not.toBe` fails vì hash hiện tại giống nhau khi chỉ đổi pitch/volume).

- [ ] **Step 3: Sửa `computeAudioHash` trong `core/tts/index.ts`**

Sửa dòng 45-48 của `core/tts/index.ts`:
```typescript
export function computeAudioHash(req: TTSRequest, normalizedText: string): string {
  const provider = req.provider || "edge-tts";
  const voice = req.voice || "vi-VN-NamMinhNeural";
  const rate = req.rate || "+0%";
  const pitch = req.pitch || "+0Hz";
  const volume = req.volume || "+0%";
  const payload = `${provider}:${voice}:${rate}:${pitch}:${volume}:${normalizedText}`;
  return createHash("sha256").update(payload).digest("hex").slice(0, 16);
}
```

- [ ] **Step 4: Chạy lại test để xác nhận test THÀNH CÔNG (Pass)**

Run:
```bash
cmd.exe /c "npm --workspace=core test -- core/tts/__tests__/cache.test.ts"
```
Expected: PASS (2 tests passed).

- [ ] **Step 5: Commit**

```bash
git add core/tts/index.ts core/tts/__tests__/cache.test.ts
git commit -m "fix(tts): include pitch and volume in cache hash key to prevent collision"
```

---

### Task 2: Thống Nhất Trường `speaker` Trong Schema & Adapter

**Files:**
- Modify: `core/schema/job.ts:38-72`
- Modify: `workshops/workshop-whiteboard/job_adapter.py:454-460`
- Create Test: `core/schema/__tests__/speaker_schema.test.ts`

- [ ] **Step 1: Viết test cho `VideoBeatSchema` chấp nhận `beat.speaker` và `metadata.characters`**

Tạo file `core/schema/__tests__/speaker_schema.test.ts`:
```typescript
import { describe, it, expect } from "vitest";
import { VideoJobSchema, VideoBeatSchema } from "../job.ts";

describe("Job Schema Speaker Support", () => {
  it("chấp nhận trường speaker ở cấp root của beat", () => {
    const beatData = {
      id: "beat_01",
      role: "dialogue",
      speaker: "Lâm Mặc",
      rawText: "Các ngươi cứ đợi đấy!",
    };
    const parsed = VideoBeatSchema.parse(beatData);
    expect((parsed as any).speaker).toBe("Lâm Mặc");
  });

  it("giữ nguyên characters và characters_voice trong metadata", () => {
    const jobData = {
      jobId: "test-job",
      title: "Test",
      workshop: "whiteboard",
      beats: [{ id: "b1", role: "hook", rawText: "Xin chào" }],
      metadata: {
        characters: ["Lâm Mặc", "Triệu Vô Cực"],
        characters_voice: {
          "lâm mặc": { voice: "vi-VN-NamMinhNeural", rate: "+20%", pitch: "-3Hz" },
        },
      },
    };
    const parsed = VideoJobSchema.parse(jobData);
    expect((parsed.metadata as any).characters).toEqual(["Lâm Mặc", "Triệu Vô Cực"]);
    expect((parsed.metadata as any).characters_voice["lâm mặc"].pitch).toBe("-3Hz");
  });
});
```

- [ ] **Step 2: Chạy test để xác nhận test THẤT BẠI**

Run:
```bash
cmd.exe /c "npm --workspace=core test -- core/schema/__tests__/speaker_schema.test.ts"
```
Expected: FAIL (Zod tước bỏ hoặc báo lỗi `speaker`, `characters`).

- [ ] **Step 3: Cập nhật `core/schema/job.ts` và `job_adapter.py`**

Trong `core/schema/job.ts`:
1. Thêm `speaker: z.string().optional()` vào `VideoBeatSchema`:
```typescript
export const VideoBeatSchema = z.object({
  id: z.string(),
  role: z.string(),
  rawText: z.string(),
  speaker: z.string().optional(),
  normalizedVoiceText: z.string().optional(),
  voice: BeatVoiceSchema.optional(),
  cues: VisualCueSchema.optional(),
  voiceFile: z.string().optional(),
  durationSec: z.number().nonnegative().optional(),
  durationFrames: z.number().int().nonnegative().optional(),
  sfx: z.string().optional(),
  visual: z.record(z.any()).default({}),
});
```
2. Cho phép `metadata` trong `VideoJobSchema` giữ lại các trường mở rộng (`characters`, `characters_voice`):
```typescript
  metadata: z.object({
    channel: z.string().default("Video Studio"),
    author: z.string().optional(),
    tags: z.array(z.string()).default([]),
    sourceUrl: z.string().optional(),
    characters: z.array(z.string()).optional(),
    characters_voice: z.record(z.any()).optional(),
  }).passthrough().default({}),
```

Trong `workshops/workshop-whiteboard/job_adapter.py` dòng 454:
Hỗ trợ fallback an toàn:
```python
explicit_speaker = beat.get("speaker") or (beat.get("voice") or {}).get("speaker")
```

- [ ] **Step 4: Chạy test để xác nhận test THÀNH CÔNG**

Run:
```bash
cmd.exe /c "npm --workspace=core test -- core/schema/__tests__/speaker_schema.test.ts"
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/schema/job.ts core/schema/__tests__/speaker_schema.test.ts workshops/workshop-whiteboard/job_adapter.py
git commit -m "feat(schema): standardize beat.speaker and allow characters in metadata"
```

---

### Task 3: Viết Test Tái Hiện Lỗi Đọc Tên Vai & Cài Đặt Dialogue Sanitizer

**Files:**
- Create Test: `workshops/workshop-whiteboard/tests/test_speaker_parser.py`
- Modify: `workshops/workshop-whiteboard/job_adapter.py`

- [ ] **Step 1: Viết test tái hiện lỗi đọc xưng vai và test quy tắc Sanitizer mới**

Tạo file `workshops/workshop-whiteboard/tests/test_speaker_parser.py`:
```python
import pytest
import sys
from pathlib import Path

root_wb = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_wb))

from job_adapter import sanitize_dialogue_text, parse_dialogue_segments

def test_sanitize_dialogue_narrator_prefix():
    text = "Người Kể Chuyện: Tiên sơn vạn trượng, ngút ngàn mây trắng."
    known = ["Người Kể Chuyện", "Lâm Mặc"]
    spk, clean = sanitize_dialogue_text(text, known_speakers=known)
    assert spk == "Người Kể Chuyện"
    assert clean == "Tiên sơn vạn trượng, ngút ngàn mây trắng."
    assert "Người Kể Chuyện:" not in clean

def test_sanitize_dialogue_character_with_expression():
    text = "Sở Thiên Kiêu (lạnh lùng): Các ngươi quỳ xuống cho ta!"
    known = ["Sở Thiên Kiêu"]
    spk, clean = sanitize_dialogue_text(text, known_speakers=known)
    assert spk == "Sở Thiên Kiêu"
    assert clean == "Các ngươi quỳ xuống cho ta!"
    assert ":" not in clean

def test_sanitize_dialogue_narrative_colon_preserved():
    text = "Hắn gầm lên: Ngươi dám sao?!"
    known = ["Lâm Mặc", "Người Kể Chuyện"]
    spk, clean = sanitize_dialogue_text(text, known_speakers=known)
    # Không phải tên nhân vật vì có động từ tường thuật
    assert spk is None
    assert clean == "Hắn gầm lên: Ngươi dám sao?!"

def test_sanitize_dialogue_time_colon_preserved():
    text = "Lúc 10:30 sáng, lò đan bốc hỏa dữ dội."
    known = ["Lâm Mặc"]
    spk, clean = sanitize_dialogue_text(text, known_speakers=known)
    assert spk is None
    assert clean == "Lúc 10:30 sáng, lò đan bốc hỏa dữ dội."

def test_parse_dialogue_segments_no_colon_in_narrator():
    text = "Lâm Mặc: Ta không phục!"
    known = ["Lâm Mặc"]
    segs = parse_dialogue_segments(text, known_speakers=known)
    assert len(segs) == 1
    assert segs[0]["speaker"] == "Lâm Mặc"
    assert segs[0]["text"] == "Ta không phục!"
    assert ":" not in segs[0]["text"]
```

- [ ] **Step 2: Chạy test để xác nhận test THẤT BẠI (vì chưa có `sanitize_dialogue_text`)**

Run:
```bash
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-whiteboard/tests/test_speaker_parser.py
```
Expected: FAIL (ImportError hoặc assertion error do code cũ chưa có hàm này).

- [ ] **Step 3: Cài đặt `sanitize_dialogue_text` và sửa `parse_dialogue_segments` trong `job_adapter.py`**

Trong `workshops/workshop-whiteboard/job_adapter.py`:
1. Thêm hàm `sanitize_dialogue_text`:
```python
REPORTING_VERBS = {"nói", "hỏi", "gầm lên", "quát", "đáp", "nghĩ", "cười lớn", "la lên", "thì thầm", "hô"}

def sanitize_dialogue_text(raw_text: str, known_speakers: list[str] | None = None) -> tuple[str | None, str]:
    if not raw_text or ":" not in raw_text:
        return None, raw_text.strip() if raw_text else ""

    parts = raw_text.split(":", 1)
    prefix = parts[0].strip()
    rest = parts[1].strip()

    # Loại trừ nếu có chứa số (giờ giấc 10:30, tỉ số)
    if any(char.isdigit() for char in prefix):
        return None, raw_text.strip()

    prefix_lower = prefix.lower()
    base_prefix = re.sub(r"\s*\([^)]*\)", "", prefix).strip()
    base_prefix_lower = base_prefix.lower()

    # Điều kiện A: Khớp Whitelist
    standard_narrators = {"người kể chuyện", "dẫn truyện", "kể chuyện", "narrator"}
    if base_prefix_lower in standard_narrators:
        return "Người Kể Chuyện", rest

    if known_speakers:
        for ks in known_speakers:
            if ks.lower() == base_prefix_lower or ks.lower() == prefix_lower:
                return ks, rest

    # Điều kiện B: Heuristic Title Case <= 4 từ và không chứa động từ tường thuật
    words = base_prefix.split()
    if 1 <= len(words) <= 4:
        # Kiểm tra xem từ cuối có phải động từ tường thuật không
        last_two = " ".join(w.lower() for w in words[-2:])
        last_one = words[-1].lower()
        if last_one in REPORTING_VERBS or last_two in REPORTING_VERBS:
            return None, raw_text.strip()

        # Kiểm tra tất cả các từ có viết hoa chữ cái đầu không
        if all(w[0].isupper() for w in words if w):
            return base_prefix, rest

    return None, raw_text.strip()
```

2. Cập nhật `parse_dialogue_segments` (loại bỏ việc append `p0 + ":"`):
- Thay thế dòng 197 `segments.append({"speaker": "narrator", "text": p0 + ":"})` bằng:
  Nếu `p0` là tên vai được bóc tách từ `sanitize_dialogue_text`, thì gán `current_speaker = spk` và KHÔNG append text `p0 + ":"`.
- Trong vòng lặp chính của `job_adapter.py` dòng 456-465:
  Áp dụng `sanitize_dialogue_text` cho TẤT CẢ các phân đoạn trước khi gọi `call_core_tts()`.

- [ ] **Step 4: Chạy lại test để xác nhận test THÀNH CÔNG**

Run:
```bash
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-whiteboard/tests/test_speaker_parser.py
```
Expected: PASS (tất cả 5 tests passed).

- [ ] **Step 5: Commit**

```bash
git add workshops/workshop-whiteboard/job_adapter.py workshops/workshop-whiteboard/tests/test_speaker_parser.py
git commit -m "feat(whiteboard): implement dialogue sanitizer to eliminate character name announcements"
```

---

### Task 4: Cập Nhật Role-Based Voice Presets & Rate +25% Trong `job_adapter.py`

**Files:**
- Modify: `workshops/workshop-whiteboard/job_adapter.py:99-154`
- Modify Test: `workshops/workshop-whiteboard/tests/test_speaker_parser.py`

- [ ] **Step 1: Viết test cho `resolve_speaker_voice` với các vai trò kịch bản**

Thêm vào `workshops/workshop-whiteboard/tests/test_speaker_parser.py`:
```python
from job_adapter import resolve_speaker_voice

def test_resolve_speaker_voice_roles():
    meta = {
        "characters_voice": {
            "lâm mặc": {"voice": "vi-VN-NamMinhNeural", "rate": "+20%", "pitch": "-3Hz"}
        }
    }
    # Khớp override từ metadata
    v_hero = resolve_speaker_voice("Lâm Mặc", job_meta=meta)
    assert v_hero["pitch"] == "-3Hz"
    assert v_hero["rate"] == "+20%"

    # Trưởng lão phản diện (preset role)
    v_elder = resolve_speaker_voice("Triệu Trưởng Lão")
    assert v_elder["pitch"] == "-6Hz"
    assert v_elder["rate"] == "+10%"

    # Nữ nhân / thiếu niên (preset role)
    v_girl = resolve_speaker_voice("Tiểu Thạch Đầu")
    assert v_girl["voice"] == "vi-VN-HoaiMyNeural"

    # Narrator mặc định cho storytelling là +25%
    v_narrator = resolve_speaker_voice("Người Kể Chuyện")
    assert v_narrator["rate"] == "+25%"
```

- [ ] **Step 2: Chạy test để xác nhận test THẤT BẠI**

Run:
```bash
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-whiteboard/tests/test_speaker_parser.py::test_resolve_speaker_voice_roles
```
Expected: FAIL.

- [ ] **Step 3: Cập nhật hàm `resolve_speaker_voice` trong `job_adapter.py`**

Xóa bỏ các hardcode tên truyện cũ ("Hạ Vi", "Đình Phong", "Kiên"), thay bằng bảng Role-based Presets:
- `default_rate`: Nếu không chỉ định, lấy mặc định `+25%` cho xưởng storytelling.
- Ánh xạ vai:
  + Dẫn truyện: `NamMinhNeural`, rate `+25%`, pitch `+0Hz`.
  + Phản diện / Lão: `NamMinhNeural`, rate `+10%`, pitch `-6Hz`.
  + Thanh niên kiêu ngạo / Công tử: `NamMinhNeural`, rate `+25%`, pitch `+3Hz`.
  + Nữ / Thiếu niên: `HoaiMyNeural`, rate `+20%`, pitch `+2Hz`.

- [ ] **Step 4: Chạy test để xác nhận test THÀNH CÔNG**

Run:
```bash
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-whiteboard/tests/test_speaker_parser.py
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add workshops/workshop-whiteboard/job_adapter.py workshops/workshop-whiteboard/tests/test_speaker_parser.py
git commit -m "feat(whiteboard): add role-based voice presets with default 1.25x rate"
```

---

### Task 5: Chuyển Trộn BGM Sang Một Lần Sau Khi Ghép Nối Video Hoàn Chỉnh

**Files:**
- Modify: `workshops/workshop-whiteboard/scripts/audio_mixer.py`
- Modify: `workshops/workshop-whiteboard/scripts/export_video.py`
- Modify Test: `workshops/workshop-whiteboard/tests/test_audio_mixer.py`

- [ ] **Step 1: Viết test cho hàm tạo filter complex có `normalize=0`, `afade` và `loudnorm`**

Cập nhật `workshops/workshop-whiteboard/tests/test_audio_mixer.py`:
```python
from audio_mixer import build_final_bgm_ducking_filter

def test_build_final_bgm_ducking_filter():
    filter_str = build_final_bgm_ducking_filter(
        total_duration_sec=120.0,
        bgm_base_vol=0.30,
        duck_ratio=6.0,
        target_lufs=-14.0
    )
    assert "normalize=0" in filter_str
    assert "sidechaincompress=" in filter_str
    assert "afade=t=out:st=118.0:d=2.0" in filter_str
    assert "loudnorm=I=-14.0" in filter_str
```

- [ ] **Step 2: Chạy test để xác nhận test THẤT BẠI**

Run:
```bash
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-whiteboard/tests/test_audio_mixer.py
```
Expected: FAIL.

- [ ] **Step 3: Cài đặt `build_final_bgm_ducking_filter` và cập nhật `export_video.py`**

1. Trong `audio_mixer.py`: Thêm hàm `build_final_bgm_ducking_filter` tạo filter complex chuẩn FFmpeg có `normalize=0`, `afade` 2 giây cuối, và `loudnorm=I={target_lufs}:LRA=11:TP=-1.5`.
2. Trong `export_video.py`:
   - Hàm `render_scene()`: Bỏ hoàn toàn phần lồng BGM `has_bgm` dòng 204-212. Chỉ giữ lại lồng giọng đọc `mp3_file`.
   - Hàm `export_whiteboard_video()`: Sau khi gọi `merge_scenes()` ghép thành file video thô `concat_raw.mp4`, nếu có `bgm_path`:
     - Dùng `ffprobe` lấy thời lượng tổng `dur_sec = get_media_duration(concat_raw)`.
     - Áp dụng lệnh FFmpeg trộn BGM với `build_final_bgm_ducking_filter` xuất ra `final_mp4`.
     - Nếu không có BGM: áp dụng filter `loudnorm` trực tiếp trên audio track của video.

- [ ] **Step 4: Chạy test để xác nhận test THÀNH CÔNG**

Run:
```bash
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-whiteboard/tests/test_audio_mixer.py
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add workshops/workshop-whiteboard/scripts/audio_mixer.py workshops/workshop-whiteboard/scripts/export_video.py workshops/workshop-whiteboard/tests/test_audio_mixer.py
git commit -m "refactor(whiteboard): apply BGM audio ducking and YouTube loudnorm once post-merge"
```

---

### Task 6: Tạo Script Tải BGM Tiên Hiệp Royalty-Free & `LICENSES.md`

**Files:**
- Create: `scripts/download-bgm.ps1`
- Create: `workshops/workshop-whiteboard/assets/audio/bgm/LICENSES.md`

- [ ] **Step 1: Viết script `scripts/download-bgm.ps1`**

Tải 2 bản nhạc nền mẫu phong cách cổ phong / tiên hiệp (Royalty-free) về `workshops/workshop-whiteboard/assets/audio/bgm/`:
- `xianxia-ambient.mp3`
- `battle-epic.mp3`
Script kiểm tra nếu tệp đã tồn tại thì bỏ qua, nếu tải thất bại thì fallback an toàn sang `healing-piano.mp3`.

- [ ] **Step 2: Tạo file `workshops/workshop-whiteboard/assets/audio/bgm/LICENSES.md`**

Ghi rõ tên track, tác giả, link nguồn, và loại giấy phép bản quyền (Creative Commons CC0 / YouTube Audio Library License) để bảo vệ kênh người dùng.

- [ ] **Step 3: Chạy thử script tải**

Run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/download-bgm.ps1
```
Expected: File nhạc được tải thành công về thư mục asset.

- [ ] **Step 4: Commit**

```bash
git add scripts/download-bgm.ps1 workshops/workshop-whiteboard/assets/audio/bgm/LICENSES.md
git commit -m "feat(assets): add BGM downloader script and royalty-free licensing documentation"
```

---

### Task 7: Tạo Thư Mục `prompts/` & Soạn Thảo `MASTER_STORY_PROMPT.md`

**Files:**
- Create: `prompts/MASTER_STORY_PROMPT.md`
- Create Test: `tests/test_master_prompt_schema.py`

- [ ] **Step 1: Tạo file `prompts/MASTER_STORY_PROMPT.md`**

Soạn thảo đầy đủ prompt 4 tầng:
1. Chỉ thị vai trò: "Ngươi là biên kịch trưởng chuyên sản xuất video truyện audio tiên hiệp/sảng văn triệu view".
2. Công thức Hook 15s vàng ở Beat 01 (Teaser cao trào) và Beat 02 (Giới thiệu & Kêu gọi Đăng ký kênh).
3. Công thức Sảng văn 3 hồi: Tuyệt lộ ➡️ Cơ duyên ➡️ Đột phá ➡️ Vả mặt.
4. Quy tắc nghiêm ngặt: `rawText` KHÔNG được chứa tên vai hay dấu hai chấm. Tên vai đặt ở `speaker`.
5. Mẫu JSON đầu ra hoàn chỉnh khớp `VideoJobSchema`.

- [ ] **Step 2: Viết test xác nhận mẫu JSON trong Prompt vượt qua kiểm tra Zod Schema**

Tạo `tests/test_master_prompt_schema.py`:
Đọc file `prompts/MASTER_STORY_PROMPT.md`, trích xuất block JSON mẫu và kiểm tra tính hợp lệ bằng schema validation.

- [ ] **Step 3: Chạy test xác nhận mẫu kịch bản hợp lệ**

Run:
```bash
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest tests/test_master_prompt_schema.py
```
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add prompts/MASTER_STORY_PROMPT.md tests/test_master_prompt_schema.py
git commit -m "docs(prompts): add master story prompt with 15s golden hook and schema validation"
```

---

### Task 8: End-to-End Integration Verification

**Files:**
- Create Test: `output/jobs/job-test-e2e-audio-drama.json`

- [ ] **Step 1: Tạo kịch bản mẫu ngắn gồm 2 phân cảnh test toàn diện**

Tạo `output/jobs/job-test-e2e-audio-drama.json` với:
- Rate `+25%`.
- 2 phân cảnh (`scene-01`, `scene-02`).
- Có cả lời dẫn và lời thoại nhân vật ("Lâm Mặc", "Trưởng Lão").
- Cố tình chèn 1 dòng có tiền tố `"Người Kể Chuyện: ..."` để kiểm tra bộ lọc sanitizer tự động bóc tách.

- [ ] **Step 2: Chạy xuất video thử nghiệm bằng lệnh `export_video.py`**

Run:
```bash
workshops/workshop-whiteboard/.venv/Scripts/python.exe workshops/workshop-whiteboard/scripts/export_video.py --job job-test-e2e-audio-drama
```
Expected: Video xuất thành công không lỗi, xuất file `output/whiteboard/job-test-e2e-audio-drama.mp4`.

- [ ] **Step 3: Đo kiểm âm thanh bằng `ffprobe` và `ebur128`**

Run:
```bash
ffmpeg -i output/whiteboard/job-test-e2e-audio-drama.mp4 -af "ebur128=framelog=verbose" -f null -
```
Expected:
- Integrated Loudness đạt xấp xỉ `-14.0 LUFS` (±1.5 LUFS).
- BGM chạy liền mạch qua 2 phân cảnh mà không bị khởi động lại.
- Dọn dẹp tệp test sau khi xác minh xong.

- [ ] **Step 4: Chạy toàn bộ test suites của repo để đảm bảo không có regression**

Run:
```bash
cmd.exe /c "npm.cmd test"
workshops/workshop-whiteboard/.venv/Scripts/python.exe -m pytest workshops/workshop-whiteboard/tests/
```
Expected: Tất cả bài test đều PASS.

- [ ] **Step 5: Commit hoàn tất**

```bash
git add output/jobs/job-test-e2e-audio-drama.json
git commit -m "test(e2e): verify audio drama pipeline with 1.25x voice, sanitizer and BGM ducking"
```

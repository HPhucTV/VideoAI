# Đặc Tả Kỹ Thuật: Nâng Cấp Kịch Bản Sảng Văn, Voice 1.25x Và Tự Động Hòa Trộn BGM (Audio Drama)

- **Ngày sửa đổi:** 2026-10-17
- **Phiên bản:** 2.0 (Lead Engineer Revision — Nguồn sự thật đối chiếu trực tiếp từ Codebase)
- **Trạng thái:** Chờ phê duyệt của Tech Lead / User
- **Phạm vi tác động:** `workshops/workshop-whiteboard`, `core/tts`, `core/schema`, `prompts/`

---

## 0. Lịch Sử & Đối Chiếu Hiện Trạng Codebase

### 0.1. Bảng thay đổi so với bản thảo trước (Changelog vs v1.0)

| Mục | Nội dung thay đổi trong bản v2.0 | Lý do thay đổi & Căn cứ kỹ thuật | File code đã xác minh |
| :--- | :--- | :--- | :--- |
| **Bối cảnh narrator** | Sửa rate mặc định hiện tại thành `-4%` (thay vì `-15%`). | Code thực tế trong `job_adapter.py` đang dùng `-4%` làm default rate. | [`job_adapter.py:116`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py#L116) |
| **Module 4 (BGM)** | Đổi từ "xây mới" sang "tinh chỉnh kiến trúc trộn BGM". | Whiteboard đã có sẵn `audio_mixer.py`, cờ `--bgm`, `--bgm-vol`, hàm `resolve_bgm_path`, `generate_default_ambient_bgm`. | [`audio_mixer.py:26-56`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/audio_mixer.py#L26-L56) |
| **Luồng trộn BGM** | Chuyển trộn BGM từ từng phân cảnh (`render_scene`) sang trộn **MỘT LẦN DUY NHẤT** sau khi ghép nối (`merge_scenes`). | Code cũ trong `export_video.py` lặp BGM từ giây 0 ở mỗi scene, khiến nhạc bị giật về đầu ở từng điểm chuyển cảnh. | [`export_video.py:204-212`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/export_video.py#L204-L212), [`export_video.py:387-398`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/export_video.py#L387-L398) |
| **Filter Ducking** | Bỏ khẳng định "tự ép xuống -20dB"; bổ sung `normalize=0` cho `amix`, fade-out 2s, `loudnorm=-14 LUFS`. | Mức nén sidechain phụ thuộc biên độ giọng đọc; `amix` mặc định chia đôi âm lượng các input nếu thiếu `normalize=0`. | [`audio_mixer.py:38`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/audio_mixer.py#L38) |
| **Đường dẫn BGM** | Đổi thành `workshops/workshop-whiteboard/assets/audio/bgm/`. Dùng `Path.exists()`. | Đường dẫn `assets/bgm/` cũ không tồn tại; `existsSync` là API Node.js, không dùng trong script Python. | [`audio_mixer.py:52`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/audio_mixer.py#L52) |
| **Module 2 (Sanitizer)** | Thay Regex cũ bằng quy tắc ngữ nghĩa chặt chẽ (whitelist vai, Title Case <= 4 từ, loại trừ giờ giấc/số). | Regex cũ khớp nhầm câu thường có dấu hai chấm ("Hắn gầm lên: Ngươi dám sao?!") và mốc giờ ("10:30"). | [`job_adapter.py:160`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py#L160), [`job_adapter.py:197`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py#L197) |
| **Vị trí Sanitizer** | Đặt tại Python trong `job_adapter.py` trước khi gọi TTS cho mọi segment (kể cả `explicit_speaker`). | Single Source of Truth cho luồng dựng whiteboard; xử lý triệt để nhánh `explicit_speaker` và `parse_dialogue_segments`. | [`job_adapter.py:456-482`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py#L456-L482) |
| **Module 3 (TTS)** | Xóa bỏ file ảo `voice_generator.py`; đưa luồng thật vào spec; bổ sung sửa `computeAudioHash` (cache key). | `voice_generator.py` không tồn tại trong repo; `computeAudioHash` hiện thiếu `pitch` và `volume` khiến cache bị đè. | [`core/tts/index.ts:45-48`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/tts/index.ts#L45-L48) |
| **Cấu hình Speed/Rate** | Bỏ qua `speed`, chỉ dùng `rate` (`+25%`). | Edge-TTS trong `core/tts/index.ts` chỉ nhận `--rate`, bỏ qua trường `speed`. | [`core/tts/index.ts:89-97`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/tts/index.ts#L89-L97) |
| **Vị trí trường speaker** | Thống nhất chuẩn hóa trường `speaker` ở root của beat và hỗ trợ fallback `beat.voice.speaker`. | Tránh lỗi lệch pha giữa `job_adapter.py:454` (`beat.speaker`) và `core/schema/job.ts:25` (`beat.voice.speaker`). | [`job_adapter.py:454`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py#L454), [`core/schema/job.ts:25`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/schema/job.ts#L25) |
| **Module 1 (Prompt)** | Bổ sung `job.json` mẫu hoàn chỉnh khớp `VideoJobSchema` Zod; ghi rõ tạo thư mục `prompts/`. | Repo hiện tại chưa có thư mục `prompts/`; cần schema validation chống sinh sai cấu trúc. | [`core/schema/job.ts:52-72`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/schema/job.ts#L52-L72) |

---

### 0.2. Bảng đối chiếu sự thật với Codebase (Truth Matrix)

| Khẳng định kỹ thuật trong spec | File liên quan & Dòng code thực tế | Trạng thái xác minh | Ghi chú kỹ thuật |
| :--- | :--- | :--- | :--- |
| File `voice_generator.py` không tồn tại trong repo | Toàn bộ workspace `VideoAI` | `[đã xác minh]` | Luồng thật là `job_adapter.py` gọi Node CLI `core/bin/tts.js`. |
| Rate mặc định narrator hiện tại là `-4%` | [`job_adapter.py:116`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py#L116) | `[đã xác minh]` | `default_rate = default_voice_config.get("rate", "-4%")`. |
| Edge-TTS bỏ qua `speed`, chỉ dùng `rate`, `pitch`, `volume` | [`core/tts/index.ts:89-97`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/tts/index.ts#L89-L97) | `[đã xác minh]` | Chỉ có `args.push("--rate=...")`, không có cờ `--speed`. |
| `computeAudioHash` bỏ quên `pitch` và `volume` | [`core/tts/index.ts:45-48`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/tts/index.ts#L45-L48) | `[đã xác minh]` | Chuỗi hash: `${provider}:${voice}:${rate}:${normalizedText}`. |
| BGM bị trộn theo từng scene và lặp từ 0s | [`export_video.py:204-212`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/export_video.py#L204-L212) | `[đã xác minh]` | Nằm trong hàm `render_scene()`, lặp `-stream_loop -1` cho từng scene. |
| Module audio ducking đã có sẵn một phần | [`audio_mixer.py:26-56`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/audio_mixer.py#L26-L56) | `[đã xác minh]` | Đã có `build_ducking_filter_complex`, `resolve_bgm_path`, `generate_default_ambient_bgm`. |
| Đường dẫn BGM mặc định hiện có | [`audio_mixer.py:52`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/audio_mixer.py#L52) | `[đã xác minh]` | Tệp `healing-piano.mp3` tại `workshops/workshop-whiteboard/assets/audio/bgm/`. |
| Phiên bản FFmpeg trên hệ thống | CLI: `ffmpeg -version` | `[đã xác minh]` | Phiên bản 9.0.2 (hỗ trợ `sidechaincompress`, `amix=normalize=0`, `loudnorm`). |
| Thư mục `prompts/` hiện chưa tồn tại | Thư mục gốc `C:\Users\tranh\Documents\Duy\VideoAI` | `[đã xác minh]` | `Test-Path 'prompts'` trả về `False`. Sẽ được tạo mới. |
| Lỗi đọc xưng vai do giữ `p0 + ":"` và nhánh explicit_speaker | [`job_adapter.py:197`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py#L197), [`job_adapter.py:456-457`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py#L456-L457) | `[đã xác minh]` | Nhánh 3 append `p0 + ":"`, nhánh explicit đưa thẳng `raw_text` vào TTS. |

---

## 1. Mục Tiêu & Bối Cảnh (Executive Summary & Goals)

Dựa trên phản hồi thực tế từ sản phẩm video truyện tu tiên audio (*Phế Đan Nghịch Thiên*), sản phẩm hiện tại gặp 3 điểm nghẽn nghiêm trọng về trải nghiệm người xem:
1. **Nội dung cốt truyện buồn ngủ:** ChatGPT/Claude mặc định sáng tác theo phong cách văn xuôi tả cảnh dài dòng, thiếu xung đột sinh tử trực diện, thiếu nhịp điệu dồn dập và các pha "vả mặt/phản sát" đắc ý (sảng văn).
2. **Thiếu lời giới thiệu / Hook mở đầu:** Không có Hook 10–15 giây đầu giữ chân người nghe, vào truyện đột ngột khiến tỷ lệ giữ chân (Audience Retention) trên YouTube tụt dốc.
3. **Giọng đọc monotone và bị lỗi xưng vai:**
   - Tốc độ đọc narrator hiện tại trong code đang đặt mặc định là `-4%` (khoảng 0.96x), nghe đều đều và thiếu năng lượng kịch tính.
   - Khi chuyển vai, giọng đọc phát âm to cả chữ *"Người kể chuyện:"*, *"Lâm Mặc:"* phá hỏng tính điện ảnh của một tác phẩm kịch truyền thanh (Audio Drama).
   - Nhạc nền (BGM) đang bị cắt vụn và nhảy về giây 0 mỗi khi đổi phân cảnh (`scene-XX`), gây đứt gãy cảm xúc âm nhạc.

### Mục tiêu kỹ thuật cụ thể:
- **Cung cấp Master Prompt Siêu Kịch Bản:** Chuẩn hóa chỉ thị cho ChatGPT/Claude để 1-click xuất kịch bản sảng văn dồn dập, có sẵn Hook 15s vàng, tuân thủ nghiêm ngặt `VideoJobSchema` của OmniVideo Studio.
- **Triệt tiêu 100% lỗi đọc tên vai:** Tái cấu trúc hàm xử lý hội thoại trong `job_adapter.py` với bộ lọc ngữ nghĩa (Dialogue Sanitizer) nhận diện chính xác vai diễn và chỉ đưa lời thoại thuần túy sang TTS.
- **Nâng tốc độ đọc lên 1.25x (`rate: "+25%"`):** Chỉ áp dụng cho archetype `storytelling` trong xưởng Whiteboard (Xưởng 3), không đổi mặc định toàn hệ thống. Ánh xạ âm sắc nhân vật theo vai trò kịch bản.
  > *Lưu ý kỹ thuật:* Tốc độ đọc nhanh hơn 25% sẽ rút ngắn thời lượng âm thanh, kéo theo việc retime animation vẽ tay và phụ đề. Bắt buộc nghe thử và kiểm tra đồng bộ trên một phân cảnh mẫu trước khi áp dụng hàng loạt.
  > *Giới hạn nền tảng:* Edge-TTS tiếng Việt chính thức chỉ có 2 giọng (`vi-VN-NamMinhNeural` và `vi-VN-HoaiMyNeural`). Các vai nam chỉ khác nhau nhẹ qua việc biến điệu `pitch` và `rate`.
- **Tinh chỉnh kiến trúc trộn BGM (Audio Ducking):** Chuyển việc hòa trộn nhạc nền từ cấp phân cảnh (`render_scene`) sang trộn **MỘT LẦN DUY NHẤT** trên bản ghép nối cuối (`merge_scenes`), áp dụng Audio Ducking, fade-out 2 giây cuối và chuẩn hóa âm lượng YouTube -14 LUFS.

---

## 2. Kiến Trúc & Luồng Dữ Liệu Thực Tế (Architecture & Data Flow)

```
[ Ý Tưởng Kịch Bản Thô ]
       │
       ▼ (Dán prompts/MASTER_STORY_PROMPT.md vào ChatGPT / Claude)
[ File job.json Hoàn Chỉnh ] ── Validate bằng VideoJobSchema (core/schema/job.ts)
       │
       ▼
[ workshops/workshop-whiteboard/job_adapter.py ]
       │
       ├─► [ Dialogue Sanitizer ] (Bóc tách tên vai theo Whitelist/TitleCase; lọc sạch text)
       │
       ├─► [ Preset Voice Resolver ] (Áp dụng rate +25%, pitch theo vai trò)
       │
       ▼ (Gọi qua CLI core/bin/tts.js)
[ core/tts/index.ts ]
       │
       ├─► computeAudioHash (Băm: provider + voice + rate + pitch + volume + normalizedText)
       │        └─► Tránh cache collision khi đổi pitch giữa các nhân vật
       │
       └─► python -m edge_tts (Sinh file .mp3 và .vtt cho từng segment)
               │
               ▼
[ workshops/workshop-whiteboard/scripts/export_video.py ]
       │
       ├─► render_scene() (Lặp từng scene: chỉ vẽ nét tay + lồng Voice thuần, KHÔNG trộn BGM)
       │
       ├─► merge_scenes() (_ffmpeg_concat_copy nối tất cả scene-XX.mp4 thành raw_joined.mp4)
       │
       └─► apply_final_bgm_and_mastering() (TRỘN BGM 1 LẦN DUY NHẤT TRÊN raw_joined.mp4)
               ├─► Input 0: raw_joined.mp4 (chứa full audio voice liền mạch)
               ├─► Input 1: BGM lặp (-stream_loop -1 -i assets/audio/bgm/...)
               ├─► Filter: sidechaincompress (ducking) + amix(normalize=0) + afade(out 2s) + loudnorm(-14 LUFS)
               └─► Output: final.mp4 (Chuẩn âm lượng YouTube, âm nhạc xuyên suốt)
```

---

## 3. Đặc Tả Chi Tiết 4 Module

### 3.1. Module 1: Master Prompt Siêu Kịch Bản (`prompts/MASTER_STORY_PROMPT.md`)

Thư mục `prompts/` hiện chưa tồn tại và sẽ được tạo mới ở thư mục gốc repo.
File `prompts/MASTER_STORY_PROMPT.md` chứa prompt hướng dẫn chuyên sâu cho ChatGPT/Claude, ép buộc xuất ra cấu trúc JSON chuẩn 100% khớp với `VideoJobSchema` trong [`core/schema/job.ts`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/schema/job.ts).

#### Cấu trúc 4 tầng bắt buộc trong Prompt:
1. **Tầng 0: 15 Giây Hook Vàng (Bắt buộc ở Beat 01 & 02):**
   - *Beat 01 (Teaser cao trào):* Trích xuất câu thoại nghẹt thở nhất ở cuối truyện (xung đột sống còn).
   - *Beat 02 (Giới thiệu & Kêu gọi):* Lời chào thương hiệu kênh, đặt câu hỏi kích thích tò mò và kêu gọi Đăng ký kênh (Subscribe CTA).
2. **Tầng 1: Nhịp điệu Sảng Văn 3 Hồi:**
   - Triệt tiêu văn phong tả cảnh dài lê thê. Mở đầu bằng xung đột hành động ngay lập tức.
   - Công thức: Bị áp bức đường cùng ➡️ Bật ngửa cơ duyên hắc ám ➡️ Đột phá sức mạnh ➡️ Phản sát vả mặt cực đã tai.
3. **Tầng 2: Quy tắc Lời Thoại Thuần:**
   - Trường `rawText` TUYỆT ĐỐI KHÔNG ghi kèm tên nhân vật hay dấu hai chấm. Tên nhân vật được khai báo riêng tại trường `speaker`.
4. **Tầng 3: Schema Contract Chuẩn:**
   - Output của prompt phải vượt qua bài kiểm tra của `VideoJobSchema.parse(json)`.

#### `job.json` Mẫu Chuẩn Cho Master Prompt:
```json
{
  "jobId": "job-phe-dan-nghich-thien-sample",
  "title": "Phế Đan Nghịch Thiên - Hồi 1",
  "workshop": "whiteboard",
  "archetype": "storytelling",
  "targetPlatform": "youtube_long",
  "canvas": {
    "width": 1920,
    "height": 1080,
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
    "channel": "Truyện Audio Tiên Hiệp",
    "author": "Omni-Director",
    "tags": ["tutien", "huyenhuyen", "whiteboard"],
    "characters": [
      "Lâm Mặc (20 tuổi, Tạp dịch cạo xỉ)",
      "Triệu Vô Cực (Trưởng lão Địa Hỏa)",
      "Sở Thiên Kiêu (Đệ tử chân truyền)",
      "Người Kể Chuyện (Dẫn truyện)"
    ],
    "characters_voice": {
      "người kể chuyện": { "voice": "vi-VN-NamMinhNeural", "rate": "+25%", "pitch": "+0Hz" },
      "lâm mặc": { "voice": "vi-VN-NamMinhNeural", "rate": "+20%", "pitch": "-3Hz" },
      "triệu vô cực": { "voice": "vi-VN-NamMinhNeural", "rate": "+10%", "pitch": "-6Hz" },
      "sở thiên kiêu": { "voice": "vi-VN-NamMinhNeural", "rate": "+25%", "pitch": "+3Hz" }
    }
  },
  "beats": [
    {
      "id": "beat_01",
      "role": "hook_teaser",
      "speaker": "Lâm Mặc",
      "rawText": "Nếu các người coi tạp dịch cạo xỉ như ta là sâu kiến, thì hôm nay, ta sẽ dùng chính ngọn hắc hỏa này thiêu rụi toàn bộ Thanh Vân Tông!",
      "cues": { "camera": "zoom_in_punch", "sfx": "fire_burst" },
      "visual": {
        "sceneId": "scene-01",
        "badge": "HOOK CAO TRÀO",
        "headline": "Ngọn Lửa Phế Tàn Nổi Dậy"
      }
    },
    {
      "id": "beat_02",
      "role": "hook_intro",
      "speaker": "Người Kể Chuyện",
      "rawText": "Chào mừng các đạo hữu đã quay trở lại. Liệu một tên tạp dịch mang phế đan có thể nghịch chuyển càn khôn? Hãy nhấn Đăng ký kênh và cùng theo dõi ngay sau đây.",
      "cues": { "camera": "static" },
      "visual": {
        "sceneId": "scene-01",
        "badge": "GIỚI THIỆU TRUYỆN",
        "headline": "Phế Đan Nghịch Thiên"
      }
    },
    {
      "id": "beat_03",
      "role": "scene_01_beat_1",
      "speaker": "Người Kể Chuyện",
      "rawText": "Mùi lưu huỳnh nồng nặc bốc lên từ lò đan số chín dưới đáy vực sâu Địa Hỏa.",
      "visual": {
        "sceneId": "scene-01",
        "badge": "HỒI 1 - ĐỊA HỎA ĐAN PHÒNG",
        "headline": "Vực Sâu Lò Đan"
      }
    }
  ]
}
```

---

### 3.2. Module 2: Bộ Lọc Dialogue Sanitizer (Chống Đọc Tên Vai)

#### 3.2.1. Phân tích nguyên nhân gốc trong Code hiện tại
Trong [`workshops/workshop-whiteboard/job_adapter.py`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py):
1. **Dòng 184 (`known_speakers`):** Bị hard-code cố định tên nhân vật của truyện cũ (`["Hạ Vi", "Lâm Hạ Vi", "Đình Phong", "Trần Đình Phong", "Kiên", "Trợ lý Kiên"]`). Khi gặp truyện mới (Lâm Mặc, Triệu Vô Cực), danh sách này vô dụng nếu `metadata.characters` không được nạp đầy đủ.
2. **Dòng 197 (Nhánh 3 - Văn xuôi nhúng):** Khi phát hiện dấu hai chấm, code thực hiện `segments.append({"speaker": "narrator", "text": p0 + ":"})`. Đây chính là thủ phạm nhét cả tên nhân vật và dấu hai chấm vào chuỗi văn bản gửi cho TTS đọc!
3. **Dòng 456–457 (Nhánh `explicit_speaker`):** Khi beat đã có trường `speaker`, code gán trực tiếp `segments = [{"speaker": explicit_speaker, "text": raw_text}]` mà hoàn toàn KHÔNG kiểm tra xem `raw_text` có bị người dùng copy sót tiền tố `Tên:` hay không.

#### 3.2.2. Thiết kế lại quy tắc Sanitizer
Quy tắc cũ bằng regex lỏng lẻo `^\s*([^:\n]{1,35})\s*[:：]\s*(.+)$` sẽ cắt nhầm:
- Câu thoại tường thuật: `"Hắn gầm lên: Ngươi dám sao?!"` ➡️ bị nhận nhầm `"Hắn gầm lên"` là tên vai!
- Mốc thời gian: `"Lúc 10:30 sáng, hắn bước vào..."` ➡️ bị nhận nhầm `"Lúc 10"` là tên vai!

**Quy tắc mới xác định tiền tố Tên Vai (Prefix Dialogue Sanitizer):**
Chuỗi đứng trước dấu hai chấm `prefix:` chỉ được coi là Tên Vai khi thỏa mãn một trong hai điều kiện:
1. **Điều kiện A (Whitelist Match):** `prefix` trùng khớp (không phân biệt hoa thường) với danh sách nhân vật đã khai báo trong `metadata.characters` (qua hàm `extract_characters_from_metadata`) HOẶC trùng các bí danh dẫn truyện chuẩn: `["người kể chuyện", "dẫn truyện", "kể chuyện", "narrator"]`.
2. **Điều kiện B (Heuristic Pattern Match):**
   - `prefix` có độ dài từ 1 đến 4 từ.
   - Tất cả các từ đều viết hoa chữ cái đầu (Title Case hoặc UPPERCASE), ví dụ: `Lâm Mặc`, `SỞ THIÊN KIÊU`. Có thể kèm cụm mô tả trạng thái trong ngoặc đơn, ví dụ: `Sở Thiên Kiêu (hừ lạnh)`.
   - Dấu hai chấm phía sau bắt buộc phải có khoảng trắng (tránh khớp nhầm URL `https://` hoặc tỉ số).
   - **Phủ định nghiêm ngặt (Exclusions):** `prefix` TUYỆT ĐỐI KHÔNG chứa chữ số (loại trừ giờ giấc `10:30`), không chứa các động từ tường thuật tiếng Việt phổ biến ở cuối cụm (`nói`, `hỏi`, `gầm lên`, `quát`, `đáp`, `nghĩ`, `cười lớn`).

#### Bảng Kiểm Thử Đúng / Sai Của Sanitizer:

| Văn bản đầu vào (`rawText`) | Kết quả nhận diện | `speaker` trích xuất | Văn bản đưa vào TTS (`clean_text`) | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| `Người Kể Chuyện: Tiên sơn vạn trượng...` | **Là tên vai** (ĐK A) | `Người Kể Chuyện` | `Tiên sơn vạn trượng...` | Cắt sạch tiền tố dẫn chuyện |
| `Lâm Mặc: Các ngươi cứ đợi đấy!` | **Là tên vai** (ĐK A & B) | `Lâm Mặc` | `Các ngươi cứ đợi đấy!` | Cắt sạch tên nhân vật |
| `Sở Thiên Kiêu (lạnh lùng): Quỳ xuống!` | **Là tên vai** (ĐK B) | `Sở Thiên Kiêu` | `Quỳ xuống!` | Nhận diện cả cụm biểu cảm |
| `Hắn gầm lên: Ngươi dám sao?!` | **KHÔNG phải vai** (Có verb) | Giữ nguyên vai cũ | `Hắn gầm lên: Ngươi dám sao?!` | Tránh cắt nhầm câu văn xuôi |
| `Lúc 10:30 sáng, lò đan phát nổ.` | **KHÔNG phải vai** (Có số) | Giữ nguyên vai cũ | `Lúc 10:30 sáng, lò đan phát nổ.` | Tránh cắt nhầm mốc thời gian |
| `Tỷ lệ 1:2 nghiêng về phía đối thủ.` | **KHÔNG phải vai** (Tỉ số) | Giữ nguyên vai cũ | `Tỷ lệ 1:2 nghiêng về phía đối thủ.` | Dấu `:` không có khoảng trắng sau |
| `Nàng mỉm cười nhẹ nhàng.` | **Không có dấu hai chấm** | Giữ nguyên vai cũ | `Nàng mỉm cười nhẹ nhàng.` | Câu trần thuật bình thường |

#### 3.2.3. Vị trí cài đặt và kiến trúc Single Source of Truth
- **Quyết định kiến trúc:** Cài đặt hàm `sanitize_dialogue_text(raw_text, known_speakers)` bằng **Python** trực tiếp trong module `workshops/workshop-whiteboard/job_adapter.py`.
- **Lý do chọn Python trong `job_adapter.py`:**
  - `job_adapter.py` là trung tâm điều phối của xưởng Whiteboard, chịu trách nhiệm phân tích kịch bản thành các segments trước khi gọi TTS.
  - Đặt tại đây sẽ chặn đứng lỗi ở cấp phân rã kịch bản, bao quát được **MỌI phân đoạn** trước khi gọi `call_core_tts()`, bao gồm cả nhánh `explicit_speaker` (dòng 456) lẫn nhánh `parse_dialogue_segments` (dòng 461).
  - Không tạo thêm phụ thuộc IPC/CLI sang Node.js, duy trì hiệu năng cao và dễ dàng viết unit test bằng `pytest`.

---

### 3.3. Module 3: Tốc Độ Đọc 1.25x & Phân Vai Âm Sắc (Audio Drama)

#### 3.3.1. Xác minh luồng gọi TTS và các file liên quan
- Trong repo **KHÔNG TỒN TẠI** file `voice_generator.py`.
- **Luồng gọi thực tế:**
  [`job_adapter.py:482`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/job_adapter.py#L482) (`call_core_tts`) ➡️ chạy subprocess gọi CLI Node [`core/bin/tts.js`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/bin/tts.js) ➡️ thực thi hàm `synthesizeVoice` trong [`core/tts/index.ts`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/tts/index.ts) ➡️ thực thi lệnh hệ thống `python -m edge_tts`.

#### 3.3.2. Điều kiện tiên quyết: Sửa Cache Key trong `core/tts/index.ts`
Trong [`core/tts/index.ts:45-48`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/tts/index.ts#L45-L48):
```typescript
// HIỆN TẠI (LỖI CACHE): Thiếu pitch và volume
export function computeAudioHash(req: TTSRequest, normalizedText: string): string {
  const payload = `${req.provider || "edge-tts"}:${req.voice || "vi-VN-NamMinhNeural"}:${req.rate || "+0%"}:${normalizedText}`;
  return createHash("sha256").update(payload).digest("hex").slice(0, 16);
}
```
*Hậu quả:* Khi hai nhân vật nam đọc cùng một câu thoại với cùng `rate="+25%"` nhưng khác `pitch` (`-6Hz` vs `+3Hz`), hash sinh ra bị trùng nhau hoàn toàn! Nhân vật thứ hai sẽ bị lấy nhầm file audio của nhân vật thứ nhất trong cache.

**Đề xuất sửa đổi bắt buộc (Tiền đề cho phân vai âm sắc):**
```typescript
// SỬA ĐỔI: Đưa đầy đủ pitch và volume vào cache key
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

#### 3.3.3. Quy định tham số Rate vs Speed
- Trong [`core/tts/index.ts:89-97`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/tts/index.ts#L89-L97), Edge-TTS **chỉ đọc tham số `rate`** (ví dụ `--rate=+25%`), hoàn toàn bỏ qua `speed`.
- Vì vậy, hệ thống quy chuẩn sử dụng thống nhất chuỗi `rate` (dạng phần trăm `"+25%"`). Không sử dụng trường `speed` dạng số thập phân để tránh hiểu nhầm.

#### 3.3.4. Bảng Preset Âm Sắc Theo Vai Trò Kịch Bản (Role-based Presets)
Tuyệt đối không hard-code tên riêng nhân vật của một bộ truyện cụ thể vào mã nguồn lõi. Trong hàm `resolve_speaker_voice()` của `job_adapter.py`, hệ thống phân loại theo **VAI TRÒ (Archetype Role)**:

| Vai trò trừu tượng | Từ khóa nhận diện trong vai trò | Voice ID | Rate | Pitch | Mô tả âm sắc |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dẫn truyện (Narrator)** | `narrator`, `dẫn truyện`, `kể chuyện` | `vi-VN-NamMinhNeural` | `+25%` | `+0Hz` | Nhịp nhanh 1.25x, rõ ràng, dồn dập |
| **Nam chính (Protagonist)** | `chính`, `nam chính`, hoặc khớp `metadata.characters[0]` | `vi-VN-NamMinhNeural` | `+20%` | `-3Hz` | Trầm vừa, gằn giọng, quật cường |
| **Phản diện già (Antagonist)**| `trưởng lão`, `lão`, `chưởng môn`, `ma đầu`, `tộc trưởng` | `vi-VN-NamMinhNeural` | `+10%` | `-6Hz` | Trầm sâu, lạnh lùng, uy áp |
| **Thanh niên ngạo mạn** | `thiếu gia`, `công tử`, `chân truyền`, `đệ tử` | `vi-VN-NamMinhNeural` | `+25%` | `+3Hz` | Giọng sắc, cao, kiêu căng |
| **Nữ giới / Thiếu niên** | `nữ`, `cô`, `nàng`, `muội`, `tiểu`, `thiếu niên` | `vi-VN-HoaiMyNeural` | `+20%` | `+2Hz` | Trong trẻo, thanh thoát |

*Ưu tiên ghi đè (Override Priority):* Cấu hình trong `metadata.characters_voice` của job luôn có độ ưu tiên cao nhất, đè lên bảng preset mặc định ở trên.

#### 3.3.5. Thống nhất vị trí trường `speaker`
- Hiện tại: `job_adapter.py:454` đọc `beat.get("speaker")`, trong khi `core/schema/job.ts:25` đặt ở `beat.voice.speaker`.
- **Thống nhất chuẩn hóa:**
  1. Cho phép khai báo `speaker` trực tiếp tại root của beat: `beat.speaker` (giúp viết kịch bản tự nhiên, tinh gọn). Cập nhật `VideoBeatSchema` trong [`core/schema/job.ts`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/schema/job.ts) thêm `speaker: z.string().optional()`.
  2. Trong `job_adapter.py`, đọc theo thứ tự fallback an toàn:
     `speaker = beat.get("speaker") or beat.get("voice", {}).get("speaker")`

---

### 3.4. Module 4: Tinh Chỉnh BGM & Audio Ducking Sau Ghép Nối

#### 3.4.1. Hiện trạng code và Vấn đề kỹ thuật
- Repo đã có sẵn file [`workshops/workshop-whiteboard/scripts/audio_mixer.py`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/audio_mixer.py) với bộ lọc `sidechaincompress`, các cờ CLI `--bgm`, `--bgm-vol`, hàm `resolve_bgm_path()`, `generate_default_ambient_bgm()` và file test [`tests/test_audio_mixer.py`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/tests/test_audio_mixer.py).
- **Vấn đề cốt tử hiện tại:** Trong [`export_video.py:204-212`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/export_video.py#L204-L212), việc trộn BGM được thực hiện bên trong hàm `render_scene()`. Mỗi phân cảnh áp dụng lệnh `-stream_loop -1 -i bgm_path`, khiến nhạc nền bị khởi động lại từ giây 0 ở mỗi scene. Khi ghép nối bằng `merge_scenes()`, âm nhạc bị vấp và giật cục liên tục.

#### 3.4.2. Thiết kế lại luồng trộn BGM: Trộn MỘT LẦN DUY NHẤT sau khi nối
1. **Trong `render_scene()` ([`export_video.py`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/export_video.py)):**
   - Loại bỏ hoàn toàn khối trộn BGM.
   - Phân cảnh chỉ xuất video vẽ nét tay kèm audio giọng đọc thuần túy (`mp3_file`) bằng lệnh stream copy (`-c:v copy`).
2. **Sau khi `merge_scenes()` hoàn tất ([`export_video.py:393-398`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/scripts/export_video.py#L393-L398)):**
   - Nối toàn bộ video phân cảnh thành tệp tạm `video_voice_concat.mp4` (video mượt mà, track giọng đọc liên tục).
   - Dùng `ffprobe` lấy chính xác tổng thời lượng video `total_dur_sec`.
   - Tiến hành trộn BGM một lần duy nhất lên `video_voice_concat.mp4` để xuất ra `final.mp4`.

#### 3.4.3. Luồng FFmpeg Mới, Index Input & Filter Complex
- **Input 0:** `video_voice_concat.mp4` (Video + Giọng đọc nối liền).
- **Input 1:** Nhạc nền BGM (`-stream_loop -1 -i bgm_path`).
- **Chuỗi Filter Complex:**
  ```text
  [0:a]asplit=2[voice_sc][voice_mix];
  [1:a]volume=0.30[bgm_in];
  [bgm_in][voice_sc]sidechaincompress=threshold=0.04:ratio=6:attack=100:release=600[ducked_bgm];
  [voice_mix][ducked_bgm]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[mix_raw];
  [mix_raw]afade=t=out:st={total_dur_sec - 2.0}:d=2.0,loudnorm=I=-14:LRA=11:TP=-1.5[outa]
  ```
- **Lệnh FFmpeg đầy đủ:**
  ```bash
  ffmpeg -y \
    -i video_voice_concat.mp4 \
    -stream_loop -1 -i assets/audio/bgm/healing-piano.mp3 \
    -filter_complex "[0:a]asplit=2[voice_sc][voice_mix];[1:a]volume=0.30[bgm_in];[bgm_in][voice_sc]sidechaincompress=threshold=0.04:ratio=6:attack=100:release=600[ducked_bgm];[voice_mix][ducked_bgm]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[mix_raw];[mix_raw]afade=t=out:st={total_dur_sec - 2.0}:d=2.0,loudnorm=I=-14:LRA=11:TP=-1.5[outa]" \
    -map 0:v -map "[outa]" \
    -c:v copy \
    -c:a aac -b:a 192k -ar 44100 -ac 2 \
    final.mp4
  ```

#### 3.4.4. Tiêu chí kiểm chứng Audio Ducking ĐO ĐƯỢC (Measurement Acceptance)
Bỏ các phát biểu ước lượng chủ quan như "tự ép xuống -20dB". Hiệu quả của sidechain compression phụ thuộc trực tiếp vào mức tín hiệu đầu vào của giọng đọc. Tiêu chí chấp nhận được định lượng bằng công cụ đo kiểm FFmpeg:
- **Đo chênh lệch mức nền (Ducking Delta):**
  Sử dụng bộ lọc `astats` hoặc `ebur128`:
  ```bash
  ffmpeg -i final.mp4 -af "ebur128=framelog=verbose" -f null -
  ```
- **Tiêu chuẩn nghiệm thu:**
  1. Tại các đoạn có giọng đọc: Mức BGM phải thấp hơn giọng đọc tối thiểu `10 dB đến 14 dB` (đảm bảo giọng đọc nổi rõ trên nền nhạc, không bị lấn át).
  2. Tại các đoạn ngắt nghỉ (> 1.0 giây) hoặc điểm chuyển cảnh: BGM tự động phục hồi về mức âm lượng cơ sở trong vòng `600ms` (`release=600`).
  3. Chuẩn âm lượng tổng thể đạt mức chuẩn YouTube: Tích phân âm lượng `I = -14 LUFS (±1 LUFS)`, True Peak `TP <= -1.5 dBFS`.
- **Yêu cầu môi trường:** FFmpeg phiên bản $\ge 4.3$ (hệ thống hiện tại là FFmpeg 9.0.2, hoàn toàn đáp ứng).

#### 3.4.5. Quản lý tài nguyên BGM & Giấy phép
1. **Đường dẫn BGM thực tế:**
   `workshops/workshop-whiteboard/assets/audio/bgm/` (đã có tệp mẫu `healing-piano.mp3`).
2. **Quy định lưu trữ:**
   - Không commit các tệp âm thanh MP3/WAV dung lượng lớn trực tiếp vào Git repository.
   - Bổ sung script PowerShell `scripts/download-bgm.ps1` (tương tự như pattern `download-sfx.ts` trong `workshop-news`) để tải các bài nhạc nền bản quyền mở (Royalty-free) từ CDN hoặc GitHub Releases khi khởi tạo môi trường.
3. **Minh bạch bản quyền:**
   Tạo tệp `workshops/workshop-whiteboard/assets/audio/bgm/LICENSES.md` ghi rõ tên bản nhạc, tác giả, đường link gốc và loại giấy phép bản quyền (Creative Commons CC0, CC-BY 4.0 hoặc YouTube Audio Library License) để bảo vệ kênh YouTube của người dùng khỏi vi phạm Content ID.

---

## 4. Xử Lý Các Trường Hợp Ngoại Lệ (Edge Cases & Resilience)

1. **Dấu hai chấm nằm giữa câu thoại (Colon in narrative text):**
   - *Ví dụ:* `"Hắn nghiến răng: Các ngươi nhớ lấy: nợ máu phải trả bằng máu!"`
   - *Xử lý:* Bộ lọc chỉ phân tích tiền tố ở đầu chuỗi (`^prefix:`). Dấu hai chấm thứ hai nằm trong thân câu không khớp với quy tắc đầu dòng nên được bảo tồn nguyên vẹn làm nội dung thoại.
2. **Mốc thời gian và chữ số đầu câu (Time & Numeric colons):**
   - *Ví dụ:* `"10:30 đêm hôm đó, lò đan bốc hỏa."`
   - *Xử lý:* Quy tắc loại trừ số sẽ phát hiện chuỗi chứa ký tự số và bỏ qua, không cắt bỏ `"10"` và không gán sai speaker.
3. **Beat không có `speaker` và không có tiền tố vai:**
   - *Xử lý:* Tự động fallback về vai `narrator` với cấu hình giọng mặc định (`NamMinhNeural`, rate `+25%`).
4. **Không tìm thấy tệp BGM hoặc người dùng tắt BGM (`--bgm off`):**
   - *Xử lý:* Kiểm tra bằng Python `Path.exists()`. Nếu không có BGM, pipeline bỏ qua bộ lọc ducking và chỉ áp dụng `loudnorm` trực tiếp trên track giọng đọc, đảm bảo 100% không bị crash pipeline.
5. **Ký tự đặc biệt trong đường dẫn Windows:**
   - *Xử lý:* Khi truyền đường dẫn tệp vào filter complex của FFmpeg trên Windows, chuẩn hóa toàn bộ dấu gạch chéo ngược `\` thành gạch chéo xuôi `/`, và escape dấu hai chấm ổ đĩa (ví dụ `C\:/...`) để tránh lỗi phân tích cú pháp của FFmpeg.

---

## 5. Kế Hoạch Kiểm Thử (Verification & Testing)

### 5.1. Unit Tests

1. **Test Cache Hash Key với Pitch & Volume:**
   - *Vị trí:* `core/tts/__tests__/cache.test.ts` (mới).
   - *Mục tiêu:* Kiểm tra hàm `computeAudioHash(req, text)`:
     - Đổi `pitch` từ `+0Hz` sang `-6Hz` ➡️ Hash bắt buộc phải thay đổi.
     - Đổi `volume` từ `+0%` sang `-10%` ➡️ Hash bắt buộc phải thay đổi.

2. **Test Tái Hiện Lỗi Đọc Tên Vai & Test Bộ Lọc Dialogue Sanitizer:**
   - *Vị trí:* `workshops/workshop-whiteboard/tests/test_speaker_parser.py` (mới).
   - *Test 1 (Tái hiện lỗi cũ):* Nạp câu `"Người Kể Chuyện: Trời mưa to."` vào hàm cũ và xác nhận lỗi trả về chứa cả `"Người Kể Chuyện:"`.
   - *Test 2 (Bộ lọc mới):* Kiểm tra toàn bộ 7 ca kiểm thử trong Bảng Kiểm Thử Đúng/Sai ở Mục 3.2.2. Đảm bảo 100% tên vai được bóc tách và chuỗi text đưa sang TTS hoàn toàn sạch sẽ.

3. **Test Cấu Hình Audio Mixer & BGM Filter:**
   - *Vị trí:* `workshops/workshop-whiteboard/tests/test_audio_mixer.py` (cập nhật).
   - *Mục tiêu:* Kiểm tra chuỗi `build_ducking_filter_complex()`:
     - Phải chứa `normalize=0`.
     - Phải chứa `sidechaincompress`.
     - Phải chứa `loudnorm`.

### 5.2. Integration Test (Kiểm thử tích hợp đầu cuối)

- Chạy lệnh xuất video thử nghiệm trên một job mẫu gồm 2 phân cảnh (`scene-01`, `scene-02`):
  ```bash
  python workshops/workshop-whiteboard/scripts/export_video.py --job job-phe-dan-nghich-thien-sample
  ```
- **Tiêu chuẩn nghiệm thu tích hợp:**
  1. Dùng `ffprobe` xác nhận video đầu ra `final.mp4` có stream audio AAC 2 kênh, thời lượng khớp với tổng thời lượng các phân cảnh.
  2. BGM chạy xuyên suốt từ đầu đến cuối video, không bị reset ngắt quãng tại điểm nối giữa `scene-01` và `scene-02`.
  3. Nghe thực tế: Tuyệt đối không còn tiếng đọc *"Người kể chuyện:"* hay *"Lâm Mặc:"*; giọng đọc nhịp nhanh 1.25x rõ ràng; nhạc nền tự động chìm xuống êm dịu khi có tiếng nói và bùng lên ở điểm chuyển cảnh.
  4. Đo kiểm `ebur128`: Âm lượng tích phân nằm trong khoảng `-14.0 ± 1.0 LUFS`.

---

## 6. Thứ Tự Triển Khai (Dependency-ordered Implementation Plan)

Các hạng mục phải được thực thi tuần tự theo đúng chuỗi phụ thuộc kỹ thuật:

1. **Bước 1: Sửa Cache Key TTS & Viết Unit Test**
   - Sửa `computeAudioHash` trong [`core/tts/index.ts`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/tts/index.ts) để băm đủ `pitch` và `volume`.
   - Viết và chạy unit test trong `core/tts/__tests__/cache.test.ts`.
2. **Bước 2: Viết Test Tái Hiện Lỗi Đọc Tên Vai**
   - Viết file test `workshops/workshop-whiteboard/tests/test_speaker_parser.py` tái hiện chính xác lỗi đọc to tên vai của code hiện tại.
3. **Bước 3: Cài Đặt Dialogue Sanitizer & Tái Cấu Trúc `job_adapter.py`**
   - Cài đặt hàm `sanitize_dialogue_text()` theo quy tắc ngữ nghĩa chặt chẽ.
   - Sửa nhánh `explicit_speaker` (dòng 456) và nhánh `parse_dialogue_segments` (dòng 182-220) trong `job_adapter.py` để loại bỏ việc chèn `p0 + ":"`.
   - Chạy test xác nhận test chuyển sang màu xanh (Green).
4. **Bước 4: Cập Nhật Role-based Voice Presets & Rate +25%**
   - Cập nhật hàm `resolve_speaker_voice()` trong `job_adapter.py` loại bỏ hard-code tên truyện cũ, thay bằng bảng ánh xạ vai trò kịch bản.
   - Đặt `default_rate = "+25%"` cho archetype `storytelling`.
   - Cập nhật [`core/schema/job.ts`](file:///C:/Users/tranh/Documents/Duy/VideoAI/core/schema/job.ts) bổ sung trường `speaker` vào `VideoBeatSchema`.
5. **Bước 5: Chuyển Trộn BGM Sang Một Lần Sau Khi Ghép Nối**
   - Trong `export_video.py`: Bỏ trộn BGM khỏi `render_scene()`.
   - Thêm hàm `apply_final_bgm_and_mastering()` sau khối `merge_scenes()`: áp dụng sidechain ducking, `normalize=0`, fade-out 2s và `loudnorm`.
   - Cập nhật [`tests/test_audio_mixer.py`](file:///C:/Users/tranh/Documents/Duy/VideoAI/workshops/workshop-whiteboard/tests/test_audio_mixer.py).
6. **Bước 6: Tạo Thư Mục `prompts/` & Soạn Thảo `MASTER_STORY_PROMPT.md`**
   - Tạo thư mục `prompts/` và tạo tệp `MASTER_STORY_PROMPT.md` chứa prompt 4 tầng và schema JSON mẫu.
   - Tạo tệp `workshops/workshop-whiteboard/assets/audio/bgm/LICENSES.md`.

---

## 7. Ngoài Phạm Vi (Out of Scope)

Để đảm bảo tính tinh gọn, ổn định và tập trung vào mục tiêu cốt lõi, các hạng mục sau **KHÔNG** nằm trong phạm vi của đợt nâng cấp này:
- Tích hợp các dịch vụ Voice AI thương mại trả phí (ElevenLabs, Vbee, OpenAI Audio API, v.v.). Hệ thống tiếp tục cam kết chạy 100% Local First qua Edge-TTS miễn phí.
- Tự động nhận diện nhịp thở / cắt khoảng lặng âm thanh bằng các mô hình AI nhận dạng tiếng nói (như Whisper VAD).
- Xây dựng giao diện kéo thả timeline âm thanh trực quan nhiều track trên Web Dashboard (toàn bộ cấu hình BGM vẫn điều khiển qua CLI flags và Job JSON).

---

## 8. Các Quyết Định Mở Cần Xin Ý Kiến (Open Decisions)

Kính đề nghị Tech Lead / User xem xét và đưa ra quyết định cho 3 vấn đề sau trước khi chuyển sang bước viết Implementation Plan:

1. **Vị trí chuẩn hóa của trường `speaker` trong Beat:**
   - *Lựa chọn A (Khuyến nghị):* Cho phép đặt `speaker` ở root của beat: `beat.speaker` (rất tự nhiên khi viết prompt và khớp với `job_adapter.py:454`), đồng thời bổ sung `speaker: z.string().optional()` vào `VideoBeatSchema`.
   - *Lựa chọn B:* Bắt buộc đặt bên trong object voice: `beat.voice.speaker` theo đúng định nghĩa ban đầu của `core/schema/job.ts:25`.
2. **Nguồn cung cấp BGM Tiên Hiệp mặc định:**
   - *Lựa chọn A (Khuyến nghị):* Viết script PowerShell `scripts/download-bgm.ps1` để tự động tải 2–3 bài nhạc nền Tiên hiệp/Huyền huyễn cổ phong chất lượng cao (Royalty-free) về thư mục assets.
   - *Lựa chọn B:* Sử dụng hàm tự sinh sóng âm Ambient `generate_default_ambient_bgm()` bằng NumPy đã có sẵn trong `audio_mixer.py`.
3. **Mức âm lượng đích cho YouTube Mastering:**
   - *Lựa chọn A (Khuyến nghị):* Cố định chuẩn hóa âm lượng theo tiêu chuẩn công nghiệp của YouTube (`-14 LUFS`, `LRA=11`, `TP=-1.5 dBFS`) cho tất cả video xuất ra từ xưởng Whiteboard.
   - *Lựa chọn B:* Giữ nguyên âm lượng gốc và cho phép cấu hình tham số loudness tùy biến trong trường `output` của job kịch bản.

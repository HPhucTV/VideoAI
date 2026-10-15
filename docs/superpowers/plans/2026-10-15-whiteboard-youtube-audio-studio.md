# Kế Hoạch Triển Khai: Nâng Cấp Xưởng 3 Thành Xưởng YouTube Truyện Audio Chuyên Nghiệp

- **Ngày lập:** 15/10/2026
- **Tài liệu đặc tả:** [`docs/superpowers/specs/2026-10-15-whiteboard-youtube-audio-studio-design.md`](file:///c:/Users/tranh/Documents/Duy/VideoAI/docs/superpowers/specs/2026-10-15-whiteboard-youtube-audio-studio-design.md)
- **Mục tiêu:** Triển khai 3 trụ cột nâng cấp:
  1. Hệ thống phân vai đa giọng đọc (Multi-Speaker TTS) & Nhạc nền tự động hạ âm lượng (BGM Ducking).
  2. Phụ đề nghệ thuật (Burn-in Subtitles) phong cách giấy kem mực đen.
  3. Đóng gói YouTube Metadata tự động (YouTube Chapters, Title & SEO Description).

---

## Danh Sách Công Việc (Tasks)

### Task 1: Module Phân Vai Đa Nhân Vật & Giọng Đọc Đa Tầng (`job_adapter.py`)
- [ ] Tạo file test `workshops/workshop-whiteboard/tests/test_speaker_parser.py`.
- [ ] Cài đặt hàm `parse_dialogue_segments(text: str)` trong `job_adapter.py` để tách các đoạn dẫn chuyện và lời thoại nhân vật (`Hạ Vi:`, `Đình Phong:`, `Kiên:`, v.v.).
- [ ] Cài đặt hàm `resolve_speaker_voice(speaker_name: str, job_meta: dict) -> dict` trả về `voice`, `pitch`, `rate`.
- [ ] Cập nhật `synthesize_beat_speech()` để gọi TTS theo từng phân đoạn và ghép nối mượt mà với khoảng lặng thoại.
- [ ] Viết unit tests kiểm thử phân tách lời thoại và gán giọng đọc.

### Task 2: Nhạc Nền BGM & Cơ Chế Audio Ducking Tự Động
- [ ] Chuẩn bị tệp nhạc nền BGM lofi/piano không lời êm dịu tại `workshops/workshop-whiteboard/assets/audio/bgm/healing-piano.mp3`.
- [ ] Viết module `workshops/workshop-whiteboard/scripts/audio_mixer.py`:
  - Hàm `mix_voice_and_bgm(voice_path, bgm_path, output_path, ducking_speech_vol=0.15, pause_vol=0.30, total_duration_sec=None)`.
  - Sử dụng bộ lọc FFmpeg `sidechaincompress` hoặc `amix` kết hợp volume automation.
- [ ] Tích hợp vào `render_scene()` trong `export_video.py` để mux BGM cùng giọng đọc.
- [ ] Viết unit tests kiểm tra lệnh trộn âm thanh và ducking.

### Task 3: Hiển Thị Phụ Đề Nghệ Thuật Khắc Trực Tiếp Lên Video (`export_video.py`)
- [ ] Thêm tham số `--with-subtitles` (mặc định: `True`) vào `export_video.py`.
- [ ] Cấu hình style phụ đề FFmpeg `subtitles` hoặc `ass`:
  - Màu chữ bút mực đen xám `&H002C2C2C`.
  - Nền mờ nhẹ bảo vệ khả năng đọc chữ trên tranh vẽ.
  - Canh lề dưới $45\text{px}$.
- [ ] Cập nhật pipeline render video để burn phụ đề vào MP4 phân cảnh.
- [ ] Viết test kiểm tra cú pháp FFmpeg subtitle filter.

### Task 4: Tự Động Xuất YouTube Metadata & Chapters (`export_metadata.py`)
- [ ] Tạo module `workshops/workshop-whiteboard/scripts/export_metadata.py`:
  - Tính toán mốc thời gian lũy kế (`00:00`, `02:01`, `04:30`...) từ độ dài thực tế của từng phân cảnh.
  - Tự động sinh `YOUTUBE_METADATA.md` với:
    - 3 Gợi ý tiêu đề CTR cao.
    - Phần mô tả chứa YouTube Timestamps click-to-jump.
    - Hashtags & Tags SEO tối ưu thuật toán tìm kiếm YouTube.
- [ ] Tích hợp gọi `export_metadata.py` ở bước cuối của `export_video.py`.
- [ ] Viết test kiểm thử định dạng và độ chính xác của timestamps.

### Task 5: Kiểm Thử Toàn Diện & Render Thử Nghiệm Kịch Bản Mẫu
- [ ] Chạy toàn bộ test suite: `pytest` và `vitest`.
- [ ] Chạy thử nghiệm xuất kịch bản *"Bản Hợp Đồng Lúc 0 Giờ"* có đầy đủ:
  - Giọng nam nữ phân vai.
  - Nhạc nền piano êm dịu có ducking.
  - Phụ đề chạy mượt ở đáy video.
  - File `YOUTUBE_METADATA.md` sẵn sàng đăng YouTube.
- [ ] Commit, merge vào `master` và đẩy lên GitHub.

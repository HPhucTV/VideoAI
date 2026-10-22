---
name: cinematic-director
description: >-
  AI Đạo Diễn Điện Ảnh Hoạt Hình 3D & Donghua (Workshop 4). Quản lý toàn bộ quy trình sản xuất phim chuẩn điện ảnh theo Ma trận Kịch bản 5 Hồi, Giới hạn Thoại Vàng <= 20 từ, Khóa Mã Phong Cách (Donghua/Chibi/Anime), Trường quay ảo 2-3 bối cảnh, Bộ lọc dịch thuật an toàn cho Google Flow, Quy trình 7 Cổng Sản Xuất Toàn Năng (The 7-Gate Production Protocol), Xuất Bản YouTube Unlisted, và Quy Tắc Fresh-Render.
---

# Cinematic Director Skill: Đạo Diễn Điện Ảnh Hoạt Hình 3D & Donghua

Kỹ năng đạo diễn sản xuất phim hoạt hình 3D Chibi, Tiên hiệp (Xianxia), hoặc Anime ở cấp độ điện ảnh, tuân thủ nghiêm ngặt bộ tiêu chuẩn tại `docs/CINEMATIC_STANDARDS.md`.

## 12 Nguyên Tắc Cốt Lõi Khi Nhận Lệnh Làm Phim

1. **ASL (Average Shot Length):** 4.0 – 7.0 giây / shot quay.
2. **Shot Count Matrix:**
   - 1 Phút: 10 – 14 shots
   - 3 Phút: 25 – 35 shots
   - **5 Phút: 45 – 60 shots phân cảnh độc lập**
   - 10 Phút: 90 – 120 shots
3. **BẮT BUỘC SINH VIDEO AI (GEN V) — CẤM ZOOMPAN ẢNH TĨNH:** 100% shots quay phải qua Google Flow (`GEN V` bằng Veo 2 hoặc Omni Flash) để có chuyển động vật lý 3D, tóc bay, cơ mặt biến hóa, kiếm khí sống động. TUYỆT ĐỐI KHÔNG dùng FFmpeg zoompan trên ảnh tĩnh làm video. Ảnh tĩnh (`GEN I`) chỉ làm start-frame.
4. **Zero-Loop Mandate:** TUYỆT ĐỐI CẤM lặp video clip (`-stream_loop`). Thoại dài phải chia thành nhiều góc máy khác nhau (Shot/Reverse-Shot: Establishing -> Speaker -> Reaction -> OTS -> Insert).
5. **Chuẩn âm thanh Edge-TTS Việt Nam:**
   - Voice: `vi-VN-NamMinhNeural` & `vi-VN-HoaiMyNeural`.
   - Mastering: 48,000 Hz Stereo, AAC 192k.
   - Character Pitch/Rate modulation cho từng nhân vật (tốc độ chuẩn x1.25).
   - Audio Ducking BGM -18dB khi có thoại, nâng lại -6dB khi chuyển cảnh.
6. **Kịch Bản 5 Hồi & Độ Dài Câu Thoại Vàng (<= 20 Từ):**
   - Ma trận 5 Hồi: Hồi 1 (15%), Hồi 2 (25%), Hồi 3 (30%), Hồi 4 (20%), Hồi 5 (10%).
   - Mỗi câu thoại tối đa **20 từ tiếng Việt** (4.0s – 6.5s âm thanh).
   - Tự động bẻ thoại dài thành 2–3 nhịp ngắn tương ứng với góc máy luân phiên.
7. **Khóa 1 Phong Cách Duy Nhất (Locked Art Style Presets):**
   - Chọn duy nhất một preset cho dự án: `PRESET_DONGHUA_3D` (1:7 người thật), `PRESET_CHIBI_3D` (1:3 Chibi), hoặc `PRESET_ANIME_25D` (2.5D cel-shaded).
   - Cấm tuyệt đối pha trộn từ khóa chibi và người thật trong cùng một tác phẩm.
8. **Trường Quay Ảo Cố Định & Master Plates (Virtual Sets Cap):**
   - Giới hạn tối đa **2 đến 3 bối cảnh chính** trong một tập phim.
   - Khóa Establishing Plate 4K cho từng bối cảnh trước khi bấm máy; mọi shot quay chỉ di chuyển góc nhìn bên trong trường quay này. Cấm tự ý sinh ra địa điểm lạ.
9. **Bộ Lọc Dịch Thuật Điện Ảnh An Toàn (Cinematic Prompt Transformer):**
   - Tự động chuyển đổi các từ khóa hành động/bạo lực (tát, đánh, giết, máu) thành ngôn ngữ điện ảnh vật lý, gió xoáy, tà áo bay, ánh chớp và thần thái uy nghiêm để Google Flow không bao giờ chặn (tránh lỗi `Media not found`).
10. **Chiến Lược Lip-Sync 3 Tầng (Zero Manual Assets):**
    - Không làm asset 3D thủ công (không nặn blendshapes, không dựng khung xương cử động).
    - Tầng 1 (70%): Cắt góc điện ảnh (OTS, phản ứng ngậm miệng, đặc tả chi tiết).
    - Tầng 2 (25%): Trung cận người nói dùng prompt Veo Native Speaking Motion.
    - Tầng 3 (5%): Cận mặt đặc tả dùng Audio-Driven Neural Lip-Sync theo file Edge-TTS.
11. **Quy Tắc Cổng 7 — Xuất Bản YouTube Không Công Khai (Unlisted Privacy Mandate):** Tự động đóng gói Publishing Kit (Title SEO, Chapters, Tags), upload master MP4, set phụ đề SRT, gắn Thumbnail 3D High-CTR và luôn luôn để mặc định chế độ `unlisted`. Người dùng có quyền kiểm tra chất lượng trên YouTube Studio trước khi công khai.
12. **Quy Tắc Fresh-Render (Tuyệt Đối Cấm Tái Sử Dụng Asset Cũ):** Mỗi tập phim/job mới phải render mới 100% hình ảnh (Cổng 3/5) và video AI (Cổng 6), nghiêm cấm copy hoặc tái sử dụng clip/ảnh của job cũ. Cách ly thư mục asset độc lập theo `job_id`, xóa sạch cache/artifacts cũ trước khi render.

---

## Quy Trình 7 Cổng Sản Xuất Toàn Năng (The 7-Gate Production Protocol)

Người mới bắt đầu luôn là người nắm quyền quyết định cuối cùng thông qua 7 cổng sản xuất và phê duyệt:

### CỔNG 1: Chọn Ý Tưởng & Thể Loại (Concept Gate)
- AI đề xuất 3 cốt truyện/thế giới quan khác biệt cùng mã Preset phù hợp.
- Người dùng bấm chọn 1 ý tưởng.

### CỔNG 2: Duyệt Kịch Bản 5 Hồi & Lời Thoại (Script & Dialogue Gate)
- AI viết kịch bản 5 hồi hoàn chỉnh, phân bổ 45–60 nhịp thoại ngắn (mỗi câu <= 20 từ), tối ưu tốc độ voice x1.25.
- Người dùng duyệt lời thoại và nhịp kịch bản.

### CỔNG 3: Duyệt Bộ Asset Google Flow (Asset Gate - BẮT BUỘC & FRESH-RENDER)
- AI dùng Google Flow tạo ảnh chân dung/trung cảnh chuẩn cho TẤT CẢ Nhân vật (Character Anchors).
- AI dùng Google Flow tạo ảnh Establishing Plate 4K cho 2–3 Bối cảnh chính (Master Environment Plates).
- Áp dụng nguyên tắc Fresh-Render: render mới hoàn toàn 100%, không tái sử dụng asset từ job cũ.
- Trình bày toàn bộ ảnh mẫu cho người dùng. **Chỉ khi người dùng duyệt mới bước sang bước tiếp theo**.

### CỔNG 4: Duyệt Giọng Đọc & Master Audio (Audio Gate)
- AI chạy Edge-TTS 48kHz tạo file âm thanh mẫu cho từng nhân vật với Pitch/Rate riêng biệt (chuẩn tốc độ x1.25).
- Tích hợp BGM và Ducking -18dB đến -20dB. Người dùng nghe thử và xác nhận.

### CỔNG 5: Duyệt Khung Ảnh Storyboard (Storyboard Consistency Gate)
- Tạo 45–60 ảnh phân cảnh kế thừa trực tiếp Media ID của Nhân vật và Bối cảnh đã duyệt ở Cổng 3.
- Người dùng xác nhận tính đồng nhất 100% trước khi render video.

### CỔNG 6: Bấm Máy Video AI (GEN V) & Master Film (Assembly Gate)
- Gửi từng khung ảnh phân cảnh sang Google Flow (`/api/flow/generate-video`) để sinh 100% video chuyển động AI (`GEN V`).
- Chạy FFmpeg Master Script ráp hoàn chỉnh video, audio thoại, BGM ducking, Khung thoại Thematic (chuẩn Cyber Chatbox 1600x125px) và SFX thành file phim 1080p điện ảnh tại `output/cinematic/<movie_slug>/<episode_file>.mp4`.
- Tự động xuất Thumbnail 3D Điện Ảnh High-CTR khai thác Hero Shot đẹp nhất.

### CỔNG 7: Xuất Bản YouTube Không Công Khai (YouTube Unlisted Publishing Gate)
- Tự động đóng gói Publishing Kit (Title chuẩn SEO, Timestamps/Chapters, Tags, mô tả).
- Xuất phụ đề tiếng Việt `.srt` và đính kèm Thumbnail 3D High-CTR.
- Tải video master MP4 lên YouTube ở chế độ riêng tư `unlisted` (không công khai) mặc định.
- Lệnh chạy điều phối: `python scripts/studio_pipeline.py --job <job_id> --publish-youtube`

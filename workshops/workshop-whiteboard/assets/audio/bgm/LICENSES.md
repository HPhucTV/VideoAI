# Giấy Phép & Bản Quyền Nhạc Nền (BGM Licenses & Usage Policy)

Tài liệu này xác nhận tính pháp lý, bản quyền và hướng dẫn sử dụng các bản nhạc nền (Background Music - BGM) đi kèm trong hệ thống OmniVideo Whiteboard Studio.

---

## 1. Danh Mục Nhạc Nền Mặc Định (Default BGM Catalogue)

Toàn bộ các bản nhạc được tích hợp sẵn đều thuộc diện **Miễn phí bản quyền (Royalty-Free)** hoặc **Phạm vi công cộng (CC0 Public Domain)**, đảm bảo **100% an toàn để kiếm tiền trên YouTube, TikTok, Facebook** mà không bị khiếu nại bản quyền (Copyright Strike hoặc Content ID Claim).

| Tên File | Phong Cách & Cảm Xúc | Tác Giả / Nguồn | Giấy Phép | Trạng Thái YouTube Content ID |
| :--- | :--- | :--- | :--- | :--- |
| `healing-piano.mp3` | Nhẹ nhàng, hoài niệm, tâm sự | OmniVideo Studio (NumPy procedural ambient) | **CC0 1.0 Universal** (Public Domain) | **Safe** (Không có Content ID) |
| `xianxia-ambient.mp3` | Cổ phong tiên hiệp, ngũ cung huyền ảo | OmniVideo Studio Procedural / Royalty-Free | **CC0 / Royalty-Free** | **Safe** (Không có Content ID) |
| `battle-epic.mp3` | Chiến đấu dồn dập, trống trận kịch tính | OmniVideo Studio Procedural / Royalty-Free | **CC0 / Royalty-Free** | **Safe** (Không có Content ID) |

### Chi tiết từng bản nhạc:

### 1.1. `healing-piano.mp3`
- **Mô tả:** Bản nhạc piano lofi thư thái, sử dụng vòng hòa thanh 4 hợp âm êm dịu `Cmaj7 - Am9 - Fmaj7 - Gsus4`.
- **Tác giả:** OmniVideo Studio (Tạo tự động bằng mô hình tổng hợp âm thanh thủ tục procedural qua NumPy và FFmpeg).
- **Giấy phép:** [Creative Commons CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/deed.vi) (Toàn quyền sử dụng thương mại, không bắt buộc ghi công).
- **Phù hợp cho:** Các phân đoạn độc thoại nội tâm, hồi tưởng quá khứ, giải thích triết lý, không gian phòng kín yên tĩnh.

### 1.2. `xianxia-ambient.mp3`
- **Mô tả:** Âm hưởng cổ phong tiên hiệp, âm giai ngũ cung (Pentatonic) thanh tịnh mô phỏng tiếng đàn tranh Guzheng, tiêu trúc và tiếng chuông xa xăm.
- **Tác giả / Nguồn:** OmniVideo Studio Procedural Audio Synthesis / Open Royalty-Free Assets.
- **Giấy phép:** Creative Commons CC0 / Royalty-Free Commercial License.
- **Phù hợp cho:** Cảnh tu luyện đan dược, khám phá tiên môn, đối ẩm thưởng trà, đàm đạo võ học, dạo cảnh bồng lai.

### 1.3. `battle-epic.mp3`
- **Mô tả:** Nhịp điệu chiến đấu dồn dập 120-130 BPM, kết hợp trống trận taiko dồn dập, âm trầm (sub-bass) rung chuyển và bè kèn đồng (brass) kịch tính trên gam Rê thứ (D minor).
- **Tác giả / Nguồn:** OmniVideo Studio Procedural Audio Synthesis / Open Royalty-Free Assets.
- **Giấy phép:** Creative Commons CC0 / Royalty-Free Commercial License.
- **Phù hợp cho:** Các cảnh giao đấu sinh tử, đọ kiếm, thi đấu lôi đài, độ kiếp thiên lôi, phá vỡ phong ấn ma vương.

---

## 2. Hướng Dẫn Thêm Nhạc Nền Riêng (Custom BGM Guide)

Người dùng có thể tự do bổ sung các bản nhạc nền riêng phù hợp với nội dung truyện của mình:

### 2.1. Yêu Cầu Định Dạng & Thông Số Kỹ Thuật
- **Định dạng:** `.mp3`, `.wav`, hoặc `.m4a`.
- **Tần số lấy mẫu (Sample Rate):** 44.1 kHz hoặc 48.0 kHz.
- **Kênh âm thanh (Channels):** Stereo (2 kênh).
- **Bitrate đề xuất:** Tối thiểu 192 kbps (đối với MP3) hoặc 16-bit PCM (đối với WAV).

### 2.2. Vị Trí Lưu Trữ & Cách Sử Dụng
1. **Lưu trữ cục bộ:** Đặt tệp nhạc của bạn vào thư mục:
   ```
   workshops/workshop-whiteboard/assets/audio/bgm/ten-nhac-cua-ban.mp3
   ```
2. **Khai báo khi render video CLI:**
   ```bash
   python workshops/workshop-whiteboard/scripts/export_video.py \
       --job-dir "workshops/workshop-whiteboard/assets/whiteboard/tam-cam" \
       --bgm "workshops/workshop-whiteboard/assets/audio/bgm/ten-nhac-cua-ban.mp3" \
       --bgm-vol 0.30 \
       --duck-ratio 6.0
   ```
3. **Cơ chế hòa âm tự động của OmniVideo:**
   - **Tự động lặp (Stream Loop):** Nhạc nền sẽ tự động lặp vô hạn theo đúng độ dài video成片 mà không bị ngắt giữa chừng.
   - **Audio Ducking:** Hệ thống tự động nén nhỏ âm lượng BGM xuống ~12-15% mỗi khi có nhân vật cất tiếng nói và nâng âm lượng lên ~30-35% khi có khoảng nghỉ hoặc tiếng lau bảng.
   - **YouTube Loudnorm Mastering:** Âm lượng tổng thể sau khi ghép nối được chuẩn hóa chuẩn YouTube `-14.0 LUFS` với đoạn chuyển mượt mà `afade` 2 giây cuối video.

---

## 3. Cảnh Báo Bản Quyền & YouTube Content ID

Khi xuất bản video lên YouTube hoặc các nền tảng mạng xã hội khác để kiếm tiền, xin lưu ý các quy định quan trọng sau:

### 3.1. Tuyệt Đối Không Sử Dụng
- **Nhạc Pop, V-Pop, K-Pop thương mại:** Các bài hát đang thịnh hành hoặc của các nghệ sĩ nổi tiếng đều đã đăng ký YouTube Content ID độc quyền.
- **Nhạc phim Anime / Phim truyền hình / Game bản quyền:** Dễ bị chặn hiển thị trên toàn cầu (Worldwide Block) hoặc chuyển doanh thu quảng cáo cho chủ sở hữu bản quyền.
- **Nhạc có chèn Watermark âm thanh:** Nhạc demo tải lậu từ các trang bán âm thanh (AudioJungle, Pond5) có chứa tiếng "AudioJungle" lặp lại.

### 3.2. Các Nguồn Nhạc Miễn Phí An Toàn Khuyên Dùng
Nếu muốn tìm thêm nhạc phong phú hơn cho kênh truyện:
1. **YouTube Audio Library (Thư viện âm thanh YouTube Studio):**
   - Truy cập: [studio.youtube.com](https://studio.youtube.com) -> *Thư viện âm thanh*.
   - **Ưu điểm:** 100% không bao giờ bị Content ID claim trên YouTube. Có thể lọc theo thể loại *Cinematic*, *Dramatic*, hoặc *Ambient*.
2. **Free Music Archive (FMA):**
   - Bộ lọc giấy phép: Chọn `Public Domain` hoặc `CC0`.
3. **Incompetech (Kevin MacLeod):**
   - Kho nhạc nền kinh điển cho YouTube. Lưu ý: Cần sao chép đoạn ghi công (Attribution) dán vào phần Mô tả (Description) của video.
4. **Musopen:**
   - Cung cấp nhạc giao hưởng cổ điển (Beethoven, Mozart, Bach) đã hết hạn bản quyền, được thu âm mới và phát hành công cộng.

### 3.3. Quy Trình Xử Lý Khi Bị Content ID Nhầm Lẫn (False Claim Dispute)
Nếu bạn sử dụng 3 bản nhạc có sẵn trong repo (`healing-piano.mp3`, `xianxia-ambient.mp3`, `battle-epic.mp3`) mà bị bất kỳ bên thứ ba nào gắn cờ Content ID:
1. Chọn nút **"Kháng nghị" (Dispute)** trên YouTube Studio.
2. Chọn lý do: **"Nội dung thuộc phạm vi công cộng hoặc có giấy phép hợp lệ"**.
3. Dẫn link tài liệu này hoặc ghi rõ:
   > *"Bản nhạc nền là sản phẩm âm thanh thủ tục (procedural synthesis) thuộc dự án mã nguồn mở OmniVideo Studio, phát hành theo giấy phép Creative Commons CC0 Public Domain. Tệp âm thanh không thuộc sở hữu của bất kỳ bên thứ ba nào."*
4. Khiếu nại sẽ được gỡ bỏ trong vòng 24 - 48 giờ.

# 🎬 CẨM NANG CHI TIẾT 3 XƯỞNG SẢN XUẤT (WORKSHOPS SPECIFICATION)
# NGUỒN SỰ THẬT DUY NHẤT (SINGLE SOURCE OF TRUTH) CHO TEMPLATE, BEATS & SAFE ZONES

> **Lưu ý:** Tài liệu này là nguồn dữ liệu chuẩn mực nhất về mặt nội dung kịch bản, quy tắc đồ họa, nhịp điệu tâm lý và âm thanh cho toàn bộ hệ thống OmniVideo Studio. Mọi tài liệu khác (`ARCHITECTURE.md`, `ROADMAP.md`) đều dẫn chiếu về tài liệu này.

---

## 1. BẢNG TIÊU CHÍ LỰA CHỌN PHÂN XƯỞNG

| Tiêu chí | 🏭 Xưởng 1: Tin Tức & Đồ Họa Nhanh | 🏭 Xưởng 2: Giải Thích & Video-as-Code | 🏭 Xưởng 3: Vẽ Tay Bảng Trắng |
| :--- | :--- | :--- | :--- |
| **Công nghệ lõi** | HyperFrames (HTML/CSS + GSAP) | Remotion 4.0 (React 19 + Tailwind v4) | Python 3.12 (OpenCV + PyAV + Pillow) |
| **Tốc độ khung hình**| **30 FPS chuẩn** (60fps tùy chọn) | **30 FPS chuẩn** | **30 FPS chuẩn** |
| **Thời lượng tối ưu**| 45 – 65 giây | 50 – 75 giây (Shorts) hoặc 3 – 8 phút (YouTube) | 60 – 90 giây (Shorts) hoặc 3 – 15 phút (YouTube) |
| **Nền tảng tối ưu** | TikTok, YouTube Shorts, Reels | TikTok/Shorts & YouTube Tech Deep Dive | YouTube Chính & TikTok Triết Lý / Bài Học |
| **Tỉ lệ khung hình** | 9:16 Dọc (1080x1920) | 9:16 Dọc (1080x1920) hoặc 16:9 (1920x1080) | 16:9 Ngang (1920x1080) hoặc 9:16 (1080x1920) |
| **Nội dung phù hợp** | Tin tức công nghệ, review GitHub repo, so sánh sản phẩm, tin giật gân | Bài giảng công nghệ, giải thích khái niệm (Docker, Redis, AI, System Design) | Kể chuyện nhân văn, đạo lý sống, tóm tắt sách, bài giảng khoa học / lịch sử |
| **Giao diện xem thử**| Xem MP4 hoặc file HTML local | **Remotion Studio Web UI** (Tua frame live) | **Whiteboard Region Editor** (Kéo box live) |

---

## 2. NGÂN SÁCH NHỊP TÂM LÝ THEO TỈ LỆ % (BEAT RATIO BUDGET)

Thay vì cố định cứng nhắc số giây (khiến kịch bản dài/ngắn bị vỡ khung), hệ thống phân bổ thời lượng theo **Tỉ lệ phần trăm ngân sách nhịp**:

```
[Hook: 8-10%] ──► [Pain/Context: 15-20%] ──► [Core Solution: 20-25%] ──► [Workflow: 25-30%] ──► [Benefits: 15-18%] ──► [Outro: 7-10%]
```

| Nhịp (Beat) | Vai trò tâm lý (Narrative Role) | Tỉ lệ % ngân sách | Mục tiêu hình ảnh & Kỹ thuật |
| :--- | :--- | :---: | :--- |
| **Beat 1: Hook** | Gây chú ý tức thì, ngăn người xem lướt đi | **8% – 10%** | Tiêu đề lớn 8xl, câu hỏi kích thích tò mò, hiệu ứng âm thanh whoosh mạnh mẽ. |
| **Beat 2: Pain Point** | Nêu bối cảnh khó khăn, nỗi đau thực tế | **15% – 20%** | Biểu tượng cảnh báo, so sánh "Cách cũ tốn công vs Cách mới", tạo sự đồng cảm. |
| **Beat 3: Solution** | Giới thiệu giải pháp hoặc khái niệm cốt lõi | **20% – 25%** | Thẻ kính (Glassmorphism), mô hình hộp 3D, từ khóa quan trọng phát sáng. |
| **Beat 4: Workflow** | Giải thích quy trình vận hành chi tiết | **25% – 30%** | Sơ đồ luồng 3 bước chuyển động mượt mà hoặc nét vẽ tay diễn giải từng hành động. |
| **Beat 5: Benefits** | Minh chứng tác động thực tế, lợi ích cốt lõi | **15% – 18%** | 3 số liệu ấn tượng (tiết kiệm thời gian, tăng tốc, nhẹ hơn) hoặc bài học rút ra. |
| **Beat 6: Outro & CTA** | Đúc kết thông điệp đắt giá + Kêu gọi hành động | **7% – 10%** | Huy hiệu thương hiệu kênh, lời kêu gọi Follow/Subscribe, card tương tác. |

*Ví dụ tính toán tự động:*
- Với video ngắn 60 giây: Hook = 5.5s, Pain = 10s, Solution = 14s, Workflow = 16s, Benefits = 9.5s, Outro = 5s.
- Với video YouTube 300 giây (5 phút): Hook = 25s, Pain = 50s, Solution = 70s, Workflow = 85s, Benefits = 45s, Outro = 25s.

---

## 3. DANH MỤC 6 TEMPLATE ĐỒ HỌA CHUYÊN DỤNG (XƯỞNG 1 & REMOTION MAPPING)

1. **`breaking-news` (Tin sốt dẻo):**
   - *Đặc điểm:* Banner đỏ cảnh báo nhấp nháy, ticker tin tức chạy chữ, ảnh nền phóng to nhẹ Ken Burns.
   - *SFX:* Tiếng tít tít bản tin hoặc camera shutter.
2. **`stat-callout` (Số liệu giật mình):**
   - *Đặc điểm:* Thẻ card nổi bật nhấn mạnh số liệu thống kê hoặc biểu đồ so sánh.
   - *SFX:* Tiếng "pop" hoặc "ding" thanh thoát.
3. **`split-screen` (Màn hình kép so sánh):**
   - *Đặc điểm:* Chia nửa màn hình (trên/dưới hoặc trái/phải) để so sánh 2 đối tượng hoặc ảnh tư liệu phía trên, giải thích phía dưới.
   - *SFX:* Tiếng whoosh trượt khung hình.
4. **`quote-card` (Trích dẫn chuyên gia):**
   - *Đặc điểm:* Thẻ trích dẫn với dấu ngoặc kép lớn và ảnh đại diện tròn của tác giả/nhân vật.
   - *SFX:* Tiếng typewriter (gõ phím) nhẹ nhàng.
5. **`listicle` (Danh sách điểm tin):**
   - *Đặc điểm:* Bảng danh sách 3 đến 5 mục xuất hiện tuần tự theo nhịp đọc của giọng nói.
   - *SFX:* Tiếng tick đếm nhịp.
6. **`big-number` (Con số khổng lồ):**
   - *Đặc điểm:* Số đếm thống kê cực đại choáng ngợp toàn màn hình (ví dụ: `1.000.000` người dùng, `82.7%` thị phần).
   - *SFX:* Tiếng bass drop hoặc boom nhẹ tạo điểm nhấn.

---

## 4. QUY CHUẨN VÙNG AN TOÀN TRÊN MÀN HÌNH (SAFE ZONES SPECIFICATION)

### 4.1. Chuẩn Mobile Dọc 9:16 (TikTok, YouTube Shorts, Reels)
Khung canvas: **1080 × 1920 pixel @ 30fps**.
* **Đỉnh trên (Top):** Trừ hao **180px** (tránh thanh tìm kiếm, biểu tượng Live và viền camera trước điện thoại). Huy hiệu kênh đặt an toàn tại `top: 150px` đến `180px`.
* **Đáy dưới (Bottom):** Trừ hao **320px** (tránh tên tài khoản người đăng, caption mô tả và thanh đĩa nhạc quay của TikTok/Shorts). Phụ đề 1 dòng đặt tại khoảng `bottom: 350px` đến `400px`.
* **Cạnh phải (Right):** Trừ hao **140px** (tránh cột nút Tim, Bình luận, Lưu, Chia sẻ).
* **Cạnh trái (Left):** Trừ hao **60px**.
* **Quy tắc vàng:** **Toàn bộ nội dung chính, thẻ card, phụ đề BẮT BUỘC căn chính giữa (Centered Focus)** trong khung an toàn 880px chiều rộng.

### 4.2. Chuẩn Video Ngang 16:9 (YouTube Long-form)
Khung canvas: **1920 × 1080 pixel @ 30fps**.
* **Đỉnh trên & Đáy dưới:** Lề an toàn tối thiểu **60px**.
* **Cạnh trái & Cạnh phải:** Lề an toàn tối thiểu **80px**.
* Phụ đề đặt ở góc dưới giữa màn hình, cách đáy 80px, font chữ kích thước vừa phải không che lấp tranh vẽ hoặc sơ đồ.

---

## 5. BỘ QUY TẮC NGỮ ÂM TIẾNG VIỆT THEO NGỮ CẢNH (CONTEXT-AWARE PHONETICS)

> ⚠️ **Lưu ý quan trọng về TTS:** Bộ máy Microsoft Edge TTS sẽ tự động đoán nghĩa của từ nếu ta để nguyên số và ký tự. Ví dụ: Nếu gửi thô `"5.5"`, TTS có thể hiểu là "5 rưỡi" (5 giờ rưỡi, 5 rưỡi kg). Do đó, kịch bản trước khi gửi sang TTS **BẮT BUỘC phải được chuẩn hóa qua `core/phonetics`**.

### Bảng đối chiếu ngữ cảnh chuẩn hóa:

| Ngữ cảnh | Ký hiệu đầu vào | Regex nhận diện | Kết quả chuẩn hóa đưa vào TTS | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| **Dấu chấm ngăn hàng nghìn (Việt Nam)** | `1.000.000`<br>`50.000đ` | `/\b\d{1,3}(\.\d{3})+\b/` | `"một triệu"`<br>`"năm mươi nghìn đồng"` | Dấu chấm đi liền sau bởi đúng 3 chữ số là ngăn hàng nghìn. |
| **Số thập phân toán học / phần trăm** | `82.7%`<br>`3.5kg` | `/\b\d+[\.,]\d+%/` | `"tám mươi hai phẩy bảy phần trăm"`<br>`"ba phẩy năm ki-lô-gam"` | Có thể dùng `"phẩy"` hoặc `"chấm"`. |
| **Số phiên bản phần mềm** | `GPT 5.5`<br>`iOS 18.2`<br>`v2.0` | `/(?:bản\|version\|v\|gpt\|ios\|android)\s*\d+[\.,]\d+/i` | `"gí pi tí năm chấm năm"`<br>`"ai ô ét mười tám chấm hai"`<br>`"phiên bản hai chấm không"` | Đứng sau từ khóa phiên bản thì luôn đọc là `"chấm"`. |
| **Tên viết tắt công nghệ (Acronyms)** | `AI`<br>`API`<br>`UI/UX`<br>`RAM` | Từ viết tắt tiếng Anh thông dụng | `"ây ai"`<br>`"ây pi ai"`<br>`"u ai u ích"`<br>`"ram"` | Tránh việc TTS đọc nhầm thành chữ cái rời tiếng Việt. |
| **Đơn vị dung lượng / Tần số** | `500MB`<br>`10GB`<br>`5G` | `/\b\d+(?:MB\|GB\|TB\|G)\b/i` | `"năm trăm mê ga bai"`<br>`"mười ghi ga bai"`<br>`"năm gờ"` | Giúp âm thanh đọc tự nhiên, chuyên nghiệp. |
| **Dấu phép tính & Ký tự đặc biệt** | `→`, `&`, `+`, `$5` | Ký tự biểu tượng toán học | `"và"`, `"cộng"`, `"năm đô la"` | TTS thường bỏ qua hoặc đọc thô ký tự này nếu không đổi. |

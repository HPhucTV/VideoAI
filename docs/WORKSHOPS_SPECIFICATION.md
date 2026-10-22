# 🎬 CẨM NANG CHI TIẾT 5 PHÂN XƯỞNG SẢN XUẤT (WORKSHOPS SPECIFICATION)
# NGUỒN SỰ THẬT DUY NHẤT (SINGLE SOURCE OF TRUTH) CHO TEMPLATE, BEATS & SAFE ZONES

> **Lưu ý:** Tài liệu này là nguồn dữ liệu chuẩn mực nhất về mặt nội dung kịch bản, quy tắc đồ họa, nhịp điệu tâm lý, âm thanh và thông số kỹ thuật của cả 4 phân xưởng trong hệ thống OmniVideo Studio. Mọi tài liệu khác (`ARCHITECTURE.md`, `ROADMAP.md`, `USER_GUIDE.md`) đều dẫn chiếu về tài liệu này.

---

## 1. BẢNG TIÊU CHÍ LỰA CHỌN PHÂN XƯỞNG

| Tiêu chí | 🏭 Xưởng 1: Tin Tức & Đồ Họa Nhanh | 🏭 Xưởng 2: Giải Thích & Video-as-Code | 🏭 Xưởng 3: Vẽ Tay Bảng Trắng & Audio Drama | 🏭 Xưởng 4: Hoạt Hình 3D (Blender / FlowKit) | 🏭 Xưởng 5: Threads & Social Drama |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Thư mục mã nguồn** | `workshops/workshop-news` | `workshops/workshop-explainer` | `workshops/workshop-whiteboard` | `workshops/workshop-blender` *(Rebuilding via FlowKit)* | `workshops/workshop-threads` |
| **Công nghệ lõi** | HyperFrames (HTML/CSS + GSAP) | Remotion 4.0 (React 19 + Tailwind v4) | Python 3.12 (OpenCV + PyAV + Pillow + Edge-TTS) | Blender 5.2 LTS (`bpy`, EEVEE Next) & Python 3.12 | Headless Chrome Native Screenshot + Edge-TTS Slang Normalizer + FFmpeg |
| **Tốc độ khung hình**| **30 FPS chuẩn** (60fps tùy chọn) | **30 FPS chuẩn** (60fps tùy chọn) | **90 FPS chuẩn nét vẽ** (30/60fps tùy chọn) | **60 FPS chuẩn 3D** (30fps tùy chọn) | **60 FPS chuẩn gameplay** (30fps tùy chọn) |
| **Thời lượng tối ưu**| 45 – 65 giây | 50 – 75 giây (Shorts) hoặc 3 – 8 phút (YouTube) | 60 – 90 giây (Shorts) hoặc **15 – 60+ phút trọn vẹn (YouTube Audio Drama)** | **10 – 60 giây (Teaser) hoặc 3 – 10+ phút (Tập phim điện ảnh chuẩn 55–75 shots/5p, Voice x1.25, Zero-Loop)** | **15 – 45 giây (Chuẩn Shorts/Reels viral)** |
| **Nền tảng tối ưu** | TikTok, YouTube Shorts, Reels | TikTok/Shorts & YouTube Tech Deep Dive | YouTube Video Dài & TikTok Triết Lý / Sách Nói | TikTok/Shorts Điện Ảnh & YouTube Hoạt Hình 3D / Donghua Chiếu Mạng | TikTok, YouTube Shorts, Instagram Reels |
| **Tỉ lệ khung hình** | 9:16 Dọc (1080x1920) | 9:16 Dọc (1080x1920) hoặc 16:9 (1920x1080) | 16:9 Ngang (1920x1080) hoặc 9:16 (1080x1920) | 16:9 Ngang (1920x1080) chuẩn điện ảnh | 9:16 Dọc (1080x1920) chuẩn Shorts |
| **Nội dung phù hợp** | Tin tức công nghệ, review GitHub repo, so sánh sản phẩm, tin giật gân | Bài giảng công nghệ, giải thích khái niệm (Docker, Redis, AI, System Design) | Kể chuyện ngôn tình/tổng tài, triết lý sống, tóm tắt sách, truyện đêm khuya, khoa học | Phim hoạt hình 3D, Tiên hiệp/Xianxia, Donghua dài tập, đối thoại đa tầng, võ thuật kỳ ảo | Drama học đường/công sở, tình huống viral Threads, đối đáp bình luận hài hước, confession |
| **Tính năng nổi bật** | Tự động xuất caption TikTok, 6 template chuyển động | Remotion Studio xem trước frame live, công thức nhịp tâm lý | Đa phân cảnh (Multi-Scene), Xóa bảng bằng tay (Hand Eraser), BGM Ducking 6:1, YouTube Chapters tự động, Tắt phụ đề (`--no-subtitles`) | **Chuẩn điện ảnh (`CINEMATIC_STANDARDS.md`): Voice x1.25, 55–75 shot/tập 5 phút, ASL 3.5–6s, Zero-Loop, Shot/Reverse-Shot đối thoại, Edge-TTS Vietnamese 48kHz Stereo, Khung thoại Thematic (chuẩn Cyber Chatbox 1600x125px), Cấm hộp đen phụ đề cũ**, Anchor Lock đồng nhất nhân vật | **Phương pháp A2 (Avatar thật từ CDN + Dark Mode AMOLED #101010 + Lọc sạch icon rác + Phiên âm tiếng Anh tự nhiên), SFX Pop chuyển cảnh, Lo-fi Chill BGM, Nền gameplay Minecraft 60FPS** |
| **Giao diện xem thử**| Xem MP4 hoặc file HTML local | **Remotion Studio Web UI** (`npm run dev` cổng 3000) | **Whiteboard Region Editor** (`preview.html`) | Blender Viewport GUI hoặc Video Library Dashboard (cổng 3333) | Xem file MP4 hoặc preview frame JPG |

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
- Với video YouTube 300 giây (5 phút - Xưởng 2): Hook = 25s, Pain = 50s, Solution = 70s, Workflow = 85s, Benefits = 45s, Outro = 25s.
- Với video Audio Drama 3600 giây (60 phút - Xưởng 3): Chia thành 9 chương hồi (mỗi chương 3 beat = 27 beats), mỗi beat trung bình ~130 giây.
- **Với phim hoạt hình 3D / Donghua (Xưởng 4):** Áp dụng trực tiếp quy chuẩn [`docs/CINEMATIC_STANDARDS.md`](CINEMATIC_STANDARDS.md). Toàn bộ voice **luôn luôn chạy ở mức x1.25** (`rate='+25%'`). Một tập 300 giây (5 phút) **BẮT BUỘC phân rã thành 55 – 75 shots độc lập (ASL 3.5–6s)**, tập 10 phút gồm 100 – 130 shots; kịch bản đào sâu chi tiết kỹ thuật/cốt truyện mà không làm lê thê, cắt góc liên tục theo kỹ thuật Shot/Reverse-Shot đối thoại, TUYỆT ĐỐI CẤM loop video clip (`-stream_loop`).

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
Khung canvas: **1080 × 1920 pixel @ 30fps / 60fps**.
* **Đỉnh trên (Top):** Trừ hao **180px** (tránh thanh tìm kiếm, biểu tượng Live và viền camera trước điện thoại). Huy hiệu kênh đặt an toàn tại `top: 150px` đến `180px`.
* **Đáy dưới (Bottom):** Trừ hao **320px** (tránh tên tài khoản người đăng, caption mô tả và thanh đĩa nhạc quay của TikTok/Shorts). Phụ đề 1 dòng đặt tại khoảng `bottom: 350px` đến `400px`.
* **Cạnh phải (Right):** Trừ hao **140px** (tránh cột nút Tim, Bình luận, Lưu, Chia sẻ).
* **Cạnh trái (Left):** Trừ hao **60px**.
* **Quy tắc vàng:** **Toàn bộ nội dung chính, thẻ card, phụ đề BẮT BUỘC căn chính giữa (Centered Focus)** trong khung an toàn 880px chiều rộng.

### 4.2. Chuẩn Video Ngang 16:9 (YouTube Long-form)
Khung canvas: **1920 × 1080 pixel @ 30fps / 60fps / 90fps**.
* **Đỉnh trên & Đáy dưới:** Lề an toàn tối thiểu **60px**.
* **Cạnh trái & Cạnh phải:** Lề an toàn tối thiểu **80px**.
* **Phụ đề & Khung thoại (Subtitle & Thematic Dialogue Boxes):**
  - **LOẠI BỎ 100% HỘP ĐEN PHỤ ĐỀ CŨ:** Tuyệt đối cấm dùng hộp phụ đề bounding box màu đen thô (`BorderStyle=3` của FFmpeg) che khuất màn hình.
  - **Quy chuẩn kích cỡ Cyber Chatbox bất di bất dịch:** `box_w = 1600px`, `box_h = 120 – 135px`, căn giữa ngang `x = 160`, cách mép đáy `40px – 45px` (`y = 900 - 915`), bo góc `radius = 16px`. Có Speaker Pill Badge góc trên bên trái (`badge_x = box_x + 24`, `badge_y = box_y - 16`). Typography chữ trắng in đậm căn giữa, đổ bóng nhẹ.
  - **May đo theo Art Style:** Tự động điều chỉnh chất liệu khung thoại theo dòng phim (Kính mờ Cyber Neon cho Tech/Robot Chibi, Khung hoa văn cổ phong ngọc bích cho Donghua/Xianxia, Frosted Glass cho Anime 2.5D).
  - Với định dạng Audio Drama / Whiteboard YouTube nghệ thuật (Xưởng 3): Hỗ trợ cờ `--no-subtitles` để loại bỏ hoàn toàn phụ đề chữ, bảo tồn độ thanh sạch của tranh vẽ tay.

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

---

## 6. QUẢN LÝ KHO THÀNH PHẨM VÀ BẢNG ĐIỀU KHIỂN (VIDEO LIBRARY DASHBOARD)

- **Địa chỉ truy cập:** `http://localhost:3333` (kích hoạt qua lệnh `npm run dashboard` hoặc phím `[7]` trên `studio.bat`).
- **Chức năng chính:**
  - Quản lý danh mục toàn bộ video đã xuất bản từ cả 4 xưởng (`output/news/`, `output/explainer/`, `output/whiteboard/`, `output/blender/`).
  - Xem trước video trực tiếp trên trình duyệt web, hiển thị thông số dung lượng (MB), độ phân giải, thời lượng (giây) và ngày tạo.
  - Tải về tệp MP4, thumbnail hoặc sao chép metadata YouTube với 1 cú nhấp chuột.

---

## 7. QUY CHUẨN THU THẬP TƯ LIỆU THỰC TẾ & B-ROLL TỰ ĐỘNG (NO-SLIDE-DECK POLICY)

> ⚠️ **MANDATORY POLICY FOR TECH & EXPLAINER VIDEOS (XƯỞNG 1 & XƯỞNG 2):**
> Tuyệt đối không biến video công nghệ thành bản "trình chiếu slide chữ đơn điệu" (Kinetic Slide Deck). Mọi video review mã nguồn mở, giới thiệu sản phẩm, giải thích code hoặc tin tức công nghệ **BẮT BUỘC PHẢI CÓ TƯ LIỆU THỰC TẾ (B-ROLL / SCREENSHOTS)** đi kèm.

### Quy Trình 3 Bước Thu Thập B-Roll & Visual Assets Tự Động:

1. **Bước 1: Chụp ảnh giao diện Web / GitHub tự động (Headless Browser Screenshot):**
   - Khi nhận URL bài báo, landing page hoặc GitHub repository:
   - Sử dụng **Headless Browser (Puppeteer/Playwright)** ngầm truy cập link nguồn để chụp ảnh màn hình chất lượng cao:
     - **Shot 1 (Overview Plate):** Chụp vùng Header, số Stars/Forks, huy hiệu và phần giới thiệu chính (`About / Readme Header`).
     - **Shot 2 (Deep-dive Plate):** Cuộn trang xuống chụp sơ đồ kiến trúc (`Workflow diagram`), bảng so sánh hoặc khối code tiêu biểu.
   - Ảnh chụp được lưu vào thư mục `images/` hoặc `assets/` của dự án video.

2. **Bước 2: Trích xuất và Render tài liệu thực tế (Document & Code Preview):**
   - **Đối với tệp tài liệu PDF/LaTeX:** Nếu repo hoặc bài viết nhắc đến sản phẩm đầu ra (CV mẫu, bài báo, hợp đồng, báo cáo), hệ thống tự động trích xuất file PDF mẫu và render trang 1 thành ảnh PNG sắc nét (qua `pdftoppm` hoặc thư viện render PDF) để trình chiếu thực tế thay vì chỉ mô tả bằng chữ.
   - **Đối với mã nguồn và câu lệnh CLI:** Sử dụng component **Terminal Simulator** (hoặc code card có Syntax Highlighting) để hiển thị thao tác gõ từng dòng lệnh thực tế (`/setup`, `/scrape`, `/apply`) thay vì chỉ liệt kê dạng text gạch đầu dòng.

3. **Bước 3: Hiển thị qua Khung Mockup Thiết Bị (Device Mockup Layout):**
   - **CẤM** đặt ảnh tư liệu chìm xuống lớp nền tối mờ 80% khiến người xem không đọc được.
   - **BẮT BUỘC** hiển thị tư liệu bên trong khung:
     - **Browser Window Frame:** Khung cửa sổ trình duyệt (có thanh địa chỉ URL, 3 nút điều hướng đỏ/vàng/xanh).
     - **Laptop / Mobile 3D Tilt Mockup:** Khung laptop nghiêng hoặc điện thoại dựng đứng sắc nét.
     - **Tỉ lệ phân bổ màn hình (Split Focus):** Nửa trên (45–50%) hiển thị tư liệu thực tế sắc nét, nửa dưới (50–55%) hiển thị phụ đề, số liệu và phân tích điểm nhấn.

---

## 8. QUY CHUẨN XƯỞNG 5 — THREADS & SOCIAL DRAMA (NATIVE SCREENSHOT, NESTED THREAD & SMART SFX)

> ⚠️ **MANDATORY POLICY FOR WORKSHOP 5 (THREADS & SOCIAL DRAMA):**
> Sản xuất video ngắn 9:16 (Shorts/TikTok/Reels) từ các bài đăng Threads và mạng xã hội đạt chuẩn native app, tuyệt đối loại bỏ cảm giác đồ họa giả lập 3D hoặc thiếu tương tác.

### 6 Trụ Cột Kỹ Thuật Độc Quyền Xưởng 5:

1. **Chuẩn Dark Mode AMOLED (#101010):**
   - Viền mỏng `1px solid #282828`, bo góc nhẹ `18px`, chiều rộng `820px` (76% khung hình 1080px), padding `22px 24px`.
   - Typography chuẩn hệ điều hành: cỡ chữ `24px`, font-weight 400–500, khoảng cách dòng `1.45`.
   - Đầy đủ nút ba chấm `···`, logo Threads mờ, 4 icon hành động (tim, bình luận, repost, share).

2. **Avatar Thật & Media Gốc (Method A2):**
   - 100% Avatar lấy trực tiếp từ CDN Instagram (`scontent.cdninstagram.com`), cấm dùng hình tròn chữ cái đầu.
   - Ảnh đính kèm (meme/chứng từ) bảo toàn tỉ lệ aspect ratio gốc, đặt trong khung bo góc `14px`.

3. **Audio Purifier & Slang Normalizer:**
   - Dọn sạch 100% emoticon ASCII (`:)))`, `=)))`, `^^`) và emoji unicode trước khi đưa vào Edge-TTS.
   - Phiên âm chuẩn các thuật ngữ mượn tiếng Anh (`teamwork` $\rightarrow$ *"tim quớc"*, `deadline` $\rightarrow$ *"đét lai"*, `2K9` $\rightarrow$ *"hai ca chín"*, `VaCT` $\rightarrow$ *"vê át"*).
   - Văn bản hiển thị giữ nguyên 100% nguyên gốc của tác giả.

4. **Watermark Kênh Đối Xứng Tuyệt Đối (0.0px Offset):**
   - Logo tròn kênh (`shared-assets/branding/hanshin_avatar.png`) đặt trên đỉnh (`y ≈ 130px`) căn giữa tuyệt đối, viền trắng mỏng sắc nét.

5. **Cây Hội Thoại Phân Nhánh (Nested Thread View) & Spring Pop:**
   - Khi hiển thị bình luận, bài viết chính xuất hiện thu nhỏ ở trên kết nối qua **đường kẻ dọc xám (Thread Connector Line)** chạy thẳng xuống avatar người bình luận.
   - Hiệu ứng nảy thẻ lò xo vật lý (`Spring Pop-in Physics` qua FFmpeg overlay: `y = center + 35*exp(-14*t)*cos(18*t)`), micro-shake khi có cảm thán mạnh.

6. **Phụ Đề Dynamic Karaoke Highlight & Bộ SFX Biểu Cảm:**
   - Phụ đề chạy chữ tự động tô sáng màu Vàng chanh / Cyan neon theo từng từ giọng đọc lướt qua ở góc dưới.
   - Bộ âm thanh biểu cảm: *Vine Boom* (giật gân, sốc), *Huh?* (thắc mắc, khó hiểu), *Whoosh* (than thở, buồn bã), *Ding* (bí quyết, sáng suốt), và *Pop* (chuyển cảnh tiêu chuẩn).


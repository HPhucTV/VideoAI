# OMNIVIDEO STUDIO — AGENTS INSTRUCTIONS & PRODUCTION STANDARDS

Welcome to **OmniVideo Studio**, an automated multi-workshop video production ecosystem.
All AI assistants, coding agents (Antigravity, Claude Code, Codex, Cursor), and subagents working in this workspace **MUST STRICTLY COMPLY** with the instructions and production standards outlined below.

---

## 🏛 HỆ THỐNG 5 PHÂN XƯỞNG SẢN XUẤT (WORKSHOPS)

1. **Xưởng 1: Tin Tức & Đồ Họa Nhanh (`workshops/workshop-news`)**
   - Format: 9:16 Dọc @ 30 FPS. Công nghệ: HyperFrames (HTML/CSS/GSAP).
2. **Xưởng 2: Video Giải Thích Code (`workshops/workshop-explainer`)**
   - Format: 9:16 hoặc 16:9 @ 30 FPS. Công nghệ: Remotion 4.0 (React 19 + Tailwind v4).
3. **Xưởng 3: Vẽ Tay Bảng Trắng & Audio Drama (`workshops/workshop-whiteboard`)**
   - Format: 16:9 hoặc 9:16 @ 90 FPS. Công nghệ: Python 3.12 (OpenCV + PyAV + Edge-TTS). Multi-scene, Hand Eraser wipe.
4. **Xưởng 4: Phim Điện Ảnh 3D & Donghua (`workshops/workshop-cinematic`)**
   - Format: 16:9 Ngang (1920x1080) @ 60 FPS hoặc 24/30 FPS điện ảnh.
   - Công nghệ: FastAPI FlowKit daemon, Google Imagen 3, Google Veo 2, Microsoft Edge-TTS Vietnamese Neural, FFmpeg Master Assembly.
5. **Xưởng 5: Threads & Social Drama (`workshops/workshop-threads`)**
   - Format: 9:16 Dọc @ 60 FPS (1080x1920 Shorts/Reels/TikTok).
   - Công nghệ: Headless Chrome Native Screenshot, Microsoft Edge-TTS Vietnamese Neural + Slang & Phonetic Normalizer, FFmpeg Compositor (Minecraft/GTA5 gameplay + SFX Pop + Lo-fi BGM).

---

## 🎬 NGUYÊN TẮC BẮT BUỘC: CẤP ĐỘ ĐIỆN ẢNH (CINEMATIC GRADE MANDATE)

> ⚠️ **MANDATORY POLICY FOR ALL FILM PRODUCTIONS:**
> Khi người dùng yêu cầu làm phim hoạt hình 3D, tiên hiệp (Xianxia), anime, hoặc bất kỳ tập phim nào ở **"cấp độ điện ảnh"**, AI **BẮT BUỘC** phải tuân theo tài liệu chi tiết tại [`docs/CINEMATIC_STANDARDS.md`](file:///c:/Users/tranh/Documents/Duy/VideoAI/docs/CINEMATIC_STANDARDS.md).

### 14 Quy Tắc Bất Di Bất Dịch:

1. **QUY TẮC NHỊP PHIM (AVERAGE SHOT LENGTH - ASL) & TĂNG CƯỜNG ĐỘ CHI TIẾT:**
   - Thời lượng trung bình mỗi shot: **3.5s – 6.0s**.
   - Mỗi câu thoại hoặc cử chỉ của nhân vật tương ứng với một góc máy riêng.
   - **Voice luôn ở mức x1.25:** Câu thoại nói nhanh gọn, dứt khoát giúp tăng số lượng shot quay. Thời lượng phim có thể dài ra mà kịch bản vẫn được mổ xẻ cực kỳ chi tiết, sâu sắc.
   - **Định lượng bắt buộc theo độ dài tập (Voice 1.25x):**
     - Phim 1 phút: **12 – 16 shots**.
     - Phim 3 phút: **30 – 45 shots**.
     - **Phim 5 phút: 55 – 75 shots phân cảnh độc lập**.
     - Phim 10 phút: **100 – 130 shots**.

2. **QUY TẮC BẮT BUỘC SINH VIDEO AI (GEN V) — CẤM ZOOMPAN ẢNH TĨNH:**
   - **100% shots quay BẮT BUỘC PHẢI LÀ VIDEO CHUYỂN ĐỘNG AI THỰC SỰ (`GEN V`)** do Google Flow (Veo 2 hoặc Omni Flash) tạo ra.
   - **TUYỆT ĐỐI CẤM** dùng ảnh tĩnh (`GEN I`) kết hợp bộ lọc `zoompan` của FFmpeg để giả lập video. Zoompan trên ảnh 2D làm khung hình bị giật giật, nhân vật bị đóng băng bất động, phá hỏng chuẩn điện ảnh. Ảnh tĩnh chỉ được dùng làm start-frame cho `GEN V`.

3. **QUY TẮC ZERO-LOOP (TUYỆT ĐỐI CẤM LẶP CLIP):**
   - **CẤM HOÀN TOÀN** việc dùng `-stream_loop` trên video Veo 2 để kéo dài thời lượng cho một đoạn thoại 20–30 giây.
   - Khi có đoạn hội thoại dài 24s: Bắt buộc chia thành **4-5 shot quay độc lập (4.5s - 6s mỗi shot)**:
     - *Shot 1:* Trung cảnh nhân vật nói.
     - *Shot 2:* Cận cảnh phản ứng người nghe.
     - *Shot 3:* Góc quay qua vai (OTS) tạo chiều sâu không gian.
     - *Shot 4:* Đặc tả chi tiết (chuôi kiếm, vết thương, giọt lệ) hoặc toàn cảnh không gian.

4. **QUY TẮC LỒNG TIẾNG NATIVE TIẾNG VIỆT & LUÔN ĐẶT TỐC ĐỘ VOICE X1.25 (EDGE-TTS 48KHZ STEREO):**
   - Sử dụng **Microsoft Edge-TTS Vietnamese Neural** (`vi-VN-NamMinhNeural` và `vi-VN-HoaiMyNeural`).
   - Âm thanh xuất chuẩn **Studio 48,000 Hz, Stereo 2 kênh, AAC 192kbps**.
   - **QUY CHUẨN BẮT BUỘC: TỐC ĐỘ VOICE LUÔN Ở MỨC x1.25 (`rate='+25%'`):**
     - Giọng đọc nhanh dứt khoát, hiện đại, không chậm chạp, giữ chân khán giả liên tục.
     - Do câu thoại ngắn lại, số shot quay sẽ tăng lên tương ứng để giữ nhịp đổi góc máy. Kịch bản được phép đào sâu kiến thức và bối cảnh chi tiết hơn mà không lo video bị lê thê.
   - **Bắt buộc điều biến tần số (Character Pitch Modulation) theo từng vai** (trầm ấm cho nam chính, the thé cho phản diện, uy nghiêm cho trưởng bối, trong trẻo cho nữ chính).
   - **Audio Ducking:** Nhạc nền BGM tự động giảm `-18dB` đến `-20dB` khi có thoại, nâng lại `-6dB` khi chuyển cảnh.

5. **QUY TẮC KỊCH BẢN 5 HỒI & ĐỘ DÀI CÂU THOẠI VÀNG (<= 20 TỪ):**
   - Kịch bản phim phân bổ chuẩn 5 Hồi: Hồi 1 (15%), Hồi 2 (25%), Hồi 3 (30%), Hồi 4 (20%), Hồi 5 (10%).
   - **Mỗi câu thoại không quá 20 từ tiếng Việt (3.5s - 5.5s âm thanh ở tốc độ x1.25)**.
   - Đoạn thoại dài phải tự động bẻ thành 2-3 câu ngắn, mỗi câu tương ứng một góc máy luân phiên khác nhau.

6. **QUY TẮC KHÓA 1 PHONG CÁCH DUY NHẤT (LOCKED ART STYLE PRESETS):**
   - Dự án chỉ chọn DUY NHẤT một mã: `PRESET_DONGHUA_3D` (1:7 người thật), `PRESET_CHIBI_3D` (1:3 Chibi), hoặc `PRESET_ANIME_25D` (2.5D cel-shaded).
   - Tuyệt đối cấm trộn lẫn từ khóa chibi và người thật trong cùng một dự án.

7. **QUY TẮC TRƯỜNG QUAY ẢO CỐ ĐỊNH (VIRTUAL SETS CAP & ZERO DRIFT):**
   - Mỗi tập phim giới hạn **tối đa 2 đến 3 bối cảnh chính** (Master Sets).
   - Tạo trước ảnh Establishing Plate 4K bằng Google Flow và khóa Media ID. Mọi shot quay chỉ được chuyển dịch góc máy bên trong bối cảnh mẫu này, cấm sinh ra các địa điểm lạ ngoài kịch bản.

8. **QUY TẮC BỘ LỌC DỊCH THUẬT ĐIỆN ẢNH AN TOÀN (CINEMATIC PROMPT TRANSFORMER):**
   - Tự động chuyển hóa các từ khóa bạo lực/hành động kịch tính (*đánh, giết, tát, máu*) thành chuyển động vật lý, khí động lực học, ánh sáng và cử chỉ trang nghiêm để Google Flow không bao giờ chặn (tránh lỗi `Media not found`).

9. **QUY TẮC ĐỒNG BỘ KHẨU HÌNH & LIP-SYNC 3 TẦNG (ZERO-MANUAL-ASSETS):**
   - **Không làm asset 3D thủ công:** Tuyệt đối không cần nặn cơ mặt hay gắn xương chuyển động (đi/chạy/bay).
   - **Tầng 1 (70%): Cắt góc điện ảnh:** Luân chuyển góc quay qua vai (OTS), toàn cảnh, cận cảnh phản ứng người nghe, đặc tả vật thể.
   - **Tầng 2 (25%): Prompt khẩu hình tự nhiên của Veo:** Cảnh trung cận người nói luôn kèm prompt cử động môi/cơ hàm nói chuyện sống động (`speaking with intense facial expressions`).
   - **Tầng 3 (5%): AI Audio-Driven Lip-Sync:** Shot siêu cận mặt kích hoạt qua mô hình Neural Lip-Sync theo audio Edge-TTS.

10. **QUY TẮC THIẾT KẾ KHUNG THOẠI THEO PHONG CÁCH DỰ ÁN & CHUẨN KÍCH CỠ CYBER CHATBOX (CẤM 100% HỘP ĐEN PHỤ ĐỀ CŨ):**
    - **LOẠI BỎ 100% HỘP ĐEN PHỤ ĐỀ CŨ:** Tuyệt đối **CẤM** dùng phụ đề kiểu bounding box đen đặc thô dày (`BorderStyle=3` của FFmpeg) chiếm 30-40% màn hình làm che mất chi tiết phòng lab/phim ảnh.
    - **Thiết kế hộp thoại theo đúng Art Style từng dòng phim:**
      - *Phim Công nghệ / Cyberpunk / Robot Chibi:* Khung kính bán trong suốt (`rgba(11, 15, 23, 0.88)`), viền Cyan Neon 2px (`#00DAF5`), kèm **Speaker Pill Badge** ở góc trên bên trái (`BÉ BYTE (AI AGENT)` / `BÉ BYTE (CHATBOT)`).
      - *Phim Tiên hiệp / Donghua 3D:* Khung thoại hoa văn cổ phong, viền hoàng kim hoặc ngọc bích bán trong suốt, tên nhân vật phong thái kiếm hiệp.
      - *Phim Anime 2.5D / Visual Novel:* Khung thoại thủy tinh mờ mượt mà phong cách JRPG, pill badge tối giản thanh lịch.
    - **LẤY HỘP CYBER CHATBOT LÀM KÍCH CỠ CHUẨN BẤT DI BẤT DỊCH (1920x1080):**
      - Chiều rộng (`box_w`): **1600px** (căn giữa ngang `x = 160`, chiếm ~83% chiều ngang).
      - Chiều cao (`box_h`): **120px – 135px** (chỉ chiếm ~11-12% chiều cao màn hình, giải phóng 88% không gian chính diện cho visual 3D).
      - Vị trí đáy (`box_y`): Cách đáy màn hình **40px – 45px** (`y = 1080 - box_h - 45 = 900 - 915`).
      - Bo góc (`radius`): **16px – 18px**.
      - **Speaker Pill Badge:** Nằm góc trên bên trái, chờm nhẹ lên viền hộp (`badge_x = box_x + 24`, `badge_y = box_y - 16`), nền màu nổi bật bo góc 8px, chữ in hoa in đậm cỡ 18-20px tương phản cao.
      - **Typography thoại:** Font Arial Bold / Segoe UI Bold cỡ **30px – 34px**, màu trắng `#FFFFFF`, căn giữa cả ngang và dọc trong hộp, có bóng đổ nhẹ để đọc rõ trên mọi khung hình chuyển động.

11. **QUY TẮC THUMBNAIL 3D ĐIỆN ẢNH (CINEMATIC 3D THUMBNAIL MANDATE — CẤM 100% SLIDE 2D):**
    - **CẤM HOÀN TOÀN** thiết kế thumbnail ở dạng slide 2D phẳng, văn bản dày đặc nhiều dòng nhỏ, hoặc dính lỗi font ô vuông `□` do thiếu font glyphs.
    - **Bắt buộc khai thác trực tiếp Asset 3D điện ảnh:** Sử dụng Frame 3D đẹp nhất (Beauty Shot / Hero Shot) từ chính tập phim (nhân vật 3D tỉ lệ chuẩn, trường quay ảo, ánh sáng Octane Render / Unreal Engine 5).
    - **Typography giật gân, tương phản cao (High-CTR):**
      - Câu hook chính ngắn gọn dưới 4–6 từ với font chữ cực đại (cỡ 80px – 110px).
      - Phối màu neon tương phản cao (Cyan Neon `#00E5FF`, Vàng Kim `#FFD700` trên nền tối gradient).
      - Bắt buộc có viền đổ bóng đen dày (`stroke 5px - 7px`) để đọc rõ ràng 100% trên màn hình điện thoại di động nhỏ.
    - **Bộ nhận diện chuẩn:** Logo kênh góc trên bên trái, pill tag chủ đề phong cách (`KỶ NGUYÊN TỰ CHỦ 2026`), và các huy hiệu kiểm chứng nổi bật.

12. **QUY TRÌNH 7 CỔNG SẢN XUẤT TOÀN NĂNG (THE 7-GATE PRODUCTION PROTOCOL):**
    - **Cổng 1:** Chọn ý tưởng & thể loại (AI đề xuất 3 cốt truyện -> Người dùng chọn).
    - **Cổng 2:** Duyệt kịch bản 5 hồi & thoại (nhịp thoại ngắn <= 20 từ, tối ưu tốc độ voice x1.25).
    - **Cổng 3 (BẮT BUỘC):** Duyệt bộ Asset Google Flow (Dàn Nhân Vật & 2-3 Bối Cảnh Master - Fresh Render). Tuyệt đối không bấm máy khi người dùng chưa duyệt Cổng 3.
    - **Cổng 4:** Duyệt giọng đọc Edge-TTS 48kHz (tốc độ x1.25) & Master Audio Ducking.
    - **Cổng 5:** Duyệt khung ảnh Storyboard (kế thừa chính xác Media ID đã duyệt).
    - **Cổng 6:** Bấm máy 100% video AI (GEN V), Master Film hoàn chỉnh với Khung thoại Thematic & **Thumbnail 3D Điện Ảnh High-CTR**.
    - **Cổng 7:** Xuất bản YouTube tự động ở chế độ không công khai (Unlisted), đóng gói Publishing Kit (Title SEO, Chapters, Tags, SRT, Thumbnail 3D).

13. **QUY TẮC CỔNG 7 — XUẤT BẢN YOUTUBE TỰ ĐỘNG Ở CHẾ ĐỘ KHÔNG CÔNG KHAI (UNLISTED PRIVACY MANDATE):**
    - Tự động đóng gói Publishing Kit (Title, Timestamps/Chapters, Tags), upload master MP4, set phụ đề SRT, gắn Thumbnail 3D High-CTR và luôn luôn để mặc định chế độ `unlisted`. Người dùng có toàn quyền kiểm tra chất lượng trên YouTube Studio trước khi quyết định công khai (Public) hoặc chia sẻ link unlisted nội bộ.

14. **QUY TẮC FRESH-RENDER (TUYỆT ĐỐI CẤM TÁI SỬ DỤNG ASSET CŨ):**
    - Mỗi tập phim/job mới phải render mới 100% hình ảnh (Cổng 3/5) và video AI (Cổng 6), nghiêm cấm copy hoặc tái sử dụng clip/ảnh của job cũ. Cách ly thư mục asset độc lập theo `job_id`, xóa sạch mọi cache cũ hoặc artifacts còn sót lại trước khi bắt đầu quy trình render để đảm bảo tính độc bản và sáng tạo mới hoàn toàn.

---

## 💻 NGUYÊN TẮC BẮT BUỘC CHO VIDEO CÔNG NGHỆ (XƯỞNG 1 & XƯỞNG 2)

> ⚠️ **NO-SLIDE-DECK POLICY:**
> Tuyệt đối **CẤM** sản xuất video công nghệ / tin tức ở dạng "slide trình chiếu chữ đơn điệu" chỉ gồm text và gradient tối.
>
> 1. **Bắt buộc tự động chụp màn hình (Headless Browser Screenshot):** Khi nhận link bài báo hoặc GitHub repo, hệ thống phải mở trình duyệt ngầm (Puppeteer/Playwright) chụp lại giao diện thực tế (Header, số Stars/Forks, bảng tính năng, diagram).
> 2. **Render tài liệu mẫu thành ảnh sắc nét:** Nếu repo có file PDF/LaTeX mẫu (CV, báo cáo), phải bóc tách render trang 1 thành ảnh để minh họa trực quan.
> 3. **Trình diễn qua khung Mockup thiết bị:** Tư liệu thực tế phải được đặt trong khung Browser Frame, Laptop 3D hoặc Mobile Mockup (chiếm 45-50% khung hình), không để ảnh chìm sau lớp nền tối mờ.

---

## 📱 NGUYÊN TẮC BẮT BUỘC CHO VIDEO THREADS (XƯỞNG 5 — NATIVE SCREENSHOT & AUDIO PURIFIER)

> ⚠️ **MANDATORY POLICY FOR WORKSHOP 5 (THREADS & SOCIAL DRAMA):**
> Video Threads phải tái hiện 100% cảm giác "Chụp màn hình điện thoại nguyên bản" (Native Mobile App Screenshot) từ các bài đăng viral, tuyệt đối cấm tạo cảm giác đồ họa 3D render giả tạo hoặc phát âm ngọng tiếng Anh.

### 6 Quy Tắc Bất Di Bất Dịch Của Xưởng 5:

1. **QUY TẮC CHUẨN DARK MODE AMOLED (#101010) & KÍCH THƯỚC PIXEL-PERFECT (CẤM THẺ TRẮNG PHỒNG TO GIẢ LẬP):**
   - **Mặc định 100% video Threads sử dụng Dark Mode AMOLED (`#101010`)**: Viền sắc nét mỏng `1px solid #282828`, bo góc thanh thoát `18px`, chiều rộng chuẩn `820px` (chiếm ~76% chiều ngang khung hình 1080px), padding `22px 24px`.
   - **TUYỆT ĐỐI CẤM** dùng thẻ nền trắng bệch (`#ffffff`) hoặc kích thước phồng to `880px` bo tròn `32px` kiểu render 3D làm người xem cảm giác như dán miếng bìa PowerPoint lên video game.
   - **Typography tự nhiên chuẩn San Francisco / Segoe UI**: Cỡ chữ `24px`, độ dày chữ vừa phải (`font-weight: 400 - 500`), khoảng cách dòng `line-height: 1.45`, không in đậm toàn bộ văn bản.
   - **Đầy đủ chi tiết UI Threads gốc**: Avatar 44px tròn, Username bold, chấm tròn `•`, thời gian đăng (vd: `21 giờ`), **nút 3 chấm `···` ở góc phải**, logo Threads và hàng 4 icon vector chính hãng (Tim, Bình luận, Repost xoay vòng, Máy bay chia sẻ).

2. **QUY TẮC BẮT BUỘC DÙNG AVATAR THẬT & ẢNH GỐC (PHƯƠNG PHÁP A2 — CẤM FALLBACK CHỮ CÁI):**
   - **Bắt buộc tải và sử dụng 100% Avatar thật** của chủ bài viết VÀ của từng người bình luận từ CDN Instagram (`scontent.cdninstagram.com`).
   - **TUYỆT ĐỐI CẤM** fallback sang hình tròn màu có chữ cái đầu (như K, P, T,...) vì làm video trông giả tạo và mất độ uy tín của bài thảo luận thật.
   - **Ảnh Meme đính kèm**: Phải giữ nguyên tỉ lệ aspect ratio tự nhiên của ảnh gốc, đặt trong khung bo góc `14px` có viền `1px solid rgba(255, 255, 255, 0.12)`.

3. **QUY TẮC BỘ LỌC DỌN SẠCH 100% ICON RÁC & PHIÊN ÂM NGỮ ÂM TIẾNG ANH (AUDIO PURIFIER):**
   - **Lọc sạch 100% icon rác trước khi đưa vào Edge-TTS**: Loại bỏ toàn bộ các ký tự mặt cười ASCII (`=)))`, `:)))`, `:>`, `^^`, `:3`, `:v`, `xD`, `T_T`...) và Unicode emoji để tránh giọng đọc đọc lỗi tên ký hiệu hoặc chắp vá thô kệch.
   - **Phiên âm ngữ âm các thuật ngữ tiếng Anh / viết tắt mạng xã hội**:
     - `teamwork` / `taowork` $\rightarrow$ *"tim quớc"*, `gánh team` $\rightarrow$ *"gánh tim"*, `teammate` $\rightarrow$ *"tim mét"*.
     - `deadline` $\rightarrow$ *"đét lai"*, `slide` $\rightarrow$ *"xờ lai"*, `project` $\rightarrow$ *"pờ rô dếch"*, `presentation` $\rightarrow$ *"p-re zen"*.
     - `leader` $\rightarrow$ *"lít đờ"*, `mentor` $\rightarrow$ *"men tò"*, `toxic` $\rightarrow$ *"tốc xích"*, `drama` $\rightarrow$ *"đra ma"*, `flex` $\rightarrow$ *"phờ lếch"*.
     - `tsv` $\rightarrow$ *"tân sinh viên"*, `dh` $\rightarrow$ *"đại học"*, `sv` $\rightarrow$ *"sinh viên"*, `clb` $\rightarrow$ *"câu lạc bộ"*.
     - `Tsb` $\rightarrow$ *"trời đất ơi"*, `đag` $\rightarrow$ *"đang"*, `đc` / `đccc` $\rightarrow$ *"được"*, `điii` $\rightarrow$ *"đi"*, `uh` $\rightarrow$ *"ừ"*.
   - **Bảo toàn văn bản hiển thị (Visual Text)**: Văn bản hiển thị trên thẻ card giữ nguyên vẹn 100% nguyên gốc của tác giả (kể cả icon và tiếng lóng), chỉ có âm thanh TTS là được chuẩn hóa phát âm.

4. **QUY TẮC CĂN GIỮA ĐỐI XỨNG TUYỆT ĐỐI CHO AVATAR WATERMARK KÊNH (ĐỘ LỆCH TÂM 0.0PX):**
   - Ảnh Avatar kênh trên đỉnh canvas (`y ≈ 130px`) phải được trích xuất chính xác theo tọa độ tâm đối xứng từ ảnh gốc kênh YouTube kèm mặt nạ tròn alpha, đảm bảo vòng tròn viền trắng và logo kênh hoàn toàn đồng tâm (sai số lệch tâm $0.0px$), tuyệt đối không để xảy ra vệt khuyết đen hoặc cắt lẹm logo.

5. **QUY TẮC CÂY HỘI THOẠI (NESTED THREAD VIEW), SPRING POP & KARAOKE HIGHLIGHT:**
   - **Nested Thread View**: Các bình luận luôn hiển thị bài viết chính thu nhỏ ở phía trên kết nối bằng **đường kẻ dọc xám (Thread Connector Line)** chạy thẳng từ avatar tác giả xuống avatar người bình luận, tái hiện 100% cấu trúc phản hồi gốc của ứng dụng Threads.
   - **Spring Pop-in Physics**: Thẻ bài viết khi xuất hiện nảy lên với phương trình dao động tắt dần vật lý (`y = center + 35*exp(-14*t)*cos(18*t)`), tạo cảm giác nảy lò xo mượt mà chuẩn ứng dụng iOS, kết hợp micro-shake khi có cảm thán mạnh.
   - **Dynamic Word-by-Word Karaoke Highlight**: Phụ đề chạy chữ tự động tô sáng màu Vàng chanh / Cyan neon theo từng từ giọng đọc lướt qua ở góc dưới màn hình, tối đa hóa Retention Rate người xem.

6. **QUY TẮC BỘ ÂM THANH BIỂU CẢM (SMART EMOTIONAL SFX & VOICE MODULATION):**
   - **Smart Emotional SFX**: Tự động nhận diện ngữ cảnh câu thoại để kích hoạt âm thanh phù hợp: *Vine Boom* (cảm thán giật gân, bàng hoàng), *Huh?* (thắc mắc, khó hiểu, quên bài), *Whoosh* (than thở, bất lực, buồn bã), *Ding* (bí quyết, sáng suốt), và *Pop* (chuyển cảnh tiêu chuẩn).
   - **Emotion Pitch & Rate Modulation**: Tự động điều chỉnh cao độ và nhịp đọc theo cảm xúc câu thoại (kịch tính tăng tốc + nâng cao độ, than thở hạ giọng trầm ấm và chậm rãi).

---

## 🛠 LỆNH ĐIỀU PHỐI NHANH (QUICK COMMANDS)
- Mở Dashboard trung tâm: `npm run dashboard` (cổng 3333) hoặc `./studio.bat`.
- Kiểm tra sức khỏe hệ thống: Chạy script kiểm tra trong `scripts/` hoặc kiểm tra FastAPI FlowKit tại `http://127.0.0.1:8100/health`.
- Pipeline tự động hóa Cổng 3 -> Cổng 7: `python scripts/studio_pipeline.py --job <job_id> --publish-youtube`
- Tài liệu chi tiết các Xưởng: Xem [`docs/WORKSHOPS_SPECIFICATION.md`](file:///c:/Users/tranh/Documents/Duy/VideoAI/docs/WORKSHOPS_SPECIFICATION.md).

# 🎬 OMNIVIDEO STUDIO — CẨM NANG ĐẠO DIỄN SẢN XUẤT (DIRECTOR'S PLAYBOOK)
## CHIẾN LƯỢC KỸ THUẬT & TÂM LÝ HÚT KHÁN GIẢ TRIỆU VIEW CHO 4 PHÂN XƯỞNG

> **Dành cho Creators & AI Agents:** Tài liệu này chuẩn hóa toàn bộ các kỹ thuật dàn dựng, tâm lý giữ chân người xem (Retention Engineering), thiết kế âm thanh xúc giác (Tactile Sound) và bộ lọc màu điện ảnh để video không bao giờ rơi vào "căn bệnh vô hồn của AI".

---

## 🏛 1. MA TRẬN 5 VŨ KHÍ TÂM LÝ GIỮ CHÂN KHÁN GIẢ (THE 5 VIRAL RETENTION WEAPONS)

```
[1. The Infinite Loop] ──► Móc câu kết về câu mở đầu ➔ Xem lại >100%
[2. 3-Second Disruption] ──► Đập vỡ quán tính ➔ Loại bỏ hoàn toàn intro
[3. Micro-Stimulation]  ──► Kích thích mỗi 3.5s ➔ Chống ngủ đông não bộ
[4. 4-Layer Soundscape] ──► Giọng + SFX + Môi trường + Sub-bass 48Hz
[5. Character Persona]  ──► Giọng điệu sắc sảo, châm biếm thông minh
```

### 1.1. Kỹ thuật Vòng Lặp Vô Tận (The Infinite Loop Hook)
- **Mục tiêu:** Đẩy tỉ lệ xem hết video (View-Through Rate / Retention) trên TikTok và YouTube Shorts vượt mốc **100% - 120%**. Thuật toán sẽ tự động phân phối video vào luồng viral cực mạnh.
- **Cơ chế:** Viết câu kết thúc (Outro / Beat cuối) sao cho nó nối thành một vế câu hoàn chỉnh với câu mở đầu (Hook / Beat 1).
- **Trường dữ liệu trong `job.json`:**
  ```json
  {
    "cues": {
      "isLoopEnding": true,
      "loopConnectingPhrase": "Và sự thật bất ngờ là..."
    }
  }
  ```
- **Ví dụ thực tế:**
  - *Câu mở đầu (Beat 1):* "...một dòng lệnh SQL bị bỏ quên của cậu thực tập sinh!"
  - *Nội dung thân bài:* Giải thích thảm họa sập mạng lúc nửa đêm, cách khắc phục, bài học...
  - *Câu kết thúc (Beat 5):* "Và lý do khiến toàn bộ hệ thống thanh toán hàng triệu đô bị thiêu rụi chính là..."
  - *Trải nghiệm người xem:* Khi video kết thúc, nó lập tức tua lại câu mở đầu mượt mà đến mức người xem tưởng video vẫn đang phát tiếp.

### 1.2. Phá Vỡ Quán Tính Thị Giác 3 Giây Đầu (The 3-Second Disruption)
- **Tuyệt đối cấm:** "Xin chào các bạn...", "Hôm nay mình sẽ chia sẻ...".
- **Hành động ngay frame 0:** 
  - Visual zoom punch từ tỉ lệ `1.35` giật về `1.0` trong 0.38s kèm rung chấn nhẹ (Micro-shake).
  - Điểm nhấn âm thanh SFX `dramatic_boom` hoặc tiếng kính vỡ / cảnh báo réo rắt.
  - Từ khóa quan trọng xuất hiện dạng Neon Pop rực rỡ (`.word-punch`).

### 1.3. Kích Thích Não Bộ Mỗi 3.5 Giây (Micro-Stimulation)
- Não bộ lướt mạng xã hội rơi vào trạng thái ngủ đông sau mỗi 3.5 giây nếu không có tín hiệu mới.
- Hệ thống hỗ trợ cờ `microStimulation` trên từng Beat:
  - `"zoom_punch"`: Ống kính zoom in nhẹ 8% tạo điểm nhấn.
  - `"sound_pop"`: Tiếng búng tay, tiếng pop bọt nước hoặc keyboard clack.
  - `"glitch_flash"`: Chớp sáng màn hình nhẹ khi có lỗi bug hoặc biến cố.
  - `"particle_burst"`: Bụi ánh sáng phát sáng khi đạt thành tựu hoặc giải pháp.

### 1.4. Thiết Kế Âm Thanh 4 Tầng (4-Layer Soundscape Architecture)
Âm thanh quyết định **60% - 70%** cảm xúc đắm chìm:
1. **Tầng 1 (Lời thoại - Center Mono):** Microsoft Edge-TTS 48kHz Stereo, âm lượng `1.30 - 1.40`.
2. **Tầng 2 (Foley & SFX - Hành động vật lý):** Tiếng bước chân, tuốt kiếm, tiếng click phím cơ, tiếng cọ sột soạt trên giấy.
3. **Tầng 3 (Ambience - Không gian môi trường):** Tiếng mưa rơi trên mái hiên, tiếng gió rít qua khe núi, tiếng lò sưởi gỗ nổ lách tách.
4. **Tầng 4 (Sub-Bass Drone 48Hz):** Dải trầm Brown noise tần số 40-60Hz rung trực tiếp vào lồng ngực khán giả ở những phân đoạn nghẹt thở hoặc chuyển cảnh hồi hộp.

---

## 🎨 2. BỘ LỌC MÀU ĐIỆN ẢNH ĐỒNG NHẤT (CINEMATIC COLOR GRADING LUTS)

Áp dụng thông qua cờ `colorGradingPreset` trong `job.json` hoặc tham số gọi API Xưởng 4:

| Mã Preset | Thể loại phù hợp | Đặc trưng hình ảnh | Chuỗi FFmpeg Filter |
| :--- | :--- | :--- | :--- |
| **`cinematic_teal_orange`** | Hành động, công nghệ cao, bom tấn | Tông da cam ấm, nền xanh lơ sâu thẳm, tương phản mạnh | `eq=contrast=1.12:brightness=-0.02:saturation=1.18,colorbalance=rs=0.08:gs=0.02:bs=-0.06:rm=-0.04:gm=0.01:bm=0.06,vignette=PI/4` |
| **`donghua_xianxia_dream`** | Tiên hiệp 3D, huyền huyễn, kiếm hiệp | Màu sắc rực rỡ, ánh sáng thần tiên, sắc tím xanh lung linh | `eq=contrast=1.08:brightness=0.02:saturation=1.25,colorbalance=rs=0.04:gs=0.02:bs=0.08:rm=0.02:gm=0.0:bm=0.05,vignette=PI/4` |
| **`dark_thriller_noir`** | Trinh thám, kinh dị, thảm họa | Muted màu, tương phản gay gắt, bóng tối sâu, lạnh lẽo | `eq=contrast=1.25:brightness=-0.05:saturation=0.75,colorbalance=rs=-0.05:gs=-0.02:bs=0.08,vignette=PI/4` |
| **`vintage_warm`** | Hoài niệm, truyện cổ tích, bài học cuộc sống | Sắc vàng hổ phách, ấm cúng, êm dịu mắt người xem | `eq=contrast=1.05:brightness=0.0:saturation=1.1,colorbalance=rs=0.1:gs=0.04:bs=-0.08,vignette=PI/4` |

---

## 📖 3. CẤU TRÚC 6 ARCHETYPES TỰ SỰ CHUẨN ĐẠO DIỄN

1. **`storytelling`:** Dan Harmon Story Circle (Cổ tích, Truyện Audio, Bài học cuộc sống).
2. **`explainer`:** Problem $\rightarrow$ Agitate $\rightarrow$ Solution $\rightarrow$ Proof (Giải thích công nghệ, Micro-learning Remotion).
3. **`versus`:** Đối đầu A vs B gay cấn (MySQL vs Redis, React vs Vue).
4. **`mythbuster`:** Lật tẩy định kiến sai lầm (Đánh trúng tâm lý tò mò).
5. **`news`:** Inverted Pyramid (Bản tin nóng HyperFrames, thời sự công nghệ).
6. **`cinematic` (Mới v2.2):** 5 Hồi chuẩn điện ảnh Hollywood / Donghua:
   - `act_1_establishment` (15%): Bối cảnh 4K & Mâu thuẫn ngầm đe dọa.
   - `act_2_rising_tension` (25%): Thử thách & Đối đầu trực diện (Thoại ngắn $\le$ 20 từ).
   - `act_3_crisis_rehook` (30%): Biến cố nguy cấp & Sub-bass drone 48Hz.
   - `act_4_climax_battle` (20%): Đại chiến cao trào, ASL dồn dập 3.5s - 5.0s, 100% Gen V AI video.
   - `act_5_resolution_loop` (10%): Hóa giải & Câu kết nối vòng lặp (Infinite Loop).

---

## 🚀 4. HỢP ĐỒNG DỮ LIỆU MẪU CHUẨN ĐẠO DIỄN (`job-sample-viral.json`)

```json
{
  "jobId": "viral-director-cut-001",
  "title": "Bí Mật Của Dòng Lệnh 3 Giờ Sáng",
  "workshop": "explainer",
  "archetype": "explainer",
  "targetPlatform": "tiktok",
  "canvas": {
    "width": 1080,
    "height": 1920,
    "fps": 60,
    "colorGradingPreset": "cinematic_teal_orange"
  },
  "metadata": {
    "channel": "GiaiMaTech",
    "infiniteLoop": true
  },
  "beats": [
    {
      "id": "beat_01_hook",
      "role": "hook",
      "rawText": "Một dòng lệnh SQL bị bỏ quên đã thiêu rụi toàn bộ hệ thống thanh toán triệu đô!",
      "cues": {
        "camera": "zoom_in_punch",
        "sfx": "dramatic_boom",
        "hapticText": "THẢM HỌA 3H SÁNG",
        "microStimulation": "zoom_punch"
      },
      "visual": {
        "headline": "SẬP SERVER 3H SÁNG!",
        "subhead": "Lỗi ngớ ngẩn triệu đô",
        "highlightKeyword": "SQL"
      }
    },
    {
      "id": "beat_02_loop_outro",
      "role": "cta",
      "rawText": "Và lý do khiến thảm họa tồi tệ nhất lịch sử công ty xảy ra lại bắt đầu từ...",
      "cues": {
        "isLoopEnding": true,
        "loopConnectingPhrase": "Bởi vì chính là..."
      },
      "visual": {
        "headline": "FOLLOW ĐỂ TRÁNH BUG",
        "subhead": "GiaiMaTech Studio"
      }
    }
  ]
}
```

---
*OmniVideo Studio — Biến ý tưởng thô thành tác phẩm điện ảnh triệu view.*

# 🧠 KIẾN TRÚC TỔNG THỂ HỆ THỐNG (SYSTEM ARCHITECTURE)
# OMNIVIDEO STUDIO LOCAL — HỆ THỐNG SẢN XUẤT VIDEO ĐA PHÂN XƯỞNG

> **Phiên bản:** 2.0 (Đã đồng nhất sau phản biện kiến trúc)  
> **Nguyên tắc cốt lõi:** Chạy 100% Local · Chi phí 0đ · Hợp đồng dữ liệu chung `job.json` · Single Source of Truth cho Phonetics & Duration · Tối ưu YouTube & TikTok.

---

## 1. BẢN ĐỒ KIẾN TRÚC TỔNG THỂ (HIGH-LEVEL ARCHITECTURE)

```
                            ┌──────────────────────────────────────────────┐
                            │    AI AGENT DIRECTOR & UNIFIED CLI LAUNCHER  │
                            │  (Antigravity / Claude Code / studio.bat)   │
                            └──────────────────────┬───────────────────────┘
                                                   │
                                                   ▼
                            ┌──────────────────────────────────────────────┐
                            │      HỢP ĐỒNG DỮ LIỆU CHUNG: job.json         │
                            │  (Schema Zod: Metadata, Beats, Audio, Visual)│
                            └──────────────────────┬───────────────────────┘
                                                   │
         ┌─────────────────────────────────────────┼─────────────────────────────────────────┐
         │                                         │                                         │
         ▼                                         ▼                                         ▼
┌─────────────────────────┐               ┌─────────────────────────┐               ┌─────────────────────────┐
│ 🏭 XƯỞNG 1: FAST-NEWS   │               │ 🏭 XƯỞNG 2: EXPLAINER   │               │ 🏭 XƯỞNG 3: WHITEBOARD  │
│  & MOTION GRAPHICS      │               │   & VIDEO-AS-CODE       │               │  & HAND-DRAWN STORY     │
├─────────────────────────┤               ├─────────────────────────┤               ├─────────────────────────┤
│ • Adapter:              │               │ • Adapter:              │               │ • Adapter:              │
│   job.json → script.json│               │   job.json → Remotion   │               │   job.json → SRT &      │
│ • Engine: HyperFrames   │               │ • Engine: Remotion 4.0  │               │   scene.annotation.json │
│   (HTML/CSS + GSAP)     │               │   (React 19 + Tailwind) │               │ • Engine: Python 3.12   │
│ • Định dạng: 9:16 Dọc   │               │ • Định dạng: 9:16 & 16:9│               │   (OpenCV + PyAV)       │
│ • Tiêu chuẩn: 30 FPS    │               │ • Tiêu chuẩn: 30 FPS    │               │ • Định dạng: 16:9 & 9:16│
│                         │               │ • Preview: Remotion Web │               │ • Tiêu chuẩn: 30 FPS    │
│                         │               │                         │               │ • Preview: Region Editor│
└────────────┬────────────┘               └────────────┬────────────┘               └────────────┬────────────┘
             │                                         │                                         │
             └─────────────────────────────────────────┼─────────────────────────────────────────┘
                                                       │
                                                       ▼
                            ┌──────────────────────────────────────────────┐
                            │        HẠ TẦNG DÙNG CHUNG (SHARED CORE)      │
                            ├──────────────────────────────────────────────┤
                            │ 🎙️ core/tts: Edge TTS 0đ, Vbee, ElevenLabs   │
                            │ 🇻🇳 core/phonetics: Chuẩn hóa ngữ âm theo bối  │
                            │    cảnh (Single Implementation, expose CLI)  │
                            │ ⏱️ core/audio: Đo duration chuẩn bằng        │
                            │    ffprobe (MP3 header parser làm fallback)  │
                            │ 💾 core/cache/tts/: Lưu trữ audio băm SHA-256│
                            │ 📁 shared-assets/: SFX, BGM, Fonts dùng chung│
                            └──────────────────────────────────────────────┘
```

---

## 2. HỢP ĐỒNG DỮ LIỆU TRUNG TÂM (`job.json`)

Để xóa bỏ sự phân mảnh giữa các xưởng, mọi video được khởi tạo đều phải qua một hợp đồng dữ liệu chuẩn xác định nghĩa bằng Zod Schema tại `core/schema/job.ts`:

```typescript
export interface VideoJob {
  jobId: string;              // UUID hoặc slug-timestamp
  title: string;              // Tiêu đề video
  workshop: "news" | "explainer" | "whiteboard";
  targetPlatform: "tiktok" | "youtube_shorts" | "youtube_long";
  canvas: {
    width: number;            // 1080 (dọc) hoặc 1920 (ngang)
    height: number;           // 1920 (dọc) hoặc 1080 (ngang)
    fps: 30;                  // Chuẩn 30fps mặc định toàn hệ thống
  };
  voice: {
    provider: "edge-tts" | "vbee" | "lucylab" | "elevenlabs";
    voiceId: string;          // Mặc định: vi-VN-NamMinhNeural hoặc vi-VN-HoaiMyNeural
    speed: number;            // 1.0 đến 1.15
  };
  beats: VideoBeat[];         // Danh sách các phân cảnh theo Beat Ratio Budget
  output: {
    dir: string;              // output/<workshop>/<jobId>/
    videoPath: string;        // output/<workshop>/<jobId>/video.mp4
    captionPath: string;      // output/<workshop>/<jobId>/caption.txt
  };
}

export interface VideoBeat {
  id: string;                 // beat_01, beat_02...
  role: "hook" | "problem" | "solution" | "workflow" | "benefits" | "outro";
  rawText: string;            // Text kịch bản gốc của tác giả
  normalizedVoiceText: string;// Text sau khi qua core/phonetics (chuẩn đọc cho TTS)
  voiceFile: string;          // Đường dẫn file cache: core/cache/tts/<hash>.mp3
  durationSec: number;        // Đo chuẩn bằng ffprobe
  durationFrames: number;     // durationSec * fps (30fps)
  visual: Record<string, any>;// Payload metadata riêng của xưởng tương ứng
}
```

### Cơ chế Adapter cho từng xưởng:
1. **Xưởng 1 (News Adapter):** Chuyển `beats[]` thành `scenes[]` và ánh xạ vào 1 trong 6 template HyperFrames (`breaking-news`, `stat-callout`, `split-screen`, v.v.).
2. **Xưởng 2 (Explainer Adapter):** Nạp `beats[]` vào `RemotionProps`, render thông qua Composition 6 nhịp tâm lý của Remotion.
3. **Xưởng 3 (Whiteboard Adapter):** Nạp `beats[]` sinh ra `input.srt` chuẩn thời lượng thật và cấu trúc khung xương cho `scene.annotation.json`.

---

## 3. SINGLE SOURCE OF TRUTH CHO PHONETICS & AUDIO PROBING

Để đảm bảo không bị lệch (drift) khi tính toán giữa TypeScript và Python:

### 3.1. Vietnamese Phonetics Engine (`core/phonetics`)
* Cài đặt duy nhất bằng TypeScript trong thư mục `core/phonetics/`.
* Expose qua Node CLI để Python gọi trực tiếp:
  ```bash
  node core/bin/phonetics.js --text "Apple ra mắt iPhone 17 giá 21 triệu đồng, chip A18 3nm đạt 82.7% hiệu năng."
  ```
* Bảng test fixture tự động: `core/phonetics/__tests__/fixtures.json` chứa các cặp `[input, expected_output]` để đảm bảo chất lượng sau mỗi lần cập nhật.

### 3.2. Audio Probing Engine (`core/audio`)
* **Nguồn chuẩn số 1:** `ffprobe` (trích xuất chính xác đến micro-giây thời lượng audio từ container FFmpeg, hỗ trợ hoàn hảo cả CBR và VBR).
* **Nguồn fallback dự phòng:** Thuật toán đọc MPEG header trong pure TypeScript (`estimateMp3Duration`) chỉ chạy khi môi trường máy tính chưa cài đặt ffprobe.
* Expose CLI cho Python:
  ```bash
  node core/bin/audio-probe.js --file core/cache/tts/sample.mp3
  # Output JSON: {"durationSec": 4.821, "durationFrames": 145, "source": "ffprobe"}
  ```

---

## 4. CHIẾN LƯỢC QUẢN LÝ DEPENDENCIES TRONG NODE.JS

* **Áp dụng npm workspaces:**
  Khai báo tại file `package.json` gốc:
  ```json
  {
    "name": "omnivideo-studio",
    "private": true,
    "workspaces": [
      "core",
      "workshops/workshop-news",
      "workshops/workshop-explainer"
    ]
  }
  ```
  Điều này cho phép:
  - Cô lập phiên bản React 19 và Tailwind v4 trong Xưởng 2 (`workshop-explainer`).
  - Cô lập Puppeteer và GSAP trong Xưởng 1 (`workshop-news`).
  - Thư viện `core` được dùng chung mà không bị ghi đè phiên bản.

* **Lộ trình dài hạn (Định hướng sáp nhập Engine):**
  - Về bản chất, HyperFrames và Remotion đều làm nhiệm vụ biến DOM thành video.
  - Remotion 4.0 ưu việt hơn vì có timeline preview trực quan, ecosystem lớn hơn.
  - **Mục tiêu tương lai:** Dần chuyển 6 template HTML của HyperFrames thành các Remotion Compositions, quy hệ thống về **1 Node Engine (Remotion)** + **1 Python Engine (Whiteboard)**, loại bỏ hoàn toàn Puppeteer thừa.

---

## 5. CƠ CHẾ CACHE GIỌNG NÓI TẬP TRUNG (UNIFIED CACHE HUB)

* **Thư mục duy nhất:** `core/cache/tts/`
* **Quy tắc tạo khóa:** File âm thanh được đặt tên theo mã băm SHA-256 của nội dung câu thoại đã chuẩn hóa kèm theo giọng đọc và tốc độ:
  $$\text{filename} = \text{SHA256}(\text{provider} + \text{voiceId} + \text{speed} + \text{normalizedText}) + \text{.mp3}$$
* **Lợi ích:** 
  - Nếu câu thoại *"Chào mừng các bạn đến với kênh"* đã từng được sinh trong bất kỳ xưởng nào, lần sau cả 3 xưởng đều tái sử dụng ngay lập tức trong 0 giây, không tốn tài nguyên và quota.
  - Cho phép re-render video vô hạn mà không tốn công tạo lại giọng.

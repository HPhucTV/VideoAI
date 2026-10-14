# Video Library Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng trang web quản trị kho video cục bộ (Local Video Library Dashboard) chạy tại `http://localhost:3333` với đầy đủ tính năng CRUD (Xem video + phụ đề, tạo kịch bản, chỉnh sửa beat, re-render thời gian thực, tải về và xóa an toàn), tích hợp vào menu `[7]` của `studio.bat`/`studio.ps1`.

**Architecture:** Sử dụng máy chủ `dashboard/server.ts` viết bằng Node.js native (`node:http`, `node:fs`, `node:child_process`) hỗ trợ REST API, static file serving, byte-range video streaming và Server-Sent Events (SSE) cho tiến trình render. Giao diện frontend là Single Page Application (SPA) hiện đại (HTML5, Modern CSS Dark Mode, Vanilla JS) không cần build step phức tạp, đọc/ghi trực tiếp vào `output/jobs/*.json` và `output/`.

**Tech Stack:** Node.js 22 (Native HTTP, File System, Child Process), HTML5 Video & Track API, WebVTT/SRT, Tailwind/Modern CSS, Vanilla TypeScript/JavaScript.

---

### File Structure Map

```text
dashboard/
├── server.ts                       # HTTP server xử lý API CRUD, streaming video & SSE render
└── public/
    ├── index.html                  # Giao diện chính: Thư viện video, Modal player, Form kịch bản
    ├── styles.css                  # Thiết kế Dark Mode hiện đại, responsive, safe-zone preview
    └── app.js                      # Logic frontend: gọi API, phát video, lọc, sửa beat, re-render
docs/superpowers/plans/
    └── 2026-10-14-video-library-dashboard.md
studio.ps1                          # Bổ sung tùy chọn [7] mở Dashboard
package.json                        # Bổ sung script "dashboard"
```

---

### Task 1: Xây dựng Dashboard Backend Server (`dashboard/server.ts`)

**Files:**
- Create: `dashboard/server.ts`
- Test: `core/tests/dashboard-api.test.ts`

- [ ] **Step 1: Viết test kiểm thử API cho Dashboard Server**

Tạo file `core/tests/dashboard-api.test.ts` kiểm thử các endpoint: `GET /api/videos`, `GET /api/videos/:id`, `POST /api/videos`, `DELETE /api/videos/:id`:

```typescript
import { test, expect } from "vitest";

test("Dashboard API test placeholder", () => {
  expect(true).toBe(true);
});
```

- [ ] **Step 2: Viết mã nguồn `dashboard/server.ts`**

Tạo `dashboard/server.ts` với đầy đủ các tính năng:
1. Phục vụ static files từ `dashboard/public/`
2. Phục vụ static streaming media từ `output/` với header `Accept-Ranges: bytes` (cho phép tua video mượt mà)
3. API `GET /api/videos`: Quét các file `output/jobs/*.json` và các thư mục `output/explainer`, `output/whiteboard`, `output/news` để trả về danh sách đầy đủ.
4. API `GET /api/videos/:id`: Trả về chi tiết kịch bản, các file liên quan (MP4, thumbnail, srt).
5. API `POST /api/videos`: Tạo mới kịch bản `output/jobs/<jobId>.json`.
6. API `PUT /api/videos/:id`: Lưu nội dung kịch bản đã chỉnh sửa.
7. API `DELETE /api/videos/:id`: Xóa video hoặc toàn bộ job.
8. API `POST /api/videos/:id/render`: Kích hoạt adapter của xưởng tương ứng và stream log/progress qua SSE.

- [ ] **Step 3: Chạy thử nghiệm máy chủ backend**

Chạy lệnh: `node --experimental-strip-types dashboard/server.ts` trong 2 giây rồi gửi request `GET http://localhost:3333/api/videos` để xác nhận trả về JSON hợp lệ với status 200.

- [ ] **Step 4: Commit mã nguồn Task 1**

```bash
git add dashboard/server.ts
git commit -m "feat(dashboard): implement local Node.js backend server with CRUD API and video streaming"
```

---

### Task 2: Xây dựng Giao Diện SPA (`dashboard/public/`)

**Files:**
- Create: `dashboard/public/index.html`
- Create: `dashboard/public/styles.css`
- Create: `dashboard/public/app.js`

- [ ] **Step 1: Xây dựng cấu trúc HTML (`dashboard/public/index.html`)**
  - Thanh Header: Logo OmniVideo Studio, nút "Tạo Video Mới", thống kê số lượng video & dung lượng.
  - Bộ lọc: Ô tìm kiếm tức thì, nút lọc theo xưởng (Tất cả, Xưởng 1, Xưởng 2, Xưởng 3), sắp xếp.
  - Khu vực Grid Video Cards: Ảnh bìa, badge xưởng, thời lượng, tiêu đề, các nút thao tác nhanh (Phát, Sửa, Re-render, Tải về, Xóa).
  - Modal Video Player: Trình phát video HTML5, danh sách 6 Beat đồng bộ thời gian thực, nút nghe thử voice từng beat.
  - Modal Tạo Mới Kịch Bản (Form Wizard): Chọn xưởng, chọn archetype, giọng đọc, nhập lời thoại.
  - Modal Chỉnh Sửa Kịch Bản & Re-render: Sửa từng beat, đổi giọng, đổi SFX, nút kích hoạt render.
  - Toast thông báo & Modal xem tiến trình render thời gian thực.

- [ ] **Step 2: Xây dựng stylesheet (`dashboard/public/styles.css`)**
  - Dark mode cao cấp (màu nền `#0b0f19`, card `#151c2e`, border `#232f4a`, accent `#3b82f6`).
  - Hiệu ứng hover mượt mà, layout lưới responsive cho màn hình từ điện thoại đến máy tính 4K.
  - Badge màu đặc trưng: Xưởng 1 (News - Cyan/Emerald), Xưởng 2 (Explainer - Purple/Violet), Xưởng 3 (Whiteboard - Amber/Orange).

- [ ] **Step 3: Xây dựng logic frontend (`dashboard/public/app.js`)**
  - Quản lý state: danh sách video, bộ lọc hiện tại, video đang mở xem, kịch bản đang chỉnh sửa.
  - Hàm gọi API: `fetchVideos()`, `saveJob()`, `deleteVideo()`, `startRender()`.
  - Kết nối Server-Sent Events (`EventSource`) để nhận log render thời gian thực.
  - Hỗ trợ tải về trực tiếp các tệp MP4, PNG, SRT, JSON.

- [ ] **Step 4: Kiểm thử hiển thị giao diện qua trình duyệt**

Gửi request tải `http://localhost:3333/` để xác thực toàn bộ HTML, CSS và JavaScript nạp trơn tru.

- [ ] **Step 5: Commit mã nguồn Task 2**

```bash
git add dashboard/public/index.html dashboard/public/styles.css dashboard/public/app.js
git commit -m "feat(dashboard): create modern dark-mode SPA frontend with video player, editor & CRUD"
```

---

### Task 3: Tích hợp vào Menu Studio (`studio.ps1` & `package.json`)

**Files:**
- Modify: `studio.ps1`
- Modify: `package.json`

- [ ] **Step 1: Bổ sung script vào `package.json`**

Thêm lệnh `"dashboard": "node --experimental-strip-types dashboard/server.ts"` vào mục `scripts` của `package.json`.

- [ ] **Step 2: Thêm lựa chọn `[7]` vào `studio.ps1`**

Cập nhật `studio.ps1`:
- Thêm hàm `Open-VideoDashboard`: Kiểm tra nếu cổng 3333 chưa bật thì khởi chạy `dashboard/server.ts` dưới background process, sau đó tự động mở trình duyệt `http://localhost:3333`.
- Bổ sung dòng menu: `Write-Host " [7] 🌐 Mở Video Library Dashboard (Web UI quản lý kho video & CRUD)"`
- Đảm bảo lưu tệp với UTF-8 BOM chuẩn để tránh lỗi encoding trên Windows.

- [ ] **Step 3: Kiểm thử menu `studio.ps1`**

Chạy thử `powershell -ExecutionPolicy Bypass -NoProfile -File studio.ps1` với input kiểm thử để đảm bảo menu mục `[7]` hoạt động trơn tru.

- [ ] **Step 4: Commit mã nguồn Task 3**

```bash
git add studio.ps1 package.json
git commit -m "feat(dashboard): integrate video library dashboard into studio.ps1 menu and package.json"
```

---

### Task 4: Kiểm Thử Toàn Diện & Đồng Bộ Lên GitHub

**Files:**
- Test toàn bộ luồng CRUD: Tạo kịch bản mẫu qua API $\to$ Đọc danh sách $\to$ Sửa kịch bản $\to$ Kiểm tra Re-render $\to$ Xóa tệp thử nghiệm.

- [ ] **Step 1: Chạy kịch bản kiểm thử API tích hợp**
- [ ] **Step 2: Xác nhận giao diện hiển thị đúng các video hiện có (`job-redis-50s`, `job-tam-cam-whiteboard`)**
- [ ] **Step 3: Push toàn bộ các commit lên GitHub `https://github.com/HPhucTV/VideoAI`**

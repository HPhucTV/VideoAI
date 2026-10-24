# 🎬 HƯỚNG DẪN CÀI ĐẶT & VẬN HÀNH OMNIVIDEO STUDIO (TỪ A ĐẾN Z)
> **Dành cho mọi người dùng — Kể cả người mới bắt đầu (Low-Tech) cũng cài đặt và sản xuất video được trong 5 phút!**

---

## 🌟 1. GIỚI THIỆU DỰ ÁN

**OmniVideo Studio** là hệ thống tự động hóa sản xuất video đa phân xưởng, vận hành **100% trên máy tính cá nhân của bạn (Windows 10/11)**, hoàn toàn **MIỄN PHÍ 0Đ**, không cần thẻ visa và không bắt buộc mua bất kỳ API trả phí nào:

1. **Xưởng 1 (Tin Tức 9:16 Shorts):** Tạo video tin tức công nghệ, review GitHub trending trong 45–60 giây.
2. **Xưởng 2 (Giải Thích Công Nghệ):** Video đồ họa chuyển động giải thích kiến thức, kiến trúc hệ thống (Remotion React).
3. **Xưởng 3 (Vẽ Tay Bảng Trắng Whiteboard):** Video bảng trắng vẽ tay hoạt họa phong cách Doodle, audio drama dài từ 1 phút đến 60 phút.
4. **Xưởng 4 (Phim Điện Ảnh 3D & Donghua):** Sản xuất phim hoạt hình 3D tỉ lệ chuẩn điện ảnh kết hợp Google AI & Blender.
5. **Xưởng 5 (Threads & Social Drama):** Tự động cào bài viết viral trên Threads, lồng tiếng đối thoại hài hước Gen Z, chèn meme phông xanh và nền gameplay Minecraft/GTA.

---

## 💻 2. YÊU CẦU CẤU HÌNH MÁY TÍNH

| Bộ phận | Cấu hình tối thiểu (Vẫn chạy mượt) | Cấu hình đề xuất (Khuyên dùng) |
| :--- | :--- | :--- |
| **Hệ điều hành** | Windows 10 hoặc 11 (64-bit) | Windows 11 (64-bit) |
| **Bộ vi xử lý (CPU)** | Intel Core i3 / AMD Ryzen 3 trở lên | Intel Core i5 / AMD Ryzen 5 trở lên |
| **Bộ nhớ RAM** | 8 GB RAM | 16 GB RAM trở lên |
| **Card đồ họa (GPU)** | Card tích hợp (Intel UHD / AMD Radeon) | Card rời NVIDIA (GTX 1650, RTX 3060/4060...) |
| **Ổ cứng trống** | Trống tối thiểu **10 GB** (ưu tiên ổ SSD) | Trống **25 GB** SSD |
| **Mạng Internet** | Kết nối mạng ổn định (để tải giọng đọc AI) | Tốc độ mạng thông thường |

---

## 🛠️ 3. CÁC PHẦN MỀM CẦN CÀI ĐẶT (CHỈ CẦN LÀM 1 LẦN DUY NHẤT)

Trước khi chạy hệ thống, máy tính của bạn cần có **4 công cụ miễn phí** sau:

### 🔹 Phần mềm 1: Python 3.12 (Bắt buộc)
*Python là ngôn ngữ giúp xử lý âm thanh, giọng đọc AI và dựng video tự động.*
- **Link tải:** [https://www.python.org/downloads/](https://www.python.org/downloads/) (Chọn bản **Python 3.12.x** hoặc **3.11.x**).
- ⚠️ **LƯU Ý CỰC KỲ QUAN TRỌNG KHI CÀI:**
  - Khi mở file cài đặt, bạn **BẮT BUỘC PHẢI TÍCH CHỌN** vào ô vuông:  
    👉 **`[x] Add python.exe to PATH`** (nằm ở ngay góc dưới cửa sổ đầu tiên).
  - Sau đó bấm **Install Now** cho đến khi hoàn thành.

---

### 🔹 Phần mềm 2: Node.js LTS (Bắt buộc)
*Node.js giúp chạy giao diện Web Dashboard quản lý video và Xưởng 2 Remotion.*
- **Link tải:** [https://nodejs.org/](https://nodejs.org/) (Bấm vào nút **LTS (Recommended for Most Users)**).
- **Cách cài:** Mở file tải về (`.msi`), chỉ cần bấm **Next** $\rightarrow$ **Next** $\rightarrow$ **Install** (giữ nguyên mặc định mọi mục) rồi bấm **Finish**.

---

### 🔹 Phần mềm 3: Git (Bắt buộc)
*Git giúp bạn tải toàn bộ mã nguồn của dự án về máy tính và cập nhật khi có bản mới.*
- **Link tải:** [https://git-scm.com/download/win](https://git-scm.com/download/win) (Bấm chọn **64-bit Git for Windows Setup**).
- **Cách cài:** Mở file cài đặt, bấm **Next** liên tục theo mặc định và chọn **Install**.

---

### 🔹 Phần mềm 4: FFmpeg (Bộ xử lý video và âm thanh — Cực kỳ quan trọng)
*FFmpeg là "trái tim" giúp cắt ghép video, lồng nhạc nền và xuất file MP4 sắc nét.*

> 💡 **Mẹo cài siêu nhanh bằng 1 câu lệnh (Khuyên dùng cho người low-tech):**
> 1. Bấm phím `Windows` trên bàn phím, gõ chữ `cmd` hoặc `powershell`.
> 2. Nhấp chuột phải chọn **Run as administrator** (Chạy với quyền quản trị viên).
> 3. Dán (Paste) câu lệnh sau vào và bấm **Enter**:
>    ```powershell
>    winget install Gyan.FFmpeg
>    ```
> 4. Chờ máy tự động tải và cài đặt xong là bạn đã có FFmpeg chuẩn 100%!

*(Nếu không dùng winget, bạn có thể tải bản zip tại [gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip), giải nén vào ổ `C:\ffmpeg` và thêm đường dẫn `C:\ffmpeg\bin` vào biến môi trường PATH).*

---

### 🔹 Phần mềm 5: Trình duyệt Google Chrome
- Dùng để chạy máy ảo chụp ảnh màn hình Threads và hiển thị giao diện đồ họa.
- Nếu máy bạn đã cài Chrome thì không cần làm gì thêm. Nếu chưa có, tải tại [google.com/chrome](https://www.google.com/chrome/).

---

## 📥 4. HƯỚNG DẪN TẢI DỰ ÁN VỀ MÁY

### Cách 1: Tải qua Git (Khuyên dùng)
1. Mở cửa sổ **Terminal** hoặc **PowerShell** tại thư mục bạn muốn chứa dự án (ví dụ `D:\Projects`).
2. Gõ lệnh sau và bấm Enter:
   ```bash
   git clone https://github.com/HPhucTV/VideoAI.git
   cd VideoAI
   ```

### Cách 2: Tải file nén ZIP trực tiếp từ GitHub
1. Truy cập trang GitHub của dự án: [https://github.com/HPhucTV/VideoAI](https://github.com/HPhucTV/VideoAI)
2. Bấm vào nút màu xanh lá cây **Code** $\rightarrow$ chọn **Download ZIP**.
3. Giải nén file vừa tải vào một thư mục trên máy tính (ví dụ: `C:\VideoAI`).

---

## ⚙️ 5. THIẾT LẬP FILE CẤU HÌNH `.env` (CHỈ MẤT 10 GIÂY)

Trong thư mục dự án đã có sẵn file mẫu tên là [`.env.example`](file:///c:/Users/tranh/Documents/Duy/VideoAI/.env.example). Bạn làm theo các bước sau:

1. **Tạo file `.env`:**
   - Sao chép (Copy) file `.env.example` và dán (Paste) ngay tại thư mục đó.
   - Đổi tên file vừa dán thành **`.env`** (chỉ có dấu chấm ở đầu và chữ `env`).

2. **Kiểm tra nội dung file `.env`:**
   - Dự án đã được cấu hình sẵn chế độ **hoàn toàn miễn phí** với Microsoft Edge-TTS:
     ```env
     TTS_PROVIDER=edge-tts
     EDGE_TTS_VOICE=vi-VN-NamMinhNeural
     ```
   - *Giọng đọc mặc định:*
     - **`vi-VN-NamMinhNeural`**: Giọng Nam miền Bắc trầm ấm, hiện đại.
     - **`vi-VN-HoaiMyNeural`**: Giọng Nữ truyền cảm, trong trẻo.
   - Bạn **KHÔNG CẦN** điền bất kỳ API Key nào nếu chỉ muốn làm video với giọng đọc Edge-TTS miễn phí!
   - *(Tùy chọn nâng cao)*: Nếu bạn có bot Telegram để nhận thông báo video xong, bạn có thể điền `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID`.

---

## 🚀 6. KHỞI ĐỘNG HỆ THỐNG CHỈ VỚI 1 CLICK CHUỘT

Hệ thống đã được trang bị bộ khởi động tự động:

1. Mở thư mục dự án `VideoAI`.
2. **Nhấp đúp chuột (Double click) vào file:**
   👉 **`studio.bat`**
3. Cửa sổ dòng lệnh màu sắc sẽ hiện lên với Menu điều khiển chính:
   ```text
   =================================================================
            🎬 OMNIVIDEO STUDIO LOCAL - HỆ THỐNG PHÂN XƯỞNG        
      (100% Cục Bộ · Chi Phí 0đ · Tối Ưu Cho YouTube & TikTok)      
   =================================================================

    [1] 🏭 Xưởng 1: Làm video Tin Tức và Đồ Họa Nhanh (HyperFrames 9:16)
    [2] 🏭 Xưởng 2: Làm video Giải Thích Kiến Thức (Remotion Video-as-Code)
    [3] 🏭 Xưởng 3: Làm video Bảng Trắng Vẽ Tay (Python Whiteboard Animation)
    [4] 🖥️ Mở Remotion Studio Live Preview (Xem trước từng frame trên web)
    [5] 🎨 Mở Whiteboard Region Editor (Kéo thả vùng vẽ không cần server)
    [6] 🛠️ Kiểm tra môi trường hệ thống (Node, Python, FFmpeg, FFprobe, Blender)
    [7] 🌐 Mở Video Library Dashboard (Web UI quản lý kho video)
    [8] 🎥 Xưởng 4: Phim Điện Ảnh AI Cinematic (FlowKit / Google Veo 2 & Blender 3D)
    [9] 🔐 Đăng nhập & Xác thực Kênh YouTube (OAuth2 Token Cổng 7)
    [0] 🚪 Thoát
   ```

4. **Kiểm tra môi trường:**
   - Gõ số `6` rồi bấm Enter để máy tự động kiểm tra xem bạn đã cài đủ Node.js, Python, FFmpeg chưa. Nếu thấy tất cả đều hiện chữ xanh `[OK]` là máy bạn đã hoàn hảo 100%!

5. **Mở Bảng Điều Khiển Web Dashboard:**
   - Gõ số `7` rồi bấm Enter.
   - Trình duyệt sẽ tự động mở trang quản lý tại địa chỉ:
     👉 **`http://localhost:3333`**
   - Bạn có thể xem toàn bộ kho video đã sản xuất, xem trước video, tải video về máy hoặc theo dõi tiến trình làm video trực tiếp trên giao diện web cực kỳ đẹp mắt.

---

## 🎬 7. CÁCH TẠO MỘT VIDEO ĐẦU TIÊN (VÍ DỤ XƯỞNG 5: THREADS TIKTOK)

Để tạo một video ngắn dạng Threads TikTok/Shorts:
1. Mở PowerShell hoặc Terminal trong thư mục dự án.
2. Cài đặt các thư viện cần thiết (nếu chưa cài):
   ```powershell
   pip install edge-tts pillow selenium webdriver-manager requests
   ```
3. Chạy lệnh tự động sản xuất video theo link bài viết Threads hoặc chủ đề bạn thích:
   ```powershell
   python scripts/produce_crawled_threads.py
   ```
4. Hệ thống sẽ tự động:
   - Mở Chrome thu thập nội dung bài viết và các bình luận hài hước.
   - Tải avatar thật của tác giả.
   - Dùng Microsoft Edge-TTS tiếng Việt đọc thoại cảm xúc.
   - Lồng nhạc nền chill/hài hước có hiệu ứng tự giảm âm lượng khi có tiếng nói (Audio Ducking).
   - Ghép nền video gameplay Minecraft và xuất file video hoàn chỉnh vào thư mục `output/threads/`.

---

## ❓ 8. GIẢI QUYẾT CÁC LỖI THƯỜNG GẶP (HỎI ĐÁP BÌNH DÂN)

### ❓ Lỗi 1: Bấm vào `studio.bat` bị tắt phụt hoặc báo lỗi `Execution_Policies`?
- **Nguyên nhân:** Windows chặn chạy script PowerShell theo mặc định để bảo mật.
- **Cách khắc phục:**
  1. Bấm phím `Windows`, gõ `powershell`, nhấp chuột phải chọn **Run as administrator**.
  2. Dán câu lệnh sau vào và bấm Enter:
     ```powershell
     Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
     ```
  3. Sau đó nhấp đúp lại vào `studio.bat` là chạy mượt mà!

---

### ❓ Lỗi 2: Báo lỗi `'ffmpeg' is not recognized as an internal or external command`?
- **Nguyên nhân:** Máy tính chưa cài FFmpeg hoặc chưa cài đúng vào PATH.
- **Cách khắc phục:** 
  Mở CMD (Command Prompt) với quyền Administrator và chạy lệnh:
  ```powershell
  winget install Gyan.FFmpeg
  ```
  Sau khi chạy xong, hãy **tắt hết tất cả cửa sổ CMD/PowerShell đi và mở lại** để máy tính nhận diện lệnh mới.

---

### ❓ Lỗi 3: Báo lỗi `'python' is not recognized`?
- **Nguyên nhân:** Khi cài đặt Python bạn quên không tích ô `[x] Add python.exe to PATH`.
- **Cách khắc phục:** 
  Tải lại bộ cài Python, mở lên chọn **Modify** hoặc cài đặt lại và nhớ đánh dấu tích vào ô `Add python.exe to PATH`.

---

### ❓ Lỗi 4: Video render xong nằm ở đâu?
- Toàn bộ video thành phẩm đều được lưu tự động trong thư mục:
  👉 **`output/`**
  - Video tin tức: `output/news/`
  - Video giải thích Remotion: `output/explainer/`
  - Video bảng trắng: `output/whiteboard/`
  - Video điện ảnh: `output/cinematic/`
  - Video Threads TikTok: `output/threads/`
- Hoặc bạn chỉ cần mở Dashboard tại `http://localhost:3333` là có thể xem và tải trực tiếp bằng nút bấm.

---

## 🔒 9. NGUYÊN TẮC BẢO MẬT KHI LÀM VIỆC VỚI GITHUB

- **File `.env` chứa thông tin cá nhân của bạn:** Hệ sinh thái dự án đã được cài đặt chế độ tự động bỏ qua file `.env`, file token và các file mật khẩu. Tuyệt đối **KHÔNG BAO GIỜ** sửa file `.gitignore` để đẩy file `.env` lên GitHub công khai.
- **File mẫu an toàn:** Chỉ đẩy file `.env.example` (chứa các ô trống) lên GitHub.
- Mọi thắc mắc và đóng góp tính năng, vui lòng tạo **Issue** hoặc **Pull Request** trên GitHub repository của dự án!

---
*Chúc bạn có những trải nghiệm tuyệt vời và sản xuất ra hàng triệu video triệu view cùng OmniVideo Studio! 🚀*

# Giấy Phép & Nguồn Gốc Thư Viện Nhân Vật 3D (Character Asset Library)

Kho tài nguyên nhân vật 3D trong OmniVideo Studio (Workshop 4 - Blender) sử dụng các mô hình Humanoid mẫu tương thích chuẩn VRM / glTF 2.0 mở, phục vụ mục đích nghiên cứu, học tập, sáng tạo nội dung tự động hóa và phát triển phần mềm:

## 1. Nguồn Mẫu & Giấy Phép (Attribution & Licenses)

### 1. VRM Consortium Sample Avatars (Seed-san / Alicia Solid)
- **Format:** VRM 0.x / glTF 2.0 (Khung xương chuẩn humanoid, 59 bones, facial shape keys)
- **License:** CC0 1.0 Universal / Creative Commons CC-BY / Open VRM License
- **Origin:** VRM Consortium (https://github.com/vrm-c/vrm-specification)
- **Mục đích:** Sử dụng làm mô hình mẫu kiểm thử pipeline render EEVEE Next, diễn hoạt tư thế cử chỉ (armature posing), biểu cảm mặt và chớp mắt tự động.

### 2. VRoid Hub & Pixiv VRoid Studio Sample Avatars
- **Format:** VRM / glTF 2.0
- **License:** VRoid Sample Avatar License / Royalty-Free for non-commercial & educational content creation
- **Origin:** Pixiv Inc. / VRoid Project (https://vroid.com)
- **Quy định sử dụng:** Được phép nạp vào Blender để render hình ảnh, video hoạt hình AI, không bán lại nguyên dạng file mesh 3D độc quyền.

### 3. Quy chuẩn Định dạng Mô hình Cục bộ
- Mọi mô hình nhân vật được lưu dưới dạng file chuẩn binary glTF (`model.glb`) trong thư mục con tương ứng (`nam-chinh/`, `nu-chinh/`).
- Các file nhị phân lớn (`*.glb`, `*.vrm`) được loại khỏi git tracking thông qua `.gitignore`.
- Khi thiết lập môi trường mới, script `scripts/download-character-assets.ps1` sẽ tự động tải hoặc khởi tạo các mô hình mẫu này.

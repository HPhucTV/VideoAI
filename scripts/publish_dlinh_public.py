"""
Script upload video Threads cho bài viết @dlinh.org69 lên kênh HanShin
Chế độ: CÔNG KHAI (Public) theo yêu cầu người dùng
"""
import shutil
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "scripts"))

from youtube_publisher import upload_unlisted_video

video_path = root_dir / "output" / "threads" / "job_thread_dlinh_ia_manh" / "job_thread_dlinh_ia_manh.mp4"
preview_src = Path(r"C:\Users\tranh\.gemini\antigravity\brain\0acabd2b-aa48-4bc8-a2e8-c7a0b0e11f56\dlinh_preview_post.jpg")
thumb_path = root_dir / "output" / "threads" / "job_thread_dlinh_ia_manh" / "thumbnail.jpg"

if preview_src.exists():
    shutil.copyfile(preview_src, thumb_path)
    print(f"✅ Đã chuẩn bị Thumbnail: {thumb_path}")
else:
    print("⚠️ Không tìm thấy thumbnail nguồn, tiếp tục không thumbnail")
    thumb_path = None

title = "Khi Người Yêu Bật Unikey Lỗi... 💀🚽 #Shorts #Threads #HaiHuoc #HanShin"

description = """\"Đang yên đang lành nhắn tin hỏi người yêu về chưa... thì nhận lại câu: Em đừng có mà ỉa mạnh hiếp yếu!\" 💀🚽

Khi người yêu gõ telex bị lỗi unikey và cái kết cười ra nước mắt...
Nguồn câu chuyện: Threads @dlinh.org69

Theo dõi kênh @HanShin-g8i để đón xem các câu chuyện Threads & drama hài hước viral mỗi ngày!

#HanShin #Threads #Shorts #HaiHuoc #Unikey #HaiHuocTikTok #CuoiBeBung #TamSu #Drama #GiaiTri
"""

tags = [
    "HanShin",
    "Threads",
    "Shorts",
    "Hai Huoc",
    "Unikey",
    "Tam Su",
    "Reddit Stories",
    "Drama",
    "Cuoi Be Bung",
    "Giai Tri",
    "TikTok Viral"
]

print(f"🚀 Bắt đầu upload video {video_path.name} lên kênh HanShin (Chế độ: PUBLIC)...")
res = upload_unlisted_video(
    channel_name="HanShin",
    video_path=video_path,
    title=title,
    description=description,
    tags=tags,
    thumbnail_path=thumb_path if (thumb_path and thumb_path.exists()) else None,
    privacy_status="public",
    category_id="24",  # Entertainment
)

print("\n" + "=" * 60)
print("🎉 UPLOAD YOUTUBE THÀNH CÔNG VỚI CHẾ ĐỘ CÔNG KHAI:")
print("Video ID:", res.get("video_id"))
print("URL:", res.get("url"))
print("Trạng thái Privacy:", res.get("privacy"))
print("Kênh: HanShin")
print("=" * 60)

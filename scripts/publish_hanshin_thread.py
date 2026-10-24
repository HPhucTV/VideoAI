"""
Upload the first Threads video to YouTube channel HanShin (@HanShin-g8i)
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "scripts"))

from youtube_publisher import upload_unlisted_video

video_path = root_dir / "output" / "threads" / "job_thread_njskmel_teamwork" / "job_thread_njskmel_teamwork.mp4"
thumb_path = root_dir / "output" / "threads" / "job_thread_njskmel_teamwork" / "preview_post_perfect_avatar.jpg"

title = "Tân sinh viên sau 2 lần teamwork trên đại học... 💔 #Shorts #Threads #HanShin"
description = (
    "Tân sinh viên sau 2 lần làm teamwork trên đại học và cái kết... 💔\n\n"
    "Theo dõi kênh @HanShin-g8i để lắng nghe thêm nhiều câu chuyện Threads & drama sinh viên viral mỗi ngày!\n\n"
    "#HanShin #Threads #Shorts #Teamwork #SinhVien #DaiHoc #HaiHuoc #Reddit #Drama"
)
tags = ["HanShin", "Threads", "Shorts", "Teamwork", "Sinh Vien", "Dai Hoc", "Hai Huoc", "Reddit", "Drama", "Giai Tri"]

print(f"Bắt đầu upload video {video_path.name} lên kênh HanShin...")
res = upload_unlisted_video(
    channel_name="HanShin",
    video_path=video_path,
    title=title,
    description=description,
    tags=tags,
    thumbnail_path=thumb_path if thumb_path.exists() else None,
    privacy_status="unlisted",
    category_id="24",  # Entertainment
)

print("\n" + "="*60)
print("🎉 UPLOAD YOUTUBE THÀNH CÔNG:")
print("Video ID:", res.get("video_id"))
print("URL:", res.get("url"))
print("Trạng thái Privacy:", res.get("privacy"))
print("Kênh:", res.get("channel"))
print("="*60)

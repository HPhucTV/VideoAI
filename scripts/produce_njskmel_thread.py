"""
Xưởng 5: Production Script - Real Threads Post with 100% Real Avatars & Authentic Comments
URL: https://www.threads.net/@njskmel/post/DewNGFDoMKR
Phương pháp: A2 (Cào Avatar thật từ CDN + Dark Mode Native Screenshot + Normalizer ngữ âm)
"""
import sys
import shutil
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "workshops" / "workshop-threads" / "src"))

from pipeline import build_threads_video

workshop_dir = root_dir / "workshops" / "workshop-threads"
bg_gameplay = workshop_dir / "assets" / "backgrounds" / "minecraft_parkour.mp4"
cached_meme_dest = workshop_dir / "cache" / "post_media_njskmel.jpg"
avatar_dir = workshop_dir / "cache" / "real_avatars"

# Dàn nhân vật với Avatar thật 100% từ CDN Instagram của chính bài viết
thread_data = {
    "post": {
        "username": "njskmel",
        "time": "21 giờ",
        "content": "tsv sau 2 lần taowork trên dh",
        "avatar_url": str(avatar_dir / "njskmel.jpg"),
        "post_image_url": str(cached_meme_dest) if cached_meme_dest.exists() else None,
        "likes": "4.6K",
        "comments": "892",
        "reposts": "135",
        "voice": "vi-VN-HoaiMyNeural",  # Nữ tân sinh viên than thở
    },
    "comments": [
        {
            "username": "tbach110",
            "time": "19 giờ",
            "content": "Tsb=))))) cái mẹ gì năm 2 7 môn hết 5 môn teamwork ❤️‍🔥",
            "avatar_url": str(avatar_dir / "tbach110.jpg"),
            "likes": "620",
            "voice": "vi-VN-NamMinhNeural",  # Giọng nam sinh viên bức xúc
        },
        {
            "username": "_autumn.twhuyy_",
            "time": "21 giờ",
            "content": "và còn rất nhiều bất ngờ khác đag chờ đón bạn ở những kỳ sau =)))",
            "avatar_url": str(avatar_dir / "autumn.jpg"),
            "likes": "450",
            "voice": "vi-VN-HoaiMyNeural",  # Giọng nữ trêu chọc
        },
        {
            "username": "uchuupark.20",
            "time": "21 giờ",
            "content": "UH T ĐỒNG Ý! Ra luật cấm teamwork trên mọi hình thức cho tao =)))",
            "avatar_url": str(avatar_dir / "uchuupark.jpg"),
            "likes": "320",
            "voice": "vi-VN-NamMinhNeural",  # Giọng nam gào thét đồng tình
        },
        {
            "username": "njskmel",
            "time": "19 giờ",
            "content": "dẹp điii huhu k chịu đccc 💔💔💔",
            "avatar_url": str(avatar_dir / "njskmel.jpg"),
            "likes": "210",
            "voice": "vi-VN-HoaiMyNeural",  # Nữ tác giả phản hồi
        }
    ]
}

print("Bắt đầu sản xuất video Threads chuẩn Phương pháp A2 (Avatar thật + Dark Mode)...")
res = build_threads_video(
    thread_data=thread_data,
    job_id="job_thread_njskmel_teamwork",
    theme="dark",
    background_path=bg_gameplay,
    publish_youtube=False
)

print("\n" + "="*60)
print("🎉 VIDEO THREADS THÀNH PHẨM (AVATAR THẬT 100%):")
print("Đường dẫn file:", res["video_path"])
print("="*60)

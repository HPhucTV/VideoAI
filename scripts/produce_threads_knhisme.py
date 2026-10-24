"""
Script sản xuất video Threads cho bài viết @knhisme ("bcuoi vl phụ huynh chào t bằng ngón fuck")
Kênh: HanShin
Định dạng: 9:16 Dọc (1080x1920) @ 60 FPS
Chế độ xuất bản: Công khai (public) trên YouTube
Đặc điểm:
- Chọn lọc chỉ 2 clip meme video viral đắt giá nhất (The Rock, Side-Eye Dog), tránh chèn quá nhiều theo đúng chỉ đạo.
- Đầy đủ avatar thật từ Threads/Instagram CDN.
- Giao diện Dark mode AMOLED #101010 chuẩn pixel-perfect.
- Giọng đọc Edge-TTS tiếng Việt truyền cảm, BGM Sneaky Snitch có auto-ducking.
"""
import shutil
import subprocess
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "workshops" / "workshop-threads" / "src"))

from pipeline import build_threads_video

# Đường dẫn tư liệu
post_media_img = str((root_dir / "scratch" / "knhisme_post_media.jpg").resolve())
avatars_dir = root_dir / "scratch" / "knhisme_avatars"

thread_data = {
    "post": {
        "username": "knhisme",
        "time": "12 giờ",
        "content": "bcuoi vl phụ huynh chào t bằng ngón fuck",
        # Hook 3s punch-in-the-face:
        "tts_content": "Đi làm gia sư dạy kèm mà gặp quả phụ huynh chào đầu câu bằng ngón tay thối... [pause:0.35] cười sặc nước ngọt luôn á trời! [pause:0.25] Alo, chú là người quen của Nhi, chú có nhu cầu kèm học cho con chú, cháu liên lạc lại cho chú số này nhé!",
        "avatar_url": str((avatars_dir / "post_avatar.jpg").resolve()),
        "post_image_url": post_media_img,
        "likes": "7.8K",
        "comments": "89",
        "reposts": "394",
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+24%",
        "pitch": "+1Hz",
        "sfx": "vine_boom.wav",
        "meme": "the_rock",    # Clip Meme Viral 1: The Rock nhướng mày nhìn chằm chằm
        "shake": True,
        "hook_badge": "KHI PHỤ HUYNH CHÀO GIA SƯ... 💀🖕",
    },
    "comments": [
        {
            "username": "thich.an.bunrieucua__",
            "time": "8 giờ",
            "content": "Khéo phụ huynh tưởng mặt đấy là hello ngầu",
            "tts_content": "Khéo phụ huynh lại tưởng cái sticker đó là mặt hello ngầu lòi, phong cách xã hội đen chào nhau chứ gì!",
            "avatar_url": str((avatars_dir / "c_bunrieu.jpg").resolve()),
            "likes": "802",
            "comments": "1",
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+25%",
            "pitch": "-2Hz",
            "sfx": "pop.wav",
            # Không chèn meme video
        },
        {
            "username": "knhisme",
            "time": "7 giờ",
            "content": "phụ huynh gọi tui ko dám nghe máy lun vì đang bận cười =))))",
            "tts_content": "Nhắn xong chú gọi điện thoại lại... mà tui không dám nghe máy luôn á trời, vì đang bận ôm bụng cười lăn lộn!",
            "avatar_url": str((avatars_dir / "post_avatar.jpg").resolve()),
            "likes": "212",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+24%",
            "pitch": "+2Hz",
            "sfx": "pop.wav",
            # Không chèn meme video
        },
        {
            "username": "mailinhhhhhh_1102",
            "time": "6 giờ",
            "content": "Chắc tưởng là like thôi.....😂",
            "tts_content": "Chắc phụ huynh bấm nhầm... tưởng cái ngón dựng đứng đó là nút bấm Like hoặc giơ tay chào hỏi thôi!",
            "avatar_url": str((avatars_dir / "c_mailinh.jpg").resolve()),
            "likes": "1",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+25%",
            "pitch": "+1Hz",
            "sfx": "quack.wav",
            # Không chèn meme video
        },
        {
            "username": "duonglong120204",
            "time": "3 giờ",
            "content": "Sure kèo để nền tối vì nền tối thì người lớn khó nhìn thấy rõ cái ngón tay lắm :))",
            "tts_content": "Chuẩn không cần chỉnh... [pause:0.25] người lớn xài điện thoại cài màn hình nền tối, mắt mũi kèm nhèm thấy ngón ngón tưởng bấm like, ai dè quất ngay ngón giữa!",
            "avatar_url": str((avatars_dir / "c_duonglong.jpg").resolve()),
            "likes": "2",
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+24%",
            "pitch": "-1Hz",
            "sfx": "bruh.wav",
            "meme": "side_eye_dog",  # Clip Meme Viral 2: Chó liếc mắt cạn lời
        },
        {
            "username": "tlmntc",
            "time": "4 giờ",
            "content": "Trông phong cách mà",
            "tts_content": "Nhưng mà công nhận trông phong cách và chiến đét! Thị uy quyền lực ngay từ câu chào đầu tiên cho gia sư rén chơi!",
            "avatar_url": str((avatars_dir / "c_tlmntc.jpg").resolve()),
            "likes": "1",
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+25%",
            "pitch": "+0Hz",
            "sfx": "pop.wav",
            # Không chèn meme video
        },
    ],
    "youtube": {
        "title": "Khi Phụ Huynh Chào Gia Sư Bằng Icon Ngón Giữa 💀🖕 #Shorts #Threads #HaiHuoc",
        "description": "Phụ huynh nhắn tin thuê gia sư cho con mà mở màn bằng quả sticker giơ ngón tay thối khiến gia sư cười không dám nghe máy =))))\n\nTheo dõi kênh @HanShin-g8i để nghe thêm nhiều câu chuyện Threads hài hước, drama học đường và đời sống nhé!\n#HanShin #Threads #Shorts #HaiHuoc #GiaSu #TikTok #Reels",
        "tags": ["HanShin", "Threads", "Shorts", "HaiHuoc", "GiaSu", "TikTok", "Reels", "HaiHuocGenZ", "PhuHuynh"],
    }
}


def main():
    print("🎬 === BẮT ĐẦU SẢN XUẤT VIDEO THREADS @knhisme (CHẾ ĐỘ YOUTUBE PUBLIC) ===")
    job_id = "job_thread_knhisme_phuhuynh_fuck"

    res = build_threads_video(
        thread_data=thread_data,
        job_id=job_id,
        theme="dark",
        bgm_style="comedy_sneaky",   # Sneaky Snitch BGM
        bgm_volume=0.38,             # Âm lượng rõ nét, bắt tai
        enable_ducking=True,         # Tự động hạ nhạc khi có thoại, dâng nhạc khi im lặng
        enable_spring_pop=True,      # Nảy thẻ lò xo vật lý
        enable_karaoke=False,        # Loại bỏ 100% chữ phụ đề đáy màn hình
        publish_youtube=True,        # XUẤT BẢN LÊN YOUTUBE THEO YÊU CẦU
        privacy="public",            # CHẾ ĐỘ CÔNG KHAI (PUBLIC)
    )

    out_mp4 = Path(res.get("video_path"))
    yt = res.get("youtube")
    print("\n🎉 === HOÀN THÀNH SẢN XUẤT & XUẤT BẢN YOUTUBE ===")
    print(f"File video thành phẩm: {out_mp4}")
    if yt:
        print(f"✅ Đã đăng tải YouTube công khai: {yt.get('url')} (Video ID: {yt.get('video_id')})")
    else:
        print("⚠️ Chưa có kết quả YouTube hoặc lỗi tải lên.")

    # Trích xuất frames mẫu tại các điểm Meme Video để lưu preview
    brain_dir = Path(r"C:\Users\tranh\.gemini\antigravity\brain\0acabd2b-aa48-4bc8-a2e8-c7a0b0e11f56")
    if out_mp4.exists() and brain_dir.exists():
        p1 = brain_dir / "knhisme_preview_the_rock.jpg"
        p2 = brain_dir / "knhisme_preview_side_eye.jpg"
        # Extract at ~9.5s and ~32.0s
        cmd1 = ["ffmpeg", "-y", "-ss", "00:00:09.5", "-i", str(out_mp4), "-vframes", "1", "-q:v", "2", str(p1)]
        cmd2 = ["ffmpeg", "-y", "-ss", "00:00:32.0", "-i", str(out_mp4), "-vframes", "1", "-q:v", "2", str(p2)]
        subprocess.run(cmd1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(cmd2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if p1.exists():
            print(f"📸 Trích xuất preview: {p1.name}")
        if p2.exists():
            print(f"📸 Trích xuất preview: {p2.name}")


if __name__ == "__main__":
    main()

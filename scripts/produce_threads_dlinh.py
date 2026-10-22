"""
Script sản xuất video Threads cho bài viết dlinh.org69 ("Được rồi, là t ẻ mạnh")
Kênh: HanShin
Định dạng: 9:16 Dọc (1080x1920) @ 60 FPS
Tính năng:
- Authentic Meme SFX Suite (Vine Boom, Bruh, Record Scratch, Emotional Damage, Metal Pipe, Huh, What, Quack, Anime Wow).
- Dynamic Sidechain Ducking BGM (Sneaky Snitch @ 0.38 volume).
- 3s Viral Punch-in-the-Face Hook & Top Hook Badge.
- Method A2 Real CDN Avatars.
- Zero Karaoke Subtitle Clutter.
- KHÔNG UPLOAD YOUTUBE (Lưu cục bộ chờ người dùng duyệt kiểm chứng).
"""
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

# Đường dẫn tư liệu đính kèm
post_media_img = str((root_dir / "scratch" / "dlinh_post_media.jpg").resolve())
avatars_dir = root_dir / "scratch" / "dlinh_avatars"

thread_data = {
    "post": {
        "username": "dlinh.org69",
        "time": "1 ngày",
        "content": "Được rồi, là t ẻ mạnh",
        # Hook 3s tát thẳng vào tình huống trớ trêu kèm awkward silence & meme boom
        "tts_content": "Đang yên đang lành nhắn tin hỏi người yêu về chưa... [pause:0.35] [sfx:record_scratch.wav] thì nhận lại câu: Em đừng có mà ỉa mạnh hiếp yếu! [sfx:vine_boom.wav] Được rồi... [pause:0.3] là tao ỉa mạnh dữ chưa?!",
        "avatar_url": str((avatars_dir / "post_avatar.jpg").resolve()),
        "post_image_url": post_media_img,
        "likes": "34.6K",
        "comments": "224",
        "reposts": "3.4K",
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+26%",
        "pitch": "+1Hz",
        "hook_badge": "KHI NGƯỜI YÊU BẬT UNIKEY LỖI... 💀🚽",
    },
    "comments": [
        {
            "username": "vietncct",
            "time": "1 ngày",
            "content": "\"có cô người yêu ỉa khỏe sẽ như thế nào\" =)))",
            "tts_content": "[sfx:bruh.wav] Có cô người yêu ỉa khỏe... thì sẽ như thế nào hả anh em? [pause:0.25] Đang lãng mạn mà tụt hết cả huyết áp!",
            "avatar_url": str((avatars_dir / "c_vietncct.jpg").resolve()),
            "likes": "850",
            "comments": "3",
            "reposts": "5",
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+25%",
            "pitch": "-2Hz",
        },
        {
            "username": "thaitungphan",
            "time": "1 ngày",
            "content": "Lần sau ỉa yếu lại nhé=)))",
            "tts_content": "Rút kinh nghiệm sâu sắc nha... [pause:0.3] Lần sau nhớ ỉa yếu yếu lại cho người yêu đỡ sợ nha má! [sfx:quack.wav]",
            "avatar_url": str((avatars_dir / "c_thaitungphan.jpg").resolve()),
            "likes": "52",
            "comments": "1",
            "reposts": "0",
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+27%",
            "pitch": "+0Hz",
        },
        {
            "username": "hidden_vn.official",
            "time": "1 ngày",
            "content": "Lực chiến bồn cầu",
            "tts_content": "[sfx:metal_pipe.wav] Quả này là lực chiến bồn cầu chắc phải cộng thêm chín nghìn chín trăm chín mươi chín giáp chứ đùa à!",
            "avatar_url": str((avatars_dir / "c_hidden.jpg").resolve()),
            "likes": "17",
            "comments": "2",
            "reposts": "0",
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+26%",
            "pitch": "+1Hz",
        },
        {
            "username": "minchou2000",
            "time": "1 ngày",
            "content": "-)) bộ m ỉa mạnh dữ lắm hả",
            "tts_content": "Ủa rồi... [pause:0.25] [sfx:huh.wav] bộ mày ỉa mạnh bạo lực dữ dằn lắm hả mà bạn trai phải lên tiếng van xin vậy?",
            "avatar_url": str((avatars_dir / "c_minchou.jpg").resolve()),
            "likes": "114",
            "comments": "2",
            "reposts": "1",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+25%",
            "pitch": "+1Hz",
        },
        {
            "username": "ngaaznn",
            "time": "1 ngày",
            "content": "Ỉa mạnh clm nó 😭",
            "tts_content": "Trời đất ơi... [sfx:emotional_damage.wav] ỉa mạnh, cười đau hết cả ruột với quả Unikey phản chủ này!",
            "avatar_url": str((avatars_dir / "c_ngaaznn.jpg").resolve()),
            "likes": "30",
            "comments": "1",
            "reposts": "0",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+26%",
            "pitch": "+2Hz",
        },
        {
            "username": "iah.yiel_",
            "time": "1 ngày",
            "content": "Ỉa mạnh thì kệ t",
            "tts_content": "Ủa rồi sao? [sfx:what.wav] Tao ỉa mạnh thì kệ tao chứ mắc mớ gì hiếp yếu ai đâu trời!",
            "avatar_url": str((avatars_dir / "c_iahyiel.jpg").resolve()),
            "likes": "25",
            "comments": "0",
            "reposts": "0",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+28%",
            "pitch": "+2Hz",
        },
        {
            "username": "sweetvenomx_x",
            "time": "1 ngày",
            "content": "Đọc mà t cười khùng🤣🤣🤣",
            "tts_content": "Nửa đêm lướt trúng quả thread này đọc mà cười khùng luôn á trời! [sfx:anime_wow.wav]",
            "avatar_url": str((avatars_dir / "c_sweetvenom.jpg").resolve()),
            "likes": "18",
            "comments": "0",
            "reposts": "0",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+25%",
            "pitch": "+1Hz",
        },
    ]
}

def main():
    print("🎬 === BẮT ĐẦU SẢN XUẤT VIDEO THREADS (KIỂM CHỨNG BỘ SFX & BGM MỚI) ===")
    job_id = "job_thread_dlinh_ia_manh"
    
    res = build_threads_video(
        thread_data=thread_data,
        job_id=job_id,
        theme="dark",
        bgm_style="comedy_sneaky",   # Sneaky Snitch BGM
        bgm_volume=0.38,             # Âm lượng rõ nét, bắt tai
        enable_ducking=True,         # Tự động hạ nhạc khi có thoại, dâng nhạc khi im lặng
        enable_spring_pop=True,      # Nảy thẻ lò xo vật lý
        enable_karaoke=False,        # Loại bỏ 100% chữ phụ đề đáy màn hình
        publish_youtube=False,       # TUYỆT ĐỐI KHÔNG UPLOAD YOUTUBE - CHỜ DUYỆT
    )
    
    print("\n🎉 === HOÀN THÀNH SẢN XUẤT VIDEO LOCAL ===")
    print(f"File video thành phẩm: {res.get('video_path')}")
    print("Trạng thái YouTube: KHÔNG TẢI LÊN (Lưu cục bộ chờ duyệt)")

if __name__ == "__main__":
    main()

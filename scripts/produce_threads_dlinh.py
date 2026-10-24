"""
Script sản xuất video Threads v2 cho bài viết @dlinh.org69 ("Được rồi, là t ẻ mạnh")
Kênh: HanShin
Định dạng: 9:16 Dọc (1080x1920) @ 60 FPS
NÂNG CẤP V2:
- 100% Đồng bộ Audio-Visual Punchline: Âm thanh Meme SFX và Meme Sticker nảy lò xo xuất hiện đồng bộ ở cuối câu đùa.
- Kho Sticker Meme: The Rock, Doge Bruh, Clown Quack, Cat What, Gibbon Huh, Grumpy Cat Toang,...
- Khắc phục triệt để mất chữ / nuốt âm: Bổ sung 0.35s tail padding và từ điển Teen-code toàn diện.
- KHÔNG UPLOAD YOUTUBE (Lưu cục bộ chờ người dùng kiểm tra).
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

# Đường dẫn tư liệu đính kèm
post_media_img = str((root_dir / "scratch" / "dlinh_post_media.jpg").resolve())
avatars_dir = root_dir / "scratch" / "dlinh_avatars"

thread_data = {
    "post": {
        "username": "dlinh.org69",
        "time": "1 ngày",
        "content": "Được rồi, là t ẻ mạnh",
        # Hook 3s tát thẳng vào tình huống trớ trêu kèm awkward silence & meme boom ở cuối câu
        "tts_content": "Đang yên đang lành nhắn tin hỏi người yêu về chưa... [pause:0.35] thì nhận lại câu: Em đừng có mà ỉa mạnh hiếp yếu! [pause:0.3] Được rồi... là tao ỉa mạnh dữ chưa?!",
        "avatar_url": str((avatars_dir / "post_avatar.jpg").resolve()),
        "post_image_url": post_media_img,
        "likes": "34.6K",
        "comments": "224",
        "reposts": "3.4K",
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+24%",
        "pitch": "+1Hz",
        "sfx": "vine_boom.wav",
        "meme": "the_rock",
        "shake": True,
        "hook_badge": "KHI NGƯỜI YÊU BẬT UNIKEY LỖI... 💀🚽",
    },
    "comments": [
        {
            "username": "vietncct",
            "time": "1 ngày",
            "content": "\"có cô người yêu ỉa khỏe sẽ như thế nào\" =)))",
            "tts_content": "Có cô người yêu ỉa khỏe... thì sẽ như thế nào hả anh em? [pause:0.25] Đang lãng mạn mà tụt hết cả huyết áp!",
            "avatar_url": str((avatars_dir / "c_vietncct.jpg").resolve()),
            "likes": "850",
            "comments": "3",
            "reposts": "5",
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+24%",
            "pitch": "-2Hz",
            "sfx": "bruh.wav",
            "meme": "side_eye_dog",
        },
        {
            "username": "thaitungphan",
            "time": "1 ngày",
            "content": "Lần sau ỉa yếu lại nhé=)))",
            "tts_content": "Rút kinh nghiệm sâu sắc nha... [pause:0.3] Lần sau nhớ ỉa yếu yếu lại cho người yêu đỡ sợ nha má!",
            "avatar_url": str((avatars_dir / "c_thaitungphan.jpg").resolve()),
            "likes": "52",
            "comments": "1",
            "reposts": "0",
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+25%",
            "pitch": "+0Hz",
            "sfx": "quack.wav",
            "meme": "pop_cat",
        },
        {
            "username": "hidden_vn.official",
            "time": "1 ngày",
            "content": "Lực chiến bồn cầu",
            "tts_content": "Quả này là lực chiến bồn cầu chắc phải cộng thêm chín nghìn chín trăm chín mươi chín giáp chứ đùa à!",
            "avatar_url": str((avatars_dir / "c_hidden.jpg").resolve()),
            "likes": "17",
            "comments": "2",
            "reposts": "0",
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+25%",
            "pitch": "+1Hz",
            "sfx": "metal_pipe.wav",
            "meme": "metal_pipe",
            "shake": True,
        },
        {
            "username": "minchou2000",
            "time": "1 ngày",
            "content": "-)) bộ m ỉa mạnh dữ lắm hả",
            "tts_content": "Ủa rồi... [pause:0.25] bộ mày ỉa mạnh bạo lực dữ dằn lắm hả mà bạn trai phải lên tiếng van xin vậy?",
            "avatar_url": str((avatars_dir / "c_minchou.jpg").resolve()),
            "likes": "114",
            "comments": "2",
            "reposts": "1",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+24%",
            "pitch": "+1Hz",
            "sfx": "huh.wav",
            "meme": "huh_cat",
        },
        {
            "username": "ngaaznn",
            "time": "1 ngày",
            "content": "Ỉa mạnh clm nó 😭",
            "tts_content": "Trời đất ơi... ỉa mạnh, cười đau hết cả ruột với quả Unikey phản chủ này!",
            "avatar_url": str((avatars_dir / "c_ngaaznn.jpg").resolve()),
            "likes": "30",
            "comments": "1",
            "reposts": "0",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+25%",
            "pitch": "+2Hz",
            "sfx": "emotional_damage.wav",
            "meme": "emotional_damage",
        },
        {
            "username": "iah.yiel_",
            "time": "1 ngày",
            "content": "Ỉa mạnh thì kệ t",
            "tts_content": "Ủa rồi sao? Tao ỉa mạnh thì kệ tao chứ mắc mớ gì hiếp yếu ai đâu trời!",
            "avatar_url": str((avatars_dir / "c_iahyiel.jpg").resolve()),
            "likes": "25",
            "comments": "0",
            "reposts": "0",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+25%",
            "pitch": "+2Hz",
            "sfx": "what.wav",
            "meme": "disappointed_fan",
        },
        {
            "username": "sweetvenomx_x",
            "time": "1 ngày",
            "content": "Đọc mà t cười khùng🤣🤣🤣",
            "tts_content": "Nửa đêm lướt trúng quả thread này đọc mà cười khùng luôn á trời!",
            "avatar_url": str((avatars_dir / "c_sweetvenom.jpg").resolve()),
            "likes": "18",
            "comments": "0",
            "reposts": "0",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+24%",
            "pitch": "+1Hz",
            "sfx": "anime_wow.wav",
            "meme": "banana_cat",
        },
    ]
}


def main():
    print("🎬 === BẮT ĐẦU RE-RENDER VIDEO THREADS (PHIÊN BẢN V3: CLIP MEME VIRAL CHUẨN TIKTOK) ===")
    job_id = "job_thread_dlinh_v3_real_memes"

    res = build_threads_video(
        thread_data=thread_data,
        job_id=job_id,
        theme="dark",
        bgm_style="comedy_sneaky",   # Sneaky Snitch BGM
        bgm_volume=0.38,             # Âm lượng rõ nét, bắt tai
        enable_ducking=True,         # Tự động hạ nhạc khi có thoại, dâng nhạc khi im lặng
        enable_spring_pop=True,      # Nảy thẻ lò xo vật lý
        enable_karaoke=False,        # Loại bỏ 100% chữ phụ đề đáy màn hình
        publish_youtube=False,       # TUYỆT ĐỐI KHÔNG UPLOAD YOUTUBE THEO YÊU CẦU
    )

    out_mp4 = Path(res.get("video_path"))
    print("\n🎉 === HOÀN THÀNH SẢN XUẤT VIDEO LOCAL ===")
    print(f"File video thành phẩm: {out_mp4}")
    print("Trạng thái YouTube: KHÔNG TẢI LÊN (Lưu cục bộ chờ duyệt)")

    # Trích xuất frames mẫu tại từng thời điểm Punchline Meme Video
    brain_dir = Path(r"C:\Users\tranh\.gemini\antigravity\brain\0acabd2b-aa48-4bc8-a2e8-c7a0b0e11f56")
    if out_mp4.exists() and brain_dir.exists():
        # Danh sách preview cần trích xuất (tên file, mốc giây xấp xỉ)
        previews = [
            ("v3_preview_the_rock.jpg", 7.5, "The Rock"),
            ("v3_preview_side_eye_dog.jpg", 14.0, "Side-Eye Dog"),
            ("v3_preview_pop_cat.jpg", 20.0, "Pop Cat"),
            ("v3_preview_metal_pipe.jpg", 26.5, "Metal Pipe"),
            ("v3_preview_huh_cat.jpg", 33.0, "Huh Cat"),
            ("v3_preview_emotional_damage.jpg", 38.5, "Emotional Damage"),
            ("v3_preview_disappointed_fan.jpg", 43.5, "Disappointed Fan"),
            ("v3_preview_banana_cat.jpg", 48.0, "Banana Cat"),
        ]
        for fname, sec, label in previews:
            out_p = brain_dir / fname
            cmd = ["ffmpeg", "-y", "-ss", f"{sec:.1f}", "-i", str(out_mp4), "-vframes", "1", "-q:v", "2", str(out_p)]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if out_p.exists():
                print(f"📸 Đã trích xuất ảnh xem trước ({label}): {out_p.name}")


if __name__ == "__main__":
    main()

"""
Script sản xuất video Threads cho bài viết @hoangbao5441
("tôi nếu bị cô xếp ngồi cạnh đứa không quen")
Kênh: HanShin
Định dạng: 9:16 Dọc (1080x1920) @ 60 FPS
Video nền: Subway Surfers (subway_surfers.mp4)
Áp dụng đầy đủ 10 Quy tắc Xưởng 5 (AGENTS.md):
- Dark Mode AMOLED (#101010) chiều rộng 820px, bo góc 18px.
- Avatar thật từ CDN Instagram.
- Voice x1.25 (Edge-TTS) lọc sạch icon và chuẩn hóa ngữ âm tiếng Anh.
- Chỉ chọn lọc 2 meme viral (Side-Eye, The Rock) đồng bộ tại điểm rơi punchline, không lạm dụng.
- Nhạc nền Sneaky Snitch có auto-ducking sidechain rõ nét.
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
post_media_img = str((root_dir / "scratch" / "hoangbao_post_media.jpg").resolve())
avatars_dir = root_dir / "scratch" / "hoangbao_avatars"
bg_subway = str((root_dir / "workshops" / "workshop-threads" / "assets" / "backgrounds" / "subway_surfers.mp4").resolve())

thread_data = {
    "post": {
        "username": "hoangbao5441",
        "time": "3 giờ",
        "content": "tôi nếu bị cô xếp ngồi cạnh đứa không quen",
        # Hook 3s punch-in-the-face:
        "tts_content": "Cảm giác của tôi mỗi khi bị cô giáo xếp chỗ ngồi cạnh một đứa lạ hoắc lạ huơ... [pause:0.35] Hai thằng ngồi im re, mặt đơ như tượng Talking Tom với Ben trên bản tin thời sự luôn á trời!",
        "avatar_url": str((avatars_dir / "post_avatar.jpg").resolve()),
        "post_image_url": post_media_img,
        "likes": "5.1K",
        "comments": "58",
        "reposts": "1.3K",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+25%",
        "pitch": "-1Hz",
        "sfx": "vine_boom.wav",
        "meme": "huh_cat",    # Clip Meme Viral 1: Huh Cat ngơ ngác cạn lời
        "punchline_offset": 7.0,
        "shake": True,
        "hook_badge": "🔥 KHI BỊ CÔ XẾP CHỖ CẠNH ĐỨA LẠ HOẮC... 💀",
    },
    "comments": [
        {
            "username": "tran.g8463",
            "time": "3 giờ",
            "content": "Xong đc 1 tuần nói như máy :))",
            "tts_content": "Chuẩn luôn! [pause:0.25] Ban đầu thì ngại ngùng không dám thở mạnh, xong đúng một tuần là hai cái mỏ nói liến thoắng như cái máy khâu!",
            "avatar_url": str((avatars_dir / "c_trang.jpg").resolve()),
            "likes": "52",
            "comments": "1",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+25%",
            "pitch": "+2Hz",
            "sfx": "pop.wav",
            # Không chèn meme video để video thanh thoát
        },
        {
            "username": "echiwibu",
            "time": "2 giờ",
            "content": 'hồi trc t bị đổi chỗ ngồi vs cái th mà t k quen, mà t ngồi t chán quá t hỏi thăm nó, r dhs nó blhđ tôi ae ạ. T hỏi mấy câu thăm hỏi đơn giản th "m đi ỉa ch", "m đi đái ch", "m bt nch k", "m có bị câm k", "giả sử m đi ỉa mà...", vca t chỉ cho nó tận hưởng giọng ca vàng tuyệt vời của t th',
            "tts_content": "Hồi trước tao cũng bị đổi chỗ ngồi với một thằng không quen. Ngồi chán quá tao quay sang hỏi thăm nó mấy câu thân mật: Mày đi vệ sinh chưa? [pause:0.25] Mày biết nói chuyện không? Giả sử mày đi mà bị kẹt giấy thì... [pause:0.35] Đã vậy tao còn hát tặng nó giọng ca vàng oanh tạc nữa. Thế quái nào nó lại nổi điên tác động vật lý tao anh em ạ!",
            "avatar_url": str((avatars_dir / "c_echiwibu.jpg").resolve()),
            "likes": "13",
            "comments": "1",
            "voice": "vi-VN-NamMinhNeural",
            "rate": "+25%",
            "pitch": "+1Hz",
            "sfx": "emotional_damage.wav",
            "meme": "the_rock",  # Clip Meme Viral 2: The Rock nhướng mày hoang mang
            "punchline_offset": 15.2,
            "shake": True,
        },
        {
            "username": "chiyurasa_1004_",
            "time": "2 giờ",
            "content": "xong mấy hôm nữa nói đến độ bà cô muốn tách tiếp luôn =)))",
            "tts_content": "Xong được vài hôm nữa thì nói nhiều đến độ bà cô chủ nhiệm muốn tiền đình, [pause:0.3] phải tức tốc tách hai đứa ra hai góc lớp lần nữa luôn á trời!",
            "avatar_url": str((avatars_dir / "c_chiyurasa.jpg").resolve()),
            "likes": "7",
            "voice": "vi-VN-HoaiMyNeural",
            "rate": "+25%",
            "pitch": "+1Hz",
            "sfx": "sad_trombone.wav",
            # Kết thúc gọn gàng, vui nhộn
        },
    ],
    "youtube": {
        "title": "Khi Bị Cô Giáo Xếp Ngồi Cạnh Đứa Lạ Hoắc... 💀 #Shorts #Threads #HaiHuoc",
        "description": "Cảm giác bị đổi chỗ ngồi cạnh đứa không quen: Ban đầu thì im re như Talking Tom và Ben, sau một tuần thì nói đến mức cô giáo đòi tách tiếp =))))\n\nTheo dõi kênh @HanShin-g8i để nghe thêm nhiều câu chuyện Threads hài hước, drama học đường và đời sống nhé!\n#HanShin #Threads #Shorts #HaiHuoc #HocDuong #SubwaySurfers #TikTok #Reels",
        "tags": ["HanShin", "Threads", "Shorts", "HaiHuoc", "HocDuong", "SubwaySurfers", "TikTok", "Reels", "HaiHuocGenZ"],
    }
}


def main():
    print("🎬 === BẮT ĐẦU SẢN XUẤT VIDEO THREADS @hoangbao5441 (SUBWAY SURFERS) ===")
    job_id = "job_thread_hoangbao_ban_cung_ban"

    res = build_threads_video(
        thread_data=thread_data,
        job_id=job_id,
        theme="dark",
        background_path=bg_subway,  # Nền Subway Surfers theo yêu cầu
        bgm_style="comedy_sneaky",   # Sneaky Snitch BGM
        bgm_volume=0.38,             # Âm lượng rõ nét, bắt tai
        enable_ducking=True,         # Tự động hạ nhạc khi có thoại, dâng nhạc khi im lặng
        enable_spring_pop=True,      # Nảy thẻ lò xo vật lý
        enable_karaoke=False,        # Loại bỏ 100% chữ phụ đề đáy màn hình
        publish_youtube=False,       # Chưa đăng Youtube (theo yêu cầu mặc định của task)
    )

    out_mp4 = Path(res.get("video_path"))
    print("\n🎉 === HOÀN THÀNH SẢN XUẤT VIDEO THREADS ===")
    print(f"File video thành phẩm: {out_mp4}")

    # Trích xuất frames preview
    brain_dir = Path(r"C:\Users\tranh\.gemini\antigravity\brain\0acabd2b-aa48-4bc8-a2e8-c7a0b0e11f56")
    if out_mp4.exists() and brain_dir.exists():
        p1 = brain_dir / "hoangbao_final_post.jpg"
        p2 = brain_dir / "hoangbao_final_huh_cat.jpg"
        p3 = brain_dir / "hoangbao_final_rock.jpg"
        # Extract at 4.0s, 8.0s, and 34.5s
        cmd1 = ["ffmpeg", "-y", "-ss", "00:00:04.0", "-i", str(out_mp4), "-vframes", "1", "-q:v", "2", str(p1)]
        cmd2 = ["ffmpeg", "-y", "-ss", "00:00:08.0", "-i", str(out_mp4), "-vframes", "1", "-q:v", "2", str(p2)]
        cmd3 = ["ffmpeg", "-y", "-ss", "00:00:34.5", "-i", str(out_mp4), "-vframes", "1", "-q:v", "2", str(p3)]
        subprocess.run(cmd1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(cmd2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(cmd3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if p1.exists():
            print(f"📸 Trích xuất preview: {p1.name}")
        if p2.exists():
            print(f"📸 Trích xuất preview: {p2.name}")
        if p3.exists():
            print(f"📸 Trích xuất preview: {p3.name}")


if __name__ == "__main__":
    main()

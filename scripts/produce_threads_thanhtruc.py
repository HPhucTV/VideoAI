"""
Xưởng 5: Production Script cho bài viết Threads thanhtrucdayne (Hội đồng quản trị & Cô gái xui xẻo)
URL: https://www.threads.com/@thanhtrucdayne/post/DewswDIFILK
Kênh phát hành: HanShin (@HanShin-g8i)
Chuẩn: Method A2, Hook 3s Punch-in-the-Face, Awkward Silence & Comedy Voice Acting
"""
import sys
from pathlib import Path

# Ensure UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "workshops" / "workshop-threads" / "src"))

from pipeline import build_threads_video

def main():
    meme_img = ROOT / "workshops" / "workshop-threads" / "assets" / "post_meme_thanhtruc.jpg"

    thread_data = {
        "url": "https://www.threads.net/@thanhtrucdayne/post/DewswDIFILK",
        "post": {
            "username": "thanhtrucdayne",
            "time": "18 giờ",
            "hook_badge": "KHI BẠN THÂN CHỬI NGƯỜI YÊU BẠN... 🤡",
            "content": "Xin lỗi hđqt\nCô gái xui xẻo đó là t 🙂",
            "tts_content": "Đang ngồi hóng bạn thân chửi thằng Huy hãm lờ đi tỏ tình ai đó... [sfx:record_scratch.wav:0.35] [pause:0.35] ...và phát hiện ra cô gái xui xẻo đó chính là mình?! Con bạn gửi tin nhắn vào nhóm: 'Vãi, nãy tao thấy thằng Huy hãm lờ tỏ tình ai á, bóng bay hoa hoét các thứ, đéo biết cô gái nào mà xui xẻo vậy... nhưng mà cũng đồng ý rồi thì phải!' [pause:0.4] [sfx:cricket.wav] Và tao phải lên thét thú tội: Xin lỗi hội đồng quản trị... Cô gái xui xẻo đó chính là tao 🙂",
            "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/722665770_18108500269785617_8768561720511085565_n.jpg?_nc_cat=1&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=sP2SEPag4sYQ7kNvwFGWmUW&_nc_oc=Adp6uebxapZfzuKC55qToXnmcr4LP4ouqFI_DlLM7wrn4j4SR1G1iXCtavoxgSQkznPx6gr_1M3Cz1wqRc2MRL2d&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=y3M_FU_nG23uQnSFxSTnCQ&_nc_ss=7b289&oh=00_AQNvHgOUSDL4kpWdILebmflPDRUMpLxdhhpVbt3rAipArw&oe=6ADFAB0C",
            "post_image_url": str(meme_img.resolve()) if meme_img.exists() else "https://instagram.fsgn2-6.fna.fbcdn.net/v/t51.82787-15/860844022_18132334360785617_4023062642470516522_n.jpg?stp=cp6_dst-jpg_e35_tt6&_nc_cat=1&ig_cache_key=NDAxMjkwNDA4MzkyNTI3MTI0Mg%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=RKSsXXe46cwQ7kNvwHiUusO&_nc_oc=AdrIkDF-ofsyShGcTtYSGlimyB-UZ6-dL2XHDdkdY2SSoFnobRVws80Jt027sbVrOJonBn4XDDmhgz5s-9CKcewc&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=instagram.fsgn2-6.fna&_nc_gid=TYYWqBdhNmtgEfz4AJQEBA&_nc_ss=7a20f&oh=00_AQM2_-5iuPE3ZeVZShj7PO1g65ih0ANJJQRy-t7bTF-_cw&oe=6ADFBDE6",
            "likes": "3,8K",
            "comments": "33",
            "reposts": "61",
            "voice": "vi-VN-HoaiMyNeural",
            "sfx": "pop.wav",
        },
        "comments": [
            {
                "username": "_mcshp",
                "time": "18 giờ",
                "content": "Tr ơi nó biết được nó lên tăng xông 🤡",
                "tts_content": "Trời đất ơi, bạn thân mà nó biết được chắc nó tăng xông xỉu ngang tại chỗ luôn á má! 🤡",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.89012-19/573323465_1219825463302212_7278921664109726296_n.jpg?stp=dst-jpg_tt6&_nc_cat=1&ig_cache_key=YW5vbnltb3VzX3Byb2ZpbGVfcGlj.3-ccb7-5&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=0y1PG7QdnsUQ7kNvwFiMl5f&_nc_oc=Adra46N9FM-iZr-q3l80XShtIMtyxdmMoOGoXYTZYzEGc8Md0-cXcEImlo2uSMb3cUYAYRklJV5TaBNvXvBhWbYY&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=y3M_FU_nG23uQnSFxSTnCQ&_nc_ss=7b289&oh=00_AQNcx4dBIoPUoDElXUqg8UrcEJtJoET8nDqY_Waqf54pFg&oe=6ADFC022",
                "likes": "230",
                "comments": "4",
                "reposts": "1",
                "voice": "vi-VN-NamMinhNeural",
                "sfx": "vine_boom.wav",
                "shake": True,
            },
            {
                "username": "yramd.i6",
                "time": "18 giờ",
                "content": "Ê bcuoi vc",
                "tts_content": "Ê mắc cười vãi chưởng, cứu tao với tụi bây ơi! [sfx:ding.wav]",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/846156825_18117773287904381_4633244431539777063_n.jpg?_nc_cat=105&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=LPu7yKAzKFAQ7kNvwGBx_lG&_nc_oc=Adqy0en-ll9QxAFlkNtYYtkC4xmnRVKMG7KH2KUwU83bQniT-E_549hXeBOBxhROKCfYdp1U0tPVJvea3Sz8fhIr&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=y3M_FU_nG23uQnSFxSTnCQ&_nc_ss=7b289&oh=00_AQOMTj-7xH1ZX2m47B1HqF0ki7o4Cvw_5Utur1hy5m5DNg&oe=6ADF914E",
                "likes": "20",
                "comments": "0",
                "reposts": "0",
                "voice": "vi-VN-HoaiMyNeural",
                "sfx": "ding.wav",
                "shake": False,
            },
            {
                "username": "jin28699",
                "time": "17 giờ",
                "content": "@mitien.vely_ quả hội đồng quản trị mất việc 🙂",
                "tts_content": "Quả này hội đồng quản trị chính thức giải tán và sa thải con bạn luôn chứ tư vấn gì nữa! [sfx:sad_trombone.wav]",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/748005037_17978852739103058_2042745031713747766_n.jpg?stp=dst-jpg_s206x206_tt6&_nc_cat=110&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy45NjAuQzMifQ%3D%3D&_nc_ohc=yCsaJU9m0VcQ7kNvwGbDYiL&_nc_oc=Adr59w_DrqGPv0EZ9nDtXjH3CxF1R39IHppBpmt4imIS3WGJ_vdJULAzZ1fKJBroZl-C7R2iHj-ZHwRl7V0W7oNy&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=y3M_FU_nG23uQnSFxSTnCQ&_nc_ss=7b289&oh=00_AQPPl1ZqhEF4BoZQbogfZ825TIlnuD0mqgNUzUXflGdwkw&oe=6ADF9755",
                "likes": "15",
                "comments": "1",
                "reposts": "0",
                "voice": "vi-VN-NamMinhNeural",
                "sfx": "pop.wav",
                "shake": False,
            },
            {
                "username": "_dhwli",
                "time": "17 giờ",
                "content": "rồi biết nhà nào sáng nhất đêm nay 😞",
                "tts_content": "Rồi xong, biết nhà nào tối nay sáng nhất đêm nay rồi đó nha! [sfx:whoosh.wav]",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/778140200_18090479297164682_5980607007481156132_n.jpg?_nc_cat=109&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=92CY_soLKC4Q7kNvwHe-y2g&_nc_oc=Adqte5ZwhB57gTqMiSHAnyyl1k7JGw-2EpGcldDxenttZYZHIIdXeg3K5CAinb0M_TeQiE850oyC5t-cxOYGa_Si&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=y3M_FU_nG23uQnSFxSTnCQ&_nc_ss=7b289&oh=00_AQOHRWpyVNpu0fzRX3I1-niLAGllPxZS_9XtgLCg6Cqe-w&oe=6ADFB646",
                "likes": "12",
                "comments": "0",
                "reposts": "0",
                "voice": "vi-VN-HoaiMyNeural",
                "sfx": "whoosh.wav",
                "shake": False,
            },
            {
                "username": "krix.iew",
                "time": "17 giờ",
                "content": "nó mà biết đi á nghe",
                "tts_content": "Nó mà biết được sự thật là đi luôn á nghe bà nội, hết cứu! [sfx:vine_boom.wav]",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/755810027_18080655947294988_6059882282208066021_n.jpg?_nc_cat=100&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=7HbJyexBTLkQ7kNvwEVIa5H&_nc_oc=AdqZRSBjreh_EwdKwI4F0JkDcPK4K-WJF8mfdHyv-_dqtQEy1FrNvBHUuCZnt-7b0eWLn8BsU4dK1YKKWzHd4NQL&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=y3M_FU_nG23uQnSFxSTnCQ&_nc_ss=7b289&oh=00_AQPIdwjVZJHC-fRrY2qN-3U1ebCuWgQ9d4ApYfb4ymIhXg&oe=6ADFA17D",
                "likes": "8",
                "comments": "0",
                "reposts": "0",
                "voice": "vi-VN-NamMinhNeural",
                "sfx": "vine_boom.wav",
                "shake": True,
            },
            {
                "username": "huyvt2108",
                "time": "16 giờ",
                "content": "Tội nghiệp mấy thằng tên Huy",
                "tts_content": "Ủa rồi mấy thằng tên Huy tụi tao làm gì sai mà đi đâu cũng bị tế vậy trời?! [sfx:bruh.wav]",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.75761-19/500522744_17845711710488888_7319568935053218129_n.jpg?_nc_cat=100&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=anlU8CmGmqYQ7kNvwGr9ZTd&_nc_oc=Adrsup0_edlKMzR4ErGNic6PFsrbpf6VgrsP6JeV-iC2hG0FDIoA3dWrMWLPJWEq3bX7cKrGa6XBg-1VZ21GQg-J&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=y3M_FU_nG23uQnSFxSTnCQ&_nc_ss=7b289&oh=00_AQPoOZXbr6jbPQsBtqghmBYR8omjr_h_rFTIlRWuA5B8EQ&oe=6ADFB15C",
                "likes": "20",
                "comments": "2",
                "reposts": "0",
                "voice": "vi-VN-NamMinhNeural",
                "sfx": "bruh.wav",
                "shake": False,
            },
            {
                "username": "iub.eiuk",
                "time": "16 giờ",
                "content": "Tao cho nyc mượn tiền mà giấu hdqt nè huhu",
                "tts_content": "Tao cũng lén cho người yêu cũ mượn tiền mà giấu hội đồng quản trị nè, đồng cảnh ngộ hu hu! [sfx:vine_boom.wav]",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.89012-19/573323465_1219825463302212_7278921664109726296_n.jpg?stp=dst-jpg_tt6&_nc_cat=1&ig_cache_key=YW5vbnltb3VzX3Byb2ZpbGVfcGlj.3-ccb7-5&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=0y1PG7QdnsUQ7kNvwFiMl5f&_nc_oc=Adra46N9FM-iZr-q3l80XShtIMtyxdmMoOGoXYTZYzEGc8Md0-cXcEImlo2uSMb3cUYAYRklJV5TaBNvXvBhWbYY&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=y3M_FU_nG23uQnSFxSTnCQ&_nc_ss=7b289&oh=00_AQNcx4dBIoPUoDElXUqg8UrcEJtJoET8nDqY_Waqf54pFg&oe=6ADFC022",
                "likes": "18",
                "comments": "1",
                "reposts": "0",
                "voice": "vi-VN-HoaiMyNeural",
                "sfx": "vine_boom.wav",
                "shake": True,
            }
        ]
    }

    print("🚀 Bắt đầu sản xuất video Threads (Comedy & Viral Hook) cho kênh HanShin...")
    mc_bg = ROOT / "workshops" / "workshop-threads" / "assets" / "backgrounds" / "minecraft_parkour.mp4"
    result = build_threads_video(
        thread_data=thread_data,
        job_id="job_thread_thanhtruc_hdqt",
        background_path=mc_bg if mc_bg.exists() else None,
        theme="dark",
        enable_karaoke=False,
        publish_youtube=False,
        privacy="unlisted"
    )

    print("\n✅ HOÀN TẤT XUẤT BẢN THREADS VIDEO!")
    print(f"File video: {result.get('video_path')}")
    print(f"Tổng số phân đoạn: {result.get('total_segments')}")
    if result.get("youtube"):
        print(f"YouTube URL: {result['youtube'].get('url')}")
        print(f"YouTube Privacy: {result['youtube'].get('privacy')}")

if __name__ == "__main__":
    main()

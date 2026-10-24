"""
Xưởng 5: Production Script cho bài viết Threads anmei_32 (2K9 V-ACT)
Kênh phát hành: HanShin (@HanShin-g8i)
Chuẩn: Method A2 (Avatar thật từ Instagram CDN, AMOLED #101010, Watermark tâm chuẩn, Clean Edge-TTS)
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
    thread_data = {
        "url": "https://www.threads.net/@anmei_32/post/Dev0YS_gQBK",
        "post": {
            "username": "anmei_32",
            "time": "1 ngày",
            "content": "Học sinh 2K9 dạo gần đây:\nKiến thức lớp 10 chưa chắc\nLớp 11 chưa nhớ\nLớp 12 không hiểu\nVaCT thì chật vật...",
            "tts_content": "Học sinh hai ca chín dạo gần đây: Kiến thức lớp mười chưa chắc, lớp mười một chưa nhớ, lớp mười hai không hiểu, vê át thì chật vật...",
            "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/724004963_18104376163856712_985720369631380623_n.jpg?_nc_cat=109&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=98PADl1S3OwQ7kNvwFPIyly&_nc_oc=AdqvmZUeKSuH7D-CgmmQRcNDb7bGLf74rg0dRpox_DtEyY0VnA3mM2YFMepaVY6EQgYB0TIrThEXmzqc-i4QF2dz&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=XYC0kNwzVz6jA2Aj26Jzxw&_nc_ss=7b289&oh=00_AQMsFBIMAVuaSB6usHsVTestsohwtCU_u2B8Q-ppcfvFmA&oe=6ADFBD1F",
            "post_image_url": "https://instagram.fsgn2-5.fna.fbcdn.net/v/t51.82787-15/856657954_18127022626856712_1478555627435164593_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=107&_nc_map=urlgen_bucketless&ig_cache_key=NDAxMjY1NjA4NTIzMTI2NjUyOA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuNjQ4LnNkci5yZWd1bGFyX3Bob3RvLkMzIn0%3D&_nc_ohc=HywkAkb9kRIQ7kNvwFMDzzR&_nc_oc=Adp9N7LhG01uTJxIHUDEFGApyc_1ifsAnCXxp7NQUq_KXYM2ocTG1-AIEeFngmS7TL96Qm7FMlGqD67xr_3L77kW&_nc_zt=23&_nc_ht=instagram.fsgn2-5.fna&_nc_gid=3d3kIqkTKSdytuCeK6V-TQ&_nc_ss=7b289&oh=00_AQO_tWgi2p5KYN92XHYlrXGEj1oM2xd7TLSe_X8JZyEDQA&oe=6ADF8C15",
            "likes": "5,6K",
            "comments": "95",
            "reposts": "1K",
            "voice": "vi-VN-HoaiMyNeural",
        },
        "comments": [
            {
                "username": "xeluvuotdeo.haivan",
                "time": "1 ngày",
                "content": "Má y chang",
                "tts_content": "Má, y chang luôn!",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/774945682_17949208362253085_4058279361953603931_n.jpg?_nc_cat=103&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=kzCs4EYsZQUQ7kNvwGn3c_K&_nc_oc=Adq6sh-TU7ZBfLfhQxhlMx4s7Td616eEzjk2AVCKLU2P3u3jIWibB-dhTW4mxboGA7V7syGrBtM4-T2zGfJ0szPT&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=XYC0kNwzVz6jA2Aj26Jzxw&_nc_ss=7b289&oh=00_AQMWKtIgDpUZWnwJbnCw4PRHbvfzSNz40IMHE_DvEjog5Q&oe=6ADFAFC9",
                "likes": "12",
                "comments": "0",
                "reposts": "0",
                "voice": "vi-VN-NamMinhNeural",
            },
            {
                "username": "meohoang.huhong",
                "time": "1 ngày",
                "content": "Mấy câu khoa học mà quăng mình cái hình bắt nhớ kiến thức làm là bỏ đi em ko có ra đâu 💔",
                "tts_content": "Mấy câu khoa học mà quăng mình cái hình bắt nhớ kiến thức làm là bỏ đi, em không có ra đâu!",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/831567778_17948674683295232_7273424442233839134_n.jpg?stp=dst-jpg_s206x206_tt6&_nc_cat=105&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4zOTkuQzMifQ%3D%3D&_nc_ohc=TyesROktkrUQ7kNvwEPALtR&_nc_oc=Adq6g0ebCE20cBKQni16jowtgsd75mvEJr3qVeeru0WSzYUXkgMEFSmGd0SlsJgyBAIRCY4VtfTHWRCGicswJof4&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=XYC0kNwzVz6jA2Aj26Jzxw&_nc_ss=7b289&oh=00_AQMqzJIg5o27FHO-k4rtyhURwgtD4gmJu4WgD_iugoMcXw&oe=6ADF8C46",
                "likes": "31",
                "comments": "3",
                "reposts": "1",
                "voice": "vi-VN-HoaiMyNeural",
            },
            {
                "username": "dangcapquasocacconso",
                "time": "22 giờ",
                "content": "Hiểu kì hai hổng kì một",
                "tts_content": "Hiểu kì hai, hổng kì một!",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/645553743_17910680700342824_423575371031498006_n.jpg?stp=dst-jpg_s206x206_tt6&_nc_cat=106&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xMDgwLkMzIn0%3D&_nc_ohc=YyQcJtafpSMQ7kNvwEC-jWj&_nc_oc=AdorhwJysA7pgfKl_YVfcszRUXU7ShnZSoJpA9sJkujMa1vqoJD6tmqBkYB3M8xKR440Hr4NEtG5abc4xsCVEXLY&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=XYC0kNwzVz6jA2Aj26Jzxw&_nc_ss=7b289&oh=00_AQMkQ_2d_wX2XYqUh3fCstSm2ui5ptZbzvGRlIBOMpRFwA&oe=6ADF9007",
                "likes": "1",
                "comments": "0",
                "reposts": "0",
                "voice": "vi-VN-NamMinhNeural",
            },
            {
                "username": "mb.an29",
                "time": "21 giờ",
                "content": "hiểu lớp này rớt mẹ lớp khc",
                "tts_content": "Hiểu lớp này rớt mẹ lớp khác!",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/656067044_17877438399540788_8956596901959919770_n.jpg?_nc_cat=104&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=u1-UcrRntEwQ7kNvwGQhJc3&_nc_oc=Adr2TrW5CywEEooG1fLXIzXo0DETxi_kq4TB0lj9cGOpF--d24nRRwJBMj6A387SMTo-_vSGkdJ0ObtUdnE7n3wD&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=XYC0kNwzVz6jA2Aj26Jzxw&_nc_ss=7b289&oh=00_AQMVO_CtbAvhUGgoJ-g_eFcLFU4sE0FYqBO9JCV8_P8uCw&oe=6ADFB53D",
                "likes": "6",
                "comments": "1",
                "reposts": "0",
                "voice": "vi-VN-HoaiMyNeural",
            },
            {
                "username": "thehehe417",
                "time": "21 giờ",
                "content": "học tích phân thì quên tiệm cận. lim liếc cx quên sạch r",
                "tts_content": "Học tích phân thì quên tiệm cận. Lim liếc cũng quên sạch rồi!",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/703987105_17876363136657950_1655264496755906109_n.jpg?_nc_cat=105&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=rdO4KKLEC7cQ7kNvwHP_mnU&_nc_oc=AdrXC1hrGbvTGudcVeIPUWujcZHSHnTVHrFd508KMicAdKy6turbWlPFT8zE5gA-TwZ2u1mRNznykipoEyWi42wS&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=XYC0kNwzVz6jA2Aj26Jzxw&_nc_ss=7b289&oh=00_AQMMaZWeH0n1Au9r9SWl2VpfEdfr9Qr6J7QQkacpPcTCoQ&oe=6ADFA193",
                "likes": "21",
                "comments": "1",
                "reposts": "0",
                "voice": "vi-VN-NamMinhNeural",
            },
            {
                "username": "anmei_32",
                "time": "17 giờ",
                "content": "đau k gì bằng",
                "tts_content": "Đau không gì bằng...",
                "avatar_url": "https://scontent.cdninstagram.com/v/t51.82787-19/724004963_18104376163856712_985720369631380623_n.jpg?_nc_cat=109&ccb=7-5&_nc_sid=30ff31&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xNTAuQzMifQ%3D%3D&_nc_ohc=98PADl1S3OwQ7kNvwFPIyly&_nc_oc=AdqvmZUeKSuH7D-CgmmQRcNDb7bGLf74rg0dRpox_DtEyY0VnA3mM2YFMepaVY6EQgYB0TIrThEXmzqc-i4QF2dz&_nc_zt=24&_nc_ht=scontent.cdninstagram.com&_nc_gid=XYC0kNwzVz6jA2Aj26Jzxw&_nc_ss=7b289&oh=00_AQMsFBIMAVuaSB6usHsVTestsohwtCU_u2B8Q-ppcfvFmA&oe=6ADFBD1F",
                "likes": "1",
                "comments": "0",
                "reposts": "0",
                "voice": "vi-VN-HoaiMyNeural",
            }
        ]
    }

    print("🚀 Bắt đầu sản xuất video Threads cho kênh HanShin...")
    mc_bg = ROOT / "workshops" / "workshop-threads" / "assets" / "backgrounds" / "minecraft_parkour.mp4"
    result = build_threads_video(
        thread_data=thread_data,
        job_id="job_thread_anmei32_2k9",
        background_path=mc_bg if mc_bg.exists() else None,
        theme="dark",
        publish_youtube=True,
        privacy="unlisted"
    )

    print("\n✅ HOÀN TẤT!")
    print(f"File video: {result.get('video_path')}")
    print(f"Tổng số phân đoạn: {result.get('total_segments')}")
    if result.get("youtube"):
        print(f"YouTube URL: {result['youtube'].get('url')}")
        print(f"YouTube Privacy: {result['youtube'].get('privacy')}")

if __name__ == "__main__":
    main()

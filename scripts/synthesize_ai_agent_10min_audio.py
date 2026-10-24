import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path
import edge_tts

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "cinematic" / "job-ai-agent-giaimatech-10min"
AUDIO_DIR = OUTPUT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# 8 Phân cảnh kịch bản đã tối ưu cho kênh Giải Mã Tech
SCENES_SCRIPT = [
    {
        "scene_id": "scene_01_hook",
        "order": 1,
        "title": "Hook: Khi AI Bắt Đầu Hành Động",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+2%",
        "pitch": "+0Hz",
        "text": (
            "Bạn đã từng hỏi AI cách làm một việc, nhận được câu trả lời rất chi tiết, "
            "nhưng cuối cùng vẫn phải tự mình thực hiện tất cả chưa? "
            "Bây giờ hãy tưởng tượng một hệ thống AI có thể nhận nhiệm vụ đó, "
            "tự sử dụng công cụ tìm kiếm, đọc dữ liệu, phân tích và xuất báo cáo cho bạn. "
            "Đây chính là ý tưởng đằng sau công nghệ AI Agent. "
            "Chào mừng bạn đến với Giải Mã Tech, hãy cùng chúng tôi khám phá ngay sau đây!"
        )
    },
    {
        "scene_id": "scene_02_compare",
        "order": 2,
        "title": "Chatbot và AI Agent Khác Nhau Ở Đâu?",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+2%",
        "pitch": "+0Hz",
        "text": (
            "Để hiểu AI Agent, hãy bắt đầu từ điểm khác biệt dễ hình dung nhất. "
            "Nếu bạn hỏi một chatbot thông thường: Hãy giúp tôi tìm hiểu về Docker. "
            "Chatbot sẽ giải thích khái niệm và đưa ra ví dụ. Đây là tương tác hỏi đáp cơ bản. "
            "Nhưng nếu bạn giao nhiệm vụ: Hãy nghiên cứu Docker từ tài liệu chính thức, "
            "tổng hợp năm khái niệm quan trọng và tạo một báo cáo Markdown. "
            "Hệ thống bắt buộc phải tự điều phối công cụ, truy xuất dữ liệu và kiểm tra kết quả. "
            "Đó là điểm khác biệt lớn nhất: Chatbot tập trung trả lời, còn AI Agent tập trung hành động."
        )
    },
    {
        "scene_id": "scene_03_architecture",
        "order": 3,
        "title": "Ba Trụ Cột Kiến Trúc Bên Trong AI Agent",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+2%",
        "pitch": "+0Hz",
        "text": (
            "Về mặt kiến trúc, một AI Agent được xây dựng từ ba thành phần chính. "
            "Thứ nhất là mô hình AI, thường là các mô hình ngôn ngữ lớn, đóng vai trò bộ não suy luận. "
            "Thứ hai là Instructions, gồm chỉ dẫn mục tiêu và các quy tắc ranh giới an toàn. "
            "Thứ ba là Tools, tức các công cụ ngoại vi như trình duyệt web, môi trường chạy code và trình ghi file. "
            "Công cụ chính là đôi tay giúp mô hình AI tương tác trực tiếp với thế giới bên ngoài."
        )
    },
    {
        "scene_id": "scene_04_docker_demo",
        "order": 4,
        "title": "Demo Thực Tế: Agent Nghiên Cứu Tài Liệu Docker",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+2%",
        "pitch": "+0Hz",
        "text": (
            "Hãy quan sát một tình huống thực tế ngay trên màn hình nổi ba đê của phòng lab. "
            "Tôi giao cho Agent nhiệm vụ nghiên cứu Docker dành cho người mới bắt đầu. "
            "Hệ thống tự động kích hoạt trình duyệt, mở đúng trang tài liệu chính thức docs chấm docker chấm com. "
            "Nó bóc tách năm khái niệm quan trọng, kiểm chứng từng nguồn tham khảo, "
            "và xuất ra file docker gạch nối basics chấm md cực kỳ ngăn nắp. "
            "Bạn có thể thấy rõ từng dòng code và kết quả được phóng to sắc nét trên màn hình nổi."
        )
    },
    {
        "scene_id": "scene_05_the_loop",
        "order": 5,
        "title": "Vòng Lặp Thực Thi Của AI Agent",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+2%",
        "pitch": "+0Hz",
        "text": (
            "Điều gì giúp AI Agent duy trì được chuỗi hành động phức tạp? "
            "Bí quyết nằm ở vòng lặp suy luận và hành động. "
            "Sau khi nhận mục tiêu, mô hình suy luận xem cần gọi công cụ nào. "
            "Khi công cụ trả về dữ liệu, mô hình quan sát kết quả để quyết định bước tiếp theo. "
            "Vòng lặp tiếp tục cho đến khi hoàn thành mục tiêu hoặc gặp hành động nhạy cảm cần con người phê duyệt."
        )
    },
    {
        "scene_id": "scene_06_safety_limits",
        "order": 6,
        "title": "Ứng Dụng Thực Tế Và Giới Hạn Cần Kiểm Soát",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+2%",
        "pitch": "+0Hz",
        "text": (
            "Hiện nay, AI Agent ứng dụng mạnh mẽ nhất trong ba lĩnh vực: "
            "Hỗ trợ lập trình, nghiên cứu tài liệu chuyên sâu, và tự động hóa quy trình nghiệp vụ. "
            "Tuy nhiên, hành động của Agent có thể gây ra hậu quả thật trên hệ thống máy tính. "
            "Nếu được cấp quyền quá rộng, nó có thể gọi sai lệnh hoặc xóa nhầm dữ liệu. "
            "Vì vậy, một kiến trúc an toàn luôn phải có hàng rào bảo vệ và cơ chế ngắt khẩn cấp."
        )
    },
    {
        "scene_id": "scene_07_decision_matrix",
        "order": 7,
        "title": "Khi Nào Nên Dùng Agent, Khi Nào Không?",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+2%",
        "pitch": "+0Hz",
        "text": (
            "Có phải bài toán nào cũng cần xây dựng AI Agent không? Câu trả lời là không. "
            "Nếu tác vụ chỉ là phân loại văn bản hay quy trình cố định từng bước, "
            "một lời gọi mô hình đơn lẻ hoặc một workflow thông thường sẽ tiết kiệm chi phí và ổn định hơn. "
            "Chỉ nên chọn kiến trúc Agent khi bài toán thực sự đòi hỏi khả năng điều phối đa công cụ linh hoạt."
        )
    },
    {
        "scene_id": "scene_08_outro_cta",
        "order": 8,
        "title": "Tổng Kết Và Teaser Tập Tiếp Theo",
        "speaker": "Người Dẫn Chuyện",
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+2%",
        "pitch": "+0Hz",
        "text": (
            "Hy vọng qua video này, bạn đã hiểu rõ bản chất của AI Agent và cách nó vận hành. "
            "Đừng quên nhấn Like và Đăng ký kênh Giải Mã Tech để cùng đón xem video tiếp theo, "
            "nơi chúng tôi sẽ giải mã giao thức kết nối công cụ MCP, Model Context Protocol. "
            "Cảm ơn các bạn đã theo dõi, xin chào và hẹn gặp lại!"
        )
    }
]

def resample_audio(src_file: Path, dst_file: Path):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src_file),
        "-ar", "48000",
        "-ac", "2",
        "-b:a", "192k",
        str(dst_file)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def get_audio_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return round(float(res.stdout.strip()), 2)

async def synthesize_all():
    print("🎙️ BẮT ĐẦU TỔNG HỢP MASTER AUDIO 48KHZ STEREO (CỔNG 4)...", flush=True)
    tracks = []
    total_dur = 0.0

    for item in SCENES_SCRIPT:
        sid = item["scene_id"]
        order = item["order"]
        text = item["text"]
        voice = item["voice"]
        rate = item["rate"]
        pitch = item["pitch"]

        temp_mp3 = AUDIO_DIR / f"temp_{order:02d}.mp3"
        final_mp3 = AUDIO_DIR / f"scene_{order:02d}.mp3"

        print(f"  [TTS {order:02d}/08] Đang sinh âm thanh: {item['title']}...", flush=True)
        comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await comm.save(str(temp_mp3))

        # Resample chuẩn Studio 48kHz Stereo 192k
        resample_audio(temp_mp3, final_mp3)
        temp_mp3.unlink(missing_ok=True)

        dur = get_audio_duration(final_mp3)
        total_dur += dur

        print(f"   -> Hoàn tất: {final_mp3.name} | Thời lượng: {dur:.2f}s | Tần số: 48,000 Hz Stereo", flush=True)
        tracks.append({
            "order": order,
            "scene_id": sid,
            "title": item["title"],
            "speaker": item["speaker"],
            "voice": voice,
            "file": str(final_mp3.relative_to(BASE_DIR)).replace("\\", "/"),
            "duration_s": dur,
            "text": text
        })
        await asyncio.sleep(0.8)

    manifest = {
        "channel": "Giải Mã Tech",
        "job_id": "job-ai-agent-giaimatech-10min",
        "audio_standard": "48000 Hz, Stereo 2 Channels, 192kbps AAC/MP3",
        "bgm_ducking_level": "-18dB",
        "total_tracks": len(tracks),
        "total_audio_duration_seconds": round(total_dur, 2),
        "tracks": tracks
    }

    manifest_path = AUDIO_DIR / "audio_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n✅ CỔNG 4 HOÀN THÀNH XUẤT SẮC!", flush=True)
    print(f"📁 Audio Manifest: {manifest_path}", flush=True)
    print(f"⏱️ Tổng thời lượng âm thanh lời dẫn: {total_dur:.2f}s (~{total_dur/60:.1f} phút)", flush=True)

if __name__ == "__main__":
    asyncio.run(synthesize_all())

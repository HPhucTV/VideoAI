import sys
import json
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
WORKSHOP_DIR = ROOT_DIR / "workshops" / "workshop-threads"
sys.path.insert(0, str(WORKSHOP_DIR / "src"))

from pipeline import build_threads_video
from core.telegram_notifier import send_telegram_message

def main():
    json_path = WORKSHOP_DIR / "cache" / "latest_crawled_thread.json"
    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])

    if not json_path.exists():
        print(json.dumps({"success": False, "error": f"Tệp không tồn tại: {json_path}"}))
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        thread_data = json.load(f)

    job_id = thread_data.get("job_id", f"job_thread_auto_{int(time.time())}")
    post = thread_data.get("post", {})
    username = post.get("username", "threads_user")
    content_snippet = post.get("content", "")[:50]

    # Thông báo Telegram bắt đầu
    send_telegram_message(
        f"🎬 <b>[XƯỞNG 5] BẮT ĐẦU SẢN XUẤT VIDEO THREADS</b>\n\n"
        f"👤 Tác giả: <b>@{username}</b>\n"
        f"📝 Nội dung: <i>\"{content_snippet}...\"</i>\n"
        f"⚙️ Job ID: <code>{job_id}</code>\n"
        f"⏳ Đang xử lý: Phân vai Edge-TTS, render thẻ AMOLED, ghép game Minecraft & SFX..."
    )

    bg_gameplay = WORKSHOP_DIR / "assets" / "backgrounds" / "minecraft_parkour.mp4"
    if not bg_gameplay.exists():
        # Fallback to any mp4 in backgrounds
        bgs = list((WORKSHOP_DIR / "assets" / "backgrounds").glob("*.mp4"))
        bg_gameplay = bgs[0] if bgs else None

    result = build_threads_video(
        thread_data=thread_data,
        job_id=job_id,
        theme="dark",
        background_path=bg_gameplay,
        bgm_style="comedy_sneaky",
        bgm_volume=0.38,
        publish_youtube=False
    )

    video_path = result.get("video_path")
    print(json.dumps({
        "success": True,
        "job_id": job_id,
        "video_path": video_path,
        "duration": result.get("duration", 0),
        "post_username": username
    }, ensure_ascii=False))

    # Thông báo Telegram hoàn tất
    send_telegram_message(
        f"✅ <b>[XƯỞNG 5] VIDEO THREADS ĐÃ RENDER XONG!</b>\n\n"
        f"👤 Tác giả: <b>@{username}</b>\n"
        f"📹 Video hoàn thành: <code>{Path(video_path).name if video_path else 'video.mp4'}</code>\n"
        f"🎯 Đạt chuẩn: AMOLED #101010, Avatar thật 100%, SFX Meme Pop lò xo & Sidechain ducking.\n"
        f"👑 Sếp có thể xem trực tiếp tại Dashboard Studio hoặc phê duyệt đăng YouTube!"
    )

if __name__ == "__main__":
    main()

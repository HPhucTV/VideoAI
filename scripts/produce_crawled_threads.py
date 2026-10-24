import sys
import os
import json
import time
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
WORKSHOP_DIR = ROOT_DIR / "workshops" / "workshop-threads"
sys.path.insert(0, str(WORKSHOP_DIR / "src"))

from pipeline import build_threads_video
from core.telegram_notifier import send_telegram_message

_WIN_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

def generate_publishing_kit(thread_data: dict, job_id: str, out_dir: Path, video_path: str) -> dict:
    post = thread_data.get("post", {})
    username = post.get("username", "threads_user")
    content = post.get("content", "").strip()
    comments = thread_data.get("comments", [])

    # Sinh Tiêu Đề Giật Gân High-CTR
    clean_snippet = content.replace("\n", " ").strip()
    clean_snippet = "".join([c for c in clean_snippet if c.isalnum() or c in " ,.-_!?;:()"]).strip()
    if len(clean_snippet) > 42:
        short_snippet = clean_snippet[:42] + "..."
    else:
        short_snippet = clean_snippet

    title_main = f"🔥 {short_snippet.upper()}... CẢM XÚC DÂNG TRÀO! 📚 #Shorts #Threads"
    title_alt1 = f"Tâm Sự Tuổi Thơ: {short_snippet} #Shorts #HanShin #TuoiTho"
    title_alt2 = f"Ai Còn Nhớ Cái Này Không? {short_snippet} 🎒 #Shorts #GiaiTri"

    # Sinh Timestamps & Description
    comment_lines = []
    for c in comments[:3]:
        c_user = c.get("username", "user")
        c_text = c.get("content", "").replace("\n", " ")
        if len(c_text) > 40:
            c_text = c_text[:40] + "..."
        comment_lines.append(f"• @{c_user}: \"{c_text}\"")

    desc_comments = "\n".join(comment_lines) if comment_lines else "• Các bình luận hoài niệm đầy cảm xúc từ cộng đồng."

    description = f"""Tâm sự Threads từ @{username}: "{content}"

Bình luận nổi bật:
{desc_comments}

Mốc thời gian (Chapters):
00:00 - Tuổi thơ ùa về & Tình huống
00:15 - Những bình luận hoài niệm cực chất
00:30 - Cái kết ấm lòng

Theo dõi kênh @HanShin-g8i để đón xem các câu chuyện Threads viral mỗi ngày!

#HanShin #Threads #Shorts #TuoiTho #SGK #HaiHuoc #GiaiTri #MinecraftParkour #TikTokViral #GenZ"""

    tags = ["HanShin", "Threads", "Shorts", "TuoiTho", "SGK", "SachGiaoKhoa", "NgayXua", "HaiHuoc", "GiaiTri", "MinecraftParkour", "TikTok Viral", "Gen Z", "Drama VN"]

    kit = {
        "title": title_main,
        "title_options": [title_main, title_alt1, title_alt2],
        "description": description.strip(),
        "tags": tags,
        "category": "24",
        "privacy": "unlisted"
    }

    kit_path = out_dir / "publishing_kit.json"
    with open(kit_path, "w", encoding="utf-8") as f:
        json.dump(kit, f, ensure_ascii=False, indent=2)

    # Trích xuất Thumbnails và Frame Candidates bằng FFmpeg (hoàn toàn ngầm với _WIN_FLAGS)
    thumb_path = out_dir / "thumb.jpg"
    try:
        # Cắt frame tại t = 2.5s làm thumb chính
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:02.500", "-i", video_path,
            "-vframes", "1", "-q:v", "2", str(thumb_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=_WIN_FLAGS)

        # Cắt 3 frame candidates
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:01.500", "-i", video_path,
            "-vframes", "1", "-q:v", "2", str(out_dir / "frame_candidate_1.jpg")
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=_WIN_FLAGS)
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:03.000", "-i", video_path,
            "-vframes", "1", "-q:v", "2", str(out_dir / "frame_candidate_2.jpg")
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=_WIN_FLAGS)
        subprocess.run([
            "ffmpeg", "-y", "-ss", "00:00:05.000", "-i", video_path,
            "-vframes", "1", "-q:v", "2", str(out_dir / "frame_candidate_3.jpg")
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=_WIN_FLAGS)
    except Exception as e:
        print(f"Lỗi trích xuất thumb: {e}", file=sys.stderr)

    return kit

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

    # Cập nhật status đang chạy
    status_file = ROOT_DIR / "output" / "threads" / "latest_status.json"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump({
            "status": "rendering",
            "job_id": job_id,
            "username": username,
            "updated_at": time.time()
        }, f)

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
        bgs = list((WORKSHOP_DIR / "assets" / "backgrounds").glob("*.mp4"))
        bg_gameplay = bgs[0] if bgs else None

    out_job_dir = ROOT_DIR / "output" / "threads" / job_id
    out_job_dir.mkdir(parents=True, exist_ok=True)

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
    if not video_path or not Path(video_path).exists():
        print(json.dumps({"success": False, "error": "Không tạo được video MP4"}))
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump({"status": "failed", "job_id": job_id, "updated_at": time.time()}, f)
        sys.exit(1)

    # Tự Động Sinh Tiêu Đề, Caption, Timestamps, Tags & Thumbnail
    kit = generate_publishing_kit(thread_data, job_id, out_job_dir, video_path)

    # Cập nhật status hoàn tất để Dashboard bắt được ngay
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump({
            "status": "completed",
            "job_id": job_id,
            "username": username,
            "title": kit.get("title", ""),
            "video_path": video_path,
            "thumb_url": f"/media/threads/{job_id}/thumb.jpg",
            "updated_at": time.time()
        }, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "success": True,
        "job_id": job_id,
        "video_path": video_path,
        "title": kit.get("title", ""),
        "duration": result.get("duration", 0),
        "post_username": username
    }, ensure_ascii=False))

    # Thông báo Telegram hoàn tất
    send_telegram_message(
        f"✅ <b>[XƯỞNG 5] VIDEO THREADS ĐÃ RENDER XONG!</b>\n\n"
        f"📌 Tiêu đề: <b>{kit.get('title', '')}</b>\n"
        f"👤 Tác giả: <b>@{username}</b>\n"
        f"📹 Video: <code>{Path(video_path).name}</code>\n"
        f"🎨 Đã sẵn sàng: Thumbnail sắc nét, Timestamps & Bộ Tags chuẩn SEO YouTube!\n"
        f"👑 Sếp có thể bấm xem và đăng YouTube ngay trên Dashboard!"
    )

if __name__ == "__main__":
    main()

"""Gate 7: YouTube Auto-Publisher & Publishing Kit module for OmniVideo Studio."""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Link to workshops/workshop-cinematic for youtube module
_ROOT = Path(__file__).resolve().parent.parent
_CINEMATIC_DIR = _ROOT / "workshops" / "workshop-cinematic"
_VENV_SITE = _CINEMATIC_DIR / ".venv" / "Lib" / "site-packages"

if str(_CINEMATIC_DIR) not in sys.path:
    sys.path.insert(0, str(_CINEMATIC_DIR))

if _VENV_SITE.exists() and str(_VENV_SITE) not in sys.path:
    sys.path.insert(0, str(_VENV_SITE))

try:
    from youtube.auth import get_authenticated_service
    from youtube.upload import set_thumbnail, upload_srt_captions
    from googleapiclient.http import MediaFileUpload
except ImportError:
    try:
        from workshops.workshop_cinematic.youtube.auth import get_authenticated_service
        from workshops.workshop_cinematic.youtube.upload import set_thumbnail, upload_srt_captions
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        get_authenticated_service = None
        set_thumbnail = None
        upload_srt_captions = None
        MediaFileUpload = None

# Fallback definitions if not provided by youtube.upload
if set_thumbnail is None:
    def set_thumbnail(youtube_service: Any, video_id: str, thumbnail_path: str | Path) -> Any:
        if MediaFileUpload is None:
            return None
        t_path = Path(thumbnail_path)
        if not t_path.exists():
            return None
        media = MediaFileUpload(str(t_path), mimetype="image/jpeg", resumable=True)
        return youtube_service.thumbnails().set(videoId=video_id, media_body=media).execute()

if upload_srt_captions is None:
    def upload_srt_captions(
        youtube_service: Any,
        video_id: str,
        srt_path: str | Path,
        language: str = "vi",
        name: str = "Tiếng Việt",
    ) -> Any:
        if MediaFileUpload is None:
            return None
        s_path = Path(srt_path)
        if not s_path.exists():
            return None
        media = MediaFileUpload(str(s_path), mimetype="application/x-subrip", resumable=True)
        body = {
            "snippet": {
                "videoId": video_id,
                "language": language,
                "name": name,
                "isDraft": False,
            }
        }
        return youtube_service.captions().insert(part="snippet", body=body, media_body=media).execute()

logger = logging.getLogger("youtube_publisher")


def format_timestamp(seconds: float) -> str:
    """Format seconds into MM:SS or HH:MM:SS."""
    total_sec = max(0, int(seconds))
    hours = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def generate_publishing_kit(job_data: dict, actual_duration_sec: float) -> dict:
    """Generate publishing metadata kit including chapters, title options, description, and tags."""
    job_id = job_data.get("jobId", "untitled-job")
    title = job_data.get("title", "OmniVideo Film")
    meta = job_data.get("metadata", {})
    channel = meta.get("channel", "OmniVideo Studio")
    beats = job_data.get("beats", [])

    # 1. Build Timestamps / Chapters starting from 00:00
    timestamps = [{"time": "00:00", "title": "Giới thiệu & Mở đầu"}]
    current_time = 2.0  # Intro bumper default 2.0s
    for idx, b in enumerate(beats, 1):
        chapter_title = (
            b.get("chapter")
            or b.get("title")
            or b.get("speaker")
            or b.get("role")
            or f"Phân cảnh {idx}"
        )
        if idx == 1 or b.get("is_new_chapter") or idx % 5 == 0 or len(beats) <= 5:
            timestamps.append({
                "time": format_timestamp(current_time),
                "title": f"Phần {len(timestamps)}: {chapter_title}",
            })
        current_time += float(b.get("durationSec", 5.0))

    # 2. Build Description
    desc_lines = [
        f"🎬 {title} - Sản xuất tự động bởi OmniVideo Studio.",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━",
        "⏱️ NỘI DUNG TỪNG PHẦN (TIMESTAMPS):",
    ]
    for ts in timestamps:
        desc_lines.append(f"{ts['time']} - {ts['title']}")
    desc_lines.extend([
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"💡 Đăng ký kênh {channel} để đón xem các tập phim hoạt hình 3D tiếp theo!",
        "#OmniVideo #Donghua3D #AIAnimation #3DFilm",
    ])

    return {
        "jobId": job_id,
        "channel": channel,
        "privacy_status": "unlisted",
        "video_title_options": [
            {"id": "seo_primary", "title": f"{title} | {channel}"},
            {"id": "hook_question", "title": f"Bí Mật Đằng Sau {title}? | {channel}"},
            {"id": "high_ctr", "title": f"Cực Sốc: {title} Đã Thay Đổi Mọi Thứ! | {channel}"},
        ],
        "timestamps": timestamps,
        "youtube_description": "\n".join(desc_lines),
        "tags": meta.get("tags", ["AI", "Donghua", "3D Animation"]),
        "actual_duration_sec": actual_duration_sec,
    }


def save_publishing_kit(kit: dict, output_path: str | Path) -> Path:
    """Save publishing kit dictionary to a JSON file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(kit, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Saved publishing kit to %s", out)
    return out


def upload_unlisted_video(
    channel_name: str,
    video_path: Path | str,
    title: str,
    description: str,
    tags: list[str],
    thumbnail_path: Optional[Path | str] = None,
    srt_path: Optional[Path | str] = None,
    privacy_status: str = "unlisted",
    category_id: str = "28",
    status_file: Optional[Path | str] = None,
    publish_at: Optional[str] = None,
) -> dict:
    """Upload video to YouTube in unlisted, public, private, or scheduled mode with thumbnail, subtitles and status progress support."""
    if get_authenticated_service is None:
        raise RuntimeError("Google API client is not installed.")

    status_path = Path(status_file) if status_file else None

    def _update_status(data: dict):
        if status_path:
            try:
                status_path.parent.mkdir(parents=True, exist_ok=True)
                status_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            except Exception as e:
                logger.warning("Failed to write status file: %s", e)

    _update_status({
        "status": "authenticating",
        "progress": 5,
        "message": f"Đang xác thực OAuth kênh YouTube '{channel_name}'...",
    })

    youtube = get_authenticated_service(channel_name)
    body = {
        "snippet": {
            "title": str(title)[:100],
            "description": str(description)[:5000],
            "tags": list(tags)[:50],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": "private" if publish_at else privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    if publish_at:
        body["status"]["publishAt"] = publish_at

    try:
        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=5 * 1024 * 1024,
        )
    except Exception as e:
        logger.warning(
            "Could not initialize MediaFileUpload for %s: %s (using mock/fallback)",
            video_path,
            e,
        )
        class _MockMedia:
            pass
        media = _MockMedia()

    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    _update_status({
        "status": "uploading",
        "progress": 10,
        "message": "Đang bắt đầu truyền các khối dữ liệu video...",
    })

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 85) + 10  # Scale chunk progress from 10% to 95%
            logger.info("Upload progress: %d%%", int(status.progress() * 100))
            _update_status({
                "status": "uploading",
                "progress": pct,
                "message": f"Đang tải dữ liệu video lên YouTube: {int(status.progress() * 100)}% ({pct}% quy trình)...",
            })

    video_id = response.get("id", "")
    url = f"https://youtu.be/{video_id}"
    logger.info("Video uploaded successfully: %s (Privacy: %s)", url, privacy_status)

    _update_status({
        "status": "processing",
        "progress": 96,
        "video_id": video_id,
        "url": url,
        "message": "Video đã lên YouTube! Đang đồng bộ Thumbnail 3D...",
    })

    # Set Thumbnail if provided (with retries for processing delay)
    if thumbnail_path and set_thumbnail:
        import time
        for attempt in range(1, 4):
            try:
                set_thumbnail(youtube, video_id, Path(thumbnail_path))
                logger.info("Custom 3D Thumbnail set successfully.")
                break
            except Exception as e:
                logger.warning("Failed to set thumbnail (attempt %d/3): %s", attempt, e)
                if attempt < 3:
                    time.sleep(5)

    # Set Subtitles if provided (with retries for processing delay)
    if srt_path and upload_srt_captions:
        import time
        for attempt in range(1, 4):
            try:
                upload_srt_captions(youtube, video_id, Path(srt_path))
                logger.info("Subtitles SRT uploaded successfully.")
                break
            except Exception as e:
                logger.warning("Failed to set subtitles (attempt %d/3): %s", attempt, e)
                if attempt < 3:
                    time.sleep(10)

    effective_privacy = "scheduled" if publish_at else privacy_status
    result_payload = {
        "status": "completed",
        "progress": 100,
        "video_id": video_id,
        "url": url,
        "privacy": effective_privacy,
        "publish_at": publish_at,
        "message": f"Upload YouTube thành công! ({'Đã lên lịch' if publish_at else effective_privacy.upper()})",
    }
    _update_status(result_payload)

    return {
        "video_id": video_id,
        "url": url,
        "privacy": effective_privacy,
        "publish_at": publish_at,
    }


if __name__ == "__main__":
    import argparse
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="YouTube Publisher CLI")
    parser.add_argument("--channel", default="HanShin", help="Channel name or folder alias")
    parser.add_argument("--video", required=True, help="Path to MP4 video file")
    parser.add_argument("--title", default="OmniVideo", help="Video Title")
    parser.add_argument("--description", default="", help="Video Description")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--privacy", default="unlisted", choices=["public", "unlisted", "private"])
    parser.add_argument("--publish-at", default=None, help="Scheduled publish time (ISO 8601 string)")
    parser.add_argument("--thumb", default=None, help="Path to thumbnail image")
    parser.add_argument("--srt", default=None, help="Path to SRT subtitle file")
    parser.add_argument("--category", default="24", help="YouTube Category ID (default: 24 Entertainment)")
    parser.add_argument("--status-file", default=None, help="Path to write real-time upload progress JSON")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    tags_list = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    try:
        res = upload_unlisted_video(
            channel_name=args.channel,
            video_path=args.video,
            title=args.title,
            description=args.description,
            tags=tags_list,
            thumbnail_path=args.thumb,
            srt_path=args.srt,
            privacy_status=args.privacy,
            category_id=args.category,
            status_file=args.status_file,
            publish_at=args.publish_at,
        )
        if args.json:
            print(json.dumps({"success": True, **res}, ensure_ascii=False))
        else:
            print(f"UPLOAD_SUCCESS: {res.get('url')} (ID: {res.get('video_id')}, Privacy: {res.get('privacy')})")
    except Exception as exc:
        if args.json:
            print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"UPLOAD_ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


"""
OmniVideo Studio - Unified 4 Workshops Studio API
Quản lý video toàn diện (CRUD), giám sát tiến trình trực tiếp (Live Monitor),
thống kê & dọn dẹp dung lượng ổ đĩa (Storage Manager) cho 4 phân xưởng.
"""
from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from agent.services.studio_tracker import studio_tracker

router = APIRouter(prefix="/api/studio", tags=["studio"])

# Thư mục gốc OmniVideo
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "output"
JOBS_DIR = OUTPUT_DIR / "jobs"

WORKSHOPS = {
    "news": {
        "id": "news",
        "name": "Xưởng 1: Tin Tức & Đồ Họa Nhanh",
        "dir": OUTPUT_DIR / "news",
        "color": "#3b82f6",  # Blue
        "aspect": "9:16",
    },
    "explainer": {
        "id": "explainer",
        "name": "Xưởng 2: Video Giải Thích Code",
        "dir": OUTPUT_DIR / "explainer",
        "color": "#8b5cf6",  # Purple
        "aspect": "9:16 / 16:9",
    },
    "whiteboard": {
        "id": "whiteboard",
        "name": "Xưởng 3: Vẽ Tay Bảng Trắng",
        "dir": OUTPUT_DIR / "whiteboard",
        "color": "#f59e0b",  # Amber
        "aspect": "16:9",
    },
    "cinematic": {
        "id": "cinematic",
        "name": "Xưởng 4: Phim Điện Ảnh AI 3D",
        "dir": OUTPUT_DIR / "cinematic",
        "color": "#ef4444",  # Red
        "aspect": "16:9",
    },
}


def _format_size(size_bytes: int) -> str:
    """Format bytes to human readable size (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def _get_dir_size(path: Path) -> int:
    """Tính tổng dung lượng thư mục."""
    total = 0
    if not path.exists():
        return 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += _get_dir_size(Path(entry.path))
    except Exception:
        pass
    return total


# ─── 1. Live Progress & Activity ────────────────────────────

@router.get("/progress")
async def get_progress():
    """Trả về trạng thái tiến trình thời gian thực của 4 xưởng."""
    return studio_tracker.get_status()


class StartJobPayload(BaseModel):
    job_id: str
    workshop: str
    title: str
    steps: Optional[List[Dict[str, str]]] = None


@router.post("/progress/start")
async def start_job(payload: StartJobPayload):
    """Đăng ký job mới vào live tracker."""
    job = studio_tracker.start_job(
        job_id=payload.job_id,
        workshop=payload.workshop,
        title=payload.title,
        steps=payload.steps,
    )
    return {"status": "ok", "job": job.model_dump()}


class UpdateProgressPayload(BaseModel):
    progress: int
    step_id: Optional[str] = None
    step_detail: Optional[str] = None
    log_line: Optional[str] = None


@router.post("/progress/{job_id}/update")
async def update_job_progress(job_id: str, payload: UpdateProgressPayload):
    """Cập nhật % và log của job đang chạy."""
    studio_tracker.update_progress(
        job_id=job_id,
        progress=payload.progress,
        step_id=payload.step_id,
        step_detail=payload.step_detail,
        log_line=payload.log_line,
    )
    return {"status": "ok"}


class CompleteJobPayload(BaseModel):
    output_video_path: Optional[str] = None
    summary: str = "Hoàn tất thành công!"


@router.post("/progress/{job_id}/complete")
async def complete_job(job_id: str, payload: CompleteJobPayload):
    """Đánh dấu job đã hoàn thành."""
    studio_tracker.complete_job(
        job_id=job_id,
        output_video_path=payload.output_video_path,
        summary=payload.summary,
    )
    return {"status": "ok"}


# ─── 2. Storage & Disk Usage ────────────────────────────────

@router.get("/storage")
async def get_storage_stats():
    """Thống kê dung lượng ổ đĩa chi tiết của 4 xưởng."""
    workshop_stats = {}
    total_workshop_bytes = 0

    for ws_key, ws_info in WORKSHOPS.items():
        size = _get_dir_size(ws_info["dir"])
        total_workshop_bytes += size
        workshop_stats[ws_key] = {
            "id": ws_key,
            "name": ws_info["name"],
            "color": ws_info["color"],
            "size_bytes": size,
            "size_formatted": _format_size(size),
        }

    # Thêm jobs dir
    jobs_size = _get_dir_size(JOBS_DIR)
    total_workshop_bytes += jobs_size

    # Dung lượng ổ cứng máy tính (Drive C:)
    drive_stat = shutil.disk_usage(ROOT_DIR)
    
    return {
        "workshops": workshop_stats,
        "total_workshops_bytes": total_workshop_bytes,
        "total_workshops_formatted": _format_size(total_workshop_bytes),
        "disk": {
            "total_bytes": drive_stat.total,
            "total_formatted": _format_size(drive_stat.total),
            "free_bytes": drive_stat.free,
            "free_formatted": _format_size(drive_stat.free),
            "used_bytes": drive_stat.used,
            "used_formatted": _format_size(drive_stat.used),
            "free_percent": round((drive_stat.free / drive_stat.total) * 100, 1),
        },
    }


@router.post("/cleanup-temp")
async def cleanup_temp():
    """Dọn dẹp các file rác, file đệm trung gian (temp audio, frames, logs) và thư mục mồ côi để giải phóng ổ cứng."""
    freed_bytes = 0
    removed_files = 0

    # 1. Quét các thư mục temp trong output
    temp_dirs = [
        OUTPUT_DIR / "temp",
        OUTPUT_DIR / "news" / "temp",
        OUTPUT_DIR / "explainer" / "temp",
        OUTPUT_DIR / "whiteboard" / "temp",
        OUTPUT_DIR / "cinematic" / "temp",
        ROOT_DIR / "workshops" / "workshop-cinematic" / "scratch",
    ]

    for tdir in temp_dirs:
        if not tdir.exists():
            continue
        for root, dirs, files in os.walk(tdir):
            for f in files:
                # Dọn file trung gian: .tmp, .wav, .raw, file log lớn, preview frames
                if f.endswith((".tmp", ".raw", ".cache", ".part")) or (
                    tdir.name == "scratch" and f.endswith((".jsonl", ".dump")) and time.time() - os.path.getmtime(os.path.join(root, f)) > 86400
                ):
                    fpath = Path(root) / f
                    try:
                        fsize = fpath.stat().st_size
                        fpath.unlink()
                        freed_bytes += fsize
                        removed_files += 1
                    except Exception:
                        pass

    # 2. Dọn dẹp các thư mục phân cảnh mồ côi (orphaned job folders) trong 4 xưởng
    # (Những thư mục còn sót lại khi file video .mp4 master đã bị xóa)
    for ws_key, ws_info in WORKSHOPS.items():
        ws_dir = ws_info["dir"]
        if not ws_dir.exists():
            continue

        existing_video_stems = set()
        for f in ws_dir.glob("*.mp4"):
            existing_video_stems.add(f.stem)
            existing_video_stems.add(f.stem.replace("-sub", ""))

        for item in list(ws_dir.iterdir()):
            if item.is_dir() and item.name != "temp":
                # Nếu thư mục phân cảnh này không thuộc về bất kỳ video master nào đang tồn tại
                if item.name not in existing_video_stems:
                    try:
                        dir_size = _get_dir_size(item)
                        shutil.rmtree(item)
                        freed_bytes += dir_size
                        removed_files += 1
                    except Exception:
                        pass
            elif item.is_file():
                # Xóa thumbnail/preview/srt/txt mồ côi nếu không có video tương ứng
                if item.suffix.lower() in (".jpg", ".jpeg", ".png", ".srt", ".vtt", ".txt"):
                    base_stem = item.stem.replace("-thumb", "").replace("-preview", "").replace("_thumbnail", "").replace("-preview-kael", "")
                    if base_stem not in existing_video_stems and not item.name.startswith("sample"):
                        try:
                            fsize = item.stat().st_size
                            item.unlink()
                            freed_bytes += fsize
                            removed_files += 1
                        except Exception:
                            pass

    return {
        "status": "ok",
        "removed_files": removed_files,
        "freed_bytes": freed_bytes,
        "freed_formatted": _format_size(freed_bytes),
        "message": f"Đã dọn dẹp {removed_files} mục rác tồn dư, giải phóng {_format_size(freed_bytes)} dung lượng!",
    }


# ─── 3. Video Library CRUD ──────────────────────────────────

@router.get("/videos")
async def list_videos(workshop: Optional[str] = None):
    """Liệt kê danh sách tất cả video thành phẩm trong 4 phân xưởng."""
    items: List[Dict[str, Any]] = []

    workshops_to_scan = [workshop] if workshop and workshop in WORKSHOPS else list(WORKSHOPS.keys())

    for ws_key in workshops_to_scan:
        ws_info = WORKSHOPS[ws_key]
        ws_dir = ws_info["dir"]
        if not ws_dir.exists():
            continue

        try:
            for entry in os.scandir(ws_dir):
                if not entry.is_file():
                    continue
                name = entry.name
                if not name.endswith(".mp4"):
                    continue

                fpath = Path(entry.path)
                fstat = entry.stat()
                stem = fpath.stem  # vd: job-mcp-cyber-chibi
                base_id = stem.replace("-sub", "")

                # Tìm thumbnail
                thumb_candidates = [
                    ws_dir / f"{stem}-thumb.png",
                    ws_dir / f"{stem}-thumb.jpg",
                    ws_dir / f"{base_id}-thumb.png",
                    ws_dir / f"{base_id}-thumb.jpg",
                    ws_dir / f"{stem}-preview.jpg",
                    ws_dir / f"{stem}-preview.png",
                    ws_dir / f"{base_id}-preview.jpg",
                    ws_dir / f"{base_id}-preview.png",
                    ws_dir / f"{stem}.png",
                    ws_dir / f"{stem}.jpg",
                    ws_dir / f"{stem}_thumbnail.png",
                ]
                thumb_file = next((c for c in thumb_candidates if c.exists()), None)
                if not thumb_file:
                    for sub_dir in (ws_dir / stem, ws_dir / base_id):
                        if (sub_dir / "thumbnails").is_dir():
                            for img_file in (sub_dir / "thumbnails").glob("*.jpg"):
                                thumb_file = img_file
                                break
                            if not thumb_file:
                                for img_file in (sub_dir / "thumbnails").glob("*.png"):
                                    thumb_file = img_file
                                    break
                        if thumb_file:
                            break

                # Tìm SRT
                srt_candidates = [
                    ws_dir / f"{stem}.srt",
                    ws_dir / f"{base_id}.srt",
                    ws_dir / base_id / "input.srt",
                ]
                srt_file = next((c for c in srt_candidates if c.exists()), None)

                # Tìm job spec nếu có
                job_spec_file = JOBS_DIR / f"{base_id}.json"
                job_title = stem
                metadata = {}
                if job_spec_file.exists():
                    try:
                        import json
                        jdata = json.loads(job_spec_file.read_text(encoding="utf-8"))
                        job_title = jdata.get("title") or job_title
                        metadata = jdata.get("metadata", {})
                    except Exception:
                        pass

                items.append({
                    "id": stem,
                    "filename": name,
                    "title": job_title,
                    "workshop": ws_key,
                    "workshop_name": ws_info["name"],
                    "workshop_color": ws_info["color"],
                    "aspect_ratio": ws_info["aspect"],
                    "size_bytes": fstat.st_size,
                    "size_formatted": _format_size(fstat.st_size),
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(fstat.st_mtime)),
                    "timestamp": fstat.st_mtime,
                    "has_thumbnail": thumb_file is not None,
                    "thumb_url": f"/api/studio/media/{ws_key}/{thumb_file.relative_to(ws_dir).as_posix()}" if thumb_file else None,
                    "video_url": f"/api/studio/media/{ws_key}/{name}",
                    "has_srt": srt_file is not None,
                    "srt_url": f"/api/studio/media/{ws_key}/{srt_file.relative_to(ws_dir).as_posix()}" if srt_file else None,
                    "metadata": metadata,
                })
        except Exception as e:
            logger.warning("Lỗi quét thư mục %s: %s", ws_dir, e)

    # Sắp xếp mới nhất lên đầu
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"status": 200, "videos": items, "count": len(items)}


@router.delete("/videos/{workshop}/{video_filename}")
async def delete_video(workshop: str, video_filename: str):
    """Xóa hoàn toàn video, ảnh thumbnail, subtitle và file kịch bản để giải phóng ổ đĩa."""
    if workshop not in WORKSHOPS:
        raise HTTPException(400, "Workshop không hợp lệ")

    ws_dir = WORKSHOPS[workshop]["dir"]
    vpath = ws_dir / video_filename
    if not vpath.exists():
        raise HTTPException(404, "Không tìm thấy file video trên ổ đĩa")

    freed_bytes = 0
    removed = []

    try:
        freed_bytes += vpath.stat().st_size
        vpath.unlink()
        removed.append(video_filename)
    except Exception as e:
        raise HTTPException(500, f"Không thể xóa video: {e}")

    # Xóa file phụ trợ (thumbnail, srt, job spec)
    stem = vpath.stem
    base_id = stem.replace("-sub", "")

    related_patterns = [
        f"{stem}-thumb.png", f"{stem}-thumb.jpg",
        f"{base_id}-thumb.png", f"{base_id}-thumb.jpg",
        f"{stem}.png", f"{stem}.jpg",
        f"{stem}.srt", f"{base_id}.srt",
        f"{stem}.vtt", f"{base_id}.vtt",
    ]

    for p in related_patterns:
        rf = ws_dir / p
        if rf.exists():
            try:
                freed_bytes += rf.stat().st_size
                rf.unlink()
                removed.append(p)
            except Exception:
                pass

    # Xóa file job json nếu có
    jf = JOBS_DIR / f"{base_id}.json"
    if jf.exists():
        try:
            freed_bytes += jf.stat().st_size
            jf.unlink()
            removed.append(jf.name)
        except Exception:
            pass

    # Xóa hoàn toàn thư mục làm việc phụ trợ (segments, shots, bumpers, audio)
    for folder_candidate in [ws_dir / stem, ws_dir / base_id]:
        if folder_candidate.is_dir():
            try:
                folder_size = _get_dir_size(folder_candidate)
                shutil.rmtree(folder_candidate)
                freed_bytes += folder_size
                removed.append(f"{folder_candidate.name}/")
            except Exception:
                pass

    return {
        "status": "ok",
        "freed_bytes": freed_bytes,
        "freed_formatted": _format_size(freed_bytes),
        "removed_files": removed,
        "message": f"Đã xóa thành công! Giải phóng {_format_size(freed_bytes)} dung lượng ổ đĩa.",
    }


# ─── 4. Media Streaming (Range Support) ──────────────────────

@router.get("/media/{workshop}/{file_path:path}")
async def serve_media(workshop: str, file_path: str, request: Request):
    """Phát video (hỗ trợ HTTP 206 Range tua nhanh) hoặc phục vụ ảnh thumbnail."""
    if workshop not in WORKSHOPS:
        raise HTTPException(404, "Phân xưởng không tồn tại")

    ws_dir = WORKSHOPS[workshop]["dir"]
    fpath = ws_dir / file_path
    if not fpath.exists():
        raise HTTPException(404, "File không tồn tại")

    ext = fpath.suffix.lower()
    content_types = {
        ".mp4": "video/mp4",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".srt": "text/plain; charset=utf-8",
        ".vtt": "text/vtt; charset=utf-8",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
    }
    media_type = content_types.get(ext, "application/octet-stream")

    file_size = fpath.stat().st_size
    range_header = request.headers.get("Range")

    if range_header and ext in (".mp4", ".mp3", ".wav"):
        # Xử lý tua video (HTTP 206 Range)
        range_val = range_header.replace("bytes=", "")
        parts = range_val.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1

        if start >= file_size:
            return Response(status_code=416, headers={"Content-Range": f"bytes */{file_size}"})

        chunk_size = end - start + 1

        def iterfile():
            with open(fpath, "rb") as f:
                f.seek(start)
                bytes_left = chunk_size
                while bytes_left > 0:
                    read_len = min(64 * 1024, bytes_left)
                    data = f.read(read_len)
                    if not data:
                        break
                    bytes_left -= len(data)
                    yield data

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": media_type,
        }
        return StreamingResponse(iterfile(), status_code=206, headers=headers)

    return FileResponse(path=fpath, media_type=media_type)


# ─── 5. Publishing Kit & Social Hub ─────────────────────────

PUBLISHING_KIT_FILE = OUTPUT_DIR / "publishing_kit.json"


class TitleVariant(BaseModel):
    id: str = "hook"
    label: str = "Hook Tò Mò"
    badge_color: str = "pink"
    metrics: str = ""
    text: str


class PublishingKitModel(BaseModel):
    video_id: Optional[str] = None
    project_id: Optional[str] = None
    status: str = "ready"
    updated_at: Optional[str] = None
    sync_note: str = "Đồng bộ tự động từ AI Agent"
    titles: List[TitleVariant] = []
    caption: str = ""
    hashtags: List[str] = []
    thumbnail_url: Optional[str] = None
    thumbnail_score: str = "94.8%"
    thumbnail_specs: str = "1920x1080 (16:9) • PNG"


@router.get("/publishing-kit")
async def get_publishing_kit():
    """Trả về gói tư liệu phát hành (tiêu đề, caption, hashtags, thumbnail) hiện tại."""
    if PUBLISHING_KIT_FILE.exists():
        try:
            import json
            data = json.loads(PUBLISHING_KIT_FILE.read_text(encoding="utf-8-sig"))
            return {"status": "ok", "kit": data}
        except Exception:
            pass
    return {
        "status": "ok",
        "kit": {
            "status": "empty",
            "sync_note": "Chưa có dự án nào đang soạn tư liệu",
            "titles": [],
            "caption": "",
            "hashtags": [],
            "thumbnail_url": None,
        },
    }


@router.post("/publishing-kit")
async def update_publishing_kit(payload: PublishingKitModel):
    """Cập nhật gói tư liệu xuất bản từ AI Agent để đẩy lên Dashboard."""
    import json
    data = payload.model_dump()
    if not data.get("updated_at"):
        data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    PUBLISHING_KIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    PUBLISHING_KIT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "message": "Đã đồng bộ gói tư liệu lên Dashboard!", "kit": data}


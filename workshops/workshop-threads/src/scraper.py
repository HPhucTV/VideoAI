"""
Xưởng 5: Threads & Social Drama (workshop-threads)
Module: scraper.py
Tính năng:
- Bóc tách nội dung bài viết và chuỗi bình luận từ mạng xã hội Threads.
- Hỗ trợ tải avatar thật và ảnh bài viết (Post Media) về cache cục bộ.
- Phân tích cú pháp văn bản tự do (khi người dùng copy/paste đoạn hội thoại Threads).
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("workshop_threads.scraper")


def cache_media(url: str, target_dir: str | Path, prefix: str = "media") -> Optional[str]:
    """Tải ảnh (avatar hoặc post media) về bộ nhớ đệm cục bộ."""
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        if url and Path(url).exists():
            return str(Path(url).resolve())
        return None

    try:
        t_dir = Path(target_dir)
        t_dir.mkdir(parents=True, exist_ok=True)
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:12]
        ext = ".jpg"
        if ".png" in url.lower():
            ext = ".png"
        elif ".webp" in url.lower():
            ext = ".webp"

        local_file = t_dir / f"{prefix}_{url_hash}{ext}"
        if not local_file.exists():
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp, open(local_file, "wb") as f:
                f.write(resp.read())
        return str(local_file.resolve())
    except Exception as e:
        logger.warning("Không thể tải media từ %s: %s", url, e)
        return None


def parse_raw_text_thread(raw_text: str) -> Dict[str, Any]:
    """
    Phân tích một đoạn văn bản copy từ Threads hoặc dàn ý hội thoại.
    Định dạng gợi ý:
    Chủ thớt: @username | 2 giờ
    Nội dung bài viết...
    ---
    Bình luận 1: @user2 | 1 giờ
    Nội dung bình luận 1...
    ---
    Bình luận 2: @user3 | 30 phút
    Nội dung bình luận 2...
    """
    blocks = [b.strip() for b in re.split(r"\n\s*---\s*\n", raw_text) if b.strip()]
    if not blocks:
        return {"post": {"username": "threads_user", "content": raw_text.strip()}, "comments": []}

    # Block đầu là Post chính
    post_lines = blocks[0].split("\n")
    header_line = post_lines[0]
    username = "threads_user"
    time_str = "vừa xong"

    if "@" in header_line or "|" in header_line:
        parts = [p.strip() for p in header_line.split("|")]
        u_match = re.search(r"@?([\w\.\-]+)", parts[0])
        if u_match:
            username = u_match.group(1)
        if len(parts) > 1:
            time_str = parts[1]
        content = "\n".join(post_lines[1:]).strip()
    else:
        content = "\n".join(post_lines).strip()

    comments = []
    for blk in blocks[1:]:
        c_lines = blk.split("\n")
        c_header = c_lines[0]
        c_user = "user_reply"
        c_time = "vừa xong"
        if "@" in c_header or "|" in c_header:
            parts = [p.strip() for p in c_header.split("|")]
            u_match = re.search(r"@?([\w\.\-]+)", parts[0])
            if u_match:
                c_user = u_match.group(1)
            if len(parts) > 1:
                c_time = parts[1]
            c_content = "\n".join(c_lines[1:]).strip()
        else:
            c_content = "\n".join(c_lines).strip()

        comments.append({
            "username": c_user,
            "time": c_time,
            "content": c_content,
            "likes": "128",
            "comments": "12",
            "reposts": "3",
        })

    return {
        "post": {
            "username": username,
            "time": time_str,
            "content": content,
            "likes": "1.5K",
            "comments": str(len(comments) * 45 + 50),
            "reposts": "32",
        },
        "comments": comments,
    }

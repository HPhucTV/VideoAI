"""
Xưởng 5: Threads & Social Drama (workshop-threads)
Module: card_engine.py
Tính năng:
- Render thẻ bài viết & chuỗi bình luận Threads / HanShin chuẩn xác như chụp màn hình ứng dụng điện thoại (Native Mobile App Screenshot).
- Loại bỏ hoàn toàn cảm giác "ảnh render 3D giả lập":
  + Chuẩn Dark Mode AMOLED (#101010) hoặc Light Mode với bo góc nhẹ 18px (thay vì 32px bo tròn thô).
  + Tỷ lệ chiều rộng chuẩn điện thoại (820px trên khung hình 1080px), padding thanh thoát (22px 24px).
  + Typography tự nhiên chuẩn San Francisco / Segoe UI / Roboto (weight 400-500 thay vì in đậm 700 toàn bộ).
  + Header bài viết đầy đủ: Avatar tròn 44px, Username bold, chấm phân cách, thời gian đăng, và biểu tượng 3 chấm (...) kinh điển của Threads.
  + Media đính kèm (ảnh meme) nguyên vẹn aspect ratio, bo góc 14px, viền mờ.
  + Thanh Action Bar chuẩn xác 4 icon: Like (tim), Comment (bóng thoại), Repost (vòng mũi tên), Share (máy bay).
  + Brand Watermark trên đỉnh canvas (Avatar kênh + HANSHIN THREADS) tăng nhận diện thương hiệu.
- Xuất file PNG trong suốt 1080x1920 bằng Headless Chrome / Edge.
"""
from __future__ import annotations

import html
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

_DEFAULT_BRAND_AVATAR = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "shared-assets"
    / "branding"
    / "hanshin_avatar.png"
)


def find_browser_executable() -> str:
    """Tìm trình duyệt Chrome hoặc Edge có sẵn trên Windows."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("Không tìm thấy Chrome hoặc Microsoft Edge trên máy tính.")


def render_card(
    username: str,
    time_str: str,
    content: str,
    output_png: str | Path,
    avatar_url: Optional[str] = None,
    post_image_url: Optional[str] = None,
    likes: str = "1.2K",
    comments: str = "328",
    reposts: str = "45",
    is_reply_to: Optional[str] = None,
    theme: str = "dark",
    width: int = 1080,
    height: int = 1920,
    card_width: int = 820,
    show_brand_header: bool = True,
    brand_title: str = "HANSHIN THREADS",
    brand_avatar_path: Optional[str | Path] = None,
    parent_context: Optional[Dict[str, str]] = None,
) -> Path:
    """
    Render thẻ bài viết Threads thành ảnh PNG trong suốt chuẩn 1080x1920,
    mô phỏng chính xác giao diện chụp màn hình điện thoại gốc (Pixel-Perfect Native Screenshot).
    """
    out_path = Path(output_png).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    browser_exe = find_browser_executable()

    safe_content = html.escape(content).replace("\n", "<br>")
    safe_username = html.escape(username)
    safe_time = html.escape(time_str)

    # 1. Avatar bài viết / bình luận
    if avatar_url and os.path.exists(avatar_url):
        avatar_src = f"file:///{Path(avatar_url).resolve().as_posix()}"
        avatar_html = f'<img class="user-avatar" src="{avatar_src}" alt="avatar" />'
    elif avatar_url and (avatar_url.startswith("http://") or avatar_url.startswith("https://")):
        avatar_html = f'<img class="user-avatar" src="{avatar_url}" alt="avatar" />'
    else:
        initial = safe_username[0].upper() if safe_username else "H"
        colors = [
            ("linear-gradient(135deg, #00daf5, #7928ca)", "#ffffff"),
            ("linear-gradient(135deg, #ff0080, #7928ca)", "#ffffff"),
            ("linear-gradient(135deg, #0070f3, #00dfd8)", "#ffffff"),
            ("linear-gradient(135deg, #f5a623, #f8e71c)", "#111827"),
            ("linear-gradient(135deg, #10b981, #059669)", "#ffffff"),
        ]
        bg_color, text_color = colors[abs(hash(username)) % len(colors)]
        avatar_html = f'<div class="user-fallback" style="background: {bg_color}; color: {text_color};">{initial}</div>'

    # 2. Ảnh meme / Media bài viết
    post_media_html = ""
    if post_image_url:
        if os.path.exists(post_image_url):
            img_src = f"file:///{Path(post_image_url).resolve().as_posix()}"
            post_media_html = f'<div class="post-media-container"><img class="post-media-img" src="{img_src}" alt="media" /></div>'
        elif post_image_url.startswith("http://") or post_image_url.startswith("https://"):
            post_media_html = f'<div class="post-media-container"><img class="post-media-img" src="{post_image_url}" alt="media" /></div>'

    # 3. Badge Đang trả lời (Reply badge)
    reply_badge_html = ""
    if is_reply_to:
        reply_badge_html = f'<div class="reply-badge">Đang trả lời <span class="reply-target">@{html.escape(is_reply_to)}</span></div>'

    # 4. Brand Header (Đỉnh Video - Watermark nhận diện kênh)
    brand_header_html = ""
    if show_brand_header:
        b_avatar_file = Path(brand_avatar_path) if brand_avatar_path else _DEFAULT_BRAND_AVATAR
        if b_avatar_file.exists():
            b_src = f"file:///{b_avatar_file.resolve().as_posix()}"
            b_img_tag = f'<img class="brand-avatar" src="{b_src}" alt="brand" />'
        else:
            b_img_tag = '<div class="brand-avatar-fallback">H</div>'

        brand_header_html = f"""
        <div class="brand-header">
          {b_img_tag}
          <div class="brand-name">{html.escape(brand_title)}</div>
        </div>
        """

    # 5. Phối màu theo Theme
    if theme == "light":
        card_bg = "#ffffff"
        card_border = "1px solid rgba(0, 0, 0, 0.08)"
        card_shadow = "0 8px 30px rgba(0, 0, 0, 0.18)"
        text_color = "#0f1419"
        user_color = "#000000"
        muted_color = "#536471"
        icon_stroke = "#0f1419"
        reply_color = "#1d9bf0"
    elif theme == "hanshin":
        card_bg = "rgba(11, 15, 25, 0.94)"
        card_border = "1.5px solid #00daf5"
        card_shadow = "0 0 30px rgba(0, 218, 245, 0.35), 0 10px 36px rgba(0, 0, 0, 0.8)"
        text_color = "#ffffff"
        user_color = "#00daf5"
        muted_color = "#94a3b8"
        icon_stroke = "#00daf5"
        reply_color = "#38bdf8"
    else:  # 'dark' (Default chuẩn Pixel-Perfect Native Threads)
        card_bg = "#101010"
        card_border = "1px solid #282828"
        card_shadow = "0 10px 36px rgba(0, 0, 0, 0.75)"
        text_color = "#f3f5f7"
        user_color = "#f3f5f7"
        muted_color = "#71767b"
        icon_stroke = "#f3f5f7"
        reply_color = "#38bdf8"

    # Threads Logo SVG
    threads_logo_svg = f"""<svg viewBox="0 0 24 24" width="22" height="22" fill="{muted_color}"><path d="M12 2C6.477 2 2 6.477 2 12c0 5.523 4.477 10 10 10 3.328 0 6.27-1.625 8.082-4.116-.395-.316-.788-.636-1.184-.954C17.382 18.995 14.836 20.35 12 20.35c-4.612 0-8.35-3.738-8.35-8.35 0-4.612 3.738-8.35 8.35-8.35 4.542 0 8.243 3.627 8.347 8.143.003.11.003.22 0 .33-.09 3.033-1.644 4.707-4.14 4.707-1.42 0-2.483-.81-2.735-2.072 1.34-.693 2.185-1.99 2.185-3.608 0-2.315-1.785-4.1-4.1-4.1-2.315 0-4.1 1.785-4.1 4.1 0 2.315 1.785 4.1 4.1 4.1.88 0 1.688-.266 2.368-.73.498 1.433 1.83 2.36 3.422 2.36 3.35 0 5.49-2.228 5.6-5.997.004-.14.004-.28 0-.42C21.43 6.046 17.18 2 12 2zm-1.8 12.35c-1.38 0-2.45-1.07-2.45-2.45s1.07-2.45 2.45-2.45 2.45 1.07 2.45 2.45-1.07 2.45-2.45 2.45z"/></svg>"""

    # Three Dots Icon SVG (Icon góc phải của mỗi post)
    three_dots_svg = f"""<svg viewBox="0 0 24 24" width="20" height="20" fill="{muted_color}"><circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/></svg>"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    width: {width}px;
    height: {height}px;
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding-top: 130px;
    overflow: hidden;
  }}

  /* Brand Header (Watermark đỉnh) */
  .brand-header {{
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 35px;
  }}
  .brand-avatar {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid rgba(255, 255, 255, 0.95);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.85);
  }}
  .brand-avatar-fallback {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #00daf5, #7928ca);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 32px;
    font-weight: 900;
  }}
  .brand-name {{
    margin-top: 10px;
    font-size: 26px;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: 2px;
    text-transform: uppercase;
    text-shadow: 0 4px 14px rgba(0, 0, 0, 0.95);
  }}

  /* Thẻ Threads chuẩn Native Screenshot */
  .threads-card {{
    width: {card_width}px;
    background: {card_bg};
    border-radius: 18px;
    padding: 22px 24px;
    border: {card_border};
    box-shadow: {card_shadow};
    color: {text_color};
  }}

  /* Hàng tác giả trên cùng */
  .card-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }}
  .user-info {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .user-avatar {{
    width: 44px;
    height: 44px;
    border-radius: 50%;
    object-fit: cover;
    display: block;
  }}
  .user-fallback {{
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 18px;
  }}
  .user-names {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .username {{
    font-size: 20px;
    font-weight: 700;
    color: {user_color};
    line-height: 1.2;
  }}
  .dot {{
    color: {muted_color};
    font-size: 15px;
  }}
  .time-ago {{
    color: {muted_color};
    font-size: 15px;
    font-weight: 400;
  }}
  .top-right-icons {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  /* Badge Reply */
  .reply-badge {{
    font-size: 14px;
    color: {muted_color};
    margin-bottom: 10px;
    font-weight: 500;
  }}
  .reply-target {{
    color: {reply_color};
    font-weight: 600;
  }}

  /* Nội dung văn bản bài viết */
  .post-text {{
    font-size: 24px;
    font-weight: 400;
    line-height: 1.45;
    color: {text_color};
    margin-bottom: 14px;
    word-break: break-word;
    letter-spacing: -0.2px;
  }}

  /* Khung ảnh bài viết / Meme */
  .post-media-container {{
    width: 100%;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    overflow: hidden;
    margin-bottom: 14px;
    background: #000000;
  }}
  .post-media-img {{
    width: 100%;
    max-height: 480px;
    object-fit: contain;
    display: block;
  }}

  /* Thanh hành động (Like, Comment, Repost, Share) */
  .actions-row {{
    display: flex;
    align-items: center;
    gap: 24px;
    padding-top: 4px;
    color: {text_color};
  }}
  .action-btn {{
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 15px;
    color: {muted_color};
    font-weight: 500;
  }}
  .action-btn svg {{
    width: 22px;
    height: 22px;
    stroke: {icon_stroke};
    stroke-width: 1.8;
    fill: none;
  }}
</style>
</head>
<body>
  {brand_header_html}

  <div class="threads-card">
    <div class="card-top">
      <div class="user-info">
        {avatar_html}
        <div class="user-names">
          <span class="username">{safe_username}</span>
          <span class="dot">•</span>
          <span class="time-ago">{safe_time}</span>
        </div>
      </div>
      <div class="top-right-icons">
        {three_dots_svg}
        {threads_logo_svg}
      </div>
    </div>

    {reply_badge_html}

    <div class="post-text">{safe_content}</div>

    {post_media_html}

    <div class="actions-row">
      <div class="action-btn">
        <svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
        <span>{likes}</span>
      </div>
      <div class="action-btn">
        <svg viewBox="0 0 24 24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
        <span>{comments}</span>
      </div>
      <div class="action-btn">
        <svg viewBox="0 0 24 24"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>
        <span>{reposts}</span>
      </div>
      <div class="action-btn">
        <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
      </div>
    </div>
  </div>
</body>
</html>
"""

    temp_html = out_path.with_suffix(".html")
    temp_html.write_text(html_content, encoding="utf-8")

    cmd = [
        browser_exe,
        "--headless",
        "--disable-gpu",
        "--default-background-color=00000000",
        f"--window-size={width},{height}",
        f"--screenshot={str(out_path)}",
        f"file:///{temp_html.as_posix()}",
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    temp_html.unlink(missing_ok=True)

    return out_path

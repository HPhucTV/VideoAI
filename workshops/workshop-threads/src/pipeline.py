"""
Xưởng 5: Threads & Social Drama (workshop-threads)
Module: pipeline.py
Bộ điều phối trung tâm sản xuất video Threads chuẩn 9:16 cho kênh HanShin.
"""
from __future__ import annotations

import glob
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Thêm đường dẫn project root và src vào sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_WORKSHOP_DIR = Path(__file__).resolve().parent.parent
_SRC_DIR = Path(__file__).resolve().parent

for p in [_ROOT, _WORKSHOP_DIR, _SRC_DIR]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

_ASSETS_DIR = _WORKSHOP_DIR / "assets"
_BG_DIR = _ASSETS_DIR / "backgrounds"
_SFX_POP = _ASSETS_DIR / "sfx" / "pop.wav"
_BGM_DIR = _ASSETS_DIR / "bgm"
_CACHE_DIR = _WORKSHOP_DIR / "cache"

from tts_engine import synthesize_speech, detect_emotion
from card_engine import render_card
from compositor import make_threads_video
from scraper import cache_media

logger = logging.getLogger("workshop_threads.pipeline")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def build_threads_video(
    thread_data: Dict[str, Any],
    job_id: Optional[str] = None,
    output_dir: Optional[str | Path] = None,
    theme: str = "dark",
    background_path: Optional[str | Path] = None,
    bgm_path: Optional[str | Path] = None,
    bgm_style: Optional[str] = "comedy_sneaky",
    bgm_volume: float = 0.38,
    enable_ducking: bool = True,
    default_male_voice: str = "vi-VN-NamMinhNeural",
    default_female_voice: str = "vi-VN-HoaiMyNeural",
    enable_spring_pop: bool = True,
    enable_karaoke: bool = False,
    publish_youtube: bool = False,
    privacy: str = "unlisted",
) -> Dict[str, Any]:
    """
    Quy trình sản xuất tự động toàn diện Xưởng 5:
    1. Phân tích cảm xúc & Sinh TTS giọng đọc đối thoại tiếng Việt (NamMinh / HoaiMy + Slang + Emotion Pitch Modulation).
    2. Render các thẻ Threads / HanShin chuẩn PNG trong suốt (Nested Threads View + AMOLED #101010).
    3. Ghép video nền gameplay + Smart Emotional SFX (Vine Boom, Huh, Pop, Whoosh) + hiệu ứng nảy Spring Pop + Karaoke Highlight.
    4. Xuất video MP4 chuẩn định dạng TikTok/Reels/Shorts.
    5. Tùy chọn đẩy lên YouTube kênh HanShin qua Cổng 7.
    """
    session_id = job_id or f"threads_{int(time.time())}"
    base_out = Path(output_dir) if output_dir else _ROOT / "output" / "threads" / session_id
    base_out.mkdir(parents=True, exist_ok=True)

    session_cache = _CACHE_DIR / session_id
    session_cache.mkdir(parents=True, exist_ok=True)

    logger.info("🎬 [XƯỞNG 5] Bắt đầu sản xuất video Threads: %s (Theme: %s)", session_id, theme)

    # 1. Xác định video nền (Ưu tiên Minecraft / Gameplay theo chuẩn Xưởng 5)
    bg_video = None
    if background_path and Path(background_path).exists():
        bg_video = Path(background_path).resolve()
    else:
        mc_candidates = list(_BG_DIR.glob("*minecraft*.mp4")) or list(_BG_DIR.glob("*parkour*.mp4"))
        if mc_candidates:
            bg_video = mc_candidates[0]
        else:
            bg_candidates = list(_BG_DIR.glob("*.mp4"))
            if bg_candidates:
                bg_video = bg_candidates[0]
            else:
                raise FileNotFoundError(f"Không tìm thấy video nền nào trong {_BG_DIR}")

    logger.info("Video nền sử dụng: %s", bg_video.name)

    segments = []

    # 2. Xử lý bài viết chính (Main Post)
    post = thread_data.get("post", {})
    post_voice = post.get("voice", default_female_voice)
    post_content = post.get("content", "")
    post_tts = post.get("tts_content", post_content)
    post_audio = session_cache / "post_voice.mp3"

    post_emo = detect_emotion(post_content)
    post_rate = post.get("rate", post_emo.get("rate", "+25%"))
    post_pitch = post.get("pitch", post_emo.get("pitch", "+0Hz"))
    post_sfx = post.get("sfx", post_emo.get("sfx", "pop.wav"))
    post_shake = post.get("shake", post_emo.get("shake", False))

    logger.info("Sinh âm thanh cho Post chính (Emotion: %s, Rate: %s, Pitch: %s)...", post_emo["emotion"], post_rate, post_pitch)
    post_dur = synthesize_speech(
        text=post_tts,
        out_file=post_audio,
        voice=post_voice,
        rate=post_rate,
        pitch=post_pitch,
    )

    # Cache avatar & post media
    avatar_cached = cache_media(post.get("avatar_url"), session_cache / "avatars", prefix="post_avatar")
    post_img_cached = cache_media(post.get("post_image_url"), session_cache / "media", prefix="post_img")

    post_card_png = session_cache / "post_card.png"
    render_card(
        username=post.get("username", "threads_user"),
        time_str=post.get("time", "vừa xong"),
        content=post_content,
        output_png=post_card_png,
        avatar_url=avatar_cached,
        post_image_url=post_img_cached,
        likes=str(post.get("likes", "1.8K")),
        comments=str(post.get("comments", "356")),
        reposts=str(post.get("reposts", "24")),
        hook_badge=post.get("hook_badge"),
        theme=theme,
    )

    segments.append({
        "card_png": str(post_card_png),
        "audio_mp3": str(post_audio),
        "duration": post_dur,
        "text": post_tts,
        "sfx": post_sfx,
        "shake": post_shake,
    })

    # 3. Xử lý chuỗi bình luận (Comments) với Nested Parent Thread UI
    parent_ctx = {
        "username": post.get("username", "threads_user"),
        "time": post.get("time", "1 ngày"),
        "content": post_content,
        "avatar_url": avatar_cached,
    }

    comments = thread_data.get("comments", [])
    for idx, c in enumerate(comments):
        c_voice = c.get("voice", default_female_voice if idx % 2 == 0 else default_male_voice)
        c_content = c.get("content", "")
        c_tts = c.get("tts_content", c_content)
        c_audio = session_cache / f"comment_{idx}_voice.mp3"

        c_emo = detect_emotion(c_content)
        c_rate = c.get("rate", c_emo.get("rate", "+25%"))
        c_pitch = c.get("pitch", c_emo.get("pitch", "+0Hz"))
        c_sfx = c.get("sfx", c_emo.get("sfx", "pop.wav"))
        c_shake = c.get("shake", c_emo.get("shake", False))

        c_dur = synthesize_speech(
            text=c_tts,
            out_file=c_audio,
            voice=c_voice,
            rate=c_rate,
            pitch=c_pitch,
        )

        c_avatar_cached = cache_media(c.get("avatar_url"), session_cache / "avatars", prefix=f"c_{idx}_avatar")
        c_card_png = session_cache / f"comment_{idx}_card.png"

        render_card(
            username=c.get("username", f"user_{idx+1}"),
            time_str=c.get("time", "vừa xong"),
            content=c_content,
            output_png=c_card_png,
            avatar_url=c_avatar_cached,
            likes=str(c.get("likes", "45")),
            comments=str(c.get("comments", "3")),
            reposts=str(c.get("reposts", "1")),
            parent_context=parent_ctx,
            theme=theme,
        )

        segments.append({
            "card_png": str(c_card_png),
            "audio_mp3": str(c_audio),
            "duration": c_dur,
            "text": c_tts,
            "sfx": c_sfx,
            "shake": c_shake,
        })

    # 4. Lắp ráp video hoàn chỉnh
    final_video_name = f"{session_id}.mp4"
    final_video_path = base_out / final_video_name

    sfx_path = _SFX_POP if _SFX_POP.exists() else None
    bgm_selected = Path(bgm_path) if bgm_path and Path(bgm_path).exists() else None
    if not bgm_selected:
        style_key = (bgm_style or "comedy_sneaky").lower().strip()
        if "monkey" in style_key:
            target_bgm = _BGM_DIR / "comedy_monkeys.mp3"
        elif "lofi" in style_key or "chill" in style_key:
            target_bgm = _BGM_DIR / "lofi_chill.mp3"
        elif "drama" in style_key or "suspense" in style_key:
            target_bgm = _BGM_DIR / "drama_suspense.mp3"
        else:
            target_bgm = _BGM_DIR / "comedy_sneaky.mp3"

        if target_bgm.exists():
            bgm_selected = target_bgm
        else:
            bgm_files = list(_BGM_DIR.glob("*.mp3"))
            if bgm_files:
                bgm_selected = bgm_files[0]

    logger.info("Nhạc nền sử dụng: %s (Volume: %.2f, Ducking: %s)", bgm_selected.name if bgm_selected else "None", bgm_volume, enable_ducking)
    logger.info("Ghép nối video hoàn chỉnh qua FFmpeg (Spring Pop, Dynamic Ducking & Authentic Meme SFX)...")
    make_threads_video(
        background_path=bg_video,
        segments=segments,
        output_path=final_video_path,
        sfx_pop_path=sfx_path,
        bgm_path=bgm_selected,
        width=1080,
        height=1920,
        pause_between=0.35,
        enable_spring_pop=enable_spring_pop,
        enable_karaoke=enable_karaoke,
        bgm_volume=bgm_volume,
        enable_ducking=enable_ducking,
    )

    logger.info("🎉 Video thành phẩm đã sẵn sàng: %s", final_video_path)

    # 5. Cổng 7: Xuất bản YouTube Shorts nếu được yêu cầu
    youtube_result = None
    if publish_youtube:
        try:
            from scripts.youtube_publisher import upload_unlisted_video
            raw_title = post.get("content", "Câu chuyện Threads viral").replace("\n", " ").strip()
            clean_title = re.sub(r"\s+", " ", raw_title)
            video_title = f"{clean_title[:60]} #Shorts #Threads"
            desc = f"{post.get('content', '')}\n\nTheo dõi kênh @HanShin-g8i để nghe thêm nhiều câu chuyện hay!\n#HanShin #Threads #Shorts"
            tags = ["HanShin", "Threads", "Shorts", "Reddit", "Drama", "Story"]

            youtube_result = upload_unlisted_video(
                channel_name="HanShin",
                video_path=final_video_path,
                title=video_title,
                description=desc,
                tags=tags,
                privacy_status=privacy,
                category_id="24",
            )
            logger.info("Đã xuất bản lên YouTube HanShin: %s", youtube_result.get("url"))
        except Exception as e:
            logger.warning("Không thể xuất bản YouTube tự động: %s", e)

    return {
        "status": "success",
        "job_id": session_id,
        "video_path": str(final_video_path),
        "total_segments": len(segments),
        "theme": theme,
        "youtube": youtube_result,
    }

import pytest
from pathlib import Path
from PIL import Image

from scripts.master_assembly_engine import (
    get_font,
    format_srt_time,
    generate_srt_file,
    generate_cyber_chatbox_overlay,
    generate_3d_thumbnail,
)


def test_format_srt_time():
    assert format_srt_time(0.0) == "00:00:00,000"
    assert format_srt_time(2.0) == "00:00:02,000"
    assert format_srt_time(65.123) == "00:01:05,123"
    assert format_srt_time(3661.05) == "01:01:01,050"


def test_generate_cyber_chatbox_overlay(tmp_path):
    out_png = tmp_path / "overlay_test.png"
    speaker = "BÉ BYTE (AI AGENT)"
    text = "Đây là câu thoại kiểm thử khung chatbox chuẩn điện ảnh."

    generate_cyber_chatbox_overlay(speaker=speaker, text=text, out_path=out_png)

    assert out_png.exists()
    assert out_png.stat().st_size > 0
    with Image.open(out_png) as img:
        assert img.size == (1920, 1080)
        assert img.mode == "RGBA"


def test_generate_srt_file(tmp_path):
    out_srt = tmp_path / "subtitles_test.srt"
    shots = [
        {
            "shot": 1,
            "duration": 4.0,
            "dialogue": "Đây là câu thoại kiểm thử chuẩn điện ảnh.",
        },
        {
            "shot": 2,
            "duration": 5.5,
            "dialogue": "Shot tiếp theo trong kịch bản 5 hồi.",
        },
    ]
    generate_srt_file(shots, out_srt, intro_offset=2.0)

    assert out_srt.exists()
    content = out_srt.read_text(encoding="utf-8")
    assert "00:00:02,000 --> 00:00:06,000" in content
    assert "00:00:06,000 --> 00:00:11,500" in content
    assert "Đây là câu thoại kiểm thử chuẩn điện ảnh." in content
    assert "Shot tiếp theo trong kịch bản 5 hồi." in content


def test_generate_3d_thumbnail_fallback(tmp_path):
    out_thumb = tmp_path / "thumb_fallback.jpg"
    generate_3d_thumbnail(
        hero_frame=None,
        hook_title="AI AGENT ĐỘT PHÁ 2026",
        out_path=out_thumb,
    )
    assert out_thumb.exists()
    assert out_thumb.stat().st_size > 0
    with Image.open(out_thumb) as img:
        assert img.size == (1920, 1080)


def test_generate_3d_thumbnail_with_hero(tmp_path):
    hero_frame = tmp_path / "hero.png"
    hero_img = Image.new("RGB", (1280, 720), (20, 30, 50))
    hero_img.save(hero_frame)

    out_thumb = tmp_path / "thumb_hero.jpg"
    generate_3d_thumbnail(
        hero_frame=hero_frame,
        hook_title="KỶ NGUYÊN TỰ CHỦ 2026",
        out_path=out_thumb,
    )
    assert out_thumb.exists()
    assert out_thumb.stat().st_size > 0

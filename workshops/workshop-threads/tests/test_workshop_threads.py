import sys
from pathlib import Path

# Setup paths
root_dir = Path(__file__).resolve().parent.parent.parent.parent
workshop_dir = Path(__file__).resolve().parent.parent
src_dir = workshop_dir / "src"

for p in [root_dir, workshop_dir, src_dir]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from tts_engine import normalize_slang, detect_emotion
from card_engine import render_card, find_browser_executable
from compositor import generate_karaoke_ass
from scraper import parse_raw_text_thread


def test_slang_normalizer():
    raw_text = "Hôm nay đi first date mà bạn ý bắt share bill qua ck, đt thì hết pin ko biết làm ntn"
    normalized = normalize_slang(raw_text)
    assert "hẹn hò lần đầu" in normalized
    assert "chia tiền" in normalized
    assert "chuyển khoản" in normalized
    assert "điện thoại" in normalized
    assert "không" in normalized
    assert "như thế nào" in normalized


def test_detect_emotion():
    e_shock = detect_emotion("Má y chang luôn!")
    assert e_shock["emotion"] == "shock"
    assert e_shock["sfx"] == "vine_boom.wav"
    assert e_shock["shake"] is True

    e_question = detect_emotion("Mấy câu này khó hiểu là sao?")
    assert e_question["emotion"] == "question"
    assert e_question["sfx"] == "huh.wav"

    e_sad = detect_emotion("đau không gì bằng...")
    assert e_sad["emotion"] == "sad"
    assert e_sad["pitch"] == "-3Hz"


def test_generate_karaoke_ass(tmp_path):
    timeline = [
        {"start": 0.0, "end": 2.0, "text": "Học sinh hai ca chín", "duration": 2.0}
    ]
    out_ass = tmp_path / "karaoke.ass"
    generate_karaoke_ass(timeline, out_ass)
    assert out_ass.exists()
    content = out_ass.read_text(encoding="utf-8")
    assert "Style: Karaoke" in content
    assert "\\k" in content
    assert "Học" in content


def test_nested_thread_card(tmp_path):
    out_png = tmp_path / "test_nested.png"
    rendered = render_card(
        username="commenter_1",
        time_str="1 giờ",
        content="Đây là câu trả lời kiểm thử cây hội thoại",
        output_png=out_png,
        parent_context={
            "username": "op_author",
            "time": "2 giờ",
            "content": "Đây là bài viết gốc cần được kết nối qua thread line",
        },
        theme="dark",
        width=720,
        height=1280,
    )
    assert rendered.exists()
    assert rendered.stat().st_size > 0


def test_parse_raw_text_thread():
    sample_text = """@hvy2908 | 12 giờ
Con trai chung thủy thật thà chết hết rồi à?
---
@dmin.music | 2 giờ
Không phải chết hết, mà trước giờ có tồn tại đâu."""
    res = parse_raw_text_thread(sample_text)
    assert res["post"]["username"] == "hvy2908"
    assert "chung thủy" in res["post"]["content"]
    assert len(res["comments"]) == 1
    assert res["comments"][0]["username"] == "dmin.music"


def test_render_card_png(tmp_path):
    browser = find_browser_executable()
    assert Path(browser).exists()

    out_png = tmp_path / "test_card.png"
    rendered = render_card(
        username="HanShin",
        time_str="1 giờ",
        content="Đây là nội dung kiểm thử thẻ bài viết phong cách Cyber Neon cho kênh HanShin.",
        output_png=out_png,
        theme="hanshin",
        width=720,
        height=1280,
    )
    assert rendered.exists()
    assert rendered.stat().st_size > 0

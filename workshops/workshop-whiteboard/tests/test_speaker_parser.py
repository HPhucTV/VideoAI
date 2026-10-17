import pytest
import sys
from pathlib import Path

root_wb = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_wb))

from job_adapter import sanitize_dialogue_text, parse_dialogue_segments, resolve_speaker_voice


def test_sanitize_dialogue_narrator_prefix():
    text = "Người Kể Chuyện: Tiên sơn vạn trượng, ngút ngàn mây trắng."
    known = ["Người Kể Chuyện", "Lâm Mặc"]
    spk, clean = sanitize_dialogue_text(text, known_speakers=known)
    assert spk == "Người Kể Chuyện"
    assert clean == "Tiên sơn vạn trượng, ngút ngàn mây trắng."
    assert "Người Kể Chuyện:" not in clean


def test_sanitize_dialogue_character_with_expression():
    text = "Sở Thiên Kiêu (lạnh lùng): Các ngươi quỳ xuống cho ta!"
    known = ["Sở Thiên Kiêu"]
    spk, clean = sanitize_dialogue_text(text, known_speakers=known)
    assert spk == "Sở Thiên Kiêu"
    assert clean == "Các ngươi quỳ xuống cho ta!"
    assert ":" not in clean


def test_sanitize_dialogue_narrative_colon_preserved():
    text = "Hắn gầm lên: Ngươi dám sao?!"
    known = ["Lâm Mặc", "Người Kể Chuyện"]
    spk, clean = sanitize_dialogue_text(text, known_speakers=known)
    # Không phải tên nhân vật vì có động từ tường thuật
    assert spk is None
    assert clean == "Hắn gầm lên: Ngươi dám sao?!"


def test_sanitize_dialogue_time_colon_preserved():
    text = "Lúc 10:30 sáng, lò đan bốc hỏa dữ dội."
    known = ["Lâm Mặc"]
    spk, clean = sanitize_dialogue_text(text, known_speakers=known)
    assert spk is None
    assert clean == "Lúc 10:30 sáng, lò đan bốc hỏa dữ dội."


def test_parse_dialogue_segments_no_colon_in_narrator():
    text = "Lâm Mặc: Ta không phục!"
    known = ["Lâm Mặc"]
    segs = parse_dialogue_segments(text, known_speakers=known)
    assert len(segs) == 1
    assert segs[0]["speaker"] == "Lâm Mặc"
    assert segs[0]["text"] == "Ta không phục!"
    assert ":" not in segs[0]["text"]


def test_parse_dialogue_simple_script():
    text = (
        "Hạ Vi: Tiệm đóng cửa từ chín giờ tối rồi anh.\n"
        "Đình Phong: Tôi không đến trú mưa. Ra giá đi."
    )
    segments = parse_dialogue_segments(text)
    assert len(segments) == 2
    assert segments[0]["speaker"] == "Hạ Vi"
    assert segments[0]["text"] == "Tiệm đóng cửa từ chín giờ tối rồi anh."
    assert segments[1]["speaker"] == "Đình Phong"
    assert segments[1]["text"] == "Tôi không đến trú mưa. Ra giá đi."


def test_parse_dialogue_with_parenthesis():
    text = "Hạ Vi (Không ngẩng đầu lên, giọng điềm nhiên): Tiệm đóng cửa từ chín giờ tối rồi anh."
    segments = parse_dialogue_segments(text)
    assert len(segments) == 1
    assert segments[0]["speaker"] == "Hạ Vi"
    assert segments[0]["text"] == "Tiệm đóng cửa từ chín giờ tối rồi anh."


def test_parse_dialogue_embedded_narrative():
    text = (
        "Hạ Vi vẫn không ngẩng đầu lên, giọng nói điềm nhiên như mặt hồ phẳng lặng: "
        "Tiệm đóng cửa từ chín giờ tối rồi anh. Khăn khô trong ngăn kéo thứ hai. "
        "Đình Phong bước thẳng tới trước bàn làm việc, lạnh lùng rút tấm danh thiếp mạ vàng đặt xuống: "
        "Tôi không đến trú mưa. Tôi trả gấp mười lần."
    )
    known_speakers = ["Hạ Vi", "Đình Phong"]
    segments = parse_dialogue_segments(text, known_speakers=known_speakers)
    assert len(segments) == 4
    assert segments[0]["speaker"] == "narrator"
    assert "Hạ Vi vẫn không ngẩng đầu lên" in segments[0]["text"]
    assert segments[1]["speaker"] == "Hạ Vi"
    assert "Tiệm đóng cửa từ chín giờ tối" in segments[1]["text"]
    assert segments[2]["speaker"] == "narrator"
    assert "Đình Phong bước thẳng tới" in segments[2]["text"]
    assert segments[3]["speaker"] == "Đình Phong"
    assert "Tôi không đến trú mưa" in segments[3]["text"]


def test_parse_dialogue_no_dialogue_defaults_to_narrator():
    text = "Đêm muộn ở thủ đô, cơn mưa rào đầu mùa hạ bất ngờ đổ ập xuống con phố cổ."
    segments = parse_dialogue_segments(text)
    assert len(segments) == 1
    assert segments[0]["speaker"] == "narrator"
    assert segments[0]["text"] == text


def test_resolve_speaker_voice_roles():
    meta = {
        "characters_voice": {
            "lâm mặc": {"voice": "vi-VN-NamMinhNeural", "rate": "+20%", "pitch": "-3Hz"}
        }
    }
    # Khớp override từ metadata
    v_hero = resolve_speaker_voice("Lâm Mặc", job_meta=meta)
    assert v_hero["pitch"] == "-3Hz"
    assert v_hero["rate"] == "+20%"

    # Trưởng lão phản diện (preset role)
    v_elder = resolve_speaker_voice("Triệu Trưởng Lão")
    assert v_elder["pitch"] == "-6Hz"
    assert v_elder["rate"] == "+10%"

    # Nữ nhân / thiếu niên (preset role)
    v_girl = resolve_speaker_voice("Tiểu Thạch Đầu")
    assert v_girl["voice"] == "vi-VN-HoaiMyNeural"

    # Thanh niên ngạo mạn (preset role)
    v_young = resolve_speaker_voice("Sở Công Tử")
    assert v_young["pitch"] == "+3Hz"
    assert v_young["rate"] == "+25%"

    # Narrator mặc định cho storytelling là +25%
    v_narrator = resolve_speaker_voice("Người Kể Chuyện")
    assert v_narrator["rate"] == "+25%"


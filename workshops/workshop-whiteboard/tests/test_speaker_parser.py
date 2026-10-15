import pytest
import sys
from pathlib import Path

root_wb = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_wb))

from job_adapter import parse_dialogue_segments, resolve_speaker_voice


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


def test_resolve_speaker_voice():
    # Female voice
    hawi_cfg = resolve_speaker_voice("Hạ Vi")
    assert hawi_cfg["voice"] == "vi-VN-HoaiMyNeural"

    # Male boss voice (deeper pitch)
    boss_cfg = resolve_speaker_voice("Đình Phong")
    assert boss_cfg["voice"] == "vi-VN-NamMinhNeural"
    assert boss_cfg["pitch"] == "-5Hz"

    # Assistant voice (higher pitch, faster rate)
    kien_cfg = resolve_speaker_voice("Trợ lý Kiên")
    assert kien_cfg["voice"] == "vi-VN-NamMinhNeural"
    assert kien_cfg["pitch"] == "+2Hz"

    # Narrator voice (calm, slightly slower)
    narr_cfg = resolve_speaker_voice("narrator")
    assert narr_cfg["voice"] == "vi-VN-NamMinhNeural"
    assert narr_cfg["rate"] == "-4%"

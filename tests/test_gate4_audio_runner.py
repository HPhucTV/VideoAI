import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from scripts.gate4_audio_runner import (
    CHARACTER_VOICE_MODULATION,
    get_audio_duration_ffprobe,
    synthesize_voice_clip,
    run_gate4_audio,
)


def test_run_gate4_audio(tmp_path):
    job_data = {
        "jobId": "job-audio-test",
        "beats": [
            {"id": "b1", "speaker": "Lâm Mặc", "rawText": "Kiếm ý nghịch thiên 1.000.000 đồng!"}
        ],
    }
    with patch("scripts.gate4_audio_runner.synthesize_voice_clip", return_value=(tmp_path / "b1.mp3", 4.5)):
        manifest = run_gate4_audio(job_data, output_dir=tmp_path)
        assert manifest["jobId"] == "job-audio-test"
        assert manifest["total_shots"] == 1
        assert len(manifest["shots"]) == 1
        assert manifest["shots"][0]["duration"] == 4.5
        assert manifest["total_duration"] == 4.5
        manifest_file = tmp_path / "audio" / "audio_manifest.json"
        assert manifest_file.exists()


def test_character_voice_modulation_profiles():
    assert "nam_chinh" in CHARACTER_VOICE_MODULATION
    assert CHARACTER_VOICE_MODULATION["nam_chinh"]["voice"] == "vi-VN-NamMinhNeural"
    assert CHARACTER_VOICE_MODULATION["nam_chinh"]["rate"] == "+22%"
    assert CHARACTER_VOICE_MODULATION["nam_chinh"]["pitch"] == "-4Hz"

    assert "phan_dien" in CHARACTER_VOICE_MODULATION
    assert CHARACTER_VOICE_MODULATION["phan_dien"]["rate"] == "+30%"
    assert CHARACTER_VOICE_MODULATION["phan_dien"]["pitch"] == "+3Hz"

    assert "truong_boi" in CHARACTER_VOICE_MODULATION
    assert CHARACTER_VOICE_MODULATION["truong_boi"]["rate"] == "+20%"
    assert CHARACTER_VOICE_MODULATION["truong_boi"]["pitch"] == "-6Hz"

    assert "nu_chinh" in CHARACTER_VOICE_MODULATION
    assert CHARACTER_VOICE_MODULATION["nu_chinh"]["voice"] == "vi-VN-HoaiMyNeural"
    assert CHARACTER_VOICE_MODULATION["nu_chinh"]["rate"] == "+23%"
    assert CHARACTER_VOICE_MODULATION["nu_chinh"]["pitch"] == "+1Hz"

    assert "narrator" in CHARACTER_VOICE_MODULATION
    assert CHARACTER_VOICE_MODULATION["narrator"]["voice"] == "vi-VN-NamMinhNeural"
    assert CHARACTER_VOICE_MODULATION["narrator"]["rate"] == "+25%"
    assert CHARACTER_VOICE_MODULATION["narrator"]["pitch"] == "-2Hz"


def test_get_audio_duration_ffprobe(tmp_path):
    dummy_file = tmp_path / "dummy.mp3"
    dummy_file.write_text("audio data")
    mock_res = MagicMock()
    mock_res.stdout = "4.567\n"

    with patch("subprocess.run", return_value=mock_res) as mock_run:
        dur = get_audio_duration_ffprobe(dummy_file)
        assert dur == 4.57
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "ffprobe" in cmd[0]
        assert str(dummy_file) in cmd


def test_synthesize_voice_clip_mock(tmp_path):
    out_mp3 = tmp_path / "test.mp3"
    with patch("scripts.gate4_audio_runner.get_audio_duration_ffprobe", return_value=3.25):
        with patch("edge_tts.Communicate") as mock_comm_cls:
            mock_comm_instance = MagicMock()
            mock_comm_instance.save = AsyncMock()
            mock_comm_cls.return_value = mock_comm_instance

            res_path, dur = synthesize_voice_clip("Xin chào", "nam_chinh", out_mp3)
            assert res_path == out_mp3
            assert dur == 3.25
            mock_comm_cls.assert_called_once_with(
                "Xin chào",
                "vi-VN-NamMinhNeural",
                rate="+22%",
                pitch="-4Hz"
            )
            mock_comm_instance.save.assert_called_once_with(str(out_mp3))

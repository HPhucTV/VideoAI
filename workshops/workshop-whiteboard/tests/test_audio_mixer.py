import pytest
import sys
from pathlib import Path

root_wb = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_wb))
scripts_dir = root_wb / "scripts"
sys.path.insert(0, str(scripts_dir))

from audio_mixer import build_ducking_filter_complex, resolve_bgm_path


def test_build_ducking_filter_complex():
    filter_str = build_ducking_filter_complex(
        bgm_base_vol=0.35,
        duck_ratio=6.0,
        attack_ms=100,
        release_ms=700,
    )
    assert "[1:a]volume=0.35[bgm]" in filter_str
    assert "sidechaincompress=" in filter_str
    assert "ratio=6.0" in filter_str
    assert "attack=100" in filter_str
    assert "release=700" in filter_str
    assert "amix=" in filter_str
    assert "duration=first" in filter_str


def test_resolve_bgm_path_custom(tmp_path):
    custom_bgm = tmp_path / "my_music.mp3"
    custom_bgm.write_text("mp3")
    resolved = resolve_bgm_path(custom_bgm, root_dir=tmp_path)
    assert resolved == custom_bgm


def test_resolve_bgm_path_none(tmp_path):
    # None returns None or default if exists
    resolved = resolve_bgm_path(None, root_dir=tmp_path)
    # Default does not exist in tmp_path, so returns None
    assert resolved is None

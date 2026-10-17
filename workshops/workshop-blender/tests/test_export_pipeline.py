import pytest
import sys
import json
from pathlib import Path

scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from export_3d_video import (
    find_blender_binary,
    build_blender_ducking_filter,
    resolve_bgm_track,
    get_media_duration,
    synthesize_beat_audio,
    export_3d_video,
)

def test_find_blender_binary():
    bin_path = find_blender_binary()
    assert bin_path is not None
    assert Path(bin_path).exists()
    assert "blender" in Path(bin_path).name.lower()

def test_build_blender_ducking_filter():
    f = build_blender_ducking_filter(
        total_duration_sec=10.0,
        bgm_base_vol=0.25,
        duck_ratio=6.0,
        fade_out_sec=2.0,
        target_lufs=-14.0,
    )
    assert "sidechaincompress=" in f
    assert "normalize=0" in f
    assert "afade=t=out:st=8.00:d=2.00" in f
    assert "loudnorm=I=-14.0" in f

def test_resolve_bgm_track():
    bgm = resolve_bgm_track(None)
    # Phải tìm được bản BGM mặc định trong repo nếu tồn tại
    assert bgm is None or Path(bgm).exists()

def test_resolve_bgm_track_custom(tmp_path):
    dummy_bgm = tmp_path / "custom_bgm.mp3"
    dummy_bgm.write_text("dummy")
    resolved = resolve_bgm_track(str(dummy_bgm))
    assert resolved == dummy_bgm.resolve()

def test_get_media_duration():
    bgm = resolve_bgm_track(None)
    if bgm and Path(bgm).exists():
        dur = get_media_duration(bgm)
        assert dur > 0.0

def test_synthesize_beat_audio_silence(tmp_path):
    out_file = tmp_path / "silence.mp3"
    synthesize_beat_audio("", {}, out_file)
    assert out_file.exists()
    dur = get_media_duration(out_file)
    assert 0.8 <= dur <= 1.2

def test_export_3d_video_dry_run(tmp_path):
    # Tạo mock job json với 1 beat ngắn
    job_data = {
        "jobId": "job-test-dry-run",
        "canvas": {"width": 1280, "height": 720, "fps": 30},
        "metadata": {
            "characters": ["Lâm Mặc"]
        },
        "beats": [
            {
                "id": "beat_01",
                "role": "hook_teaser",
                "speaker": "Lâm Mặc",
                "rawText": "Kiếm ý nghịch thiên!",
                "cues": {"camera": "zoom_in_punch"}
            }
        ]
    }
    job_file = tmp_path / "test_job.json"
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(job_data, f, ensure_ascii=False)

    out = export_3d_video(
        job_path_or_id=job_file,
        resolution="720p",
        fps=30,
        dry_run=True,
    )
    assert out.name == "job-test-dry-run.mp4"
    assert "output" in str(out)
    assert "blender" in str(out)

import json
import pytest
import sys
from pathlib import Path

root_wb = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_wb))
scripts_dir = root_wb / "scripts"
sys.path.insert(0, str(scripts_dir))

from export_metadata import generate_youtube_metadata, format_youtube_timestamp


def test_format_youtube_timestamp():
    assert format_youtube_timestamp(0) == "00:00"
    assert format_youtube_timestamp(65) == "01:05"
    assert format_youtube_timestamp(3665) == "01:01:05"


def test_generate_youtube_metadata(tmp_path):
    job_data = {
        "jobId": "job-test",
        "title": "Bản Hợp Đồng Lúc 0 Giờ",
        "metadata": {
            "genre": "Ngôn tình hiện đại, Tổng tài, Chữa lành",
            "characters": ["Trần Đình Phong", "Lâm Hạ Vi"],
            "tags": ["ngon tinh", "tong tai", "chua lanh"]
        }
    }
    job_file = tmp_path / "job-test.json"
    job_file.write_text(json.dumps(job_data, ensure_ascii=False), encoding="utf-8")

    scene_data = [
        {"scene_id": "scene-01", "title": "Vị khách không mời lúc nửa đêm", "duration_sec": 121.4},
        {"scene_id": "scene-02", "title": "Liều thuốc ngủ đắt giá nhất", "duration_sec": 180.0},
    ]

    out_md = tmp_path / "YOUTUBE_METADATA.md"
    generate_youtube_metadata(job_file, scene_data, out_md)

    assert out_md.exists()
    content = out_md.read_text(encoding="utf-8")
    assert "00:00 - Phân cảnh 1: Vị khách không mời lúc nửa đêm" in content
    assert "02:01 - Phân cảnh 2: Liều thuốc ngủ đắt giá nhất" in content
    assert "Bản Hợp Đồng Lúc 0 Giờ" in content
    assert "#TruyenAudio" in content

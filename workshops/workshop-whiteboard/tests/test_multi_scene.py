import pytest
import sys
from pathlib import Path

root_wb = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_wb))

from job_adapter import (
    cluster_beats_into_scenes,
    fmt_srt_time,
    generate_image_prompt_md,
)

def test_cluster_beats_into_scenes():
    beats = []
    for i in range(1, 13):
        chapter = "CHƯƠNG I" if i <= 4 else ("CHƯƠNG II" if i <= 9 else "CHƯƠNG III")
        beats.append({
            "id": f"beat_{i:02d}",
            "rawText": f"Noi dung cau {i}",
            "visual": {
                "headline": f"Tieu de {i}",
                "badge": chapter
            }
        })

    scenes = cluster_beats_into_scenes(beats, max_beats_per_scene=4)
    # Tightened assertions: exactly 4 scenes with [4, 4, 1, 3] distribution
    assert len(scenes) == 4
    assert [len(s["beats"]) for s in scenes] == [4, 4, 1, 3]
    for s_idx, s in enumerate(scenes):
        assert len(s["beats"]) <= 4
        assert s["sceneId"] == f"scene-{s_idx+1:02d}"

def test_cluster_empty_beats():
    assert cluster_beats_into_scenes([]) == []

def test_cluster_by_scene_id():
    beats = [
        {"id": "b1", "visual": {"sceneId": "sc1"}},
        {"id": "b2", "visual": {"sceneId": "sc1"}},
        {"id": "b3", "visual": {"sceneId": "sc2"}},
    ]
    scenes = cluster_beats_into_scenes(beats, max_beats_per_scene=4)
    assert len(scenes) == 2
    assert len(scenes[0]["beats"]) == 2
    assert scenes[0]["sceneId"] == "scene-01"
    assert len(scenes[1]["beats"]) == 1
    assert scenes[1]["sceneId"] == "scene-02"

def test_cluster_default_badge():
    beats = [
        {"id": f"b{i}", "visual": {}} for i in range(1, 6)
    ]
    scenes = cluster_beats_into_scenes(beats, max_beats_per_scene=4)
    assert len(scenes) == 2
    assert scenes[0]["badge"] == "PHÂN CẢNH 1"
    assert scenes[1]["badge"] == "PHÂN CẢNH 2"

def test_fmt_srt_time_and_zero_based_timeline():
    # Verify SRT formatting starting at 00:00:00,000
    assert fmt_srt_time(0) == "00:00:00,000"
    assert fmt_srt_time(1500) == "00:00:01,500"
    assert fmt_srt_time(65432) == "00:01:05,432"
    assert fmt_srt_time(3661005) == "01:01:01,005"

    # Simulate local scene timeline starting at 0ms
    local_current_ms = 0
    beat_durations = [3200, 4500]
    local_srt_entries = []
    for dur in beat_durations:
        start_ms = local_current_ms
        end_ms = start_ms + dur
        local_srt_entries.append((fmt_srt_time(start_ms), fmt_srt_time(end_ms)))
        local_current_ms = end_ms + 250

    assert local_srt_entries[0][0] == "00:00:00,000"
    assert local_srt_entries[0][1] == "00:00:03,200"
    assert local_srt_entries[1][0] == "00:00:03,450"
    assert local_srt_entries[1][1] == "00:00:07,950"

def test_generate_image_prompt_md():
    beats = [
        {
            "id": "beat_01",
            "visual": {
                "headline": "Tiệm Sách Cũ Tĩnh Hiên",
                "label": "Khung cảnh tiệm sách trong đêm mưa",
                "subhead": "Đêm mưa mùa hạ và tiếng nhạc Jazz"
            }
        },
        {
            "id": "beat_02",
            "visual": {
                "headline": "Người Thợ Phục Chế",
                "label": "Lâm Hạ Vi cẩn trọng dán giấy",
                "subhead": "Nét mặt tập trung tỉ mỉ"
            }
        }
    ]
    elements_text = (
        "- **Nhịp 1 (beat_01)**: Khung cảnh tiệm sách trong đêm mưa — Đêm mưa mùa hạ và tiếng nhạc Jazz\n"
        "- **Nhịp 2 (beat_02)**: Lâm Hạ Vi cẩn trọng dán giấy — Nét mặt tập trung tỉ mỉ"
    )
    prompt_md = generate_image_prompt_md(
        scene_id="scene-01",
        scene_badge="CHƯƠNG I: VỊ KHÁCH ĐÊM MUỘN",
        job_title="Bản Hợp Đồng Lúc 0 Giờ",
        elements_text=elements_text,
        beats=beats
    )

    # Verify scene metadata & badge
    assert "scene-01" in prompt_md
    assert "CHƯƠNG I: VỊ KHÁCH ĐÊM MUỘN" in prompt_md
    assert "Bản Hợp Đồng Lúc 0 Giờ" in prompt_md

    # Verify visual keywords from beats
    assert "Tiệm Sách Cũ Tĩnh Hiên" in prompt_md
    assert "Người Thợ Phục Chế" in prompt_md

    # Verify Notion doodle style guidelines
    assert "Notion Doodle Style" in prompt_md
    assert "#F5EBD7" in prompt_md
    assert "minimal hand-drawn sketch" in prompt_md.lower()
    assert "clean line art" in prompt_md.lower()
    assert "dark gray outlines" in prompt_md.lower()
    assert "NO text" in prompt_md

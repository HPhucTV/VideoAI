import pytest
import sys
from pathlib import Path

root_wb = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_wb))

from job_adapter import cluster_beats_into_scenes

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
    assert len(scenes) >= 3
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

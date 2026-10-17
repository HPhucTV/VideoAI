import pytest
import sys
from pathlib import Path

wb_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(wb_dir))

from job_adapter import build_blender_timeline_spec, resolve_camera_action

def test_resolve_camera_action_mapping():
    # Khớp từ visual cues
    assert resolve_camera_action({"camera": "zoom_in_punch"}, "hook_teaser") == "dolly_in"
    assert resolve_camera_action({"camera": "pan_right"}, "dialogue") == "orbit"
    assert resolve_camera_action({"camera": "static"}, "dialogue") == "static"
    assert resolve_camera_action({"camera": "zoom_out_slow"}, "outro") == "dolly_out"
    
    # Suy luận mặc định theo role nếu cues không chỉ định
    assert resolve_camera_action(None, "hook_teaser") == "dolly_in"
    assert resolve_camera_action(None, "hook_intro") == "orbit"
    assert resolve_camera_action(None, "climax") == "dolly_in"
    assert resolve_camera_action(None, "scene_01") == "static"

def test_build_blender_timeline_spec():
    job_dict = {
        "jobId": "job-3d-test",
        "canvas": {"width": 1280, "height": 720, "fps": 30},
        "metadata": {
            "characters": ["Lâm Mặc", "Người Kể Chuyện"]
        },
        "beats": [
            {
                "id": "beat_01",
                "role": "hook_teaser",
                "speaker": "Lâm Mặc",
                "rawText": "Lâm Mặc: Ta không phục!",
                "cues": {"camera": "zoom_in_punch"}
            },
            {
                "id": "beat_02",
                "role": "hook_intro",
                "speaker": "Người Kể Chuyện",
                "rawText": "Người Kể Chuyện: Chào mừng đạo hữu.",
                "cues": {"camera": "pan_right"}
            }
        ]
    }
    
    # Giả lập thời lượng audio đo được cho từng beat
    audio_durations = {
        "beat_01": 3.2,
        "beat_02": 2.8
    }
    
    spec = build_blender_timeline_spec(job_dict, audio_durations)
    
    assert spec["jobId"] == "job-3d-test"
    assert spec["fps"] == 30
    assert spec["resolution"] == [1280, 720]
    # Tổng thời lượng 6.0s * 30fps = 180 frames
    assert spec["total_frames"] == 180
    assert len(spec["shots"]) == 2
    
    # Shot 1
    s1 = spec["shots"][0]
    assert s1["id"] == "beat_01"
    assert s1["camera_action"] == "dolly_in"
    assert s1["start_frame"] == 1
    assert s1["end_frame"] == 96 # 3.2 * 30
    assert s1["clean_text"] == "Ta không phục!" # Đã lọc sạch tên vai
    
    # Shot 2
    s2 = spec["shots"][1]
    assert s2["id"] == "beat_02"
    assert s2["camera_action"] == "orbit"
    assert s2["start_frame"] == 97
    assert s2["end_frame"] == 180
    assert s2["clean_text"] == "Chào mừng đạo hữu."

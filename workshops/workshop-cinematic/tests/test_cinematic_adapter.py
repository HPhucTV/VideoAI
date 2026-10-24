import pytest
import sys
from pathlib import Path

# Add workshop root
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from job_adapter import map_camera_to_video_prompt, convert_job_to_flowkit


def test_map_camera_to_video_prompt():
    prompt = map_camera_to_video_prompt("orbit_360", "Warrior standing on peak")
    assert "360-degree smooth cinematic orbit" in prompt
    assert "Warrior standing on peak" in prompt

    prompt_dolly = map_camera_to_video_prompt("dolly_in", "")
    assert "Slow dramatic dolly in zoom" in prompt_dolly


@pytest.mark.asyncio
async def test_convert_job_to_flowkit():
    sample_job = {
        "jobId": "test-epic-film",
        "title": "Bản Hùng Ca Bão Cát",
        "workshop": "cinematic",
        "canvas": {"width": 1920, "height": 1080, "fps": 60},
        "metadata": {
            "characters": ["Lâm Phong", "Nguyệt Nhi"],
            "language": "vi",
        },
        "beats": [
            {
                "id": "beat_01",
                "role": "hook",
                "speaker": "Lâm Phong",
                "rawText": "Gió cát sa mạc nổi lên, ngày quyết chiến đã tới.",
                "cues": {"camera": "dolly_in"},
                "visual": {"prompt": "A lone warrior standing amidst desert sandstorm at sunset"},
            },
            {
                "id": "beat_02",
                "role": "climax",
                "speaker": "Nguyệt Nhi",
                "rawText": "Ta sẽ luôn ở phía sau tương trợ huynh.",
                "cues": {"camera": "orbit_360"},
                "visual": {"prompt": "Female archer drawing magical bow with glowing arrow"},
            },
        ],
    }

    result = await convert_job_to_flowkit(sample_job, default_material="cinematic_film")
    assert result["jobId"] == "test-epic-film"
    assert result["scenesCount"] == 2
    assert result["orientation"] == "HORIZONTAL"
    assert len(result["scenes"]) == 2

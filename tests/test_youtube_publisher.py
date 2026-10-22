import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.youtube_publisher import generate_publishing_kit, upload_unlisted_video


def test_generate_publishing_kit(tmp_path):
    job_data = {
        "jobId": "test-job-01",
        "title": "AI Agent La Gi?",
        "metadata": {
            "channel": "Giai Ma Tech",
            "tags": ["AI", "Technology"],
        },
        "beats": [
            {
                "id": "b1",
                "speaker": "Be Byte",
                "rawText": "Cau thoai mo dau",
                "durationSec": 5.0,
            },
            {
                "id": "b2",
                "speaker": "Be Byte",
                "rawText": "Cau thoai tiep theo",
                "durationSec": 6.0,
            },
        ],
    }
    kit = generate_publishing_kit(job_data, actual_duration_sec=13.0)
    assert kit["jobId"] == "test-job-01"
    assert kit["channel"] == "Giai Ma Tech"
    assert kit["privacy_status"] == "unlisted"
    assert "AI Agent La Gi?" in kit["video_title_options"][0]["title"]
    assert len(kit["timestamps"]) >= 2
    assert kit["timestamps"][0]["time"] == "00:00"
    assert "AI Agent" in kit["youtube_description"]
    assert kit["tags"] == ["AI", "Technology"]
    assert kit["actual_duration_sec"] == 13.0


def test_upload_unlisted_video_mock():
    mock_service = MagicMock()
    mock_insert = MagicMock()
    mock_service.videos().insert.return_value = mock_insert
    mock_insert.next_chunk.return_value = (None, {"id": "mock_vid_123"})

    with patch("scripts.youtube_publisher.get_authenticated_service", return_value=mock_service):
        with patch("scripts.youtube_publisher.set_thumbnail") as mock_thumb:
            with patch("scripts.youtube_publisher.upload_srt_captions") as mock_srt:
                res = upload_unlisted_video(
                    channel_name="Giai Ma Tech",
                    video_path=Path("dummy.mp4"),
                    title="Test Video",
                    description="Test Desc",
                    tags=["test"],
                    thumbnail_path=Path("thumb.jpg"),
                    srt_path=Path("sub.srt"),
                    privacy_status="unlisted",
                )
                assert res["video_id"] == "mock_vid_123"
                assert "https://youtu.be/mock_vid_123" in res["url"]
                assert res["privacy"] == "unlisted"
                mock_thumb.assert_called_once()
                mock_srt.assert_called_once()

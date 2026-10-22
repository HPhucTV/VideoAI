import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.studio_pipeline import StudioPipeline, parse_args


def test_studio_pipeline_init():
    pipeline = StudioPipeline(job_id="test-job")
    assert pipeline.job_id == "test-job"
    assert pipeline.publish_youtube is False
    assert pipeline.privacy == "unlisted"
    assert pipeline.dry_run is False

    custom_pipeline = StudioPipeline(
        job_id="custom-job",
        publish_youtube=True,
        privacy="public",
        dry_run=True,
    )
    assert custom_pipeline.job_id == "custom-job"
    assert custom_pipeline.publish_youtube is True
    assert custom_pipeline.privacy == "public"
    assert custom_pipeline.dry_run is True


def test_studio_pipeline_dry_run(tmp_path):
    job_file = tmp_path / "job.json"
    job_data = {
        "jobId": "test-job",
        "title": "Dry Run Video Test",
        "beats": [
            {"id": "b1", "speaker": "narrator", "rawText": "Hello world from dry run."}
        ],
    }
    job_file.write_text(json.dumps(job_data, ensure_ascii=False), encoding="utf-8")

    pipeline = StudioPipeline(job_id="test-job", dry_run=True, output_base=tmp_path)
    result = pipeline.run(job_file)

    assert result["status"] == "success"
    assert result["dry_run"] is True


def test_studio_pipeline_mock_run(tmp_path):
    job_file = tmp_path / "job.json"
    job_data = {
        "jobId": "test-mock-job",
        "title": "Mock Video Test",
        "metadata": {
            "channel": "Giai Ma Tech",
            "tags": ["AI", "Tech"],
        },
        "beats": [
            {
                "id": "b1",
                "speaker": "narrator",
                "rawText": "Thử nghiệm pipeline đầy đủ từ Cổng 3 đến Cổng 7.",
                "durationSec": 4.5,
            }
        ],
    }
    job_file.write_text(json.dumps(job_data, ensure_ascii=False), encoding="utf-8")

    mock_manifest = {
        "jobId": "test-mock-job",
        "total_shots": 1,
        "total_duration": 4.5,
        "shots": [
            {
                "shot": 1,
                "id": "b1",
                "speaker": "narrator",
                "dialogue": "Thử nghiệm pipeline đầy đủ từ Cổng 3 đến Cổng 7.",
                "duration": 4.5,
                "audio_file": str(tmp_path / "cinematic" / "test-mock-job" / "audio" / "shots" / "b1.mp3"),
            }
        ],
    }
    mock_upload_res = {
        "video_id": "test_video_123",
        "url": "https://youtu.be/test_video_123",
        "privacy": "unlisted",
    }

    with patch("scripts.studio_pipeline.run_gate4_audio", return_value=mock_manifest) as mock_audio:
        with patch("scripts.studio_pipeline.upload_unlisted_video", return_value=mock_upload_res) as mock_upload:
            pipeline = StudioPipeline(
                job_id="test-mock-job",
                publish_youtube=True,
                privacy="unlisted",
                dry_run=False,
                output_base=tmp_path,
            )
            result = pipeline.run(job_file)

            assert result["status"] == "success"
            assert result["dry_run"] is False
            mock_audio.assert_called_once()
            mock_upload.assert_called_once()

            job_dir = tmp_path / "cinematic" / "test-mock-job"
            assert (job_dir / "test-mock-job.srt").exists()
            assert (job_dir / "test-mock-job_thumbnail.jpg").exists()
            assert (job_dir / "youtube_publishing_kit.json").exists()
            assert result["youtube_result"] == mock_upload_res


def test_cli_arg_parsing():
    args = parse_args(["--job", "test-job-01", "--publish-youtube", "--privacy", "public", "--dry-run"])
    assert args.job == "test-job-01"
    assert args.publish_youtube is True
    assert args.privacy == "public"
    assert args.dry_run is True

    # Test default privacy and flags
    args_default = parse_args(["--job", "test-job-02"])
    assert args_default.job == "test-job-02"
    assert args_default.publish_youtube is False
    assert args_default.privacy == "unlisted"
    assert args_default.dry_run is False

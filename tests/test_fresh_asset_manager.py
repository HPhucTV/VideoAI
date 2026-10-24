import pytest
from pathlib import Path
from scripts.fresh_asset_manager import FreshAssetManager

def test_fresh_asset_manager_isolates_job(tmp_path):
    mgr = FreshAssetManager(job_id="job-new-episode-01", base_output_dir=tmp_path)
    job_dir = mgr.get_job_dir()
    assert job_dir == tmp_path / "cinematic" / "job-new-episode-01"
    assert mgr.is_fresh_render() is True

def test_verify_no_stale_assets(tmp_path):
    mgr = FreshAssetManager(job_id="job-fresh-test", base_output_dir=tmp_path)
    stale_video = mgr.get_job_dir() / "videos" / "shot_01.mp4"
    stale_video.parent.mkdir(parents=True, exist_ok=True)
    stale_video.write_text("old_video_bytes")
    
    # Enforcing fresh render cleans existing directory or warns
    mgr.prepare_clean_workspace(force_fresh=True)
    assert not stale_video.exists()

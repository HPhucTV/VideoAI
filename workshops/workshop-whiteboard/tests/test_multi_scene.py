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


# ──────────────────────────────────────────────────────────────
# Tests for export_video.py (Multi-Scene Pipeline)
# ──────────────────────────────────────────────────────────────
scripts_wb = root_wb / "scripts"
sys.path.insert(0, str(scripts_wb))
from export_video import parse_args, sort_scene_folders, render_scene


def test_export_video_cli_args():
    # 1. Default CLI args
    args = parse_args([])
    assert args.job_id == "job-ban-hop-dong-luc-0-gio"
    assert args.fps == 90
    assert args.cap_long_edge == 1080
    assert args.scene is None
    assert args.eraser_seconds == 1.3

    # 2. Custom CLI args with selective scene
    custom_args = parse_args([
        "job-test-custom",
        "--fps", "60",
        "--cap-long-edge", "720",
        "--scene", "scene-02",
        "--eraser-seconds", "2.0"
    ])
    assert custom_args.job_id == "job-test-custom"
    assert custom_args.fps == 60
    assert custom_args.cap_long_edge == 720
    assert custom_args.scene == "scene-02"
    assert custom_args.eraser_seconds == 2.0


def test_sort_scene_folders():
    folders = [
        Path("scenes/scene-10"),
        Path("scenes/scene-02"),
        Path("scenes/scene-01"),
        Path("scenes/scene-03"),
        Path("scenes/scene-09"),
    ]
    sorted_folders = sort_scene_folders(folders)
    assert [f.name for f in sorted_folders] == [
        "scene-01", "scene-02", "scene-03", "scene-09", "scene-10"
    ]


def test_render_scene_with_and_without_eraser(tmp_path, monkeypatch):
    s1_dir = tmp_path / "scene-01"
    s1_dir.mkdir()
    (s1_dir / "scene-01.png").write_text("png")
    (s1_dir / "scene-01.annotation.json").write_text("{}")
    (s1_dir / "scene-01.mp3").write_text("mp3")

    s2_dir = tmp_path / "scene-02"
    s2_dir.mkdir()
    (s2_dir / "scene-02.png").write_text("png")
    (s2_dir / "scene-02.annotation.json").write_text("{}")
    (s2_dir / "scene-02.mp3").write_text("mp3")

    recorded_runs = []

    def mock_run(cmd, *args, **kwargs):
        recorded_runs.append([str(c) for c in cmd])
        for c in cmd:
            if str(c).endswith(".mp4"):
                Path(c).write_text("mp4")
        return type("Result", (), {"returncode": 0})()

    monkeypatch.setattr("subprocess.run", mock_run)

    # Scene 1 of 2: Not last -> with_eraser=True, eraser_seconds=1.3, audio filter apad
    mp4_1 = render_scene(
        scene_folder=s1_dir,
        scene_idx=0,
        total_scenes=2,
        root_dir=tmp_path,
        job_dir=tmp_path,
        job_id="test-job",
        fps=90,
        cap_long_edge=1080,
        eraser_seconds=1.3,
        ffmpeg_bin="ffmpeg",
        node_env={},
    )
    assert mp4_1.name == "scene-01.mp4"
    render_cmd_1 = recorded_runs[0]
    assert "--with-eraser" in render_cmd_1
    assert "--eraser-seconds" in render_cmd_1
    assert "1.3" in render_cmd_1
    ffmpeg_cmd_1 = recorded_runs[1]
    assert "-filter_complex" in ffmpeg_cmd_1
    assert any("apad" in c for c in ffmpeg_cmd_1)
    assert "-ar" in ffmpeg_cmd_1
    assert "44100" in ffmpeg_cmd_1

    recorded_runs.clear()

    # Scene 2 of 2: Last scene -> with_eraser=False, still has apad in filter_complex to prevent gaze cutoff
    mp4_2 = render_scene(
        scene_folder=s2_dir,
        scene_idx=1,
        total_scenes=2,
        root_dir=tmp_path,
        job_dir=tmp_path,
        job_id="test-job",
        fps=90,
        cap_long_edge=1080,
        eraser_seconds=1.3,
        ffmpeg_bin="ffmpeg",
        node_env={},
    )
    assert mp4_2.name == "scene-02.mp4"
    render_cmd_2 = recorded_runs[0]
    assert "--with-eraser" not in render_cmd_2
    ffmpeg_cmd_2 = recorded_runs[1]
    assert "-filter_complex" in ffmpeg_cmd_2
    assert any("apad" in c for c in ffmpeg_cmd_2)


def test_render_scene_with_bgm_and_subtitles(tmp_path, monkeypatch):
    s_dir = tmp_path / "scene-01"
    s_dir.mkdir()
    (s_dir / "scene-01.png").write_text("png")
    (s_dir / "scene-01.annotation.json").write_text("{}")
    (s_dir / "scene-01.mp3").write_text("mp3")
    (s_dir / "scene-01.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nSub text\n\n")

    bgm_file = tmp_path / "piano.mp3"
    bgm_file.write_text("bgm")

    recorded = []

    def mock_run(cmd, *args, **kwargs):
        recorded.append([str(c) for c in cmd])
        for c in cmd:
            if str(c).endswith(".mp4"):
                Path(c).write_text("mp4")
        return type("Result", (), {"returncode": 0})()

    monkeypatch.setattr("subprocess.run", mock_run)

    mp4 = render_scene(
        scene_folder=s_dir,
        scene_idx=0,
        total_scenes=1,
        root_dir=tmp_path,
        job_dir=tmp_path,
        job_id="test-job",
        fps=90,
        cap_long_edge=1080,
        eraser_seconds=0.0,
        ffmpeg_bin="ffmpeg",
        node_env={},
        bgm_path=bgm_file,
        bgm_vol=0.25,
        duck_ratio=5.0,
        with_subtitles=True,
    )
    assert mp4.name == "scene-01.mp4"
    ff_cmd = recorded[1]
    assert "-stream_loop" in ff_cmd
    fc = [ff_cmd[i+1] for i, c in enumerate(ff_cmd) if c == "-filter_complex"][0]
    assert "sidechaincompress=" in fc
    assert "ratio=5.0" in fc
    assert "subtitles=" in fc


def test_render_scene_default_no_subtitles_stream_copy(tmp_path, monkeypatch):
    s_dir = tmp_path / "scenes" / "scene-01"
    s_dir.mkdir(parents=True)
    (s_dir / "scene-01.png").write_text("dummy-png")
    (s_dir / "scene-01.annotation.json").write_text("{}")
    (s_dir / "scene-01.mp3").write_text("dummy-mp3")
    (s_dir / "scene-01.srt").write_text("1\n00:00:00,000 --> 00:00:02,000\nHello\n")

    recorded = []

    def mock_run(cmd, *args, **kwargs):
        recorded.append(cmd)
        if any("render_stream_whiteboard.py" in str(c) for c in cmd):
            (s_dir / "video-silent.mp4").write_text("dummy-silent-video")
        elif "ffmpeg" in str(cmd[0]):
            (s_dir / "scene-01.mp4").write_text("dummy-final-video")
        return type("Result", (), {"returncode": 0})()

    monkeypatch.setattr("subprocess.run", mock_run)

    # Calling render_scene with default with_subtitles (which is now False)
    mp4 = render_scene(
        scene_folder=s_dir,
        scene_idx=0,
        total_scenes=1,
        root_dir=tmp_path,
        job_dir=tmp_path,
        job_id="test-job",
        fps=90,
        cap_long_edge=1080,
        eraser_seconds=0.0,
        ffmpeg_bin="ffmpeg",
        node_env={},
    )
    assert mp4.name == "scene-01.mp4"
    ff_cmd = recorded[1]
    # Verify no subtitles filter and stream copy -c:v copy
    assert "-c:v" in ff_cmd
    c_v_idx = ff_cmd.index("-c:v")
    assert ff_cmd[c_v_idx + 1] == "copy"
    if "-filter_complex" in ff_cmd:
        fc = [ff_cmd[i+1] for i, c in enumerate(ff_cmd) if c == "-filter_complex"][0]
        assert "subtitles=" not in fc


def test_export_whiteboard_video_multi_scene_e2e(tmp_path, monkeypatch):
    from export_video import export_whiteboard_video
    import merge_scenes

    job_id = "job-test-multi"
    job_dir = tmp_path / "output" / "whiteboard" / job_id
    scenes_dir = job_dir / "scenes"
    scenes_dir.mkdir(parents=True)

    # Global backward compat files
    (job_dir / "input.mp3").write_text("global-audio")
    (job_dir / "scene-01.annotation.json").write_text("{}")
    (job_dir / "scene-01.png").write_text("png-data")

    # 3 scenes
    for i in range(1, 4):
        s_dir = scenes_dir / f"scene-{i:02d}"
        s_dir.mkdir()
        (s_dir / f"scene-{i:02d}.png").write_text("png-data")
        (s_dir / f"scene-{i:02d}.annotation.json").write_text("{}")
        (s_dir / f"scene-{i:02d}.mp3").write_text("audio-data")

    rendered_scenes = []

    def mock_subprocess_run(cmd, *args, **kwargs):
        cmd_strs = [str(c) for c in cmd]
        # Check if render_stream_whiteboard
        if any("render_stream_whiteboard.py" in str(c) for c in cmd):
            # Output is argument at index 4 (or similar)
            out_mp4 = Path(cmd_strs[4])
            out_mp4.write_text("silent-mp4-data")
            rendered_scenes.append(out_mp4.parent.name)
        # Check if ffmpeg muxing
        elif "ffmpeg" in cmd_strs[0] or cmd_strs[0].endswith("ffmpeg.exe"):
            out_mp4 = Path(cmd_strs[-1])
            out_mp4.write_text("muxed-mp4-data")
        return type("Result", (), {"returncode": 0})()

    monkeypatch.setattr("subprocess.run", mock_subprocess_run)

    # Mock merge_scenes concat
    merged_calls = []

    def mock_concat(inputs, output):
        merged_calls.append(list(inputs))
        output.write_text("final-video-data")
        return True

    monkeypatch.setattr(merge_scenes, "_ffmpeg_concat_copy", mock_concat)

    # 1. Full multi-scene export
    final_video = export_whiteboard_video(job_id=job_id, root_dir=tmp_path)
    assert final_video.exists()
    assert final_video.name == f"{job_id}.mp4"
    assert rendered_scenes == ["scene-01", "scene-02", "scene-03"]
    assert len(merged_calls) == 1
    assert [p.name for p in merged_calls[0]] == ["scene-01.mp4", "scene-02.mp4", "scene-03.mp4"]
    # Verify thumbnail
    thumb = tmp_path / "output" / "whiteboard" / f"{job_id}-thumb.png"
    assert thumb.exists()

    # 2. Selective re-render of scene-02 only
    rendered_scenes.clear()
    merged_calls.clear()
    final_video_2 = export_whiteboard_video(job_id=job_id, scene="scene-02", root_dir=tmp_path)
    assert final_video_2.exists()
    # Only scene-02 was re-rendered!
    assert rendered_scenes == ["scene-02"]
    # All 3 scenes were re-merged!
    assert len(merged_calls) == 1
    assert [p.name for p in merged_calls[0]] == ["scene-01.mp4", "scene-02.mp4", "scene-03.mp4"]


def test_export_whiteboard_video_single_scene_compat(tmp_path, monkeypatch):
    from export_video import export_whiteboard_video

    job_id = "job-test-single"
    job_dir = tmp_path / "output" / "whiteboard" / job_id
    job_dir.mkdir(parents=True)

    # Single scene files (no scenes/ folder)
    (job_dir / "input.mp3").write_text("global-audio")
    (job_dir / "scene-01.annotation.json").write_text("{}")
    (job_dir / "scene-01.png").write_text("png-data")

    def mock_subprocess_run(cmd, *args, **kwargs):
        cmd_strs = [str(c) for c in cmd]
        if any("render_stream_whiteboard.py" in str(c) for c in cmd):
            Path(cmd_strs[4]).write_text("silent-mp4-data")
        elif "ffmpeg" in cmd_strs[0] or cmd_strs[0].endswith("ffmpeg.exe"):
            Path(cmd_strs[-1]).write_text("final-mp4-data")
        return type("Result", (), {"returncode": 0})()

    monkeypatch.setattr("subprocess.run", mock_subprocess_run)

    final_video = export_whiteboard_video(job_id=job_id, root_dir=tmp_path)
    assert final_video.exists()
    assert final_video.name == f"{job_id}.mp4"
    thumb = tmp_path / "output" / "whiteboard" / f"{job_id}-thumb.png"
    assert thumb.exists()


def test_export_video_invalid_scene_raises_value_error(tmp_path):
    from export_video import export_whiteboard_video
    import pytest

    job_id = "job-test-invalid"
    job_dir = tmp_path / "output" / "whiteboard" / job_id
    scenes_dir = job_dir / "scenes"
    scenes_dir.mkdir(parents=True)
    (scenes_dir / "scene-01").mkdir()

    with pytest.raises(ValueError, match="Không tìm thấy phân cảnh scene-99"):
        export_whiteboard_video(job_id=job_id, scene="scene-99", root_dir=tmp_path)


def test_export_video_single_scene_with_scene_flag_raises(tmp_path):
    from export_video import export_whiteboard_video
    import pytest

    job_id = "job-single-only"
    job_dir = tmp_path / "output" / "whiteboard" / job_id
    job_dir.mkdir(parents=True)
    (job_dir / "input.mp3").write_text("mp3")
    (job_dir / "scene-01.annotation.json").write_text("{}")
    (job_dir / "scene-01.png").write_text("png")

    with pytest.raises(ValueError, match="Không thể dùng tham số --scene"):
        export_whiteboard_video(job_id=job_id, scene="scene-01", root_dir=tmp_path)


def test_export_video_missing_scene_mp4_in_selective_returns_partial_path(tmp_path, monkeypatch):
    from export_video import export_whiteboard_video

    job_id = "job-selective-partial"
    job_dir = tmp_path / "output" / "whiteboard" / job_id
    scenes_dir = job_dir / "scenes"
    scenes_dir.mkdir(parents=True)

    for s_name in ["scene-01", "scene-02"]:
        s_dir = scenes_dir / s_name
        s_dir.mkdir()
        (s_dir / f"{s_name}.png").write_text("png")
        (s_dir / f"{s_name}.annotation.json").write_text("{}")
        (s_dir / f"{s_name}.mp3").write_text("mp3")

    def mock_subprocess_run(cmd, *args, **kwargs):
        cmd_strs = [str(c) for c in cmd]
        if "ffmpeg" in cmd_strs[0] or cmd_strs[0].endswith("ffmpeg.exe"):
            Path(cmd_strs[-1]).write_text("muxed-mp4")
        elif any("render_stream_whiteboard.py" in str(c) for c in cmd):
            Path(cmd_strs[4]).write_text("silent-mp4")
        return type("Result", (), {"returncode": 0})()

    monkeypatch.setattr("subprocess.run", mock_subprocess_run)

    # Render only scene-01 when scene-02 is NOT yet rendered
    res = export_whiteboard_video(job_id=job_id, scene="scene-01", root_dir=tmp_path)
    assert res == scenes_dir / "scene-01" / "scene-01.mp4"
    assert res.exists()
    # Final video was not merged because scene-02 is missing
    final_video = tmp_path / "output" / "whiteboard" / f"{job_id}.mp4"
    assert not final_video.exists()




import os
import shutil
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _ffmpeg_bin() -> str:
    env_bin = os.environ.get("FFMPEG_BIN")
    if env_bin:
        return env_bin
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


_FLOAT_MIN = 0.0
_FLOAT_MAX = 2.0


def _clamp_float(value: float, name: str, lo: float = _FLOAT_MIN, hi: float = _FLOAT_MAX) -> float:
    """Clamp float to [lo, hi] and warn if out of bounds."""
    if value < lo or value > hi:
        logger.warning("Parameter %s=%s out of bounds [%s, %s], clamping", name, value, lo, hi)
        return max(lo, min(hi, value))
    return value


def probe_duration(path: str) -> float | None:
    """Return media duration in seconds via ffprobe, or None on failure."""
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        return float(probe.stdout.strip())
    except (ValueError, AttributeError, subprocess.SubprocessError, OSError):
        logger.error("probe_duration failed for %s", path)
        return None


def normalize_clip(input_path: str, output_path: str, size: str | None = None,
                   fps: int = 30) -> bool:
    """Re-encode one clip to uniform h264/yuv420p + AAC so concat -c copy is safe.

    Clips from different providers (Flow vs assistant) may differ in codec,
    pixel format, or timebase; normalizing first avoids concat failures.
    """
    cmd = ["ffmpeg", "-y", "-i", str(input_path),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(int(fps)),
           "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
           "-movflags", "+faststart"]
    if size:
        cmd += ["-vf", f"scale={size}:force_original_aspect_ratio=decrease,"
                       f"pad={size}:(ow-iw)/2:(oh-ih)/2"]
    cmd.append(str(output_path))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except (subprocess.SubprocessError, OSError) as e:
        logger.error("Normalize failed for %s: %s", input_path, e)
        return False
    if result.returncode != 0:
        logger.error("Normalize failed for %s: %s", input_path, result.stderr[-300:])
        return False
    return True


def trim_video(input_path: str, output_path: str, start: float, end: float) -> bool:
    """Trim video to [start, end] seconds."""
    if not Path(input_path).exists():
        logger.error("trim_video: input file not found: %s", input_path)
        return False
    duration = end - start
    cmd = [
        _ffmpeg_bin(), "-y", "-i", input_path,
        "-ss", str(start), "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-force_key_frames", "expr:gte(t,0)",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        logger.error("Trim failed: %s", result.stderr[-200:])
        return False
    return True


def merge_videos(video_paths: list[str], output_path: str) -> bool:
    """Concatenate videos using ffmpeg concat demuxer."""
    concat_file = output_path + ".concat.txt"
    try:
        with open(concat_file, "w", encoding="utf-8") as f:
            for p in video_paths:
                # Escape single quotes and use POSIX forward slashes for ffmpeg concat demuxer
                escaped = Path(p).as_posix().replace("'", "'\\''")
                f.write(f"file '{escaped}'\n")

        cmd = [
            _ffmpeg_bin(), "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-c:v", "copy", "-c:a", "copy",
            "-movflags", "+faststart",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    finally:
        Path(concat_file).unlink(missing_ok=True)
    if result.returncode != 0:
        logger.error("Merge failed: %s", result.stderr[-200:])
        return False
    return True


def add_narration(video_path: str, narration_path: str, output_path: str,
                  narration_volume: float = 1.0, sfx_volume: float = 0.4,
                  fade_in: float = 0.5, fade_out: float = 0.5) -> bool:
    """Overlay narration audio on video, ducking the existing SFX track."""
    if not Path(video_path).exists():
        logger.error("add_narration: video file not found: %s", video_path)
        return False
    if not Path(narration_path).exists():
        logger.error("add_narration: narration file not found: %s", narration_path)
        return False

    # Clamp float params to prevent filter injection
    narration_volume = _clamp_float(narration_volume, "narration_volume")
    sfx_volume = _clamp_float(sfx_volume, "sfx_volume")
    fade_in = _clamp_float(fade_in, "fade_in")
    fade_out = _clamp_float(fade_out, "fade_out")

    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", video_path],
        capture_output=True, text=True, timeout=30,
    )
    try:
        duration = float(probe.stdout.strip())
    except (ValueError, AttributeError):
        logger.error("ffprobe failed for %s: %s", video_path, probe.stderr[-200:] if probe.stderr else "no output")
        return False
    fade_start = max(0, duration - fade_out)

    cmd = [
        _ffmpeg_bin(), "-y", "-i", video_path, "-i", narration_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-filter_complex",
        f"[0:a]volume={sfx_volume}[sfx];[1:a]volume={narration_volume},afade=t=in:st=0:d={fade_in},afade=t=out:st={fade_start}:d={fade_out}[narr];[sfx][narr]amerge=inputs=2,pan=stereo|c0=c0+c2|c1=c1+c3[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-shortest",
        "-movflags", "+faststart",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        logger.error("Add narration failed: %s", result.stderr[-200:])
        return False
    return True


def add_music(video_path: str, music_path: str, output_path: str,
              music_volume: float = 0.3, fade_in: float = 2.0, fade_out: float = 3.0) -> bool:
    """Overlay background music on video."""
    if not Path(video_path).exists():
        logger.error("add_music: video file not found: %s", video_path)
        return False
    if not Path(music_path).exists():
        logger.error("add_music: music file not found: %s", music_path)
        return False

    # Clamp float params to prevent filter injection
    music_volume = _clamp_float(music_volume, "music_volume")
    fade_in = _clamp_float(fade_in, "fade_in")
    fade_out = _clamp_float(fade_out, "fade_out")

    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", video_path],
        capture_output=True, text=True, timeout=30,
    )
    try:
        duration = float(probe.stdout.strip())
    except (ValueError, AttributeError):
        logger.error("ffprobe failed for %s: %s", video_path, probe.stderr[-200:] if probe.stderr else "no output")
        return False
    fade_start = max(0, duration - fade_out)

    cmd = [
        _ffmpeg_bin(), "-y", "-i", video_path, "-i", music_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-filter_complex",
        f"[0:a]volume=1.0[orig];[1:a]volume={music_volume},afade=t=in:st=0:d={fade_in},afade=t=out:st={fade_start}:d={fade_out}[music];[orig][music]amerge=inputs=2,pan=stereo|c0=c0+c2|c1=c1+c3[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-shortest",
        "-movflags", "+faststart",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        logger.error("Add music failed: %s", result.stderr[-200:])
        return False
    return True


COLOR_GRADING_PRESETS = {
    "cinematic_teal_orange": (
        "eq=contrast=1.12:brightness=-0.02:saturation=1.18,"
        "colorbalance=rs=0.08:gs=0.02:bs=-0.06:rm=-0.04:gm=0.01:bm=0.06:rh=0.05:gh=0.02:bh=-0.04"
    ),
    "donghua_xianxia_dream": (
        "eq=contrast=1.08:brightness=0.02:saturation=1.25,"
        "colorbalance=rs=0.04:gs=0.02:bs=0.08:rm=0.02:gm=0.0:bm=0.05"
    ),
    "dark_thriller_noir": (
        "eq=contrast=1.25:brightness=-0.05:saturation=0.75,"
        "colorbalance=rs=-0.05:gs=-0.02:bs=0.08"
    ),
    "vintage_warm": (
        "eq=contrast=1.05:brightness=0.0:saturation=1.1,"
        "colorbalance=rs=0.1:gs=0.04:bs=-0.08"
    ),
}


def apply_color_grading(
    input_path: str,
    output_path: str,
    preset: str = "cinematic_teal_orange",
    vignette: bool = True,
) -> bool:
    """Áp dụng bộ lọc màu điện ảnh đồng nhất (LUT/Color Grading) lên video qua FFmpeg."""
    if not Path(input_path).exists():
        logger.error("apply_color_grading: input file not found: %s", input_path)
        return False
    filter_chain = COLOR_GRADING_PRESETS.get(preset)
    if not filter_chain:
        logger.warning("apply_color_grading: unknown preset %s, using cinematic_teal_orange", preset)
        filter_chain = COLOR_GRADING_PRESETS["cinematic_teal_orange"]
    if vignette:
        filter_chain = f"{filter_chain},vignette=PI/4"

    cmd = [
        _ffmpeg_bin(), "-y", "-i", str(input_path),
        "-vf", filter_chain,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        logger.error("Apply color grading failed: %s", result.stderr[-200:])
        return False
    return True


def add_cinematic_sub_bass_drone(
    video_path: str,
    output_path: str,
    drone_volume: float = 0.25,
    cutoff_hz: int = 48,
) -> bool:
    """Tổng hợp và hòa trộn dải trầm Brown noise 40-60Hz tạo độ rung lồng ngực kịch tính."""
    if not Path(video_path).exists():
        logger.error("add_cinematic_sub_bass_drone: video file not found: %s", video_path)
        return False
    duration = probe_duration(video_path)
    if not duration:
        return False

    drone_volume = _clamp_float(drone_volume, "drone_volume", 0.0, 1.0)
    cmd = [
        _ffmpeg_bin(), "-y", "-i", str(video_path),
        "-f", "lavfi", "-i", f"anoisesrc=c=brown:r=48000:a=0.3,lowpass=f={cutoff_hz},volume={drone_volume}",
        "-filter_complex",
        "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        logger.error("Add sub-bass drone failed: %s", result.stderr[-200:])
        return False
    return True

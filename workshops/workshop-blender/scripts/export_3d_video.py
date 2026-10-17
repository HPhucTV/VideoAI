#!/usr/bin/env python3
"""
Export 3D Video Pipeline (export_3d_video.py)

Orchestrates 3D video generation from unified job specifications:
1. Synthesizes dialogue voiceover per beat via Edge TTS (Node script or local engine)
2. Measures beat audio durations using ffprobe
3. Concatenates beat audio tracks into a master voice track using FFmpeg
4. Generates Blender timeline spec with camera choreographies
5. Invokes Blender headless renderer to render 3D animation
6. Mixes audio with dynamic BGM sidechain ducking (-14 LUFS) and muxes into final MP4
7. Cleans up temporary artifacts
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add workshop-blender directory to sys.path so job_adapter can be imported
SCRIPT_DIR = Path(__file__).resolve().parent
BLENDER_WORKSHOP_DIR = SCRIPT_DIR.parent
REPO_ROOT = BLENDER_WORKSHOP_DIR.parent.parent

if str(BLENDER_WORKSHOP_DIR) not in sys.path:
    sys.path.insert(0, str(BLENDER_WORKSHOP_DIR))

from job_adapter import build_blender_timeline_spec, sanitize_dialogue_text


def find_blender_binary() -> str | None:
    """
    Locates the Blender executable across environment variables, common Windows install paths, and PATH.
    Priority:
    1. Environment variables BLENDER_PATH or BLENDER_BIN.
    2. Common Windows installation paths (Blender 5.2, 5.1, 5.0, 4.2, etc.).
    3. System PATH via shutil.which("blender").
    """
    # 1. Environment variables
    for env_var in ("BLENDER_PATH", "BLENDER_BIN"):
        val = os.environ.get(env_var)
        if val and Path(val).is_file():
            return str(Path(val).resolve())

    # 2. Common Windows installation paths
    common_paths = [
        r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
    ]
    for p_str in common_paths:
        p = Path(p_str)
        if p.is_file():
            return str(p.resolve())

    # Check Blender Foundation directory for any installed version
    blender_foundation = Path(r"C:\Program Files\Blender Foundation")
    if blender_foundation.is_dir():
        for b_dir in sorted(blender_foundation.glob("Blender *"), reverse=True):
            cand = b_dir / "blender.exe"
            if cand.is_file():
                return str(cand.resolve())

    # 3. System PATH
    which_blender = shutil.which("blender")
    if which_blender:
        return str(Path(which_blender).resolve())

    return None


def resolve_bgm_track(custom_bgm: str | Path | None) -> Path | None:
    """
    Resolves background music file:
    - If custom_bgm is provided and exists: return Path(custom_bgm)
    - Otherwise search for default BGM in:
      workshops/workshop-whiteboard/assets/audio/bgm/xianxia-ambient.mp3
      workshops/workshop-whiteboard/assets/audio/bgm/healing-piano.mp3
      workshops/workshop-whiteboard/assets/audio/bgm/battle-epic.mp3
    """
    if custom_bgm:
        p = Path(custom_bgm)
        if p.is_file():
            return p.resolve()
        p_rel = REPO_ROOT / custom_bgm
        if p_rel.is_file():
            return p_rel.resolve()

    # Search default BGMs in repo
    default_candidates = [
        REPO_ROOT / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "xianxia-ambient.mp3",
        REPO_ROOT / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "healing-piano.mp3",
        REPO_ROOT / "workshops" / "workshop-whiteboard" / "assets" / "audio" / "bgm" / "battle-epic.mp3",
    ]
    for cand in default_candidates:
        if cand.is_file():
            return cand.resolve()

    return None


def build_blender_ducking_filter(
    total_duration_sec: float,
    bgm_base_vol: float = 0.25,
    duck_ratio: float = 6.0,
    fade_out_sec: float = 2.0,
    target_lufs: float = -14.0,
) -> str:
    """
    Builds FFmpeg filter complex string for sidechain ducking and loudness normalization:
    - [0:a] is voice track, split into sidechain trigger and mix stream
    - [1:a] is background music, attenuated to base volume
    - Sidechain compressor ducks BGM during speech
    - amix mixes voice and ducked BGM
    - afade applies smooth fadeout at the end
    - loudnorm normalizes to broadcast target LUFS (e.g. -14.0)
    """
    fade_start = max(0.0, total_duration_sec - fade_out_sec)
    return (
        f"[0:a]asplit=2[voice_sc][voice_mix];"
        f"[1:a]volume={bgm_base_vol}[bgm_in];"
        f"[bgm_in][voice_sc]sidechaincompress=threshold=0.04:ratio={duck_ratio}:attack=100:release=600[ducked_bgm];"
        f"[voice_mix][ducked_bgm]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[mix_raw];"
        f"[mix_raw]afade=t=out:st={fade_start:.2f}:d={fade_out_sec:.2f},loudnorm=I={target_lufs:.1f}:LRA=11:TP=-1.5[outa]"
    )


def get_media_duration(file_path: Path | str) -> float:
    """
    Measures duration of audio/video file using ffprobe.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Media file not found: {path}")

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path.resolve())
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    val = res.stdout.decode("utf-8", errors="replace").strip()
    return float(val) if val else 0.0


def synthesize_beat_audio(text: str, voice_cfg: dict, out_file: Path) -> Path:
    """
    Synthesizes speech audio for a beat:
    Primary: Calls Node script core/bin/tts.js
    Fallback: Python edge_tts via current venv or system python
    """
    out_file = Path(out_file).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    clean_text = text.strip()
    if not clean_text:
        # Generate 1.0s silence if text is empty
        cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "1.0", str(out_file)]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return out_file

    voice = voice_cfg.get("voice") or voice_cfg.get("voiceId") or "vi-VN-NamMinhNeural"
    rate = voice_cfg.get("rate", "+0%")
    pitch = voice_cfg.get("pitch", "+0Hz")
    volume = voice_cfg.get("volume", "+0%")

    tts_script = REPO_ROOT / "core" / "bin" / "tts.js"
    node_bin = shutil.which("node")

    # 1. Try Node script core/bin/tts.js
    if node_bin and tts_script.is_file():
        cmd = [
            node_bin,
            str(tts_script),
            "--text", clean_text,
            "--voice", voice,
            "--rate", rate,
            "--pitch", pitch,
            "--volume", volume,
            "--out", str(out_file)
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            stdout = res.stdout.decode("utf-8", errors="replace").strip()
            # Extract JSON from stdout
            json_start = stdout.find("{")
            json_end = stdout.rfind("}")
            if json_start != -1 and json_end != -1:
                data = json.loads(stdout[json_start:json_end+1])
                src_path = Path(data.get("filePath", ""))
                if src_path.is_file():
                    if src_path.suffix.lower() == out_file.suffix.lower():
                        shutil.copyfile(src_path, out_file)
                    else:
                        subprocess.run(
                            ["ffmpeg", "-y", "-i", str(src_path), "-ar", "44100", "-ac", "2", str(out_file)],
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                    return out_file
        except Exception as e:
            print(f"[WARN] Node TTS script failed ({e}), attempting Python edge_tts fallback...", file=sys.stderr)

    # 2. Fallback: python -m edge_tts
    py_executables = [
        str(REPO_ROOT / "workshops" / "workshop-whiteboard" / ".venv" / "Scripts" / "python.exe"),
        sys.executable,
        shutil.which("python") or "python",
    ]

    for py_bin in py_executables:
        if not py_bin or not Path(py_bin).is_file():
            continue
        cmd = [
            py_bin, "-m", "edge_tts",
            "--text", clean_text,
            "--voice", voice,
            "--write-media", str(out_file)
        ]
        if rate and rate != "+0%":
            cmd.append(f"--rate={rate}")
        if pitch and pitch != "+0Hz":
            cmd.append(f"--pitch={pitch}")
        if volume and volume != "+0%":
            cmd.append(f"--volume={volume}")

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if out_file.is_file() and out_file.stat().st_size > 0:
                return out_file
        except Exception:
            continue

    # 3. If all TTS attempts fail, raise RuntimeError
    raise RuntimeError(
        f"Failed to synthesize audio for text: '{clean_text[:40]}...' using Node tts.js and edge_tts fallback."
    )


def export_3d_video(
    job_path_or_id: str | Path,
    resolution: str = "720p",
    fps: int = 30,
    dry_run: bool = False,
    custom_bgm: str | Path | None = None,
    bgm_vol: float = 0.25,
    blender_bin: str | None = None,
    keep_temp: bool = False,
) -> Path:
    """
    Coordinates end-to-end 3D video export pipeline:
    1. Reads and parses job JSON specification.
    2. Creates temporary working directory _temp_<jobId>.
    3. Synthesizes dialogue voiceover per beat, measuring durations with ffprobe.
    4. Concatenates beat audio files into _voice_track.wav via FFmpeg.
    5. Builds Blender timeline spec and writes to _temp/render_spec.json.
    6. Calls Blender headless renderer with blender_renderer.py.
    7. Muxes video with dynamic BGM sidechain ducking (-14 LUFS) to output/blender/<jobId>.mp4.
    8. Cleans up temporary directory.
    """
    # 1. Resolve job file
    job_file = None
    p_input = Path(job_path_or_id)
    if p_input.is_file():
        job_file = p_input.resolve()
    else:
        # Search candidate locations
        cands = [
            REPO_ROOT / "output" / "jobs" / f"{job_path_or_id}.json",
            REPO_ROOT / "output" / "jobs" / str(job_path_or_id),
            REPO_ROOT / "output" / f"{job_path_or_id}.json",
            REPO_ROOT / "output" / str(job_path_or_id),
            REPO_ROOT / f"{job_path_or_id}.json",
            Path(f"{job_path_or_id}.json"),
        ]
        for c in cands:
            if c.is_file():
                job_file = c.resolve()
                break

    if not job_file:
        raise FileNotFoundError(f"Job file not found for: {job_path_or_id}")

    with open(job_file, "r", encoding="utf-8") as f:
        job_dict = json.load(f)

    job_id = job_dict.get("jobId") or job_file.stem
    print(f"[INFO] Starting 3D video export for job: {job_id}")

    # Set canvas resolution & fps
    res_map = {
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "4k": (3840, 2160),
    }
    canvas = job_dict.get("canvas") or {}
    w, h = res_map.get(resolution.lower(), (1280, 720))
    # Preserve vertical orientation if original canvas was vertical
    orig_w = canvas.get("width", 1280)
    orig_h = canvas.get("height", 720)
    if orig_h > orig_w:
        w, h = h, w

    job_dict["canvas"] = {
        "width": w,
        "height": h,
        "fps": int(fps)
    }

    # 2. Create temporary working directory _temp_<jobId>
    temp_dir = REPO_ROOT / f"_temp_{job_id}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 3. Synthesize dialogue audio per beat and measure duration
        base_voice = job_dict.get("voice", {})
        default_voice_cfg = {
            "voice": base_voice.get("voiceId") or base_voice.get("voice", "vi-VN-NamMinhNeural"),
            "rate": base_voice.get("rate", "+0%"),
            "pitch": base_voice.get("pitch", "+0Hz"),
            "volume": base_voice.get("volume", "+0%"),
        }

        metadata = job_dict.get("metadata") or {}
        known_speakers = metadata.get("characters", [])
        char_voices = metadata.get("characters_voice", {})

        audio_durations = {}
        beat_audio_files = []

        beats = job_dict.get("beats", [])
        print(f"[INFO] Synthesizing audio for {len(beats)} beats...")

        for idx, beat in enumerate(beats):
            beat_id = beat.get("id", f"beat_{idx+1:02d}")
            raw_text = beat.get("rawText", "")
            spk, clean_text = sanitize_dialogue_text(raw_text, known_speakers)
            speaker = beat.get("speaker") or spk or "Người Kể Chuyện"

            # Match character voice config
            speaker_lower = speaker.strip().lower()
            matched_voice = None
            if isinstance(char_voices, dict):
                for k, v in char_voices.items():
                    k_lower = k.strip().lower()
                    if k_lower == speaker_lower or k_lower in speaker_lower or speaker_lower in k_lower:
                        matched_voice = v
                        break

            beat_cfg = dict(default_voice_cfg)
            if matched_voice and isinstance(matched_voice, dict):
                beat_cfg.update({
                    "voice": matched_voice.get("voice") or matched_voice.get("voiceId") or beat_cfg["voice"],
                    "rate": matched_voice.get("rate", beat_cfg["rate"]),
                    "pitch": matched_voice.get("pitch", beat_cfg["pitch"]),
                    "volume": matched_voice.get("volume", beat_cfg["volume"]),
                })

            beat_out_file = temp_dir / f"{beat_id}.mp3"
            synthesize_beat_audio(clean_text or raw_text, beat_cfg, beat_out_file)
            dur = get_media_duration(beat_out_file)
            audio_durations[beat_id] = dur
            beat_audio_files.append(beat_out_file)
            print(f"  - [{beat_id}] ({dur:.2f}s) {speaker}: {clean_text[:30]}...")

        # 4. Concatenate beat audio tracks into _voice_track.wav via FFmpeg
        voice_track = temp_dir / "_voice_track.wav"
        concat_list_file = temp_dir / "concat_audio.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for af in beat_audio_files:
                f.write(f"file '{af.resolve().as_posix()}'\n")

        print(f"[INFO] Concatenating beat audio files to: {voice_track.name}")
        cmd_concat = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-ar", "44100",
            "-ac", "2",
            str(voice_track)
        ]
        subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        total_voice_dur = get_media_duration(voice_track)
        print(f"[INFO] Voice track ready, duration: {total_voice_dur:.2f}s")

        # 5. Build Blender timeline spec and save to _temp/render_spec.json
        timeline_spec = build_blender_timeline_spec(job_dict, audio_durations, default_fps=int(fps))
        render_spec_file = temp_dir / "render_spec.json"
        with open(render_spec_file, "w", encoding="utf-8") as f:
            json.dump(timeline_spec, f, ensure_ascii=False, indent=2)
        print(f"[INFO] Blender timeline spec written to: {render_spec_file.name}")

        # 6. Call Blender headless renderer
        b_bin = blender_bin or find_blender_binary()
        if not b_bin:
            raise RuntimeError(
                "Blender binary not found. Please install Blender (e.g. 5.2 LTS) or set BLENDER_PATH."
            )

        renderer_script = BLENDER_WORKSHOP_DIR / "scripts" / "blender_renderer.py"
        raw_video_path = temp_dir / "raw_video.mp4"

        cmd_blender = [
            b_bin,
            "-b",
            "-P", str(renderer_script.resolve()),
            "--",
            "--spec", str(render_spec_file.resolve()),
            "--output", str(raw_video_path.resolve()),
        ]
        if dry_run:
            cmd_blender.append("--dry-run")

        print(f"[INFO] Executing Blender headless renderer...")
        res_blender = subprocess.run(cmd_blender, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res_blender.returncode != 0:
            err_msg = res_blender.stderr.decode("utf-8", errors="replace")
            print(err_msg, file=sys.stderr)
            raise RuntimeError(f"Blender renderer failed with exit code {res_blender.returncode}")

        # 7. Mux BGM sidechain ducking (-14 LUFS) and Video to output/blender/<jobId>.mp4
        output_dir = REPO_ROOT / "output" / "blender"
        output_dir.mkdir(parents=True, exist_ok=True)
        final_video = output_dir / f"{job_id}.mp4"

        if dry_run:
            print(f"[OK] [DRY-RUN] Pipeline completed. Render skipped. Target output: {final_video}")
            return final_video

        bgm_track = resolve_bgm_track(custom_bgm)
        if bgm_track and bgm_track.is_file():
            print(f"[INFO] Muxing video and audio with BGM sidechain ducking ({bgm_track.name})...")
            duck_filter = build_blender_ducking_filter(
                total_duration_sec=total_voice_dur,
                bgm_base_vol=bgm_vol,
                duck_ratio=6.0,
                fade_out_sec=2.0,
                target_lufs=-14.0
            )
            cmd_mux = [
                "ffmpeg", "-y",
                "-i", str(voice_track),
                "-stream_loop", "-1", "-i", str(bgm_track),
                "-i", str(raw_video_path),
                "-filter_complex", duck_filter,
                "-map", "2:v:0",
                "-map", "[outa]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(final_video)
            ]
        else:
            print(f"[INFO] Muxing video and voice track without BGM...")
            cmd_mux = [
                "ffmpeg", "-y",
                "-i", str(raw_video_path),
                "-i", str(voice_track),
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(final_video)
            ]

        subprocess.run(cmd_mux, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"[OK] Final 3D video exported successfully: {final_video}")
        return final_video

    finally:
        # 8. Clean up temporary directory
        if not keep_temp and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        prog="export_3d_video.py",
        description="End-to-End 3D Video Export Pipeline Orchestrator (Blender + Audio Sidechain Ducking)"
    )
    parser.add_argument("--job", type=str, help="Job ID or job name (resolved in output/jobs)")
    parser.add_argument("--job-file", type=str, help="Explicit path to job JSON file")
    parser.add_argument("--resolution", type=str, default="720p", choices=["720p", "1080p", "4k"], help="Video resolution (default: 720p)")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30)")
    parser.add_argument("--bgm", type=str, default=None, help="Path to custom background music audio file")
    parser.add_argument("--bgm-vol", type=float, default=0.25, help="Background music base volume ratio (default: 0.25)")
    parser.add_argument("--dry-run", action="store_true", help="Run pipeline, setup scene without rendering full video")
    parser.add_argument("--blender-bin", type=str, default=None, help="Path to Blender binary executable")
    parser.add_argument("--keep-temp", action="store_true", help="Preserve temporary folder for inspection")

    args = parser.parse_args()

    job_target = args.job_file or args.job
    if not job_target:
        parser.error("Either --job or --job-file must be provided.")

    out = export_3d_video(
        job_path_or_id=job_target,
        resolution=args.resolution,
        fps=args.fps,
        dry_run=args.dry_run,
        custom_bgm=args.bgm,
        bgm_vol=args.bgm_vol,
        blender_bin=args.blender_bin,
        keep_temp=args.keep_temp,
    )
    print(f"\n[DONE] Exported: {out}")


if __name__ == "__main__":
    main()

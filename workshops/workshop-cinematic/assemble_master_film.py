import json
import os
import subprocess
import sys

AUDIO_MANIFEST = "output/cinematic/audio/audio_manifest.json"
MASTER_AUDIO = "output/cinematic/audio/master_film_audio_48k.mp3"
INTRO_FILE = "shared-assets/branding/intro_horizontal_16x9.mp4"
OUTRO_FILE = "shared-assets/branding/outro_horizontal_16x9.mp4"
VIDEOS_DIR = "output/cinematic/videos"
TEMP_DIR = "output/cinematic/temp_assembly"
SUBTITLES_FILE = "output/cinematic/subtitles/content.srt"
FINAL_OUTPUT = "output/cinematic/master_film_chatbot_vs_agent_16x9.mp4"

# Shot-to-video mapping with source trim bounds (all clips are 8.0s)
SHOT_MAPPING = [
    {"shot_id": "shot_01", "src_video": "video_act1.mp4", "src_start": 0.0, "src_duration": 4.0},
    {"shot_id": "shot_02", "src_video": "video_act1.mp4", "src_start": 3.0, "src_duration": 5.0},
    {"shot_id": "shot_03", "src_video": "video_act1_agentx.mp4", "src_start": 0.0, "src_duration": 6.0},
    {"shot_id": "shot_04", "src_video": "video_act2_crisis.mp4", "src_start": 0.0, "src_duration": 4.5},
    {"shot_id": "shot_05", "src_video": "video_act2_crisis.mp4", "src_start": 3.0, "src_duration": 5.0},
    {"shot_id": "shot_06", "src_video": "video_act2_helpless.mp4", "src_start": 0.0, "src_duration": 4.5},
    {"shot_id": "shot_07", "src_video": "video_act2_helpless.mp4", "src_start": 3.0, "src_duration": 5.0},
    {"shot_id": "shot_08", "src_video": "video_act3_action.mp4", "src_start": 0.0, "src_duration": 4.5},
    {"shot_id": "shot_09", "src_video": "video_act3_action.mp4", "src_start": 3.0, "src_duration": 5.0},
    {"shot_id": "shot_10", "src_video": "video_act3_success.mp4", "src_start": 0.0, "src_duration": 4.5},
    {"shot_id": "shot_11", "src_video": "video_act3_success.mp4", "src_start": 3.5, "src_duration": 4.5},
    {"shot_id": "shot_12", "src_video": "video_act4_compare.mp4", "src_start": 0.0, "src_duration": 4.5},
    {"shot_id": "shot_13", "src_video": "video_act4_compare.mp4", "src_start": 1.5, "src_duration": 6.5},
    {"shot_id": "shot_14", "src_video": "video_act4_icons.mp4", "src_start": 0.0, "src_duration": 6.5},
    {"shot_id": "shot_15", "src_video": "video_act5_conclusion.mp4", "src_start": 0.0, "src_duration": 4.5},
    {"shot_id": "shot_16", "src_video": "video_act5_conclusion.mp4", "src_start": 3.0, "src_duration": 5.0},
]

def run_cmd(cmd, desc=""):
    print(f"\n--- {desc} ---")
    print(" ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        print(f"Error running command: {res.stderr}")
        raise RuntimeError(f"Command failed: {desc}")
    return res.stdout

def assemble():
    os.makedirs(TEMP_DIR, exist_ok=True)
    with open(AUDIO_MANIFEST, "r", encoding="utf-8") as f:
        audio_shots = json.load(f)

    # 1. Check all source video files exist
    print("Step 1: Checking source video clips...")
    for item in SHOT_MAPPING:
        v_path = os.path.join(VIDEOS_DIR, item["src_video"])
        if not os.path.exists(v_path):
            raise FileNotFoundError(f"Missing required video: {v_path}")
        print(f"  Found {item['src_video']} ({os.path.getsize(v_path)} bytes)")

    # 2. Render each shot to exact duration, 1920x1080 @ 60fps
    print("\nStep 2: Conforming 16 individual shots...")
    shot_files = []

    for idx, (map_item, audio_item) in enumerate(zip(SHOT_MAPPING, audio_shots), 1):
        target_dur = audio_item["duration_s"]
        shot_out = os.path.join(TEMP_DIR, f"shot_{idx:02d}.mp4")
        src_path = os.path.join(VIDEOS_DIR, map_item["src_video"]).replace("\\", "/")

        src_st = map_item["src_start"]
        src_d = map_item["src_duration"]
        pts_factor = target_dur / src_d

        vf = f"setpts={pts_factor:.6f}*PTS,scale=1920:1080:flags=lanczos,fps=60"

        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{src_st:.3f}",
            "-t", f"{src_d:.3f}",
            "-i", src_path,
            "-vf", vf,
            "-t", f"{target_dur:.3f}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-an",
            shot_out
        ]
        run_cmd(cmd, f"Rendering Shot {idx:02d} ({target_dur:.2f}s)")
        shot_files.append(shot_out)

    # 3. Concat all 16 shots into body video using filtergraph concat
    print("\nStep 3: Concatenating 16 Shots into Body Video via Filtergraph...")
    body_video = os.path.join(TEMP_DIR, "body_video.mp4")
    concat_inputs = []
    filter_ins = ""
    for idx, sfile in enumerate(shot_files):
        concat_inputs.extend(["-i", sfile])
        filter_ins += f"[{idx}:v]"
    filter_concat = f"{filter_ins}concat=n={len(shot_files)}:v=1:a=0[v]"

    cmd_concat_body = [
        "ffmpeg", "-y",
        *concat_inputs,
        "-filter_complex", filter_concat,
        "-map", "[v]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        body_video
    ]
    run_cmd(cmd_concat_body, "Concatenating 16 Shots via filtergraph")

    # 4. Mux master audio and burn in subtitles
    print("\nStep 4: Muxing master audio and burning subtitles...")
    body_with_audio_subs = os.path.join(TEMP_DIR, "body_with_audio_subs.mp4")
    sub_filter = "subtitles=output/cinematic/subtitles/content.srt:force_style='FontName=Arial,FontSize=22,Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=4,Outline=1,Shadow=0,Alignment=2,MarginV=40'"

    run_cmd([
        "ffmpeg", "-y",
        "-i", body_video,
        "-i", MASTER_AUDIO,
        "-vf", sub_filter,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-ac", "2",
        "-shortest",
        body_with_audio_subs
    ], "Adding Master Audio 48kHz and Burning in Cyberpunk Subtitles")

    # 5. Final Concat: Intro (2s) + Body (89.02s) + Outro (4.5s) using Filtergraph Concat
    print("\nStep 5: Final Filtergraph Concat: Intro (2s) + Body + Outro (4.5s)...")
    filter_final = (
        "[0:v]scale=1920:1080:flags=lanczos,fps=60,format=yuv420p,setpts=PTS-STARTPTS[v0]; "
        "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a0]; "
        "[1:v]scale=1920:1080:flags=lanczos,fps=60,format=yuv420p,setpts=PTS-STARTPTS[v1]; "
        "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a1]; "
        "[2:v]scale=1920:1080:flags=lanczos,fps=60,format=yuv420p,setpts=PTS-STARTPTS[v2]; "
        "[2:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a2]; "
        "[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]"
    )

    run_cmd([
        "ffmpeg", "-y",
        "-i", INTRO_FILE,
        "-i", body_with_audio_subs,
        "-i", OUTRO_FILE,
        "-filter_complex", filter_final,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        FINAL_OUTPUT
    ], "Rendering Master Film via Filtergraph Concat")

    file_size_mb = os.path.getsize(FINAL_OUTPUT) / (1024 * 1024)
    print(f"\n==================================================================")
    print(f"MASTER FILM GENERATION COMPLETED SUCCESSFULLY!")
    print(f"Output File: {FINAL_OUTPUT}")
    print(f"File Size: {file_size_mb:.2f} MB")
    print(f"==================================================================")

if __name__ == "__main__":
    assemble()

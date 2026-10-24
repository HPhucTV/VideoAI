import json
import os

def generate_srt():
    manifest_path = "output/cinematic/audio/audio_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        shots = json.load(f)

    def to_srt_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int(round((seconds - int(seconds)) * 1000))
        if ms >= 1000:
            ms = 999
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    os.makedirs("output/cinematic/subtitles", exist_ok=True)

    # Content SRT (offset = 0)
    curr = 0.0
    srt_content = []
    for idx, shot in enumerate(shots, 1):
        start_s = curr
        end_s = curr + shot["duration_s"]
        curr = end_s
        text = shot["text"]
        srt_content.append(f"{idx}\n{to_srt_time(start_s)} --> {to_srt_time(end_s)}\n{text}\n")

    with open("output/cinematic/subtitles/content.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))

    # Full SRT (offset = 2.0s for intro)
    curr = 2.0
    srt_full = []
    for idx, shot in enumerate(shots, 1):
        start_s = curr
        end_s = curr + shot["duration_s"]
        curr = end_s
        text = shot["text"]
        srt_full.append(f"{idx}\n{to_srt_time(start_s)} --> {to_srt_time(end_s)}\n{text}\n")

    with open("output/cinematic/subtitles/full_with_intro.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_full))

    print("Generated SRT subtitles successfully!")

if __name__ == "__main__":
    generate_srt()

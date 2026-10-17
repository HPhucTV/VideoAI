import json
import re
import subprocess
from pathlib import Path

def parse_srt_time(ts_str: str) -> int:
    # "00:01:23,456" -> ms
    parts = ts_str.strip().replace(",", ":").split(":")
    h, m, s, ms = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
    return ((h * 3600 + m * 60 + s) * 1000) + ms

def format_srt_time(ms: int) -> str:
    h = ms // 3600000
    rem = ms % 3600000
    m = rem // 60000
    rem = rem % 60000
    s = rem // 1000
    millis = rem % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{millis:03d}"

def scale_srt_file(srt_path: Path, factor: float):
    if not srt_path.exists():
        return
    content = srt_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    new_lines = []
    time_pat = re.compile(r"^(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})")
    
    for line in lines:
        m = time_pat.match(line.strip())
        if m:
            start_ms = round(parse_srt_time(m.group(1)) * factor)
            end_ms = round(parse_srt_time(m.group(2)) * factor)
            new_lines.append(f"{format_srt_time(start_ms)} --> {format_srt_time(end_ms)}")
        else:
            new_lines.append(line)
            
    srt_path.write_text("\n".join(new_lines), encoding="utf-8")

def calibrate_all():
    job_id = "job-hop-dong-100-ty-tong-tai"
    job_dir = Path("output/whiteboard") / job_id
    scenes_dir = job_dir / "scenes"
    
    durations = []
    for i in range(1, 10):
        sid = f"scene-{i:02d}"
        ann = json.loads((scenes_dir / sid / f"{sid}.annotation.json").read_text(encoding="utf-8"))
        durations.append(ann["sceneDurationMs"] / 1000.0)
    
    total_audio = sum(durations)
    eraser_total = 8 * 1.3
    target_total = 3605.0 # 60 minutes 05 seconds
    target_audio = target_total - eraser_total
    factor = target_audio / total_audio
    tempo = 1.0 / factor
    
    print(f"[*] Calibrating 9 scenes to exactly ~60 minutes:")
    print(f"    Current audio: {total_audio:.2f}s ({total_audio/60:.2f} min)")
    print(f"    Target total video: {target_total:.2f}s ({target_total/60:.2f} min)")
    print(f"    Scaling factor: {factor:.5f}, atempo: {tempo:.5f}")
    
    for i in range(1, 10):
        sid = f"scene-{i:02d}"
        sdir = scenes_dir / sid
        mp3_path = sdir / f"{sid}.mp3"
        tmp_mp3 = sdir / f"{sid}_calibrated.mp3"
        ann_path = sdir / f"{sid}.annotation.json"
        srt_path = sdir / f"{sid}.srt"
        
        print(f"  -> Processing {sid}...")
        # 1. FFmpeg atempo filter
        cmd = [
            "ffmpeg", "-y", "-i", str(mp3_path),
            "-filter:a", f"atempo={tempo:.5f}",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(tmp_mp3)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tmp_mp3.replace(mp3_path)
        
        # 2. Update annotation.json
        ann = json.loads(ann_path.read_text(encoding="utf-8"))
        ann["sceneDurationMs"] = round(ann["sceneDurationMs"] * factor)
        for elem in ann.get("elements", []):
            if "reveal" in elem:
                elem["reveal"]["startMs"] = round(elem["reveal"]["startMs"] * factor)
                elem["reveal"]["durationMs"] = round(elem["reveal"]["durationMs"] * factor)
        ann_path.write_text(json.dumps(ann, indent=2, ensure_ascii=False), encoding="utf-8")
        
        # 3. Update scene SRT
        scale_srt_file(srt_path, factor)
        
    # Scale global input.mp3 and input.srt as well
    global_mp3 = job_dir / "input.mp3"
    global_tmp = job_dir / "input_calibrated.mp3"
    global_srt = job_dir / "input.srt"
    global_ann = job_dir / "scene-01.annotation.json"
    
    if global_mp3.exists():
        print("  -> Calibrating global input.mp3...")
        cmd = [
            "ffmpeg", "-y", "-i", str(global_mp3),
            "-filter:a", f"atempo={tempo:.5f}",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(global_tmp)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        global_tmp.replace(global_mp3)
        
    if global_srt.exists():
        print("  -> Calibrating global input.srt...")
        scale_srt_file(global_srt, factor)
        
    if global_ann.exists():
        ann = json.loads(global_ann.read_text(encoding="utf-8"))
        ann["sceneDurationMs"] = round(ann["sceneDurationMs"] * factor)
        for elem in ann.get("elements", []):
            if "reveal" in elem:
                elem["reveal"]["startMs"] = round(elem["reveal"]["startMs"] * factor)
                elem["reveal"]["durationMs"] = round(elem["reveal"]["durationMs"] * factor)
        global_ann.write_text(json.dumps(ann, indent=2, ensure_ascii=False), encoding="utf-8")
        
    print("[OK] Calibration complete!")

if __name__ == "__main__":
    calibrate_all()
